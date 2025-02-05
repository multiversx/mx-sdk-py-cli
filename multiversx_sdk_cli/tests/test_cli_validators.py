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
        == "66c0a8334b4e9d2bcc87214762c2957c8b190c91db27f6bac43a9c309f5310a752d293796938c3c131e9e96836e00e62fabec64a1205b05822f634415f675909"
    )
    assert (
        data
        == "stake@02@F8910E47CF9464777C912E6390758BB39715FFFCB861B184017920E4A807B42553F2F21E7F3914B81BCF58B66A72AB16D97013AE1CFF807CEFC977EF8CBF116258534B9E46D19528042D16EF8374404A89B184E0A4EE18C77C49E454D04EAE8D@1865870F7F69162A2DFEFD33FE232A9CA984C6F22D1EE3F6A5B34A8EB8C9F7319001F29D5A2EED85C1500ACA19FA4189@1B4E60E6D100CDF234D3427494DAC55FBAC49856CADC86BCB13A01B9BB05A0D9143E86C186C948E7AE9E52427C9523102EFE9019A2A9C06DB02993F2E3E6756576AE5A3EC7C235D548BC79DE1A6990E1120AE435CB48F7FC436C9F9098B92A0D@12B309791213AAC8AD9F34F0D912261E30F9AB060859E4D515E020A98B91D82A7CD334E4B504BB93D6B75347CCCD6318@B2A11555CE521E4944E09AB17549D85B487DCD26C84B5017A39E31A3670889BA"
    )


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
        == "01bcfddf60d36c6f1fa6449640f3b4ed1755003b1c128b4d4b6e0a74f2c9edbee0e94a8f1058b9388cdbd97e7bd8fada3fc64bc7ed99f4239694f996b85f0108"
    )
    assert (
        tx["guardianSignature"]
        == "dfbd3d7ed19d607085779fef911e77ca63cfddb159aa3338bad9209064d50f90a24aeeac8082ec3b424afb3054189aab11467c016bb0ba945a43e191a9073306"
    )
    assert (
        data
        == "stake@02@F8910E47CF9464777C912E6390758BB39715FFFCB861B184017920E4A807B42553F2F21E7F3914B81BCF58B66A72AB16D97013AE1CFF807CEFC977EF8CBF116258534B9E46D19528042D16EF8374404A89B184E0A4EE18C77C49E454D04EAE8D@1865870F7F69162A2DFEFD33FE232A9CA984C6F22D1EE3F6A5B34A8EB8C9F7319001F29D5A2EED85C1500ACA19FA4189@1B4E60E6D100CDF234D3427494DAC55FBAC49856CADC86BCB13A01B9BB05A0D9143E86C186C948E7AE9E52427C9523102EFE9019A2A9C06DB02993F2E3E6756576AE5A3EC7C235D548BC79DE1A6990E1120AE435CB48F7FC436C9F9098B92A0D@12B309791213AAC8AD9F34F0D912261E30F9AB060859E4D515E020A98B91D82A7CD334E4B504BB93D6B75347CCCD6318@B2A11555CE521E4944E09AB17549D85B487DCD26C84B5017A39E31A3670889BA"
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
    assert tx["gasLimit"] == 5101000
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "c9506332641dc0a45a71b4f8e256f3761151173de73b0e2fbe627afa487911c6905911c74a45e04c947938eb30e1bc785cdae83cbbd35f248c4519b7a3e6800f"
    )
    assert data == "unStakeTokens@000098a7d9b8314c0000"


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
    assert tx["gasLimit"] == 5099500
    assert tx["chainID"] == "localnet"
    assert tx["version"] == 2
    assert tx["options"] == 0
    assert (
        tx["signature"]
        == "6eadd1d09700ba8fa8aedf01dcb6b44cb2551b59d65c2ab1ff8cac6bb0052a40a796b9ccb9d92439d6fdbd8536c7de5c5a28312ffef77ac9c1353f8236355206"
    )
    assert data == "unBondTokens@0001158e460913d00000"


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
