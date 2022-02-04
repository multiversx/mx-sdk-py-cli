import base64
from typing import Any, Dict, List, Union

from erdpy.interfaces import ISimulateCostResponse, ISimulateResponse, ITransactionOnNetwork
from erdpy.utils import ISerializable


class GenericProxyResponse(ISerializable):
    def __init__(self, data: Any) -> None:
        self.__dict__.update(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self.__dict__.get(key, default)


class NetworkConfig:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.num_shards = data.get("erd_num_shards_without_meta", 0)
        self.min_gas_price = data.get("erd_min_gas_price", 0)
        self.chain_id = data.get("erd_chain_id", "?")
        self.min_tx_version = data.get("erd_min_transaction_version", 0)


class TransactionOnNetwork(ITransactionOnNetwork):
    def __init__(self, hash: str, response: GenericProxyResponse) -> None:
        raw = response.get("transaction", dict())
        contract_results: List[Dict[str, Any]] = raw.get("smartContractResults", [])
        logs: List[Dict[str, Any]] = raw.get("logs", [])

        self.raw = raw
        self.hash = hash
        self.parsed_contract_results = [SmartContractResult(item) for item in contract_results]
        self.parsed_logs = [Log(item) for item in logs]

    def is_done(self) -> bool:
        return self.raw.get("hyperblockNonce", 0) > 0

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["hash"] = self.hash
        result["parsed"] = {
            "smartContractResults": self.parsed_contract_results,
            "logs": self.parsed_logs
        }

        return result


class SmartContractResult(ISerializable):
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw
        self.parsed_data = decode_hex_base64(raw.get("data"))
        self.parsed_log = Log(raw.get("logs", {}))

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = {
            "data": self.parsed_data,
            "log": self.parsed_log
        }

        return result


class Log(ISerializable):
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.events = []


class SimulateResponse(ISimulateResponse):
    def __init__(self, response: GenericProxyResponse) -> None:
        contract_results: Dict[str, Any] = response.get("scResults") or dict()

        self.raw = response.to_dictionary()
        self.parsed_contract_results = [SmartContractResult(item) for item in contract_results.values()]

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = {
            "smartContractResults": self.parsed_contract_results
        }

        return result


class SimulateCostResponse(ISimulateCostResponse):
    def __init__(self, response: GenericProxyResponse) -> None:
        contract_results: Dict[str, Any] = response.get("smartContractResults") or dict()

        self.raw = response.to_dictionary()
        self.parsed_contract_results = [SmartContractResult(item) for item in contract_results.values()]

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = {
            "smartContractResults": self.parsed_contract_results
        }

        return result


def decode_hex_base64(input: Union[str, None]) -> str:
    return bytes.fromhex(decode_base64(input)).decode('ascii') if input else ""


def decode_base64(input: Union[str, None]) -> str:
    return base64.b64decode(input).decode() if input else ""

