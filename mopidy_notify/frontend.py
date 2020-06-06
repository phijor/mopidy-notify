import logging
from operator import attrgetter
from pathlib import Path
from typing import Optional, Tuple

import pykka
import notify2

from mopidy.core import CoreListener
from mopidy.models import TlTrack, Track, Image

from .icon import IconStore
from . import Extension, __version__ as ext_version

logger = logging.getLogger(__name__)


class NotifyFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config: dict, core: pykka.ActorProxy):
        super().__init__()
        self.config: dict = config
        self.core: pykka.ActorProxy = core
        self.notify = notify2.init("mopidy")
        self.icon_store = IconStore(
            hostname=self.config["http"]["hostname"],
            port=self.config["http"]["port"],
            proxy_config=self.config["proxy"],
            user_agent=f"{Extension.dist_name}/{ext_version}",
        )

    def track_playback_started(self, tl_track: TlTrack):
        self.show_notification(tl_track)

    def track_playback_resumed(self, tl_track: TlTrack, time_position):
        self.show_notification(tl_track)

    def show_notification(
        self, tl_track: TlTrack,
    ):
        track: Track
        (tl_id, track) = tl_track

        artists = (
            ", ".join(map(attrgetter("name"), track.artists)) or "[Unknown Artist]"
        )
        name = track.name
        album = track.album.name
        icon = self.fetch_icon(track.uri)

        logger.debug(f"Showing notification for {track.uri} (icon: {icon})")
        notification = notify2.Notification(
            summary=f"{name}",
            message=f"{artists} — {album}",
            icon=icon.as_uri() if icon is not None else "",
        )
        notification.show()

    def fetch_icon(self, track_uri: str) -> Optional[Path]:
        logger.debug(f"Fetching notification icon for {track_uri}")
        images: Optional[Tuple[Image]] = self.core.library.get_images(
            [track_uri]
        ).get().get(track_uri)
        logger.debug(
            "Found {} images, resolutions: {}".format(
                len(images), ", ".join(f"{i.width}x{i.height}" for i in images)
            )
        )

        if images is not None and len(images) > 0:
            acceptable = list(filter(lambda i: i.width <= 200, images))

            width = attrgetter("width")
            if not acceptable:
                icon = min(images, key=width)
            else:
                icon = max(acceptable, key=width)
            return self.icon_store.fetch(icon.uri)
        else:
            return None
