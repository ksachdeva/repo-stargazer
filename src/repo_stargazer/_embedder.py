import logging
from pathlib import Path

import pandas as pd
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_community.storage import SQLStore
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_openai import (
    AzureOpenAIEmbeddings,
    OpenAIEmbeddings,
)
from langchain_text_splitters import TextSplitter
from rich.progress import track

from ._config import EmbedderSettings
from ._locations import cache_directory, data_directory, readme_data_directory
from ._types import EmbeddingModelType, GitHubRepoInfo

_LOGGER = logging.getLogger("repo_stargazer.embedder")


def make_embedding_instance(embedder_settings: EmbedderSettings) -> Embeddings:
    underlying_embedding: Embeddings

    embedding_type = embedder_settings.provider_type
    embedding_model = embedder_settings.model_name
    embedding_api_key = embedder_settings.api_key
    embedding_api_version = embedder_settings.api_version
    embedding_api_endpoint = embedder_settings.api_endpoint
    embedding_api_deployment = embedder_settings.api_deployment

    if embedding_type == EmbeddingModelType.openai:
        underlying_embedding = OpenAIEmbeddings(
            model=embedding_model,
            api_key=embedding_api_key,
        )
    elif embedding_type == EmbeddingModelType.azure_openai:
        underlying_embedding = AzureOpenAIEmbeddings(
            model=embedding_model,
            api_version=embedding_api_version,
            api_key=embedding_api_key,
            azure_endpoint=embedding_api_endpoint,
            azure_deployment=embedding_api_deployment,
        )
    elif embedding_type == EmbeddingModelType.ollama:
        underlying_embedding = OllamaEmbeddings(
            model=embedding_model,
            base_url=embedding_api_endpoint,
        )
    else:
        raise ValueError(
            f"Unsupported embedding model type: {embedding_type}. Supported types are: openai, azure_openai, ollama."
        )

    embedding_db_path = "sqlite:///" + str(cache_directory().joinpath("embedding.db"))
    store = SQLStore(namespace=embedding_model, db_url=embedding_db_path)
    store.create_schema()

    return CacheBackedEmbeddings.from_bytes_store(
        underlying_embeddings=underlying_embedding,
        document_embedding_cache=store,
    )


def run_embedder(text_splitter: TextSplitter, vector_store: VectorStore) -> None:
    parquet_files = data_directory().glob("*.starred.parquet")

    def _process_read_me(index: int, row: pd.Series) -> None:
        repo_info = GitHubRepoInfo(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            created_at=row["created_at"],
            topics=row["topics"],
        )

        # add the description as a separate text unit
        if row["description"]:
            vector_store.add_texts(
                [row["description"]],
                metadatas=[repo_info],  # type: ignore
            )

        readme_file_path = readme_data_directory() / f"{row.id}.md"

        # some repositories may not have a README file
        if not readme_file_path.exists():
            return

        readme_content = Path(readme_file_path).read_text(encoding="utf-8")

        if readme_content.strip() == "":
            _LOGGER.warning("Skipping empty README for repository %s", row["name"])
            return

        text_units = text_splitter.split_text(readme_content)
        # _LOGGER.debug("Number of text units for repo %s: %d", row["name"], len(text_units))

        metadatas = [repo_info] * len(text_units)

        vector_store.add_texts(
            text_units,
            metadatas=metadatas,  # type: ignore
        )

    for f in parquet_files:
        _LOGGER.info("Processing file: %s", f)
        df = pd.read_parquet(f)

        for index, row in track(df.iterrows(), description="Processing readme files", total=len(df)):
            _process_read_me(index, row)  # type: ignore
