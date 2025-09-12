from typing import Any

from multiversx_sdk import Address, TokenType, TransactionsFactoryConfig

from multiversx_sdk_cli import cli_shared
from multiversx_sdk_cli.args_validation import (
    validate_broadcast_args,
    validate_chain_id_args,
)
from multiversx_sdk_cli.tokens import TokensManagementWrapper


def setup_parser(args: list[str], subparsers: Any) -> Any:
    parser = cli_shared.add_group_subparser(
        subparsers, "token", "Perform token management operations (issue tokens, create NFTs, set roles, etc.)"
    )
    subparsers = parser.add_subparsers()

    sub = cli_shared.add_command_subparser(subparsers, "token", "issue-fungible", "Issue a new fungible ESDT token.")
    add_issuing_tokens_args(
        sub,
        with_initial_supply=True,
        with_num_decimals=True,
        with_transfer_nft_create_role=False,
    )
    add_common_args(args, sub)
    sub.set_defaults(func=issue_fungible)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "issue-semi-fungible",
        "Issue a new semi-fungible ESDT token.",
    )
    add_issuing_tokens_args(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=issue_semi_fungible)

    sub = cli_shared.add_command_subparser(
        subparsers, "token", "issue-non-fungible", "Issue a new non-fungible ESDT token (NFT)."
    )
    add_issuing_tokens_args(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=issue_non_fungible)

    sub = cli_shared.add_command_subparser(subparsers, "token", "register-meta-esdt", "Register a MetaESDT token.")
    add_issuing_tokens_args(sub, with_num_decimals=True)
    add_common_args(args, sub)
    sub.set_defaults(func=register_meta_esdt)

    sub = cli_shared.add_command_subparser(
        subparsers, "token", "register-and-set-all-roles", "Register a token and set all roles."
    )
    sub.add_argument(
        "--token-name",
        required=True,
        type=str,
        help="the name of the token to be issued: 3-20 alphanumerical characters",
    )
    sub.add_argument(
        "--token-ticker",
        required=True,
        type=str,
        help="the ticker of the token to be issued: 3-10 UPPERCASE alphanumerical characters",
    )
    sub.add_argument(
        "--num-decimals",
        required=True,
        type=int,
        help="a numerical value between 0 and 18 representing number of decimals",
    )
    sub.add_argument(
        "--token-type",
        required=True,
        type=str,
        choices=["NFT", "SFT", "META", "FNG"],
        help="the token type",
    )
    add_common_args(args, sub)
    sub.set_defaults(func=register_and_set_all_roles)

    sub = cli_shared.add_command_subparser(
        subparsers, "token", "set-burn-role-globally", "Set the burn role globally for a token."
    )
    _add_token_identifier_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=set_burn_role_globally)

    sub = cli_shared.add_command_subparser(
        subparsers, "token", "unset-burn-role-globally", "Unset the burn role globally for a token."
    )
    _add_token_identifier_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=unset_burn_role_globally)

    sub = cli_shared.add_command_subparser(
        subparsers, "token", "set-special-role-fungible", "Set special roles on a fungible token for a user."
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_fungible(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=set_special_role_on_fungible)

    sub = cli_shared.add_command_subparser(
        subparsers, "token", "unset-special-role-fungible", "Unset special roles on a fungible token for a user."
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_fungible(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=unset_special_role_on_fungible)

    sub = cli_shared.add_command_subparser(
        subparsers, "token", "set-special-role-semi-fungible", "Set special roles on a semi-fungible token for a user."
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_semi_fungible(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=set_special_role_on_semi_fungible)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "unset-special-role-semi-fungible",
        "Unset special roles on a semi-fungible token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_semi_fungible(sub, with_nft_create=False)
    add_common_args(args, sub)
    sub.set_defaults(func=unset_special_role_on_semi_fungible)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "set-special-role-meta-esdt",
        "Set special roles on a meta-esdt token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_meta_esdt(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=set_special_role_on_meta_esdt)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "unset-special-role-meta-esdt",
        "Unset special roles on a meta-esdt token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_meta_esdt(sub, with_nft_create=False)
    add_common_args(args, sub)
    sub.set_defaults(func=unset_special_role_on_meta_esdt)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "set-special-role-nft",
        "Set special roles on a non-fungible token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_nft(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=set_special_role_on_nft)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "unset-special-role-nft",
        "Unset special roles on a non-fungible token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    _add_special_roles_args_for_nft(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=unset_special_role_on_nft)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "create-nft",
        "Create a non-fungible token.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--initial-quantity", type=int, required=True, help="The initial quantity of the token.")
    sub.add_argument("--name", type=str, required=True, help="The name of the token.")
    sub.add_argument("--royalties", type=int, required=True, help="The royalties of the token.")
    sub.add_argument("--hash", type=str, required=True, help="The hash of the token.")
    sub.add_argument("--attributes", type=str, required=True, help="The hex-string attributes of the token.")
    sub.add_argument("--uris", nargs="+", required=True, help="The uris of the token.")
    add_common_args(args, sub)
    sub.set_defaults(func=create_nft)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "pause",
        "Pause a token.",
    )
    _add_token_identifier_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=pause_token)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "unpause",
        "Unpause a token.",
    )
    _add_token_identifier_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=unpause_token)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "freeze",
        "Freeze a token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=freeze_token)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "unfreeze",
        "Unfreeze a token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=unfreeze_token)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "wipe",
        "Wipe a token for a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=wipe_token)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "local-mint",
        "Mint new tokens.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--supply-to-mint", required=True, type=int, help="The amount of new tokens to mint")
    add_common_args(args, sub)
    sub.set_defaults(func=local_mint)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "local-burn",
        "Burn tokens.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--supply-to-burn", required=True, type=int, help="The amount of tokens to burn")
    add_common_args(args, sub)
    sub.set_defaults(func=local_burn)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "update-attributes",
        "Update token attributes.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    sub.add_argument("--attributes", required=True, type=str, help="The hex-string attributes of the token")
    add_common_args(args, sub)
    sub.set_defaults(func=update_attributes)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "add-quantity",
        "Increase token quantity.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    sub.add_argument("--quantity", required=True, type=str, help="The quantity to add")
    add_common_args(args, sub)
    sub.set_defaults(func=add_quantity)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "burn-quantity",
        "Burn token quantity.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    sub.add_argument("--quantity", required=True, type=str, help="The quantity to burn")
    add_common_args(args, sub)
    sub.set_defaults(func=burn_quantity)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "modify-royalties",
        "Modify token royalties.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    sub.add_argument("--royalties", required=True, type=str, help="The new token royalties (e.g. 1234 for 12.34%)")
    add_common_args(args, sub)
    sub.set_defaults(func=modify_royalties)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "set-new-uris",
        "Set new uris.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    sub.add_argument("--uris", required=True, nargs="+", help="The new uris")
    add_common_args(args, sub)
    sub.set_defaults(func=set_new_uris)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "modify-creator",
        "Modify the creator of the token.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    add_common_args(args, sub)
    sub.set_defaults(func=modify_creator)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "update-metadata",
        "Update the metadata of the token.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    sub.add_argument("--token-name", required=True, type=str, help="The new name of the token")
    sub.add_argument("--royalties", required=True, type=int, help="The new token royalties (e.g. 1234 for 12.34%)")
    sub.add_argument("--hash", required=True, type=str, help="The new hash of the token")
    sub.add_argument(
        "--attributes", required=True, type=str, help="The new attributes of the token as a hex-encoded string"
    )
    sub.add_argument("--uris", required=True, nargs="+", help="The new uris")
    add_common_args(args, sub)
    sub.set_defaults(func=update_metadata)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "nft-metadata-recreate",
        "Recreate the metadata of the token.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    sub.add_argument("--token-name", required=True, type=str, help="The new name of the token")
    sub.add_argument("--royalties", required=True, type=int, help="The new token royalties (e.g. 1234 for 12.34%)")
    sub.add_argument("--hash", required=True, type=str, help="The new hash of the token")
    sub.add_argument(
        "--attributes", required=True, type=str, help="The new attributes of the token as a hex-encoded string"
    )
    sub.add_argument("--uris", required=True, nargs="+", help="The new uris")
    add_common_args(args, sub)
    sub.set_defaults(func=nft_metadata_recreate)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "change-to-dynamic",
        "Change a token to a dynamic token.",
    )
    _add_token_identifier_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=change_to_dynamic)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "update-token-id",
        "Update token id.",
    )
    _add_token_identifier_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=update_token_id)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "register-dynamic-token",
        "Register a dynamic token.",
    )
    sub.add_argument("--token-name", type=str, required=True, help="The token name")
    sub.add_argument("--token-ticker", type=str, required=True, help="The token ticker")
    sub.add_argument(
        "--token-type", type=str, required=True, choices=["NFT", "SFT", "FNG", "META"], help="The token type"
    )
    sub.add_argument(
        "--denominator", type=int, default=None, help="The number of decimals, only needed when token type is META ESDT"
    )
    add_common_args(args, sub)
    sub.set_defaults(func=register_dynamic_token)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "register-dynamic-and-set-all-roles",
        "Register a dynamic token and set all roles.",
    )
    sub.add_argument("--token-name", type=str, required=True, help="The token name")
    sub.add_argument("--token-ticker", type=str, required=True, help="The token ticker")
    sub.add_argument(
        "--token-type", type=str, required=True, choices=["NFT", "SFT", "FNG", "META"], help="The token type"
    )
    sub.add_argument(
        "--denominator", type=int, default=None, help="The number of decimals, only needed when token type is META ESDT"
    )
    add_common_args(args, sub)
    sub.set_defaults(func=register_dynamic_and_set_all_roles)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "transfer-ownership",
        "Transfer the ownership of a token to another user.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--new-owner", type=str, required=True, help="The new token owner")
    add_common_args(args, sub)
    sub.set_defaults(func=transfer_ownership)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "freeze-single-nft",
        "Freeze the NFT of a user.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    _add_user_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=freeze_single_nft)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "unfreeze-single-nft",
        "Unfreeze the NFT of a user.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", required=True, type=int, help="The nonce of the token as decimal value")
    _add_user_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=unfreeze_single_nft)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "change-sft-to-meta-esdt",
        "Change a semi fungible token to a Meta ESDT.",
    )
    sub.add_argument("--collection", required=True, type=str, help="The collection identifier")
    sub.add_argument("--decimals", type=int, required=True, help="The number of decimals the meta esdt will have")
    add_common_args(args, sub)
    sub.set_defaults(func=change_sft_to_meta_esdt)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "transfer-nft-create-role",
        "Transfer the nft create role to a user.",
    )
    _add_token_identifier_arg(sub)
    _add_user_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=transfer_nft_create_role)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "stop-nft-creation",
        "Stop the creation of new NFTs.",
    )
    _add_token_identifier_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=stop_nft_creation)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "wipe-single-nft",
        "Wipe the NFT of a user.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", type=int, required=True, help="The nonce of the NFT as a decimal number")
    _add_user_arg(sub)
    add_common_args(args, sub)
    sub.set_defaults(func=wipe_single_nft)

    sub = cli_shared.add_command_subparser(
        subparsers,
        "token",
        "add-uris",
        "Add uris for a token.",
    )
    _add_token_identifier_arg(sub)
    sub.add_argument("--token-nonce", type=int, required=True, help="The nonce of the NFT as a decimal number")
    sub.add_argument("--uris", nargs="+", required=True, help="The new uris to be added to the token.")
    add_common_args(args, sub)
    sub.set_defaults(func=add_uris)

    parser.epilog = cli_shared.build_group_epilog(subparsers)
    return subparsers


