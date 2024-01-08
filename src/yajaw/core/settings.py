"""Module responsible for initializing the configuration settings."""
import asyncio
import logging

from dotenv import dotenv_values


def define_logger():
    """Configure the global settings for logging."""
    logging.getLogger("httpx").setLevel(logging.WARNING)
    msg_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=msg_format)
    return logging.getLogger(__package__)


def initialize_configuration() -> dict:
    """Creates the global configuration based on environment."""
    env_values = dotenv_values()
    return {
        "jira": {
            "pat": env_values.get("JIRA_PAT"),
            "base_url": env_values.get("JIRA_BASE_URL"),
            "server_api_v2": env_values.get("JIRA_API_V2"),
            "agile_api_v1": env_values.get("JIRA_AGILE_API_V1"),
            "greenhopper_api": env_values.get("JIRA_GREENHOPPER_API"),
        },
        "log": {"logger": define_logger()},
        "concurrency": {"semaphore": asyncio.BoundedSemaphore(100)},
    }


CONFIG = initialize_configuration()
