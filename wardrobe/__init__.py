"""wardrobe package.

StackedDict class is available at package level, for convenience:

>>> from wardrobe import StackedDict
>>> s = StackedDict(a=1, b=2, c=3)

Or:

>>> from wardrobe import *
>>> s = StackedDict(a=1, b=2, c=3)

See :py:class:`wardrobe.stackeddict.StackedDict` for details.

"""
from os.path import abspath, dirname, join

from wardrobe.stackeddict import StackedDict 


#: Implement :pep:`396`
package_dir = dirname(abspath(__file__))
version_file = join(package_dir, 'version.txt')
__version__ = open(version_file).read().strip()
