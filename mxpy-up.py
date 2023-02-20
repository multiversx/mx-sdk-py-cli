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
    parser.add_argument("--exact-version", help="the exact version of mxpy to install")
    parser.add_argument("--from-branch", help="use a branch of multiversx/mx-sdk-py-cli")
    parser.add_argument("--not-interactive", action="store_true", default=False)
    parser.set_defaults(modify_path=True)
    args = parser.parse_args()

    exact_version = args.exact_version
    from_branch = args.from_branch
    interactive = not args.not_interactive

    logging.basicConfig(level=logging.DEBUG)

    if get_operating_system() == "windows":
        print("""
IMPORTANT NOTE
==============

Windows support is limited and experimental.
""")
        confirm_continuation(interactive)

    guard_non_root_user()
    guard_python_version()
    migrate_old_elrondsdk()
    migrate_v6(interactive)

    # In case of a fresh install:
    sdk_path.mkdir(parents=True, exist_ok=True)
    create_venv()
    install_mxpy(exact_version, from_branch)

    run_post_install_checks()

    if interactive:
        guide_system_path_alteration()


def guard_non_root_user():
    logger.info("Checking user (should not be root).")

    operating_system = get_operating_system()

    if operating_system == "windows":
        return
    if os.getuid() == 0:
        raise InstallError("You should not install mxpy as root.")


def guard_python_version():
    python_version = (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)

    logger.info("Checking Python version.")
    logger.info(f"Python version: {format_version(python_version)}")
    if python_version < MIN_REQUIRED_PYTHON_VERSION:
        raise InstallError(f"You need Python {format_version(MIN_REQUIRED_PYTHON_VERSION)} or later.")


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


def migrate_v6(interactive: bool):
    nodejs_folder = sdk_path / "nodejs"

    if nodejs_folder.exists():
        print(f"""
In previous versions of the SDK, the "wasm-opt" tool was installed in the "nodejs" folder.

This is no longer the case - now, "wasm-opt" is a separate module.

The following folder will be removed: {nodejs_folder}.

You may need to reinstall wasm-opt using `mxpy deps install wasm-opt`.
""")
        confirm_continuation(interactive)

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
    builder = venv.EnvBuilder(with_pip=True, symlinks=True)
    builder.clear_directory(venv_folder)
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

    shortcut_content = get_mxpy_shortcut_content()
    shortcut_path.write_text(shortcut_content)

    st = os.stat(shortcut_path)
    os.chmod(shortcut_path, st.st_mode | stat.S_IEXEC)

    logger.info("You have successfully installed mxpy.")


def get_mxpy_shortcut_content():
    operating_system = get_operating_system()
    venv_path = get_mxpy_venv_path()

    if operating_system == "windows":
        return f"""#!/bin/sh
. "{venv_path / 'Scripts' / 'activate'}"
python3 -m multiversx_sdk_cli.cli "$@"
deactivate
"""

    return f"""#!/bin/sh
. "{venv_path / 'bin' / 'activate'}"
python3 -m multiversx_sdk_cli.cli "$@"
deactivate
"""


def run_in_venv(args: List[str], venv_path: Path):
    env = os.environ.copy()

    if "PYTHONHOME" in env:
        del env["PYTHONHOME"]

    env["PATH"] = str(venv_path / "bin") + ":" + env["PATH"]
    env["VIRTUAL_ENV"] = str(venv_path)

    process = subprocess.Popen(args, env=env)
    return process.wait()


def run_post_install_checks():
    multiversx_sdk_path = Path("~/multiversx-sdk").expanduser()
    elrond_sdk_path = Path("~/elrondsdk").expanduser()

    logger.info("Running post-install checks...")
    print("~/multiversx-sdk exists", "OK" if multiversx_sdk_path.exists() else "NOK")
    print("~/elrondsdk is removed or missing", "OK" if not elrond_sdk_path.exists() else "NOK")
    print("~/multiversx-sdk/mxpy shortcut created", "OK" if (multiversx_sdk_path / "mxpy").exists() else "NOK")
    print("~/multiversx-sdk/erdpy.json is renamed or missing", "OK" if not (multiversx_sdk_path / "erdpy.json").exists() else "NOK")


