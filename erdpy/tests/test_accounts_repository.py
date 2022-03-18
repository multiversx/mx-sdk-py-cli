from erdpy.accounts import Address
from erdpy.accounts_repository import AccountsRepository
from erdpy.interfaces import IAddress, IElrondProxy
from erdpy.workstation import get_tools_folder

TESTNET_USERS_FOLDER = get_tools_folder() / "testwallets" / "latest" / "users"
DUMMY_NONCE = 42


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
    proxy = ElrondProxyStub()
    repository = AccountsRepository.create_from_folder(TESTNET_USERS_FOLDER)
    repository.sync_nonces(proxy)

    for account in repository.get_all():
        assert account.nonce == DUMMY_NONCE


class ElrondProxyStub(IElrondProxy):
    def get_account_nonce(self, address: IAddress) -> int:
        return DUMMY_NONCE