def add_common_args(args: list[str], sub: Any):
    cli_shared.add_wallet_args(args, sub)
    cli_shared.add_tx_args(args, sub, with_receiver=False, with_data=False)
    cli_shared.add_proxy_arg(sub)
    cli_shared.add_broadcast_args(sub)
    cli_shared.add_wait_result_and_timeout_args(sub)
    cli_shared.add_guardian_wallet_args(args, sub)
    cli_shared.add_relayed_v3_wallet_args(args, sub)
    cli_shared.add_outfile_arg(sub)


def add_issuing_tokens_args(
    sub: Any,
    with_initial_supply: bool = False,
    with_num_decimals: bool = False,
    with_transfer_nft_create_role: bool = True,
):
    sub.add_argument(
        "--token-name",
        required=True,
        type=str,
        help="the name of the token to be issued: 3-20 alphanumerical characters",
    )
    sub.add_argument(
        "--token-ticker",
        required=True,
        type=str,
        help="the ticker of the token to be issued: 3-10 UPPERCASE alphanumerical characters",
    )

    if with_initial_supply:
        sub.add_argument(
            "--initial-supply", required=True, type=int, help="the initial supply of the token to be issued"
        )

    if with_num_decimals:
        sub.add_argument(
            "--num-decimals",
            required=True,
            type=int,
            help="a numerical value between 0 and 18 representing number of decimals",
        )

    sub.add_argument(
        "--can-not-freeze",
        action="store_false",
        dest="can_freeze",
        default=True,
        help="make token not freezable",
    )
    sub.add_argument(
        "--can-not-wipe",
        action="store_false",
        dest="can_wipe",
        default=True,
        help="make token not wipable",
    )
    sub.add_argument(
        "--can-not-pause",
        action="store_false",
        dest="can_pause",
        default=True,
        help="make token not pausable",
    )
    sub.add_argument(
        "--can-not-change-owner",
        action="store_false",
        dest="can_change_owner",
        default=True,
        help="don't allow changing the token's owner",
    )
    sub.add_argument(
        "--can-not-upgrade",
        action="store_false",
        dest="can_upgrade",
        default=True,
        help="don't allow upgrading the token",
    )
    sub.add_argument(
        "--can-not-add-special-roles",
        action="store_false",
        dest="can_add_special_roles",
        default=True,
        help="don't allow special roles to be added for the token",
    )

    if with_transfer_nft_create_role:
        sub.add_argument(
            "--can-not-transfer-nft-create-role",
            action="store_false",
            dest="can_transfer_nft_create_role",
            default=True,
            help="don't allow for nft create roles to be transfered for the token",
        )


