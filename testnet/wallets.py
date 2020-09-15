from erdpy.accounts import Address
from erdpy.testnet.config import TestnetConfiguration
from erdpy.wallet import derive_keys, pem

# Non-private mnemonics, for developer use
VALIDATOR_REWARDS_MNEMONIC = "teach wonder cheap pottery merge jeans ketchup spider federal agent armed tobacco myth priority hurt pony thing dune switch grace jewel chunk luggage genius"
USER_ACCOUNTS_MNEMONIC = "moral volcano peasant pass circle pen over picture flat shop clap goat never lyrics gather prepare woman film husband gravity behind test tiger improve"


def get_validators_addresses(testnet_config: TestnetConfiguration):
    for validator_index in range(testnet_config.num_all_validators()):
        rewards_address = get_rewards_address(validator_index)
        bls_pubkey = get_bls_pubkey(testnet_config, validator_index)
        yield {
            "address": rewards_address.bech32(),
            "pubkey": bls_pubkey,
        }


def get_rewards_address(validator_index):
    _, public_key = derive_keys(VALIDATOR_REWARDS_MNEMONIC, validator_index)
    address = Address(public_key)
    return address


def get_bls_pubkey(testnet_config: TestnetConfiguration, validator_index):
    pem_file = testnet_config.validator_config_folder(validator_index) / "validatorKey.pem"
    _, bls_key = pem.parse_validator_pem(pem_file)
    return bls_key
