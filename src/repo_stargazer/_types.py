from enum import Enum
from typing import TypedDict


class EmbeddingModelType(str, Enum):
    openai = "openai"
    azure_openai = "azure_openai"
    ollama = "ollama"


class GitHubRepoInfo(TypedDict):
    id: int
    name: str
    description: str | None
    created_at: str
    topics: list[str] | str
