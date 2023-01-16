import logging
import os
import os.path
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger("installer")

MIN_REQUIRED_PYTHON_VERSION = (3, 8, 0)


def main():
    parser = ArgumentParser()
    parser.add_argument("--modify-path", dest="modify_path", action="store_true", help="whether to modify $PATH (in profile file)")
    parser.add_argument("--no-modify-path", dest="modify_path", action="store_false", help="whether to modify $PATH (in profile file)")
    parser.add_argument("--sdk-path", default="~/multiversx-sdk", help="where to install multiversx-sdk")
    parser.add_argument("--exact-version", help="the exact version of mxpy to install")
    parser.add_argument("--from-branch", help="use a branch of multiversx/mx-sdk-py-cli")
    parser.set_defaults(modify_path=True)
    args = parser.parse_args()

    sdk_path = Path(args.sdk_path).expanduser().resolve()
    modify_path = args.modify_path
    exact_version = args.exact_version
    from_branch = args.from_branch

    logging.basicConfig(level=logging.DEBUG)

    operating_system = get_operating_system()
    python_version = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

    logger.info("Checking user.")
    if os.getuid() == 0:
        raise InstallError("You should not install mxpy as root.")

    logger.info("Checking Python version.")
    logger.info(f"Python version: {format_version(python_version)}")
    if python_version < MIN_REQUIRED_PYTHON_VERSION:
        raise InstallError(f"You need Python {format_version(MIN_REQUIRED_PYTHON_VERSION)} or later.")

    logger.info("Checking operating system.")
    logger.info(f"Operating system: {operating_system}")
    if operating_system != "linux" and operating_system != "osx":
        raise InstallError("Your operating system is not supported yet.")

    migrate_old_elrondsdk(sdk_path)
    create_venv(sdk_path)
    install_mxpy(sdk_path, exact_version, from_branch)
    if modify_path:
        add_sdk_to_path(sdk_path)
        logger.info("""
###############################################################################
Upon restarting the user session, [$ mxpy] command should be available in your shell.
###############################################################################
""")

    run_post_install_checks(sdk_path)


def format_version(version: Tuple[int, int, int]) -> str:
    major, minor, patch = version
    return f"{major}.{minor}.{patch}"


def get_operating_system():
    aliases = {
        "linux": "linux",
        "linux1": "linux",
        "linux2": "linux",
        "darwin": "osx",
        "win32": "windows",
        "cygwin": "windows",
        "msys": "windows"
    }

    operating_system = aliases.get(sys.platform)
    if operating_system is None:
        raise InstallError(f"Unknown platform: {sys.platform}")

    return operating_system


def migrate_old_elrondsdk(sdk_path: Path) -> None:
    old_folder = os.path.expanduser("~/elrondsdk")
    if os.path.isdir(old_folder):
        answer = input(f"Older installation folder {old_folder} has to be renamed. Allow? (y/n)")
        if answer.lower() not in ["y", "yes"]:
            raise InstallError("Installation will not continue.")
        shutil.move(old_folder, sdk_path)
        logger.info("Renamed folder.")

    # Remove erdpy-venv (since mxpy-venv is used instead).
    old_venv = sdk_path / "erdpy-venv"
    if old_venv.exists():
        shutil.rmtree(old_venv)
        logger.info("Removed old virtual environment.")

    # Remove "erdpy-activate", since it is not recommended anymore when writing Python scripts.
    # The multiversx-sdk-* libraries should be used instead for writing Python scripts and modules that interact with the Network
    # (according to the official cookbook).
    old_erdpy_activate = sdk_path / "erdpy-activate"
    if old_erdpy_activate.exists():
        old_erdpy_activate.unlink()


def create_venv(sdk_path: Path):
    require_venv()
    venv_folder = get_mxpy_venv_path(sdk_path)
    venv_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Creating virtual environment in: {venv_folder}.")
    import venv
    builder = venv.EnvBuilder(with_pip=True)
    builder.clear_directory(venv_folder)
    builder.create(venv_folder)

    logger.info(f"Virtual environment has been created in: {venv_folder}.")


