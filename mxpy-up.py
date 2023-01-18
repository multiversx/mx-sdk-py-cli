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
sdk_path = Path("~/multiversx-sdk").expanduser().resolve()


def main():
    parser = ArgumentParser()
    parser.add_argument("--modify-path", dest="modify_path", action="store_true", help="whether to modify $PATH (in profile file)")
    parser.add_argument("--no-modify-path", dest="modify_path", action="store_false", help="whether to modify $PATH (in profile file)")
    parser.add_argument("--exact-version", help="the exact version of mxpy to install")
    parser.add_argument("--from-branch", help="use a branch of multiversx/mx-sdk-py-cli")
    parser.set_defaults(modify_path=True)
    args = parser.parse_args()

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

    migrate_old_elrondsdk()

    # In case of a fresh install:
    sdk_path.mkdir(parents=True, exist_ok=True)

    create_venv()
    install_mxpy(exact_version, from_branch)
    if modify_path:
        add_sdk_to_path()
        logger.info("""
###############################################################################
Upon restarting the user session, [$ mxpy] command should be available in your shell.
###############################################################################
""")

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

    # Fix existing symlinks.
    old_mandos_link = sdk_path / "vmtools" / "mandos-test"
    old_testwallets_link = sdk_path / "testwallets" / "latest"
    old_nodejs_link = sdk_path / "nodejs" / "latest"

    new_mandos_link = sdk_path / "vmtools" / "run-scenarios"
    new_testwallets_link = sdk_path / "testwallets" / "latest"
    new_nodejs_link = sdk_path / "nodejs" / "latest"

    try:
        old_target = os.readlink(old_mandos_link)
        new_target = old_target.replace("elrondsdk", "multiversx-sdk")
        old_mandos_link.unlink()
        os.symlink(new_target, str(new_mandos_link))
        logger.info("Fixed old mandos symlink.")
    except FileNotFoundError:
        logger.info("Old mandos symlink does not exist.")

    try:
        old_target = os.readlink(old_testwallets_link)
        new_target = old_target.replace("elrondsdk", "multiversx-sdk")
        old_testwallets_link.unlink()
        os.symlink(new_target, str(new_testwallets_link))
        logger.info("Fixed old testwallets symlink.")
    except FileNotFoundError:
        logger.info("Old testwallets symlink does not exist.")

    try:
        old_target = os.readlink(old_nodejs_link)
        new_target = old_target.replace("elrondsdk", "multiversx-sdk")
        old_nodejs_link.unlink()
        os.symlink(new_target, str(new_nodejs_link))
        logger.info("Fixed old nodejs symlink.")
    except FileNotFoundError:
        logger.info("Old nodejs symlink does not exist.")


def create_venv():
    require_python_venv_tools()
    venv_folder = get_mxpy_venv_path()
    venv_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Creating virtual environment in: {venv_folder}.")
    import venv
    builder = venv.EnvBuilder(with_pip=True)
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
    return_code = run_in_venv(["mxpy", "--version"], venv_path)
    if return_code != 0:
        raise InstallError("Could not install mxpy.")

    logger.info("Creating symlink to mxpy...")

    link_path = sdk_path / "mxpy"

    try:
        link_path.unlink()
        logger.info(f"Removed symlink: {link_path}")
    except FileNotFoundError:
        logger.info(f"Symlink does not exist yet: {link_path}")
        pass

    os.symlink(str(get_mxpy_venv_path() / "bin" / "mxpy"), link_path)
    logger.info(f"Created symlink: {link_path}")
    logger.info("You have successfully installed mxpy.")


def run_in_venv(args: List[str], venv_path: Path):
    if "PYTHONHOME" in os.environ:
        del os.environ["PYTHONHOME"]

    process = subprocess.Popen(args, env={
        "PATH": str(venv_path / "bin") + ":" + os.environ["PATH"],
        "VIRTUAL_ENV": str(venv_path)
    })

    return process.wait()


def add_sdk_to_path():
    old_export_directive = f'export PATH="{Path("~/elrondsdk").expanduser()}:$PATH"\t# elrond-sdk'
    new_export_directive = f'export PATH="${{HOME}}/multiversx-sdk:$PATH"\t# multiversx-sdk'

    profile_file = get_profile_file()
    profile_info_content = profile_file.read_text()

    logger.info(f"Using shell profile: {profile_file}")

    if old_export_directive in profile_info_content:
        # We don't perform the removal automatically (a bit risky)
        logger.warning(f"Please manually remove the following entry from the shell profile ({profile_file}): {old_export_directive}.")

    if new_export_directive in profile_info_content:
        # Note: in some (rare) cases, here we'll have false positives (e.g. if the export directive is commented out).
        logger.info(f"multiversx-sdk path ({sdk_path}) is already configured in shell profile.")
        return

    logger.info(f"Configuring multiversx-sdk path [{sdk_path}] in shell profile...")
    logger.info(f"[{profile_file}] is being modified...")

    with open(profile_file, "a") as file:
        file.write(f'\n{new_export_directive}\n')

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

    return Path(file).expanduser().resolve()


def run_post_install_checks():
    multiversx_sdk_path = Path("~/multiversx-sdk").expanduser()
    elrond_sdk_path = Path("~/elrondsdk").expanduser()

    logger.info("Running post-install checks...")
    print("~/multiversx-sdk exists", "✓" if multiversx_sdk_path.exists() else "✗")
    print("~/elrondsdk is removed or missing", "✓" if not elrond_sdk_path.exists() else "✗")
    print("~/multiversx-sdk/mxpy link created", "✓" if (multiversx_sdk_path / "mxpy").exists() else "✗")
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
