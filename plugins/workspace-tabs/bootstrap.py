#!/usr/bin/env python3
"""bootstrap.py — workspace.default-tabs event hook.

Runs on the `workspace.created` event and turns the freshly created
workspace into a pi / nvim / terminal three-tab layout:

  1. The default first tab is renamed to "pi".
  2. A "nvim" tab is created.
  3. A "terminal" tab is created.

By default all three are plain interactive shells. Optionally set
BOOTSTRAP_PI and/or BOOTSTRAP_NVIM in the plugin config to have the hook
also start the pi agent or launch nvim.

All tabs share the workspace's working directory (the origin pane cwd).

Behavior is configurable through HERDR_PLUGIN_CONFIG_DIR/config.env
(created by `herdr plugin config-dir workspace.default-tabs`):

  BOOTSTRAP_PI=1            # also start the pi agent in the pi tab
  BOOTSTRAP_NVIM=1          # also launch nvim in the nvim tab
  NVIM_CMD=vim              # command run in the nvim tab
  PI_START_TIMEOUT_MS=60000 # agent start readiness timeout for pi

By default the plugin only creates/renames tabs: pi, nvim, and terminal
arrive as plain interactive shells, ready for you to launch pi or nvim
yourself.

The hook is idempotent: workspaces that already have pi/nvim/terminal tabs
are left untouched.
"""

import json
import os
import shlex
import subprocess
import sys

LOG_TAG = "workspace.default-tabs"


def log(msg: str) -> None:
    print(f"[{LOG_TAG}] {msg}", file=sys.stderr, flush=True)


def resolve_bin() -> str:
    return os.environ.get("HERDR_BIN_PATH") or "herdr"


def run(bin_path: str, args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [bin_path, *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def out_json(bin_path: str, args):
    p = run(bin_path, args)
    if p.returncode != 0:
        log(f"herdr {' '.join(args)} failed: {p.stderr.strip() or p.stdout.strip()}")
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        log(f"unexpected non-JSON response from herdr {' '.join(args)}")
        return None


def find_workspace_id() -> str:
    wsid = os.environ.get("HERDR_WORKSPACE_ID")
    if wsid:
        return wsid
    for var in ("HERDR_PLUGIN_EVENT_JSON", "HERDR_PLUGIN_CONTEXT_JSON"):
        raw = os.environ.get(var)
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            for cand in (obj.get("created_workspace"), obj.get("workspace")):
                if isinstance(cand, dict) and cand.get("workspace_id"):
                    return cand["workspace_id"]
    return ""


def load_config() -> dict:
    cfg_dir = os.environ.get("HERDR_PLUGIN_CONFIG_DIR")
    if not cfg_dir:
        return {}
    cfg_path = os.path.join(cfg_dir, "config.env")
    if not os.path.isfile(cfg_path):
        return {}
    config: dict = {}
    with open(cfg_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip().strip("\"'")
    return config


def main() -> int:
    bin_path = resolve_bin()
    wsid = find_workspace_id()
    if not wsid:
        log("no workspace id in context; skipping")
        return 0

    config = load_config()
    bootstrap_pi = config.get("BOOTSTRAP_PI") == "1"
    bootstrap_nvim = config.get("BOOTSTRAP_NVIM") == "1"
    nvim_cmd = shlex.split(config.get("NVIM_CMD", "nvim")) or ["nvim"]
    try:
        pi_timeout_ms = int(config.get("PI_START_TIMEOUT_MS", "60000"))
    except ValueError:
        pi_timeout_ms = 60000

    tabs = (out_json(bin_path, ["tab", "list", "--workspace", wsid]) or {}).get("result", {}).get("tabs", [])
    labels = {t.get("label", "").lower() for t in tabs}
    if {"pi", "nvim", "terminal"} <= labels:
        log(f"workspace {wsid} already has pi/nvim/terminal tabs; skipping")
        return 0

    KNOWN = {"pi", "nvim", "terminal"}
    origin = next((t for t in tabs if t.get("label", "").lower() not in KNOWN), None)
    if origin is None:
        log(f"workspace {wsid}: no origin tab to rename; skipping")
        return 0
    origin_tab = origin["tab_id"]

    panes = (out_json(bin_path, ["pane", "list", "--workspace", wsid]) or {}).get("result", {}).get("panes", [])
    origin_pane = next((p for p in panes if p.get("tab_id") == origin_tab), None)
    cwd = (origin_pane or {}).get("cwd") or ""

    log(f"workspace {wsid}: bootstrapping pi/nvim/terminal tabs (cwd={cwd or '(inherit)'})")

    # 1. pi tab: rename the origin tab and start the pi agent.
    p = run(bin_path, ["tab", "rename", origin_tab, "pi"])
    if p.returncode != 0:
        log(f"tab rename to 'pi' failed: {p.stderr.strip() or p.stdout.strip()}")
    if bootstrap_pi:
        if origin_pane is None:
            log("no root pane for the pi tab; pi not started")
        else:
            p = run(bin_path, ["agent", "start", "pi", "--kind", "pi", "--pane", origin_pane["pane_id"], "--timeout", str(pi_timeout_ms)])
            if p.returncode != 0:
                log(f"pi agent start failed: {p.stderr.strip() or p.stdout.strip()}")

    # 2/3. nvim and terminal tabs.
    for label, launch in (("nvim", bootstrap_nvim), ("terminal", False)):
        args = ["tab", "create", "--workspace", wsid, "--label", label, "--no-focus"]
        if cwd:
            args += ["--cwd", cwd]
        resp = out_json(bin_path, args) or {}
        result = resp.get("result") or {}
        tab_id = (result.get("tab") or {}).get("tab_id")
        pane_id = (result.get("root_pane") or {}).get("pane_id")
        if not pane_id and tab_id:
            panes = (out_json(bin_path, ["pane", "list", "--workspace", wsid]) or {}).get("result", {}).get("panes", [])
            pane_id = next((p.get("pane_id") for p in panes if p.get("tab_id") == tab_id), None)
        if label == "nvim" and launch:
            if not pane_id:
                log("no root pane for the nvim tab; nvim not launched")
            else:
                p = run(bin_path, ["pane", "run", pane_id, *nvim_cmd])
                if p.returncode != 0:
                    log(f"nvim launch failed: {p.stderr.strip() or p.stdout.strip()}")

    log(f"workspace {wsid}: done")
    return 0


if __name__ == "__main__":
    sys.exit(main())