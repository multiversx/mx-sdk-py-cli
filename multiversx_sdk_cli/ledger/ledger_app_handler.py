from typing import List

from ledgercomm import Transport

from multiversx_sdk_cli.errors import LedgerError
from multiversx_sdk_cli.ledger.config import (LedgerAppConfiguration,
                                              load_ledger_config_from_response)

SIGN_USING_HASH_VERSION = "1.0.11"
CONNECTION_ERROR_MSG = "check if device is plugged in, unlocked and on MultiversX app"

# Also see: https://github.com/multiversx/mx-sdk-js-hw-provider/blob/main/src/ledgerApp.ts
CLA = 0xed
SIGN_RAW_TX_INS = 0x04
SIGN_HASH_TX_INS = 0x07
SIGN_MESSAGE_INS = 0x06
PROVIDE_ESDT_INFO_INS = 0x08
GET_ADDRESS_AUTH_TOKEN_INS = 0x09


class Apdu:
    cla: int
    ins: int
    p1: int
    p2: int
    data: bytes


class LedgerApp:
    def __init__(self):
        try:
            self.transport = Transport(interface="hid", debug=False)  # Nano S/X using HID interface
        except:
            raise LedgerError(CONNECTION_ERROR_MSG)

    def close(self):
        self.transport.close()

    def set_address(self, account_index: int = 0, address_index: int = 0):
        data = account_index.to_bytes(4, byteorder='big') + address_index.to_bytes(4, byteorder='big')
        self.transport.send(cla=0xed, ins=0x05, p1=0x00, p2=0x00, cdata=data)
        sw, _ = self.transport.recv()
        err = get_error(sw)
        if err != '':
            raise LedgerError(err)

    def get_address(self, account_index: int = 0, address_index: int = 0) -> str:
        data = account_index.to_bytes(4, byteorder='big') + address_index.to_bytes(4, byteorder='big')

        self.transport.send(cla=0xed, ins=0x03, p1=0x00, p2=0x00, cdata=data)
        sw, response = self.transport.recv()
        assert isinstance(response, bytes)

        err = get_error(sw)
        if err != '':
            raise LedgerError(CONNECTION_ERROR_MSG + " (" + err + ")")

        response_body = response[1:]
        address = response_body.decode("utf-8")
        return address

    def get_app_configuration(self) -> LedgerAppConfiguration:
        self.transport.send(cla=0xed, ins=0x02, p1=0x00, p2=0x00, cdata=b"")
        sw, response = self.transport.recv()
        err = get_error(sw)
        if err != '':
            raise LedgerError(CONNECTION_ERROR_MSG + " (" + err + ")")
        return load_ledger_config_from_response(response)

    def get_version(self) -> str:
        config = self.get_app_configuration()
        return config.version

    def sign_transaction(self, tx_bytes: bytes, should_use_hash_signing: bool) -> str:
        ins_signing_method = SIGN_RAW_TX_INS
        if should_use_hash_signing:
            ins_signing_method = SIGN_HASH_TX_INS

        return self._do_sign(tx_bytes, ins_signing_method)

    def sign_message(self, message_bytes: bytes) -> str:
        return self._do_sign(message_bytes, SIGN_MESSAGE_INS)

    def _do_sign(self, data: bytes, ins_signing_method: int) -> str:
        total_size = len(data)
        max_chunk_size = 150

        apdus: List[Apdu] = []

        offset = 0
        while offset != total_size:
            is_first = offset == 0

            apdu = Apdu()

            if is_first:
                apdu.p1 = 0x00
            else:
                apdu.p1 = 0x80

            has_more = offset + max_chunk_size < total_size
            chunk_size = total_size - offset
            if has_more:
                chunk_size = max_chunk_size

            apdu.ins = ins_signing_method
            apdu.p2 = 0x00
            apdu.cla = CLA
            apdu.data = data[offset:offset + chunk_size]

            apdus.append(apdu)

            offset += chunk_size

        return self.get_signature_from_apdus(apdus)

    def get_signature_from_apdus(self, apdus: List[Apdu]) -> str:
        sw: int
        response: bytes
        for apdu in apdus:
            self.transport.send(
                cla=apdu.cla,
                ins=apdu.ins,
                p1=apdu.p1,
                p2=apdu.p2,
                cdata=apdu.data)
            sw, response = self.transport.recv()

        assert isinstance(response, bytes)
        if len(response) != 65 or response[0] != 64 or get_error(sw) != '':
            err_message = "signature failed"
            err = get_error(sw)
            if err != '':
                err_message += ': ' + err
            raise LedgerError(err_message)

        response_body = response[1:]
        signature = response_body.hex()
        return signature


def get_error(code: int):
    switcher = {
        0x9000: '',
        0x6985: 'user denied',
        0x6D00: 'unknown instruction',
        0x6E00: 'wrong cla',
        0x6E10: 'signature failed',
        0x6E01: 'invalid arguments',
        0x6E02: 'invalid message',
        0x6E03: 'invalid p1',
        0x6E04: 'message too long',
        0x6E05: 'receiver too long',
        0x6E06: 'amount too long',
        0x6E07: 'contract data disabled',
        0x6E08: 'message incomplete',
        0x6E09: 'wrong tx version',
        0x6E0A: 'nonce too long',
        0x6E0B: 'invalid amount',
        0x6E0C: 'invalid fee',
        0x6E0D: 'pretty failed',
        0x6E0E: 'data too long',
        0x6E0F: 'wrong tx options',
        0x6E11: 'regular signing is deprecated',
    }

    return switcher.get(code, "unknown error code: " + hex(code))
