"""TBD"""
import asyncio
import logging
import tomllib
from pathlib import Path
from typing import ClassVar


class YajawConfig:
    """TBD"""

    JIRA_PAT: str
    JIRA_BASE_URL: str
    SERVER_API_V2: str
    SERVER_API: str
    AGILE_API_V1: str
    AGILE_API: str
    GREENHOPPER_API: str
    TRIES: int
    DELAY: float
    BACKOFF: float
    LOGGER: logging.Logger
    SEMAPHORE: asyncio.BoundedSemaphore
    TIMEOUT: int
    DEFAULT_PAGINATION: dict

    _MIN_SEMAPHORE_LIMIT: int = 5

    __conf: ClassVar = {
        "jira": {
            "token": "AAA...",
            "base_url": "https://my-dummy-jira-url.com",
            "server_api_v2": "rest/api/2",
            "agile_api_v1": "rest/agile/1.0",
            "greenhopper_api": "rest/greenhopper/1.0",
        },
        "log": {"msg_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        "retries": {"tries": 10, "delay": 0.0, "backoff": 2},
        "requests": {"timeout": 60},
        "concurrency": {"semaphore_limit": 50},
        "pagination": {"page_results": 40},
    }

    __sections: ClassVar = ["jira", "log", "retries", "requests", "concurrency"]

    @staticmethod
    def configuration(section, setting):
        """TBD"""
        return YajawConfig.__conf[section][setting]

    @staticmethod
    def update_configuration(section, setting, value):
        """TBD"""
        if section in YajawConfig.__sections:
            YajawConfig.__conf[section][setting] = value
        else:
            raise NameError

    @staticmethod
    def load_settings():
        """Load configuration settings from file"""
        fname = "yajaw.toml"
        try:
            with open(Path.home() / ".yajaw" / fname, "rb") as toml:
                YajawConfig.__conf = tomllib.load(toml)
        except FileNotFoundError:
            ...
        YajawConfig.__conf["log"]["logger"] = YajawConfig.define_logger()
        limit = YajawConfig.__conf["concurrency"]["semaphore_limit"]
        # Ensures da minimum value of 5 for the BoundedSemaphore
        semaphore_limit = (
            limit if limit > YajawConfig._MIN_SEMAPHORE_LIMIT else YajawConfig._MIN_SEMAPHORE_LIMIT
        )
        YajawConfig.__conf["concurrency"]["semaphore"] = asyncio.BoundedSemaphore(semaphore_limit)
        YajawConfig.__conf["pagination"]["default"] = {
            "startAt": 0,
            "maxResults": YajawConfig.__conf["pagination"]["page_results"],
        }
        YajawConfig.set_class_variables()

    @staticmethod
    def define_logger():
        """Configure the global settings for logging."""
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.basicConfig(level=logging.INFO, format=YajawConfig.__conf["log"]["msg_format"])
        return logging.getLogger(__package__)

    @staticmethod
    def set_class_variables():
        """TBD"""
        YajawConfig.JIRA_PAT = YajawConfig.__conf["jira"]["token"]
        YajawConfig.JIRA_BASE_URL = YajawConfig.__conf["jira"]["base_url"]
        YajawConfig.SERVER_API_V2 = YajawConfig.__conf["jira"]["server_api_v2"]
        YajawConfig.SERVER_API = YajawConfig.SERVER_API_V2
        YajawConfig.AGILE_API_V1 = YajawConfig.__conf["jira"]["agile_api_v1"]
        YajawConfig.AGILE_API = YajawConfig.AGILE_API_V1
        YajawConfig.GREENHOPPER_API = YajawConfig.__conf["jira"]["greenhopper_api"]
        YajawConfig.TRIES = YajawConfig.__conf["retries"]["tries"]
        YajawConfig.DELAY = YajawConfig.__conf["retries"]["delay"]
        YajawConfig.BACKOFF = YajawConfig.__conf["retries"]["backoff"]
        YajawConfig.LOGGER = YajawConfig.__conf["log"]["logger"]
        YajawConfig.SEMAPHORE = YajawConfig.__conf["concurrency"]["semaphore"]
        YajawConfig.TIMEOUT = YajawConfig.__conf["requests"]["timeout"]
        YajawConfig.DEFAULT_PAGINATION = YajawConfig.__conf["pagination"]["default"]
