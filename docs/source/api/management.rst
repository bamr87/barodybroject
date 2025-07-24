Management Commands
===================

This section documents custom Django management commands.

Available Commands
------------------

The following management commands are available in the parodynews app:

Fetch Models Command
--------------------

.. automodule:: parodynews.management.commands.fetch_models
   :members:
   :undoc-members:
   :show-inheritance:

Refresh Migrations Command
--------------------------

.. automodule:: parodynews.management.commands.refreshmigrations
   :members:
   :undoc-members:
   :show-inheritance:

Reset Database Command
----------------------

.. automodule:: parodynews.management.commands.reset_db
   :members:
   :undoc-members:
   :show-inheritance:

Generate Field Defaults Command
-------------------------------

.. automodule:: parodynews.management.commands.generate_field_defaults
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

To use these management commands:

.. code-block:: bash

   python manage.py fetch_models
   python manage.py refreshmigrations
   python manage.py reset_db
   python manage.py generate_field_defaults

Additional Information
----------------------

For more information about Django management commands, see the `Django Management Commands Documentation <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/>`_.