import os
import subprocess
from pathlib import Path
from typing import Union, List
from erdpy.errors import DockerError


def is_docker_installed():
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        output = result.stdout
    
        if "Docker version" in output:
            return True
        else:
            raise DockerError()
    except:
        print("Something went wrong when checking if docker is installed!")


def run_docker(image: str, project_path: Union[Path, None], contract_path: str, output_path: Path,
                cargo_target_dir: Union[Path, None], no_wasm_opt: bool):
    docker_mount_args: List[str] = ["--volume", f"{output_path}:/output"]

    if project_path:
        docker_mount_args.extend(["--volume", f"{project_path}:/project"])

    if cargo_target_dir:
        docker_mount_args += ["--volume", f"{cargo_target_dir}:/cargo-target-dir"]

    docker_args = ["docker", "run"]

    docker_args += ["--interactive"]
    docker_args += ["--tty"]
    docker_args += docker_mount_args
    docker_args += ["--user", f"{str(os.getuid())}:{str(os.getgid())}"]
    docker_args += ["--rm", image]

    entrypoint_args: List[str] = []

    if project_path:
        entrypoint_args.extend(["--project", "project"])

    if no_wasm_opt:
        entrypoint_args.append("--no-wasm-opt")

    if contract_path:
        entrypoint_args.extend(["--contract", contract_path])

    args = docker_args + entrypoint_args

    result = subprocess.run(args)

    return result.returncode
