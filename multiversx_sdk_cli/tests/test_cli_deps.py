import shutil

from multiversx_sdk_cli.cli import main
from multiversx_sdk_cli.config import get_dependency_tag


def test_deps_install_rust():
    default_tag = get_dependency_tag("rust")
    return_code = main(["deps", "install", "rust", "--tag", default_tag])
    if return_code:
        assert False
    else:
        assert True


def test_deps_install_vmtools():
    return_code = main(["deps", "install", "vmtools"])
    if return_code:
        assert False
    else:
        assert True


def test_deps_check_rust():
    return_code = main(["deps", "check", "rust"])
    if return_code:
        assert False
    else:
        assert True


def test_check_sc_meta():
    which_sc_meta = shutil.which("sc-meta")
    if which_sc_meta:
        assert True
    elif which_sc_meta is None:
        assert False


def test_deps_check_vmtools():
    return_code = main(["deps", "check", "vmtools"])
    if return_code:
        assert False
    else:
        assert True
