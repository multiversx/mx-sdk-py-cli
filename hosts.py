import asyncio
import logging

from erdpy import nodedebug

logger = logging.getLogger("hosts")


class Host:
    def __init__(self):
        pass

    def run_flow(self):
        raise NotImplementedError()

    def deploy_contract(self, contract):
        raise NotImplementedError()

    def execute_contract(self, contract):
        raise NotImplementedError()


class DebugHost(Host):
    def __init__(self):
        super().__init__()

    def run_flow(self, flow):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_node_debug_and_flow(flow))
        loop.close()

    async def _run_node_debug_and_flow(self, flow):
        await asyncio.wait([
            nodedebug.start_async(),
            self._wrap_flow(flow)
        ])

    async def _wrap_flow(self, flow):
        logger.info("Wait before starting flow...")
        await asyncio.sleep(1)
        logger.info("Starting flow...")
        flow()
        logger.info("Flow ran.")
        await asyncio.sleep(1)
        nodedebug.stop()

    def deploy_contract(self, contract, sender):
        tx_hash, contract_address = nodedebug.deploy(contract.bytecode, sender)
        contract.address = contract_address
        return tx_hash, contract_address

    def execute_contract(self, contract, sender, function):
        nodedebug.execute(contract.address, sender, function)

    def query_contract(self, contract, function):
        return nodedebug.query(contract.address, function, None)

class TestnetHost(Host):
    pass
