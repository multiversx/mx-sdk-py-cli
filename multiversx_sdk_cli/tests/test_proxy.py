from multiversx_sdk_core import Address
from multiversx_sdk_network_providers.proxy_network_provider import \
    ProxyNetworkProvider

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.cli import main


def test_get_account():
    result = main(
        [
            "account",
            "get",
            "--address",
            "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            "--proxy",
            "https://testnet-api.multiversx.com"
        ]
    )
    if not result:
        assert True
    else:
        assert False


def test_sync_nonce():
    account = Account(address=Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"))
    proxy = ProxyNetworkProvider("https://devnet-api.multiversx.com")
    account.sync_nonce(proxy)

    assert account.nonce >= 42


def test_query_contract():
    result = main(
        [
            "contract",
            "query",
            "erd1qqqqqqqqqqqqqpgqpuz9r56ylk39x45cgqmaw2w8hfn47ft3d8ssavktr5",
            "--function",
            "getSum",
            "--proxy",
            "https://devnet-api.multiversx.com",
        ]
    )
    if not result:
        assert True
    else:
        assert False


def test_get_transaction():
    result = main(
        [
            "tx",
            "get",
            "--proxy",
            "https://devnet-api.multiversx.com",
            "--hash",
            "9e6ca966b18dc0317ff3be9b53be183ddb068a163769d286b2c1b1dff3ac00e5",
        ]
    )

    if not result:
        assert True
    else:
        assert False
