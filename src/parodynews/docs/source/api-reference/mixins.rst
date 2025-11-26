======
Mixins
======

Reusable mixin classes for views and models.

.. currentmodule:: parodynews.mixins

.. automodule:: parodynews.mixins
   :members:
   :undoc-members:
   :show-inheritance:

Overview
========

Mixins provide reusable functionality that can be added to views and models.

Usage Examples
==============

Using View Mixins
-----------------

.. code-block:: python

   from django.views.generic import ListView
   from parodynews.mixins import CustomMixin
   
   class MyView(CustomMixin, ListView):
       model = MyModel

See Also
========

* :doc:`views` - Views using mixins
* :doc:`models` - Models with mixins
