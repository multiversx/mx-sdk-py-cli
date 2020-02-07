import asyncio
import logging

from erdpy import nodedebug

logger = logging.getLogger("gateway")


class Gateway:
    def __init__(self):
        pass

    def run_flow(self):
        raise NotImplementedError()

    def deploy_contract(self, contract):
        raise NotImplementedError()


class DebugGateway(Gateway):
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

    def deploy_contract(self, contract):
        tx_hash = None
        contract_address = None

        return tx_hash, contract_address


class TestnetGateway(Gateway):
    pass
