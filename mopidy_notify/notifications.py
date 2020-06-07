from pathlib import Path
from typing import Any, Dict, Optional, Union

import dbus

DEFAULT_TIMEOUT = -1


class Notification:
    def __init__(
        self,
        nid: int = 0,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        icon: Union[Path, str, None] = None,
        summary: str = "",
        message: str = "",
        hints: Optional[Dict[str, Any]] = None,
    ):
        self.nid: int = nid
        self.timeout: int = 0 if timeout is None else timeout
        self.icon: str = "" if icon is None else icon.as_uri() if isinstance(
            icon, Path
        ) else icon
        self.summary: str = summary
        self.message: str = message
        self.hints: dict = hints or dict()


class DbusNotifier:
    def __init__(self, appname: str, dbus: Optional[dbus.SessionBus] = None):
        self.appname: str = appname
        self.dbus = dbus or dbus.SessionBus()
        self.object = self.dbus.get_object(
            "org.freedesktop.Notifications", "/org/freedesktop/Notifications"
        )
        self.interface = self.dbus.Interface(
            self.object, dbus_interface="org.freedesktop.Notifications"
        )

    def show(self, notification: Notification):
        nid = self.interface.Notify(
            self.appname,
            notification.nid,
            notification.icon,
            notification.summary,
            notification.message,
            [],  # actions
            notification.hints,
            notification.timeout,
        )

        notification.nid = nid
