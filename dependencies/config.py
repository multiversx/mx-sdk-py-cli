from erdpy.dependencies.modules import StandaloneModule, SOLLModule, NodeDebugModule, Rust


def get_all_modules():
    return [
        StandaloneModule(key="llvm", name="llvm", tag="v9",
                         groups=["C_BUILDCHAIN", "SOL_BUILDCHAIN"],
                         urls_by_platform={
                             "linux": "vendor-llvm/v9-19feb/linux-amd64.tar.gz?t=19feb",
                             "osx": "vendor-llvm/v9-19feb/darwin-amd64.tar.gz",
                             "windows": "vendor-llvm/v9-19feb/windows-amd64.tar.gz",
                         }),

        SOLLModule(key="soll", name="soll", tag="v0.0.5",
                         groups=["SOL_BUILDCHAIN"],
                         urls_by_platform={
                             "linux": "vendor-soll/v005/linux-amd64.tar.gz",
                             "osx": "vendor-soll/v005/darwin-amd64.tar.gz"
                         }),

        NodeDebugModule(key="nodedebug", name="nodedebug", tag="v0.1.0",
                         groups=["NODE_DEBUG"],
                         urls_by_platform={
                             "linux": "nodedebug/v010/linux-amd64.tar.gz",
                             "osx": "nodedebug/v010-libfix/darwin-amd64.tar.gz"
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
