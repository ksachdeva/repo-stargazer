import logging
from typing import Any

import pandas as pd
from github import Github
from github.PaginatedList import PaginatedList
from github.Repository import Repository
from langchain_community.vectorstores import LanceDB as LanceDBVectorStore
from langchain_text_splitters import TokenTextSplitter
from mpire.pool import WorkerPool
from rich.progress import track

from ._config import SETTINGS, Settings
from ._embedder import make_embedding_instance, run_embedder
from ._locations import data_directory, readme_data_directory, vector_store_dir
from ._types import GitHubRepoInfo, RetrievalResult

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
    def repo_to_dict(repo: Repository) -> GitHubRepoInfo:
        return GitHubRepoInfo(
            id=repo.id,
            name=repo.full_name,
            description=repo.description,
            created_at=repo.created_at.isoformat(),
            topics=repo.get_topics(),
        )

    with WorkerPool() as pool:
        records = pool.map(repo_to_dict, repos, progress_bar=True)

    return pd.DataFrame(records)


class RSG:
    def __init__(
        self,
        settings: Settings,
    ) -> None:
        SETTINGS.set(settings)
        self._settings = settings
        self._gh = Github(self._settings.github_pat.get_secret_value())

        self._vs = LanceDBVectorStore(
            uri=str(vector_store_dir()),
            embedding=make_embedding_instance(embedder_settings=settings.embedder),
            table_name="github-readme",
        )

    async def ask(self, query: str, search_kwargs: dict[str, Any]) -> list[RetrievalResult]:
        """Ask a question about the repositories."""

        retriever = self._vs.as_retriever(search_kwargs=search_kwargs)

        documents = await retriever.ainvoke(input=query)

        _LOGGER.info("Retrieved %d documents for query: %s", len(documents), query)

        results: list[RetrievalResult] = []

        for doc in documents:
            _LOGGER.info("Document: %s", doc.metadata["name"])
            results.append(
                RetrievalResult(
                    chunk=doc.page_content,
                    repo_info=doc.metadata,  # type: ignore
                )
            )

        return results

    def _embed(self) -> None:
        text_splitter = TokenTextSplitter(
            chunk_size=self._settings.embedder.chunk_size,
            chunk_overlap=self._settings.embedder.chunk_overlap,
        )

        run_embedder(
            text_splitter=text_splitter,
            vector_store=self._vs,
        )

    def get_readme(self, repo_name: str) -> str:
        """Get the README of a repository."""

        user = self._gh.get_user()

        parquet_file_path = data_directory() / f"{user.id}-repos.starred.parquet"

        df = pd.read_parquet(parquet_file_path)

        try:
            repo_id = df[df["name"] == repo_name].iloc[0]["id"]

            _LOGGER.info("Fetching README for repository %s with ID %s", repo_name, repo_id)

            readme_file_path = readme_data_directory() / f"{repo_id}.md"
            if not readme_file_path.exists():
                return f"README for repository {repo_name} not found."

            return readme_file_path.read_text()

        except IndexError:
            _LOGGER.error("Repository %s not found in starred repositories.", repo_name)
            return f"Repository {repo_name} not found in starred repositories."
        except Exception as e:
            _LOGGER.error("Error fetching README for repository %s: %s", repo_name, e)
            return f"Error fetching README for repository {repo_name}: {e}"

    def build(self) -> None:
        user = self._gh.get_user()

        starred_repos_iter = user.get_starred()
        total_stars = starred_repos_iter.totalCount

        parquet_file_path = data_directory() / f"{user.id}-repos.starred.parquet"

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

        self._embed()
