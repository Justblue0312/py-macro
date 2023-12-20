import json
import logging
import os
from pathlib import Path
from typing import Any

from contrib.patterns import singleton
from core import LOG_DIR


class BaseLogging:
    def __init__(self, file_name: str):
        self.file_name = f"{file_name}.log"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.log_file = os.path.join(LOG_DIR, self.file_name)
        if not os.path.exists(self.log_file):
            Path(self.log_file).touch(mode=0o644, exist_ok=True)
            self._mode = "w"
        else:
            self._mode = "a"
        self.file_handler = logging.FileHandler(self.log_file)
        self.file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(levelname)s]:[%(name)s] - (%(asctime)s; %(filename)s:%(lineno)d): %(message)s"
        )
        self.file_handler.setFormatter(formatter)

        self.logger.handlers = []

    def _set_logger(self):
        with open(self.log_file, self._mode) as f:
            pass
        self.logger.addHandler(self.file_handler)

    def info(self, message: str | json.JSONEncoder | Any):
        self._set_logger()
        self.logger.info(message)

    def warning(self, message: str | json.JSONEncoder | Any):
        self._set_logger()
        self.logger.warning(message)

    def error(self, message: str | json.JSONEncoder | Any):
        self._set_logger()
        self.logger.error(message)

    def debug(self, message: str | json.JSONEncoder | Any):
        self._set_logger()
        self.logger.debug(message)


@singleton
class InitLogger:
    logger = BaseLogging("database")

    db_logger = logging.getLogger("sqlalchemy")
    db_logger.addHandler(logger.file_handler)
    db_logger.setLevel(logging.DEBUG)
