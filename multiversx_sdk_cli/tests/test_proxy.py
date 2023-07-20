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


def test_get_hyperblock_by_nonce():
    result = main(
        [
            "hyperblock",
            "get",
            "--key",
            "4312144",
            "--proxy",
            "https://devnet-api.multiversx.com",
        ]
    )
    if not result:
        assert True
    else:
        assert False


def test_get_hyperblock_by_hash():
    result = main(
        [
            "hyperblock",
            "get",
            "--key",
            "756cb9c0a2d16b0fe9027a21c845a4f4eb1f1331630632669c88250128b40440",
            "--proxy",
            "https://devnet-api.multiversx.com",
        ]
    )
    if not result:
        assert True
    else:
        assert False


def test_sync_nonce():
    account = Account("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    proxy = ProxyNetworkProvider("https://devnet-api.multiversx.com")
    account.sync_nonce(proxy)

    assert account.nonce >= 11480


def test_query_contract():
    result = main(
        [
            "contract",
            "query",
            "erd1qqqqqqqqqqqqqpgquykqja5c4v33zdmnwglj3jphqwrelzdn396qlc9g33",
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


def test_get_num_shards():
    result = main(
        [
            "network",
            "num-shards",
            "--proxy",
            "https://testnet-api.multiversx.com"
        ]
    )

    if not result:
        assert True
    else:
        assert False


def test_get_last_block_nonce():
    result = main(
        [
            "network",
            "block-nonce",
            "--shard",
            "4294967295",
            "--proxy",
            "https://testnet-api.multiversx.com"
        ]
    )

    if not result:
        assert True
    else:
        assert False


def test_get_chain_id():
    result = main(
        [
            "network",
            "chain",
            "--proxy",
            "https://testnet-api.multiversx.com"
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
            "cbe2026b8d9c3ee75f2846ea8e0b646b19e6fca754e43edb4113757fc3350952",
        ]
    )

    if not result:
        assert True
    else:
        assert False
