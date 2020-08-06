import logging
import traceback

from erdpy import errors
from erdpy.contracts import SmartContract
from erdpy.proxy import ElrondProxy

logger = logging.getLogger("environments")


class Environment:
    def __init__(self):
        pass

    def run_flow(self):
        raise NotImplementedError()

    def deploy_contract(self, contract, owner, arguments, gas_price, gas_limit, chain, version):
        raise NotImplementedError()

    def execute_contract(self, contract, caller, function, arguments, gas_price, gas_limit, chain, version):
        raise NotImplementedError()

    def query_contract(self, contract, function, arguments=None):
        raise NotImplementedError()


class TestnetEnvironment(Environment):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def run_flow(self, flow):
        return self._wrap_flow(flow)

    def _wrap_flow(self, flow):
        try:
            logger.debug("Starting flow...")
            result = flow()
            logger.debug("Flow ran.")
            return result
        except errors.KnownError as err:
            logger.critical(err)
        except Exception:
            print(traceback.format_exc())

    def deploy_contract(self, contract: SmartContract, owner, arguments, gas_price, gas_limit, value, chain, version):
        logger.debug("deploy_contract")
        tx = contract.deploy(owner, arguments, gas_price, gas_limit, value, chain, version)
        proxy = self._get_proxy()
        tx_hash = tx.send(proxy)
        return tx_hash, contract.address

    def execute_contract(self, contract: SmartContract, caller, function, arguments, gas_price, gas_limit, value, chain, version):
        logger.debug("execute_contract: %s", contract.address.bech32())
        tx = contract.execute(caller, function, arguments, gas_price, gas_limit, value, chain, version)
        proxy = self._get_proxy()
        tx_hash = tx.send(proxy)
        return tx_hash

    def upgrade_contract(self, contract: SmartContract, caller, arguments, gas_price, gas_limit, value, chain, version):
        logger.debug("upgrade_contract: %s", contract.address.bech32())
        tx = contract.upgrade(caller, arguments, gas_price, gas_limit, value, chain, version)
        proxy = self._get_proxy()
        tx_hash = tx.send(proxy)
        return tx_hash

    def query_contract(self, contract, function, arguments=None):
        logger.debug("query_contract: %s", contract.address.bech32())
        proxy = self._get_proxy()
        return_data = contract.query(proxy, function, arguments)
        return return_data

    def _get_proxy(self):
        return ElrondProxy(self.url)
