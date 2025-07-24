Admin Documentation
===================

This section documents the Django admin interface customizations.

.. note::
   The admin documentation is automatically generated from the Django admin configurations.

Parodynews Admin
----------------

The admin interface provides comprehensive content management capabilities.

Admin Features:

- Content creation and editing
- User management
- Import/export functionality
- Bulk operations
- Custom filters and search

Admin Files Location:
   - ``src/parodynews/admin.py``
   - ``src/parodynews/resources.py``

.. automodule:: parodynews.admin
   :members:
   :undoc-members:
   :show-inheritance:

Admin Resources
---------------

Import/export resources for data management.

.. automodule:: parodynews.resources
   :members:
   :undoc-members:
   :show-inheritance:

Admin Customizations
--------------------

**Custom Admin Classes**
   Enhanced admin interfaces with custom functionality.

**Inline Admin**
   Related model editing within parent model admin.

**List Filters**
   Custom filters for improved data navigation.

**Search Fields**
   Configured search functionality across model fields.

Additional Information
----------------------

For more information about Django admin, see the `Django Admin Documentation <https://docs.djangoproject.com/en/stable/ref/contrib/admin/>`_.