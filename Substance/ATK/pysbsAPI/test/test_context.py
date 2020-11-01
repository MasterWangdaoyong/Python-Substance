# coding: utf-8
import unittest
import logging
import sys
import os
log = logging.getLogger(__name__)

from pysbs.context import Context
from pysbs import python_helpers
from pysbs import substance
from pysbs import context
from pysbs.api_exceptions import SBSImpossibleActionError

testModule = sys.modules[__name__]


class ContextTest(unittest.TestCase):

    @staticmethod
    def getTestResourceDir():
        return python_helpers.getAbsPathFromModule(testModule, 'resources/BTImpactPropag')

    @staticmethod
    def openTestDocument(aFileName):
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/' + aFileName)
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc


    def test_UrlAliasMgr(self):
        """
        This tests some potential problems with
        """
        c = Context()
        urlAliasManager = c.getUrlAliasMgr()

        drivePlatform = os.path.splitdrive(self.getTestResourceDir())[0] != ''


        # Only run this test on platforms with a drives
        if drivePlatform:
            self.assertEqual(urlAliasManager.toRelPath('d:\\dummy', 'c:/dummy2'), 'd:\\dummy')

            # Make sure another ValueError is properly thrown
            with self.assertRaises(ValueError):
                urlAliasManager.toRelPath('', '/a/b/c')

            doc = self.openTestDocument('Resources.sbs')
            self.assertIsNotNone(doc)

            resourceList = doc.getSBSResourceList()
            self.assertIs(len(resourceList), 1)
            # Split off drive
            drive, _ = os.path.splitdrive(self.getTestResourceDir())
            # Move forward to a different drive to make sure we link
            # a resource on a different drive
            newDrive = drive.replace(drive[0], chr(ord(drive[0]) + 1))
            doc.relocateResource(resourceList[0], os.path.join(newDrive, '/dummy.png'), checkPathExists=False)