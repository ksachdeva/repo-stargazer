import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService, Session
from google.genai import types as genai_types
from pydantic import ConfigDict
from typing_extensions import override

from ._utils import convert_a2a_parts_to_genai, convert_genai_parts_to_a2a

_LOGGER = logging.getLogger(__name__)


class A2ARunConfig(RunConfig):
    """Custom override of ADK RunConfig to smuggle extra data through the event loop."""

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
    current_task_updater: TaskUpdater


class RepoStargazerAgentExecutor(AgentExecutor):
    def __init__(self, agent: LlmAgent) -> None:
        self._agent = agent
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),  # type: ignore
            memory_service=InMemoryMemoryService(),  # type: ignore
        )

    async def _upsert_session(self, session_id: str) -> Session:
        return await self._runner.session_service.get_session(
            app_name=self._runner.app_name,
            user_id="self",
            session_id=session_id,
        ) or await self._runner.session_service.create_session(
            app_name=self._runner.app_name,
            user_id="self",
            session_id=session_id,
        )

    async def _process_request(
        self,
        new_message: genai_types.Content,
        session_id: str,
        task_updater: TaskUpdater,
    ) -> None:
        session = await self._upsert_session(session_id)

        session_id = session.id
        run_config = A2ARunConfig(current_task_updater=task_updater)

        async for event in self._runner.run_async(
            session_id=session_id,
            user_id="self",
            new_message=new_message,
            run_config=run_config,
        ):
            _LOGGER.info("Received ADK event: %s", event)
            _LOGGER.info(f"Is final message : {event.is_final_response()}")
            if event.is_final_response():
                assert event.content is not None
                assert event.content.parts is not None
                response = convert_genai_parts_to_a2a(event.content.parts)
                _LOGGER.info("Yielding final response: %s", response)
                await task_updater.add_artifact(response)
                await task_updater.complete()
                break

    @override
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        assert context.task_id is not None
        assert context.context_id is not None
        assert context.message is not None
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if not context.current_task:
            # Immediately notify that the task is submitted.
            await updater.submit()

        # get to work
        await updater.start_work()

        await self._process_request(
            genai_types.UserContent(
                parts=convert_a2a_parts_to_genai(context.message.parts),
            ),
            context.context_id,
            updater,
        )

    @override
    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        pass
