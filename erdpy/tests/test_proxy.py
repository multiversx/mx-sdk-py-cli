import os
from erdpy.cli import main
from erdpy.accounts import Account
from erdpy_network.proxy_network_provider import ProxyNetworkProvider


def test_get_transactions():
    main(
        [
            "account",
            "get-transactions",
            "--address",
            "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
            "--outfile",
            "txs.txt",
        ]
    )
    assert os.path.isfile("txs.txt") == True


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
            "https://devnet-api.elrond.com",
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
            "https://devnet-api.elrond.com",
        ]
    )
    if not result:
        assert True
    else:
        assert False


def test_sync_nonce():
    account = Account("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    proxy = ProxyNetworkProvider("https://devnet-api.elrond.com")
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
            "https://devnet-api.elrond.com",
        ]
    )
    if not result:
        assert True
    else:
        assert False


def test_get_contract_address_by_deploy_tx_hash():
    result = main(
        [
            "staking-provider",
            "get-contract-address",
            "--create-tx-hash",
            "12b9820df0fd71fc4b81b13a5484a0038b256249aae358112892ba599808bf7e",
            "--proxy",
            "https://devnet-api.elrond.com",
        ]
    )
    if not result:
        assert True
    else:
        assert False
