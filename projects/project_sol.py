import logging
import subprocess
from os import path
from pathlib import Path

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project

logger = logging.getLogger("ProjectSol")

class ProjectSol(Project):
    def __init__(self, directory):
        super().__init__(directory)

    def perform_build(self):
        """
        See https://github.com/second-state/SOLL/blob/master/utils/ll2ewasm_sol
        """

        self.unit = self.find_file(".sol")
        self.unit_name = self.unit.stem
        self.file_ll = self.unit.with_suffix(".ll")
        self.file_functions = self.unit.with_suffix(".functions")
        self.file_main_ll = self.unit.with_suffix(".main.ll")
        self.file_bc = self.unit.with_suffix(".bc")
        self.file_o = self.unit.with_suffix(".o")

        try:
            self._create_main_ll()
            self._emit_LLVM()
            self._emit_funcions()
            self._do_llvm_link()
            self._do_llvm_opt()
            self._do_llc()
            self._do_wasm_ld()
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def _create_main_ll(self):
        logger.info("_create_main_ll")

        package_path = Path(__file__).parent
        template_path = package_path.joinpath("sol_main_ll.txt")
        template = utils.read_file(template_path)
        content = template.replace("{{NAME}}", self.unit_name)
        utils.write_file(self.file_main_ll, content)

    def _emit_LLVM(self):
        logger.info("_emit_LLVM")

        tool = self._get_soll_path()
        args = [tool, "-action", "EmitLLVM", str(self.unit)]
        output = myprocess.run_process(args)
        utils.write_file(self.file_ll, output)

    def _emit_funcions(self):
        logger.info("_emit_funcions")

        tool = self._get_soll_path()
        args = [tool, "-action", "EmitFuncSig", str(self.unit)]
        output = myprocess.run_process(args)
        utils.write_file(self.file_functions, output)

    def _do_llvm_link(self):
        logger.info("_do_llvm_link")

        tool = path.join(self._get_llvm_path(), "llvm-link")
        args = [tool, self.file_ll, self.file_main_ll, "-o", self.file_bc]
        myprocess.run_process(args)

    def _do_llvm_opt(self):
        logger.info("_do_llvm_opt")

        tool = path.join(self._get_llvm_path(), "opt")
        args = [tool, "-std-link-opts", "-Oz", "-polly", self.file_bc, "-o", self.file_bc]
        myprocess.run_process(args)

    def _do_llc(self):
        logger.info("_do_llc")

        tool = path.join(self._get_llvm_path(), "llc")
        args = [tool, "-O3", "-filetype=obj", self.file_bc, "-o", self.file_o]
        myprocess.run_process(args)

    def _do_wasm_ld(self):
        logger.info("_do_wasm_ld")

        tool = path.join(self._get_llvm_path(), "wasm-ld")
        args = [
            tool, 
            "--entry",
            "main",
            "--demangle",
            "--no-gc-sections",
            "--export-all",
            "--allow-undefined",
            "--verbose",
            self.file_o,
            "-o", self.get_file_wasm()
        ]
        myprocess.run_process(args)

    def get_file_wasm(self):
        return self.find_file(".sol").with_suffix(".wasm")

    def _get_soll_path(self):
        directory = dependencies.get_install_directory("soll")
        return path.join(directory, "soll")

    def _get_llvm_path(self):
        return dependencies.get_install_directory("llvm")

    def get_dependencies(self):
        return ["soll", "llvm"]


# private static async buildSolModule(smartContract: SmartContract): Promise<any> {
#         let filePath = smartContract.SourceFile.Path;
#         let filePathWithoutExtension = smartContract.SourceFile.PathWithoutExtension;
#         let filePath_ll = `${filePathWithoutExtension}.ll`;
#         let filePath_functions = `${filePathWithoutExtension}.functions`;
#         let filePath_main_ll = `${filePathWithoutExtension}.main.ll`;
#         let filePath_bc = `${filePathWithoutExtension}.bc`;
#         let filePath_o = `${filePathWithoutExtension}.o`;
#         let filePath_wasm = `${filePathWithoutExtension}.wasm`;

