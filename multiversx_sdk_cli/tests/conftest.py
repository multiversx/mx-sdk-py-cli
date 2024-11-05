import pytest


# function executed right after test items collected but before test run
def pytest_collection_modifyitems(config, items):
    if not config.getoption('-m'):
        skip_me = pytest.mark.skip(reason="to run marked tests, you need to explicitly run them with -m")
        for item in items:
            if "require_localnet" in item.keywords:
                item.add_marker(skip_me)
            if "run_on_windows" in item.keywords:
                item.add_marker(skip_me)
