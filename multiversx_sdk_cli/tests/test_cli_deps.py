import shutil
from pathlib import Path

import pytest

from multiversx_sdk_cli.cli import main


def test_deps_install_rust():
    return_code = main(["deps", "install", "rust", "--overwrite"])
    assert return_code == 0


def test_deps_check_rust():
    return_code = main(["deps", "check", "rust"])
    assert True if return_code == 0 else False

    which_rustc = shutil.which("rustc")
    assert which_rustc and Path.is_file(Path(which_rustc))

    which_cargo = shutil.which("cargo")
    assert which_cargo and Path.is_file(Path(which_cargo))

    which_sc_meta = shutil.which("sc-meta")
    assert which_sc_meta and Path.is_file(Path(which_sc_meta))

    which_wasm_opt = shutil.which("wasm-opt")
    assert which_wasm_opt and Path.is_file(Path(which_wasm_opt))

    which_twiggy = shutil.which("twiggy")
    assert which_twiggy and Path.is_file(Path(which_twiggy))


@pytest.mark.skip_on_windows
def test_deps_install_vmtools():
    return_code = main(["deps", "install", "vmtools"])
    assert return_code == 0


@pytest.mark.skip_on_windows
def test_deps_check_vmtools():
    return_code = main(["deps", "check", "vmtools"])
    assert return_code == 0
