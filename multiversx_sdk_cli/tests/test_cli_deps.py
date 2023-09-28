import shutil
from pathlib import Path

import pytest

from multiversx_sdk_cli.cli import main


def test_deps_install_rust():
    return_code = main(["deps", "install", "rust", "--overwrite"])
    assert True if return_code == 0 else False


def test_deps_check_rust():
    return_code = main(["deps", "check", "rust"])
    assert True if return_code == 0 else False

    which_rustc = shutil.which("rustc")
    if which_rustc:
        assert Path.is_file(Path(which_rustc))

    which_cargo = shutil.which("cargo")
    if which_cargo:
        assert Path.is_file(Path(which_cargo))

    which_sc_meta = shutil.which("sc-meta")
    if which_sc_meta:
        assert Path.is_file(Path(which_sc_meta))

    which_wasm_opt = shutil.which("wasm-opt")
    if which_wasm_opt:
        assert Path.is_file(Path(which_wasm_opt))

    which_twiggy = shutil.which("twiggy")
    if which_twiggy:
        assert Path.is_file(Path(which_twiggy))


@pytest.mark.skip_on_windows
def test_deps_install_vmtools():
    return_code = main(["deps", "install", "vmtools"])
    assert True if return_code == 0 else False


@pytest.mark.skip_on_windows
def test_deps_check_vmtools():
    return_code = main(["deps", "check", "vmtools"])
    assert True if return_code == 0 else False
