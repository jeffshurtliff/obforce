# -*- coding: utf-8 -*-
"""
:Module:            tests.conftest
:Synopsis:          Keeps pytest identifiers bounded before environment updates and reporting
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     27 Oct 2026
"""

from __future__ import annotations

import pytest

MAX_PARAMETER_ID_BYTES = 96
MAX_TEST_NODE_ID_BYTES = 512


def pytest_make_parametrize_id(config: pytest.Config, val: object, argname: str) -> str | None:
    """Describe large string/byte parameters without copying their contents into IDs.

    The test receives the original complete value. Pytest supplies deterministic
    suffixes when multiple parameters share the same descriptive ID.
    """
    if isinstance(val, bytes) and len(val) > MAX_PARAMETER_ID_BYTES:
        return f'bytes-length-{len(val)}'
    if isinstance(val, str) and len(val.encode('utf-8', errors='surrogatepass')) > MAX_PARAMETER_ID_BYTES:
        return f'string-length-{len(val)}'
    return None


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Refuse oversized explicit IDs before pytest sets PYTEST_CURRENT_TEST.

    Never echo the invalid identifier or payload. This conservative UTF-8 ceiling
    also stays well below Windows' UTF-16 environment-value ceiling.
    """
    excessive = sum(len(item.nodeid.encode('utf-8', errors='surrogatepass')) > MAX_TEST_NODE_ID_BYTES for item in items)
    if excessive:
        raise pytest.UsageError(
            f'Test identifier budget exceeded: {excessive} item(s) exceed {MAX_TEST_NODE_ID_BYTES} UTF-8 bytes. '
            'Use short descriptive parameter IDs; test payloads must stay in values/fixtures.'
        )
