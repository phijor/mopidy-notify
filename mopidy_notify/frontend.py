import logging
from operator import attrgetter
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional, Tuple

import pykka
from mopidy.core import CoreListener
from mopidy.models import Artist, Image, TlTrack, Track

from . import Extension
from . import __version__ as ext_version
from .icon import IconStore
from .notifications import DbusNotifier, Notification

logger = logging.getLogger(__name__)


class NotifyFrontend(pykka.ThreadingActor, CoreListener):
    def __init__(self, config: dict, core: pykka.ActorProxy):
        super().__init__()
        self.config: dict = config
        self.core: pykka.ActorProxy = core

        self.summary_template = Template(self.ext_config["track_summary"])
        self.message_template = Template(self.ext_config["track_message"])

        self.notifier = DbusNotifier("mopidy")
        self.icon_store = IconStore(
            hostname=self.config["http"]["hostname"],
            port=self.config["http"]["port"],
            proxy_config=self.config["proxy"],
            user_agent=f"{Extension.dist_name}/{ext_version}",
        )

    @property
    def ext_config(self) -> Dict[str, Any]:
        return self.config[Extension.ext_name]

    def track_playback_started(self, tl_track: TlTrack):
        self.show_notification(tl_track)

    def track_playback_resumed(self, tl_track: TlTrack, time_position):
        self.show_notification(tl_track)

    def show_notification(self, tl_track: TlTrack):
        track: Track
        (tl_id, track) = tl_track

        def preformat_artists(
            artists: List[Artist], joiner=", ", default="[Unknown Artist]"
        ):
            return joiner.join(map(attrgetter("name"), artists)) or default

        template_mapping = {
            "track": track.name,
            "artists": preformat_artists(track.artists),
            "album": track.album.name,
            "composers": preformat_artists(track.composers),
            "performers": preformat_artists(track.performers),
            "genre": track.genre,
            "date": track.date,
            "bitrate": track.bitrate,
            "comment": track.comment,
            "musicbrainz_id": track.musicbrainz_id,
        }

        icon = self.fetch_icon(track.uri)

        logger.debug(f"Showing notification for {track.uri} (icon: {icon})")
        notification = Notification(
            summary=self.summary_template.safe_substitute(template_mapping),
            message=self.message_template.safe_substitute(template_mapping),
            icon=icon.as_uri()
            if icon is not None
            else self.ext_config["fallback_icon"],
        )
        self.notifier.show(notification)

    def fetch_icon(self, track_uri: str) -> Optional[Path]:
        logger.debug(f"Fetching notification icon for {track_uri}")
        images: Optional[Tuple[Image]] = (
            self.core.library.get_images([track_uri]).get().get(track_uri)
        )
        logger.debug(
            "Found {} images, resolutions: {}".format(
                len(images),
                ", ".join(f"{i.width}x{i.height}" for i in images) or "N/A",
            )
        )

        if images is not None and len(images) > 0:
            acceptable = list(
                filter(lambda i: i.width <= self.ext_config["max_icon_size"], images,)
            )

            width = attrgetter("width")
            if not acceptable:
                icon = min(images, key=width)
            else:
                icon = max(acceptable, key=width)
            return self.icon_store.fetch(icon.uri)
        else:
            return None
