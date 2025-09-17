from typing import Any

from multiversx_sdk import (
    Address,
    DelegatedVoteInfo,
    GovernanceConfig,
    GovernanceController,
    ProposalInfo,
    ProxyNetworkProvider,
    Transaction,
    VoteType,
)

from multiversx_sdk_cli import cli_shared, utils
from multiversx_sdk_cli.args_validation import (
    validate_broadcast_args,
    validate_chain_id_args,
    validate_proxy_argument,
)
from multiversx_sdk_cli.cli_output import CLIOutputBuilder
from multiversx_sdk_cli.config import get_config_for_network_providers
from multiversx_sdk_cli.config_env import get_address_hrp
from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.interfaces import IAccount
from multiversx_sdk_cli.signing_wrapper import SigningWrapper


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers, "governance", "Propose, vote and interact with the governance contract."
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "propose",
        f"Create a new governance proposal.{CLIOutputBuilder.describe()}",
    )

    _add_commit_hash_arg(sub)
    sub.add_argument("--start-vote-epoch", required=True, type=int, help="the epoch in which the voting will start")
    sub.add_argument("--end-vote-epoch", required=True, type=int, help="the epoch in which the voting will stop")
    _add_common_args(args, sub)

    sub.set_defaults(func=create_proposal)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "vote",
        f"Vote for a governance proposal.{CLIOutputBuilder.describe()}",
    )

    _add_proposal_nonce_arg(sub)
    sub.add_argument(
        "--vote",
        required=True,
        type=str,
        choices=["yes", "no", "veto", "abstain"],
        help="the type of vote",
    )
    _add_common_args(args, sub)

    sub.set_defaults(func=vote)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "close-proposal",
        f"Close a governance proposal.{CLIOutputBuilder.describe()}",
    )

    _add_proposal_nonce_arg(sub)
    _add_common_args(args, sub)

    sub.set_defaults(func=close_proposal)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "clear-ended-proposals",
        f"Clear ended proposals.{CLIOutputBuilder.describe()}",
    )

    sub.add_argument(
        "--proposers",
        nargs="+",
        required=True,
        type=str,
        help="a list of users who initiated the proposals (e.g. --proposers erd1..., erd1...)",
    )
    _add_common_args(args, sub)

    sub.set_defaults(func=clear_ended_proposals)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "claim-accumulated-fees",
        f"Claim the accumulated fees.{CLIOutputBuilder.describe()}",
    )
    _add_common_args(args, sub)

    sub.set_defaults(func=claim_accumulated_fees)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "change-config",
        f"Change the config of the contract.{CLIOutputBuilder.describe()}",
    )

    sub.add_argument("--proposal-fee", required=True, type=int, help="the cost to create a new proposal")
    sub.add_argument(
        "--lost-proposal-fee",
        required=True,
        type=int,
        help="the amount of native tokens the proposer loses if the proposal fails",
    )
    sub.add_argument(
        "--min-quorum", required=True, type=int, help="the min quorum to be reached for the proposal to pass"
    )
    sub.add_argument("--min-veto-threshold", required=True, type=int, help="the min veto threshold")
    sub.add_argument("--min-pass-threshold", required=True, type=int, help="the min pass threshold")
    _add_common_args(args, sub)

    sub.set_defaults(func=change_config)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "get-voting-power",
        f"Get the voting power of an user.{CLIOutputBuilder.describe()}",
    )

    sub.add_argument("--user", required=True, type=str, help="the bech32 address of the user")
    cli_shared.add_proxy_arg(sub)

    sub.set_defaults(func=get_voting_power)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "get-config",
        f"Get the config of the governance contract.{CLIOutputBuilder.describe()}",
    )

    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_config)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "get-proposal",
        f"Get info about a proposal.{CLIOutputBuilder.describe()}",
    )

    _add_proposal_nonce_arg(sub)
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_proposal)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "governance",
        "get-delegated-vote-info",
        f"Get info about a delegated vote.{CLIOutputBuilder.describe()}",
    )

    sub.add_argument("--contract", required=True, type=str, help="the bech32 address of the contract")
    sub.add_argument("--user", required=True, type=str, help="the bech32 address of the user")
    cli_shared.add_proxy_arg(sub)
    sub.set_defaults(func=get_delegated_vote_info)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def _add_commit_hash_arg(sub: Any):
    sub.add_argument("--commit-hash", required=True, type=str, help="the commit hash of the proposal")


def _add_proposal_nonce_arg(sub: Any):
    sub.add_argument("--proposal-nonce", required=True, type=int, help="the nonce of the proposal")


def _add_common_args(args: Any, sub: Any):
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)
    cli_shared.add_outfile_arg(sub)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_wait_result_and_timeout_args(sub)


def _ensure_args(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)


def _initialize_controller(args: Any) -> GovernanceController:
    chain = args.chain if hasattr(args, "chain") else None
    chain_id = cli_shared.get_chain_id(args.proxy, chain)
    config = get_config_for_network_providers()
    proxy_url = args.proxy if args.proxy else ""
    proxy = ProxyNetworkProvider(url=proxy_url, config=config)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)

    return GovernanceController(
        chain_id=chain_id,
        network_provider=proxy,
        address_hrp=get_address_hrp(),
        gas_limit_estimator=gas_estimator,
    )


def _sign_transaction(transaction: Transaction, sender: IAccount, guardian_and_relayer_data: GuardianRelayerData):
    signer = SigningWrapper()
    signer.sign_transaction(
        transaction=transaction,
        sender=sender,
        guardian_and_relayer=guardian_and_relayer_data,
    )