def _add_token_identifier_arg(sub: Any):
    sub.add_argument("--token-identifier", required=True, type=str, help="the token identifier")


def _add_user_arg(sub: Any):
    sub.add_argument("--user", required=True, type=str, help="the bech32 address of the user")


def _add_special_roles_args_for_fungible(sub: Any):
    sub.add_argument(
        "--local-mint",
        action="store_true",
        default=False,
        help="role for local minting",
    )
    sub.add_argument(
        "--local-burn",
        action="store_true",
        default=False,
        help="role for local burning",
    )
    sub.add_argument(
        "--esdt-transfer-role",
        action="store_true",
        default=False,
        help="role for esdt transfer",
    )


def _add_special_roles_args_for_meta_esdt(sub: Any, with_nft_create: bool = True):
    if with_nft_create:
        sub.add_argument(
            "--nft-create",
            action="store_true",
            default=False,
            help="role for nft create",
        )

    sub.add_argument(
        "--nft-burn",
        action="store_true",
        default=False,
        help="role for nft burn",
    )
    sub.add_argument(
        "--nft-add-quantity",
        action="store_true",
        default=False,
        help="role for adding quantity",
    )
    sub.add_argument(
        "--esdt-transfer-role",
        action="store_true",
        default=False,
        help="role for esdt transfer",
    )


