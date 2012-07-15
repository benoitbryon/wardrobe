"""StackedDict implementation."""
from collections import deque
from copy import copy

from wardrobe.exceptions import PopException


class StackedDict(object):
    """Dictionary-like object made of stacked layers.

    Instances act like dictionaries.

    Calls to :py:meth:`push` or :py:meth:`pop` affect (respectively create or
    delete) one entire layer of the stack.

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
    >>> clark.push()  # doctest: +ELLIPSIS
    <wardrobe.stackeddict.StackedDict object at 0x...>
    >>> clark.update({'top': 'shirt', 'bottom': 'jeans', 'head': 'glasses'})
    >>> del clark['sex_appeal']
    >>> dict(clark) == {'top': 'shirt',
    ...                 'bottom': 'jeans',
    ...                 'head': 'glasses',
    ...                 'friend': 'Lois'}
    True
    >>> clark.pop() == {'top': 'shirt', 'bottom': 'jeans', 'head': 'glasses'}
    True
    >>> dict(clark) == {'top': 'blue bodysuit',
    ...                 'bottom': 'red underpants',
    ...                 'friend': 'Lois',
    ...                 'sex_appeal': True}
    True

    """

    def __init__(self, initial=None, **kwargs):
        """Constructor.

        >>> sd = StackedDict()
        >>> list(sd._stack)
        [{}]
        >>> sd = StackedDict({'a': 1})
        >>> list(sd._stack)
        [{'a': 1}]
        >>> sd = StackedDict(a=1)
        >>> list(sd._stack)
        [{'a': 1}]

        """
        if initial is None:
            if kwargs:
                initial = kwargs
            else:
                initial = {}
        self._reset_stack(initial)
        self._deleted_keys = deque([set()])

    def __copy__(self):
        """Copy operator.

        >>> from copy import copy
        >>> right = StackedDict()
        >>> left = right
        >>> left is right
        True
        >>> right = StackedDict()
        >>> left = copy(right)
        >>> left is right
        False
        >>> left == right
        True

        """
        duplicate = copy(super(StackedDict, self))
        duplicate._stack = copy(self._stack)
        return duplicate

    def __len__(self):
        """Return number of elements.

        >>> stacked_dict = StackedDict({'a': 1, 'b': 2})
        >>> len(stacked_dict)
        2
        >>> stacked_dict.push()['c'] = 3
        >>> len(stacked_dict)
        3
        >>> stacked_dict.push()['c'] = 4
        >>> len(stacked_dict)
        3
        >>> silent = stacked_dict.pop()
        >>> len(stacked_dict)
        3
        >>> silent = stacked_dict.pop()
        >>> len(stacked_dict)
        2

        """
        return len(self.keys())

    def __getitem__(self, key):
        """Get a variable's value, starting at the current layer and going
        upward.

        >>> stacked_dict = StackedDict()
        >>> stacked_dict['some_key']
        Traceback (most recent call last):
        ...
        KeyError: 'some_key'
        >>> stacked_dict['some_key'] = 'first'
        >>> stacked_dict['some_key']
        'first'
        >>> silent = stacked_dict.push()
        >>> stacked_dict['some_key']
        'first'
        >>> stacked_dict['some_key'] = 'second'
        >>> stacked_dict['some_key']
        'second'
        >>> silent = stacked_dict.push()
        >>> stacked_dict['some_key']
        'second'
        >>> silent = stacked_dict.pop()
        >>> stacked_dict['some_key']
        'second'
        >>> silent = stacked_dict.pop()
        >>> stacked_dict['some_key']
        'first'
        >>> silent = stacked_dict.pop()
        >>> stacked_dict['some_key']
        Traceback (most recent call last):
        ...
        KeyError: 'some_key'

        """
        for layer in self._stack:
            try:
                return layer[key]
            except KeyError:
                pass
            if key in self._deleted_keys[0]:
                raise KeyError(key)
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._stack[0][key] = value
        try:
            self._deleted_keys[0].remove(key)
        except KeyError:
            pass

    def __delitem__(self, key):
        """Remove a key/value pair from current layer.

        Affects only current layer, i.e. keys that were deleted in a layer
        can reappear when the layer is dropped.

        >>> stacked_dict = StackedDict(a=1, b=2, c=3, d=4)
        >>> del stacked_dict['d']
        >>> stacked_dict['d']
        Traceback (most recent call last):
        ...
        KeyError: 'd'
        >>> silent = stacked_dict.push()
        >>> stacked_dict['d']
        Traceback (most recent call last):
        ...
        KeyError: 'd'
        >>> del stacked_dict['a']
        >>> stacked_dict['a']
        Traceback (most recent call last):
        ...
        KeyError: 'a'
        >>> stacked_dict['a'] = 'restored'
        >>> 'a' in stacked_dict.keys()
        True
        >>> del stacked_dict['a']
        >>> del stacked_dict['unknown']
        Traceback (most recent call last):
        ...
        KeyError: 'unknown'
        >>> del stacked_dict['d']
        Traceback (most recent call last):
        ...
        KeyError: 'd'
        >>> silent = stacked_dict.pop()
        >>> stacked_dict['a']
        1
        >>> del stacked_dict['a']
        >>> stacked_dict['a']
        Traceback (most recent call last):
        ...
        KeyError: 'a'

        .. note::

           Current implementation maintains a list of deleted keys for each
           layer of the stack. The list of deleted keys can be bigger than
           the layer itself if you delete many keys.

        """
        try:
            del self._stack[0][key]
        except KeyError:
            if not key in self.keys():
                raise
        if len(self._stack) > 1:  # There is no need to store deleted keys on
                                  # initial level.
            self._deleted_keys[0].add(key)

    def __iter__(self):
        """Iterate over keys.

        .. warning:

           Current implementation builds the full list of keys then returns an
           iterator on it.

        .. note::

           As with dict type, keys are not ordered.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> i = iter(s)
        >>> i  # doctest: +ELLIPSIS
        <listiterator object at 0x...>
        >>> keys = [k for k in i]
        >>> 'a' in keys and 'b' in keys and 'c' in keys
        True

        """
        return iter(self.keys())

    def __contains__(self, key):
        """Implement "in" operator.
        
        >>> s = StackedDict(a=1, b=2, c=3)
        >>> 'a' in s
        True
        >>> 'b' in s
        True
        >>> 1 in s
        False
        
        """
        return self.has_key(key)

    def __cmp__(self, other):
        return cmp(self._stack, other._stack)

    def __enter__(self):
        """Implement context management ("with" statement).
        
        >>> s = StackedDict(a=1, b=2)
        >>> with s.push():
        ...    s['a'] = 'one'
        >>> s['a']
        1
        
        """
        self.push()

    def __exit__(self, exc_type, exc_value, traceback):
        """Implement context management ("with" statement)."""
        self.pop()

    def _reset_stack(self, initial={}):
        """(re)initialize data."""
        self._stack = deque([initial])

    def has_key(self, key):
        """Return True if key is in instance, False otherwise.
        
        Affects global instance, not "only the current layer".

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> s.has_key('a')
        True
        >>> s.has_key('b')
        True
        >>> s.has_key(1)
        False
        >>> s.push()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> s.has_key('a')
        True
        >>> del s['a']
        >>> s.has_key('a')
        False
        >>> s.push()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> s.has_key('a')
        False
        
        """
        for depth, layer in enumerate(self._stack):
            if key in layer:
                return True
            if key in self._deleted_keys[depth]:
                return False
        return False

    def keys(self):
        """Return iterable on keys.

        >>> stacked_dict = StackedDict(a=1, b=2, c=3)
        >>> keys = stacked_dict.keys()
        >>> len(keys) == 3
        True
        >>> 'a' in keys and 'b' in keys and 'c' in keys
        True

        Deleted keys aren't returned... until the layer where the key was
        deleted is dropped.

        >>> stacked_dict = StackedDict(a=1)
        >>> stacked_dict.keys()
        ['a']
        >>> silent = stacked_dict.push()
        >>> del stacked_dict['a']
        >>> stacked_dict.keys()
        []
        >>> silent = stacked_dict.push()
        >>> stacked_dict.keys()
        []
        >>> silent = stacked_dict.pop()
        >>> stacked_dict.keys()
        []
        >>> silent = stacked_dict.pop()
        >>> stacked_dict.keys()
        ['a']

        """
        keys = set()
        for depth, layer in enumerate(reversed(self._stack)):
            # keys = previous_keys + layer_keys - layer_deleted_keys
            keys.update(set(layer.keys()))
            keys.difference_update(self._deleted_keys[depth])
        return list(keys)

    def update(self, *args, **kwargs):
        """Update instance from dict (positional argument) and/or iterable
        (keyword arguments).
        
        Affects only current layer.

        Positional argument can be a dict...

        >>> s = StackedDict(a=1, b=2)
        >>> s.update({'a': 'A', 'c': 3})
        >>> dict(s) == {'a': 'A', 'b': 2, 'c': 3}
        True
        
        ... or any object that can be converted to a dict.

        >>> s = StackedDict(a=1, b=2)
        >>> s.update((('a', 'A'), ('c', 3)))
        >>> dict(s) == {'a': 'A', 'b': 2, 'c': 3}
        True

        Also accepts input as keyword arguments.

        >>> s = StackedDict(a=1, b=2)
        >>> s.update(a='A', c=3)
        >>> dict(s) == {'a': 'A', 'b': 2, 'c': 3}
        True

        A combination of positional and keyword arguments is accepted. The
        positional argument is handled as a dict.

        >>> s = StackedDict(a=1, b=2)
        >>> s.update({'a': 'A'}, c=3)
        >>> dict(s) == {'a': 'A', 'b': 2, 'c': 3}
        True

        But only one positional argument is accepted. This mimics a limitation
        of the standard dict type.

        >>> s = StackedDict(a=1, b=2)
        >>> s.update({'a': 'A'}, {'c': 3})
        Traceback (most recent call last):
        ...
        TypeError: update expected at most 1 arguments, got 2

        """
        if args:
            if len(args) > 1:
                raise TypeError('update expected at most 1 arguments, got %d' \
                                % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def push(self):
        self._stack.appendleft({})
        self._deleted_keys.appendleft(set())
        return self

    def pop(self):
        self._deleted_keys.popleft()
        return self._stack.popleft()
