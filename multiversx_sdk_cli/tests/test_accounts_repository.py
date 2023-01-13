from typing import Protocol

from multiversx_sdk_cli.accounts import Address, AccountOnNetwork
from multiversx_sdk_cli.accounts_repository import AccountsRepository
from multiversx_sdk_cli.interfaces import IAddress
from multiversx_sdk_cli.workstation import get_tools_folder

TESTNET_USERS_FOLDER = get_tools_folder() / "testwallets" / "latest" / "users"
DUMMY_NONCE = 42


class INetworkProvider(Protocol):
    def get_account(self, address: IAddress) -> AccountOnNetwork:
        ...


def test_create_from_folder():
    repository = AccountsRepository.create_from_folder(TESTNET_USERS_FOLDER)
    assert len(repository) == 12


def test_create_from_files():
    repository = AccountsRepository.create_from_files([
        TESTNET_USERS_FOLDER / "alice.pem",
        TESTNET_USERS_FOLDER / "bob.pem",
        TESTNET_USERS_FOLDER / "carol.pem"
    ])
    assert len(repository) == 3


def test_create_performs_deduplication():
    repository = AccountsRepository.create_from_files([
        TESTNET_USERS_FOLDER / "alice.pem",
        TESTNET_USERS_FOLDER / "alice.pem"
    ])
    assert len(repository) == 1


def test_get_account():
    repository = AccountsRepository.create_from_folder(TESTNET_USERS_FOLDER)
    alice = repository.get_account(Address("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"))
    bob = repository.get_account(Address("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"))
    nobody = repository.get_account(Address("erd19kc9n22h6yy07e9tdnfdpuu5fr5qkcyzmw9tnumkygw056jxhutskpyree"))

    assert alice is not None
    assert bob is not None
    assert nobody is None


def test_sync_nonces():
    proxy = ProxyStub()
    repository = AccountsRepository.create_from_folder(TESTNET_USERS_FOLDER)
    repository.sync_nonces(proxy)

    for account in repository.get_all():
        assert account.nonce == DUMMY_NONCE


class ProxyStub(INetworkProvider):    
    def get_account(self, address: IAddress) -> AccountOnNetwork:
        account =  AccountOnNetwork()
        account.nonce = DUMMY_NONCE

        return account
