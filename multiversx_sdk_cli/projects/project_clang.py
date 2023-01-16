import logging
import subprocess
from os import path
from pathlib import Path
from typing import List

from multiversx_sdk_cli import dependencies, errors, myprocess, utils
from multiversx_sdk_cli.projects.project_base import Project, rename_wasm_files

logger = logging.getLogger('ProjectClang')


class ProjectClang(Project):

    def __init__(self, directory: Path):
        super().__init__(directory)

    def perform_build(self):
        self.config = self.load_config()
        self.ensure_source_files()

        self.unit = self.get_unit_file()
        self.file_ll = self.unit.with_suffix('.ll')
        self.file_o = self.unit.with_suffix('.o')
        self.file_export = self.unit.with_suffix('.export')
        self.file_output = self.unit.with_suffix('.wasm')

        try:
            self.do_clang()
            self.do_llvm_link()
            self.do_llc()
            self.do_wasm()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def do_clang(self):
        logger.info('do_clang')

        tool = path.join(self._get_llvm_path(), 'clang-9')
        args = [
            tool,
            '-cc1', '-emit-llvm',
            '-triple=wasm32-unknown-unknown-wasm',
        ]

        if self.options.get('optimized', False):
            args.append('-Ofast')
        else:
            args.append('-O0')

        args.extend(map(str, self.get_source_files()))
        myprocess.run_process(args)

    def do_llvm_link(self):
        logger.info('do_llvm_link')
        tool = path.join(self._get_llvm_path(), 'llvm-link')
        args = [tool]
        args.extend(['-o', str(self.file_ll)])
        args.extend(map(str, self.get_ll_files()))
        myprocess.run_process(args)

    def do_llc(self):
        logger.info('do_llc')
        tool = path.join(self._get_llvm_path(), 'llc')
        args = [tool]

        if self.options.get('optimized', False):
            args.append('-O3')
        else:
            args.append('-O0')

        args.append('-filetype=obj')
        args.append(str(self.file_ll))

        args.extend(['-o', str(self.file_o)])
        myprocess.run_process(args)

    def do_wasm(self):
        logger.info('do_wasm')
        tool = path.join(self._get_llvm_path(), 'wasm-ld')
        args = [
            tool,
            '--no-entry',
            str(self.file_o),
            '-o', str(self.file_output),
            '--strip-all',
            '-allow-undefined'
        ]

        if self.options.get('verbose', False):
            args.append('--verbose')

        logger.info('exported functions:')
        for export in self.get_exported_functions():
            logger.info(f'\t{export}')
            args.append(f'-export={export}')

        myprocess.run_process(args)

    def _do_after_build_custom(self) -> List[Path]:
        output_wasm_file = self._copy_to_output(self.file_output)
        self.file_output.unlink()
        self.file_ll.unlink()
        self.file_o.unlink()
        for ll_file in self.get_ll_files():
            try:
                ll_file.unlink()
            except FileNotFoundError:
                pass

        paths = rename_wasm_files([output_wasm_file], self.options.get("wasm-name"))
        return paths

    def _get_llvm_path(self):
        return dependencies.get_module_directory('llvm')

    def get_source_files(self):
        for filename in self.config['source_files']:
            yield (self.path / filename).expanduser().resolve()

    def get_ll_files(self):
        for source_file in self.get_source_files():
            yield source_file.with_suffix('.ll')

    def get_unit_file(self):
        first_file = next(self.get_source_files())
        return first_file

    def ensure_source_files(self):
        try:
            source_files = self.config['source_files']
            if len(source_files) == 0:
                source_files = self.get_source_files_from_folder()
        except KeyError:
            source_files = self.get_source_files_from_folder()

        self.config['source_files'] = source_files

    def get_exported_functions(self) -> List[str]:
        file_export = self.find_file_globally('*.export')
        lines = utils.read_lines(file_export)
        return lines

    def default_config(self):
        config = super().default_config()
        config['language'] = 'clang'
        config['source_files'] = self.get_source_files_from_folder()
        return config

    def get_source_files_from_folder(self):
        return list(map(str, self.path.rglob('*.c')))

    def get_dependencies(self):
        return ['llvm']
