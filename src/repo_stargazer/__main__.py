import asyncio
import logging

from typer import Typer

from repo_stargazer._app import RSG
from repo_stargazer._config import Settings

cli_app = Typer(name="The RSG agent")


def make_rsg() -> RSG:
    settings = Settings()  # type: ignore[call-arg]
    return RSG(settings)


@cli_app.command()
def build() -> None:
    """Build the database."""
    rsg = make_rsg()
    rsg.build()


@cli_app.command()
def ask(query: str) -> None:
    """Ask a question."""
    rsg = make_rsg()
    asyncio.run(rsg.ask(query))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("repo_stargazer.app").setLevel(logging.DEBUG)
    logging.getLogger("repo_stargazer.embedder").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    cli_app()
