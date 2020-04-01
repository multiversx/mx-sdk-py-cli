import json
import logging
import os
import shutil
from datetime import date
from os import path
from pathlib import Path

from erdpy import dependencies, errors, utils
from erdpy.projects import shared
from erdpy.projects.project_rust import CargoFile
from erdpy.projects.templates_config import get_templates_repositories
from texttable import Texttable

logger = logging.getLogger("projects.templates")


def list_project_templates(as_json=False):
    templates = []

    for repository in get_templates_repositories():
        repository.download()
        for template in repository.get_templates():
            templates.append(TemplateSummary(template, repository))

    templates = sorted(templates, key=lambda item: item.name)

    if as_json:
        pretty_json = json.dumps([item.__dict__ for item in templates], indent=4)
        print(pretty_json)
    else:
        table = Texttable()
        table_data = [["Name", "Github", "Language"]]
        table_data.extend([[item.name, item.github, item.language] for item in templates])
        table.add_rows(table_data)
        print(table.draw())


class TemplateSummary():
    def __init__(self, name, repository):
        self.name = name
        self.github = repository.github
        self.language = repository.get_language(name)


def create_from_template(name, template_name, directory):
    directory = path.expanduser(directory)

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
    template.apply(template_name, name)

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

    def apply(self, template_name, project_name):
        self.template_name = template_name
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
        cargo_debug_path = path.join(self.directory, "debug", "Cargo.toml")
        launch_path = path.join(self.directory, ".vscode", "launch.json")
        tasks_path = path.join(self.directory, ".vscode", "tasks.json")
        debug_main_path = path.join(self.directory, "debug", "src", "main.rs")

        logger.info("Updating cargo files...")

        cargo_file = CargoFile(cargo_path)
        cargo_file.package_name = self.project_name
        cargo_file.version = "0.0.1"
        cargo_file.authors = ["you"]
        cargo_file.edition = "2018"
        cargo_file.save()

        cargo_file_debug = CargoFile(cargo_debug_path)
        cargo_file_debug.package_name = f"{self.project_name}-debug"
        cargo_file_debug.version = "0.0.1"
        cargo_file_debug.authors = ["you"]
        cargo_file_debug.edition = "2018"
        cargo_file_debug.save()

        logger.info("Applying replacements...")

        self._replace_in_files(
            [launch_path, tasks_path],
            [
                ("{{PROJECT_NAME}}", self.project_name),
                ("{{PATH_RUST_BIN}}", self.rust_bin_directory),
                ("{{RUSTUP_HOME}}", self.rust_directory),
                ("{{CARGO_HOME}}", self.rust_directory)
            ])

        self._replace_in_files(
            [debug_main_path],
            [
                # Example "use simple_coin::*" to "use my_project::*"
                (f"use {self.template_name.replace('-', '_')}::*", f"use {self.project_name.replace('-', '_')}::*")
            ]
        )

        self._replace_in_files(
            [cargo_debug_path],
            [
                (f"[dependencies.{self.template_name}]", f"[dependencies.{self.project_name}]")
            ]
        )

    def _replace_in_files(self, files, replacements):
        for file in files:
            content = utils.read_file(file)

            for to_replace, replacement in replacements:
                content = content.replace(to_replace, replacement)

            utils.write_file(file, content)


class TemplateSol(Template):
    pass
