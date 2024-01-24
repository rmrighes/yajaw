"""
Module responsible for handling the yajaw configuration.
"""
import asyncio
import logging
import tomllib
from pathlib import Path
from typing import ClassVar

import yajaw


class ContextFilter(logging.Filter):
    """ "Provides correlation id parameter for the logger"""

    def filter(self, record):
        record.correlation_id = yajaw.correlation_id.get()
        return True


class YajawConfig:
    """
     Class representing the configuration used by yajaw.

    It defines a series of class attributes representing the
    configuration settings used by yajaw. It also provides
    the basic load and update configuration settings methods.

    Attributes:
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

    Raises:
        NameError: Raised when it can't update the configuration
        using the provided section and settings.
    """

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

    _configuration_settings: ClassVar = {
        "jira": {
            "token": "AAA...",
            "base_url": "https://my-dummy-jira-url.com",
            "server_api_v2": "rest/api/2",
            "agile_api_v1": "rest/agile/1.0",
            "greenhopper_api": "rest/greenhopper/1.0",
        },
        "retries": {"tries": 10, "delay": 0.0, "backoff": 2},
        "requests": {"timeout": 60},
        "concurrency": {"semaphore_limit": 50},
        "pagination": {"page_results": 40},
    }

    __sections: ClassVar = ["jira", "log", "retries", "requests", "concurrency"]

    @staticmethod
    def configuration(
        section: str, setting: str
    ) -> str | float | dict | logging.Logger | asyncio.BoundedSemaphore:
        """
        configuration Retrieves the specified configuration.

        Method returns the configuration setting for the provided
        section and setting

        Args:
            section (str): Section of the configuration.
            setting (str): Specific setting of the configuration under the section.

        Returns:
            str | float | dict | logging.Logger | asyncio.BoundedSemaphore:
            The configuration requested.
        """
        return YajawConfig._configuration_settings[section][setting]

    @staticmethod
    def update_configuration(
        section: str,
        setting: str,
        value: str | float | dict | logging.Logger | asyncio.BoundedSemaphore,
    ):
        """
        update_configuration Save the provided setting to the configuration dictionary.

        Method updates the configuration dictionary with the informed setting value
        using the section and setting keys.

        Args:
            section (str): Section of the configuration.
            setting (str): Specific setting of the configuration under the section.
            value (str | float | dict | logging.Logger | asyncio.BoundedSemaphore):
            The setting value to be stored.

        Raises:
            NameError: _description_
        """
        if section in YajawConfig.__sections:
            YajawConfig._configuration_settings[section][setting] = value
        else:
            raise NameError

    @staticmethod
    def load_settings():
        """
        load_settings Load settings from the configuration file.

        Yajaw settings are loaded to a dictionary in memory from a configuration file, or
        default values if the file is missing.
        """
        fname = "yajaw.toml"
        try:
            with open(Path.home() / ".yajaw" / fname, "rb") as toml:
                YajawConfig._configuration_settings = tomllib.load(toml)
        except FileNotFoundError:
            ...
        YajawConfig._configuration_settings["log"] = {}
        YajawConfig._configuration_settings["log"]["logger"] = YajawConfig.define_logger()
        limit = YajawConfig._configuration_settings["concurrency"]["semaphore_limit"]
        # Ensures da minimum value of 5 for the BoundedSemaphore
        semaphore_limit = (
            limit if limit > YajawConfig._MIN_SEMAPHORE_LIMIT else YajawConfig._MIN_SEMAPHORE_LIMIT
        )
        YajawConfig._configuration_settings["concurrency"]["semaphore"] = asyncio.BoundedSemaphore(
            semaphore_limit
        )
        YajawConfig._configuration_settings["pagination"]["default"] = {
            "startAt": 0,
            "maxResults": YajawConfig._configuration_settings["pagination"]["page_results"],
        }
        YajawConfig.set_class_variables()

    @staticmethod
    def define_logger() -> logging.Logger:
        """
        define_logger Configures the logging.Logger used by yajaw.

        Adjusts the logging level for some dependencies to avoid
        an excess or lack of log data from them. It congure the
        message format and logging level used by yajaw.

        Returns:
            logging.Logger: The yajaw logging.Logger object.
        """
        logging.getLogger("httpx").setLevel(logging.WARNING)

        logger = logging.getLogger(__package__)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)-27s %(name)-8s %(levelname)-8s [ %(correlation_id)s ] %(message)s"
        )
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        logger.addFilter(ContextFilter())
        return logger

    @staticmethod
    def set_class_variables():
        """
        set_class_variables Updates the class variablers with the setting from the dictionary.

        Yajaw settings are loaded to a dictionary in memory from a configuration file, or
        default values if the file is missing. The method takes the content from the
        dictionary and updates the class variables accordingly.
        """
        YajawConfig.JIRA_PAT = YajawConfig._configuration_settings["jira"]["token"]
        YajawConfig.JIRA_BASE_URL = YajawConfig._configuration_settings["jira"]["base_url"]
        YajawConfig.SERVER_API_V2 = YajawConfig._configuration_settings["jira"]["server_api_v2"]
        YajawConfig.SERVER_API = YajawConfig.SERVER_API_V2
        YajawConfig.AGILE_API_V1 = YajawConfig._configuration_settings["jira"]["agile_api_v1"]
        YajawConfig.AGILE_API = YajawConfig.AGILE_API_V1
        YajawConfig.GREENHOPPER_API = YajawConfig._configuration_settings["jira"]["greenhopper_api"]
        YajawConfig.TRIES = YajawConfig._configuration_settings["retries"]["tries"]
        YajawConfig.DELAY = YajawConfig._configuration_settings["retries"]["delay"]
        YajawConfig.BACKOFF = YajawConfig._configuration_settings["retries"]["backoff"]
        YajawConfig.LOGGER = YajawConfig._configuration_settings["log"]["logger"]
        YajawConfig.SEMAPHORE = YajawConfig._configuration_settings["concurrency"]["semaphore"]
        YajawConfig.TIMEOUT = YajawConfig._configuration_settings["requests"]["timeout"]
        YajawConfig.DEFAULT_PAGINATION = YajawConfig._configuration_settings["pagination"][
            "default"
        ]
