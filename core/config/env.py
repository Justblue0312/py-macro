import json
import logging
import os
from typing import Any, Dict, List

from .config import STORAGE_DIR

logger = logging.getLogger(__name__)
config_path = os.path.join(STORAGE_DIR, "setup", "config.json")


class Env:
    def __init__(self) -> None:
        self.config_path = config_path
        self.data: Dict[str, Any] = self._load_config()
        if not self.data:
            raise FileNotFoundError("Config File Not Found")

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, mode="r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Config file error: {e}")
            return {}

    def get(self, key: str, default_value: Any = None) -> Any:
        return self.data.get(key, default_value)

    def set(self, key: str, value: Dict[str, Any] | List[str | int] | str | int | None):
        self.data[key] = value

    def build(self):
        with open(self.config_path, mode="w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


env = Env()
