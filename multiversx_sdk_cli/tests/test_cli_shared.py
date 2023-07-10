from multiversx_sdk_cli.cli_shared import convert_args_object_to_args_list


class ContractBuildArgs:
    def __init__(self) -> None:
        self.verbose = False
        self.path = "testadata-out/SANDBOX/myadder-rs"
        self.no_wasm_opt = False
        self.wasm_symbols = False
        self.wasm_name = None
        self.wasm_suffix = None
        self.target_dir = None
        self.wat = False
        self.mir = False
        self.llvm_ir = False
        self.ignore = None
        self.no_imports = False
        self.no_abi_git_version = False
        self.twiggy_top = False
        self.twiggy_paths = False
        self.twiggy_monos = False
        self.twiggy_dominators = False
        self.func = "should be a func object"


def test_args_obj_to_list():
    contract_build_args = ContractBuildArgs()

    args_list = convert_args_object_to_args_list(contract_build_args)

    assert len(args_list) == 2
    assert args_list[0] == "--path"
    assert args_list[1] == contract_build_args.path

    contract_build_args.no_wasm_opt = True
    args_list = convert_args_object_to_args_list(contract_build_args)

    assert len(args_list) == 3
    assert args_list[0] == "--path"
    assert args_list[1] == contract_build_args.path
    assert args_list[2] == "--no-wasm-opt"

    contract_build_args.ignore = "random_directory"
    contract_build_args.no_imports = True
    args_list = convert_args_object_to_args_list(contract_build_args)

    assert len(args_list) == 6
    assert args_list[3] == "--ignore"
    assert args_list[4] == contract_build_args.ignore
    assert args_list[5] == "--no-imports"
