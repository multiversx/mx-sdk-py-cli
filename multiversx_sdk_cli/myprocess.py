import asyncio
import logging
import subprocess
import traceback
from pathlib import Path
from typing import Any, List, Optional, Union

from multiversx_sdk_cli import errors

logger = logging.getLogger("myprocess")

ReturnCode = int


def run_process(args: List[str], env: Any = None, dump_to_stdout: bool = True, cwd: Optional[Union[str, Path]] = None) -> str:
    logger.info(f"run_process: {args}, in folder: {cwd}")

    try:
        output = subprocess.check_output(args, shell=False, universal_newlines=True, stderr=subprocess.STDOUT, env=env, cwd=cwd)
        logger.info("Successful run. Output:")
        if dump_to_stdout:
            print(output or "[No output]")
        return output
    except subprocess.CalledProcessError as error:
        raise errors.ExternalProcessError(error.cmd, error.output)


def run_process_async(
    args: List[str],
    env: Any = None,
    cwd: Optional[str] = None,
    stdout_sink=None,
    stderr_sink=None
) -> ReturnCode:
    logger.info(f"run_process_async: {args}, in folder: {cwd}")
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_async_subprocess(args, env, stdout_sink, stderr_sink, cwd))
    loop.close()
    asyncio.set_event_loop(asyncio.new_event_loop())
    return result


async def _async_subprocess(args, env, stdout_sink, stderr_sink, cwd: Optional[str]) -> ReturnCode:
    process = await asyncio.create_subprocess_exec(*args, env=env, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE, cwd=cwd)

    await asyncio.wait([
        _read_stream(process.stdout, stdout_sink),
        _read_stream(process.stderr, stderr_sink)
    ])
    return await process.wait()


async def _read_stream(stream, sink):
    sink = sink or ConsoleOutputSink()
    sink.open()

    while True:
        try:
            line = await stream.readline()
            if line:
                line = line.decode("utf-8", "replace").strip()
                sink.write(line)
            else:
                break
        except Exception:
            print(traceback.format_exc())

    sink.close()


class OutputSink:
    def open(self):
        pass

    def write(self, line: str):
        pass

    def close(self):
        pass


class ConsoleOutputSink(OutputSink):
    def write(self, line: str):
        print(line)


class FileOutputSink(OutputSink):
    def __init__(self, filepath: str) -> None:
        super().__init__()
        self.filepath = filepath
        self.file = None

    def open(self):
        self.file = open(self.filepath, "w")

    def write(self, line: str):
        if self.file is None:
            return

        self.file.write(line)

    def close(self):
        if self.file is None:
            return

        self.file.close()
