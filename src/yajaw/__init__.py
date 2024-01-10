# SPDX-FileCopyrightText: 2023-present rmrighes <rmrighes@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""File __init__.py responsible for enabling the import of yajaw package and
global configuration settings."""

import asyncio
import logging
import tomllib
from pathlib import Path

__all__ = ["jira"]


def load_settings_from_file() -> dict:
    """Load configuration settings from file"""
    fname = "yajaw.toml"
    with open(Path.home() / ".yajaw" / fname, "rb") as toml:
        return tomllib.load(toml)


def define_logger(config: dict):
    """Configure the global settings for logging."""
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format=config["log"]["msg_format"])
    return logging.getLogger(__package__)


def initialize_configuration() -> dict:
    """Creates the global configuration based on environment."""
    config = load_settings_from_file()
    config["log"]["logger"] = define_logger(config)
    config["concurrency"]["semaphore"] = asyncio.BoundedSemaphore(
        config["concurrency"]["semaphore_limit"]
    )
    config["pagination"]["default"] = [
        {
            "startAt": config["pagination"]["start_at"],
            "maxResults": config["pagination"]["max_results"],
        }
    ]
    return config


CONFIG = initialize_configuration()
