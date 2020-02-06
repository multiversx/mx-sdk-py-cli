import asyncio
import subprocess
import logging

logger = logging.getLogger("myprocess")


def run_process(args, env=None):
    logger.info(f"run_process: {args}")

    output = subprocess.check_output(
        args, shell=False, universal_newlines=True, stderr=subprocess.STDOUT, env=env)
    logger.info("Successful run. Output:")
    print(output or "[No output]")
    return output


def run_process_piped_output(args, env=None):
    logger.info(f"run_process_realtime_output: {args}")

    process = subprocess.Popen(args, shell=False, universal_newlines=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)

    while True:
        line = process.stdout.readline()
        if not line:
            break
        print(line.strip())


def run_process_async(args, env=None):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(_stream_subprocess(args, env))
    loop.close()
    return result


async def _stream_subprocess(args, env=None):
    process = await asyncio.create_subprocess_exec(*args, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    await asyncio.wait([
        _read_stream(process.stdout),
        _read_stream(process.stderr)
    ])
    return await process.wait()


async def _read_stream(stream):
    while True:
        line = await stream.readline()
        if line:
            print(str(line, "utf-8").strip())
        else:
            break
