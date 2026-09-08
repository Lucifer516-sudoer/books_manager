import datetime
import mimetypes
from collections.abc import AsyncGenerator, Generator
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Self
from urllib.parse import urlparse

import aiofiles
import httpx
from httpx import HTTPError, Response
from slugify import slugify

from config import settings
from errors import DownloadError


class DownloadProgressStatus(StrEnum):
    ON_GOING = "on_going"
    DONE = "done"
    YET_TO = "yet_to"
    ALREADY_DONE = "already_done"


@dataclass
class Progress:
    """Progress of the download"""

    response_code: int
    """The status code of the request"""
    status: DownloadProgressStatus = field(
        default=DownloadProgressStatus.YET_TO
    )
    """Downloading status, as download progresses"""

    downloaded_size: int = field(default=0)
    """The stream size downloaded in `bytes`"""

    total_size: int = field(default=0)
    """The actual stream size `bytes`"""

    @property
    def progress_percentage(self) -> float:
        """The percentage of stream downloaded, as percentage

        Returns:
            float: Progress percentage (Rounded to 5 decimals)
        """
        return (
            round(self.downloaded_size / self.total_size * 100, 5)
            if self.total_size > 0
            else 0
        )


class Downloader:
    def __init__(self, url: str, file_name: str | None = None) -> None:
        self._url = url
        self._file_name = settings.BOOKS_DIR / (
            slugify(file_name)
            if file_name is not None
            else self._manually_retrieve_file_name()
        )
        self._chunk_size = 1024 * 12  # 12 KB

    @property
    def default_header(self) -> dict[str, Any]:
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

    def _retrieve_response(self) -> Response | None:
        with httpx.Client(
            follow_redirects=True,
            headers=self.default_header,
        ) as client:
            try:
                return client.get(self.url)
            except (httpx.RemoteProtocolError, httpx.HTTPError):
                return None

    def _supports_ranges(self, response: Response | None = None) -> bool:
        if response is None:
            response = self.client.get(
                self.url, headers={"Range": "bytes=0-0"}
            )
        return (
            response.status_code == int(httpx.codes.PARTIAL_CONTENT)
            and "Content-Range" in response.headers
        )

    def _manually_retrieve_file_name(
        self, response: Response | None = None
    ) -> str:
        if response:
            content_type = response.headers.get(
                "Content-Type", "application/pdf"
            )  # a sensible default
        else:
            content_type = "application/pdf"

        ext = mimetypes.guess_extension(content_type)
        print(ext)
        return (
            slugify(urlparse(self.url).netloc)
            + str(datetime.datetime.now().strftime("_%d_%m_%Y__%H_%M_%S"))
            + ext
            if ext is not None
            else ".pdf"
        )

    def _content_length(self, response: Response) -> int:
        """Used to retrieve the size of the file when downloading in whole"""
        return (
            int(response.headers.get("Content-Length"))
            if response.headers.get("Content-Length") is not None
            else 0
        )

    async def _async_download_whole(
        self, response: Response, *, replace: bool = False
    ) -> AsyncGenerator[Progress, None]:
        # Check the response codes for safety
        try:
            response.raise_for_status()
        except HTTPError as err:
            raise DownloadError(
                f"Couldnt initialize the connection: {response}"
            ) from err

        # check if the file is there actually or not,
        # if self.
        async def download_the_bloody_file(
            response: Response,
        ):
            # A small Tribute to Captain Jacksparrow
            progress = Progress(
                response_code=response.status_code,
                status=DownloadProgressStatus.ON_GOING,
                downloaded_size=0,
                total_size=self._content_length(response=response),
            )
            async with aiofiles.open(self.file_name, "wb+") as file:
                async for content in response.aiter_bytes(self._chunk_size):
                    await file.write(content)
                    progress.downloaded_size += len(content)
                    yield progress

        if self.file_name.exists() and not replace:
            file_size = self.file_name.stat().st_size
            yield Progress(
                response_code=response.status_code,
                status=DownloadProgressStatus.ALREADY_DONE,
                downloaded_size=file_size,
                total_size=file_size,
            )
        else:
            async for progress in download_the_bloody_file(response):
                yield progress

    def _download_whole(
        self, response: Response, *, replace: bool = False
    ) -> Generator[Progress, Any, None]:
        # Check the response codes for safety
        try:
            response.raise_for_status()
        except HTTPError as err:
            raise DownloadError(
                f"Couldnt initialize the connection: {response}"
            ) from err

        # check if the file is there actually or not,
        # if self.
        def download_the_bloody_file(
            response: Response,
        ) -> Generator[Progress, None, None]:
            # A small Tribute to Captain Jacksparrow
            progress = Progress(
                response_code=response.status_code,
                status=DownloadProgressStatus.ON_GOING,
                downloaded_size=0,
                total_size=self._content_length(response=response),
            )
            with Path.open(self.file_name, "wb+") as file:
                for content in response.iter_bytes(self._chunk_size):
                    file.write(content)
                    progress.downloaded_size = file.tell()
                    yield progress

        if self.file_name.exists() and not replace:
            yield Progress(
                response_code=response.status_code,
                status=DownloadProgressStatus.ALREADY_DONE,
                downloaded_size=self.file_name.stat().st_size,
                total_size=self.file_name.stat().st_size,
            )
        else:
            yield from download_the_bloody_file(response)

    def _download_in_parts(self):
        part_file = Path(str(self.file_name) + ".part")
        seek_point = part_file.stat().st_size if part_file.exists() else 0

        with self.client.stream(
            "GET", self.url, headers={"Range": f"bytes={seek_point}-"}
        ) as response:
            if response.status_code != int(httpx.codes.PARTIAL_CONTENT):
                raise DownloadError(
                    "Server did not have the courtesy to honor the range "
                    f"request: {response.status_code}"
                )
            total_size = int(
                response.headers["Content-Range"].rsplit("/", 1)[1]
            )
            if total_size == seek_point and part_file.rename(self.file_name):
                yield Progress(
                    response_code=response.status_code,
                    status=DownloadProgressStatus.ALREADY_DONE,
                    downloaded_size=total_size,
                    total_size=total_size,
                )
            with Path.open(part_file, "ab") as file:
                progress = Progress(
                    response_code=response.status_code,
                    status=DownloadProgressStatus.ON_GOING,
                    downloaded_size=seek_point,
                    total_size=total_size,
                )

                for content in response.iter_bytes(self._chunk_size):
                    progress.downloaded_size += len(content)
                    file.write(content)

                    if progress.downloaded_size == progress.total_size:
                        progress.status = DownloadProgressStatus.DONE
                        part_file.rename(self.file_name)
                    yield progress

    def download(self) -> Generator[Progress, None, None]:
        with self.client.stream("GET", self.url) as response:
            yield from self._download_whole(response)

    #
    # Context Manager stuffs
    #
    def __enter__(self) -> Self:
        self.client = httpx.Client(
            headers=self.default_header, follow_redirects=True
        )

        return self

    async def __aenter__(self) -> Self:
        self.async_client = httpx.AsyncClient(
            headers=self.default_header, follow_redirects=True
        )
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore
        self.client.close()

    async def __aexit__(self, exc_type, exc, tb):  # type: ignore
        await self.async_client.aclose()
