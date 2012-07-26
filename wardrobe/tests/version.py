"""Tests around project's version."""
from os.path import abspath, basename, dirname, join
from unittest import TestCase


package_dir = dirname(dirname(abspath(__file__)))
package_name = basename(package_dir)


class PEP396TestCase(TestCase):
    """Check's PEP 396 compliance, i.e. package's __version__ attribute."""
    def get_package_version(self):
        """Return __version__ attribute of project's main package."""
        project_package = __import__(package_name, globals(), locals(),
                                     ['__version__'], -1)
        return project_package.__version__

    def get_installed_version(self):
        """Return installed version, via setuptools.pkg_resources."""
        import pkg_resources
        return pkg_resources.get_distribution(package_name).version

    def test_version_present(self):
        """Check that project main package/module has __version__ attribute."""
        try:
            version = self.get_package_version()
        except ImportError:
            self.fail('%s package has no attribute __version__.' % package_name)

    def test_version_match(self):
        """Check that project's package/module __version__ matches
        pkg_resources information."""
        try:
            installed_version = self.get_installed_version()
        except ImportError:
            self.fail('Cannot import pkg_resources module. It is part of ' \
                      'setuptools, which is a dependency of %s.' % package_name)
        package_version = self.get_package_version()
        self.assertEqual(installed_version, package_version,
                         'Version mismatch: version.txt tells "%s" whereas ' \
                         'pkg_resources tells "%s". ' \
                         'YOU MAY NEED TO RUN ``make update`` to update the ' \
                         'installed version in development environment.' \
                         % (package_version, installed_version))
