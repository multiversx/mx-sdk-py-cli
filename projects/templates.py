import logging
import os
import shutil
from os import path
from pathlib import Path

from erdpy import dependencies, environment, errors, utils
from erdpy.projects import shared
from erdpy.projects.templates_config import get_templates_repositories

logger = logging.getLogger("projects.templates")


def list_project_templates():
    templates = []

    for repo in get_templates_repositories():
        repo.download()
        templates.extend(repo.get_templates())

    templates = sorted(templates)
    print(templates)


def create_from_template(name, template_name, directory):
    logger.info("create_from_template.name: %s", name)
    logger.info("create_from_template.template_name: %s", template_name)
    logger.info("create_from_template.directory: %s", directory)

    if not directory:
        logger.info("Using current directory")
        directory = os.getcwd()

    project_directory = path.join(directory, name)

    _download_templates_repositories()
    _copy_template(template_name, project_directory)
    template = _load_as_template(project_directory)
    template.apply(name)

    logger.info("Project created, template applied.")


def _download_templates_repositories():
    for repo in get_templates_repositories():
        repo.download()


def _copy_template(template, destination_path):
    for repo in get_templates_repositories():
        if repo.has_template(template):
            repo.copy_template(template, destination_path)
            return

    raise errors.TemplateMissingError(template)


def _load_as_template(directory):
    if shared.is_source_clang(directory):
        return TemplateClang(directory)
    if shared.is_source_sol(directory):
        return TemplateSol(directory)
    if shared.is_source_rust(directory):
        return TemplateRust(directory)


class Template:
    def __init__(self, directory):
        self.directory = directory

    def apply(self, project_name):
        self.project_name = project_name
        self._extend()
        self._replace_placeholders()

    def _extend(self):
        pass

    def _replace_placeholders(self):
        pass


class TemplateClang(Template):
    pass


class TemplateRust(Template):
    def _extend(self):
        logger.info("TemplateRust._extend")

        package_path = Path(__file__).parent
        launch_file = package_path.joinpath("vscode_launch_rust.json")
        tasks_file = package_path.joinpath("vscode_tasks_rust.json")
        vscode_directory = path.join(self.directory, ".vscode")

        logger.info("Creating directory [.vscode]...")
        os.mkdir(vscode_directory)
        logger.info("Adding files: [launch.json], [tasks.json]")
        shutil.copy(launch_file, path.join(vscode_directory, "launch.json"))
        shutil.copy(tasks_file, path.join(vscode_directory, "tasks.json"))

    def _replace_placeholders(self):
        rust_module = dependencies.get_module_by_key("rust")
        self.rust_directory = rust_module.get_directory()
        self.rust_bin_directory = path.join(self.rust_directory, "bin")

        cargo_path = path.join(self.directory, "Cargo.toml")
        launch_path = path.join(self.directory, ".vscode", "launch.json")
        tasks_path = path.join(self.directory, ".vscode", "tasks.json")
        self._replace_placeholders_in_file(cargo_path)
        self._replace_placeholders_in_file(launch_path)
        self._replace_placeholders_in_file(tasks_path)

    def _replace_placeholders_in_file(self, filepath):
        content = utils.read_file(filepath)
        content = content.replace("{{PROJECT_NAME}}", self.project_name)
        content = content.replace("{{PATH_RUST_BIN}}", self.rust_bin_directory)
        content = content.replace("{{RUSTUP_HOME}}", self.rust_directory)
        content = content.replace("{{CARGO_HOME}}", self.rust_directory)
        utils.write_file(filepath, content)


class TemplateSol(Template):
    pass
