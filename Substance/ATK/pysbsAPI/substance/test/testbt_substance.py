# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import sys

from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers
from pysbs import sbsgenerator
from pysbs import context
from pysbs import substance
from pysbs import graph
from pysbs import mdl

import pysbs_demos

testModule = sys.modules[__name__]


class SBSSubstanceBTTests(unittest.TestCase):

    def test_CreateMDLGraphFromTemplate(self):
        """
        This test checks the ability to create a MDL graph from a template
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/graphMDLFromTemplate.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), aFileAbsPath=fileAbsPath)

        # Template from demoCreationMDL
        demoCreationPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/resultDemoCreationMDL.sbs')
        templateGraphPath = demoCreationPath+'/DemoMDLGraph'
        aGraph = sbsDoc.createMDLGraph(aGraphIdentifier='DemoMDLGraph',
                                    aTemplate=templateGraphPath,
                                    copyInternalReferencedObjects=False)

        depDemoCreation = sbsDoc.getDependencyFromPath(demoCreationPath)
        self.assertIsInstance(depDemoCreation, substance.SBSDependency)
        self.assertEqual(len(aGraph.getAllReferencesOnDependency(aDependency=depDemoCreation)), 1)

        sbsDoc.createMDLGraph(aGraphIdentifier='DemoMDLGraph', aTemplate=templateGraphPath)
        sbsDoc.createMDLGraph(aGraphIdentifier='DemoMDLGraph', aTemplate=templateGraphPath)

        # Template from the template list
        mdlGraph = sbsDoc.createMDLGraph(aGraphIdentifier='mdlFromTemplate', aTemplate=mdl.mdlenum.MDLGraphTemplateEnum.DIELECTRIC_IOR)
        self.assertIsInstance(mdlGraph, mdl.MDLGraph)

        # Final check
        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 1)
        self.assertEqual(len(sbsDoc.getSBSResourceList()), 1)
        self.assertEqual(len(sbsDoc.getSBSGroupList()), 1)
        self.assertEqual(len(sbsDoc.getSBSGraphList()), 1)
        self.assertEqual(len(sbsDoc.getMDLGraphList()), 4)
        self.assertEqual(len(sbsDoc.getSBSFunctionList()), 0)
        self.assertEqual(len(sbsDoc.getAllInternalReferences()), 5)
        self.assertEqual(len(mdlGraph.getAllInputGroups()), 3)

        sbsDoc.writeDoc()
        resDoc = substance.SBSDocument(context.Context(), aFileAbsPath=sbsDoc.mFileAbsPath)
        self.assertTrue(resDoc.parseDoc())

        refDocPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/refGraphMDLFromTemplate.sbs')
        refDoc = substance.SBSDocument(context.Context(), aFileAbsPath=refDocPath)
        self.assertTrue(refDoc.parseDoc())
        self.assertTrue(refDoc.equals(resDoc))

        os.remove(sbsDoc.mFileAbsPath)


    def test_ChangeInternalPath(self):
        """
        This test checks the ability to change the internal path of a Graph/Function/Resource/Group,\
        by changing its identifier, or moving it under another folder
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule,u'./resources/resultDemoCreation.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/testChangeInternalPath.sbs')

        sbsDoc = substance.SBSDocument(context.Context(), fileAbsPath)
        sbsDoc.parseDoc()

        # Add a MDL graph given a template from resultDemoCreationMDL.sbs
        mdlTemplatePath = python_helpers.getAbsPathFromModule(testModule, u'./resources/resultDemoCreationMDL.sbs')
        mdlTemplatePath = mdlTemplatePath.replace('\\', '/') + '/DemoMDLGraph'

        mdlGraph = sbsDoc.createMDLGraph(aTemplate=mdlTemplatePath)
        self.assertIsInstance(mdlGraph, mdl.MDLGraph)

        aGroup = sbsDoc.getSBSGroup('Bitmaps')
        aGraph = sbsDoc.getSBSGraph('MyGraph')
        aSubGraph = sbsDoc.getSBSGraph('MySubGraph')
        aSubGraphMDL = sbsDoc.getSBSGraph('SBSGraph')
        aFct = sbsDoc.getSBSFunction('MyFunction')
        aRes = sbsDoc.getSBSResource('SD_Icon_Color')
        aResIES = sbsDoc.getSBSResource('pkg:///Resources/Comet')

        self.assertTrue(aRes.getPkgResourcePath().startswith('pkg:///MyResources/Bitmaps/SD_Icon_Color'))
        sbsDoc.moveObjectUnderGroup(aObject=aGroup, aGroup=None)
        self.assertTrue(aRes.getPkgResourcePath().startswith('pkg:///Bitmaps/SD_Icon_Color'))
        sbsDoc.moveObjectUnderGroup(aObject=aResIES, aGroup='pkg:///Bitmaps')

        newGroup = sbsDoc.createGroup(aGroupIdentifier='NewGroup')
        sbsDoc.moveObjectUnderGroup(aObject=aSubGraph, aGroup=newGroup)

        rootGroup = sbsDoc.createGroup(aGroupIdentifier='Root')
        sbsDoc.moveObjectUnderGroup(aObject=aGraph, aGroup=rootGroup)
        sbsDoc.moveObjectUnderGroup(aObject=aFct, aGroup=rootGroup)
        sbsDoc.moveObjectUnderGroup(aObject=mdlGraph, aGroup=rootGroup)
        sbsDoc.moveObjectUnderGroup(aObject=aSubGraphMDL, aGroup=rootGroup)
        sbsDoc.moveObjectUnderGroup(aObject=newGroup, aGroup=rootGroup)

        resGroup = sbsDoc.getObject('pkg:///MyResources')
        self.assertTrue(sbsDoc.removeObject('pkg:///MyResources'))
        self.assertTrue(sbsDoc.removeObject('pkg:///Resources'))

        with self.assertRaises(SBSImpossibleActionError):   # Invalid path
            self.assertTrue(sbsDoc.removeObject('pkg:///invalid'))
        with self.assertRaises(SBSImpossibleActionError):   # Invalid path
            self.assertTrue(sbsDoc.removeObject('pkg:///MyGraph'))
        with self.assertRaises(SBSImpossibleActionError):   # Invalid UID
            self.assertTrue(sbsDoc.removeObject('1234567890'))
        with self.assertRaises(SBSImpossibleActionError):   # Invalid object, has already been removed
            self.assertTrue(sbsDoc.removeObject(resGroup))

        self.assertEqual(sbsDoc.setObjectIdentifier(aObject=aGraph.mUID, aIdentifier='MyFunction'), 'MyFunction_1')
        self.assertEqual(sbsDoc.setObjectIdentifier(aObject=aGraph.mUID, aIdentifier='MyFunction_1'), 'MyFunction_1')
        self.assertEqual(sbsDoc.setObjectIdentifier(aObject=aGraph, aIdentifier=u'ütf-8?'), u'ütf-8_')
        self.assertEqual(sbsDoc.setObjectIdentifier(aObject=aGraph, aIdentifier=u'ütf-8?'), u'ütf-8_')
        self.assertEqual(sbsDoc.setObjectIdentifier(aObject=rootGroup, aIdentifier=u'rööt'), u'rööt')

        # Check final Substance
        self.assertEqual(len(sbsDoc.getSBSGroupList()), 3)
        self.assertEqual(len(sbsDoc.getSBSGraphList()), 3)
        self.assertEqual(len(sbsDoc.getSBSFunctionList()), 1)
        self.assertEqual(len(sbsDoc.getSBSResourceList()), 2)

        self.assertEqual(sbsDoc.getContent().mGraphs, None)
        self.assertEqual(sbsDoc.getContent().mResources, None)
        self.assertEqual(sbsDoc.getContent().mFunctions, None)
        self.assertEqual(len(sbsDoc.getContent().mGroups), 2)
        self.assertIsInstance(sbsDoc.getObjectFromInternalPath(u'pkg:///Bitmaps'), substance.SBSGroup)
        self.assertIsInstance(sbsDoc.getObjectFromInternalPath(u'pkg:///rööt'), substance.SBSGroup)
        self.assertIsInstance(sbsDoc.getObjectFromInternalPath(u'pkg:///rööt/ütf-8_'), graph.SBSGraph)
        self.assertIsInstance(sbsDoc.getObjectFromInternalPath(u'pkg:///rööt/NewGroup'), substance.SBSGroup)
        self.assertIsInstance(sbsDoc.getObjectFromInternalPath(u'pkg:///rööt/NewGroup/MySubGraph'), graph.SBSGraph)
        self.assertIsInstance(sbsDoc.getObjectFromInternalPath(u'pkg:///rööt/MyFunction'), graph.SBSFunction)

        self.assertEqual(len(sbsDoc.getAllInternalReferences()), 5)
        self.assertEqual(len(sbsDoc.getAllInternalReferences(aInternalPath=u'pkg:///rööt/NewGroup/MySubGraph')), 1)
        self.assertEqual(len(sbsDoc.getAllInternalReferences(aInternalPath=u'pkg:///rööt/MyFunction')), 1)
        self.assertEqual(len(sbsDoc.getAllInternalReferences(aInternalPath='pkg:///Bitmaps/SD_Icon_Color')), 1)
        self.assertEqual(len(sbsDoc.getAllInternalReferences(aInternalPath='pkg:///Bitmaps/Comet')), 1)

        sbsDoc.writeDoc(aNewFileAbsPath=destAbsPath, aUpdateRelativePaths=True)
        os.remove(sbsDoc.mFileAbsPath)
