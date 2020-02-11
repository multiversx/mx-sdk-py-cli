from erdpy.dependencies.modules import StandaloneModule, Rust


def get_all_modules():
    return [
        StandaloneModule(key="llvm-for-c", name="llvm", tag="v9",
                         groups=["C_BUILDCHAIN"],
                         urls_by_platform={
                             "linux": "vendor-llvm/v9/linux-amd64.tar.gz",
                             "osx": "vendor-llvm/v9/darwin-amd64.tar.gz",
                             "windows": "vendor-llvm/v9/windows-amd64.tar.gz",
                         }),

        StandaloneModule(key="llvm-for-soll", name="llvm", tag="v8",
                         groups=["SOL_BUILDCHAIN"],
                         urls_by_platform={
                             "linux": "vendor-llvm/v8/linux-amd64.tar.gz",
                             "osx": "vendor-llvm/v8/darwin-amd64.tar.gz",
                             "windows": "vendor-llvm/v8/windows-amd64.tar.gz",
                         }),

        StandaloneModule(key="soll", name="soll", tag="v0.0.3",
                         groups=["SOL_BUILDCHAIN"],
                         urls_by_platform={
                             "linux": "vendor-soll/linux-amd64.tar.gz",
                             "osx": "vendor-soll/darwin-amd64.tar.gz"
                         }),

        StandaloneModule(key="nodedebug", name="nodedebug", tag="v0.0.5",
                         groups=["NODE_DEBUG"],
                         urls_by_platform={
                             "linux": "nodedebug/v005/linux-amd64.tar.gz",
                             "osx": "nodedebug/v005/darwin-amd64.tar.gz"
                         }),

        Rust(key="rust", name="rust", tag="initial",
             groups=["RUST_BUILDCHAIN"])
    ]
