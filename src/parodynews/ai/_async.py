"""
File: _async.py
Description: Run a coroutine to completion from synchronous Django code
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage: from parodynews.ai._async import run_sync
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from concurrent.futures import ThreadPoolExecutor
from typing import Any, TypeVar

T = TypeVar("T")


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Block on ``coro`` whether or not an event loop is already running.

    Django views are synchronous, so ``asyncio.run`` is normally enough. Under
    ASGI (or inside a test that already owns a loop) a loop *is* running, and
    ``asyncio.run`` would raise; in that case the coroutine is driven on a
    fresh loop in a worker thread instead.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(asyncio.run, coro).result()
