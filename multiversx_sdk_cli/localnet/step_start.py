import asyncio
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Coroutine, List

from multiversx_sdk_cli import workstation
from multiversx_sdk_cli.localnet.config_root import ConfigRoot
from multiversx_sdk_cli.localnet.constants import \
    NETWORK_MONITORING_INTERVAL_IN_SECONDS

logger = logging.getLogger("localnet")


NODES_START_DELAY = 1
PROXY_START_DELAY = 10

is_after_genesis = False


def start(configfile: Path, stop_after_seconds: int):
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(do_start(configfile, stop_after_seconds))
        loop.close()
        asyncio.set_event_loop(asyncio.new_event_loop())
    except KeyboardInterrupt:
        pass


async def do_start(configfile: Path, stop_after_seconds: int):
    config = ConfigRoot.from_file(configfile)
    logger.info('localnet folder is %s', config.root())

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
            f"--rest-api-interface={observer.api_interface()}"
        ], cwd=observer.folder, delay=NODES_START_DELAY))

        logger.info(f"Observer: shard = {observer.shard}, API = {observer.api_address()}")

    # Validators
    for validator in config.validators():
        to_run.append(run([
            "./node",
            "--use-log-view",
            "--log-save",
            f"--log-level={loglevel}",
            "--log-logger-name",
            f"--rest-api-interface={validator.api_interface()}"
        ], cwd=validator.folder, delay=NODES_START_DELAY))

        logger.info(f"Validator: shard = {validator.shard}, API = {validator.api_address()}")

    # Proxy
    to_run.append(run([
        "./proxy",
        "--log-save"
    ], cwd=config.proxy_folder(), delay=PROXY_START_DELAY))

    logger.info(f"Proxy: API = {config.networking.get_proxy_url()}")

    # Monitor network
    to_run.append(monitor_network(stop_after_seconds))

    tasks = [asyncio.create_task(item) for item in to_run]
    await asyncio.gather(*tasks)


async def monitor_network(stop_after_seconds: int):
    loop = asyncio.get_running_loop()
    end_time = loop.time() + stop_after_seconds

    while True:
        current_loop_time = loop.time()

        if current_loop_time >= end_time:
            loop.stop()
            sys.exit(0)

        await asyncio.sleep(NETWORK_MONITORING_INTERVAL_IN_SECONDS)


async def run(args: List[str], cwd: Path, delay: int = 0):
    await asyncio.sleep(delay)

    logger.info(f"Starting process {args} in folder {cwd}")

    env = os.environ.copy()

    if workstation.is_linux():
        env["LD_LIBRARY_PATH"] = str(cwd)
    else:
        # For MacOS, libwasmer is directly found near the binary (no workaround needed)
        pass

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
