# SPDX-FileCopyrightText: 2023-present rmrighes <rmrighes@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
"""File __init__.py responsible for enabling the import of yajaw.core package."""

__all__ = ["rest", "exceptions"]

class HttpStatusCode:
    OK: int = 200
    UNAUTHORIZED: int = 401
    FORBIDDEN: int = 403
    NOT_FOUND: int = 404