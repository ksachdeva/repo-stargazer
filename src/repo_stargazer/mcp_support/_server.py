from mcp.server.fastmcp import FastMCP
from pydantic import Field

from repo_stargazer._app import RSG


def make_mcp_server(rsg: RSG) -> FastMCP:
    """Create a FastMCP server instance."""
    mcp = FastMCP("The Repository Stargazer")

    @mcp.resource("gitreadme://{repo_name}", description="Get the README of a repository.")
    def get_readme(repo_name: str) -> str:
        """Get the README of a repository."""
        repo_name = repo_name.replace("%2F", "/")
        repo_name = repo_name.strip("/")
        readme = rsg.get_readme(repo_name)
        return readme

    @mcp.tool(
        description="Find the github repositories that have been starred by the user that fulfill the provided query."
    )
    async def find_starred_repos(
        query: str = Field(description="The query to use to filter starred repositories."),
    ) -> list[str]:
        results = await rsg.ask(query, search_kwargs={"k": 5})
        repo_names = [result.repo_info["name"] for result in results]

        # remove the duplicates
        repo_names = list(set(repo_names))

        # for each repo we will at least fetch its description

        return repo_names

    return mcp
