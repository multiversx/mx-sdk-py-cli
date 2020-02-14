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

        StandaloneModule(key="nodedebug", name="nodedebug", tag="v0.0.7",
                         groups=["NODE_DEBUG"],
                         urls_by_platform={
                             "linux": "nodedebug/v007/linux-amd64.tar.gz",
                             "osx": "nodedebug/v007/darwin-amd64.tar.gz"
                         }),
                        
        StandaloneModule(key="testrunner", name="testrunner", tag="v0.0.1",
                         groups=["testing"],
                         urls_by_platform={
                             "linux": "testrunner/v001/linux-amd64.tar.gz",
                             "osx": "testrunner/v001/darwin-amd64.tar.gz"
                         }),

        Rust(key="rust", name="rust", tag="initial",
             groups=["RUST_BUILDCHAIN"])
    ]
