# -*- coding: utf-8 -*-

"""
    Licensed to the Apache Software Foundation (ASF) under one
    or more contributor license agreements.  See the NOTICE file
    distributed with this work for additional information
    regarding copyright ownership.  The ASF licenses this file
    to you under the Apache License, Version 2.0 (the
    "License"); you may not use this file except in compliance
    with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing,
    software distributed under the License is distributed on an
    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
    KIND, either express or implied.  See the License for the
    specific language governing permissions and limitations
    under the License.
"""

import sys
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


def get_description():
    """
    Returns the long description of the current
    package

    Returns:
        str
    """
    with open("README.md", "r") as readme:
        return readme.read()


setup(
    name="myqlm-simulators",
    version="0.0.0",
    author="Atos Quantum Lab",
    license="Atos myQLM EULA",
    description="myQLM-simulators package",
    long_description=get_description(),
    long_description_content_type='text/markdown',
    url="https://atos.net/en/lp/myqlm",
    project_urls={
        "Documentation": "https://myqlm.github.io",
        "Bug Tracker": "https://github.com/myQLM/myqlm-issues/issues",
        "Community": "https://myqlmworkspace.slack.com",
        "Source code": "https://github.com/myQLM/myqlm-simulators"
    },
    packages=find_namespace_packages(include=["qat.*"]),
    test_suite="tests",
    install_requires=["qat-core", "qat-lang", "qat-variational", "numpy~=2.0"],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
