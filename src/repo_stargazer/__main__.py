# ruff: noqa: B008

import asyncio
import logging
from pathlib import Path

import typer
import uvicorn
from typer import Typer

from repo_stargazer._app import RSG
from repo_stargazer._config import Settings
from repo_stargazer.a2a_support import make_a2a_server
from repo_stargazer.mcp_support._server import make_mcp_server

cli_app = Typer(name="The RSG agent")


def _make_rsg(config: Path) -> RSG:
    Settings._toml_file = config  # type: ignore[attr-defined]
    settings = Settings()  # type: ignore[call-arg]
    return RSG(settings=settings)


@cli_app.command()
def build(
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    """Build the database."""
    rsg = _make_rsg(config)
    rsg.build()


@cli_app.command()
def ask(
    query: str,
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    """Ask a question."""
    rsg = _make_rsg(config)
    asyncio.run(rsg.retrieve_starred_repositories(query))


@cli_app.command()
def get_readme(
    repo_name: str,
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    """Get the README of a repository."""
    rsg = _make_rsg(config)
    readme = rsg.get_readme(repo_name)
    print(readme)


@cli_app.command()
def run_mcp_server(
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    """Run the MCP server."""
    rsg = _make_rsg(config)
    make_mcp_server(rsg).run(transport="stdio")


@cli_app.command()
def run_agent_server(
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    rsg = _make_rsg(config)
    agent = rsg.make_adk_agent()
    settings = rsg.get_settings()
    a2a_app = make_a2a_server(agent, settings.a2a_server)
    uvicorn.run(
        app=a2a_app.build(),
        host=settings.a2a_server.host,
        port=settings.a2a_server.port,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("repo_stargazer.app").setLevel(logging.DEBUG)
    logging.getLogger("repo_stargazer.embedder").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    cli_app()
