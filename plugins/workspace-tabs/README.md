# Default Workspace Tabs (workspace.default-tabs)

Herdr plugin that gives every new workspace a three-tab layout:

| Tab        | Contents                       |
| ---------- | ------------------------------ |
| `pi`       | plain interactive shell        |
| `nvim`     | plain interactive shell        |
| `terminal` | plain interactive shell        |

All three tabs share the workspace's working directory. The plugin only
handles naming — nothing is auto-launched unless you opt in (see
[Configuration](#configuration)).

## How it works

The plugin declares a `[[events]]` hook on `workspace.created`. When Herdr
emits that event (TUI new workspace, `herdr workspace create`, or a git
worktree that opens a new workspace), `bootstrap.py` runs and:

1. renames the workspace's default first tab to `pi`,
2. creates an `nvim` tab,
3. creates a `terminal` tab.

The hook is idempotent — a workspace that already has `pi`/`nvim`/`terminal`
tabs is left untouched.

## Install

```sh
herdr plugin link ~/.herdr/plugins/workspace-tabs
herdr plugin list
```

Tabs are created only for workspaces created **after** linking. Existing
workspaces are never modified.

## Configuration

Optional overrides live in the plugin config directory:

```sh
herdr plugin config-dir workspace.default-tabs
```

Create a `config.env` file there (see `bootstrap.py` for the full list):

```sh
# Also start the pi agent in the pi tab.
BOOTSTRAP_PI=1
# Also launch nvim in the nvim tab.
BOOTSTRAP_NVIM=1
# Command for the nvim tab (accepts arguments).
NVIM_CMD="nvim -u NONE"
# How long agent start waits for pi interactive readiness.
PI_START_TIMEOUT_MS=60000
```

## Troubleshooting / uninstall

```sh
herdr plugin log list --plugin workspace.default-tabs   # hook output
herdr plugin unlink workspace.default-tabs              # stop running the hook
```