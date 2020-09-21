import asyncio
import logging
import traceback
from typing import Any

from erdpy.testnet.config import TestnetConfiguration

logger = logging.getLogger("testnet")


def start(args: Any):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do_start(args))
    loop.close()
    asyncio.set_event_loop(asyncio.new_event_loop())


async def do_start(args: Any):
    testnet_config = TestnetConfiguration.from_file(args.configfile)
    logger.info('testnet folder is %s', testnet_config.root())

    to_run = []

    # Seed node
    to_run.append(run(["./seednode", "--log-save"], cwd=testnet_config.seednode_folder()))

    # Observers
    for observer in testnet_config.observers():
        to_run.append(run([
            "./node",
            "--use-log-view",
            "--log-save",
            "--log-level=*:DEBUG",
            "--log-logger-name",
            "--log-correlation",
            f"--destination-shard-as-observer={observer.shard}",
            f"--rest-api-interface=localhost:{observer.api_port}"
        ], cwd=observer.folder, delay=5))

    # Validators
    for validator in testnet_config.validators():
        to_run.append(run([
            "./node",
            "--use-log-view",
            "--log-save",
            "--log-level=*:DEBUG",
            "--log-logger-name",
            "--log-correlation",
            f"--rest-api-interface=localhost:{validator.api_port}"
        ], cwd=validator.folder, delay=5))

    # Proxy
    to_run.append(run([
        "./proxy",
    ], cwd=testnet_config.proxy_folder(), delay=50))

    await asyncio.gather(*to_run)


async def run(args, env=None, cwd: str = None, delay: int = 0):
    await asyncio.sleep(delay)

    process = await asyncio.create_subprocess_exec(*args, env=env, stdout=asyncio.subprocess.PIPE,
                                                   stderr=asyncio.subprocess.PIPE, cwd=cwd)

    pid = process.pid

    print(f"Started process [{pid}]", args)
    await asyncio.wait([
        _read_stream(process.stdout, pid),
        _read_stream(process.stderr, pid)
    ])

    return_code = await process.wait()
    print(f"Proces [{pid}] stopped. Return code: {return_code}.")


async def _read_stream(stream, pid):
    markers_of_interest = ["started committing block", "ERROR", "WARN"]
    while True:
        try:
            line = await stream.readline()
            if line:
                line = line.decode("utf-8", "replace").strip()
                if any(e in line for e in markers_of_interest):
                    print(f"[PID={pid}]", line)
            else:
                break
        except Exception:
            print(traceback.format_exc())
