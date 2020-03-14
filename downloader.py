
import logging
import sys
import requests

from erdpy import errors

logger = logging.getLogger("downloader")

CHUNK_SIZE = 1024 * 16


def download(url, filename):
    if url is None:
        raise errors.BadUrlError()

    logger.info(f"download_url.url: {url}")
    logger.info(f"download_url.filename: {filename}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        chunk_number = 0
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                file.write(chunk)
                _report_download_progress(chunk_number, total_size)
                chunk_number += 1
    except requests.HTTPError as err:
        raise errors.DownloadError(
            f"Could not download [{url}] to [{filename}]") from err

    logger.info("Download done.")


def _report_download_progress(chunk_number, total_size):
    num_chunks = total_size / CHUNK_SIZE + 1
    progress = int(chunk_number / num_chunks * 100)
    print(f"{progress} %", end="\r", file=sys.stderr)
