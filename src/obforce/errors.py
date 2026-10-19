# -*- coding: utf-8 -*-
"""
:Module:            obforce.errors
:Synopsis:          Defines typed failures and terminal outcome precedence
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     19 Oct 2026
"""

from __future__ import annotations

from collections.abc import Iterable
from enum import IntEnum

import click


class ExitCode(IntEnum):
    """Represent the version-one terminal outcomes, independent of their precedence."""

    SUCCESS = 0
    OPERATIONAL = 1
    INVALID = 2
    CONFLICT = 3
    INCOMPLETE = 4


class OperationalError(click.ClickException):
    """Report a safe, caller-supplied operational diagnostic without raw input data."""

    exit_code = ExitCode.OPERATIONAL


class ConfigError(OperationalError):
    """Reject invalid explicit configuration without discovering a fallback."""

    exit_code = ExitCode.INVALID


class ModelError(ConfigError):
    """Reject malformed normalized records before dependent processing."""


class ConflictError(OperationalError):
    """Refuse ambiguous identity, ownership, or recovery-required state."""

    exit_code = ExitCode.CONFLICT


class CoverageError(OperationalError):
    """Report a completed operation whose requested coverage is incomplete."""

    exit_code = ExitCode.INCOMPLETE


def exit_code(outcomes: Iterable[ExitCode]) -> ExitCode:
    """Select conflict, invalid, operational, incomplete, then success, in that order.

    :param outcomes: Collected typed outcomes; an empty collection means success.
    :returns: Highest-precedence outcome, not the greatest numeric value.
    :raises ValueError: If an outcome is not a recognized code.
    """
    codes = {ExitCode(value) for value in outcomes}
    return next(
        (code for code in (ExitCode.CONFLICT, ExitCode.INVALID, ExitCode.OPERATIONAL, ExitCode.INCOMPLETE) if code in codes),
        ExitCode.SUCCESS,
    )
