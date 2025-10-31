
# source Directory

## Purpose
This directory contains Sphinx documentation source files including ReStructuredText (RST) files, configuration, and Python modules for generating comprehensive API documentation. It serves as the source content for building HTML, PDF, and other documentation formats using the Sphinx documentation generator.

## Contents
- `conf.py`: Sphinx configuration file defining documentation build settings, extensions, themes, and output options
- `api.rst`: ReStructuredText file documenting the API reference with auto-generated content from Python docstrings
- `usage.rst`: ReStructuredText file containing usage instructions, tutorials, and user guides
- `views.rst`: ReStructuredText file documenting Django views and URL patterns
- `views.py`: Python module with view functions and documentation utilities
- `parortd.py`: Python module containing custom documentation tools and utilities

## Usage
Sphinx source files are processed to generate documentation:

```rst
.. Example RST syntax in api.rst
API Reference
=============

.. automodule:: parodynews.models
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: parodynews.views
   :members:
   :undoc-members:

# Example conf.py configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx'
]

html_theme = 'sphinx_rtd_theme'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True
}
```

Documentation features:
- **Auto-Documentation**: Automatic API documentation generation from Python docstrings
- **Custom Themes**: Configurable themes for professional documentation appearance  
- **Cross-References**: Internal and external documentation linking
- **Code Examples**: Syntax-highlighted code samples and examples
- **Multiple Formats**: Support for HTML, PDF, and ePub output formats
- **Search Integration**: Full-text search capabilities in generated documentation

## Container Configuration
Sphinx source files processed in documentation build environment:
- Sphinx and dependencies available in development container
- RST files compiled to HTML during documentation build process
- Generated documentation served through static web servers
- Build process integrated with CI/CD pipelines for automatic updates

## Related Paths
- Incoming: RST source files authored by developers and auto-generated from Python code
- Outgoing: Compiled into HTML, PDF, and other formats in the parent build directory
