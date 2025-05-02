"""Custom logger with colored output for SEPAL-UI."""

import logging
import sys
from pathlib import Path

import colorlog

# ANSI background color codes
BLUE_BG = "\033[44m"
PURPLE_BG = "\033[45m"
YELLOW_BG = "\033[43m"
RESET = "\033[0m"


class CustomLogger:
    def __init__(
        self,
        name: str,
        level: int = logging.DEBUG,
        module_color: str = BLUE_BG,
        log_file: str | Path | None = None,
    ):
        """Initialize a custom logger with colored output.

        Args:
            name: The name of the logger, will be displayed on each log message.
            level: The logging level.
            module_color: The background color of the module name.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        format_str = f"%(log_color)s%(asctime)s - {module_color}%(name)s{RESET} - %(levelname)s - %(message)s"
        console_formatter = colorlog.ColoredFormatter(
            format_str,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Add file handler if log_file is specified
        if log_file:
            log_file = Path(log_file)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

    def message_to_string(self, *messages: str) -> str:
        """Convert a list of messages to a single string."""
        return " ".join(str(msg) for msg in messages)

    def debug(self, *messages: str):
        """Log a debug."""
        self.logger.debug(self.message_to_string(*messages))

    def info(self, *messages: str):
        """Logs out an infomessage."""
        self.logger.info(self.message_to_string(*messages))

    def warning(self, *messages: str):
        """Logs out a warning."""
        self.logger.warning(self.message_to_string(*messages))

    def error(self, *messages: str):
        """Logs out an error."""
        self.logger.error(self.message_to_string(*messages))

    def critical(self, *messages: str):
        """Logs out a critical error."""
        self.logger.critical(self.message_to_string(*messages))


logger = CustomLogger("SEPAL-UI", module_color=YELLOW_BG)
