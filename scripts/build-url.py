#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from urllib.parse import urlencode, quote

DEFAULTS = {
    "urlpath": "launch",
    "branch": "main",
    "cleanup": False,
    "overwrite": True,
    "run_postbuild": False,
}


def build_url(cfg: dict) -> str:
    inner = {"repo": cfg["target_repo"]}

    if cfg.get("branch") and cfg["branch"] != DEFAULTS["branch"]:
        inner["branch"] = cfg["branch"]

    if cfg.get("notebook_path"):
        inner["notebookpath"] = cfg["notebook_path"]

    if cfg.get("cleanup", DEFAULTS["cleanup"]) != DEFAULTS["cleanup"]:
        inner["cleanup"] = "1" if cfg["cleanup"] else "0"

    if cfg.get("overwrite", DEFAULTS["overwrite"]) != DEFAULTS["overwrite"]:
        inner["overwrite"] = "1" if cfg["overwrite"] else "0"

    if cfg.get("run_postbuild", DEFAULTS["run_postbuild"]) != DEFAULTS["run_postbuild"]:
        inner["run_postbuild"] = "1" if cfg["run_postbuild"] else "0"

    for key, value in cfg.get("env", {}).items():
        inner[key] = value

    if cfg.get("data_files"):
        inner["data"] = json.dumps(cfg["data_files"], separators=(",", ":"))

    inner_urlpath = f"{DEFAULTS['urlpath']}?{urlencode(inner)}"

    binder_base = cfg["binder_base"].rstrip("/")
    return (
        f"{binder_base}/v2/gh/{cfg['launcher_repo']}/{cfg['launcher_ref']}"
        f"?urlpath={quote(inner_urlpath, safe='')}"
    )


def main():
    if len(sys.argv) != 2:
        print("Usage: build-url.py launch.json", file=sys.stderr)
        raise SystemExit(1)

    cfg = json.loads(Path(sys.argv[1]).read_text())
    print(build_url(cfg))


if __name__ == "__main__":
    main()
