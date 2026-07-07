#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from urllib.parse import urlencode, quote


def build_nbstager_url(config: dict) -> str:
    binder_base = config.get("binder_base", "https://mybinder.org").rstrip("/")

    owner = config["owner"]
    repo = config["repo"]
    branch = config.get("branch", "main")
    notebookpath = config.get("notebookpath")

    inner = {}

    if notebookpath:
        inner["notebookpath"] = notebookpath

    for key, value in config.get("env", {}).items():
        inner[key] = value

    if config.get("data"):
        inner["data"] = json.dumps(config["data"], separators=(",", ":"))

    launch_urlpath = "launch?" + urlencode(inner)

    return (
        f"{binder_base}/v2/gh/{owner}/{repo}/{branch}"
        f"?urlpath={quote(launch_urlpath, safe='')}"
    )


def main():
    if len(sys.argv) != 2:
        print("Usage: python build_nbstager_url.py example_def.json", file=sys.stderr)
        sys.exit(1)

    config = json.loads(Path(sys.argv[1]).read_text())
    print(build_nbstager_url(config))


if __name__ == "__main__":
    main()
