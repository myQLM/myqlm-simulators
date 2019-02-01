#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest


class TestMyFunction(unittest.TestCase):

    def test_feature_1(self):
        a = 1
        b = 1
        self.assertTrue(a == b)

    def a_method(self):
        print("Hello")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
