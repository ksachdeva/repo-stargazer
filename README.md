# The Repo Stargazer

## Problem

I have been starring github projects for a long time. 

There are two primary intentions behind giving stars -

* Recognize the efforts of the author(s).
* Bookmark the repository for my own use.

Unfortunately the user interface to search the existing starred repositories is very primitive.

Also, it would be nice to have not only Semantic search but also provide the results to LLM to 
further explore the starred repositories.

> I also wanted to explore Google ADK, Google A2A Protocol & MCP. This project makes use of all 3 technologies.

## Solution

This project/tool uses semantic search and an AI agent as an attempt to solve the above problems.

## Install (User)

Read below to install `uv`. You haven't done it yet? Come on guys!!

https://docs.astral.sh/uv/getting-started/installation/

and then simply run `repo-stargazer` using `uvx`

> If you don't know - `uvx` will create an isolated environment, download the latest version and then run this tool. It's magic!!

```bash
uvx --from repo-stargazer rsg --help
```

## Usage

The tool requires you to have a configuration file in which various settings are to be specified. 

There is an example configuration file `rsg-config.example.toml` at the root of this repository. The configuration
uses TOML syntax.

You should make a copy of it and perhaps call it `rsg-config.toml` (The name of the file does not really matter!)

### Step 1 - Obtain the Github Personal Access Token

This tool fetches your starred github repositories. In order to access to them without incurring rate limits
it is required to use the Github Personal Access Token.

Read this to learn how to obtain it -

https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

### Step 2 - Edit the `rsg-config.toml`

- You should provide the Github PAT obtained in Step 1
- You should fill the `[embedder]` section (Supported provider types are - ollama, openai, azure_openai)
- You should fill the `[agent.litellm_params]` section

In `rsg-config.example.toml`, I have added necessary comments to help fill out various configuration.

### Step 3 - Build the database

The real work starts with this step. 

At the moment, I use naive RAG technique.

- Information about your starred github repos are downloaded using the GitHub API
- Then the `readme` files of these repos are downloaded. Note - Some repos, do not have `readme` file.
- Then these `readme` files are chunked and their embeddings are stored in a vector store

The data above (including vectorstore) is stored in your computers data directories for example `$HOME/.local/share/rsg`
on macos and linux.

You can change the location of the data by setting the environment variable `RSG_DATA_HOME`

```bash
uvx --from repo-stargazer rsg build --config rsg-config.toml
```

### Step 4 - Run the agent using adk web & ui

Let's see all of it in action.

For the user interface, I am still using the development UI that comes as part of Google ADK. 

In near future, would provide a decent UI with out any developer specific elements.

```bash
uvx --from repo-stargazer rsg run-adk-server --config rsg-config.toml
```

## Developer

```bash
# I shouldn't have to write this instruction. But what the heck!
git clone https://github.com/ksachdeva/repo-stargazer
```

Now open the repo in `devcontainer`. You should know these things!

Just in case, Read if you have never used `devcontainers` 

https://code.visualstudio.com/docs/devcontainers/containers

Various commands (via poe [https://poethepoet.natn.io/index.html]) to use during development.

> Hint - Look inside `pyproject.toml` to see the underlying poe magic!

```bash
# Help
# Note - The `pyproject.toml` has `RSG_DATA_HOME` env variable set to `$PWD/tmp`
uv run poe --help
```


```bash
# Build the database
# Note - The `pyproject.toml` has `RSG_DATA_HOME` env variable set to `$PWD/tmp`
uv run poe build --config rsg-config.toml
```

```bash
# Run the Google ADK server
# Note - The `pyproject.toml` has `RSG_DATA_HOME` env variable set to `$PWD/tmp`
uv run poe adk-server --config rsg-config.toml
```