def create_proposal(args: Any):
    _ensure_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    controller = _initialize_controller(args)
    transaction = controller.create_transaction_for_new_proposal(
        sender=sender,
        nonce=sender.nonce,
        commit_hash=args.commit_hash,
        start_vote_epoch=args.start_vote_epoch,
        end_vote_epoch=args.end_vote_epoch,
        native_token_amount=args.value,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    _sign_transaction(transaction, sender, guardian_and_relayer_data)
    cli_shared.send_or_simulate(transaction, args)


def vote(args: Any):
    _ensure_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    [vote_value] = [v for v in VoteType if v.value == args.vote]
    controller = _initialize_controller(args)

    transaction = controller.create_transaction_for_voting(
        sender=sender,
        nonce=sender.nonce,
        proposal_nonce=args.proposal_nonce,
        vote=vote_value,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    _sign_transaction(transaction, sender, guardian_and_relayer_data)
    cli_shared.send_or_simulate(transaction, args)


def close_proposal(args: Any):
    _ensure_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    controller = _initialize_controller(args)
    transaction = controller.create_transaction_for_closing_proposal(
        sender=sender,
        nonce=sender.nonce,
        proposal_nonce=args.proposal_nonce,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    _sign_transaction(transaction, sender, guardian_and_relayer_data)
    cli_shared.send_or_simulate(transaction, args)


def clear_ended_proposals(args: Any):
    _ensure_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    proposers = [Address.new_from_bech32(proposer) for proposer in args.proposers]
    controller = _initialize_controller(args)

    transaction = controller.create_transaction_for_clearing_ended_proposals(
        sender=sender,
        nonce=sender.nonce,
        proposers=proposers,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    _sign_transaction(transaction, sender, guardian_and_relayer_data)
    cli_shared.send_or_simulate(transaction, args)


def claim_accumulated_fees(args: Any):
    _ensure_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    controller = _initialize_controller(args)
    transaction = controller.create_transaction_for_claiming_accumulated_fees(
        sender=sender,
        nonce=sender.nonce,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    _sign_transaction(transaction, sender, guardian_and_relayer_data)
    cli_shared.send_or_simulate(transaction, args)


def change_config(args: Any):
    _ensure_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )

    controller = _initialize_controller(args)
    transaction = controller.create_transaction_for_changing_config(
        sender=sender,
        nonce=sender.nonce,
        proposal_fee=args.proposal_fee,
        lost_proposal_fee=args.lost_proposal_fee,
        min_quorum=args.min_quorum,
        min_veto_threshold=args.min_veto_threshold,
        min_pass_threshold=args.min_pass_threshold,
        guardian=guardian_and_relayer_data.guardian.address if guardian_and_relayer_data.guardian else None,
        relayer=guardian_and_relayer_data.relayer.address if guardian_and_relayer_data.relayer else None,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
    )

    _sign_transaction(transaction, sender, guardian_and_relayer_data)
    cli_shared.send_or_simulate(transaction, args)


def get_voting_power(args: Any):
    validate_proxy_argument(args)

    controller = _initialize_controller(args)
    user = Address.new_from_bech32(args.user)

    voting_power = controller.get_voting_power(user)
    print("Voting power: ", voting_power)


def get_config(args: Any):
    validate_proxy_argument(args)

    controller = _initialize_controller(args)

    contract_config = controller.get_config()
    utils.dump_out_json(_config_to_dict(contract_config))


def get_proposal(args: Any):
    validate_proxy_argument(args)

    controller = _initialize_controller(args)

    info = controller.get_proposal(args.proposal_nonce)
    utils.dump_out_json(_proposal_to_dict(info))


def get_delegated_vote_info(args: Any):
    validate_proxy_argument(args)

    controller = _initialize_controller(args)

    contract = Address.new_from_bech32(args.contract)
    user = Address.new_from_bech32(args.user)
    info = controller.get_delegated_vote_info(contract, user)
    utils.dump_out_json(_delegated_vote_info_to_dict(info))


def _config_to_dict(config: GovernanceConfig) -> dict[str, Any]:
    return {
        "proposal_fee": config.proposal_fee,
        "min_quorum": config.min_quorum,
        "min_pass_threshold": config.min_pass_threshold,
        "min_veto_threshold": config.min_veto_threshold,
        "last_proposal_nonce": config.last_proposal_nonce,
    }


def _proposal_to_dict(proposal: ProposalInfo) -> dict[str, Any]:
    return {
        "cost": proposal.cost,
        "commit_hash": proposal.commit_hash,
        "nonce": proposal.nonce,
        "issuer": proposal.issuer.to_bech32(),
        "start_vote_epoch": proposal.start_vote_epoch,
        "end_vote_epoch": proposal.end_vote_epoch,
        "quorum_stake": proposal.quorum_stake,
        "num_yes_votes": proposal.num_yes_votes,
        "num_no_votes": proposal.num_no_votes,
        "num_veto_votes": proposal.num_veto_votes,
        "num_abstain_votes": proposal.num_abstain_votes,
        "is_closed": proposal.is_closed,
        "is_passed": proposal.is_passed,
    }


def _delegated_vote_info_to_dict(delegated_vote_info: DelegatedVoteInfo) -> dict[str, Any]:
    return {
        "used_stake": delegated_vote_info.used_stake,
        "used_power": delegated_vote_info.used_power,
        "total_stake": delegated_vote_info.total_stake,
        "total_power": delegated_vote_info.total_power,
    }
