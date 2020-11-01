import unittest
import logging
log = logging.getLogger(__name__)
import os
import sys
import shutil
import platform

from pysbs_demos import demos
from pysbs_demos import demos_batchtools

from pysbs import python_helpers
from pysbs import context
from pysbs import substance


testModule = sys.modules[__name__]

class GlobalBTTests(unittest.TestCase):

    def test_DemoCreationMDL(self):
        log.info('\nGlobalTests: test_DemoCreationMDL')
        aContext = context.Context()
        refAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refDemoCreationMDL.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDemoCreationMDL.sbs')
        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos.demoCreationMDL(aContext, destAbsPath))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        docRef.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()
        self.assertTrue(docRef.equals(docDest))

        os.remove(destAbsPath)

    @unittest.skipIf(platform.system() == 'Linux' and not os.environ.get('DISPLAY', False), 'sbsbaker cannot run on a machine without a graphic environment.')
    def test_DemoUdims(self):

        log.info('\nGlobalTests: test_DemoUdims')
        aContext = context.Context()
        resourcePath = python_helpers.getAbsPathFromModule(testModule, 'resources')

        refAbsPath = os.path.join(resourcePath, 'refDemoUdim.sbs')
        destAbsPath = os.path.join(resourcePath, 'testDemoUdim.sbs')
        templatePath = os.path.join(resourcePath, os.pardir, os.pardir, 'sample', 'TemplateGraphUdims.sbs')

        if os.path.exists(destAbsPath):
            os.remove(destAbsPath)
        self.assertTrue(demos_batchtools.demoUdimPipeline(aContext,
                                                          aTemplateSbsPath=templatePath,
                                                          aDestSbsPath=destAbsPath,
                                                          aMeshPath=os.path.join(resourcePath, 'Models', 'scifi_container_low.fbx'),
                                                          aUdimList='1001,1002',
                                                          aOutputSize='10',
                                                          aOutputBakingPath=os.path.join(resourcePath, 'UdimsOutput', 'Baking'),
                                                          aOutputRenderPath=os.path.join(resourcePath, 'UdimsOutput', 'Render')))

        docRef = substance.SBSDocument(aContext, refAbsPath)
        docRef.parseDoc()
        docDest = substance.SBSDocument(aContext, destAbsPath)
        docDest.parseDoc()
        self.assertTrue(docRef.equals(docDest))

        os.remove(destAbsPath)
        shutil.rmtree(os.path.join(resourcePath, 'UdimsOutput'))
