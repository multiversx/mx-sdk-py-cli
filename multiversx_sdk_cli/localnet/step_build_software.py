import logging
import subprocess
from pathlib import Path
from typing import Dict, List

from multiversx_sdk_cli import dependencies, utils, workstation
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
        _copy_wasmer_libs(config, cmd_node)
        _set_rpath(cmd_node / "node")

    if "seednode" in software_components:
        logger.info("Building seednode...")

        cmd_seednode = config.software.mx_chain_go.get_cmd_seednode_folder()
        _do_build(cmd_seednode, golang_env)
        _copy_wasmer_libs(config, cmd_seednode)
        _set_rpath(cmd_seednode / "seednode")

    if "proxy" in software_components:
        logger.info("Building proxy...")

        cmd_proxy = config.software.mx_chain_proxy_go.get_cmd_proxy_folder()
        _do_build(cmd_proxy, golang_env)


def _do_build(cwd: Path, env: Dict[str, str]):
    return_code = subprocess.check_call(["go", "build"], cwd=cwd, env=env)
    if return_code != 0:
        raise KnownError(f"error code = {return_code}, see output")


def _copy_wasmer_libs(config: ConfigRoot, destination: Path):
    golang = dependencies.get_golang()
    vm_go_folder_name = _get_chain_vm_go_folder_name(config)
    vm_go_path = golang.get_gopath() / "pkg" / "mod" / vm_go_folder_name
    wasmer_path = vm_go_path / "wasmer"
    wasmer2_path = vm_go_path / "wasmer2"

    libraries.copy_libraries(wasmer_path, destination)
    libraries.copy_libraries(wasmer2_path, destination)


def _get_chain_vm_go_folder_name(config: ConfigRoot) -> str:
    go_mod = config.software.mx_chain_go.get_path_within_source(Path("go.mod"))
    lines = utils.read_lines(go_mod)
    line = [line for line in lines if "github.com/multiversx/mx-chain-vm-go" in line][0]
    parts = line.split()
    return f"{parts[0]}@{parts[1]}"


def _set_rpath(cmd_path: Path):
    """
    Set the rpath of the executable to the current directory, on a best-effort basis.

    For other occurrences of this approach, see:
     - https://github.com/multiversx/mx-chain-scenario-cli-go/blob/master/.github/workflows/on_release_attach_artifacts.yml
    """

    if not workstation.is_osx():
        # We're only patching the executable on macOS.
        # For Linux, we're leveraging LD_LIBRARY_PATH to resolve the libraries.
        return

    try:
        subprocess.check_call([
            "install_name_tool",
            "-add_rpath",
            "@loader_path",
            cmd_path
        ])
    except Exception as e:
        # In most cases, this isn't critical (libraries might be found among the downloaded Go packages).
        logger.warning(f"Failed to set rpath of {cmd_path}: {e}")
