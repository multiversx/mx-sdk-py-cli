import asyncio
import logging
import os
import traceback
from pathlib import Path
from typing import Any, Coroutine, List

from multiversx_sdk_cli.testnet.config import TestnetConfiguration

logger = logging.getLogger("localnet")


NODES_START_DELAY = 1
PROXY_START_DELAY = 10

is_after_genesis = False


def start(args: Any):
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(do_start(args))
        loop.close()
        asyncio.set_event_loop(asyncio.new_event_loop())
    except KeyboardInterrupt:
        pass


async def do_start(args: Any):
    config = TestnetConfiguration.from_file(args.configfile)
    logger.info('testnet folder is %s', config.root())

    to_run: List[Coroutine[Any, Any, None]] = []

    # Seed node
    to_run.append(run(["./seednode", "--log-save"], cwd=config.seednode_folder()))

    loglevel = _patch_loglevel(config.general.log_level)
    logger.info(f"loglevel: {loglevel}")

    # Observers
    for observer in config.observers():
        to_run.append(run([
            "./node",
            "--use-log-view",
            "--log-save",
            f"--log-level={loglevel}",
            "--log-logger-name",
            f"--destination-shard-as-observer={observer.shard}",
            f"--rest-api-interface=localhost:{observer.api_port}"
        ], cwd=observer.folder, delay=NODES_START_DELAY))

    # Validators
    for validator in config.validators():
        to_run.append(run([
            "./node",
            "--use-log-view",
            "--log-save",
            f"--log-level={loglevel}",
            "--log-logger-name",
            f"--rest-api-interface=localhost:{validator.api_port}"
        ], cwd=validator.folder, delay=NODES_START_DELAY))

    # Proxy
    to_run.append(run([
        "./proxy",
        "--log-save"
    ], cwd=config.proxy_folder(), delay=PROXY_START_DELAY))

    tasks = [asyncio.create_task(item) for item in to_run]
    await asyncio.gather(*tasks)


async def run(args: List[str], cwd: Path, delay: int = 0):
    await asyncio.sleep(delay)

    logger.info(f"Starting process {args} in folder {cwd}")

    # TODO: Fix this. Useful for Linux, but not for Mac
    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = str(cwd)

    process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE, cwd=cwd, limit=1024 * 512, env=env)

    pid = process.pid

    print(f"Started process [{pid}]", args)
    await asyncio.wait([
        asyncio.create_task(_read_stream(process.stdout, pid)),
        asyncio.create_task(_read_stream(process.stderr, pid))
    ])

    return_code = await process.wait()
    print(f"Proces [{pid}] stopped. Return code: {return_code}.")


async def _read_stream(stream: Any, pid: int):
    while True:
        try:
            line = await stream.readline()
            if line:
                line = line.decode("utf-8", "replace").strip()
                if _is_interesting_logline(line):
                    _dump_interesting_log_line(pid, line)
            else:
                break
        except Exception:
            print(traceback.format_exc())


def _patch_loglevel(loglevel: str) -> str:
    loglevel = loglevel or "*:DEBUG"

    if "vm:" not in loglevel:
        loglevel += ",vm:TRACE"
    if "process/smartcontract:" not in loglevel:
        loglevel += ",process/smartcontract:TRACE"

    return loglevel


LOGLINE_GENESIS_THRESHOLD_MARKER = "started committing block"
LOGLINE_AFTER_GENESIS_INTERESTING_MARKERS = ["started committing block", "ERROR", "WARN", "vm", "smartcontract"]
# We ignore SC calls on genesis.
LOGLINE_ON_GENESIS_INTERESTING_MARKERS = ["started committing block", "ERROR", "WARN"]


def _is_interesting_logline(logline: str):
    global is_after_genesis

    if LOGLINE_GENESIS_THRESHOLD_MARKER in logline:
        is_after_genesis = True

    if is_after_genesis:
        return any(e in logline for e in LOGLINE_AFTER_GENESIS_INTERESTING_MARKERS)
    return any(e in logline for e in LOGLINE_ON_GENESIS_INTERESTING_MARKERS)


def _dump_interesting_log_line(pid: int, logline: str):
    print(f"[PID={pid}]", logline)
