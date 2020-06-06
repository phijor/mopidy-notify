import logging
import pathlib

import pkg_resources

from mopidy import config, ext

__version__ = pkg_resources.get_distribution("Mopidy-Notify").version

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = "Mopidy-Notify"
    ext_name = "notify"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()
        # TODO: Comment in and edit, or remove entirely
        # schema["username"] = config.String()
        # schema["password"] = config.Secret()
        return schema

    def setup(self, registry):
        from .frontend import NotifyFrontend

        registry.add("frontend", NotifyFrontend)