def guide_system_path_alteration():
    interactive = True
    operating_system = get_operating_system()

    if operating_system == "windows":
        print(f"""
###############################################################################
On Windows, for the "mxpy" command shortcut to be available, you need to add the directory "{sdk_path}" to the system PATH.

You can do this by following these steps:

https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10

###############################################################################
Do you understand the above?
###############################################################################
""")
        confirm_continuation(interactive)
        return

    old_export_directive = f'export PATH="{Path("~/elrondsdk").expanduser()}:$PATH"\t# elrond-sdk'
    new_export_directive = f'export PATH="${{HOME}}/multiversx-sdk:$PATH"\t# multiversx-sdk'

    profile_files = get_profile_files()

    if not profile_files:
        print(f"""
###############################################################################
No shell profile files have been found.

The "mxpy" command shortcut will not be available until you add the directory "{sdk_path}" to the system PATH.
###############################################################################
Do you understand the above?
""")
        confirm_continuation(interactive)
        return

    profile_files_formatted = "\n".join(f" - {file}" for file in profile_files)
    profile_files_contents = [profile_file.read_text() for profile_file in profile_files]
    any_old_export_directive = any(old_export_directive in content for content in profile_files_contents)
    any_new_export_directive = any(new_export_directive in content for content in profile_files_contents)

    if any_old_export_directive:
        # We don't perform the removal automatically (a bit risky)
        print(f"""
###############################################################################
It seems that the old path "~/elrondsdk" is still configured in shell profile.

Please MANUALLY remove it from the shell profile (now or after the installer script ends).

Your shell profile files:
{profile_files_formatted}

The entry (entries) to remove: 
    {old_export_directive}
###############################################################################
Make sure you understand the above before proceeding further.
###############################################################################
""")
        confirm_continuation(interactive)

    if any_new_export_directive:
        # Note: in some (rare) cases, here we'll have false positives (e.g. if the export directive is commented out).
        print(f"""
###############################################################################
It seems that the path "~/multiversx-sdk" is already configured in shell profile.

To confirm this, check the shell profile (now or after the installer script ends). 

Your shell profile files:
{profile_files_formatted}

The entry to check (it should be present): 
    {new_export_directive}.
###############################################################################
Make sure you understand the above before proceeding further.
###############################################################################
""")
        confirm_continuation(interactive)
        return

    print(f"""
###############################################################################
In order to use the "mxpy" command shortcut, you have to manually extend the PATH variable to include "~/multiversx-sdk".

In order to manually extend the PATH variable, add the following line to your shell profile file upon installation:

    export PATH="${{HOME}}/multiversx-sdk:${{PATH}}"

Your shell profile files:
{profile_files_formatted}

Upon editing the shell profile file, you may have to RESTART THE USER SESSION for the changes to take effect.
""")
    confirm_continuation(interactive)


def get_profile_files() -> List[Path]:
    files = [
        Path("~/.profile").expanduser().resolve(),
        Path("~/.bashrc").expanduser().resolve(),
        Path("~/.bash_profile").expanduser().resolve(),
        Path("~/.zshrc").expanduser().resolve()
    ]

    return [file for file in files if file.exists()]


class InstallError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


def confirm_continuation(interactive: bool):
    if not interactive:
        return

    answer = input("Continue? (y/n)")
    if answer.lower() not in ["y", "yes"]:
        print("Confirmation not given. Will stop.")
        exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        logger.fatal(err)
        sys.exit(1)

    print("""
###############################################################################
Installer script finished successfully.
###############################################################################
For more information go to https://docs.multiversx.com.
For support, please contact us at http://discord.gg/MultiversXBuilders.
###############################################################################
""")
