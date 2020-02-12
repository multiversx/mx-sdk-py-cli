import subprocess

from erdpy import dependencies, errors, myprocess, utils
from erdpy.projects.project_base import Project


class ProjectSol(Project):
    def __init__(self, directory):
        super().__init__(directory)

    def perform_build(self):
        try:
            pass
        except subprocess.CalledProcessError as err:
            raise errors.BuildError(err.output)

    def get_dependencies(self):
        return ["soll", "llvm-for-soll"]


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