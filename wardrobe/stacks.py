from collections import deque
from copy import copy


class PopException(Exception):
    """pop() has been called more times than push()."""
    pass


class StackedDict(object):
    """Dictionary-like object made of stacked layers.

    Instances act like dictionaries.

    Calls to :py:meth:`push` or :py:meth:`pop` affect (respectively create or
    delete) one entire layer of the stack.

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
    >>> clark.push()  # doctest: +ELLIPSIS
    <wardrobe.stacks.StackedDict object at 0x...>
    >>> clark['top'] = 'shirt'
    >>> clark['bottom'] = 'jeans'
    >>> clark['top']
    'shirt'
    >>> clark['bottom']
    'jeans'
    >>> clark['friend']
    'Lois'
    >>> dropped = clark.pop()
    >>> dropped == {'top': 'shirt', 'bottom': 'jeans'}
    True
    >>> clark['top']
    'blue bodysuit'
    >>> clark['bottom']
    'red underpants'
    >>> clark['friend']
    'Lois'

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
        """Remove a key/value.

        >>> stacked_dict = StackedDict(a=1, b=2, c=3)
        >>> stacked_dict._deleted_keys[0]
        set([])
        >>> stacked_dict['a']
        1
        >>> silent = stacked_dict.push()
        >>> stacked_dict['a'] = 'one'
        >>> stacked_dict['a']
        'one'
        >>> del stacked_dict['a']
        >>> stacked_dict._deleted_keys[0]
        set(['a'])
        >>> stacked_dict['a']
        Traceback (most recent call last):
        ...
        KeyError: 'a'
        >>> silent = stacked_dict.pop()
        >>> stacked_dict['a']
        1
        >>> del stacked_dict['a']
        >>> stacked_dict['a']
        Traceback (most recent call last):
        ...
        KeyError: 'a'

        """
        del self._stack[0][key]
        self._deleted_keys[0].add(key)

    def __iter__(self):
        return iter(self._stack)

    def __contains__(self, key):
        return self._has_key(key)

    def __cmp__(self, other):
        return cmp(self._stack, other._stack)

    def _reset_stack(self, initial={}):
        """(re)initialize data."""
        self._stack = deque([initial])

    def _has_key(self, key):
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

        """
        all_keys = set()
        for depth, layer in enumerate(self._stack):
            layer_keys = set(layer.keys()).difference(self._deleted_keys[depth])
            all_keys.update(layer_keys)
        return list(all_keys)

    def push(self):
        self._stack.appendleft({})
        self._deleted_keys.appendleft(set())
        return self

    def pop(self):
        self._deleted_keys.popleft()
        return self._stack.popleft()