def _add_special_roles_args_for_nft(sub: Any, with_nft_create: bool = True):
    if with_nft_create:
        sub.add_argument(
            "--nft-create",
            action="store_true",
            default=False,
            help="role for nft create",
        )

    sub.add_argument(
        "--nft-burn",
        action="store_true",
        default=False,
        help="role for nft burn",
    )
    sub.add_argument(
        "--nft-update-attributes",
        action="store_true",
        default=False,
        help="role for updating attributes",
    )

    sub.add_argument(
        "--nft-add-uri",
        action="store_true",
        default=False,
        help="role for adding uri",
    )

    sub.add_argument(
        "--esdt-transfer-role",
        action="store_true",
        default=False,
        help="role for esdt transfer",
    )

    sub.add_argument(
        "--nft-update",
        action="store_true",
        default=False,
        help="role for updating nft",
    )

    sub.add_argument(
        "--esdt-modify-royalties",
        action="store_true",
        default=False,
        help="role for modifying royalties",
    )

    sub.add_argument(
        "--esdt-set-new-uri",
        action="store_true",
        default=False,
        help="role for setting new uri",
    )

    sub.add_argument(
        "--esdt-modify-creator",
        action="store_true",
        default=False,
        help="role for modifying creator",
    )

    sub.add_argument(
        "--nft-recreate",
        action="store_true",
        default=False,
        help="role for recreating nft",
    )


