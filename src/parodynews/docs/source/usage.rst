Usage
=====

.. _installation:

Installation
------------

To use parortd, first install it using pip:

.. code-block:: console

   (.venv) $ pip install parortd

Creating recipes
----------------

To retrieve a list of random ingredients,
you can use the ``parortd.get_random_ingredients()`` function:

.. autofunction:: parortd.get_random_ingredients


The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
or ``"veggies"``. Otherwise, :py:func:`parortd.get_random_ingredients`
will raise an exception.

.. autoexception:: parortd.InvalidKindError



