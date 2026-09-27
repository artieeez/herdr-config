# herdr-config

Versioned Herdr configuration and custom plugin source. This repository
**is** `~/.config/herdr` — the directory herdr uses for its config, plugin
registry, and live state:

```
~/.config/herdr/                   ← this repo
├── config.toml                    tracked — your herdr configuration
├── plugins/
│   ├── workspace-tabs/            tracked — workspace.default-tabs plugin source
│   ├── config/                    ignored — per-plugin config/state (herdr-managed)
│   └── github/                    ignored — GitHub-installed plugin checkouts (herdr-managed)
├── session.json                   ignored — live session state
├── plugins.json                   ignored — plugin registry
├── *.log, *.sock, release-notes.json, .plugins.lock   ignored — live state
└── .gitignore                     tracked — the transient-file policy
```

`session.json`, logs, sockets, `plugins.json`, `release-notes.json`,
`.plugins.lock`, and the `plugins/config/` + `plugins/github/` subtrees are
rewritten continuously by the running herdr server and are **gitignored**.
Only `config.toml` and your plugin sources are versioned — see `.gitignore`
for the exact policy.

## Setup

```sh
git clone git@github.com:artieeez/herdr-config.git ~/.config/herdr
herdr plugin link ~/.config/herdr/plugins/workspace-tabs
# or from GitHub:
herdr plugin install artieeez/herdr-config/plugins/workspace-tabs
```

After editing `config.toml`, reload herdr with `prefix+shift+r`
(reload config). If herdr ever rewrites `config.toml` (e.g.
`herdr config reset-keys`), the change shows up as a normal git diff.

## Maintenance

If a future herdr version starts writing new files into `~/.config/herdr`,
add them to `.gitignore` before running `git add -A`. See each plugin's
`README.md` for configuration options.