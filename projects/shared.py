import os


def is_source_clang(directory):
    return _directory_contains_file(directory, ".c")


def is_source_cpp(directory):
    return _directory_contains_file(directory, ".cpp")


def is_source_sol(directory):
    return _directory_contains_file(directory, ".sol")


def is_source_rust(directory):
    return _directory_contains_file(directory, "Cargo.toml")


def _directory_contains_file(directory, name_suffix):
    for file in os.listdir(directory):
        if file.lower().endswith(name_suffix.lower()):
            return True
