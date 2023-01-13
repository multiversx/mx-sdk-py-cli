
import logging
import sys

import requests

from multiversx_sdk_cli import errors

logger = logging.getLogger("downloader")

CHUNK_SIZE = 1024 * 16
LINECLEAR = '\r' + ' ' * 20 + '\r'

PROGRESS_RULER = 'Downloading...\n|_,_,_,_,_,,_,_,_,_,_|'


def download(url: str, filename: str) -> None:
    if url is None:
        raise errors.BadUrlError()

    logger.info(f"download_url.url: {url}")
    logger.info(f"download_url.filename: {filename}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        print(PROGRESS_RULER, file=sys.stderr)
        print(' ', end='', file=sys.stderr)
        sys.stderr.flush()
        total_size = int(response.headers.get("content-length", 0))
        chunk_number = 0
        progress = 0
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                file.write(chunk)
                progress = _report_download_progress(progress, chunk_number, total_size)
                chunk_number += 1
        print('', file=sys.stderr)
        sys.stderr.flush()
    except requests.HTTPError as err:
        raise errors.DownloadError(
            f"Could not download [{url}] to [{filename}]") from err

    logger.info("Download done.")


def _report_download_progress(progress, chunk_number, total_size):
    try:
        num_chunks = int(total_size / CHUNK_SIZE)
        new_progress = int((chunk_number / num_chunks) * 20)
        if new_progress > progress:
            progress_markers = '·' * (new_progress - progress)
            print(progress_markers, end='', file=sys.stderr)
        sys.stderr.flush()
        return new_progress
    except ZeroDivisionError:
        return 0
