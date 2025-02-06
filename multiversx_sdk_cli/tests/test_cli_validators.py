import json
from pathlib import Path
from typing import Any

from multiversx_sdk_cli.cli import main

testdata_path = Path(__file__).parent / "testdata"
testdata_out = Path(__file__).parent / "testdata-out"

alice_pem = testdata_path / "alice.pem"
reward_address = "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
bls_key = "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"

relayer = testdata_path / "testUser.pem"
guardian = testdata_path / "testUser2.pem"


def test_stake(capsys: Any):
    validators_json = testdata_path / "validators_file.json"

    return_code = main(
        [
            "validator",
            "stake",
            "--pem",
            str(alice_pem),
            "--value",
            "2500000000000000000000",
            "--validators-file",
            str(validators_json),
            "--reward-address",
            reward_address,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=0",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "2500000000000000000000"
    assert tx["nonce"] == 0
    assert tx["gasLimit"] == 11029500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "e9dd1159bc55bde84872f0595c9e24b0b210deb8cb02a1df7d7b0e1277436d2043437ffeaff540e11200c00417cf5ce396b3154f968ad62ab4359fb05a493b0d"
    )
    assert (
        data
        == "stake@02@f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d@1865870f7f69162a2dfefd33fe232a9ca984c6f22d1ee3f6a5b34a8eb8c9f7319001f29d5a2eed85c1500aca19fa4189@1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d@12b309791213aac8ad9f34f0d912261e30f9ab060859e4d515e020a98b91d82a7cd334e4b504bb93d6b75347cccd6318@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
    )


def test_top_up(capsys: Any):
    return_code = main(
        [
            "validator",
            "stake",
            "--pem",
            str(alice_pem),
            "--value",
            "2500000000000000000000",
            "--top-up",
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=0",
            "--reward-address",
            "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "2500000000000000000000"
    assert tx["nonce"] == 0
    assert tx["gasLimit"] == 5057500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "ca4ebd1b9c92b0479351e9f84b0394ce15f529f4a5c056ab2dd37b923d7af81cbb7bfc8fbbea571843a797e3382795c0419f69ab357acbd9611899d39e449107"
    )
    assert data == "stake"


def test_stake_with_relayer_and_guardian(capsys: Any):
    validators_json = testdata_path / "validators_file.json"

    return_code = main(
        [
            "validator",
            "stake",
            "--pem",
            str(alice_pem),
            "--value",
            "2500000000000000000000",
            "--validators-file",
            str(validators_json),
            "--reward-address",
            reward_address,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=0",
            "--options=2",
            "--relayer",
            "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5",
            "--guardian",
            "erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4",
            "--guardian-pem",
            str(guardian),
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "2500000000000000000000"
    assert tx["nonce"] == 0
    assert tx["gasLimit"] == 11029500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 2
    assert tx["guardian"] == "erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"
    assert tx["relayer"] == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
    assert (
        tx["signature"]
        == "9ecca226c3e5913906a5f22971a0d84bb7a8c652e309ffab4073dea8bbd88caccc2ad9e33b6929f16acdedb676ad574ad66d520abd5b398469fa0cff3fc7ca03"
    )
    assert (
        tx["guardianSignature"]
        == "12c1ee05d34282555d85f7786dc0e7ffbce960de88fb75ba81a237bd1f2cc175f50ee42e60b2857bf2cd49d02de12a4017f1c95f14910fcc27bc7cb16b41ce04"
    )
    assert (
        data
        == "stake@02@f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d@1865870f7f69162a2dfefd33fe232a9ca984c6f22d1ee3f6a5b34a8eb8c9f7319001f29d5a2eed85c1500aca19fa4189@1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d@12b309791213aac8ad9f34f0d912261e30f9ab060859e4d515e020a98b91d82a7cd334e4b504bb93d6b75347cccd6318@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"
    )


def test_stake_top_up(capsys: Any):
    return_code = main(
        [
            "validator",
            "stake",
            "--top-up",
            "--pem",
            str(alice_pem),
            "--value",
            "2711000000000000000000",
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "2711000000000000000000"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5057500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "3af38033e7661311e2e180b29930271ad54c05716e13bb33bafdb89e48250db525c056a51a25faf8e5bba31f6ddc03ed48f9e0e79b5f3da5ccc9f0b0a9a83207"
    )
    assert data == "stake"


def test_unstake(capsys: Any):
    return_code = main(
        [
            "validator",
            "unstake",
            "--pem",
            str(alice_pem),
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5350000
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "b387f3255670f17dbc4dd84bbed1f70631d2528f8f8ece7fb5c0fcc29a8b0b142583fe216c9de0086ebb69f9a50fc087ac4e5570fa2f61694df3b2cdb9389008"
    )
    assert (
        data
        == "unStake@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )


def test_unbond(capsys: Any):
    return_code = main(
        [
            "validator",
            "unbond",
            "--pem",
            str(alice_pem),
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5348500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "65c01d7c0ac26169d74d56612d1eab3a00c82b2f57af6b4aebbf39aa75e0f5e973d7daabb00bfad14d2f8bf63936ca9d69ef8fb76b8ac9c8ad0d2f808936930e"
    )
    assert (
        data
        == "unBond@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )


def test_unjail(capsys: Any):
    return_code = main(
        [
            "validator",
            "unjail",
            "--pem",
            str(alice_pem),
            "--value",
            "2500000000000000000000",
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "2500000000000000000000"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5348500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "5e682ba1e16b62971d3c6e6943ec954eb29fc31d8794d21afdd9e2c4ea5ba209a59cba8bd39c2a6ab9f80f066d558679e5b22bfca561caedbfa6a7297ad97d00"
    )
    assert (
        data
        == "unJail@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )


def test_change_reward_address(capsys: Any):
    return_code = main(
        [
            "validator",
            "change-reward-address",
            "--pem",
            str(alice_pem),
            "--reward-address",
            reward_address,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5176000
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "565e64ea28d48150e3798e20c0a0a0294374992ed05e5153e93339b3f86acdd25db308b474dd8315a544d6e375ed9e07b01c3475bdc7986fde79eae26bd5a40c"
    )
    assert data == "changeRewardAddress@b2a11555ce521e4944e09ab17549d85b487dcd26c84b5017a39e31a3670889ba"


def test_claim(capsys: Any):
    return_code = main(
        [
            "validator",
            "claim",
            "--pem",
            str(alice_pem),
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5057500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "be19a2c0bf5ce1da5f72a7451bff57725161bb67a8b85e397d44570585e6b7ff40858b0d30fd9a12f06c70655b1c417389f25059e0a95dc76e488185cea68208"
    )
    assert data == "claim"


def test_unstake_nodes(capsys: Any):
    return_code = main(
        [
            "validator",
            "unstake-nodes",
            "--pem",
            str(alice_pem),
            "--nodes-public-key",
            bls_key,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5357500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "983b3127490949bc29e722a40a87871e88a6eb085fffb4d2801b2a79b39ff0aa395a39dc03367edb5f3858ed7ad9bea7b0c141110717cb639c45010055254606"
    )
    assert (
        data
        == "unStakeNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )


def test_unstake_tokens(capsys: Any):
    return_code = main(
        [
            "validator",
            "unstake-tokens",
            "--pem",
            str(alice_pem),
            "--unstake-value",
            "11000000000000000000",
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5095000
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "ed8e401e875d70bc3a62bf966fc8a9ecda2d49a851fe216f265176be5ab43040a85df55798dc828c928079573e2aa8dc52627e87c92824d8c91fdc3f3d195e0a"
    )
    assert data == "unStakeTokens@98a7d9b8314c0000"


def test_unbond_nodes(capsys: Any):
    return_code = main(
        [
            "validator",
            "unbond-nodes",
            "--pem",
            str(alice_pem),
            "--nodes-public-keys",
            bls_key,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5356000
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "ee261c7e7f1dc7822b31c609c570ba1b1da3e39ea68e231f2aea30ca9f70e0f61679f81739f22eee338fa9b8c14d498ca8892cde118d53b08f1440fe3737eb02"
    )
    assert (
        data
        == "unBondNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )


def test_unbond_tokens(capsys: Any):
    return_code = main(
        [
            "validator",
            "unbond-tokens",
            "--pem",
            str(alice_pem),
            "--unbond-value",
            "20000000000000000000",
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5096500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "a7c96028a97d035c0068b9c2a4bbc4ee3b9613d81dfa4c388fd8a90e66f4e200e715e87a760c0a7d456f3b3a4dc225f760084477cb15ac690c9e1cb7c006f70d"
    )
    assert data == "unBondTokens@01158e460913d00000"


def test_clean_registration_data(capsys: Any):
    return_code = main(
        [
            "validator",
            "clean-registered-data",
            "--pem",
            str(alice_pem),
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5078500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "005c35ccf2bbffbc753c8971aba1edffb43dbad1db62a88a26d295445937bb7f84dfd26e31329f8622ec9b53c5be4a39f1dd8ab83189f2cd5211c1c8541d7b00"
    )
    assert data == "cleanRegisteredData"


def test_re_stake_unstaked_nodes(capsys: Any):
    return_code = main(
        [
            "validator",
            "restake-unstaked-nodes",
            "--pem",
            str(alice_pem),
            "--nodes-public-keys",
            bls_key,
            "--chain",
            "localnet",
            "--estimate-gas",
            "--nonce=7",
        ]
    )
    assert return_code == 0

    output = get_output(capsys)
    tx = output["emittedTransaction"]
    data = output["emittedTransactionData"]

    assert tx["sender"] == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert tx["receiver"] == "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
    assert tx["value"] == "0"
    assert tx["nonce"] == 7
    assert tx["gasLimit"] == 5369500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "5f2196b81d9a72df401655becfc31e4167d89e76235f52abf506f9d9b10375b8b699339693b3f2d12552366e38ec2722a2ed50490a2beeaee0ae819d08f1ea0e"
    )
    assert (
        data
        == "reStakeUnStakedNodes@e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )


def get_output(capsys: Any):
    tx = _read_stdout(capsys)
    return json.loads(tx)


def _read_stdout(capsys: Any) -> str:
    return capsys.readouterr().out.strip()
