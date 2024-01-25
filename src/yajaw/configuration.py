"""
Module responsible for handling the yajaw configuration.
"""
import asyncio
import logging
import tomllib
from pathlib import Path
from typing import ClassVar

import yajaw


class _ContextFilter(logging.Filter):
    """Provides correlation id parameter for the logger"""

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
        JIRA_PAT: Personal access token used to authenticate in Jira
        JIRA_BASE_URL: Base url serving the Jira instance
        SERVER_API_V2: Path serving the rest server API version 2
        SERVER_API: Path serving the desired rest server API version
        AGILE_API_V1: Path serving the rest agile API version 1
        AGILE_API: Path serving the rest agile API version 1
        GREENHOPPER_API: Path serving the internal rest greenhopper API
        TRIES: How many time a request will be attempted before it fails
        DELAY: Number of seconds to wait before submitting the next request
        BACKOFF: Number multiplied against the delay to define its new value\
        in order to adjust the load against the Jira instance
        LOGGER: Logger instance created based on configuration settings
        SEMAPHORE: Semaphore object created based on configuration settings
        TIMEOUT: Number of seconds used to configure the semaphore timeout setting
        DEFAULT_PAGINATION: Initial dictionary with the start position and number \
        of results to be requested in paginated requests

    Raises:
        NameError: Raised when it can't update the configuration\
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
        Retrieves the specified configuration.

        Method returns the configuration setting for the provided
        section and setting

        Args:
            section (str): Section of the configuration.
            setting (str): Specific setting of the configuration under the section.

        Returns:
            Value of the configuration requested.
        """
        return YajawConfig._configuration_settings[section][setting]

    @staticmethod
    def update_configuration(
        section: str,
        setting: str,
        value: str | float | dict | logging.Logger | asyncio.BoundedSemaphore,
    ):
        """
        Update the provided configuration setting.

        Updates the configuration dictionary with the informed setting value
        using the section and setting keys and refresh the class attributes.

        Args:
            section (str): Section of the configuration.
            setting (str): Specific setting of the configuration under the section.\
            value (str | float | dict | logging.Logger | asyncio.BoundedSemaphore):\
            The setting value to be stored.

        Raises:
            NameError: Can't update the configuration using the provided section and settings.
        """
        if section in YajawConfig.__sections:
            YajawConfig._configuration_settings[section][setting] = value
            YajawConfig._set_class_variables()
        else:
            raise NameError

    @staticmethod
    def load_initial_settings():
        """
        Load settings from the configuration file.

        Yajaw settings are loaded to a dictionary in memory from a configuration file, or
        use default values if the file is missing. Jira instance and access must be updated
        if no file is found.
        """
        fname = "yajaw.toml"
        try:
            with open(Path.home() / ".yajaw" / fname, "rb") as toml:
                YajawConfig._configuration_settings = tomllib.load(toml)
        except FileNotFoundError:
            ...
        YajawConfig._configuration_settings["log"] = {}
        YajawConfig._configuration_settings["log"]["logger"] = YajawConfig._define_logger()
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
        YajawConfig._set_class_variables()

    @staticmethod
    def _define_logger() -> logging.Logger:
        """
        Configures the logging.Logger used by yajaw.

        Adjusts the logging level for some dependencies to avoid
        an excess or lack of log data from them. It congure the
        message format and logging level used by yajaw.

        Returns:
            The yajaw logging.Logger object.
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
        logger.addFilter(_ContextFilter())
        return logger

    @staticmethod
    def _set_class_variables():
        """
        Updates the class variablers with the setting from the dictionary.

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
