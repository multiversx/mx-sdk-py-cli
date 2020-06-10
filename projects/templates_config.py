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
            key="sc-examples-rs",
            url="https://github.com/ElrondNetwork/sc-examples-rs/archive/master.zip",
            github="ElrondNetwork/sc-examples-rs",
            relative_path="sc-examples-rs-master"
        )
    ]
