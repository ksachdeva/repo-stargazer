"""This module is needed so that we can test via adk run or web"""

import os
from pathlib import Path

from repo_stargazer import RSG, Settings

CONFIG_FILE_PATH = os.getenv("RSG_CONFIG_FILE", None)

if CONFIG_FILE_PATH is None:
    raise ValueError("RSG_CONFIG_FILE environment variable is not set.")

Settings._toml_file = Path(CONFIG_FILE_PATH)
settings = Settings()  # type: ignore

app = RSG(settings=settings)

root_agent = app.make_adk_agent()
