import os
from pathlib import Path

from xdg_base_dirs import xdg_cache_home, xdg_config_home, xdg_data_home


def _get_data_home() -> Path:
    env_rsg_data = os.getenv("RSG_DATA_HOME", None)
    if env_rsg_data:
        return Path(env_rsg_data).expanduser().resolve()
    return xdg_data_home()


def _get_config_home() -> Path:
    env_rsg_data = os.getenv("RSG_DATA_HOME", None)
    if env_rsg_data:
        return Path(env_rsg_data).joinpath("config").expanduser().resolve()
    return xdg_config_home()


def _get_cache_home() -> Path:
    env_rsg_data = os.getenv("RSG_DATA_HOME", None)
    if env_rsg_data:
        return Path(env_rsg_data).joinpath("cache").expanduser().resolve()
    return xdg_cache_home()


def _rsg_directory(root: Path) -> Path:
    directory = root / "rsg"
    directory.mkdir(exist_ok=True, parents=True)
    return directory


def data_directory() -> Path:
    """Return (possibly creating) the application data directory."""
    return _rsg_directory(_get_data_home())


def config_directory() -> Path:
    """Return (possibly creating) the application config directory."""
    return _rsg_directory(_get_config_home())


def config_file() -> Path:
    return config_directory() / "config.yaml"


def readme_data_directory() -> Path:
    """Return (possibly creating) the readme data directory."""
    readmes_dir = data_directory() / "readmes"
    readmes_dir.mkdir(exist_ok=True, parents=True)
    return readmes_dir


def cache_directory() -> Path:
    return _rsg_directory(_get_cache_home())


def vector_store_dir() -> Path:
    """Return (possibly creating) the vector store directory."""
    vector_store_dir = data_directory() / "vector_store"
    vector_store_dir.mkdir(exist_ok=True, parents=True)
    return vector_store_dir
