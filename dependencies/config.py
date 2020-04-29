from erdpy.dependencies.modules import (ArwenToolsModule, Rust, SOLLModule,
                                        StandaloneModule)


def get_all_modules():
    return [
        StandaloneModule(key="llvm", name="llvm", tag="v9", groups=["C_BUILDCHAIN", "SOL_BUILDCHAIN"],
                         urls_by_platform={
                             "linux": "vendor-llvm/v9-19feb/linux-amd64.tar.gz?t=19feb",
                             "osx": "vendor-llvm/v9-19feb/darwin-amd64.tar.gz",
                             "windows": "vendor-llvm/v9-19feb/windows-amd64.tar.gz",
        }),

        SOLLModule(key="soll", name="soll", tag="v0.0.5", groups=["SOL_BUILDCHAIN"],
                   urls_by_platform={
            "linux": "vendor-soll/v005/linux-amd64.tar.gz",
            "osx": "vendor-soll/v005/darwin-amd64.tar.gz"
        }),

        ArwenToolsModule(key="arwentools", name="arwentools", tag="geb3c3f7", groups=["ARWENTOOLS"],
                         urls_by_platform={
                             "linux": "travis-builds/ARWEN_v0.3.15-120-geb3c3f7_linux_amd64.tar.gz",
                             "osx": "travis-builds/ARWEN_v0.3.15-120-geb3c3f7_darwin_amd64.tar.gz"
        }),

        Rust(key="rust", name="rust", tag="initial", groups=["RUST_BUILDCHAIN"])
    ]
