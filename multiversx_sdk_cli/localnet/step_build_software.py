import logging
import subprocess
from pathlib import Path
from typing import Dict, List

from multiversx_sdk_cli import dependencies, utils
from multiversx_sdk_cli.errors import KnownError
from multiversx_sdk_cli.localnet import libraries
from multiversx_sdk_cli.localnet.config_root import ConfigRoot

logger = logging.getLogger("localnet")


def build(configfile: Path, software_components: List[str]):
    config = ConfigRoot.from_file(configfile)

    golang = dependencies.get_golang()
    golang_env = golang.get_env()

    if "node" in software_components:
        logger.info("Building node...")

        cmd_node = config.software.mx_chain_go.get_cmd_node_folder()
        _do_build(cmd_node, golang_env)

        wasmer_path = golang.get_gopath() / "pkg" / "mod" / _get_wasm_vm_package(config) / "wasmer"
        libraries.copy_libraries(wasmer_path, cmd_node)

    if "seednode" in software_components:
        logger.info("Building seednode...")

        cmd_seednode = config.software.mx_chain_go.get_cmd_seednode_folder()
        _do_build(cmd_seednode, golang_env)

        wasmer_path = golang.get_gopath() / "pkg" / "mod" / _get_wasm_vm_package(config) / "wasmer"
        libraries.copy_libraries(wasmer_path, cmd_seednode)

    if "proxy" in software_components:
        logger.info("Building proxy...")

        cmd_proxy = config.software.mx_chain_proxy_go.get_cmd_proxy_folder()
        _do_build(cmd_proxy, golang_env)


def _do_build(cwd: Path, env: Dict[str, str]):
    return_code = subprocess.check_call(["go", "build"], cwd=cwd, env=env)
    if return_code != 0:
        raise KnownError(f"error code = {return_code}, see output")


def _get_wasm_vm_package(config: ConfigRoot) -> str:
    go_mod = config.software.mx_chain_go.get_path_within_source(Path("go.mod"))
    lines = utils.read_lines(go_mod)
    line = [line for line in lines if "github.com/multiversx/mx-chain-vm-v" in line][-1]
    parts = line.split()
    return f"{parts[0]}@{parts[1]}"
