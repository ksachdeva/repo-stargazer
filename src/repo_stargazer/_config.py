from contextvars import ContextVar
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from ._types import EmbeddingModelType
from .agent import AgentConfig


class EmbedderSettings(BaseModel):
    provider_type: EmbeddingModelType
    model_name: str
    api_key: SecretStr | None = None
    api_endpoint: str | None = None
    api_version: str | None = None
    api_deployment: str | None = None

    chunk_size: int = 1200
    chunk_overlap: int = 100


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    github_pat: SecretStr
    embedder: EmbedderSettings

    agent: AgentConfig

    _toml_file: ClassVar[Path]

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            TomlConfigSettingsSource(settings_cls, cls._toml_file),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


SETTINGS: ContextVar[Settings] = ContextVar("settings")
