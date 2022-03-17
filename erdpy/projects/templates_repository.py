from pathlib import Path
import shutil
import time
from os import path

from erdpy import downloader, utils, workstation


class TemplatesRepository:
    def __init__(self, key: str, url: str, github: str, relative_path: str):
        self.key = key
        self.url = url
        self.github = github
        self.relative_path = relative_path

    def download(self):
        self._download_if_old()
        
        templates_folder = self.get_folder()
        try:
            shutil.rmtree(templates_folder)
        except FileNotFoundError:
            pass

        archive = self._get_archive_path()
        utils.unzip(archive, templates_folder)

    def _download_if_old(self):
        CACHE_DURATION = 30
        archive = self._get_archive_path()

        if path.isfile(archive):
            if time.time() - path.getmtime(archive) < CACHE_DURATION:
                return

        downloader.download(self.url, str(archive))

    def _get_archive_path(self) -> Path:
        tools_folder = workstation.get_tools_folder()
        archive = tools_folder / f"{self.key}.zip"
        return archive

    def get_folder(self) -> Path:
        tools_folder = workstation.get_tools_folder()
        folder = tools_folder / "templates" / self.key
        return folder

    def has_template(self, template: str) -> bool:
        folder = self.get_template_folder(template)
        has = folder.is_dir()
        return has

    def get_template_folder(self, template: str) -> Path:
        return self.get_payload_folder() / template

    def get_templates(self):
        templates = utils.get_subfolders(self.get_payload_folder())
        templates = [item for item in templates if self.is_template(item)]
        return templates

    def is_template(self, subfolder: str) -> bool:
        elrond_json_file = self.get_metadata_file(subfolder)
        return elrond_json_file.is_file()

    def get_metadata_file(self, template_folder: str) -> Path:
        return self.get_payload_folder() / template_folder / "elrond.json"

    def get_language(self, template: str):
        metadata_file = self.get_metadata_file(template)
        metadata = utils.read_json_file(metadata_file)
        return metadata.get("language", "unknown")


    def get_payload_folder(self) -> Path:
        return self.get_folder() / self.relative_path
