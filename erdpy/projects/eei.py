import logging
import sys
import requests
import toml
from typing import Dict, List, Union
from erdpy import utils
from erdpy.diskcache import DiskCache
from erdpy.errors import NotSupportedProjectFeature
from erdpy.projects.interfaces import IProject
from erdpy.proxy.core import ElrondProxy

logger = logging.getLogger("eei")

MAINNET_PROXY_URL = "https://gateway.elrond.com"
MAINNET_ENABLE_EPOCHS_URL = "https://raw.githubusercontent.com/ElrondNetwork/elrond-config-mainnet/master/enableEpochs.toml"
DEVNET_PROXY_URL = "https://devnet-gateway.elrond.com"
DEVNET_ENABLE_EPOCHS_URL = "https://raw.githubusercontent.com/ElrondNetwork/elrond-config-devnet/master/enableEpochs.toml"


def check_compatibility(project: IProject):
    if _should_skip_checks(project):
        return

    logger.info("check_compatibility")

    wasm_file = project.get_file_wasm()
    imports_file = wasm_file.with_suffix(".imports.json")
    imports = utils.read_json_file(imports_file)

    compatible_with_mainnet = _check_imports_compatibility(imports, ActivationKnowledge("mainnet", MAINNET_PROXY_URL, MAINNET_ENABLE_EPOCHS_URL))
    compatible_with_devnet = _check_imports_compatibility(imports, ActivationKnowledge("devnet", DEVNET_PROXY_URL, DEVNET_ENABLE_EPOCHS_URL))

    if _should_ignore_checks(project):
        return

    if not compatible_with_mainnet or not compatible_with_devnet:
        raise NotSupportedProjectFeature()


def _should_skip_checks(project: IProject):
    return project.get_option("eei-checks-skip") is True


def _should_ignore_checks(project: IProject):
    return project.get_option("eei-checks-ignore") is True


def _check_imports_compatibility(imports: List[str], activation_knowledge: 'ActivationKnowledge') -> bool:
    registry = EEIRegistry(activation_knowledge)
    registry.sync_flags()

    not_active: List[str] = []
    not_active_maybe: List[str] = []

    for function_name in imports:
        is_active = registry.is_function_active(function_name)
        if is_active is False:
            not_active.append(function_name)
        elif is_active is None:
            not_active_maybe.append(function_name)

    if not_active:
        logger.error(f"This contract requires functionality not yet available on *{activation_knowledge.network_name}*: {not_active}.")
    if not_active_maybe:
        logger.warn(f"This contract requires functionality that may not be available on *{activation_knowledge.network_name}*: {not_active_maybe}.")

    return len(not_active + not_active_maybe) == 0


class ActivationKnowledge(DiskCache):
    def __init__(self, network_name: str, proxy_url: str, enable_epochs_url: str) -> None:
        super().__init__("projects.eei.ActivationKnowledge", 60 * 30)
        self.network_name = network_name
        self.proxy_url = proxy_url
        self.enable_epochs_url = enable_epochs_url

    def is_flag_active(self, flag_name: str):
        current_epoch_key = f"epoch:{self.proxy_url}"
        enable_epochs_key = f"config:{self.enable_epochs_url}"

        current_epoch: int = self.get_and_cache_item(current_epoch_key, self._fetch_current_epoch)
        enable_epochs: Dict[str, int] = self.get_and_cache_item(enable_epochs_key, self._fetch_enable_epochs)
        enable_epoch = enable_epochs.get(flag_name, sys.maxsize)
        return enable_epoch >= current_epoch

    def _fetch_current_epoch(self):
        logger.info(f"fetch_current_epoch: {self.proxy_url}")
        proxy = ElrondProxy(self.proxy_url)
        return proxy.get_epoch()

    def _fetch_enable_epochs(self):
        logger.info(f"fetch_enable_epochs: {self.enable_epochs_url}")
        response = requests.get(self.enable_epochs_url)
        response.raise_for_status()
        enable_epochs = toml.loads(response.text).get("EnableEpochs", dict())
        return dict(enable_epochs)


