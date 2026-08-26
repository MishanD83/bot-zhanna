"""Общие фикстуры для pytest."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
