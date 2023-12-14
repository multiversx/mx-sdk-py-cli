from multiversx_sdk_cli import config, errors, ux
from multiversx_sdk_cli.dependencies.modules import Rust


def check_if_rust_is_installed():
    RUST_MODULE_KEY = "rust"
    rust_module = Rust(RUST_MODULE_KEY)
    if not rust_module.is_installed(""):
        tag = config.get_dependency_tag(RUST_MODULE_KEY)
        ux.show_critical_error("Rust is not installed on your machine. Run `mxpy deps install rust --overwrite` and try again.")
        raise errors.DependencyMissing(RUST_MODULE_KEY, tag)
