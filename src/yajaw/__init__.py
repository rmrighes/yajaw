# SPDX-FileCopyrightText: 2023-present rmrighes <rmrighes@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""
Module responsible for the initialization of configuration settings.
There's no need to import it directly.
"""

import sys
import uuid
from contextvars import ContextVar
from enum import Enum

from yajaw import __about__ as about
from yajaw.configuration import YajawConfig

__all__ = ["jira", "configuration", "exceptions", "ApiType"]


ApiType = Enum("API", ["CLASSIC", "AGILE", "INTERNAL"])
Option = Enum("Confirmation", ["YES", "NO"])

YajawConfig.load_initial_settings()

correlation_id: ContextVar[uuid.UUID] = ContextVar(
    "correlation_id", default=uuid.UUID("00000000-0000-0000-0000-000000000000")
)

correlation_id.set(uuid.uuid4())

YajawConfig.LOGGER.info(
    f"Inititalized {__package__} successfully.\n"
    f"\tPython {sys.version}\n"
    f"\t{__package__} {about.__version__}"
)
