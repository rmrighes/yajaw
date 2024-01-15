"""TBD"""
import asyncio
import logging
import tomllib
from pathlib import Path

import yajaw

MIN_SEMAPHORE_LIMIT = 5


def _load_settings() -> dict:
    """Load configuration settings from file"""
    fname = "yajaw.toml"
    try:
        with open(Path.home() / ".yajaw" / fname, "rb") as toml:
            return tomllib.load(toml)
    except FileNotFoundError:
        return _load_default_settings()


def _load_default_settings() -> dict:
    """TBD"""
    toml_str = """
        [jira]
        token = "AAA..."
        base_url = "https://my-dummy-jira-url.com"
        server_api_v2 = "rest/api/2"
        agile_api_v1 = "rest/agile/1.0"
        greenhopper_api = "rest/greenhopper/1.0"
        [log]
        msg_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        [retries]
        tries = 10
        delay = 0.0
        backoff = 2
        [requests]
        timeout = 60
        [concurrency]
        semaphore_limit = 50
        [pagination]
        page_results = 40
    """
    return tomllib.loads(toml_str)


def _define_logger(config: dict):
    """Configure the global settings for logging."""
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO, format=config["log"]["msg_format"])
    return logging.getLogger(__package__)


def initialize_configuration() -> dict:
    """Creates the global configuration based on environment."""
    config = _load_settings()
    config["log"]["logger"] = _define_logger(config)
    limit = config["concurrency"]["semaphore_limit"]
    # Ensures a minimum value of 5 for the BoundedSemaphore
    semaphore_limit = limit if limit > MIN_SEMAPHORE_LIMIT else MIN_SEMAPHORE_LIMIT
    config["concurrency"]["semaphore"] = asyncio.BoundedSemaphore(semaphore_limit)
    config["pagination"]["default"] = {
        "startAt": 0,
        "maxResults": config["pagination"]["page_results"],
    }
    return config


# Override Jira connection configurations


def set_user_token(token: str) -> None:
    """TBD"""
    yajaw.JIRA_PAT = token


def set_jira_base_url(base_url: str) -> None:
    """TBD"""
    yajaw.JIRA_BASE_URL = base_url
