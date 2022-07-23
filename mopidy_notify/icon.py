import logging
import os
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import quote, urljoin

import requests
from mopidy import httpclient

logger = logging.getLogger(__name__)

CACHE_LOCATION = next(
    Path(path) / __name__
    for path in [os.environ.get("XDG_RUNTIME_DIR"), os.environ.get("TMP"), "/tmp"]
    if path is not None
)


class IconStore:
    def __init__(
        self,
        hostname: str,
        port: int,
        proxy_config: Dict[str, str],
        user_agent: str,
    ):
        self.cache_location: Path = self._init_cache_location()
        self.hostname: str = hostname
        self.port: int = port
        self.http_session: requests.Session = self._init_http_session(
            proxy=httpclient.format_proxy(proxy_config),
            user_agent=httpclient.format_user_agent(user_agent),
        )

    @staticmethod
    def _init_cache_location() -> Path:
        CACHE_LOCATION.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Caching icons at {CACHE_LOCATION}")
        return CACHE_LOCATION

    @staticmethod
    def _init_http_session(proxy: Optional[str], user_agent: str) -> requests.Session:
        session = requests.Session()
        if proxy:
            session.proxies.update({"http": proxy, "https": proxy})
        session.headers.update({"user-agent": user_agent})
        return session

    def fetch(self, uri: str) -> Path:
        icon_path = self.format_cache_target(uri)
        if not icon_path.exists():
            full_http_uri = self.format_uri(uri)
            logger.debug(f"Fetching icon from {full_http_uri} => {icon_path}")
            response = self.http_session.get(full_http_uri)
            with open(icon_path, mode="wb") as f:
                f.write(response.content)
        else:
            logger.debug(f"Found cached icon for {uri} at {icon_path}")

        return icon_path

    def format_uri(self, uri: str) -> str:
        return urljoin(f"http://{self.hostname}:{self.port}/", uri)

    def format_cache_target(self, uri: str) -> Path:
        return self.cache_location / quote(uri, safe="")
