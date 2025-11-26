=====
Forms
=====

Django forms for data validation and user input in Parodynews.

.. currentmodule:: parodynews.forms

.. automodule:: parodynews.forms
   :members:
   :undoc-members:
   :show-inheritance:

Overview
========

Parodynews uses Django forms for:

* Data validation
* User input handling
* Admin interface customization
* API data validation

Key Forms
=========

(Forms will be auto-documented from docstrings when built)

Usage Examples
==============

Using Forms in Views
--------------------

.. code-block:: python

   from django.views.generic import FormView
   from parodynews.forms import AssistantForm
   
   class CreateAssistantView(FormView):
       form_class = AssistantForm
       template_name = 'create_assistant.html'
       success_url = '/assistants/'
       
       def form_valid(self, form):
           form.save()
           return super().form_valid(form)

See Also
========

* :doc:`models` - Models used by forms
* :doc:`views` - Views using forms
* :doc:`../user-guide/index` - User guide
