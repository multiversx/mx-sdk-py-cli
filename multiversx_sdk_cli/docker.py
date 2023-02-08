import logging
import os
import subprocess
from pathlib import Path
from typing import List

from multiversx_sdk_cli.errors import KnownError

logger = logging.getLogger("docker")


def is_docker_installed():
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        output = result.stdout

        if "Docker version" in output:
            return True
        else:
            return False
    except:
        logger.error("Something went wrong when checking if docker is installed!")


def run_docker(
        image: str,
        project_path: Path,
        contract: str,
        output_path: Path,
        no_wasm_opt: bool,
        docker_interactive: bool,
        docker_tty: bool,
        no_default_platform: bool
):
    docker_mount_args: List[str] = ["--volume", f"{output_path}:/output"]

    if project_path:
        docker_mount_args.extend(["--volume", f"{project_path}:/project"])

    docker_args = ["docker", "run"]

    if not (no_default_platform):
        docker_args += ["--platform", "linux/amd64"]

    if docker_interactive:
        docker_args += ["--interactive"]
    if docker_tty:
        docker_args += ["--tty"]

    docker_args += docker_mount_args
    docker_args += ["--user", f"{str(os.getuid())}:{str(os.getgid())}"]
    docker_args += ["--rm", image]

    entrypoint_args: List[str] = []

    if project_path:
        entrypoint_args.extend(["--project", "project"])

    if no_wasm_opt:
        entrypoint_args.append("--no-wasm-opt")

    if contract:
        entrypoint_args.extend(["--contract", contract])

    args = docker_args + entrypoint_args

    logger.info(f"Docker running with args: {args}")

    try:
        result = subprocess.run(args)
        result.check_returncode()
    except subprocess.CalledProcessError as error:
        raise KnownError(f"Docker run failed with error code: {error.returncode}")
