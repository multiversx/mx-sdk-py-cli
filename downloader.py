
import logging
import urllib
from os import path
from urllib.request import urlretrieve

from erdpy import config, environment, errors, utils

logger = logging.getLogger("downloader")


def download(url, filename):
    if url is None:
        raise errors.BadUrlError()

    logger.info(f"download_url.url: {url}")
    logger.info(f"download_url.filename: {filename}")

    try:
        urlretrieve(url, filename, _report_download_progress)
    except urllib.error.HTTPError as err:
        raise errors.DownloadError(
            f"Could not download [{url}] to [{filename}]") from err

    logger.info("Download done.")


def _report_download_progress(block_number, read_size, total_size):
    num_blocks = total_size / read_size + 1
    progress = int(block_number / num_blocks * 100)
    print(f"{progress} %", end="\r")
