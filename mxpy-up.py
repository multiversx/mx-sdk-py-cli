import logging
import os
import os.path
import shutil
import stat
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger("installer")

MIN_REQUIRED_PYTHON_VERSION = (3, 8, 0)
sdk_path = Path("~/multiversx-sdk").expanduser().resolve()


def main():
    parser = ArgumentParser()
    parser.add_argument("--modify-path", dest="modify_path", action="store_true", help="(deprecated, not used)")
    parser.add_argument("--no-modify-path", dest="modify_path", action="store_false", help="(deprecated, not used)")
    parser.add_argument("--exact-version", help="the exact version of mxpy to install")
    parser.add_argument("--from-branch", help="use a branch of multiversx/mx-sdk-py-cli")
    parser.add_argument("--yes", action="store_true", default=False)
    parser.set_defaults(modify_path=True)
    args = parser.parse_args()

    exact_version = args.exact_version
    from_branch = args.from_branch
    yes = args.yes

    logging.basicConfig(level=logging.DEBUG)

    operating_system = get_operating_system()
    logger.info(f"Operating system: {operating_system}")

    python_version = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

    logger.info("Checking user.")
    if hasattr(os, "getuid") and os.getuid() == 0:
        raise InstallError("You should not install mxpy as root.")

    logger.info("Checking Python version.")
    logger.info(f"Python version: {format_version(python_version)}")
    if python_version < MIN_REQUIRED_PYTHON_VERSION:
        raise InstallError(f"You need Python {format_version(MIN_REQUIRED_PYTHON_VERSION)} or later.")

    migrate_old_elrondsdk()
    migrate_v6(yes)

    # In case of a fresh install:
    sdk_path.mkdir(parents=True, exist_ok=True)

    create_venv()
    install_mxpy(exact_version, from_branch)

    run_post_install_checks()


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


def migrate_old_elrondsdk() -> None:
    old_sdk_path = Path("~/elrondsdk").expanduser().resolve()
    if old_sdk_path.exists():
        old_sdk_path.rename(sdk_path)
        logger.info(f"Renamed {old_sdk_path} to {sdk_path}.")
    else:
        logger.info(f"Old SDK path does not exist: {old_sdk_path}.")

    # Remove erdpy-venv (since mxpy-venv is used instead).
    old_venv = sdk_path / "erdpy-venv"
    try:
        shutil.rmtree(old_venv)
        logger.info("Removed old virtual environment.")
    except FileNotFoundError:
        logger.info("Old virtual environment does not exist.")

    # Remove "erdpy-activate", since it is not recommended anymore when writing Python scripts.
    # The multiversx-sdk-* libraries should be used instead for writing Python scripts and modules that interact with the Network
    # (according to the official cookbook).
    old_erdpy_activate = sdk_path / "erdpy-activate"
    try:
        old_erdpy_activate.unlink()
        logger.info("Removed old erdpy-activate.")
    except FileNotFoundError:
        logger.info("Old erdpy-activate does not exist.")

    # Remove old erdpy symlink.
    old_erdpy = sdk_path / "erdpy"
    try:
        old_erdpy.unlink()
        logger.info("Removed old erdpy symlink.")
    except FileNotFoundError:
        logger.info("Old erdpy symlink does not exist.")

    # Rename the global config file.
    # We won't handle local config files, they have to be migrated manually.
    old_config_path = sdk_path / "erdpy.json"
    new_config_path = sdk_path / "mxpy.json"
    if old_config_path.exists():
        old_config_path.rename(new_config_path)
        logger.info(f"Renamed {old_config_path} to {new_config_path}.")
    else:
        logger.info(f"Old config path does not exist: {old_config_path}.")

    # Remove vmtools, if exists. Has to be re-downloaded, and re-compiled (libwasmer-related issues will arise otherwise).
    old_vmtools = sdk_path / "vmtools"
    try:
        shutil.rmtree(old_vmtools)
        logger.warning("Removed old vmtools.")
        logger.warning("You have to re-download vmtools using [mxpy deps install vmtools].")
    except FileNotFoundError:
        logger.info("Old vmtools does not exist.")

    # Fix existing symlinks.
    old_testwallets_link = sdk_path / "testwallets" / "latest"
    new_testwallets_link = sdk_path / "testwallets" / "latest"

    try:
        old_target = os.readlink(old_testwallets_link)
        new_target = old_target.replace("elrondsdk", "multiversx-sdk")
        old_testwallets_link.unlink()
        os.symlink(new_target, str(new_testwallets_link))
        logger.info("Fixed old testwallets symlink.")
    except FileNotFoundError:
        logger.info("Old testwallets symlink does not exist.")


