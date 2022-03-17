import logging
from typing import List, Union

from erdpy.projects.eei_activation import ActivationEpochsInfo


class EEIRegistry:
    def __init__(self, activation_info: ActivationEpochsInfo) -> None:
        self.activation_info = activation_info
        
        storageAPICostOptimizationEnableEpoch = FeatureFlag("StorageAPICostOptimizationEnableEpoch")

        self.flags = [
            storageAPICostOptimizationEnableEpoch
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
            EEIFunction("mBufferSetByteSlice", storageAPICostOptimizationEnableEpoch, []),
            EEIFunction("mBufferAppend", None, []),
            EEIFunction("mBufferAppendBytes", None, []),
            EEIFunction("mBufferToBigIntUnsigned", None, []),
            EEIFunction("mBufferToBigIntSigned", None, []),
            EEIFunction("mBufferFromBigIntUnsigned", None, []),
            EEIFunction("mBufferFromBigIntSigned", None, []),
            EEIFunction("mBufferStorageStore", None, []),
            EEIFunction("mBufferStorageLoad", None, []),
            EEIFunction("mBufferStorageLoadFromAddress", storageAPICostOptimizationEnableEpoch, []),
            EEIFunction("mBufferGetArgument", None, []),
            EEIFunction("mBufferFinish", None, []),
            EEIFunction("mBufferSetRandom", None, []),

            # eei core
            EEIFunction("getSCAddress", None, []),
            EEIFunction("getOwnerAddress", None, []),
            EEIFunction("getShardOfAddress", None, []),
            EEIFunction("isSmartContract", None, []),
            EEIFunction("getExternalBalance", None, []),
            EEIFunction("getBlockHash", None, []),
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
            EEIFunction("getCallValue", None, []),
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
            EEIFunction("finish", None, []),
            EEIFunction("signalError", None, []),
            EEIFunction("getGasLeft", None, []),
            EEIFunction("getESDTBalance", None, []),
            EEIFunction("getESDTNFTNameLength", None, []),
            EEIFunction("getESDTNFTAttributeLength", None, []),
            EEIFunction("getESDTNFTURILength", None, []),
            EEIFunction("getESDTTokenData", None, []),
            EEIFunction("getESDTLocalRoles", storageAPICostOptimizationEnableEpoch, []),
            EEIFunction("validateTokenIdentifier", storageAPICostOptimizationEnableEpoch, []),
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
            EEIFunction("cleanReturnData", storageAPICostOptimizationEnableEpoch, []),
            EEIFunction("deleteFromReturnData", storageAPICostOptimizationEnableEpoch, []),
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
            EEIFunction("managedSha256", storageAPICostOptimizationEnableEpoch, []),
            EEIFunction("keccak256", None, []),
            EEIFunction("managedKeccak256", storageAPICostOptimizationEnableEpoch, []),
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
            flag.sync(self.activation_info)

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

    def sync(self, activation_info: ActivationEpochsInfo):
        try:
            self.is_active = activation_info.is_flag_active(self.name)
        except Exception as err:
            self.is_active = None
            logging.error(err)


class EEIFunction:
    def __init__(self, name: str, activated_by: Union[FeatureFlag, None], tags: List[str]) -> None:
        self.name = name
        self.activated_by = activated_by
        self.tags = tags
