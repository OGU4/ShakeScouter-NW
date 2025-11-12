#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2024 mntone
# Licensed under the GPLv3 license.

import unittest

from glob import glob

from utils import forceCwd

# Set current working directory.
forceCwd(__file__)

def createTestSuite():
	filenames = glob('**/*_test.py', recursive=True)
	modules = [str[0:len(str) - 3].replace('\\', '.') for str in filenames]
	suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in modules]
	testSuite = unittest.TestSuite(suites)
	return testSuite

testSuite = createTestSuite()
text_runner = unittest.TextTestRunner().run(testSuite)
