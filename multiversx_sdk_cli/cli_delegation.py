from pathlib import Path
from typing import Any

from multiversx_sdk import (
    Address,
    DelegationTransactionsOutcomeParser,
    ProxyNetworkProvider,
    TransactionsFactoryConfig,
    ValidatorPublicKey,
    ValidatorsSigners,
)

from multiversx_sdk_cli import cli_shared, errors, utils
from multiversx_sdk_cli.args_validation import (
    validate_broadcast_args,
    validate_chain_id_args,
    validate_nonce_args,
    validate_proxy_argument,
    validate_receiver_args,
)
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.delegation import DelegationOperations


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(subparsers, "staking-provider", "Staking provider omnitool")
    subparsers = parser.add_subparsers()

    # create new delegation contract
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "create-new-delegation-contract",
        "Create a new delegation system smart contract, transferred value must be "
        "greater than baseIssuingCost + min deposit value",
    )
    _add_common_arguments(args, sub)
    sub.add_argument(
        "--total-delegation-cap",
        required=True,
        type=int,
        help="the total delegation contract capacity",
    )
    sub.add_argument("--service-fee", required=True, type=int, help="the delegation contract service fee")
    sub.set_defaults(func=do_create_delegation_contract)

    # get contract address
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "get-contract-address",
        "Get create contract address by transaction hash",
    )
    sub.add_argument("--create-tx-hash", required=True, type=str, help="the hash")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_contract_address_by_deploy_tx_hash)

    # add a new node
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "add-nodes",
        "Add new nodes must be called by the contract owner",
    )
    sub.add_argument(
        "--validators-pem", required=True, type=str, help="a PEM file holding the BLS keys; can contain multiple nodes"
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        type=str,
        help="bech32 address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=add_new_nodes)

    # remove nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "remove-nodes",
        "Remove nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes as CSV (addrA,addrB)")
    sub.add_argument("--validators-pem", type=str, help="a PEM file holding the BLS keys; can contain multiple nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        type=str,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=remove_nodes)

    # stake nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "stake-nodes",
        "Stake nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes as CSV (addrA,addrB)")
    sub.add_argument("--validators-pem", type=str, help="a PEM file holding the BLS keys; can contain multiple nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        type=str,
        help="bech32 address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=stake_nodes)

    # unbond nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "unbond-nodes",
        "Unbond nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes as CSV (addrA,addrB)")
    sub.add_argument("--validators-pem", type=str, help="a PEM file holding the BLS keys; can contain multiple nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=unbond_nodes)

    # unstake nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "unstake-nodes",
        "Unstake nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes as CSV (addrA,addrB)")
    sub.add_argument("--validators-pem", type=str, help="a PEM file holding the BLS keys; can contain multiple nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=unstake_nodes)

    # unjail nodes
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "unjail-nodes",
        "Unjail nodes must be called by the contract owner",
    )
    sub.add_argument("--bls-keys", help="a list with the bls keys of the nodes as CSV (addrA,addrB)")
    sub.add_argument("--validators-pem", type=str, help="a PEM file holding the BLS keys; can contain multiple nodes")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=unjail_nodes)

    # delegate
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "delegate",
        "Delegate funds to a delegation contract",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=delegate)

    # claim rewards
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "claim-rewards",
        "Claim the rewards earned for delegating",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=claim_rewards)

    # redelegate rewards
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "redelegate-rewards",
        "Redelegate the rewards earned for delegating",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=redelegate_rewards)

    # undelegate
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "undelegate",
        "Undelegate funds from a delegation contract",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=undelegate)

    # withdraw
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "withdraw",
        "Withdraw funds from a delegation contract",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=withdraw)

    # change service fee
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "change-service-fee",
        "Change service fee must be called by the contract owner",
    )
    sub.add_argument("--service-fee", required=True, type=int, help="new service fee value")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=change_service_fee)

    # modify total delegation cap
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "modify-delegation-cap",
        "Modify delegation cap must be called by the contract owner",
    )
    sub.add_argument("--delegation-cap", required=True, help="new delegation contract capacity")
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=modify_delegation_cap)

    # set automatic activation
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "automatic-activation",
        "Automatic activation must be called by the contract owner",
    )

    sub.add_argument(
        "--set",
        action="store_true",
        required=not (utils.is_arg_present(args, "--unset")),
        help="set automatic activation True",
    )
    sub.add_argument(
        "--unset",
        action="store_true",
        required=not (utils.is_arg_present(args, "--set")),
        help="set automatic activation False",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=automatic_activation)

    # set redelegate cap
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "redelegate-cap",
        "Redelegate cap must be called by the contract owner",
    )

    sub.add_argument(
        "--set",
        action="store_true",
        required=not (utils.is_arg_present(args, "--unset")),
        help="set redelegate cap True",
    )
    sub.add_argument(
        "--unset",
        action="store_true",
        required=not (utils.is_arg_present(args, "--set")),
        help="set redelegate cap False",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=redelegate_cap)

    # set metadata
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "set-metadata",
        "Set metadata must be called by the contract owner",
    )

    sub.add_argument("--name", required=True, type=str, help="name field in staking provider metadata")
    sub.add_argument("--website", required=True, type=str, help="website field in staking provider metadata")
    sub.add_argument(
        "--identifier",
        required=True,
        type=str,
        help="identifier field in staking provider metadata",
    )
    sub.add_argument(
        "--delegation-contract",
        required=True,
        help="address of the delegation contract",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=set_metadata)

    # convert validator to delegation contract
    sub = cli_shared.add_command_subparser(
        subparsers,
        "staking-provider",
        "make-delegation-contract-from-validator",
        "Create a delegation contract from validator data. Must be called by the node operator",
    )

    sub.add_argument(
        "--max-cap",
        required=True,
        type=int,
        help="total delegation cap in EGLD, fully denominated. Use value 0 for uncapped",
    )
    sub.add_argument(
        "--fee",
        required=True,
        type=int,
        help="service fee as hundredths of percents. (e.g.  a service fee of 37.45 percent is expressed by the integer 3745)",
    )
    _add_common_arguments(args, sub)
    sub.set_defaults(func=make_new_contract_from_validator_data)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_common_arguments(args: list[str], sub: Any):
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_outfile_arg(sub, what="signed transaction, hash")
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)