def _add_special_roles_args_for_semi_fungible(sub: Any, with_nft_create: bool = True):
    if with_nft_create:
        sub.add_argument(
            "--nft-create",
            action="store_true",
            default=False,
            help="role for nft create",
        )

    sub.add_argument(
        "--nft-burn",
        action="store_true",
        default=False,
        help="role for nft burn",
    )
    sub.add_argument(
        "--nft-add-quantity",
        action="store_true",
        default=False,
        help="role for adding quantity",
    )
    sub.add_argument(
        "--esdt-transfer-role",
        action="store_true",
        default=False,
        help="role for esdt transfer",
    )
    sub.add_argument(
        "--nft-update",
        action="store_true",
        default=False,
        help="role for updating nft",
    )
    sub.add_argument(
        "--esdt-modify-royalties",
        action="store_true",
        default=False,
        help="role for modifying royalties",
    )
    sub.add_argument(
        "--esdt-set-new-uri",
        action="store_true",
        default=False,
        help="role for setting new uri",
    )
    sub.add_argument(
        "--esdt-modify-creator",
        action="store_true",
        default=False,
        help="role for modifying creator",
    )
    sub.add_argument(
        "--nft-recreate",
        action="store_true",
        default=False,
        help="role for recreating nft",
    )


def validate_token_args(args: Any, with_initial_supply: bool = False, with_num_decimals: bool = False):
    if with_initial_supply and args.initial_supply < 0:
        raise ValueError("Initial supply must be a non-negative integer")

    if with_num_decimals and not (0 <= args.num_decimals <= 18):
        raise ValueError("Number of decimals must be between 0 and 18")

    if not (3 <= len(args.token_name) <= 20) or not args.token_name.isalnum():
        raise ValueError("Token name must be 3-20 alphanumerical characters")

    if not (3 <= len(args.token_ticker) <= 10) or not args.token_ticker.isalnum() or not args.token_ticker.isupper():
        raise ValueError("Token ticker must be 3-10 UPPERCASE alphanumerical characters")


def _ensure_issue_args(args: Any, with_initial_supply: bool = False, with_num_decimals: bool = False):
    validate_broadcast_args(args)
    validate_chain_id_args(args)
    validate_token_args(args, with_initial_supply, with_num_decimals)


def issue_fungible(args: Any):
    _ensure_issue_args(args, with_initial_supply=True, with_num_decimals=True)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_issuing_fungible_token(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        initial_supply=args.initial_supply,
        num_decimals=args.num_decimals,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
        can_freeze=args.can_freeze,
        can_wipe=args.can_wipe,
        can_pause=args.can_pause,
        can_change_owner=args.can_change_owner,
        can_upgrade=args.can_upgrade,
        can_add_special_roles=args.can_add_special_roles,
    )

    cli_shared.send_or_simulate(transaction, args)


def issue_semi_fungible(args: Any):
    _ensure_issue_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_issuing_semi_fungible_token(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
        can_freeze=args.can_freeze,
        can_wipe=args.can_wipe,
        can_pause=args.can_pause,
        can_transfer_nft_create_role=args.can_transfer_nft_create_role,
        can_change_owner=args.can_change_owner,
        can_upgrade=args.can_upgrade,
        can_add_special_roles=args.can_add_special_roles,
    )

    cli_shared.send_or_simulate(transaction, args)


def issue_non_fungible(args: Any):
    _ensure_issue_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_issuing_non_fungible_token(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
        can_freeze=args.can_freeze,
        can_wipe=args.can_wipe,
        can_pause=args.can_pause,
        can_transfer_nft_create_role=args.can_transfer_nft_create_role,
        can_change_owner=args.can_change_owner,
        can_upgrade=args.can_upgrade,
        can_add_special_roles=args.can_add_special_roles,
    )

    cli_shared.send_or_simulate(transaction, args)


