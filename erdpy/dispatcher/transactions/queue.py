import json
import logging
import os
import time
from collections import OrderedDict
from os import path

from erdpy import utils
from erdpy.accounts import Account
from erdpy.proxy.core import ElrondProxy
from erdpy.transactions import BunchOfTransactions
from erdpy.workstation import get_tools_folder

logger = logging.getLogger("queue")


def _prepare_tx(args):
    ordered_fields = OrderedDict()
    ordered_fields["nonce"] = 0
    ordered_fields["value"] = int(args.value)
    ordered_fields["receiver"] = args.receiver
    ordered_fields["gasPrice"] = int(args.gas_price)
    ordered_fields["gasLimit"] = int(args.gas_limit)
    ordered_fields["data"] = args.data
    ordered_fields["chain"] = args.chain
    ordered_fields["version"] = args.version

    return ordered_fields


def _wait_to_execute_txs(proxy, owner, expected_nonce):
    new_nonce = 0
    old_time = time.time()
    timeout = False
    while new_nonce < expected_nonce and not timeout:
        owner.sync_nonce(proxy)
        new_nonce = owner.nonce
        # timeout if passed a minute
        timeout = time.time() - old_time > 59
    if timeout:
        logger.error("Not all transactions were executed")
    else:
        logger.info(f"Transactions were executed")


class TransactionQueue:
    _TXS_FILE_NAME = "txs.json"
    _TXS_FIELD_NAME = "transactions"
    _TXS_INFO_FILE_NAME = "txs_info.txt"

    def __init__(self):
        tools_folder = get_tools_folder()

        txs_file_dir = path.join(tools_folder, "transactions")
        # create transactions directory if not exits
        if not os.path.exists(txs_file_dir):
            os.mkdir(txs_file_dir)

        self.txs_file_path = path.join(txs_file_dir, self._TXS_FILE_NAME)
        if not os.path.exists(self.txs_file_path):
            # create transactions file if not exits
            utils.write_file(self.txs_file_path, '{"' + self._TXS_FIELD_NAME + '":[]}')

        self.txs_info_file_path = path.join(txs_file_dir, self._TXS_INFO_FILE_NAME)
        if not os.path.exists(self.txs_info_file_path):
            utils.write_file(self.txs_info_file_path, f"index:{0}")

    def enqueue_transaction(self, args):
        prepared = _prepare_tx(args)
        data = self._read_json_file()
        temp_data = data[self._TXS_FIELD_NAME]
        temp_data.append(prepared)
        self._write_json_file(data)

    def _read_json_file(self):
        with open(self.txs_file_path, "r") as json_file:
            try:
                data = json.load(json_file)
            except Exception:
                logger.error("Cannot read transactions file")
                return {self._TXS_FIELD_NAME: []}
            return data

    def _write_json_file(self, data):
        with open(self.txs_file_path, "w") as json_file:
            json.dump(data, json_file, indent=1)

    def _remove_all_transactions(self):
        os.remove(self.txs_file_path)

    def _read_index(self):
        info = utils.read_file(self.txs_info_file_path)
        info_slit = info.split(":")
        return int(info_slit[1])

    def clean_transactions_queue(self):
        os.remove(self.txs_info_file_path)
        os.remove(self.txs_file_path)

    def dispatch_transactions_continuously(self, args):
        while True:
            logger.info("dispatch_transactions_continuously()")
            self.dispatch_transactions(args)
            time.sleep(int(args.interval))

    def dispatch_transactions(self, args):
        data = self._read_json_file()
        txs = data[self._TXS_FIELD_NAME]
        txs_index = self._read_index()

        total_txs = len(txs) - txs_index
        if total_txs == 0 or len(txs) == 0:
            logger.info("No transactions to dispatch")
            return

        proxy = ElrondProxy(args.proxy)
        # Need to sync nonce
        if args.pem:
            owner = Account(pem_file=args.pem)
        elif args.keyfile and args.passfile:
            owner = Account(key_file=args.keyfile, pass_file=args.passfile)

        owner.sync_nonce(proxy)
        nonce = owner.nonce
        old_nonce = nonce

        print(nonce)
        bunch = BunchOfTransactions()
        idx = txs_index
        while idx < len(txs):
            tx = txs[idx]
            # TODO CHECK IF BUNCH OF TRANSACTION generate transactions with chain id and version
            bunch.add(
                owner,
                tx.get("receiver"),
                nonce,
                tx.get("value"),
                tx.get("data"),
                tx.get("gasPrice"),
                tx.get("gasLimit")
            )
            # increment nonce
            nonce += 1
            idx += 1

        logger.info(f"Sending {total_txs} transactions")
        try:
            num_sent, hashes = bunch.send(proxy)
        except Exception:
            logger.error("No valid transactions to send")
            num_sent = 0
            hashes = []

        logger.info(f"{num_sent} transactions were accepted by observers")
        for key in hashes:
            print(f"tx {txs_index+int(key)}: hash => {hashes[key]}")

        utils.write_file(self.txs_info_file_path, f"index:{len(txs)}")
        # wait until transactions are executed
        _wait_to_execute_txs(proxy, owner, old_nonce + num_sent)
