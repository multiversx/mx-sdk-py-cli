import _thread
import time
import unittest

from erdpy.config import DEFAULT_GAS_PRICE
from erdpy.dispatcher.transactions.queue import TransactionQueue


def _create_mock_args():
    args = TestArgs()
    args.data = "data1"
    args.receiver = "erd12cl2dgtjws8vt9yf4v9869vryt0juv3eq8hzzq6mlm9ck935vs3q9lfnqe"
    args.gas_price = DEFAULT_GAS_PRICE
    args.gas_limit = 50000
    args.value = "100"
    args.nonce = 0
    return args


def write_in_queue():
    args = _create_mock_args()
    queue = TransactionQueue()

    idx = 0
    while idx < 5000:
        args.value = str(idx)
        queue.enqueue_transaction(args)
        time.sleep(0.001)
        idx += 1


class DispatcherTestCase(unittest.TestCase):
    # this a manual test needs proxy and pem file with funds
    @unittest.skip
    def test_multi_thread(self):
        _thread.start_new_thread(write_in_queue, ())

        args = TestArgs()
        args.proxy = "http://localhost:7950"
        args.pem = "./../../../file.pem"
        args.interval = 2
        queue = TransactionQueue()
        queue.dispatch_transactions_continuously(args)

        self.assertFalse(False)

    @unittest.skip
    def test_enqueue_tx(self):
        write_in_queue()
        self.assertFalse(False)

    @unittest.skip
    def test_dispatcher_txs(self):
        args = TestArgs()
        args.proxy = "http://localhost:7950"
        args.pem = "./../../../file.pem"
        queue = TransactionQueue()
        queue.dispatch_transactions(args)
        self.assertFalse(False)

    @unittest.skip
    def test_clean(self):
        queue = TransactionQueue()
        queue.clean_transactions_queue()
        self.assertFalse(False)


class TestArgs(object):
    pass
