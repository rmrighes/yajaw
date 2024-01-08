"""Module responsible for initializing the configuration settings."""
import asyncio
import logging
import tomllib
from pathlib import Path


def load_settings_from_file() -> dict:
    """Load configuration settings from file"""
    fname = "yajaw.toml"
    with open(Path.home() / ".yajaw" / fname, "rb") as toml:
        config = tomllib.load(toml)
    return config


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
    return config


CONFIG = initialize_configuration()
