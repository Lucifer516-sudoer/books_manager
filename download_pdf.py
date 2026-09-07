import mimetypes
import time
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import httpx
from httpx import HTTPError, Response
from slugify import slugify

from config import settings
from errors import DownloadError


@dataclass
class Progress:
    """Progress of the download"""

    response_code: int
    """The status code of the request
    """
    downloaded_size: int = field(default=0)
    """The stream size downloaded in `bytes`
    """

    total_size: int = field(default=0)
    """The actual stream size `bytes`
    """

    @property
    def progress_percentage(self) -> float:
        """The percentage of stream downloaded, as percentage

        Returns:
            float: Progress percentage (Rounded to 5 decimals)
        """
        return round(self.downloaded_size / self.total_size * 100, 5)


class Downloader:
    def __init__(self, url: str, file_name: str | None) -> None:
        self._url = url
        self._file_name = settings.BOOKS_DIR / (
            slugify(file_name)
            if file_name is not None
            else self._manually_retrieve_file_name(self._toss_light_head())
        )
        self._chunk_size = 1024 * 12  # 12 KB

    @property
    def default_header(self) -> dict[str, str]:
        return {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/151.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,"
                "application/xhtml+xml,"
                "application/xml;q=0.9,"
                "image/avif,"
                "image/webp,"
                "image/apng,"
                "application/pdf;q=0.8,"
                "*/*;q=0.7"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }

    @property
    def url(self) -> str:
        return self._url

    @property
    def file_name(self) -> Path:
        return self._file_name

    def _toss_light_head(self) -> Response:
        with httpx.Client(
            follow_redirects=True,
            http2=True,
        ) as client:
            return client.head(self.url)

    def _accepting_ranges(self, response: Response) -> bool:
        return "bytes" in response.headers.get("Accept-Ranges").lower()

    def _manually_retrieve_file_name(self, response: Response) -> str:
        content_type = response.headers.get("Content-Type", None)
        ext = mimetypes.guess_extension(content_type)
        return (
            slugify(urlparse(self.url).netloc) + str(time.time()) + ext
            if ext is not None
            else ".pdf"
        )

    def _content_length(self, response: Response) -> int | None:
        return (
            int(response.headers.get("Content-Length"))
            if response.headers.get("Content-Length") is not None
            else None
        )

    def _download_whole(self, response: Response):
        # Check the response codes for safety
        try:
            response.raise_for_status()
        except HTTPError as err:
            raise DownloadError(
                f"Couldnt initialize the connection: {response}"
            ) from err

        # check if the file is there actually or not,
        # if self.

        if self.file_name.exists():
            ...
