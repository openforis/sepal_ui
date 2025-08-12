"""Logging configuration for the Sepal UI project.

To use this logging configuration, set the environment variable
SEPALUI_LOG_CFG to the path of the logging configuration file.
The repo has a sample configuration file in the root directory.

"""

import logging
import logging.config
from pathlib import Path
from typing import Optional, Union

import tomli

log = logging.getLogger("sepalui")


def setup_logging(
    logger_name: str,
    config_path: Optional[Union[str, Path]] = None,
) -> logging.Logger:
    """Set up logging configuration from a TOML file and return the configured logger.

    Args:
        logger_name: Name of the logger to configure and return.
        config_path: Path to the logging configuration file.
                    Defaults to "logging_config.toml" in the caller's directory.

    Returns:
        The configured logger instance.

    If the configuration file does not exist, a NullHandler is added to the specified logger.
    If the file exists, it is loaded and the logging configuration is applied.
    """
    # Determine the configuration file path
    if config_path:
        cfg_path = Path(config_path)
    else:
        # Default to logging_config.toml in the caller's directory
        import inspect

        caller_file = Path(inspect.stack()[1].filename)
        cfg_path = caller_file.parent / "logging_config.toml"

    # Get the logger to configure
    target_log = logging.getLogger(logger_name)

    if not cfg_path.exists():
        # Remove existing handlers and add NullHandler
        for handler in target_log.handlers[:]:
            target_log.removeHandler(handler)
        target_log.addHandler(logging.NullHandler())
        return target_log

    if not cfg_path.is_file():
        raise FileNotFoundError(f"Logging config not found at {cfg_path}")

    with cfg_path.open("rb") as f:
        cfg = tomli.load(f)

    logging.config.dictConfig(cfg)

    return target_log


# Initialize sepalui logging with default behavior for backward compatibility
log = setup_logging(
    "sepalui", config_path=Path(__file__).parent.parent.parent / "logging_config.toml"
)
