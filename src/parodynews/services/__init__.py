"""
File: __init__.py
Description: Application workflows built on the provider-agnostic AI layer
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage:
    from parodynews.services import content, threads, publishing, assistants

The services own every multi-step workflow (generate an article, run an
assistant on a thread, turn a message into a post, push a post to GitHub).
Views stay thin and providers stay dumb.
"""

from . import assistants, content, publishing, threads

__all__ = ["assistants", "content", "publishing", "threads"]
