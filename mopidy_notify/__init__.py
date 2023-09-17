import logging
import pathlib

from importlib.metadata import version
from mopidy import config, ext

__version__ = version("Mopidy-Notify")

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
        schema["max_icon_size"] = config.Integer(minimum=0)
        schema["fallback_icon"] = config.Path()
        schema["track_summary"] = config.String()
        schema["track_message"] = config.String()
        return schema

    def setup(self, registry):
        from .frontend import NotifyFrontend

        registry.add("frontend", NotifyFrontend)
