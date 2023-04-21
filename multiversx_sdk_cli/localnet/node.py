from pathlib import Path


class Node:
    def __init__(self, index: int, folder: Path, shard: str, api_port: int) -> None:
        self.index = index
        self.folder = folder
        self.shard = shard
        self.api_port = api_port

    def key_file_path(self):
        return self.folder / "config" / "validatorKey.pem"

    def api_address(self):
        return f"http://{self.api_interface()}"

    def api_interface(self):
        return f"localhost:{self.api_port}"

    def __repr__(self) -> str:
        return f"Node {self.index}, shard={self.shard}, port={self.api_port}, folder={self.folder}"


class NodeStatus:
    def __init__(self, nonce: int) -> None:
        self.nonce = nonce
