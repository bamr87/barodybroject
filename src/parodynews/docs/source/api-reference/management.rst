===================
Management Commands
===================

Custom Django management commands.

.. currentmodule:: parodynews.management.commands

Overview
========

Parodynews provides custom management commands for:

* Data import/export
* Database operations
* Content generation
* System maintenance

Available Commands
==================

(Commands will be documented as they are discovered)

Usage
=====

Run management commands:

.. code-block:: bash

   # In development
   docker-compose -f .devcontainer/docker-compose_dev.yml exec python \\
       python manage.py <command_name>
   
   # In production
   docker-compose exec web-prod python manage.py <command_name>

See Also
========

* :doc:`../developer-guide/index` - Developer guide
* :doc:`../how-to/index` - How-to guides
