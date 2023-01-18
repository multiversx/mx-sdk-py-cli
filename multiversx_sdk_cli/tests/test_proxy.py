from pathlib import Path
from multiversx_sdk_cli.cli import main
from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_network_providers.proxy_network_provider import ProxyNetworkProvider


def test_get_transactions():
    output_file = Path(__file__).parent / "testdata-out" / "transactions.txt"

    main(
        [
            "account",
            "get-transactions",
            "--address",
            "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            "--outfile",
            str(output_file),
        ]
    )
    assert Path.is_file(output_file) == True


def test_get_account():
    result = main(
        [
            "account",
            "get",
            "--address",
            "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
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
            "3895403",
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
            "85ccf29f51d7acf0fbb6cfcf2e4b89eee2f2264dd989edd5a870d33dacc24743",
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
    result = main(["network", "num-shards"])

    if not result:
        assert True
    else:
        assert False


def test_get_last_block_nonce():
    result = main(["network", "block-nonce", "--shard", "4294967295"])

    if not result:
        assert True
    else:
        assert False


def test_get_chain_id():
    result = main(["network", "chain"])

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
            "2cb813be9d5e5040abb2522da75fa5c8d94f72caa510ff51d7525659f398298b",
        ]
    )

    if not result:
        assert True
    else:
        assert False
