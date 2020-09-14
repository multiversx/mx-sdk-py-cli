import time

from erdpy.projects.templates_repository import TemplatesRepository


def get_templates_repositories():
    timestamp = int(time.time())

    return [
        TemplatesRepository(
            key="sc-examples",
            url=f"https://github.com/ElrondNetwork/sc-examples/archive/master.zip?t={timestamp}",
            github="ElrondNetwork/sc-examples",
            relative_path="sc-examples-master"
        ),

        TemplatesRepository(
            key="elrond-wasm-rs",
            url=f"https://github.com/ElrondNetwork/elrond-wasm-rs/archive/master.zip?t={timestamp}",
            github="ElrondNetwork/elrond-wasm-rs",
            relative_path="elrond-wasm-rs-master/examples"
        )
    ]
