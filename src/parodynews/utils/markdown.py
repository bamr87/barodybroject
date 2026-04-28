"""
File: markdown.py
Description: Markdown generation and file I/O helpers
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: from parodynews.utils.markdown import save_markdown_file
"""

import os

from django.conf import settings


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