def migrate_v6(yes: bool):
    nodejs_folder = sdk_path / "nodejs"

    if nodejs_folder.exists():
        print(f"""
In previous versions of the SDK, the "wasm-opt" tool was installed in the "nodejs" folder.

This is no longer the case - now, "wasm-opt" is a separate module.

The following folder will be removed: {nodejs_folder}.

You may need to reinstall wasm-opt using `mxpy deps install wasm-opt`.
""")
        confirm_continuation(yes)

        shutil.rmtree(nodejs_folder)

    global_testnet_toml = sdk_path / "testnet.toml"
    if global_testnet_toml.exists():
        global_testnet_toml.unlink()


def create_venv():
    require_python_venv_tools()
    venv_folder = get_mxpy_venv_path()
    venv_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Creating virtual environment in: {venv_folder}.")
    import venv
    builder = venv.EnvBuilder(with_pip=True)

    logger.info("builder.clear_directory()")
    builder.clear_directory(venv_folder)

    logger.info("builder.create()")
    builder.create(venv_folder)

    logger.info(f"Virtual environment has been created in: {venv_folder}.")


def require_python_venv_tools():
    operating_system = get_operating_system()

    try:
        import ensurepip
        import venv
        logger.info(f"Packages found: {ensurepip}, {venv}.")
    except ModuleNotFoundError:
        if operating_system == "linux":
            python_venv = f"python{sys.version_info.major}.{sys.version_info.minor}-venv"
            raise InstallError(f'Packages [venv] or [ensurepip] not found. Please run "sudo apt install {python_venv}" and then run mxpy-up again.')
        else:
            raise InstallError("Packages [venv] or [ensurepip] not found, please install them first. See https://docs.python.org/3/tutorial/venv.html.")


def get_mxpy_venv_path():
    return sdk_path / "mxpy-venv"


def install_mxpy(exact_version: str, from_branch: str):
    logger.info("Installing mxpy in virtual environment...")

    if from_branch:
        package_to_install = f"https://github.com/multiversx/mx-sdk-py-cli/archive/refs/heads/{from_branch}.zip"
    else:
        package_to_install = "multiversx_sdk_cli" if not exact_version else f"multiversx_sdk_cli=={exact_version}"

    venv_path = get_mxpy_venv_path()

    return_code = run_in_venv(["python3", "-m", "pip", "install", "--upgrade", "pip"], venv_path)
    if return_code != 0:
        raise InstallError("Could not upgrade pip.")
    return_code = run_in_venv(["pip3", "install", "--no-cache-dir", package_to_install], venv_path)
    if return_code != 0:
        raise InstallError("Could not install mxpy.")

    logger.info("Creating mxpy shortcut...")

    shortcut_path = sdk_path / "mxpy"

    try:
        shortcut_path.unlink()
        logger.info(f"Removed existing shortcut: {shortcut_path}")
    except FileNotFoundError:
        logger.info(f"Shortcut does not exist yet: {shortcut_path}")
        pass

    shortcut_path.write_text(f"""#!/bin/sh
. "{venv_path}/bin/activate"
python3 -m multiversx_sdk_cli.cli "$@"
deactivate
""")

    st = os.stat(shortcut_path)
    os.chmod(shortcut_path, st.st_mode | stat.S_IEXEC)

    logger.info("You have successfully installed mxpy.")


def run_in_venv(args: List[str], venv_path: Path):
    if "PYTHONHOME" in os.environ:
        del os.environ["PYTHONHOME"]

    process = subprocess.Popen(args, env={
        "PATH": str(venv_path / "bin") + ":" + os.environ["PATH"],
        "VIRTUAL_ENV": str(venv_path)
    })

    return process.wait()


def run_post_install_checks():
    multiversx_sdk_path = Path("~/multiversx-sdk").expanduser()
    elrond_sdk_path = Path("~/elrondsdk").expanduser()

    logger.info("Running post-install checks...")
    print("~/multiversx-sdk exists", "✓" if multiversx_sdk_path.exists() else "✗")
    print("~/elrondsdk is removed or missing", "✓" if not elrond_sdk_path.exists() else "✗")
    print("~/multiversx-sdk/mxpy shortcut created", "✓" if (multiversx_sdk_path / "mxpy").exists() else "✗")
    print("~/multiversx-sdk/erdpy.json is renamed or missing", "✓" if not (multiversx_sdk_path / "erdpy.json").exists() else "✗")


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
For support, please contact us at http://discord.gg/MultiversXBuilders (recommended) or https://t.me/MultiversXDevelopers.
""")


def confirm_continuation(yes: bool = False):
    if (yes):
        return

    answer = input("Continue? (y/n)")
    if answer.lower() not in ["y", "yes"]:
        print("Confirmation not given. Will stop.")
        exit(1)
