"""Logging configuration for the Sepal UI project.

To use this logging configuration, set the environment variable
SEPALUI_LOG_CFG to the path of the logging configuration file.
The repo has a sample configuration file in the root directory.

"""

import logging
import logging.config
import os
from pathlib import Path

import tomli

log = logging.getLogger("sepalui")


def setup_logging():
    """Set up logging configuration from a TOML file.

    The configuration file path can be set using the SEPALUI_LOG_CFG environment variable.
    If the file does not exist, a NullHandler is added to the log
    If the file exists, it is loaded and the logging configuration is applied.
    """
    cfg_path = (
        os.getenv("SEPALUI_LOG_CFG") or Path(__file__).parent.parent.parent / "logging_config.toml"
    )

    cfg_path = Path(cfg_path)

    if not cfg_path.exists():
        for handler in log.handlers[:]:
            log.removeHandler(handler)
        log.addHandler(logging.NullHandler())
        return

    if not cfg_path.is_file():
        raise FileNotFoundError(f"Logging config not found at {cfg_path}")

    with cfg_path.open("rb") as f:
        cfg = tomli.load(f)

    logging.config.dictConfig(cfg)


setup_logging()
