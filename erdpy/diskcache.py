from pathlib import Path
import time
from typing import Any, Callable, Dict

from erdpy import utils, workstation


class DiskCache:
    def __init__(self, cache_name: str, max_age: int) -> None:
        self.cache_name = Path(cache_name)
        self.max_age = max_age

    def get_path(self) -> Path:
        return workstation.get_tools_folder() / f"{self.cache_name}.json"

    def get_and_cache_item(self, key: str, item_provider: Callable[[], Any]) -> Any:
        if not self.has_item(key):
            item = item_provider()
            self.save_item(key, item)
        item = self._get_cached_item(key)
        return item

    def has_item(self, key: str):
        cache = self._load_all()
        item = cache.get(key, None)
        timestamp = cache.get(f"timestamp:{key}", 0)
        age = abs(self._now() - timestamp)
        expired = age > self.max_age
        return True if item is not None and not expired else False

    def save_item(self, key: str, item: Any):
        cache = self._load_all()
        cache[key] = item
        cache[f"timestamp:{key}"] = self._now()
        self._store_all(cache)

    def _get_cached_item(self, key: str):
        return self._load_all().get(key)

    def _load_all(self) -> Dict[str, Any]:
        path = self.get_path()
        if path.exists():
            return utils.read_json_file(path)
        return dict()

    def _store_all(self, cache: Any):
        utils.write_json_file(str(self.get_path()), cache)

    def _now(self):
        return int(time.time())
