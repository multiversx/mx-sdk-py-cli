from multiversx_sdk import Address, ProxyNetworkProvider

from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_cli.cli import main
from multiversx_sdk_cli.config import get_config_for_network_providers


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
    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider("https://testnet-api.multiversx.com", config=config)
    account.sync_nonce(proxy)
    assert True if account.nonce else False


def test_query_contract():
    result = main(
        [
            "contract",
            "query",
            "erd1qqqqqqqqqqqqqpgq6qr0w0zzyysklfneh32eqp2cf383zc89d8sstnkl60",
            "--function",
            "getSum",
            "--proxy",
            "https://devnet-api.multiversx.com",
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
