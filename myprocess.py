import asyncio
import logging
import subprocess
import traceback

from erdpy import feedback, errors

logger = logging.getLogger("myprocess")


def run_process(args, env=None):
    logger.info(f"run_process: {args}")

    try:
        output = subprocess.check_output(args, shell=False, universal_newlines=True, stderr=subprocess.STDOUT, env=env)
        logger.info("Successful run. Output:")
        print(output or "[No output]")
        return output
    except subprocess.CalledProcessError as error:
        raise errors.ExternalProcessError(error.cmd, error.output)


def run_process_async(args, env=None):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(async_subprocess(args, env))
    loop.close()
    asyncio.set_event_loop(asyncio.new_event_loop())
    return result


async def async_subprocess(args, env=None, sinks=None):
    process = await asyncio.create_subprocess_exec(*args, env=env, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    await asyncio.wait([
        _read_stream(process.stdout, sinks),
        _read_stream(process.stderr, sinks)
    ])
    return await process.wait()


async def _read_stream(stream, sinks=None):
    while True:
        try:
            line = await stream.readline()
            if line:
                line = line.decode("utf-8", "replace").strip()
                if sinks is None:
                    print(line)
                else:
                    for sink in sinks:
                        feedback.get_sink(sink).write(line)
            else:
                break
        except Exception:
            print(traceback.format_exc())
