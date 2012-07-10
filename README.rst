########
wardrobe
########

This project provides stack-based datastructures for Python: list of stacks.

Example:

::

    >>> from wardrobe import StackedDict
    >>> clark = StackedDict()
    >>> clark['top'] = 'blue bodysuit'
    >>> clark['bottom'] = 'red underpants'
    >>> clark['friend'] = 'Lois'
    >>> clark['top']
    'blue bodysuit'
    >>> clark['bottom']
    'red underpants'
    >>> clark['friend']
    'Lois'
    >>> clark.push()
    >>> clark['top'] = 'shirt'
    >>> clark['bottom'] = 'jeans'
    >>> clark['top']
    'shirt'
    >>> clark['bottom']
    'jeans'
    >>> clark['friend']
    'Lois'
    >>> clark.pop()
    {'top': 'shirt', 'bottom': 'jeans'}
    >>> clark['top']
    'blue bodysuit'
    >>> clark['bottom']
    'red underpants'
    >>> clark['friend']
    'Lois'

Original code is based on `Django's django.template.context:Context objects`_.

**********
Ressources
**********

* `code repository`_
* `bugtracker`_


**********
References
**********

.. target-notes::

.. _`Django's django.template.context:Context objects`: 
   https://github.com/django/django/blob/master/django/template/context.py
.. _`code repository`: https://github.com/benoitbryon/wardrobe
.. _`bugtracker`: https://github.com/benoitbryon/wardrobe/issues
