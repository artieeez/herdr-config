# herdr-config

Versioned Herdr configuration and custom plugin source, kept under herdr's
own config directory:

```
~/.config/herdr/
├── config.toml            → symlink → herdr-config/config.toml
├── herdr-config/          ← this repo
│   ├── config.toml        user's herdr configuration
│   └── plugins/
│       └── workspace-tabs/   workspace.default-tabs — pi / nvim / terminal
│                             tabs in every new workspace (naming only)
├── plugins/               herdr-managed: per-plugin config/state +
│                          GitHub-installed checkouts (never commit this)
└── session.json, *.log, *.sock, plugins.json  → herdr-managed live state
```

The repo is a **subdir** of `~/.config/herdr`, never the directory itself:
herdr continuously rewrites `session.json`, logs, sockets, and `plugins.json`
in its config dir, and keeps managed plugin checkouts under `plugins/github/`.
Those must never be tracked or committed.

## Setup

```sh
git clone git@github.com:artieeez/herdr-config.git ~/.config/herdr/herdr-config

# Track config.toml through a symlink (herdr keeps reading its usual path):
ln -s herdr-config/config.toml ~/.config/herdr/config.toml

herdr plugin link ~/.config/herdr/herdr-config/plugins/workspace-tabs
# or from GitHub:
herdr plugin install artieeez/herdr-config/plugins/workspace-tabs
```

After editing `config.toml`, reload herdr with `prefix+shift+r`
(reload config).

## Note on managed state

Everything else in `~/.config/herdr` is herdr-owned: `session.json` (live
session), `herdr-server.log`/`herdr-client.log`, `plugins.json`,
`release-notes.json`, sockets, and the `plugins/config/` + `plugins/github/`
subtrees. Do not `git add` them; they churn continuously and contain live
session/agent data.

See each plugin's `README.md` for configuration options.