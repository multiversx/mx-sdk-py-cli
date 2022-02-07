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

        self.raw = raw
        self.hash = hash
        self.parsed_contract_results = [SmartContractResult(item) for item in contract_results]
        self.parsed_logs: List[Log] = []

    def is_done(self) -> bool:
        hyperblock: int = self.raw.get("hyperblockNonce", 0)
        return hyperblock > 0

    def get_hash(self) -> str:
        return self.hash

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = dict()

        if self.parsed_contract_results:
            result["parsed"]["smartContractResults"] = self.parsed_contract_results
        if self.parsed_logs:
            result["parsed"]["logs"] = self.parsed_logs

        return result


class SmartContractResult(ISerializable):
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw
        self.return_message = self._parse_return_message()
        self.arguments = self._parse_arguments()
        self.parsed_log = Log(raw.get("logs", {}))

    def _parse_return_message(self) -> str:
        try:
            data_parts = self._parse_data_parts()
            return_message_encoded = data_parts[0]
            return_message = bytes.fromhex(return_message_encoded).decode("ascii")
            return return_message
        except:
            return ""

    def _parse_arguments(self) -> List[str]:
        try:
            data_parts = self._parse_data_parts()
            arguments = data_parts[1:]
            return arguments
        except:
            return []

    def _parse_data_parts(self) -> List[str]:
        data: str = self.raw.get("data", "").lstrip("@")
        return data.split("@")

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = {
            "returnMessage": self.return_message,
            "arguments": self.arguments,
            "log": self.parsed_log
        }

        return result


class Log(ISerializable):
    def __init__(self, raw: Dict[str, Any]) -> None:
        self.raw = raw


class SimulateResponse(ISimulateResponse):
    def __init__(self, response: GenericProxyResponse) -> None:
        result: Dict[str, Any] = response.get("result") or dict()
        contract_results: Dict[str, Any] = result.get("scResults") or dict()

        self.raw = response.to_dictionary()
        self.parsed_contract_results = [SmartContractResult(item) for item in contract_results.values()]

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = dict()

        if self.parsed_contract_results:
            result["parsed"]["smartContractResults"] = self.parsed_contract_results

        return result


class SimulateCostResponse(ISimulateCostResponse):
    def __init__(self, response: GenericProxyResponse) -> None:
        contract_results: Dict[str, Any] = response.get("smartContractResults") or dict()

        self.raw = response.to_dictionary()
        self.parsed_contract_results = [SmartContractResult(item) for item in contract_results.values()]

    def to_dictionary(self) -> Dict[str, Any]:
        result: Dict[str, Any] = dict()
        result.update(self.raw)
        result["parsed"] = dict()

        if self.parsed_contract_results:
            result["parsed"]["smartContractResults"] = self.parsed_contract_results

        return result


def decode_hex_base64(input: Union[str, None]) -> str:
    return bytes.fromhex(decode_base64(input)).decode('ascii') if input else ""


def decode_base64(input: Union[str, None]) -> str:
    return base64.b64decode(input).decode() if input else ""
