from collections import deque
from copy import copy


class PopException(Exception):
    """pop() has been called more times than push()."""
    pass


class StackedDict(object):
    """Dictionary of stacks.

    Calls to push() or pop() affect one entire layer of the stack.

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
    def __init__(self):
        self._reset_stack()

    def _reset_stack(self, initial={}):
        self.stack = deque([initial])

    def __copy__(self):
        duplicate = copy(super(StackedDict, self))
        duplicate.stack = self.stack[:]
        return duplicate

    def __len__(self):
        return len(self.stack)

    def __getitem__(self, key):
        """Get a variable's value, starting at the current layer and going
        upward."""
        for layer in self.stack:
            try:
                return layer[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.stack[0][key] = value

    def __delitem__(self, key):
        del self.stack[0][key]

    def __iter__(self):
        return iter(self.stack)

    def push(self):
        layer = {}
        self.stack.appendleft(layer)

    def pop(self):
        return self.stack.popleft()

    def has_key(self, key):
        for layer in self.stack:
            if key in layer:
                return True
        return False

    def __contains__(self, key):
        return self.has_key(key)
