from typing import Any, List

import pytest

from multiversx_sdk_cli.native_auth_client import (
    NativeAuthClient,
    NativeAuthClientConfig,
)


def mock(mocker: Any, code: int, response: Any):
    mock_response = mocker.Mock()
    mock_response.status_code = code
    mock_response.json.return_value = response
    mocker.patch("requests.get", return_value=mock_response)


def mock_side_effect(mocker: Any, responses: List[Any]):
    def side_effect(*args: Any, **kwargs: Any):
        response = responses.pop(0)
        mock_response = mocker.Mock()
        mock_response.status_code = response["code"]
        mock_response.json.return_value = response["response"]
        return mock_response

    mocker.patch("requests.get", side_effect=side_effect)


class TestNativeAuth:
    ADDRESS = "erd1qnk2vmuqywfqtdnkmauvpm8ls0xh00k8xeupuaf6cm6cd4rx89qqz0ppgl"
    SIGNATURE = "906e79d54e69e688680abee54ec0c49ce2561eb5abfd01865b31cb3ed738272c7cfc4fc8cc1c3590dd5757e622639b01a510945d7f7c9d1ceda20a50a817080d"
    BLOCK_HASH = "ab459013b27fdc6fe98eed567bd0c1754e0628a4cc16883bf0170a29da37ad46"
    TTL = 86400
    ORIGIN = "https://api.multiversx.com"
    TOKEN = f"aHR0cHM6Ly9hcGkubXVsdGl2ZXJzeC5jb20.{BLOCK_HASH}.{TTL}.e30"
    ACCESS_TOKEN = "ZXJkMXFuazJ2bXVxeXdmcXRkbmttYXV2cG04bHMweGgwMGs4eGV1cHVhZjZjbTZjZDRyeDg5cXF6MHBwZ2w.YUhSMGNITTZMeTloY0drdWJYVnNkR2wyWlhKemVDNWpiMjAuYWI0NTkwMTNiMjdmZGM2ZmU5OGVlZDU2N2JkMGMxNzU0ZTA2MjhhNGNjMTY4ODNiZjAxNzBhMjlkYTM3YWQ0Ni44NjQwMC5lMzA.906e79d54e69e688680abee54ec0c49ce2561eb5abfd01865b31cb3ed738272c7cfc4fc8cc1c3590dd5757e622639b01a510945d7f7c9d1ceda20a50a817080d"
    INVALID_HASH_ERROR = "Validation failed for block hash 'hash'. Length should be 64."

    def test_latest_block_should_return_signable_token(self, mocker: Any):
        mock(mocker, 200, [{"hash": self.BLOCK_HASH}])
        config = NativeAuthClientConfig(origin=self.ORIGIN, expiry_seconds=self.TTL)
        client = NativeAuthClient(config)
        token = client.initialize()
        assert token == self.TOKEN

    def test_throws_internal_server_error(self, mocker: Any):
        mock(mocker, 500, {})
        client = NativeAuthClient()
        with pytest.raises(Exception):
            client.initialize()

    # if `/blocks/latest` raises error should fallback to `/blocks?size=1`
    def test_fallback_mechanism(self, mocker: Any):
        mock(
            mocker,
            400,
            [
                {
                    "statusCode": 400,
                    "message": self.INVALID_HASH_ERROR,
                    "error": "Bad request",
                }
            ],
        )
        mock(mocker, 200, {"hash": self.BLOCK_HASH})

        config = NativeAuthClientConfig(origin=self.ORIGIN, expiry_seconds=self.TTL)
        client = NativeAuthClient(config)

        token = client.initialize()
        assert token == self.TOKEN

    def test_generate_access_token(self):
        client = NativeAuthClient()
        access_token = client.get_token(self.ADDRESS, self.TOKEN, self.SIGNATURE)
        assert access_token == self.ACCESS_TOKEN


class TestNativeAuthWithGateway:
    ADDRESS = "erd1qnk2vmuqywfqtdnkmauvpm8ls0xh00k8xeupuaf6cm6cd4rx89qqz0ppgl"
    SIGNATURE = "906e79d54e69e688680abee54ec0c49ce2561eb5abfd01865b31cb3ed738272c7cfc4fc8cc1c3590dd5757e622639b01a510945d7f7c9d1ceda20a50a817080d"
    BLOCK_HASH = "ab459013b27fdc6fe98eed567bd0c1754e0628a4cc16883bf0170a29da37ad46"
    TTL = 86400
    ORIGIN = "https://api.multiversx.com"
    TOKEN = f"aHR0cHM6Ly9hcGkubXVsdGl2ZXJzeC5jb20.{BLOCK_HASH}.{TTL}.e30"
    ACCESS_TOKEN = "ZXJkMXFuazJ2bXVxeXdmcXRkbmttYXV2cG04bHMweGgwMGs4eGV1cHVhZjZjbTZjZDRyeDg5cXF6MHBwZ2w.YUhSMGNITTZMeTloY0drdWJYVnNkR2wyWlhKemVDNWpiMjAuYWI0NTkwMTNiMjdmZGM2ZmU5OGVlZDU2N2JkMGMxNzU0ZTA2MjhhNGNjMTY4ODNiZjAxNzBhMjlkYTM3YWQ0Ni44NjQwMC5lMzA.906e79d54e69e688680abee54ec0c49ce2561eb5abfd01865b31cb3ed738272c7cfc4fc8cc1c3590dd5757e622639b01a510945d7f7c9d1ceda20a50a817080d"
    LATEST_ROUND = 115656
    METASHARD = 4294967295
    GATEWAY = "https://gateway.multiversx.com"

    def test_latest_block_should_return_signable_token(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": {"data": {"status": {"erd_current_round": self.LATEST_ROUND}}},
            },
            {
                "code": 200,
                "response": {"data": {"blocks": [{"shard": self.METASHARD, "hash": self.BLOCK_HASH}]}},
            },
        ]
        mock_side_effect(mocker, responses)

        config = NativeAuthClientConfig(
            origin=self.ORIGIN,
            gateway_url=self.GATEWAY,
            block_hash_shard=self.METASHARD,
            expiry_seconds=self.TTL,
        )
        client = NativeAuthClient(config)
        token = client.initialize()
        assert token == self.TOKEN

    def test_should_raise_internal_server_error(self, mocker: Any):
        responses = [
            {
                "code": 500,
                "response": {"data": {"status": {"erd_current_round": self.LATEST_ROUND}}},
            }
        ]
        mock_side_effect(mocker, responses)

        config = NativeAuthClientConfig(gateway_url=self.GATEWAY, block_hash_shard=self.METASHARD)
        client = NativeAuthClient(config)

        with pytest.raises(Exception):
            client.initialize()

    def test_raises_internal_server_error_on_second_request(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": {"data": {"status": {"erd_current_round": self.LATEST_ROUND}}},
            },
            {"code": 500, "response": {""}},
        ]
        mock_side_effect(mocker, responses)

        config = NativeAuthClientConfig(gateway_url=self.GATEWAY, block_hash_shard=self.METASHARD)
        client = NativeAuthClient(config)

        with pytest.raises(Exception):
            client.initialize()

    def test_generate_access_token(self):
        config = NativeAuthClientConfig(gateway_url=self.GATEWAY, block_hash_shard=self.METASHARD)
        client = NativeAuthClient(config)

        access_token = client.get_token(address=self.ADDRESS, token=self.TOKEN, signature=self.SIGNATURE)

        assert access_token == self.ACCESS_TOKEN
