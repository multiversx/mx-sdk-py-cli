import json
import logging
import os
from pathlib import Path
import shutil
from typing import Any, List, Tuple

from erdpy import errors, utils
from erdpy.projects import shared
from erdpy.projects.project_rust import CargoFile
from erdpy.projects.templates_config import get_templates_repositories
from erdpy.projects.templates_repository import TemplatesRepository

logger = logging.getLogger("projects.templates")
ERDJS_SNIPPETS_FOLDER_NAME = "erdjs-snippets"


def list_project_templates():
    summaries: List[TemplateSummary] = []

    for repository in get_templates_repositories():
        repository.download()
        for template in repository.get_templates():
            summaries.append(TemplateSummary(template, repository))

    summaries = sorted(summaries, key=lambda item: item.name)

    pretty_json = json.dumps([item.__dict__ for item in summaries], indent=4)
    print(pretty_json)


class TemplateSummary():
    def __init__(self, name: str, repository: TemplatesRepository):
        self.name = name
        self.github = repository.github
        self.language = repository.get_language(name)


def create_from_template(project_name: str, template_name: str, directory: Path):
    directory = directory.expanduser()

    logger.info("create_from_template.project_name: %s", project_name)
    logger.info("create_from_template.template_name: %s", template_name)
    logger.info("create_from_template.directory: %s", directory)

    if not directory:
        logger.info("Using current directory")
        directory = Path.cwd()

    project_directory = Path(directory) / project_name
    if project_directory.exists():
        raise errors.BadDirectory(str(project_directory))

    _download_templates_repositories()
    _copy_template(template_name, project_directory, project_name)

    template = _load_as_template(project_directory)
    template.apply(template_name, project_name)

    logger.info("Project created, template applied.")


def _download_templates_repositories():
    for repo in get_templates_repositories():
        repo.download()


def _copy_template(template: str, destination_path: Path, project_name: str):
    for repo in get_templates_repositories():
        if repo.has_template(template):
            source_path = repo.get_template_folder(template)
            shutil.copytree(source_path, destination_path)
            _copy_erdjs_snippets(template, repo.get_payload_folder(), destination_path, project_name)
            return

    raise errors.TemplateMissingError(template)


def _copy_erdjs_snippets(template: str,  templates_payload_folder: Path, destination_path: Path, project_name: str):
    source_erdjs_snippets_folder = templates_payload_folder / ERDJS_SNIPPETS_FOLDER_NAME
    source_erdjs_snippets_subfolder = source_erdjs_snippets_folder / template
    destination_erdjs_snippets_folder = destination_path.parent / ERDJS_SNIPPETS_FOLDER_NAME
    no_snippets = not source_erdjs_snippets_subfolder.is_dir()

    logger.info(f"_copy_erdjs_snippets, source_erdjs_snippets_subfolder: {source_erdjs_snippets_subfolder}")
    logger.info(f"_copy_erdjs_snippets, destination_erdjs_snippets_folder: {destination_erdjs_snippets_folder}")

    if no_snippets:
        logger.info(f"_copy_erdjs_snippets: no snippets in template {template}")
        return

    utils.ensure_folder(destination_erdjs_snippets_folder)

    # Copy snippets to destination
    # First, copy the subfolder associated with the template
    shutil.copytree(source_erdjs_snippets_subfolder, destination_erdjs_snippets_folder / project_name)

    # After that, copy the remaining files from the source folder - not recursively (on purpose).
    for file in os.listdir(source_erdjs_snippets_folder):
        source_file = source_erdjs_snippets_folder / file
        destination_file = destination_erdjs_snippets_folder / file
        should_copy = source_file.is_file() and not destination_file.exists()

        if should_copy:
            logger.info(f"_copy_erdjs_snippets, file: {file}")
            shutil.copy(source_file, destination_file)


def _load_as_template(directory: Path):
    if shared.is_source_clang(directory):
        return TemplateClang(directory)
    if shared.is_source_rust(directory):
        return TemplateRust(directory)
    raise errors.BadTemplateError(directory)


