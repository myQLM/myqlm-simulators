import os, sys
from setuptools import setup, find_namespace_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main([".", "-v"])
        sys.exit(errno)

setup(
    name="qat-pylinalg",
    version="0.0.2",
    author="Atos Quantum Lab",
    license="Atos myQLM EULA",
    packages=find_namespace_packages(),
    test_suite="tests",
    install_requires=["thrift==0.10", "qat-core>=0.0.9",
                      "qat-lang>=0.0.8", "numpy"],
    tests_require=['pytest'],
    cmdclass = {'test': PyTest},
)
