from mopidy_notify import Extension
from mopidy_notify import frontend as frontend_lib  # noqa: F401


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
