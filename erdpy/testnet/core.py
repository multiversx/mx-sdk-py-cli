import asyncio
import logging
from pathlib import Path
import traceback
from typing import Any, Coroutine, List

from erdpy.testnet.config import TestnetConfiguration

logger = logging.getLogger("testnet")


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
    testnet_config = TestnetConfiguration.from_file(args.configfile)
    logger.info('testnet folder is %s', testnet_config.root())

    to_run: List[Coroutine[Any, Any, None]] = []

    # Seed node
    to_run.append(run(["./seednode", "--log-save"], cwd=testnet_config.seednode_folder()))

    loglevel = _patch_loglevel(testnet_config.loglevel())
    logger.info(f"loglevel: {loglevel}")

    # Observers
    for observer in testnet_config.observers():
        to_run.append(run([
            "./node",
            "--use-log-view",
            "--log-save",
            f"--log-level={loglevel}",
            "--log-logger-name",
            "--log-correlation",
            f"--destination-shard-as-observer={observer.shard}",
            f"--rest-api-interface=localhost:{observer.api_port}"
        ], cwd=observer.folder, delay=NODES_START_DELAY))

    # Validators
    for validator in testnet_config.validators():
        to_run.append(run([
            "./node",
            "--use-log-view",
            "--log-save",
            f"--log-level={loglevel}",
            "--log-logger-name",
            "--log-correlation",
            f"--rest-api-interface=localhost:{validator.api_port}"
        ], cwd=validator.folder, delay=NODES_START_DELAY))

    # Proxy
    to_run.append(run([
        "./proxy",
        "--log-save"
    ], cwd=testnet_config.proxy_folder(), delay=PROXY_START_DELAY))

    await asyncio.gather(*to_run)


async def run(args: List[str], cwd: Path, delay: int = 0):
    await asyncio.sleep(delay)

    process = await asyncio.create_subprocess_exec(*args, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE, cwd=cwd, limit=1024 * 512)

    pid = process.pid

    print(f"Started process [{pid}]", args)
    await asyncio.wait([
        _read_stream(process.stdout, pid),
        _read_stream(process.stderr, pid)
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

    if "arwen:" not in loglevel:
        loglevel += ",arwen:TRACE"
    if "process/smartcontract:" not in loglevel:
        loglevel += ",process/smartcontract:TRACE"

    return loglevel


LOGLINE_GENESIS_THRESHOLD_MARKER = "started committing block"
LOGLINE_AFTER_GENESIS_INTERESTING_MARKERS = ["started committing block", "ERROR", "WARN", "arwen", "smartcontract"]
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
