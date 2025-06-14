from typing import Any

from pydantic import BaseModel


class LiteLLMConfig(BaseModel):
    model: str
    provider_config: dict[str, Any]


class AgentConfig(BaseModel):
    host: str = "localhost"
    port: int = 10001

    litellm_params: LiteLLMConfig