def validate_arguments(args: Any):
    validate_nonce_args(args)
    validate_receiver_args(args)
    validate_broadcast_args(args)
    validate_chain_id_args(args)


def _get_delegation_controller(args: Any):
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    config = TransactionsFactoryConfig(chain_id)
    delegation = DelegationOperations(config)
    return delegation


def do_create_delegation_contract(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    delegation = _get_delegation_controller(args)

    tx = delegation.prepare_transaction_for_new_delegation_contract(
        owner=sender,
        native_amount=int(args.value),
        total_delegation_cap=int(args.total_delegation_cap),
        service_fee=int(args.service_fee),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def get_contract_address_by_deploy_tx_hash(args: Any):
    validate_proxy_argument(args)

    config = get_config_for_network_providers()
    proxy = ProxyNetworkProvider(url=args.proxy, config=config)
    transaction = proxy.get_transaction(args.create_tx_hash)

    parser = DelegationTransactionsOutcomeParser()
    outcome = parser.parse_create_new_delegation_contract(transaction)

    if len(outcome) > 1:
        print("This transaction created more than one delegation contract.")

    for i in range(len(outcome)):
        print(f"Delegation contract address: {outcome[i].contract_address.to_bech32()}")


def add_new_nodes(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    public_keys, signed_messages = _get_public_keys_and_signed_messages(args)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_adding_nodes(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        public_keys=public_keys,
        signed_messages=signed_messages,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def _get_public_keys_and_signed_messages(args: Any) -> tuple[list[ValidatorPublicKey], list[bytes]]:
    validators_file_path = Path(args.validators_pem).expanduser()
    validators_file = ValidatorsSigners.new_from_pem(validators_file_path)
    signers = validators_file.get_signers()

    pubkey = Address.new_from_bech32(args.delegation_contract).get_public_key()

    public_keys: list[ValidatorPublicKey] = []
    signed_messages: list[bytes] = []
    for signer in signers:
        signed_message = signer.sign(pubkey)

        public_keys.append(signer.secret_key.generate_public_key())
        signed_messages.append(signed_message)

    return public_keys, signed_messages


def remove_nodes(args: Any):
    validate_arguments(args)
    _check_if_either_bls_keys_or_validators_file_are_provided(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    public_keys = _load_validators_public_keys(args)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_removing_nodes(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        public_keys=public_keys,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def _load_validators_public_keys(args: Any) -> list[ValidatorPublicKey]:
    if args.bls_keys:
        return _parse_public_bls_keys(args.bls_keys)

    validators_file_path = Path(args.validators_pem).expanduser()
    validators_file = ValidatorsSigners.new_from_pem(validators_file_path)
    return validators_file.get_public_keys()


def _parse_public_bls_keys(public_bls_keys: str) -> list[ValidatorPublicKey]:
    keys = public_bls_keys.split(",")
    validator_public_keys: list[ValidatorPublicKey] = []

    for key in keys:
        validator_public_keys.append(ValidatorPublicKey(bytes.fromhex(key)))

    return validator_public_keys


def stake_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    public_keys = _load_validators_public_keys(args)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_staking_nodes(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        public_keys=public_keys,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def _check_if_either_bls_keys_or_validators_file_are_provided(args: Any):
    bls_keys = args.bls_keys
    validators_file = args.validators_pem

    if not bls_keys and not validators_file:
        raise errors.BadUsage("No bls keys or validators file provided. Use either `--bls-keys` or `--validators-pem`")


def unbond_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    public_keys = _load_validators_public_keys(args)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_unbonding_nodes(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        public_keys=public_keys,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def unstake_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    public_keys = _load_validators_public_keys(args)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_unstaking_nodes(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        public_keys=public_keys,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def unjail_nodes(args: Any):
    _check_if_either_bls_keys_or_validators_file_are_provided(args)
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    public_keys = _load_validators_public_keys(args)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_unjailing_nodes(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        public_keys=public_keys,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def delegate(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    value = int(args.value)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_delegating(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=value,
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def claim_rewards(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_claiming_rewards(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )
    cli_shared.send_or_simulate(tx, args)


def redelegate_rewards(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_redelegating_rewards(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )
    cli_shared.send_or_simulate(tx, args)


def undelegate(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0
    value = int(args.value)

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_undelegating(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=value,
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def withdraw(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_withdrawing(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def change_service_fee(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_changing_service_fee(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        service_fee=int(args.service_fee),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def modify_delegation_cap(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_modifying_delegation_cap(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        delegation_cap=int(args.delegation_cap),
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def automatic_activation(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_automatic_activation(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        set=args.set,
        unset=args.unset,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def redelegate_cap(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_redelegate_cap(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        set=args.set,
        unset=args.unset,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def set_metadata(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_setting_metadata(
        owner=sender,
        delegation_contract=Address.new_from_bech32(args.delegation_contract),
        name=args.name,
        website=args.website,
        identifier=args.identifier,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)


def make_new_contract_from_validator_data(args: Any):
    validate_arguments(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    gas_limit = args.gas_limit if args.gas_limit else 0

    delegation = _get_delegation_controller(args)
    tx = delegation.prepare_transaction_for_creating_delegation_contract_from_validator(
        owner=sender,
        max_cap=args.max_cap,
        service_fee=args.fee,
        gas_limit=gas_limit,
        gas_price=int(args.gas_price),
        value=int(args.value),
        nonce=sender.nonce,
        version=int(args.version),
        options=int(args.options),
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(tx, args)
