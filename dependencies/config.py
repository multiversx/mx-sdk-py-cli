from erdpy.dependencies.modules import ArwenToolsModule, Rust, StandaloneModule


def get_all_deps():
    return [
        StandaloneModule(key="llvm", aliases=["clang", "cpp"]),
        ArwenToolsModule(key="arwentools"),
        Rust(key="rust", tag="initial")
    ]
