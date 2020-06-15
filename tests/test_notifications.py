from pathlib import Path
from unittest import mock

from mopidy_notify.notifications import DEFAULT_TIMEOUT, DbusNotifier, Notification


def test_notification_default_timeout():
    assert Notification().timeout == DEFAULT_TIMEOUT


def test_notification_no_timeout_conversion():
    assert Notification(timeout=None).timeout == 0


def test_notification_icon_default():
    assert Notification().icon == ""


def test_notification_icon_named():
    name = "named-icon-foobar"
    assert Notification(icon=name).icon == name


def test_notification_icon_path_uri():
    path = "/foo/bar"
    assert Notification(icon=Path(path)).icon == f"file://{path}"


def test_notification_no_hints():
    assert Notification().hints == dict()


def test_notification_some_hints():
    hints = {"category": "foo"}
    assert Notification(hints=hints).hints == hints


def test_notifier_show_update_id():
    session_bus = mock.Mock()

    notifier = DbusNotifier(appname="test", session_bus=session_bus)

    ID = 1337
    notification = Notification()

    notifier.notifications = mock.Mock(**{"Notify.return_value": ID})
    notifier.show(notification)
    notifier.notifications.Notify.assert_called_once()

    assert notification.nid == ID
