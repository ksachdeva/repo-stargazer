import json
from pathlib import Path

import github as gh
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from rich.progress import track

from .config import SETTINGS, Settings
from .locations import data_directory


class RSG:
    def __init__(self, settings: Settings) -> None:
        SETTINGS.set(settings)
        self._settings = settings
        self._gh = gh.Github(self._settings.github_pat.get_secret_value())

    def _refetch_starred_repositories(
        self,
        total_stars: int,
        starred_repos: PaginatedList[Repository],
    ) -> list[str]:
        repos: list[str] = []
        for repo in track(starred_repos, total=total_stars, description="Fetching Starred Repos"):
            repos.append(repo.full_name)

        return repos

    def build_db(self) -> None:
        user = self._gh.get_user()

        starred_repos_iter = user.get_starred()
        total_stars = starred_repos_iter.totalCount

        starred_repos_json = data_directory() / f"{user.id}-starred-repos.json"

        if starred_repos_json.exists():
            starred_repos_list: list[str] = json.loads(Path.read_text(starred_repos_json))
        else:
            starred_repos_list = []

        if len(starred_repos_list) != total_stars:
            starred_repos_list = self._refetch_starred_repositories(total_stars, starred_repos_iter)
            starred_repos_json.write_text(json.dumps(starred_repos_list, indent=2))
