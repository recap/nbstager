from jupyter_server.utils import url_path_join

from .handlers import LaunchHandler


def _jupyter_server_extension_points():
    return [{"module": "nbstager"}]


def _load_jupyter_server_extension(serverapp):
    web_app = serverapp.web_app
    base_url = web_app.settings["base_url"]

    # Keep the route short and platform-neutral.
    route = url_path_join(base_url, "launch")
    web_app.add_handlers(".*$", [(route, LaunchHandler)])

    serverapp.log.info("nbstager enabled at %s", route)