class EEIRegistry:
    def __init__(self, activation_knowledge: ActivationKnowledge) -> None:
        self.activation_knowledge = activation_knowledge
        useDifferentGasCostForReadingCachedStorageEpoch = FeatureFlag("UseDifferentGasCostForReadingCachedStorageEpoch")

        self.flags = [
            useDifferentGasCostForReadingCachedStorageEpoch
        ]

        self.functions: List[EEIFunction] = [
            # big int
            EEIFunction("bigIntNew", None, []),
            EEIFunction("bigIntUnsignedByteLength", None, []),
            EEIFunction("bigIntSignedByteLength", None, []),
            EEIFunction("bigIntGetUnsignedBytes", None, []),
            EEIFunction("bigIntGetSignedBytes", None, []),
            EEIFunction("bigIntSetUnsignedBytes", None, []),
            EEIFunction("bigIntSetSignedBytes", None, []),
            EEIFunction("bigIntIsInt64", None, []),
            EEIFunction("bigIntGetInt64", None, []),
            EEIFunction("bigIntSetInt64", None, []),
            EEIFunction("bigIntAdd", None, []),
            EEIFunction("bigIntSub", None, []),
            EEIFunction("bigIntMul", None, []),
            EEIFunction("bigIntTDiv", None, []),
            EEIFunction("bigIntTMod", None, []),
            EEIFunction("bigIntEDiv", None, []),
            EEIFunction("bigIntEMod", None, []),
            EEIFunction("bigIntPow", None, []),
            EEIFunction("bigIntLog2", None, []),
            EEIFunction("bigIntSqrt", None, []),
            EEIFunction("bigIntAbs", None, []),
            EEIFunction("bigIntNeg", None, []),
            EEIFunction("bigIntSign", None, []),
            EEIFunction("bigIntCmp", None, []),
            EEIFunction("bigIntNot", None, []),
            EEIFunction("bigIntAnd", None, []),
            EEIFunction("bigIntOr", None, []),
            EEIFunction("bigIntXor", None, []),
            EEIFunction("bigIntShr", None, []),
            EEIFunction("bigIntShl", None, []),
            EEIFunction("bigIntFinishUnsigned", None, []),
            EEIFunction("bigIntFinishSigned", None, []),
            EEIFunction("bigIntStorageStoreUnsigned", None, []),
            EEIFunction("bigIntStorageLoadUnsigned", None, []),
            EEIFunction("bigIntGetUnsignedArgument", None, []),
            EEIFunction("bigIntGetSignedArgument", None, []),
            EEIFunction("bigIntGetCallValue", None, []),
            EEIFunction("bigIntGetESDTCallValue", None, []),
            EEIFunction("bigIntGetESDTCallValueByIndex", None, []),
            EEIFunction("bigIntGetESDTExternalBalance", None, []),
            EEIFunction("bigIntGetExternalBalance", None, []),

            # small int
            EEIFunction("smallIntGetUnsignedArgument", None, []),
            EEIFunction("smallIntGetSignedArgument", None, []),
            EEIFunction("smallIntFinishUnsigned", None, []),
            EEIFunction("smallIntFinishSigned", None, []),
            EEIFunction("smallIntStorageStoreUnsigned", None, []),
            EEIFunction("smallIntStorageStoreSigned", None, []),
            EEIFunction("smallIntStorageLoadUnsigned", None, []),
            EEIFunction("smallIntStorageLoadSigned", None, []),
            EEIFunction("int64getArgument", None, []),
            EEIFunction("int64storageStore", None, []),
            EEIFunction("int64storageLoad", None, []),
            EEIFunction("int64finish", None, []),

            # buffers
            EEIFunction("mBufferNew", None, []),
            EEIFunction("mBufferNewFromBytes", None, []),
            EEIFunction("mBufferGetLength", None, []),
            EEIFunction("mBufferGetBytes", None, []),
            EEIFunction("mBufferGetByteSlice", None, []),
            EEIFunction("mBufferCopyByteSlice", None, []),
            EEIFunction("mBufferEq", None, []),
            EEIFunction("mBufferSetBytes", None, []),
            EEIFunction("mBufferSetByteSlice", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("mBufferAppend", None, []),
            EEIFunction("mBufferAppendBytes", None, []),
            EEIFunction("mBufferToBigIntUnsigned", None, []),
            EEIFunction("mBufferToBigIntSigned", None, []),
            EEIFunction("mBufferFromBigIntUnsigned", None, []),
            EEIFunction("mBufferFromBigIntSigned", None, []),
            EEIFunction("mBufferStorageStore", None, []),
            EEIFunction("mBufferStorageLoad", None, []),
            EEIFunction("mBufferStorageLoadFromAddress", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("mBufferGetArgument", None, []),
            EEIFunction("mBufferFinish", None, []),
            EEIFunction("mBufferSetRandom", None, []),

            # eei core
            EEIFunction("getSCAddress", None, []),
            EEIFunction("getOwnerAddress", None, []),
            EEIFunction("getShardOfAddress", None, []),
            EEIFunction("isSmartContract", None, []),
            EEIFunction("getExternalBalance", None, []),
            EEIFunction("blockHash", None, []),
            EEIFunction("transferValue", None, []),
            EEIFunction("transferESDTExecute", None, []),
            EEIFunction("transferESDTNFTExecute", None, []),
            EEIFunction("multiTransferESDTNFTExecute", None, []),
            EEIFunction("transferValueExecute", None, []),
            EEIFunction("getArgumentLength", None, []),
            EEIFunction("getArgument", None, []),
            EEIFunction("getFunction", None, []),
            EEIFunction("getNumArguments", None, []),
            EEIFunction("storageStore", None, []),
            EEIFunction("storageLoadLength", None, []),
            EEIFunction("storageLoad", None, []),
            EEIFunction("storageLoadFromAddress", None, []),
            EEIFunction("getCaller", None, []),
            EEIFunction("checkNoPayment", None, []),
            EEIFunction("callValue", None, []),
            EEIFunction("getESDTValue", None, []),
            EEIFunction("getESDTTokenName", None, []),
            EEIFunction("getESDTTokenNonce", None, []),
            EEIFunction("getESDTTokenType", None, []),
            EEIFunction("getCallValueTokenName", None, []),
            EEIFunction("getESDTValueByIndex", None, []),
            EEIFunction("getESDTTokenNameByIndex", None, []),
            EEIFunction("getESDTTokenNonceByIndex", None, []),
            EEIFunction("getESDTTokenTypeByIndex", None, []),
            EEIFunction("getCallValueTokenNameByIndex", None, []),
            EEIFunction("getNumESDTTransfers", None, []),
            EEIFunction("getCurrentESDTNFTNonce", None, []),
            EEIFunction("writeLog", None, ["deprecated"]),
            EEIFunction("writeEventLog", None, []),
            EEIFunction("returnData", None, []),
            EEIFunction("signalError", None, []),
            EEIFunction("getGasLeft", None, []),
            EEIFunction("getESDTBalance", None, []),
            EEIFunction("getESDTNFTNameLength", None, []),
            EEIFunction("getESDTNFTAttributeLength", None, []),
            EEIFunction("getESDTNFTURILength", None, []),
            EEIFunction("getESDTTokenData", None, []),
            EEIFunction("getESDTLocalRoles", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("validateTokenIdentifier", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("executeOnDestContext", None, []),
            EEIFunction("executeOnDestContextByCaller", None, []),
            EEIFunction("executeOnSameContext", None, []),
            EEIFunction("executeReadOnly", None, []),
            EEIFunction("createContract", None, []),
            EEIFunction("deployFromSourceContract", None, []),
            EEIFunction("upgradeContract", None, []),
            EEIFunction("upgradeFromSourceContract", None, []),
            EEIFunction("asyncCall", None, []),
            EEIFunction("getNumReturnData", None, []),
            EEIFunction("getReturnDataSize", None, []),
            EEIFunction("getReturnData", None, []),
            EEIFunction("cleanReturnData", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("deleteFromReturnData", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("setStorageLock", None, []),
            EEIFunction("getStorageLock", None, []),
            EEIFunction("isStorageLocked", None, []),
            EEIFunction("clearStorageLock", None, []),
            EEIFunction("getBlockTimestamp", None, []),
            EEIFunction("getBlockNonce", None, []),
            EEIFunction("getBlockRound", None, []),
            EEIFunction("getBlockEpoch", None, []),
            EEIFunction("getBlockRandomSeed", None, []),
            EEIFunction("getStateRootHash", None, []),
            EEIFunction("getPrevBlockTimestamp", None, []),
            EEIFunction("getPrevBlockNonce", None, []),
            EEIFunction("getPrevBlockRound", None, []),
            EEIFunction("getPrevBlockEpoch", None, []),
            EEIFunction("getPrevBlockRandomSeed", None, []),
            EEIFunction("getOriginalTxHash", None, []),

            # eei core (managed)
            EEIFunction("managedSCAddress", None, []),
            EEIFunction("managedOwnerAddress", None, []),
            EEIFunction("managedCaller", None, []),
            EEIFunction("managedSignalError", None, []),
            EEIFunction("managedWriteLog", None, []),
            EEIFunction("managedMultiTransferESDTNFTExecute", None, []),
            EEIFunction("managedTransferValueExecute", None, []),
            EEIFunction("managedExecuteOnDestContext", None, []),
            EEIFunction("managedExecuteOnDestContextByCaller", None, []),
            EEIFunction("managedExecuteOnSameContext", None, []),
            EEIFunction("managedExecuteReadOnly", None, []),
            EEIFunction("managedCreateContract", None, []),
            EEIFunction("managedDeployFromSourceContract", None, []),
            EEIFunction("managedUpgradeContract", None, []),
            EEIFunction("managedUpgradeFromSourceContract", None, []),
            EEIFunction("managedAsyncCall", None, []),
            EEIFunction("managedGetMultiESDTCallValue", None, []),
            EEIFunction("managedGetESDTBalance", None, []),
            EEIFunction("managedGetESDTTokenData", None, []),
            EEIFunction("managedGetReturnData", None, []),
            EEIFunction("managedGetPrevBlockRandomSeed", None, []),
            EEIFunction("managedGetBlockRandomSeed", None, []),
            EEIFunction("managedGetStateRootHash", None, []),
            EEIFunction("managedGetOriginalTxHash", None, []),

            # crypto
            EEIFunction("sha256", None, []),
            EEIFunction("managedSha256", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("keccak256", None, []),
            EEIFunction("managedKeccak256", useDifferentGasCostForReadingCachedStorageEpoch, []),
            EEIFunction("ripemd160", None, []),
            EEIFunction("verifyBLS", None, []),
            EEIFunction("verifyEd25519", None, []),
            EEIFunction("verifySecp256k1", None, []),
            EEIFunction("verifyCustomSecp256k1", None, []),
            EEIFunction("encodeSecp256k1DerSignature", None, []),
            EEIFunction("addEC", None, []),
            EEIFunction("doubleEC", None, []),
            EEIFunction("isOnCurveEC", None, []),
            EEIFunction("scalarBaseMultEC", None, []),
            EEIFunction("scalarMultEC", None, []),
            EEIFunction("marshalEC", None, []),
            EEIFunction("unmarshalEC", None, []),
            EEIFunction("marshalCompressedEC", None, []),
            EEIFunction("unmarshalCompressedEC", None, []),
            EEIFunction("generateKeyEC", None, []),
            EEIFunction("createEC", None, []),
            EEIFunction("getCurveLengthEC", None, []),
            EEIFunction("getPrivKeyByteLengthEC", None, []),
            EEIFunction("ellipticCurveGetValues", None, [])
        ]

        self.functions_dict = {function.name: function for function in self.functions}

    def sync_flags(self):
        for flag in self.flags:
            flag.sync(self.activation_knowledge)

    def is_function_active(self, function_name: str) -> Union[bool, None]:
        function = self.functions_dict.get(function_name, None)
        if function is None:
            return False
        if function.activated_by is None:
            return True
        return function.activated_by.is_active


class FeatureFlag:
    def __init__(self, name: str) -> None:
        self.name = name
        self.is_active: Union[bool, None] = None

    def sync(self, knowledge: 'ActivationKnowledge'):
        self.is_active = knowledge.is_flag_active(self.name)
        try:
            self.is_active = knowledge.is_flag_active(self.name)
        except Exception as err:
            self.is_active = None
            logging.error(err)


class EEIFunction:
    def __init__(self, name: str, activated_by: Union[FeatureFlag, None], tags: List[str]) -> None:
        self.name = name
        self.activated_by = activated_by
        self.tags = tags
