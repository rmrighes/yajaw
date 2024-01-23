# SPDX-FileCopyrightText: 2023-present rmrighes <rmrighes@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""
Module responsible for the initialization of configuration settings.
There's no need to import it directly.
"""

from enum import Enum

from yajaw.configuration import YajawConfig

__all__ = ["jira", "configuration", "exceptions", "ApiType"]

ApiType = Enum("API", ["CLASSIC", "AGILE", "INTERNAL"])
Option = Enum("Confirmation", ["YES", "NO"])

YajawConfig.load_settings()
