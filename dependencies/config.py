from erdpy.dependencies.modules import ArwenToolsModule, Rust, StandaloneModule


def get_all_modules():
    return [
        StandaloneModule(key="llvm", name="llvm", tag="v9", groups=["clang", "cpp"],
                         urls_by_platform={
                             "linux": "vendor-llvm/v9-19feb/linux-amd64.tar.gz?t=19feb",
                             "osx": "vendor-llvm/v9-19feb/darwin-amd64.tar.gz",
                             "windows": "vendor-llvm/v9-19feb/windows-amd64.tar.gz",
        }),

        ArwenToolsModule(key="arwentools", name="arwentools", tag="g03d0b3f", groups=["arwentools"],
                         urls_by_platform={
                             "linux": "travis-builds/ARWEN_v0.3.20-24-ge8c5c68_linux_amd64.tar.gz",
                             "osx": "travis-builds/ARWEN_v0.3.20-24-ge8c5c68_darwin_amd64.tar.gz"
        }),

        Rust(key="rust", name="rust", tag="initial", groups=["rust"])
    ]
