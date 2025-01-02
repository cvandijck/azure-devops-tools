import logging
from pathlib import Path
from typing import Optional

DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


class PackageFilter(logging.Filter):
    def __init__(self, package_name):
        super().__init__()
        self.package_name = package_name

    def filter(self, record):
        return record.name.startswith(self.package_name)


def configure_logging(
    level=logging.INFO,
    log_format: str = DEFAULT_LOGGING_FORMAT,
    log_file_path: Optional[Path] = None,
    exclude_external_logs: bool = False,
) -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter(log_format)

    if log_file_path:
        file_handler = logging.FileHandler(str(log_file_path))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if exclude_external_logs:
        package_name = __name__.split('.')[0]
        package_filter = PackageFilter(package_name)
        logger.addFilter(package_filter)

    return logger


def convert_logging_level(level: str) -> int:
    mapping = logging.getLevelNamesMapping()
    return mapping[level.upper()]
