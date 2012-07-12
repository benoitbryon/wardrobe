########
wardrobe
########

This project provides a stack-based datastructure for Python: StackedDict.

Example:

::

    >>> from wardrobe import StackedDict
    >>> clark = StackedDict()  # Clark gets dressed.
    >>> clark['top'] = 'blue bodysuit'
    >>> clark['bottom'] = 'red underpants'
    >>> clark['friend'] = 'Lois'
    >>> clark['top']
    'blue bodysuit'
    >>> clark['bottom']
    'red underpants'
    >>> clark['friend']
    'Lois'
    >>> clark.push()  # Let's add new layers of clothes.
    >>> # Override top and bottom, not friend.
    >>> clark['top'] = 'shirt'
    >>> clark['bottom'] = 'jeans'
    >>> clark['top']
    'shirt'
    >>> clark['bottom']
    'jeans'
    >>> clark['friend']  # Clark's friend is still Lois.
    'Lois'
    >>> # ... Oh! the Earth is in danger! Go Clark, go!
    >>> clark.pop()  # Drop costume.
    {'top': 'shirt', 'bottom': 'jeans'}
    >>> clark['top']
    'blue bodysuit'
    >>> clark['bottom']
    'red underpants'
    >>> clark['friend']
    'Lois'

wardrobe.StackedDict is useful to create context objects, like `Django's
django.template.context:Context objects`_.

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
