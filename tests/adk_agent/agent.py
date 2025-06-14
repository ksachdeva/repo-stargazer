"""This module is needed so that we can test via adk run or web"""

from repo_stargazer import RSG, Settings

settings = Settings()  # type: ignore

app = RSG(settings=settings)

root_agent = app.make_adk_agent()
