# The Repo Stargazer

## Problem

I have been starring github projects for a long time. 

There are two primary intentions behind giving stars -

* Recognize the efforts of the author
* Bookmark the repository for my own use

Unfortunately the user interface to search the existing starred repositories is very primitive.

Also, it would be nice to have not only do Semantic search but also provide the results to LLM to 
further explore the starred repositories.

## Solution

This project uses semantic search and an AI agent as an attempt to solve the above problem.

## Architecture & Implementation Details

[TBD]

## Install (User)

You should be able to run this as tool thanks to `uvx`

```bash
uvx --from repo-stargazer rsg --help
```

## Usgage

The tool requires you to have a configuration file in which various settings are to be specified. 

There is an example configuration file `rsg-config.example.toml` at the root of this repository. The configuration
uses TOML syntax.

You should make a copy of it as perhaps call it `rsg-config.toml` (The name of the file does not really matter!)

### Step 1 - Obtain the Github Personal Access Token

[TBD]

### Step 2 - Edit the `rsg-config.toml`

- You should provide the Github PAT obtained in Step 1
- You should fill the `[embedder]` section (Supported provider types are - ollama, openai, azure_openai)
- You should fill the `[agent.litellm_params]` section

[TBD] - Don't think above instructions are enough! To update and explain in detail the settings

### Step 3 - Build the database

```bash
uvx --from repo-stargazer rsg build --config rsg-config.toml
```

### Step 4 - Run the agent using adk web & ui

The agent is built using Google ADK and I have done somewhat of a hack to be able run the agent
by the built-in fastapi server & user interface. The server & user interface is meant for development needs but
for now it is the only UI there is 

```bash
uvx --from repo-stargazer rsg run-adk-server --config rsg-config.toml
```
