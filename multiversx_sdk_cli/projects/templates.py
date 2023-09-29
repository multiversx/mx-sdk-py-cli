import logging
from pathlib import Path
from typing import Union

from multiversx_sdk_cli import myprocess
from multiversx_sdk_cli.dependencies.install import install_module

logger = logging.getLogger("projects.templates")


class Contract:
    def __init__(self,
                 tag: Union[str, None] = None,
                 name: Union[str, None] = None,
                 template: str = "",
                 path: Path = Path()
                 ) -> None:
        self.tag = tag
        self.name = name
        self.template = template
        self.path = path

    def get_contract_templates(self) -> str:
        self._check_if_dependencies_installed()
        args = self._prepare_args_to_list_templates()
        templates = myprocess.run_process(args=args, dump_to_stdout=False)
        return templates

    def create_from_template(self) -> None:
        self._check_if_dependencies_installed()
        args = self._prepare_args_to_create_new_contract_from_template()
        myprocess.run_process(args)

    def _check_if_dependencies_installed(self):
        logger.info("Checking if the necessarry dependencies are installed.")
        install_module("rust")

    def _prepare_args_to_list_templates(self) -> list[str]:
        args = ["sc-meta", "templates"]

        if self.tag:
            args.extend(["--tag", self.tag])

        return args

    def _prepare_args_to_create_new_contract_from_template(self) -> list[str]:
        args = ["sc-meta", "new", "--template", self.template, "--path", str(self.path)]

        if self.name:
            args.extend(["--name", self.name])

        if self.tag:
            args.extend(["--tag", self.tag])

        return args
