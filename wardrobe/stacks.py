from collections import deque
from copy import copy


class PopException(Exception):
    """pop() has been called more times than push()."""
    pass


class StackedDict(object):
    """Dictionary-like object made of stacked layers.

    Instances act like dictionaries.

    Calls to :py:meth:`push` or :py:meth:`pop`affect (respectively create or
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

    def _reset_stack(self, initial={}):
        """Initialize data."""
        self._stack = deque([initial])

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
        return len(self._stack)

    def __getitem__(self, key):
        """Get a variable's value, starting at the current layer and going
        upward."""
        for layer in self._stack:
            try:
                return layer[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._stack[0][key] = value

    def __delitem__(self, key):
        del self._stack[0][key]

    def __iter__(self):
        return iter(self._stack)

    def push(self):
        layer = {}
        self._stack.appendleft(layer)

    def pop(self):
        return self._stack.popleft()

    def _has_key(self, key):
        for layer in self._stack:
            if key in layer:
                return True
        return False

    def __contains__(self, key):
        return self._has_key(key)

    def __cmp__(self, other):
        return cmp(self._stack, other._stack)
