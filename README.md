# herdr-config

Personal Herdr configuration: plugins, keybindings, and setup for
[herdr](https://herdr.dev) — a terminal workspace manager for AI coding
agents.

## Layout

```
plugins/
  workspace-tabs/   workspace.default-tabs — pi / nvim / terminal tabs
                    in every new workspace (naming only)
```

## Install

```sh
gh repo clone artieeez/herdr-config
herdr plugin link ~/dev/herdr-config/plugins/workspace-tabs
# or from GitHub:
herdr plugin install artieeez/herdr-config/plugins/workspace-tabs
```

See each plugin's `README.md` for configuration options.