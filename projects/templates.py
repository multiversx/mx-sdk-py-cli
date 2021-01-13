import json
import logging
import os
from os import path

from erdpy import errors, utils
from erdpy.projects import shared
from erdpy.projects.project_rust import CargoFile
from erdpy.projects.templates_config import get_templates_repositories
from erdpy.testnet import wallets

logger = logging.getLogger("projects.templates")


def list_project_templates():
    templates = []

    for repository in get_templates_repositories():
        repository.download()
        for template in repository.get_templates():
            templates.append(TemplateSummary(template, repository))

    templates = sorted(templates, key=lambda item: item.name)

    pretty_json = json.dumps([item.__dict__ for item in templates], indent=4)
    print(pretty_json)


class TemplateSummary():
    def __init__(self, name, repository):
        self.name = name
        self.github = repository.github
        self.language = repository.get_language(name)


def create_from_template(name: str, template_name: str, directory: str):
    directory = path.expanduser(directory)

    logger.info("create_from_template.name: %s", name)
    logger.info("create_from_template.template_name: %s", template_name)
    logger.info("create_from_template.directory: %s", directory)

    if not directory:
        logger.info("Using current directory")
        directory = os.getcwd()

    project_directory = path.join(directory, name)
    if path.exists(project_directory):
        raise errors.BadDirectory(project_directory)

    _download_templates_repositories()
    _copy_template(template_name, project_directory)

    template = _load_as_template(project_directory)
    template.apply(template_name, name)

    logger.info("Project created, template applied.")

    wallets.copy_all_to(path.join(project_directory, "wallets"))

    logger.info("Test wallets have been copied into the project.")


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
        self._patch()

    def _patch(self):
        """Implemented by derived classes"""
        pass


class TemplateClang(Template):
    pass


class TemplateRust(Template):
    CARGO_TOML = "Cargo.toml"

    def _patch(self):
        logger.info("Patching cargo files...")
        self._patch_cargo()
        self._patch_cargo_wasm()
        self._patch_cargo_abi()

        logger.info("Patching source code...")
        self._patch_source_code_wasm()
        self._patch_source_code_abi()
        self._patch_source_code_tests()

        logger.info("Patching test files...")
        self._patch_mandos_tests()

    def _patch_cargo(self):
        cargo_path = path.join(self.directory, TemplateRust.CARGO_TOML)

        cargo_file = CargoFile(cargo_path)
        cargo_file.package_name = self.project_name
        cargo_file.version = "0.0.0"
        cargo_file.authors = ["you"]
        cargo_file.edition = "2018"
        cargo_file.publish = False

        for dependency in cargo_file.get_dependencies().values():
            del dependency["path"]
        for dependency in cargo_file.get_dev_dependencies().values():
            del dependency["path"]

        cargo_file.save()

    def _patch_cargo_wasm(self):
        cargo_path = path.join(self.directory, "wasm", TemplateRust.CARGO_TOML)

        cargo_file = CargoFile(cargo_path)
        cargo_file.package_name = f"{self.project_name}-wasm"
        cargo_file.version = "0.0.0"
        cargo_file.authors = ["you"]
        cargo_file.edition = "2018"
        cargo_file.publish = False

        for dependency in cargo_file.get_dependencies().values():
            del dependency["path"]
        # Currently, the following logic is not really needed (we don't have dev-dependencies in wasm/Cargo.toml):
        for dependency in cargo_file.get_dev_dependencies().values():
            del dependency["path"]

        # Patch the path towards the project crate (one folder above):
        cargo_file.get_dependency(self.template_name)["path"] = ".."

        cargo_file.save()

        self._replace_in_files(
            [cargo_path],
            [
                (f"[dependencies.{self.template_name}]", f"[dependencies.{self.project_name}]")
            ]
        )

    def _patch_cargo_abi(self):
        cargo_path = path.join(self.directory, "abi", TemplateRust.CARGO_TOML)
        if not path.isfile(cargo_path):
            return

        cargo_file = CargoFile(cargo_path)
        cargo_file.package_name = f"{self.project_name}-abi"
        cargo_file.version = "0.0.0"
        cargo_file.authors = ["you"]
        cargo_file.edition = "2018"
        cargo_file.publish = False

        for dependency in cargo_file.get_dependencies().values():
            del dependency["path"]
        for dependency in cargo_file.get_dev_dependencies().values():
            del dependency["path"]

        # Patch the path towards the project crate (one folder above):
        cargo_file.get_dependency(self.template_name)["path"] = ".."

        cargo_file.save()

        self._replace_in_files(
            [cargo_path],
            [
                (f"[dependencies.{self.template_name}]", f"[dependencies.{self.project_name}]")
            ]
        )

    def _patch_source_code_wasm(self):
        lib_path = path.join(self.directory, "wasm", "src", "lib.rs")

        self._replace_in_files(
            [lib_path],
            [
                (f"use {self.template_name.replace('-', '_')}::*", f"use {self.project_name.replace('-', '_')}::*")
            ]
        )

    def _patch_source_code_abi(self):
        abi_main_path = path.join(self.directory, "abi", "src", "main.rs")
        if not path.exists(abi_main_path):
            return

        self._replace_in_files(
            [abi_main_path],
            [
                # Example: replace "use simple-erc20::*" to "use my_token::*"
                (f"use {self.template_name.replace('-', '_')}::*", f"use {self.project_name.replace('-', '_')}::*")
            ]
        )

    def _patch_source_code_tests(self):
        test_dir_path = path.join(self.directory, "tests")
        if not path.isdir(test_dir_path):
            return

        test_paths = utils.list_files(test_dir_path)
        self._replace_in_files(
            test_paths,
            [
                # Example: replace "use simple-erc20::*" to "use my_token::*"
                (f"use {self.template_name.replace('-', '_')}::*", f"use {self.project_name.replace('-', '_')}::*"),
                # Example: replace "extern crate adder;" to "extern crate myadder"
                (f"extern crate {self.template_name.replace('-', '_')};", f"extern crate {self.project_name.replace('-', '_')};")
            ]
        )

    def _patch_mandos_tests(self):
        test_dir_path = path.join(self.directory, "mandos")
        if not path.isdir(test_dir_path):
            return

        test_paths = [e for e in utils.list_files(test_dir_path, suffix=".json")]
        self._replace_in_files(
            test_paths,
            [
                (f"{self.template_name}.wasm", f"{self.project_name.replace('-', '_')}.wasm")
            ]
        )

        for file in test_paths:
            data = utils.read_json_file(file)
            # Patch fields
            data["name"] = data.get("name", "").replace(self.template_name, self.project_name)
            utils.write_json_file(file, data)

    def _replace_in_files(self, files, replacements):
        for file in files:
            content = utils.read_file(file)

            for to_replace, replacement in replacements:
                content = content.replace(to_replace, replacement)

            utils.write_file(file, content)


class TemplateSol(Template):
    pass
