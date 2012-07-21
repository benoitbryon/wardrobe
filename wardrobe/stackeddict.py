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

        >>> dict(StackedDict())
        {}
        >>> dict(StackedDict({'a': 1}))
        {'a': 1}
        >>> dict(StackedDict(a=1))
        {'a': 1}

        """
        if initial is None:
            if kwargs:
                initial = kwargs
            else:
                initial = {}
        self._reset(initial)

    def _reset(self, initial={}):
        """(re)initialize data."""
        self._dict = initial  # Active layer.
        self._created = deque([])  # Store keys that have been created in
                                   # current layer.
        self._overriden = deque([])  # Store overriden (deleted or updated)
                                   # (key, value) pairs.

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
        duplicate._dict = copy(self._dict)
        duplicate._created = copy(self._created)
        duplicate._overriden = copy(self._overriden)
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
        return len(self._dict)

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
        Traceback (most recent call last):
        ...
        PopException
        >>> stacked_dict['some_key']
        'first'

        """
        return self._dict[key]

    def _has_layers(self):
        return bool(self._overriden)

    def __setitem__(self, key, value):
        if self._has_layers():  # We may have to backup value.
            if key not in self._dict:  # Adding a brand new key/value pair.
                self._created[0].add(key)
            elif key not in self._created[0]:  # A former layer is being
                                               # overriden.
                if key not in self._overriden[0]:  # Backup hasn't been set yet.
                    self._overriden[0][key] = self._dict[key]
        self._dict[key] = value

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
        if self._has_layers():
            try:
                self._created[0].remove(key)
            except KeyError:
                self._overriden[0][key] = self._dict.pop(key)
        else:
            del self._dict[key]

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
        """Comparison operator."""
        return cmp(dict(self), dict(other))

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

    def clear(self):
        """Remove all items from the dictionary.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> s.clear()
        >>> dict(s)
        {}

        Affects only current layer.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> s.push().update(c='C', d=4, e=5)
        >>> s.clear()
        >>> dict(s)
        {}
        >>> s.pop()
        {}
        >>> dict(s) == dict(a=1, b=2, c=3)
        True

        """
        if self._has_layers():
            # Delete keys created in current layer.
            for key in self._created[0]:
                del self._dict[key]
            self._created[0] = set()
            # Delete keys that have already been backuped.
            for key in self._overriden[0].keys():
                del self._dict[key]
            # Remaining keys are overriden ones.
            for key in self._dict.keys():
                self._overriden[0][key] = self._dict.pop(key)
        else:
            self._dict.clear()

    def copy(self):
        """Return a shallow copy of instance.
        
        >>> s1 = StackedDict(a=1, b=2, c=3)
        >>> s2 = s1.copy()
        >>> s1 == s2
        True
        >>> s1 is s2
        False
        
        """
        return copy(self)

    @classmethod
    def fromkeys(cls, seq, value=None):
        """Create a new dictionary with keys from seq and values set to value.

        :py:meth:`fromkeys` is a class method that returns a new dictionary.
        value defaults to None.

        """
        initial = dict.fromkeys(seq, value)
        return cls(**initial)

    def get(key, default=None):
        """"""
        try:
            return self[key]
        except KeyError:
            return default

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
        return self._dict.has_key(key)

    def items(self):
        """Return a copy of the dictionary's list of (key, value) pairs.

        >>> s = StackedDict(a=1, b=2)
        >>> i = s.items()
        >>> i.sort()
        >>> i
        [('a', 1), ('b', 2)]
        >>> s.push().update(c=3)
        >>> i = s.items()
        >>> i.sort()
        >>> i
        [('a', 1), ('b', 2), ('c', 3)]

        """
        return [(key, self[key]) for key in self.keys()]

    def iteritems(self):
        """Return an iterator over the dictionary's (key, value) pairs.

        >>> s = StackedDict(a=1, b=2)
        >>> i = s.iteritems()
        >>> i  # doctest: +ELLIPSIS
        <generator object iteritems at 0x...>
        >>> i = list(i)
        >>> i.sort()
        >>> i
        [('a', 1), ('b', 2)]
        >>> s.push().update(c=3)
        >>> i = s.iteritems()
        >>> i  # doctest: +ELLIPSIS
        <generator object iteritems at 0x...>
        >>> i = list(i)
        >>> i.sort()
        >>> i
        [('a', 1), ('b', 2), ('c', 3)]

        """
        for item in self._dict.iteritems():
            yield item

    def iterkeys(self):
        for key in self._dict.iterkeys():
            yield keys

    def itervalues(self):
        for value in self._dict.itervalues():
            yield value

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
        return self._dict.keys()

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

    def pop(self):
        """Restore dictionary to state before last push().
        
        >>> s = StackedDict(a=1, b=2)
        >>> s.push().update(c=3, d=4)
        >>> s.pop()
        {'c': 3, 'd': 4}
        >>> dict(s)
        {'a': 1, 'b': 2}
        >>> s.push().update(a='A', b='B')
        >>> s.pop()
        {'a': 'A', 'b': 'B'}
        >>> dict(s)
        {'a': 1, 'b': 2}
        >>> s.push().update(a='A', c=3)
        >>> s.pop()
        {'a': 'A', 'c': 3}
        >>> dict(s)
        {'a': 1, 'b': 2}

        Raises PopException when invoked on a StackedDict instance that hasn't
        been pushed yet.

        >>> s = StackedDict()
        >>> s.pop()
        Traceback (most recent call last):
        ...
        PopException
        
        """
        layer = {}  # We will return current changes.
        # Pop.
        try:
            created = self._created.popleft()
            overriden = self._overriden.popleft()
        except IndexError:
            raise PopException()
        # Delete created keys.
        for key in created: 
            layer[key] = self._dict.pop(key)
        # Restore overridden (key, value) pairs. 
        for key, value in overriden.items():
            try:
                layer[key] = self._dict[key]
            except KeyError:  # Case of deleted item.
                pass
            self._dict[key] = value
        return layer

    def popitem(self):
        """Remove and return some (key, value) pair as a 2-tuple; but raise
        KeyError if D is empty.

        Affects only the current layer.

        """
        for key in self.iterkeys():
            value = self[key]
            del self[key]
            return key, value

    def push(self):
        self._created.appendleft(set())
        self._overriden.appendleft({})
        return self

    def setdefault(self, key, default):
        return self._dict.setdefault(key, default)

    def values(self):
        pass

    def viewitems(self):
        pass

    def viewkeys(self):
        pass

    def viewvalues(self):
        pass
