import shutil
from os import path

from erdpy import downloader, errors, utils, workstation
from erdpy.projects import shared


class TemplatesRepository:
    def __init__(self, key, url, github, relative_path):
        self.key = key
        self.url = url
        self.github = github
        self.relative_path = relative_path

    def download(self):
        archive = self._get_archive_path()
        downloader.download(self.url, archive)
        templates_folder = self.get_folder()
        try:
            shutil.rmtree(templates_folder)
        except FileNotFoundError:
            pass
        utils.unzip(archive, templates_folder)

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
        return path.join(self.get_folder(), self.relative_path,  template)

    def get_templates(self):
        folder = path.join(self.get_folder(), self.relative_path)
        templates = utils.get_subfolders(folder)
        return templates

    def copy_template(self, template, destination_path):
        if not self.has_template(template):
            raise errors.TemplateMissingError(template)

        source_path = self.get_template_folder(template)
        shutil.copytree(source_path, destination_path)

    def get_language(self, template):
        directory = self.get_template_folder(template)

        if shared.is_source_clang(directory):
            return "C / C++"
        if shared.is_source_sol(directory):
            return "Solidity"
        if shared.is_source_rust(directory):
            return "Rust"
        return "unknown"
