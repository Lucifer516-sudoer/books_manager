from dataclasses import dataclass, field

# import httpx
from httpx import Response
from slugify import slugify


@dataclass
class Progress:
    response_code: int
    downloaded_size: int = field(default=0)
    total_size: int = field(default=0)

    @property
    def progress_percentage(self) -> float:
        return round(self.downloaded_size / self.total_size * 100, 5)


class Downloader:
    def __init__(self, url: str, file_name: str) -> None:
        self._url = url
        self._file_name = slugify(file_name)

    @property
    def url(self) -> str:
        return self._url

    @property
    def file_name(self) -> str:
        return self._file_name

    def _accept_ranges(self, response: Response) -> bool:
        if response.headers.get("Accept-Ranges") == "bytes":
            return True

        return False

    async def _write_to_file(self): ...


# async def _write_to_part_file(file_name: str, stream):
#     async with open(file_name, "wb+") as file:
#         file.write
# async def download(url: str, file_name: str | None = None):
#     headers: dict[str, str] = {
#         "User-Agent": (
#             "Mozilla/5.0 (X11; Linux x86_64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/151.0.0.0 Safari/537.36"
#         ),
#         "Accept": (
#             "text/html,"
#             "application/xhtml+xml,"
#             "application/xml;q=0.9,"
#             "image/avif,"
#             "image/webp,"
#             "image/apng,"
#             "application/pdf;q=0.8,"
#             "*/*;q=0.7"
#         ),
#         "Accept-Language": "en-US,en;q=0.9",
#         "Accept-Encoding": "gzip, deflate, br",
#     }

#     if not file_name:
#         file_name = slugify(url.split("/")[-1].strip())

#     part = f"{file_name}.part"

#     async with httpx.AsyncClient(
#         follow_redirects=True,
#         http2=True,
#     ) as client:
#         async with client.stream(
#             method="GET",
#             url=url,
#             headers=headers,
#         ) as response:
#             progress = Progress(
#                 response.status_code, response.headers.get("Content-Length", 0)
#             )

#             yield progress


# url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
# output_filename = "large_document.pdf"

# # Open a client context manager and stream the content
# with httpx.Client() as client:
#     with client.stream("GET", url) as response:
#         response.raise_for_status()

#         # Open local file and write the chunks sequentially
#         with open(output_filename, "wb") as file:
#             for chunk in response.iter_bytes(chunk_size=8192):
#                 file.write(chunk)

# print("Streaming download complete!")