class Template:
    def __init__(self, directory: Path):
        self.directory = directory

    def apply(self, template_name: str, project_name: str):
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
        self._patch_sub_crate("wasm")
        self._patch_sub_crate("abi")
        self._patch_sub_crate("meta")

        logger.info("Patching source code...")
        self._patch_source_code_files([
            self.directory / "abi" / "src" / "main.rs",
            self.directory / "wasm" / "src" / "lib.rs",
            self.directory / "meta" / "src" / "main.rs",
        ], ignore_missing=True)
        self._patch_source_code_tests()

        logger.info("Patching test files...")
        self._patch_mandos_tests()

    def _patch_cargo(self):
        cargo_path = self.directory / TemplateRust.CARGO_TOML

        cargo_file = CargoFile(cargo_path)
        cargo_file.package_name = self.project_name
        cargo_file.version = "0.0.0"
        cargo_file.authors = ["you"]
        cargo_file.edition = "2018"
        cargo_file.publish = False

        remove_path_from_dependencies(cargo_file)

        cargo_file.save()

    def _patch_sub_crate(self, sub_name: str) -> None:
        cargo_path = self.directory / sub_name / TemplateRust.CARGO_TOML
        if not cargo_path.is_file():
            return

        cargo_file = CargoFile(cargo_path)
        cargo_file.package_name = f"{self.project_name}-{sub_name}"
        cargo_file.version = "0.0.0"
        cargo_file.authors = ["you"]
        cargo_file.edition = "2018"
        cargo_file.publish = False

        remove_path_from_dependencies(cargo_file)

        # Patch the path towards the project crate (one folder above):
        cargo_file.get_dependency(self.template_name)["path"] = ".."

        cargo_file.save()

        self._replace_in_files(
            [cargo_path],
            [
                (f"[dependencies.{self.template_name}]", f"[dependencies.{self.project_name}]")
            ],
            ignore_missing=False
        )

    def _with_underscores(self, name: str) -> str:
        return name.replace('-', '_')

    def _patch_source_code_files(self, source_paths: List[Path], ignore_missing: bool) -> None:
        template_name = self._with_underscores(self.template_name)
        project_name = self._with_underscores(self.project_name)

        self._replace_in_files(
            source_paths,
            [
                # Example: replace "use simple_erc20::*" to "use my_token::*"
                (f"use {template_name}::*", f"use {project_name}::*"),
                # Example: replace "<simple_erc20::AbiProvider>()" to "<my_token::AbiProvider>()"
                (f"<{template_name}::AbiProvider>()", f"<{project_name}::AbiProvider>()"),
                # Example: replace "extern crate adder;" to "extern crate myadder;"
                (f"extern crate {template_name};", f"extern crate {project_name};"),
                # Example: replace "empty::ContractObj" to "foo_bar::ContractObj"
                (f"{template_name}::ContractObj", f"{project_name}::ContractObj"),
                (f"{template_name}::ContractBuilder", f"{project_name}::ContractBuilder"),
                (f"{template_name}::contract_obj", f"{project_name}::contract_obj"),
            ],
            ignore_missing
        )

    def _patch_source_code_tests(self):
        test_dir_path = self.directory / "tests"
        if not test_dir_path.is_dir():
            return

        test_paths = utils.list_files(test_dir_path)
        self._patch_source_code_files(test_paths, ignore_missing=False)

    def _patch_mandos_tests(self):
        test_dir_path = self.directory / "mandos"
        if not test_dir_path.is_dir():
            return

        test_paths = utils.list_files(test_dir_path, suffix=".json")
        self._replace_in_files(
            test_paths,
            [
                (f"{self.template_name}.wasm", f"{self.project_name}.wasm")
            ],
            ignore_missing=False
        )

        for file in test_paths:
            data = utils.read_json_file(file)
            # Patch fields
            data["name"] = data.get("name", "").replace(self.template_name, self.project_name)
            utils.write_json_file(str(file), data)

    def _replace_in_files(self, files: List[Path], replacements: List[Tuple[str, str]], ignore_missing: bool) -> None:
        for file in files:
            if ignore_missing and not file.exists():
                continue
            content = utils.read_file(file)
            assert isinstance(content, str)

            for to_replace, replacement in replacements:
                content = content.replace(to_replace, replacement)

            utils.write_file(file, content)


def remove_path(dependency: Any) -> None:
    try:
        del dependency["path"]
    except TypeError:
        pass


def remove_path_from_dependencies(cargo_file: CargoFile) -> None:
    for dependency in cargo_file.get_dependencies().values():
        remove_path(dependency)
    for dependency in cargo_file.get_dev_dependencies().values():
        remove_path(dependency)
