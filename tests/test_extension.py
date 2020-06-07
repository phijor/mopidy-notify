from unittest import mock

from mopidy_notify import Extension
from mopidy_notify import frontend as frontend_lib


def test_get_default_config():
    ext = Extension()

    config = ext.get_default_config()

    assert "[notify]" in config
    assert "enabled = true" in config


def test_get_config_schema():
    ext = Extension()

    schema = ext.get_config_schema()

    assert "max_icon_size" in schema
    assert "fallback_icon" in schema
    assert "track_summary" in schema
    assert "track_message" in schema


def test_setup():
    registry = mock.Mock()

    ext = Extension()
    ext.setup(registry)

    calls = [mock.call("frontend", frontend_lib.NotifyFrontend)]
    registry.add.assert_has_calls(calls, any_order=True)