def require_venv():
    operating_system = get_operating_system()

    try:
        import ensurepip
        import venv
        logger.info(f"Packages found: {ensurepip}, {venv}.")
    except ModuleNotFoundError:
        if operating_system == "linux":
            python_venv = f"python{sys.version_info.major}.{sys.version_info.minor}-venv"
            raise InstallError(f'Packages [venv] or [ensurepip] not found. Please run "sudo apt install {python_venv}" and then run erdpy-up again.')
        else:
            raise InstallError("Packages [venv] or [ensurepip] not found, please install them first. See https://docs.python.org/3/tutorial/venv.html.")


def get_mxpy_venv_path(sdk_path: Path):
    return sdk_path / "mxpy-venv"


def install_mxpy(sdk_path: Path, exact_version: str, from_branch: str):
    logger.info("Installing mxpy in virtual environment...")
    if from_branch:
        package_to_install = f"https://github.com/multiversx/mx-sdk-py-cli/archive/refs/heads/{from_branch}.zip"
    else:
        package_to_install = "multiversx_sdk_cli" if not exact_version else f"multiversx_sdk_cli=={exact_version}"

    venv_path = get_mxpy_venv_path(sdk_path)

    return_code = run_in_venv(["python3", "-m", "pip", "install", "--upgrade", "pip"], venv_path)
    if return_code != 0:
        raise InstallError("Could not upgrade pip.")
    return_code = run_in_venv(["pip3", "install", "--no-cache-dir", package_to_install], venv_path)
    if return_code != 0:
        raise InstallError("Could not install mxpy.")
    return_code = run_in_venv(["mxpy", "--version"], venv_path)
    if return_code != 0:
        raise InstallError("Could not install mxpy.")

    logger.info("Checking and upgrading configuration file")

    # Create symlink to "bin/mxpy"
    link_path = os.path.join(sdk_path, "mxpy")
    if os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(str(get_mxpy_venv_path(sdk_path) / "bin" / "mxpy"), link_path)
    logger.info("You have successfully installed mxpy.")


def run_in_venv(args: List[str], venv_path: Path):
    if "PYTHONHOME" in os.environ:
        del os.environ["PYTHONHOME"]

    process = subprocess.Popen(args, env={
        "PATH": str(venv_path / "bin") + ":" + os.environ["PATH"],
        "VIRTUAL_ENV": str(venv_path)
    })

    return process.wait()


def add_sdk_to_path(sdk_path: Path):
    logger.info("Checking PATH variable.")
    PATH = os.environ["PATH"]
    if str(sdk_path) in PATH:
        logger.info(f"multiversx-sdk path ({sdk_path}) already in $PATH variable.")
        return

    profile_file = get_profile_file()
    logger.info(f"Adding multiversx-sdk path [{sdk_path}] to $PATH variable.")
    logger.info(f"[{profile_file}] will be modified.")

    with open(profile_file, "a") as file:
        file.write(f'\nexport PATH="{sdk_path}:$PATH"\t# elrond-sdk\n')

    logger.info(f"""
###############################################################################
[{profile_file}] has been modified.
Please RESTART THE USER SESSION.
###############################################################################
""")


def get_profile_file():
    operating_system = get_operating_system()
    file = None

    if operating_system == "linux":
        file = "~/.profile"
    else:
        value = input("""Please choose your preferred shell:
1) zsh
2) bash
""")
        if value not in ["1", "2"]:
            raise InstallError("Invalid choice.")

        value = int(value)
        if value == 1:
            file = "~/.zshrc"
        else:
            file = "~/.bash_profile"

    return os.path.expanduser(file)


def run_post_install_checks(sdk_path: Path):
    pass


class InstallError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logger.fatal(err)
        sys.exit(1)

    logger.info("""

For more information go to https://docs.multiversx.com.
For support, please contact us at https://t.me/ElrondDevelopers.
""")
