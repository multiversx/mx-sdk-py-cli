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
    assert False if result else True


def test_sync_nonce():
    account = Account(address=Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"))
    proxy = ProxyNetworkProvider("https://testnet-api.multiversx.com")
    account.sync_nonce(proxy)
    assert True if account.nonce else False


def test_query_contract():
    result = main(
        [
            "contract",
            "query",
            "erd1qqqqqqqqqqqqqpgq8z2zzyu30f4607hth0tfj5m3vpjvwrvvrawqw09jem",
            "--function",
            "getSum",
            "--proxy",
            "https://testnet-api.multiversx.com",
        ]
    )
    assert False if result else True


def test_get_transaction():
    result = main(
        [
            "tx",
            "get",
            "--proxy",
            "https://devnet-api.multiversx.com",
            "--hash",
            "06f381ee88ed27ba08a35f995f17dceb737e1a99c5c4da0c247bbe7aa1d18551",
        ]
    )
    assert False if result else True
