from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from google.adk.agents import LlmAgent

from repo_stargazer.agent import DEFAULT_DESCRIPTION

from ._config import AgentServerConfig
from ._executor import RepoStargazerAgentExecutor

_NAME: str = "RSG"


def make_a2a_server(
    agent: LlmAgent,
    config: AgentServerConfig,
) -> A2AStarletteApplication:
    skills = [
        AgentSkill(
            id="retrieves_starred_repos",
            name=_NAME,
            description=DEFAULT_DESCRIPTION,
            tags=["starred-repos", "github"],
        ),
    ]

    agent_card = AgentCard(
        name=_NAME,
        description=DEFAULT_DESCRIPTION,
        url=f"http://{config.host}:{config.port}/",
        version="0.0.1",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=skills,
    )

    agent_executor = RepoStargazerAgentExecutor(agent)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    return A2AStarletteApplication(agent_card, request_handler)
