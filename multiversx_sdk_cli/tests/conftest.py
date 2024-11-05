import pytest


# function executed right after test items collected but before test run
def pytest_collection_modifyitems(config, items):
    if not config.getoption('-m'):
        skip_me = pytest.mark.skip(reason="require_localnet will only run if explicitly set to with -m")
        for item in items:
            if "require_localnet" in item.keywords:
                item.add_marker(skip_me)
