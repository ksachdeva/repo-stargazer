# ruff: noqa: B008

import asyncio
import logging
import os
from pathlib import Path

import typer
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
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
def retrieve(
    query: str,
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    """Retrieve top 5 repositories based on a query."""
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
def run_a2a_server(
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    """Run the A2A server for the agent."""
    rsg = _make_rsg(config)
    agent = rsg.make_adk_agent()
    settings = rsg.get_settings()
    a2a_app = make_a2a_server(agent, settings.a2a_server)
    uvicorn.run(
        app=a2a_app.build(),
        host=settings.a2a_server.host,
        port=settings.a2a_server.port,
    )


@cli_app.command()
def run_adk_server(
    host: str = typer.Option("localhost", help="Host to run the server on"),
    port: int = typer.Option(8000, help="Port to run the server on"),
    config: Path = typer.Option(
        ...,
        file_okay=True,
        dir_okay=False,
        help="The RSG TOML Configuration file",
    ),
) -> None:
    """Serve the agent via ADK Dev web server and UI."""

    os.environ["RSG_CONFIG_FILE"] = str(config)

    agents_dir = Path(__file__).parent / "ui"

    app = get_fast_api_app(
        agents_dir=str(agents_dir),
        web=True,
        trace_to_cloud=False,
    )

    uconfig = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=True,
    )

    server = uvicorn.Server(uconfig)
    server.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("repo_stargazer.app").setLevel(logging.DEBUG)
    logging.getLogger("repo_stargazer.embedder").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    cli_app()
