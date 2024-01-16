# SPDX-FileCopyrightText: 2023-present rmrighes <rmrighes@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""File __init__.py responsible for enabling the import of yajaw package and
global configuration settings."""

from enum import Enum

from yajaw.configuration import YajawConfig

__all__ = ["jira", "configuration", "ApiType"]

ApiType = Enum("API", ["CLASSIC", "AGILE", "INTERNAL"])
Option = Enum("Confirmation", ["YES", "NO"])

YajawConfig.load_settings()
