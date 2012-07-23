"""StackedDict implementation."""
from collections import deque, MutableMapping
from copy import copy


class NoRevisionException(Exception):
    """Exception raised when reset() has been called more times than
    commit()."""


class StackedDict(MutableMapping):
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
    >>> clark.commit()  # doctest: +ELLIPSIS
    <wardrobe.stackeddict.StackedDict object at 0x...>
    >>> clark.update({'top': 'shirt', 'bottom': 'jeans', 'head': 'glasses'})
    >>> del clark['sex_appeal']
    >>> dict(clark) == {'top': 'shirt',
    ...                 'bottom': 'jeans',
    ...                 'head': 'glasses',
    ...                 'friend': 'Lois'}
    True
    >>> clark.reset()  # doctest: +ELLIPSIS
    <wardrobe.stackeddict.StackedDict object at 0x...>
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

        >>> s = StackedDict({'a': 1, 'b': 2})
        >>> len(s)
        2
        >>> s.commit()['c'] = 3
        >>> len(s)
        3
        >>> s.commit()['c'] = 4
        >>> len(s)
        3
        >>> silent = s.reset()
        >>> len(s)
        3
        >>> silent = s.reset()
        >>> len(s)
        2

        """
        return len(self._dict)

    def __getitem__(self, key):
        """Get a variable's value, starting at the current layer and going
        upward.

        >>> s = StackedDict()
        >>> s['some_key']
        Traceback (most recent call last):
        ...
        KeyError: 'some_key'
        >>> s['some_key'] = 'first'
        >>> s['some_key']
        'first'
        >>> silent = s.commit()
        >>> s['some_key']
        'first'
        >>> s['some_key'] = 'second'
        >>> s['some_key']
        'second'
        >>> silent = s.commit()
        >>> s['some_key']
        'second'
        >>> silent = s.reset()
        >>> s['some_key']
        'second'
        >>> silent = s.reset()
        >>> s['some_key']
        'first'
        >>> silent = s.reset()
        Traceback (most recent call last):
        ...
        NoRevisionException
        >>> s['some_key']
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

        >>> s = StackedDict(a=1, b=2, c=3, d=4)
        >>> del s['d']
        >>> s['d']
        Traceback (most recent call last):
        ...
        KeyError: 'd'
        >>> silent = s.commit()
        >>> s['d']
        Traceback (most recent call last):
        ...
        KeyError: 'd'
        >>> del s['a']
        >>> s['a']
        Traceback (most recent call last):
        ...
        KeyError: 'a'
        >>> s['a'] = 'restored'
        >>> 'a' in s.keys()
        True
        >>> del s['a']
        >>> del s['unknown']
        Traceback (most recent call last):
        ...
        KeyError: 'unknown'
        >>> del s['d']
        Traceback (most recent call last):
        ...
        KeyError: 'd'
        >>> silent = s.reset()
        >>> s['a']
        1
        >>> del s['a']
        >>> s['a']
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
        >>> with s.commit():
        ...    s['a'] = 'one'
        >>> s['a']
        1
        
        """
        self.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        """Implement context management ("with" statement)."""
        self.reset()

    def clear(self):
        """Remove all items from the dictionary.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> s.clear()
        >>> dict(s)
        {}

        Affects only current layer.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> s.commit().update(c='C', d=4, e=5)
        >>> s.clear()
        >>> dict(s)
        {}
        >>> silent = s.reset()
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
        """Create a new StackedDict with keys from seq and values set to value.

        :py:meth:`fromkeys` is a class method that returns a new StackedDict.
        value defaults to None.

        >>> s = StackedDict.fromkeys(['a', 'b', 'c'])
        >>> filter(lambda x: x is not None, s.values())
        []

        >>> s = StackedDict.fromkeys(['a', 'b', 'c'], 42)
        >>> filter(lambda x: x is not 42, s.values())
        []

        >>> s = StackedDict.fromkeys(range(1, 5), 'Hello world!')
        >>> filter(lambda x: x != 'Hello world!', s.values())
        []

        """
        initial = dict.fromkeys(seq, value)
        return cls(initial)

    def get(self, key, default=None):
        """Return the value for key if key is in the dictionary, else default.

        If default is not given, it defaults to None, so that this method never
        raises a KeyError.

        >>> s = StackedDict(a=1)
        >>> s.get('a')
        1
        >>> s.get('b') is None
        True
        >>> s.get('b', 2)
        2

        """
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
        >>> s.commit()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> s.has_key('a')
        True
        >>> del s['a']
        >>> s.has_key('a')
        False
        >>> s.commit()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> s.has_key('a')
        False
        
        """
        return self._dict.has_key(key)

    def items(self):
        """Return a copy of the StackedDict's list of (key, value) pairs.

        >>> s = StackedDict(a=1, b=2)
        >>> i = s.items()
        >>> i.sort()
        >>> i
        [('a', 1), ('b', 2)]
        >>> s.commit().update(c=3)
        >>> i = s.items()
        >>> i.sort()
        >>> i
        [('a', 1), ('b', 2), ('c', 3)]

        """
        return [(key, self[key]) for key in self.keys()]

    def iteritems(self):
        """Return an iterator over the StackedDict's (key, value) pairs.

        >>> s = StackedDict(a=1, b=2)
        >>> i = s.iteritems()
        >>> i  # doctest: +ELLIPSIS
        <generator object iteritems at 0x...>
        >>> i = list(i)
        >>> i.sort()
        >>> i
        [('a', 1), ('b', 2)]
        >>> s.commit().update(c=3)
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
        """Return an iterator over the StackedDict's keys.
        
        >>> s = StackedDict(a=1, b=2, c=3)
        >>> i = s.iterkeys()
        >>> i  # doctest: +ELLIPSIS
        <generator object iterkeys at 0x...>
        >>> l = list(i)
        >>> l.sort()
        >>> l
        ['a', 'b', 'c']
        
        """
        for key in self._dict.iterkeys():
            yield key

    def itervalues(self):
        """Return an iterator over the StackedDict's values.
        
        >>> s = StackedDict(a=1, b=2, c=3)
        >>> i = s.itervalues()
        >>> i  # doctest: +ELLIPSIS
        <generator object itervalues at 0x...>
        >>> l = list(i)
        >>> l.sort()
        >>> l
        [1, 2, 3]
        
        """
        for value in self._dict.itervalues():
            yield value

    def keys(self):
        """Return iterable on keys.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> keys = s.keys()
        >>> len(keys) == 3
        True
        >>> 'a' in keys and 'b' in keys and 'c' in keys
        True

        Deleted keys aren't returned... until the layer where the key was
        deleted is dropped.

        >>> s = StackedDict(a=1)
        >>> s.keys()
        ['a']
        >>> silent = s.commit()
        >>> del s['a']
        >>> s.keys()
        []
        >>> silent = s.commit()
        >>> s.keys()
        []
        >>> silent = s.reset()
        >>> s.keys()
        []
        >>> silent = s.reset()
        >>> s.keys()
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

    def pop(self, key, *args):
        """If key is in the dictionary, remove it and return its value, else
        return default.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> s.pop('a')
        1
        >>> 'a' in s
        False
        >>> s.pop('a', 'A')
        'A'

        If default is not given and key is not in the dictionary, a KeyError is
        raised.

        >>> s = StackedDict()
        >>> s.pop('a')
        Traceback (most recent call last):
        ...
        KeyError: 'a'

        Affects only current layer.

        >>> s = StackedDict(a=1, b=2, c=3)
        >>> s.commit()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> s.pop('b')
        2
        >>> silent = s.reset()
        >>> s['b']
        2

        """
        value = self._dict.pop(key, *args)
        if self._has_layers():
            try:
                self._created[0].remove(key)
            except KeyError:
                if key not in self._overriden[0]:
                    self._overriden[0][key] = value
        return value

    def popitem(self):
        """Remove and return some (key, value) pair as a 2-tuple.

        >>> s = StackedDict(a=1)
        >>> s.popitem()
        ('a', 1)
        >>> len(s)
        0

        Raises KeyError if D is empty.

        >>> s = StackedDict()
        >>> s.popitem()
        Traceback (most recent call last):
        ...
        KeyError: 'popitem(): dictionary is empty'

        Affects only the current layer.

        >>> s = StackedDict(a=1)
        >>> silent = s.commit()
        >>> s.popitem()
        ('a', 1)
        >>> silent = s.reset()
        >>> dict(s)
        {'a': 1}

        """
        key, value = self._dict.popitem()
        if self._has_layers():
            try:  # Delete key from created keys...
                self._created[0].remove(key)
            except KeyError:  # ... or mark key as overriden.
                if key not in self._overriden[0]:
                    self._overriden[0][key] = value
        return key, value

    def setdefault(self, key, default=None):
        """If key is in the dictionary, return its value. If not, insert key
        with a value of default and return default. default defaults to None.

        >>> s = StackedDict()
        >>> s.setdefault('a', 1)
        1
        >>> s.setdefault('a', 2)
        1
        >>> s.setdefault('b') is None
        True

        """
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def values(self):
        """Return a copy of the StackedDict's list of values.

        >>> s = StackedDict(a=1, b=2)
        >>> values = s.values()
        >>> values.sort()
        >>> values
        [1, 2]

        """
        return self._dict.values()

    def viewitems(self):
        """Return a new view of the StackedDict's items ((key, value) pairs).

        See http://docs.python.org/library/stdtypes.html#dictionary-view-objects
        for documentation of view objects.

        >>> s = StackedDict()
        >>> view = s.viewitems()
        >>> view
        dict_items([])
        >>> s.update(a=1)
        >>> view
        dict_items([('a', 1)])
        >>> s.commit().update(a='A')
        >>> view
        dict_items([('a', 'A')])

        """
        return self._dict.viewitems()

    def viewkeys(self):
        """

        See http://docs.python.org/library/stdtypes.html#dictionary-view-objects
        for documentation of view objects.

        >>> s = StackedDict()
        >>> view = s.viewkeys()
        >>> view
        dict_keys([])
        >>> s.update(a=1)
        >>> view
        dict_keys(['a'])
        >>> s.commit()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> del s['a']
        >>> s['b'] = 2
        >>> view
        dict_keys(['b'])

        """
        return self._dict.viewkeys()

    def viewvalues(self):
        """

        See http://docs.python.org/library/stdtypes.html#dictionary-view-objects
        for documentation of view objects.

        >>> s = StackedDict()
        >>> view = s.viewvalues()
        >>> view
        dict_values([])
        >>> s.update(a=1)
        >>> view
        dict_values([1])
        >>> s.commit()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> del s['a']
        >>> s['b'] = 2
        >>> view
        dict_values([2])

        """
        return self._dict.viewvalues()

    def commit(self):
        """Save current dictionary state, record next changes in some diff
        history.

        Returns StackedDict instance, so that you can chain operations.

        Use :py:meth:`reset` to restore the saved state.

        >>> s = StackedDict(a=1)
        >>> s.commit().update(a='A')
        >>> dict(s)
        {'a': 'A'}
        >>> silent = s.reset()
        >>> dict(s)
        {'a': 1}

        """
        self._created.appendleft(set())
        self._overriden.appendleft({})
        return self

    def reset(self):
        """Restore dictionary to state before last :py:meth:`commit`.
        
        >>> s = StackedDict(a=1, b=2)
        >>> s.commit().update(c=3, d=4)
        >>> s.reset()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> dict(s)
        {'a': 1, 'b': 2}
        >>> s.commit().update(a='A', b='B')
        >>> s.reset()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> dict(s)
        {'a': 1, 'b': 2}
        >>> s.commit().update(a='A', c=3)
        >>> s.reset()  # doctest: +ELLIPSIS
        <wardrobe.stackeddict.StackedDict object at 0x...>
        >>> dict(s)
        {'a': 1, 'b': 2}

        Raises NoRevisionException when invoked on a StackedDict instance that hasn't
        been pushed yet.

        >>> s = StackedDict()
        >>> s.reset()
        Traceback (most recent call last):
        ...
        NoRevisionException
        
        """
        # Pop.
        try:
            created = self._created.popleft()
            overriden = self._overriden.popleft()
        except IndexError:
            raise NoRevisionException()
        # Delete created keys.
        for key in created: 
            del self._dict[key]
        # Restore overridden (key, value) pairs. 
        for key, value in overriden.items():
            self._dict[key] = value
        return self
