"""
Sphinx configuration for Parodynews documentation.

This configuration enables comprehensive documentation generation for the
Django-based parody news generator application with OpenAI integration.

Author: Barodybroject Team
Created: 2025-11-25
Last Modified: 2025-11-25
Version: 2.0.0
"""

import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parents[3].resolve()
sys.path.insert(0, str(project_root / 'src'))

# Configure Django settings for autodoc
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings')
try:
    django.setup()
except Exception as e:
    print(f"Warning: Could not setup Django: {e}")

# -- Project information -----------------------------------------------------
project = 'Parodynews'
copyright = '2025, Barodybroject Team'
author = 'Barodybroject Team'
release = '2.0.0'
version = '2.0'

# -- General configuration ---------------------------------------------------
extensions = [
    # Core Sphinx extensions
    'sphinx.ext.autodoc',           # Auto-generate docs from docstrings
    'sphinx.ext.autosummary',       # Generate summary tables
    'sphinx.ext.napoleon',          # Google/NumPy docstring support
    'sphinx.ext.viewcode',          # Add source code links
    'sphinx.ext.intersphinx',       # Link to other documentation
    'sphinx.ext.todo',              # TODO directive support
    'sphinx.ext.coverage',          # Documentation coverage checking
    'sphinx.ext.doctest',           # Test code examples
    'sphinx.ext.duration',          # Build time measurement
    'sphinx.ext.githubpages',       # GitHub Pages integration
]

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = False

# Napoleon settings (Google/NumPy docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
autodoc_typehints = 'description'
autodoc_typehints_format = 'short'

# Intersphinx mapping (link to other docs)
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 
               'https://docs.djangoproject.com/en/stable/_objects/'),
}

# Templates and static files
templates_path = ['_templates']
html_static_path = ['_static']
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    '**.ipynb_checkpoints',
]

# Source file settings
source_suffix = {
    '.rst': 'restructuredtext',
}
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

html_context = {
    'display_github': True,
    'github_user': 'bamr87',
    'github_repo': 'barodybroject',
    'github_version': 'main',
    'conf_py_path': '/src/parodynews/docs/source/',
}

html_show_sourcelink = True
html_show_sphinx = False
html_show_copyright = True

# -- Options for LaTeX/PDF output --------------------------------------------
latex_engine = 'pdflatex'
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
}
latex_documents = [
    (master_doc, 'parodynews.tex', 'Parodynews Documentation',
     'Barodybroject Team', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc, 'parodynews', 'Parodynews Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (master_doc, 'parodynews', 'Parodynews Documentation',
     author, 'parodynews', 'AI-powered parody news generator.',
     'Miscellaneous'),
]

# -- Options for EPUB output -------------------------------------------------
epub_show_urls = 'footnote'
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# -- Extension configuration -------------------------------------------------

# TODO extension
todo_include_todos = True
todo_emit_warnings = False
