from multiversx_sdk_cli.ledger.config import compare_versions
from multiversx_sdk_cli.ledger.ledger_app_handler import get_error


class TestLedger:
    def test_compare_versions(self):
        assert compare_versions("v1.0.0", "v1.0.1") == -1
        assert compare_versions("v1.0.1", "v1.0.1") == 0
        assert compare_versions("v1.0.1", "v1.0.0") == 1
        assert compare_versions("v1.0.0.1", "v1.0.0") == 1
        assert compare_versions("v1.0.1", "v1.0.1.0.0.4") == -1

    def test_get_error(self):
        assert get_error(0x6E0C) == "invalid fee"
        assert get_error(0x6E11) == "regular signing is deprecated"
        assert get_error(0x9000) == ""
        assert get_error(0x9999999999) == "unknown error code: 0x9999999999"
