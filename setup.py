# coding=utf-8
"""Python packaging."""
import os
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


NAME = 'wardrobe'
README = read_relative_file('README')
VERSION = read_relative_file(os.path.join(NAME, 'version.txt')).strip()


setup(name=NAME,
      version=VERSION,
      description='Stack-based datastructures: StackedDict.',
      long_description=README,
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2.7',
                   ],
      keywords='stack dict context',
      author='Benoit Bryon',
      author_email='benoit@marmelune.net',
      url='https://github.com/benoitbryon/%s' % NAME,
      license='BSD',
      packages=[NAME],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools'],
      )
