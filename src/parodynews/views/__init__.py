"""
File: __init__.py
Description: Server-rendered views that remain after the React migration
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2026-09-14
Version: 0.6.0

The domain UI lives in the React app under ``src/frontend`` and talks to
``parodynews.api``. Django still renders the SPA shell (``SPAView``) and the
allauth account pages.
"""

from .spa import SPAView

__all__ = ["SPAView"]
