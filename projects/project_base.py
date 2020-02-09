import binascii
import os
from os import path
from pathlib import Path

from erdpy import dependencies, errors, utils


class Project:
    def __init__(self, directory):
        self.directory = directory

    def build(self, debug):
        self.debug = debug
        self._ensure_dependencies_installed()
        self.unit = self.get_main_unit()
        self.file_wasm = self.unit.with_suffix(".wasm")
        self.file_wasm_hex = self.unit.with_suffix(".hex")
        self.file_wasm_hex_arwen = self.unit.with_suffix(".hex.arwen")
        self.perform_build()
        self._create_arwen_files()

    def _ensure_dependencies_installed(self):
        module_keys = self.get_dependencies()
        for module_key in module_keys:
            dependencies.install_module(module_key)

    def get_dependencies(self):
        raise NotImplementedError()

    def get_main_unit(self):
        raise NotImplementedError()

    def perform_build(self):
        raise NotImplementedError()

    def find_file(self, suffix):
        all_files = os.listdir(self.directory)
        files = [file for file in all_files if file.endswith(suffix)]

        if len(files) == 0:
            raise errors.KnownError(f"No file with suffix: [{suffix}].")
        if len(files) > 1:
            raise errors.KnownError(
                f"More files found with suffix: [{suffix}]")

        file = path.join(self.directory, files[0])
        return Path(file).resolve()

    def _create_arwen_files(self):
        ARWEN_TAG = b"@0500"

        with open(self.file_wasm, "rb") as file:
            bytecode_hex = binascii.hexlify(file.read())
        with open(self.file_wasm_hex, "wb+") as file:
            file.write(bytecode_hex)
        with open(self.file_wasm_hex_arwen, "wb+") as file:
            file.write(bytecode_hex)
            file.write(ARWEN_TAG)

    def get_bytecode(self):
        bytecode = utils.read_file(self.file_wasm_hex_arwen)
        return bytecode
