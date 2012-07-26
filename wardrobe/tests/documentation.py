"""Tests around project's documentation."""
from os import chdir
from os.path import (abspath, basename, dirname, exists, getmtime, isdir,
                     isfile, join)
import shutil
from subprocess import Popen, PIPE
import time
from unittest import TestCase


package_dir = dirname(dirname(abspath(__file__)))
package_name = basename(package_dir)
project_dir = dirname(package_dir)
build_dir = join(project_dir, 'var', 'docs', 'html')


class DocumentationBuildTestCase(TestCase):
    """Make sure documentation builds without errors or warnings."""
    def setUp(self):
        """Setup."""
        # Cd to project's root.
        chdir(project_dir)

    def test_documentation_build(self):
        """Build documentation."""
        build_file = join(build_dir, 'index.html')
        # First, if files to be generated already exist, remember their
        # modification time.
        build_time = None
        if exists(build_file):
            build_time = time.ctime(getmtime(build_file))
        # Run build.
        command = ['make', 'documentation']
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        return_code = process.wait()
        stderr = process.communicate()[1]
        # sphinx-build echoes 'making output directory\n' to STDERR. Ignore it.
        stderr = stderr.replace('Making output directory...\n', '')
        # Check result.
        self.assertEqual(return_code, 0)
        self.assertEqual(stderr, '')
        self.assertTrue(isdir(build_dir))
        self.assertTrue(isfile(build_file))
        if build_time is not None:
            self.assertTrue(time.ctime(getmtime(build_file)) > build_time)

    def test_readme_build(self):
        """Build README."""
        build_file = join(build_dir, 'README.html')
        # First, if files to be generated already exist, remember their
        # modification time.
        build_time = None
        if exists(build_file):
            build_time = time.ctime(getmtime(build_file))

        # Run build.
        command = ['make', 'readme']
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        return_code = process.wait()
        stderr = process.communicate()[1]
        # Check result.
        self.assertEqual(stderr, '')
        self.assertEqual(return_code, 0)
        self.assertTrue(isdir(build_dir))
        self.assertTrue(isfile(build_file))
