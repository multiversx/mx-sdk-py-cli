import time

from erdpy import config
from erdpy.projects.templates_repository import TemplatesRepository


def get_templates_repositories():
    timestamp = int(time.time())
    examples_rs_tag = config.get_dependency_tag('elrond_wasm_rs')
    examples_rs_tag_no_v = examples_rs_tag[1:]

    return [
        TemplatesRepository(
            key="sc-examples",
            url=f"https://github.com/ElrondNetwork/sc-examples/archive/master.zip?t={timestamp}",
            github="ElrondNetwork/sc-examples",
            relative_path="sc-examples-master"
        ),

        TemplatesRepository(
            key="elrond-wasm-rs",
            url=f"https://github.com/ElrondNetwork/elrond-wasm-rs/archive/{examples_rs_tag}.zip?t={timestamp}",
            github="ElrondNetwork/elrond-wasm-rs",
            relative_path=f"elrond-wasm-rs-{examples_rs_tag_no_v}/examples"
        )
    ]
