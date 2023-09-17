import logging
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from string import Template
from typing import Any, Dict, List, Optional, Tuple

import pykka
from mopidy.core.listener import CoreListener
from mopidy.models import Artist, Image, TlTrack, Track

from . import Extension
from . import __version__ as ext_version
from .icon import IconStore
from .notifications import DbusNotifier, Notification

logger = logging.getLogger(__name__)


def find_preferred_image(images: List[Image], preferred_size) -> Optional[Image]:
    """Find image in a list whose width is closest to `preferred_size`.

    Returns `None` if the given list is empty.
    """

    # Images may have `width` set to `None`.

    # All images that have their width set
    known_width = [i for i in images if i.width is not None]

    # All images below the preferred size
    acceptable = [i for i in known_width if i.width <= preferred_size]

    width = attrgetter("width")
    if acceptable:
        # Prefer the largest image below the maximum size.
        return max(acceptable, key=width)
    elif known_width:
        # If there are no such images, return the smallest image
        # with known size
        return min(known_width, key=width)
    elif images:
        # There's at least one image. Just pick the first.
        return images[0]
    else:
        return None


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
        logger.info("Initialized desktop notification frontend")

    @property
    def ext_config(self) -> Dict[str, Any]:
        return self.config[Extension.ext_name]

    def track_playback_started(self, tl_track: TlTrack):
        self.show_notification(tl_track)

    def track_playback_resumed(self, tl_track: TlTrack, time_position: int):
        self.show_notification(tl_track, time_position)

    def show_notification(self, tl_track: TlTrack, time_position: int = 0):
        track: Track = tl_track.track

        def preformat_artists(
            artists: List[Artist], joiner=", ", default="[Unknown Artist]"
        ):
            return joiner.join(map(attrgetter("name"), artists)) or default

        # time_position is the number of milliseconds since track start.
        timestamp = datetime.utcfromtimestamp(time_position // 1000)
        # Omit hour if the current running time is below one hour.
        time_format = "{0:%H}:{0:%M}:{0:%S}" if timestamp.hour >= 1 else "{0:%M}:{0:%S}"

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
            "time": time_format.format(timestamp),
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

    def get_images(self, track_uri: str) -> List[Image]:
        try:
            # Look up images for this track by its URL
            images: dict[str, Tuple[Image]] = self.core.library.get_images(
                [track_uri]
            ).get(timeout=5.0)
            # Images are indexed by URL, so get the list of images for this URL
            return list(images.get(track_uri, ()))
        except pykka.Timeout:
            return []

    def fetch_icon(self, track_uri: str) -> Optional[Path]:
        logger.debug(f"Fetching notification icon for {track_uri}")
        images = self.get_images(track_uri)
        logger.debug(
            "Found {} images, resolutions: {}".format(
                len(images),
                ", ".join(f"{i.width}x{i.height}" for i in images) or "N/A",
            )
        )

        preferred = find_preferred_image(
            images, preferred_size=self.ext_config["max_icon_size"]
        )
        if not preferred:
            return None
        else:
            return self.icon_store.fetch(preferred.uri)
