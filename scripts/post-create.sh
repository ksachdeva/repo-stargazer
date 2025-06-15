#!/usr/bin/env bash

USERNAME=vscode

echo "changing zshrc theme to ys ..."
sed -i s/^ZSH_THEME=".\+"$/ZSH_THEME=\"ys\"/g ~/.zshrc    

echo "sym link zsh_history ..."
mkdir -p /commandhistory 
touch /commandhistory/.zsh_history
sudo chown -R $USERNAME /commandhistory 

SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.zsh_history"
echo "$SNIPPET" >> "/home/$USERNAME/.zshrc"

echo 'eval "$(uv generate-shell-completion zsh)"' >> "/home/$USERNAME/.zshrc"
echo 'eval "$(uvx --generate-shell-completion zsh)"' >> "/home/$USERNAME/.zshrc"

echo "uv sync ..."
uv sync