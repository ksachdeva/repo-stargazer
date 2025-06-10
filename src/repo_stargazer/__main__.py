import asyncio
import logging

from typer import Typer

from repo_stargazer._app import RSG
from repo_stargazer._config import Settings
from repo_stargazer.mcp_support._server import make_mcp_server

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
    asyncio.run(rsg.ask(query, search_kwargs={"k": 5}))


@cli_app.command()
def get_readme(repo_name: str) -> None:
    """Get the README of a repository."""
    rsg = make_rsg()
    readme = rsg.get_readme(repo_name)
    print(readme)


@cli_app.command()
def run_mcp_server() -> None:
    """Run the MCP server."""
    rsg = make_rsg()
    make_mcp_server(rsg).run(transport="stdio")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("repo_stargazer.app").setLevel(logging.DEBUG)
    logging.getLogger("repo_stargazer.embedder").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    cli_app()
