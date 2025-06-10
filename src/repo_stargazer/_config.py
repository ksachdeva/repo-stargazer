import os
from contextvars import ContextVar
from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

from ._locations import config_file
from ._types import EmbeddingModelType


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

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        config_from_env = os.getenv("RSG_CONFIG_FILE")
        if config_from_env:
            conf_file = Path(config_from_env).resolve()
        else:
            conf_file = config_file()

        default_sources = (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

        if conf_file.exists():
            return (
                init_settings,
                TomlConfigSettingsSource(settings_cls, conf_file),
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )
        return default_sources


SETTINGS: ContextVar[Settings] = ContextVar("settings")
