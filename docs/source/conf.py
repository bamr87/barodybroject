# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------
# Add the Django project root to the Python path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings')

# Set up environment variables for Django
os.environ.setdefault('DEBUG', 'True')
os.environ.setdefault('SECRET_KEY', 'docs-secret-key-for-sphinx')
os.environ.setdefault('DATABASE_URL', 'sqlite:///docs-temp.db')
os.environ.setdefault('CONTAINER_APP_NAME', 'docs')
os.environ.setdefault('CONTAINER_APP_ENV_DNS_SUFFIX', 'localhost')

# Try to set up Django, but continue if it fails
try:
    import django
    django.setup()
    django_available = True
except Exception as e:
    print(f"Warning: Django setup failed: {e}")
    django_available = False

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Barodybroject'
copyright = '2025, bamr87'
author = 'bamr87'
description = 'Django application integrated with OpenAI to generate content with the help of assistants'

version = '0.1.0'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
]

# Only add typehints extension if available
try:
    import sphinx_autodoc_typehints
    extensions.append('sphinx_autodoc_typehints')
except ImportError:
    pass

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'en'

# -- Autodoc configuration --------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Mock imports that might fail during documentation build
autodoc_mock_imports = [
    'azure',
    'boto3',
    'botocore',
    'django_ses',
    'openai',
    'pygithub',
]

# Generate autosummary even if no references
autosummary_generate = True
autosummary_imported_members = True

# -- Napoleon settings -------------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# -- Intersphinx configuration -----------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'django': ('https://docs.djangoproject.com/en/stable/', 'https://docs.djangoproject.com/en/stable/_objects/'),
}

# -- Todo extension ----------------------------------------------------------
todo_include_todos = True
