# SPDX-FileCopyrightText: 2023-present rmrighes <rmrighes@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""File __init__.py responsible for enabling the import of yajaw package and
global configuration settings."""
from enum import Enum

from yajaw import configuration

__all__ = ["jira", "configuration", "ApiType"]

ApiType = Enum("API", ["CLASSIC", "AGILE", "INTERNAL"])

app_config = configuration.initialize_configuration()

TRIES = app_config["retries"]["tries"]
DELAY = app_config["retries"]["delay"]
BACKOFF = app_config["retries"]["backoff"]
LOGGER = app_config["log"]["logger"]
SEMAPHORE = app_config["concurrency"]["semaphore"]
JIRA_PAT = app_config["jira"]["token"]
JIRA_BASE_URL = app_config["jira"]["base_url"]
SERVER_API = app_config["jira"]["server_api_v2"]
AGILE_API = app_config["jira"]["agile_api_v1"]
GREENHOPPER_API = app_config["jira"]["greenhopper_api"]
DEFAULT_PAGINATION = app_config["pagination"]["default"]
TIMEOUT = app_config["requests"]["timeout"]
