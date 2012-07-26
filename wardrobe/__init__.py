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
project_dir = dirname(package_dir)
version_file = join(project_dir, 'VERSION')
__version__ = open(version_file).read().strip()
