"""wardrobe package.

StackedDict class is available at package level, for convenience:

>>> from wardrobe import StackedDict
>>> s = StackedDict(a=1, b=2, c=3)

Or:

>>> from wardrobe import *
>>> s = StackedDict(a=1, b=2, c=3)

See :py:class:`wardrobe.stackeddict.StackedDict` for details.

"""
from wardrobe.stackeddict import StackedDict 
from wardrobe.version import version as project_version


#: Implement :pep:`396`
__version__ = project_version
