from erdpy.accounts import Account
from erdpy.transactions import Transaction
import logging
from pathlib import Path
import unittest


logging.basicConfig(level=logging.INFO)


class TransactionsTestCase(unittest.TestCase):
    def setUp(self):
        self.testdata = Path(__file__).parent.joinpath("testdata")
        self.alice = Account(pem_file=str(self.testdata.joinpath("keys", "alice.pem")))

    def test_serialize_transaction_payload(self):
        # With data field
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "42"
        transaction.sender = "alice"
        transaction.receiver = "bob"
        transaction.gasPrice = 43
        transaction.gasLimit = 44
        transaction.data = "foobar"
        transaction.chainID = "BoN"
        transaction.version = 1
        serialized = transaction.serialize().decode()
        self.assertEqual("""{"nonce":0,"value":"42","receiver":"bob","sender":"alice","gasPrice":43,"gasLimit":44,"data":"Zm9vYmFy","chainID":"BoN","version":1}""", serialized)

        # Without data field
        transaction.data = ""
        serialized = transaction.serialize().decode()
        self.assertEqual("""{"nonce":0,"value":"42","receiver":"bob","sender":"alice","gasPrice":43,"gasLimit":44,"chainID":"BoN","version":1}""", serialized)

        # With actual addresses
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        transaction.chainID = "BoN"
        transaction.version = 1
        serialized = transaction.serialize().decode()
        self.assertEqual("""{"nonce":0,"value":"0","receiver":"erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr","sender":"erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz","gasPrice":200000000000000,"gasLimit":500000000,"data":"Zm9v","chainID":"BoN","version":1}""", serialized)

    def test_serialize_transaction_as_inner(self):
        transaction = Transaction()
        transaction.nonce = 0
        transaction.value = "0"
        transaction.sender = "erd1l453hd0gt5gzdp7czpuall8ggt2dcv5zwmfdf3sd3lguxseux2fsmsgldz"
        transaction.receiver = "erd188nydpkagtpwvfklkl2tn0w6g40zdxkwfgwpjqc2a2m2n7ne9g8q2t22sr"
        transaction.gasPrice = 200000000000000
        transaction.gasLimit = 500000000
        transaction.data = "foo"
        transaction.chainID = "BoN"
        transaction.version = 1
        transaction.sign(self.alice)
        serialized = transaction.serialize_as_inner()

        self.assertEqual("relayedTx@7b226e6f6e6365223a302c2276616c7565223a302c227265636569766572223a224f655a47687431437775596d33376655756233615256346d6d73354b48426b4443757132716670354b67343d222c2273656e646572223a222f576b62746568644543614832424235332f7a6f517454634d6f4a323074544744592f5277304d384d704d3d222c226761735072696365223a3230303030303030303030303030302c226761734c696d6974223a3530303030303030302c2264617461223a225a6d3976222c22636861696e4944223a22516d394f222c2276657273696f6e223a312c227369676e6174757265223a2262516b49673975745968334a4f7a413036314e65785343515054397a6e57336d2f51732f746f544d43454741745a48752b56473670667a426571757a714e776d785476504d304b49652f6f5164534b345354514e43413d3d227d", serialized)
