Contributing
============

We welcome contributions to Barodybroject! This guide will help you get started.

Getting Started
---------------

1. **Fork the Repository**
   
   Fork the project on GitHub and clone your fork locally.

2. **Set Up Development Environment**
   
   Follow the installation guide to set up your development environment.

3. **Create a Feature Branch**
   
   .. code-block:: bash
   
      git checkout -b feature/your-feature-name

Development Guidelines
----------------------

Code Style
~~~~~~~~~~

- Follow PEP 8 for Python code style
- Use 4 spaces for indentation in Python files
- Use tabs for indentation in other files (following VS Code guidelines)
- Use double quotes for user-facing strings that need localization
- Use single quotes for other strings

Naming Conventions
~~~~~~~~~~~~~~~~~~

- Use PascalCase for type names
- Use PascalCase for enum values
- Use camelCase for function and method names
- Use camelCase for property names and local variables
- Use whole words in names when possible

Django Best Practices
~~~~~~~~~~~~~~~~~~~~~

- Follow Django best practices for models, views, and templates
- Keep imports grouped and organized: stdlib, third-party, then local apps
- Prefer function-based or class-based views consistently
- Limit model methods to logic directly related to that model's data

Testing
-------

Writing Tests
~~~~~~~~~~~~~

- Write tests for all new functionality
- Use pytest-django for testing
- Place tests in appropriate test files or test directories
- Follow the AAA pattern: Arrange, Act, Assert

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   python -m pytest
   
   # Run specific test file
   python -m pytest parodynews/tests/test_models.py
   
   # Run with coverage
   python -m pytest --cov=parodynews

Code Quality
------------

Linting
~~~~~~~

Use Ruff for code linting:

.. code-block:: bash

   ruff check .
   ruff format .

Type Checking
~~~~~~~~~~~~~

While not strictly enforced, type hints are encouraged:

.. code-block:: python

   def process_content(content: str) -> dict:
       """Process content and return metadata."""
       return {"length": len(content)}

Documentation
~~~~~~~~~~~~~

- Document all public APIs using docstrings
- Use Google-style docstrings
- Update Sphinx documentation for new features
- Include code examples where appropriate

Submitting Changes
------------------

1. **Ensure Tests Pass**
   
   Run the full test suite and ensure all tests pass.

2. **Update Documentation**
   
   Update relevant documentation for your changes.

3. **Commit Messages**
   
   Write clear, descriptive commit messages:
   
   .. code-block::
   
      feat: add user profile management
      
      - Add UserProfile model
      - Create profile edit view
      - Add profile templates
      - Update user admin interface

4. **Create Pull Request**
   
   - Create a pull request against the main branch
   - Include a clear description of your changes
   - Reference any related issues
   - Ensure CI checks pass

Code Review Process
-------------------

All contributions go through code review:

1. **Automated Checks**
   
   - Tests must pass
   - Code style checks must pass
   - No security vulnerabilities

2. **Manual Review**
   
   - Code quality and maintainability
   - Documentation completeness
   - Test coverage

3. **Feedback and Iteration**
   
   - Address reviewer feedback
   - Make requested changes
   - Update tests and documentation as needed

Release Process
---------------

Releases follow semantic versioning (SemVer):

- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes, backward compatible

Bug Reports
-----------

When reporting bugs, please include:

- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Relevant log output or error messages

Feature Requests
----------------

For feature requests:

- Describe the problem you're trying to solve
- Explain why this feature would be useful
- Provide examples of how it would be used
- Consider implementation challenges

Community
---------

- Be respectful and inclusive
- Follow the code of conduct
- Help others in discussions
- Share knowledge and best practices

Getting Help
------------

If you need help:

- Check the documentation
- Search existing issues
- Ask in discussions
- Contact maintainers

Thank you for contributing to Barodybroject!