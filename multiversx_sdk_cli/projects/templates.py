import json
import logging
import shutil
from pathlib import Path
from typing import Any, List, Tuple

from multiversx_sdk_cli import errors, utils
from multiversx_sdk_cli.projects import shared
from multiversx_sdk_cli.projects.project_rust import CargoFile
from multiversx_sdk_cli.projects.templates_config import \
    get_templates_repositories
from multiversx_sdk_cli.projects.templates_repository import \
    TemplatesRepository

logger = logging.getLogger("projects.templates")


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
            return

    raise errors.TemplateMissingError(template)


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
        template_name = self._with_underscores(self.template_name)

        tests = (self.directory / "tests").glob("*.rs")

        source_code_files = [
            self.directory / "src" / f"{template_name}.rs",
            self.directory / "src" / "lib.rs",
            self.directory / "abi" / "src" / "main.rs",
            self.directory / "wasm" / "src" / "lib.rs",
            self.directory / "meta" / "src" / "main.rs",
        ]

        source_code_files.extend(tests)

        logger.info("Patching source code...")
        self._patch_source_code_files(source_code_files, ignore_missing=True)
        self._patch_source_code_tests()

        logger.info("Patching test files...")
        self._patch_scenarios_tests()

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

    def _contract_name(self, name: str) -> str:
        chars = name.replace("-", " ").replace("_", " ").split()
        return ''.join(i.capitalize() for i in chars[0:])

    def _patch_source_code_files(self, source_paths: List[Path], ignore_missing: bool) -> None:
        template_name = self._with_underscores(self.template_name)
        project_name = self._with_underscores(self.project_name)
        template_contract_name = self._contract_name(self.template_name)
        project_contract_name = self._contract_name(self.project_name)

        self._replace_in_files(
            source_paths,
            [
                # Example: replace contract name "pub trait SimpleERC20" to "pub trait MyContract"
                (f"pub trait {template_contract_name}", f"pub trait {project_contract_name}"),
                # Example: replace "simple_erc20.wasm" to "my_token.wasm"
                (f"{self.template_name}.wasm", f"{self.project_name}.wasm"),
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

    def _patch_scenarios_tests(self):
        test_dir_path = self.directory / "scenarios"
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
