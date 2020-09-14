from erdpy.projects.templates_repository import TemplatesRepository


def get_templates_repositories():
    return [
        TemplatesRepository(
            key="sc-examples",
            url="https://github.com/ElrondNetwork/sc-examples/archive/master.zip",
            github="ElrondNetwork/sc-examples",
            relative_path="sc-examples-master"
        ),

        TemplatesRepository(
            key="elrond-wasm-rs",
            url="https://github.com/ElrondNetwork/elrond-wasm-rs/archive/master.zip",
            github="ElrondNetwork/elrond-wasm-rs",
            relative_path="elrond-wasm-rs-master/examples"
        )
    ]