#         let toolsFolder = Builder.getSolidityToolsFolder();
#         let llvmToolsFolder = Builder.getLlvmToolsFolder("v8");

#         let sollPath: string = path.join(toolsFolder, "soll");
#         let llvmLinkPath: string = path.join(llvmToolsFolder, "llvm-link");
#         let llvmOptPath: string = path.join(llvmToolsFolder, "opt");
#         let llvmLlcPath: string = path.join(llvmToolsFolder, "llc");
#         let wasmLdPath: any = path.join(llvmToolsFolder, "wasm-ld");

#         let mainLlContent = `
# source_filename = "${smartContract.SourceFile.Name}"
# target datalayout = "e-m:e-p:32:32-i64:64-n32:64-S128"
# target triple = "wasm32-unknown-unknown-wasm"
# declare void @solidity.main()
# define void @main() {
#     tail call void @solidity.main()
#     ret void
# }`;

#         function emitLLVM(): Promise<any> {
#             return ProcessFacade.execute({
#                 program: sollPath,
#                 args: ["-action", "EmitLLVM", filePath],
#                 stdoutToFile: filePath_ll,
#                 channels: ["builder", "build:SOL"],
#                 doNotDumpStdout: true
#             });
#         }

#         function traceLineByLine() {
#             let ll = FsFacade.readFile(filePath_ll);
#             let lines = ll.split(/\r?\n/);
#             let linesNew: string[] = [];

#             lines.forEach(line => {
#                 linesNew.push(line);

#                 if (line.startsWith("target triple =")) {
#                     linesNew.push("", "declare void @debugPrintLineNumber(i32) ; IDE-generated")
#                 }

#                 if (line.startsWith("  ret") || line.startsWith("  br") || line.startsWith("  unreachable") || 
#                     line.startsWith("  switch") || line.startsWith("  ]") || line.startsWith("    ") || line.indexOf(" = phi") > 0) {
#                     return;
#                 }

#                 if (line.startsWith("  ")) {
#                     linesNew.push(`  call void @debugPrintLineNumber(i32 ${linesNew.length + 1}) ; IDE-generated`)
#                 }
#             });

#             let newLl = linesNew.join("\n");
#             FsFacade.writeFile(filePath_ll, newLl);
#         }

#         function emitFuncSig(): Promise<any> {
#             return ProcessFacade.execute({
#                 program: sollPath,
#                 args: ["-action", "EmitFuncSig", filePath],
#                 stdoutToFile: filePath_functions,
#                 channels: ["builder", "build:SOL"]
#             });
#         }

#         function llvmLink(): Promise<any> {
#             return ProcessFacade.execute({
#                 program: llvmLinkPath,
#                 args: [filePath_ll, filePath_main_ll, "-o", filePath_bc],
#                 channels: ["builder", "build:SOL"]
#             });
#         }

#         function llvmOpt(): Promise<any> {
#             return ProcessFacade.execute({
#                 program: llvmOptPath,
#                 args: ["-std-link-opts", "-Oz", "-polly", filePath_bc, "-o", filePath_bc],
#                 channels: ["builder", "build:SOL"]
#             });
#         }

#         function doLlc(): Promise<any> {
#             return ProcessFacade.execute({
#                 program: llvmLlcPath,
#                 args: ["-O3", "-filetype=obj", filePath_bc, "-o", filePath_o],
#                 channels: ["builder", "build:SOL"]
#             });
#         }

#         function doWasmLd(): Promise<any> {
#             return ProcessFacade.execute({
#                 program: wasmLdPath,
#                 args: ["--entry", "main", /* "--gc-sections", */ "--demangle", "--no-gc-sections", "--export-all", "--allow-undefined", "--verbose", filePath_o, "-o", filePath_wasm],
#                 channels: ["builder", "build:SOL"]
#             });
#         }

#         FsFacade.writeFile(filePath_main_ll, mainLlContent)
#         await emitLLVM();
#         //traceLineByLine();
#         await emitFuncSig();
#         await llvmLink();
#         await llvmOpt();
#         await doLlc();
#         await doWasmLd();
#     }
