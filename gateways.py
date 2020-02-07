from erdpy import nodedebug

class Gateway:
    def __init__(self):
        pass

    def deploy_contract(self, contract):
        raise NotImplementedError()


class DebugGateway(Gateway):
    def __init__(self):
        super().__init__()

    def deploy_contract(self, contract):
        nodedebug.start(force=False)

        tx_hash = None
        contract_address = None

        return tx_hash, contract_address


class TestnetGateway(Gateway):
    pass
