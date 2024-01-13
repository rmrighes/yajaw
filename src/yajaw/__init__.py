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

SEM_LIMIT = 5

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
    limit = config["concurrency"]["semaphore_limit"]
    # Ensures a minimum value of 5 for the BoundedSemaphore
    semaphore_limit = limit if limit > SEM_LIMIT else SEM_LIMIT
    config["concurrency"]["semaphore"] = asyncio.BoundedSemaphore(semaphore_limit)
    config["pagination"]["default"] = {
        "startAt": 0,
        "maxResults": config["pagination"]["page_results"],
    }
    return config


CONFIG = initialize_configuration()

TRIES = CONFIG["retries"]["tries"]
DELAY = CONFIG["retries"]["delay"]
BACKOFF = CONFIG["retries"]["backoff"]
LOGGER = CONFIG["log"]["logger"]
SEMAPHORE = CONFIG["concurrency"]["semaphore"]
JIRA_PAT = CONFIG["jira"]["token"]
JIRA_BASE_URL = CONFIG["jira"]["base_url"]
SERVER_API = CONFIG["jira"]["server_api_v2"]
AGILE_API = CONFIG["jira"]["agile_api_v1"]
GREENHOPPER_API = CONFIG["jira"]["greenhopper_api"]
DEFAULT_PAGINATION = CONFIG["pagination"]["default"]
TIMEOUT = CONFIG["requests"]["timeout"]
