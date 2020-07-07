from erdpy.dependencies.modules import ArwenToolsModule, Rust, StandaloneModule


def get_all_modules():
    return [
        StandaloneModule(key="llvm", name="llvm", tag="v9", groups=["clang", "cpp"],
                         urls_by_platform={
                             "linux": "vendor-llvm/v9-19feb/linux-amd64.tar.gz?t=19feb",
                             "osx": "vendor-llvm/v9-19feb/darwin-amd64.tar.gz",
                             "windows": "vendor-llvm/v9-19feb/windows-amd64.tar.gz",
        }),

        ArwenToolsModule(key="arwentools", name="arwentools", tag="ge1f8648", groups=["arwentools"],
                         urls_by_platform={
                             "linux": "travis-builds/ARWEN_v0.3.26-4-ge1f8648_linux_amd64.tar.gz",
                             "osx": "travis-builds/ARWEN_v0.3.26-4-ge1f8648_darwin_amd64.tar.gz"
        }),

        Rust(key="rust", name="rust", tag="initial", groups=["rust"])
    ]
