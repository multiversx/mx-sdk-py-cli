from erdpy import errors, config
from erdpy.transactions import PlainTransaction, TransactionPayloadToSign, PreparedTransaction
from erdpy.wallet import signing


class SmartContract:
    def __init__(self, address=None, bytecode=None):
        self.address = address
        self.bytecode = bytecode

    def prepare_deploy_transaction(self, owner, arguments, gas_price, gas_limit):
        arguments = arguments or []
        gas_price = int(gas_price or config.DEFAULT_GASPRICE)
        gas_limit = int(gas_limit or config.DEFAULT_GASLIMIT)

        plain = PlainTransaction()
        plain.nonce = owner.nonce
        plain.value = "0"
        plain.sender = owner.address
        plain.receiver = "0" * 64
        plain.gasPrice = gas_price
        plain.gasLimit = gas_limit
        plain.data = self.prepare_deploy_transaction_data(arguments)

        payload = TransactionPayloadToSign(plain)
        signature = signing.sign_transaction(payload, owner.pem_file)
        prepared = PreparedTransaction(plain, signature)
        return prepared

    def prepare_deploy_transaction_data(self, arguments):
        tx_data = self.bytecode

        for arg in arguments:
            tx_data += f"@{_prepare_argument(arg)}"

        return tx_data


def _prepare_argument(argument):
    hex_prefix = "0X"
    as_string = str(argument).upper()

    if as_string.startswith(hex_prefix):
        return as_string[len(hex_prefix):]

    if not as_string.isnumeric():
        raise errors.UnknownArgumentFormat(as_string)

    as_number = int(as_string)
    as_hexstring = hex(as_number)[len(hex_prefix):]
    if len(as_hexstring) % 2 == 1:
        as_hexstring = "0" + as_hexstring

    return as_hexstring


def compute_contract_address(owner, nonce):
    """
    Implement as follows (Go):

    func (bh *BlockChainHookImpl) NewAddress(creatorAddress []byte, creatorNonce uint64, vmType []byte) ([]byte, error) {
        addressLength := bh.addrConv.AddressLen()
        if len(creatorAddress) != addressLength {
            return nil, ErrAddressLengthNotCorrect
        }

        if len(vmType) != core.VMTypeLen {
            return nil, ErrVMTypeLengthIsNotCorrect
        }

        base := hashFromAddressAndNonce(creatorAddress, creatorNonce)
        prefixMask := createPrefixMask(vmType)
        suffixMask := createSuffixMask(creatorAddress)

        copy(base[:core.NumInitCharactersForScAddress], prefixMask)
        copy(base[len(base)-core.ShardIdentiferLen:], suffixMask)

        return base, nil
    }

    func hashFromAddressAndNonce(creatorAddress []byte, creatorNonce uint64) []byte {
        buffNonce := make([]byte, 8)
        binary.LittleEndian.PutUint64(buffNonce, creatorNonce)
        adrAndNonce := append(creatorAddress, buffNonce...)
        scAddress := keccak.Keccak{}.Compute(string(adrAndNonce))

        return scAddress
    }

    func createPrefixMask(vmType []byte) []byte {
        prefixMask := make([]byte, core.NumInitCharactersForScAddress-core.VMTypeLen)
        prefixMask = append(prefixMask, vmType...)

        return prefixMask
    }

    func createSuffixMask(creatorAddress []byte) []byte {
        return creatorAddress[len(creatorAddress)-2:]
    }
    """
