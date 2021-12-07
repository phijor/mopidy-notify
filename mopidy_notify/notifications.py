from pathlib import Path
from typing import Any, Dict, Optional, Union

from pydbus import SessionBus

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
        self.icon: str = (
            "" if icon is None else icon.as_uri() if isinstance(icon, Path) else icon
        )
        self.summary: str = summary
        self.message: str = message
        self.hints: dict = hints or dict()


class DbusNotifier:
    def __init__(self, appname: str, session_bus: Optional[SessionBus] = None):
        self.appname: str = appname
        self.session_bus = session_bus or SessionBus()
        self.notifications = self.session_bus.get(".Notifications")

    def show(self, notification: Notification):
        nid = self.notifications.Notify(
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
