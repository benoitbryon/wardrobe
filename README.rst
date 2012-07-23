########
wardrobe
########

wardrobe is a Python project that provides a stack-based datastructure:
:py:class`StackedDict`.

:py:class`StackedDict` is a dictionary-like object with additional methods to
save the current state (commit) and restore it (reset).

Example:

::

  >>> from wardrobe import StackedDict
  >>> clark = StackedDict(top='blue bodysuit', bottom='red underpants',
  ...                     sex_appeal=True)
  >>> clark['bottom']
  'red underpants'
  >>> clark['friend'] = 'Lois'
  >>> dict(clark) == {'top': 'blue bodysuit',
  ...                 'bottom': 'red underpants',
  ...                 'friend': 'Lois',
  ...                 'sex_appeal': True}
  True
  >>> clark.commit()  # doctest: +ELLIPSIS
  <wardrobe.stackeddict.StackedDict object at 0x...>
  >>> clark.update({'top': 'shirt', 'bottom': 'jeans', 'head': 'glasses'})
  >>> del clark['sex_appeal']
  >>> dict(clark) == {'top': 'shirt',
  ...                 'bottom': 'jeans',
  ...                 'head': 'glasses',
  ...                 'friend': 'Lois'}
  True
  >>> clark.reset() == {'top': 'shirt', 'bottom': 'jeans', 'head': 'glasses'}
  True
  >>> dict(clark) == {'top': 'blue bodysuit',
  ...                 'bottom': 'red underpants',
  ...                 'friend': 'Lois',
  ...                 'sex_appeal': True}
  True

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
