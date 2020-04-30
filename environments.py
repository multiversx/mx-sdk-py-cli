import asyncio
import logging
import traceback

from erdpy import errors, nodedebug
from erdpy.proxy import ElrondProxy

logger = logging.getLogger("environments")


class Environment:
    def __init__(self):
        pass

    def run_flow(self):
        raise NotImplementedError()

    def deploy_contract(self, contract, owner, arguments=None, gas_price=None, gas_limit=None):
        raise NotImplementedError()

    def execute_contract(self, contract, caller, function, arguments=None, gas_price=None, gas_limit=None):
        raise NotImplementedError()

    def query_contract(self, contract, function, arguments=None):
        raise NotImplementedError()


class DebugEnvironment(Environment):
    def __init__(self):
        super().__init__()

    def run_flow(self, flow):
        nodedebug.install_if_missing()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_node_debug_and_flow(flow))
        loop.close()
        asyncio.set_event_loop(asyncio.new_event_loop())

    async def _run_node_debug_and_flow(self, flow):
        await asyncio.wait([
            nodedebug.start_async(),
            self._wrap_flow(flow)
        ])

    async def _wrap_flow(self, flow):
        try:
            logger.debug("Wait before starting flow...")
            await asyncio.sleep(1)
            logger.debug("Starting flow...")
            flow()
            logger.debug("Flow ran.")
            await asyncio.sleep(1)
        except errors.KnownError as err:
            logger.critical(err)
        except Exception:
            print(traceback.format_exc())
        finally:
            nodedebug.stop()

    def deploy_contract(self, contract, owner, arguments=None, gas_price=None, gas_limit=None):
        raise Exception("Temporarily disabled: deploy_contract on debug")

        logger.debug("deploy_contract")
        tx_hash, contract_address = nodedebug.deploy(contract.bytecode, owner, arguments, gas_price, gas_limit)
        contract.address = contract_address
        return tx_hash, contract_address

    def execute_contract(self, contract, caller, function, arguments=None, gas_price=None, gas_limit=None):
        raise Exception("Temporarily disabled: execute_contract on debug")

        logger.debug("execute_contract")
        nodedebug.execute(contract.address, caller, function, arguments, gas_price, gas_limit)

    def query_contract(self, contract, function, arguments=None):
        raise Exception("Temporarily disabled: query_contract on debug")

        logger.debug("query_contract")
        return nodedebug.query(contract.address, function, arguments)


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

    def deploy_contract(self, contract, owner, arguments=None, gas_price=None, gas_limit=None, value=None):
        logger.debug("deploy_contract")
        proxy = self._get_proxy()
        tx_hash, address = contract.deploy(proxy, owner, arguments, gas_price, gas_limit, value)
        return tx_hash, contract.address

    def execute_contract(self, contract, caller, function, arguments=None, gas_price=None, gas_limit=None, value=None):
        logger.debug("execute_contract: %s", contract.address.bech32())
        proxy = self._get_proxy()
        tx_hash = contract.execute(proxy, caller, function, arguments, gas_price, gas_limit, value)
        return tx_hash

    def upgrade_contract(self, contract, caller, arguments=None, gas_price=None, gas_limit=None, value=None):
        logger.debug("upgrade_contract: %s", contract.address.bech32())
        proxy = self._get_proxy()
        tx_hash = contract.upgrade(proxy, caller, arguments, gas_price, gas_limit, value)
        return tx_hash

    def query_contract(self, contract, function, arguments=None):
        logger.debug("query_contract: %s", contract.address.bech32())
        proxy = self._get_proxy()
        return_data = contract.query(proxy, function, arguments)
        return return_data

    def _get_proxy(self):
        return ElrondProxy(self.url)
