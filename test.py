import rich.progress

from config import settings
from download_pdf import Downloader, DownloadProgressStatus

url = "https://fsn1-speed.hetzner.com/100MB.bin"

settings.BOOKS_DIR.mkdir(parents=True, exist_ok=True)


with Downloader(url=url) as downloader:
    with rich.progress.Progress(
        "[progress.percentage]{task.percentage:>3.0f}%",
        rich.progress.SpinnerColumn(spinner_name="aesthetic"),
        rich.progress.DownloadColumn(),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TimeRemainingColumn(elapsed_when_finished=True),
    ) as progress:
        download_task = progress.add_task(
            "Download",
            total=0,
        )

        for download_progress in downloader.download():
            if download_progress.status == DownloadProgressStatus.ALREADY_DONE:
                progress.update(
                    download_task,
                    total=download_progress.total_size,
                    completed=download_progress.downloaded_size,
                )
                continue
            progress.console.print(downloader.file_name)
            progress.update(
                download_task,
                total=download_progress.total_size,
                completed=download_progress.downloaded_size,
            )
