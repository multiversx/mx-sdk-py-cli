from os import path

from erdpy import workstation, errors, utils


class Sink:
    def __init__(self, name, channels=None):
        self.name = name
        self.channels = channels or []

    def write(self, text):
        for channel in self.channels:
            channel.write(text)


class OutputChannel:
    def write(self, text):
        pass

    def close(self):
        pass


class ConsoleChannel(OutputChannel):
    def write(self, text):
        print(text)


class FileChannel(OutputChannel):
    def __init__(self, name):
        directory = path.join(workstation.get_tools_folder(), "OutputChannels")
        utils.ensure_folder(directory)
        filepath = path.join(directory, f"{name}.txt")
        self.file = open(filepath, "a")

    def write(self, text):
        self.file.write(text)
        self.file.write("\n")

    def close(self):
        self.file.close()


__sinks = {
    "llvm": Sink("llvm", channels=[FileChannel("llvm")])
}


def get_sink(name):
    sink = __sinks.get(name)
    if sink is None:
        raise errors.BadSink(name)
    return sink
