import shutil
import time
from os import path

from erdpy import downloader, errors, utils, workstation


class TemplatesRepository:
    def __init__(self, key, url, github, relative_path):
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

        downloader.download(self.url, archive)


    def _get_archive_path(self):
        tools_folder = workstation.get_tools_folder()
        archive = path.join(tools_folder, f"{self.key}.zip")
        return archive

    def get_folder(self):
        tools_folder = workstation.get_tools_folder()
        folder = path.join(tools_folder, "templates", self.key)
        return folder

    def has_template(self, template):
        folder = self.get_template_folder(template)
        has = path.isdir(folder)
        return has

    def get_template_folder(self, template):
        return path.join(self.get_folder(), self.relative_path, template)

    def get_templates(self):
        folder = path.join(self.get_folder(), self.relative_path)
        templates = utils.get_subfolders(folder)
        templates = [item for item in templates if self.is_template(item)]
        return templates

    def is_template(self, subfolder):
        elrond_json_file = self.get_metadata_file(subfolder)
        return path.isfile(elrond_json_file)

    def get_metadata_file(self, template_folder):
        return path.join(self.get_folder(), self.relative_path, template_folder, "elrond.json")

    def copy_template(self, template, destination_path):
        if not self.has_template(template):
            raise errors.TemplateMissingError(template)

        source_path = self.get_template_folder(template)
        shutil.copytree(source_path, destination_path)

    def get_language(self, template):
        metadata_file = self.get_metadata_file(template)
        metadata = utils.read_json_file(metadata_file)
        return metadata.get("language", "unknown")
