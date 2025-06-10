import logging

from typer import Typer

from repo_stargazer.app import RSG
from repo_stargazer.config import Settings

cli_app = Typer(name="The RSG agent")


def make_rsg() -> RSG:
    settings = Settings()  # type: ignore[call-arg]
    return RSG(settings)


@cli_app.command()
def build_db() -> None:
    """Build the database."""
    rsg = make_rsg()
    rsg.build_db()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    cli_app()
