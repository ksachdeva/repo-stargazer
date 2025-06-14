from google.adk.agents.llm_agent import LlmAgent, ToolUnion
from google.adk.models.lite_llm import LiteLlm

from ._config import AgentConfig, LiteLLMConfig
from ._prompts import DEFAULT_DESCRIPTION, SYSTEM_PROMPT


def _make_litellm(params: LiteLLMConfig) -> LiteLlm:
    return LiteLlm(
        params.model,
        **params.provider_config,
    )


def create_agent(
    model_config: AgentConfig,
    tools: list[ToolUnion],
    description: str = DEFAULT_DESCRIPTION,
    system_prompt: str = SYSTEM_PROMPT,
) -> LlmAgent:
    agent = LlmAgent(
        name="rsg",
        model=_make_litellm(model_config.litellm_params),
        description=description,
        instruction=system_prompt,
        tools=tools,
    )

    return agent
