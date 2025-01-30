import pytest

from multiversx_sdk_cli.cli import main


def test_deps_install_testwallets():
    return_code = main(["deps", "install", "testwallets"])
    assert return_code == 0


def test_deps_check_testwallets():
    return_code = main(["deps", "check", "testwallets"])
    assert return_code == 0


@pytest.mark.skip_on_windows
def test_deps_install_all():
    return_code = main(["deps", "install", "all"])
    assert return_code == 0


@pytest.mark.skip_on_windows
def test_deps_check_all():
    return_code = main(["deps", "check", "all"])
    assert return_code == 0
