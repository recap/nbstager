import json
import os
import shlex
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import tornado.web
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join

WORKSPACE_DIR_NAME = "workspace"
ENV_PREFIX = ""

RESERVED_PARAMS = {
    "repo",
    "branch",
    "urlpath",
    "notebookpath",
    "targetpath",
    "overwrite",
    "cleanup",
    "data",
    "run_postbuild",
    "install_r_deps",
}


def get_server_root(handler: JupyterHandler) -> Path:
    root = handler.settings.get("server_root_dir")
    if root is None:
        root = handler.contents_manager.root_dir
    return Path(os.path.expanduser(root)).resolve()


def is_safe_relative_path(path: str) -> bool:
    p = Path(path)
    return not p.is_absolute() and ".." not in p.parts


def filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or "downloaded_file"


def stage_data_files(work: Path, data_json: str | None, log):
    if not data_json:
        log.info("No data staging requested")
        return

    try:
        specs = json.loads(data_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid data JSON: {exc}") from exc

    if isinstance(specs, dict):
        specs = [specs]

    if not isinstance(specs, list):
        raise ValueError("data must be a JSON object or a JSON array of objects")

    manifest = []

    for i, spec in enumerate(specs):
        if not isinstance(spec, dict):
            raise ValueError(f"data[{i}] must be an object")

        url = spec.get("url")
        if not url:
            raise ValueError(f"data[{i}] is missing required field 'url'")

        parsed = urlparse(url)
        if parsed.scheme not in {"https", "http"}:
            raise ValueError(f"Unsupported URL scheme for {url!r}")

        relative_path = spec.get("path") or filename_from_url(url)
        if not is_safe_relative_path(relative_path):
            raise ValueError(f"Unsafe data path: {relative_path!r}")

        dest = work / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        log.info("Staging data file %s -> %s", url, dest)
        with urllib.request.urlopen(url, timeout=60) as response:
            dest.write_bytes(response.read())

        manifest.append({
            "url": url,
            "path": str(dest.relative_to(work)),
            "size": dest.stat().st_size,
        })

    manifest_path = work / "data_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    log.info("Wrote data manifest: %s", manifest_path)


def shell_escape_env_value(value: str) -> str:
    return shlex.quote(value)


def write_env(env_file: Path, params: dict[str, str], log):
    log.info("Writing environment file: %s", env_file)

    lines = []
    for key, value in sorted(params.items()):
        env_key = ENV_PREFIX + key.upper().replace("-", "_")
        if not env_key.replace("_", "").isalnum():
            log.warning("Skipping invalid parameter %r -> %r", key, env_key)
            continue
        lines.append(f"{env_key}={shell_escape_env_value(value)}")

    env_file.parent.mkdir(parents=True, exist_ok=True)
    env_file.write_text("\n".join(lines) + "\n")
    log.info("Wrote %s (%d bytes)", env_file, env_file.stat().st_size)


class LaunchHandler(JupyterHandler):
    @tornado.web.authenticated
    def get(self):
        urlpath = self.get_argument("urlpath", "lab/tree")
        notebookpath = self.get_argument("notebookpath")

        data_json = self.get_argument("data", None)

        server_root = get_server_root(self)
        env_file = server_root / ".env"

        params = {}
        for key, values in self.request.query_arguments.items():
            if key not in RESERVED_PARAMS:
                params[key] = values[-1].decode("utf-8")

        try:
            write_env(env_file, params, self.log)
            stage_data_files(server_root, data_json, self.log)

        except Exception as exc:
            self.set_status(500)
            self.finish({"status": "error", "message": str(exc)})
            return

        redirect_url = (
            url_path_join(self.base_url, urlpath, notebookpath)
            if notebookpath
            else url_path_join(self.base_url, urlpath)
        )

        self.log.info("Redirecting to %s", redirect_url)
        self.redirect(redirect_url)
    # def get(self):
    #     urlpath = self.get_argument("urlpath", "lab/tree")
    #     notebookpath = self.get_argument("notebookpath", None)
    #     data_json = self.get_argument("data", None)
    #
    #     server_root = get_server_root(self)
    #     work = server_root 
    #     env_file = work / ".env"
    #
    #     params = {}
    #     for key, values in self.request.query_arguments.items():
    #         if key in RESERVED_PARAMS:
    #             continue
    #         params[key] = values[-1].decode("utf-8")
    #
    #     try:
    #         write_env(env_file, params, self.log)
    #         stage_data_files(work, data_json, self.log)
    #
    #     except Exception as exc:
    #         self.set_status(500)
    #         self.finish({"status": "error", "message": str(exc)})
    #         return
    #
    #     if notebookpath:
    #         redirect_url = url_path_join(self.base_url, urlpath, work, notebookpath)
    #     else:
    #         redirect_url = url_path_join(self.base_url, urlpath, work)
    #
    #     self.log.info("Redirecting to %s", redirect_url)
    #     self.redirect(redirect_url)
