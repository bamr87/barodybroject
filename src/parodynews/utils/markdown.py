"""
File: markdown.py
Description: Markdown generation and file I/O helpers
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1
- django-markdownify: >=0.9.5

Usage: from parodynews.utils.markdown import save_markdown_file
"""

import logging
import os

from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import mark_safe
from markdownify.templatetags.markdownify import markdownify

logger = logging.getLogger(__name__)


def render_markdown(text):
    """Render Markdown to sanitized HTML. This is the app's ONE renderer.

    It delegates to `django-markdownify`'s template filter — the exact function
    the `|markdownify` filter applies in `message_detail.html`,
    `thread_detail.html`, `content_processing.html` and `pages_post_detail.html`.
    Calling it from Python rather than reimplementing it is what keeps the live
    preview byte-identical to the server-rendered page: a second renderer would
    bring a second sanitizer, and the two would eventually disagree about what
    is safe to emit. Sanitization (bleach) happens inside that filter, so
    callers must not add `|safe` on top of the result.

    Args:
        text: Markdown source. `None` and empty values render as empty.

    Returns:
        SafeString: sanitized HTML, safe to insert into a template or return
        over HTTP.
    """
    if not text:
        return mark_safe("")
    try:
        return markdownify(str(text))
    except Exception:
        # Malformed Markdown has to degrade to something readable and INERT —
        # never a traceback, never a silently blanked field. The source is
        # escaped on the way out so this fallback cannot become the injection
        # the sanitizer exists to prevent.
        logger.warning(
            "Markdown rendering failed; falling back to escaped source",
            exc_info=True,
        )
        return mark_safe(
            '<pre class="markdown-render-error">%s</pre>' % escape(str(text))
        )


def json_to_markdown(data):
    """
    Convert JSON data structure to Markdown format recursively.

    Args:
        data: JSON-compatible data structure to convert

    Returns:
        str: Formatted Markdown text
    """

    def convert_to_md(data, level=1):
        markdown = ""
        if isinstance(data, dict):
            for key, value in data.items():
                markdown += f"{'#' * level} {key}\n\n"
                markdown += convert_to_md(value, level + 1)
        elif isinstance(data, list):
            for item in data:
                markdown += f"* {convert_to_md(item, level + 1)}\n"
        else:
            markdown += f"{data}\n\n"
        return markdown

    return convert_to_md(data)


def generate_markdown_file(data, filename):
    """
    Generate a Markdown file from provided data.

    Args:
        data: Content to write to Markdown file
        filename: Name of the output Markdown file

    Returns:
        str: Full path to the generated Markdown file
    """
    file_path = os.path.join(settings.POST_DIR, filename)

    with open(file_path, "w") as file:
        file.write(data)

    return file_path
