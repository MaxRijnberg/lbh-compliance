from lbh_compliance.config.settings import LOG_DIR

from typing import Literal

import logging
import datetime as dt


def get_logger(
    name: str,
    logging_level_str: Literal["debug", "info", "warn", "error", "critical"] = "info",
) -> logging.Logger:
    logger = logging.getLogger(name)

    logging_dict = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    if not (logging_level_int := logging_dict.get(logging_level_str.lower())):
        raise ValueError(
            f'Expected "logging_level_str" to be any of {logging_dict.keys()}, got "{logging_level_str}" instead'
        )

    if not logger.handlers:
        # Add formatting and config basic level
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        logger.setLevel(logging_level_int)

        # Add FileHandler
        fhandler = logging.FileHandler(LOG_DIR / f"{dt.date.today()}.log")
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)

        # Add StreamHandler
        shandler = logging.StreamHandler()
        shandler.setFormatter(formatter)
        logger.addHandler(shandler)

        # Initial message
        logger.log(logging_level_int, f"Logging level set to {logging_level_str}")

    return logger