def register_meta_esdt(args: Any):
    _ensure_issue_args(args, with_num_decimals=True)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_registering_meta_esdt(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        decimals=args.num_decimals,
        can_freeze=args.can_freeze,
        can_wipe=args.can_wipe,
        can_pause=args.can_pause,
        can_transfer_nft_create_role=args.can_transfer_nft_create_role,
        can_change_owner=args.can_change_owner,
        can_upgrade=args.can_upgrade,
        can_add_special_roles=args.can_add_special_roles,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def register_and_set_all_roles(args: Any):
    _ensure_issue_args(args, with_num_decimals=True)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )
    [token_type] = [type for type in TokenType if args.token_type == type.value]

    transaction = controller.create_transaction_for_registering_and_set_all_roles(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        decimals=args.num_decimals,
        token_type=token_type,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def set_burn_role_globally(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_setting_burn_role_globally(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unset_burn_role_globally(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unsetting_burn_role_globally(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def set_special_role_on_fungible(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_setting_special_role_on_fungible(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        add_role_local_mint=args.local_mint,
        add_role_local_burn=args.local_burn,
        add_role_esdt_transfer_role=args.esdt_transfer_role,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unset_special_role_on_fungible(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unsetting_special_role_on_fungible(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        remove_role_local_mint=args.local_mint,
        remove_role_local_burn=args.local_burn,
        remove_role_esdt_transfer_role=args.esdt_transfer_role,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def set_special_role_on_semi_fungible(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_setting_special_role_on_semi_fungible(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        add_role_nft_create=args.nft_create,
        add_role_nft_burn=args.nft_burn,
        add_role_nft_add_quantity=args.nft_add_quantity,
        add_role_esdt_transfer_role=args.esdt_transfer_role,
        add_role_nft_update=args.nft_update,
        add_role_esdt_modify_royalties=args.esdt_modify_royalties,
        add_role_esdt_set_new_uri=args.esdt_set_new_uri,
        add_role_esdt_modify_creator=args.esdt_modify_creator,
        add_role_nft_recreate=args.nft_recreate,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unset_special_role_on_semi_fungible(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unsetting_special_role_on_semi_fungible(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        remove_role_nft_burn=args.nft_burn,
        remove_role_nft_add_quantity=args.nft_add_quantity,
        remove_role_esdt_transfer_role=args.esdt_transfer_role,
        remove_role_nft_update=args.nft_update,
        remove_role_esdt_modify_royalties=args.esdt_modify_royalties,
        remove_role_esdt_set_new_uri=args.esdt_set_new_uri,
        remove_role_esdt_modify_creator=args.esdt_modify_creator,
        remove_role_nft_recreate=args.nft_recreate,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def set_special_role_on_meta_esdt(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_setting_special_role_on_meta_esdt(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        add_role_nft_create=args.nft_create,
        add_role_nft_burn=args.nft_burn,
        add_role_nft_add_quantity=args.nft_add_quantity,
        add_role_esdt_transfer_role=args.esdt_transfer_role,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unset_special_role_on_meta_esdt(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unsetting_special_role_on_meta_esdt(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        remove_role_nft_burn=args.nft_burn,
        remove_role_nft_add_quantity=args.nft_add_quantity,
        remove_role_esdt_transfer_role=args.esdt_transfer_role,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def set_special_role_on_nft(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_setting_special_role_on_non_fungible(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        add_role_nft_create=args.nft_create,
        add_role_nft_burn=args.nft_burn,
        add_role_nft_update_attributes=args.nft_update_attributes,
        add_role_nft_add_uri=args.nft_add_uri,
        add_role_esdt_transfer_role=args.esdt_transfer_role,
        add_role_nft_update=args.nft_update,
        add_role_esdt_modify_royalties=args.esdt_modify_royalties,
        add_role_esdt_set_new_uri=args.esdt_set_new_uri,
        add_role_esdt_modify_creator=args.esdt_modify_creator,
        add_role_nft_recreate=args.nft_recreate,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unset_special_role_on_nft(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unsetting_special_role_on_non_fungible(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        remove_role_nft_burn=args.nft_burn,
        remove_role_nft_update_attributes=args.nft_update_attributes,
        remove_role_nft_add_uri=args.nft_add_uri,
        remove_role_esdt_transfer_role=args.esdt_transfer_role,
        remove_role_nft_update=args.nft_update,
        remove_role_esdt_modify_royalties=args.esdt_modify_royalties,
        remove_role_esdt_set_new_uri=args.esdt_set_new_uri,
        remove_role_esdt_modify_creator=args.esdt_modify_creator,
        remove_role_nft_recreate=args.nft_recreate,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def create_nft(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_creating_nft(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        initial_quantity=args.initial_quantity,
        name=args.name,
        royalties=args.royalties,
        hash=args.hash,
        attributes=bytes.fromhex(args.attributes),
        uris=args.uris,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def pause_token(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_pausing(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unpause_token(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unpausing(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def freeze_token(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_freezing(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unfreeze_token(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unfreezing(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def wipe_token(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_wiping(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def local_mint(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_local_minting(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        supply_to_mint=args.supply_to_mint,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def local_burn(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_local_burning(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        supply_to_burn=args.supply_to_burn,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def update_attributes(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_updating_attributes(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        attributes=bytes.fromhex(args.attributes),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def add_quantity(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_adding_quantity(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        quantity=args.quantity,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def burn_quantity(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_burning_quantity(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        quantity=args.quantity,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def modify_royalties(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_modifying_royalties(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        royalties=args.royalties,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def set_new_uris(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_setting_new_uris(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        uris=args.uris,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def modify_creator(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_modifying_creator(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def update_metadata(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_updating_metadata(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        new_token_name=args.token_name,
        new_royalties=args.royalties,
        new_hash=args.hash,
        new_attributes=bytes.fromhex(args.attributes),
        new_uris=args.uris,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def nft_metadata_recreate(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_recreating_metadata(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        new_token_name=args.token_name,
        new_royalties=args.royalties,
        new_hash=args.hash,
        new_attributes=bytes.fromhex(args.attributes),
        new_uris=args.uris,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def change_to_dynamic(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_changing_token_to_dynamic(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def update_token_id(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_updating_token_id(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def register_dynamic_token(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    [token_type] = [token_type for token_type in TokenType if token_type.value == args.token_type]
    transaction = controller.create_transaction_for_registering_dynamic_token(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        token_type=token_type,
        denominator=args.denominator,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def register_dynamic_and_set_all_roles(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    [token_type] = [token_type for token_type in TokenType if token_type.value == args.token_type]
    transaction = controller.create_transaction_for_registering_dynamic_and_setting_roles(
        sender=sender,
        nonce=sender.nonce,
        token_name=args.token_name,
        token_ticker=args.token_ticker,
        token_type=token_type,
        denominator=args.denominator,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def transfer_ownership(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_transferring_ownership(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        new_owner=Address.new_from_bech32(args.new_owner),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def freeze_single_nft(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_freezing_single_nft(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        user=Address.new_from_bech32(args.user),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def unfreeze_single_nft(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_unfreezing_single_nft(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        user=Address.new_from_bech32(args.user),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def change_sft_to_meta_esdt(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_changing_sft_to_meta_esdt(
        sender=sender,
        nonce=sender.nonce,
        collection_identifier=args.collection,
        decimals=args.decimals,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def transfer_nft_create_role(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_transferring_nft_create_role(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        user=Address.new_from_bech32(args.user),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def stop_nft_creation(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_stopping_nft_creation(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def wipe_single_nft(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_wiping_single_nft(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        user=Address.new_from_bech32(args.user),
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)


def add_uris(args: Any):
    validate_broadcast_args(args)
    validate_chain_id_args(args)

    sender = cli_shared.prepare_sender(args)
    guardian_and_relayer_data = cli_shared.get_guardian_and_relayer_data(
        sender=sender.address.to_bech32(),
        args=args,
    )
    chain_id = cli_shared.get_chain_id(args.proxy, args.chain)
    gas_estimator = cli_shared.initialize_gas_limit_estimator(args)
    controller = TokensManagementWrapper(
        config=TransactionsFactoryConfig(chain_id),
        gas_limit_estimator=gas_estimator,
    )

    transaction = controller.create_transaction_for_adding_uris(
        sender=sender,
        nonce=sender.nonce,
        token_identifier=args.token_identifier,
        token_nonce=args.token_nonce,
        uris=args.uris,
        gas_limit=args.gas_limit,
        gas_price=args.gas_price,
        version=args.version,
        options=args.options,
        guardian_and_relayer_data=guardian_and_relayer_data,
    )

    cli_shared.send_or_simulate(transaction, args)
