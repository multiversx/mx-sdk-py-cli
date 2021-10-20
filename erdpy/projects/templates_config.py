import time

from erdpy import config
from erdpy.projects.templates_repository import TemplatesRepository
from erdpy.utils import query_latest_release_tag


def get_templates_repositories():
    timestamp = int(time.time())
    examples_rs_tag = config.get_dependency_tag('elrond_wasm_rs')

    if examples_rs_tag == 'latest':
        examples_rs_tag = query_latest_release_tag('ElrondNetwork/elrond-wasm-rs')

    examples_rs_tag_no_v = remove_initial_v_from_version(examples_rs_tag)

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
            relative_path=f"elrond-wasm-rs-{examples_rs_tag_no_v}/contracts/examples"
        )
    ]


def remove_initial_v_from_version(version: str) -> str:
    """Remove the initial 'v' from semver strings 'vX.XX.XX', but leave branch
    names or non-semver tags unchanged"""
    if version[0] != 'v':
        return version

    version_no_v = version[1:]
    if not version_no_v[0].isnumeric():
        return version

    return version_no_v
