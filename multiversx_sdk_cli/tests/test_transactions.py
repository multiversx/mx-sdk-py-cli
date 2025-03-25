from pathlib import Path

from multiversx_sdk import Account, Address

from multiversx_sdk_cli.guardian_relayer_data import GuardianRelayerData
from multiversx_sdk_cli.transactions import TransactionsController

testdata = Path(__file__).parent / "testdata"


class TestTransactionsController:
    controller = TransactionsController("D")
    alice = Account.new_from_pem(testdata / "alice.pem")

    def test_create_transaction_without_data_and_value(self):
        guardian_relayer_data = GuardianRelayerData()
        transaction = self.controller.create_transaction(
            sender=self.alice,
            receiver=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            native_amount=0,
            gas_limit=50000,
            gas_price=1000000000,
            nonce=7,
            version=2,
            options=0,
            guardian_and_relayer_data=guardian_relayer_data,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        assert transaction.value == 0
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 50000
        assert transaction.gas_price == 1000000000
        assert transaction.nonce == 7
        assert transaction.version == 2
        assert transaction.options == 0
        assert not transaction.data
        assert not transaction.guardian
        assert not transaction.relayer
        assert not transaction.guardian_signature
        assert not transaction.relayer_signature
        assert (
            transaction.signature.hex()
            == "ecf9e9f8d395741c0fbb61eaba74295448ba380dd00a228463e29a278d4e3c9219b2fa54133e32510837e03d7cc9f17738b99b701e148ce098b8340064a5f409"
        )

    def test_create_transfer_transaction(self):
        guardian_relayer_data = GuardianRelayerData()
        transaction = self.controller.create_transaction(
            sender=self.alice,
            receiver=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            native_amount=123456789,
            gas_limit=50000,
            gas_price=1000000000,
            nonce=7,
            version=2,
            options=0,
            guardian_and_relayer_data=guardian_relayer_data,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        assert transaction.value == 123456789
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 50000
        assert transaction.gas_price == 1000000000
        assert transaction.nonce == 7
        assert transaction.version == 2
        assert transaction.options == 0
        assert not transaction.data
        assert not transaction.guardian
        assert not transaction.relayer
        assert not transaction.guardian_signature
        assert not transaction.relayer_signature
        assert (
            transaction.signature.hex()
            == "fe0ff59c06c453eed882db562f98c0684a32763a79580a33e269af6edbebc150007118b298f34d17c54b90d55cee76ed1e5254832db8acb2c34ef12f14b8b40d"
        )

    def test_create_transaction_with_data(self):
        guardian_relayer_data = GuardianRelayerData()
        transaction = self.controller.create_transaction(
            sender=self.alice,
            receiver=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            native_amount=0,
            gas_limit=50000,
            gas_price=1000000000,
            nonce=7,
            version=2,
            options=0,
            data="testdata",
            guardian_and_relayer_data=guardian_relayer_data,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        assert transaction.value == 0
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 50000
        assert transaction.gas_price == 1000000000
        assert transaction.nonce == 7
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.data == b"testdata"
        assert not transaction.guardian
        assert not transaction.relayer
        assert not transaction.guardian_signature
        assert not transaction.relayer_signature
        assert (
            transaction.signature.hex()
            == "74bb3bd0c4e87ed64a01456f888236a74b5672cf194a33a2225d868f5f43d65e9149f3145b9431075828ff842f70b977b778895925f37037db979e71563c540c"
        )

    def test_create_guarded_transaction(self):
        guardian_relayer_data = GuardianRelayerData(
            guardian=Account.new_from_pem(testdata / "testUser2.pem"),
            guardian_address=Address.new_from_bech32("erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"),
        )

        transaction = self.controller.create_transaction(
            sender=self.alice,
            receiver=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            native_amount=0,
            gas_limit=200000,
            gas_price=1000000000,
            nonce=7,
            version=2,
            options=0,
            data="testdata",
            guardian_and_relayer_data=guardian_relayer_data,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        assert transaction.value == 0
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 200000
        assert transaction.gas_price == 1000000000
        assert transaction.nonce == 7
        assert transaction.version == 2
        assert transaction.options == 2
        assert transaction.data == b"testdata"
        assert not transaction.relayer
        assert not transaction.relayer_signature
        assert (
            transaction.guardian
            and transaction.guardian.to_bech32() == "erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"
        )
        assert (
            transaction.guardian_signature.hex()
            == "c8b186f85c6e79e157aac48ec55d3f915abbc396e257d30aff193135485395c4b026e7921853366a16bcbbb8dbe5f6cf98a917a8ca11ccdc3f29f5a5a7d7af0c"
        )
        assert (
            transaction.signature.hex()
            == "8e9338de8f1d66bc6cd2f8e42cb62b5456d82ba66fdf9b8ace750ab3fa697f348084b41996b19d172b627b0b0a312ef76d29191d627b4d9959a3bf17409f780b"
        )

    def test_create_relayed_transaction(self):
        guardian_relayer_data = GuardianRelayerData(
            relayer=Account.new_from_pem(testdata / "testUser2.pem"),
            relayer_address=Address.new_from_bech32("erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"),
        )

        transaction = self.controller.create_transaction(
            sender=self.alice,
            receiver=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            native_amount=0,
            gas_limit=200000,
            gas_price=1000000000,
            nonce=7,
            version=2,
            options=0,
            data="testdata",
            guardian_and_relayer_data=guardian_relayer_data,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        assert transaction.value == 0
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 200000
        assert transaction.gas_price == 1000000000
        assert transaction.nonce == 7
        assert transaction.version == 2
        assert transaction.options == 0
        assert transaction.data == b"testdata"
        assert not transaction.guardian
        assert not transaction.guardian_signature
        assert (
            transaction.relayer
            and transaction.relayer.to_bech32() == "erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"
        )
        assert (
            transaction.relayer_signature.hex()
            == "385fb15816d52118b97a20451c2b225a81ce9be130ad13987453cab36e858f79af0473effc845bef1537ad9f878001e6fcdfeefa36c46c5e8bb6aab83c9b2a0b"
        )
        assert (
            transaction.signature.hex()
            == "89c2de2939bdd4ed2bdaf8f859f9020b6f7510b3a7298daaebdef53ce1de588181e1c27f8933745927e610ebfe6c41a8875e2b052a48fa22464903f3821b830e"
        )

    def test_create_guarded_relayed_transaction(self):
        guardian_relayer_data = GuardianRelayerData(
            guardian=Account.new_from_pem(testdata / "testUser.pem"),
            guardian_address=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            relayer=Account.new_from_pem(testdata / "testUser2.pem"),
            relayer_address=Address.new_from_bech32("erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"),
        )

        transaction = self.controller.create_transaction(
            sender=self.alice,
            receiver=Address.new_from_bech32("erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"),
            native_amount=0,
            gas_limit=200000,
            gas_price=1000000000,
            nonce=7,
            version=2,
            options=0,
            data="testdata",
            guardian_and_relayer_data=guardian_relayer_data,
        )

        assert transaction.sender == self.alice.address
        assert transaction.receiver.to_bech32() == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        assert transaction.value == 0
        assert transaction.chain_id == "D"
        assert transaction.gas_limit == 200000
        assert transaction.gas_price == 1000000000
        assert transaction.nonce == 7
        assert transaction.version == 2
        assert transaction.options == 2
        assert transaction.data == b"testdata"

        assert (
            transaction.guardian
            and transaction.guardian.to_bech32() == "erd1cqqxak4wun7508e0yj9ng843r6hv4mzd0hhpjpsejkpn9wa9yq8sj7u2u5"
        )
        assert (
            transaction.guardian_signature.hex()
            == "06bc457b510cae975e1cc6ab863ed765aadbd948ad23cbd204d66a2b92bee683922d308148af47e28d186bceba13474c79f16b26803c65c908f1d4a2e2ac6a0e"
        )

        assert (
            transaction.relayer
            and transaction.relayer.to_bech32() == "erd1ssmsc9022udc8pdw7wk3hxw74jr900xg28vwpz3z60gep66fasasl2nkm4"
        )
        assert (
            transaction.relayer_signature.hex()
            == "86e2460a6045ac3142c23f06c3b31fc132f38227faa25ffc8f7e9ce32c4542f6ed37d740d3c83c4454f2390befd223b968d4767c28991f574689b36faa978209"
        )

        assert (
            transaction.signature.hex()
            == "b0bce606f2cfd52d6641f8e96aa29dcfd334af4707d88f81dba01dac67e72a99d7143dccadc8d120b387c4eaac84dc01865e57488a2162480a0f15acf50b6306"
        )
