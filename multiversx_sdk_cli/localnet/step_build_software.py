import logging
import os
import shutil
from pathlib import Path
from typing import Any, List

from multiversx_sdk_cli import dependencies, myprocess, utils
from multiversx_sdk_cli.errors import KnownError
from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.config_software import SoftwareResolution

logger = logging.getLogger("localnet")


def build(args: Any):
    config = ConfigRoot.from_file(args.configfile)
    resolution = config.software.resolution

    if resolution == SoftwareResolution.LocalPrebuiltCmdFolders:
        logger.info("Using local prebuilt CMD folders, nothing to build")
        return

    if resolution == SoftwareResolution.LocalSourceFolders or resolution == SoftwareResolution.RemoteArchives:
        golang = dependencies.get_golang()
        golang_env = golang.get_env()

        logger.info("Building seednode...")
        [node_parent, seednode_parent, proxy_parent] = config.software.get_binaries_parents()

        logger.info("Building node...")
        myprocess.run_process(['go', 'build'], cwd=node_parent, env=golang_env)

        logger.info("Building node...")
        myprocess.run_process(['go', 'build'], cwd=seednode_parent, env=golang_env)

        logger.info("Building proxy...")
        myprocess.run_process(['go', 'build'], cwd=proxy_parent, env=golang_env)

        wasm_vm_package = _get_wasm_vm_package(config)
        wasmer_path = golang.get_gopath() / "pkg" / "mod" / wasm_vm_package / "wasmer"

        copy_libraries(wasmer_path, node_parent)
        copy_libraries(wasmer_path, seednode_parent)

        return

    raise KnownError(f"Unknown software resolution: {resolution}")


def _get_wasm_vm_package(config: ConfigRoot) -> str:
    go_mod = config.software.get_mx_chain_go_path_in_source(Path("go.mod"))
    lines = utils.read_lines(go_mod)
    line = [line for line in lines if "github.com/multiversx/mx-chain-vm-v" in line][-1]
    parts = line.split()
    return f"{parts[0]}@{parts[1]}"


# TODO de-duplicate code
def copy_libraries(source: Path, destination: Path):
    libraries: List[Path] = list(source.glob("*.dylib")) + list(source.glob("*.so"))

    for library in libraries:
        logger.info(f"Copying {library} to {destination}")

        shutil.copy(library, destination)
        os.chmod(destination / library.name, 0o755)
