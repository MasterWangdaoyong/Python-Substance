# coding: utf-8

import os
import unittest

import pysbs
from pysbs import *

PATH_VERSION = os.path.join(
    # root folder
    os.path.dirname(
        # pysbs folder
        os.path.dirname(
            # test folder
            os.path.dirname(__file__)
        )
    ),
    'VERSION'
)
assert os.path.exists(PATH_VERSION)

with open(PATH_VERSION, 'r') as file:
    VERSION_STRING = file.read()

class PySBSTest(unittest.TestCase):

    def test_Version(self):
        """
        This tests checks the module __version__
        """
        self.assertEqual(VERSION_STRING, pysbs.__version__)

    def test_Author(self):
        """
        This tests checks the module __author__
        """
        self.assertEqual('Adobe', pysbs.__author__)

    def test_WildImports(self):
        """
        This tests module exported when calling from pysbs import *
        """
        # Nothing is done with object, but we
        publicAPIModules = [
            'api_decorators',
            'api_exceptions',
            'api_helpers',
            'autograph',
            'base',
            'batchtools',
            'common_interfaces',
            'compnode',
            'context',
            'freeimagebindings',
            'graph',
            'lzmabindings',
            'mdl',
            'params',
            'psdparser',
            'python_helpers',
            'qtclasses',
            'sbsarchive',
            'sbsbakers',
            'sbscleaner',
            'sbscommon',
            'sbsenum',
            'sbsexporter',
            'sbsgenerator',
            'sbsimpactmanager',
            'sbslibrary',
            'sbsparser',
            'sbswriter',
            'substance',
        ]
        for modulename in publicAPIModules:
            self.assertIn(
                modulename, globals(),
                msg='pysbs module {} not found after from pysbs import *'.format(modulename)
            )
