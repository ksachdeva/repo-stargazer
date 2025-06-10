import logging
from typing import Any

import pandas as pd
from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from mpire.pool import WorkerPool
from rich.progress import track

from ._config import SETTINGS, Settings
from ._locations import data_directory, readme_data_directory

_LOGGER = logging.getLogger("repo_stargazer.app")


def _refetch_starred_repositories(
    total_stars: int,
    starred_repos: PaginatedList[Repository],
) -> list[Repository]:
    repos: list[Repository] = []
    for repo in track(starred_repos, total=total_stars, description="Fetching Starred Repos"):
        repos.append(repo)

    return repos


def _repos_to_df(repos: list[Repository]) -> pd.DataFrame:
    def repo_to_dict(repo: Repository) -> dict[str, Any]:
        return {
            "id": repo.id,
            "name": repo.full_name,
            "description": repo.description,
            "created_at": repo.created_at.isoformat(),
            "topics": repo.get_topics(),
        }

    with WorkerPool() as pool:
        records = pool.map(repo_to_dict, repos, progress_bar=True)

    return pd.DataFrame(records)


class RSG:
    def __init__(self, settings: Settings) -> None:
        SETTINGS.set(settings)
        self._settings = settings
        self._gh = Github(self._settings.github_pat.get_secret_value())

    def build_db(self) -> None:
        user = self._gh.get_user()

        starred_repos_iter = user.get_starred()
        total_stars = starred_repos_iter.totalCount

        parquet_file_path = data_directory() / f"{user.id}-starred-repos.parquet"

        df: pd.DataFrame | None = None

        if parquet_file_path.exists():
            df = pd.read_parquet(parquet_file_path)

        if df is None or len(df) != total_stars:
            starred_repos_list = _refetch_starred_repositories(total_stars, starred_repos_iter)
            _LOGGER.debug(
                "Fetched %d starred repositories for user %s",
                len(starred_repos_list),
                user.login,
            )
            df = _repos_to_df(starred_repos_list)
            _LOGGER.debug("Saving repositories to DataFrame with %d rows", len(df))
            df.to_parquet(parquet_file_path)

        # fetch the readme of the repositories
        def _fetch_and_write_readme(index: int, row: pd.Series) -> None:
            readme_file_path = readme_data_directory() / f"{row.id}.md"
            if readme_file_path.exists():
                return
            repo = self._gh.get_repo(row["id"])
            try:
                readme = repo.get_readme()
            except Exception as e:
                _LOGGER.warning(
                    "Failed to fetch README for repository %s: %s",
                    row["name"],
                    e,
                )
                return
            readme_file_path.write_bytes(readme.decoded_content)

        with WorkerPool() as pool:
            pool.map(_fetch_and_write_readme, df.iterrows(), iterable_len=len(df), progress_bar=True)
