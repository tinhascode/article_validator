import logging
from typing import Optional


class LoggerConfig:
    def __init__(
        self, level: int = logging.INFO, handler: Optional[logging.Handler] = None
    ):
        self.level = level
        if handler is None:
            handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(formatter)
        handler.setLevel(level)
        self.handler = handler
        self._configured = False

    def configure_root(self) -> None:
        root = logging.getLogger()
        if not self._configured:
            for h in list(root.handlers):
                root.removeHandler(h)
            root.setLevel(self.level)
            root.addHandler(self.handler)
            self._configured = True

    def get_logger(self, name: str):
        self.configure_root()
        logger = logging.getLogger(name)
        logger.setLevel(self.level)
        return logger


_default_config = LoggerConfig()


def get_logger(name: str):
    return _default_config.get_logger(name)
