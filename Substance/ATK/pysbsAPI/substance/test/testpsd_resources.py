# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import shutil
import sys

from pysbs import python_helpers
from pysbs import sbsgenerator
from pysbs import sbsenum
from pysbs import context
from pysbs import substance
from pysbs import psdparser


testModule = sys.modules[__name__]

class SBSPSDResourceTests(unittest.TestCase):

    def openTestDocument(self, aFilename):
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/' + aFilename)
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        self.assertTrue(sbsDoc.parseDoc())
        return sbsDoc

    def test_CreateLinkedResourcePsd(self):
        """
        This test checks the creation of linked PSD resource
        """
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testLinkPsdResource.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath=destAbsPath,
                                                aGraphIdentifier='Graph')
        aPsdPath = sbsDoc.buildAbsPathFromRelToMePath('PsdResource.0.psd')
        aResource = sbsDoc.createLinkedResource(aResourcePath=aPsdPath,
                                                aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP,
                                                aAttributes={
                                                    sbsenum.AttributesEnum.Description: 'This is a <PSD> resource'},
                                                aParentFolder=None)
        self.assertIsInstance(aResource, substance.resource.SBSResource)
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.Description), 'This is a <PSD> resource')

        aPsdPath2 = sbsDoc.buildAbsPathFromRelToMePath('PsdRaw.psd')
        aResourceRaw = sbsDoc.createLinkedResource(aResourcePath=aPsdPath2,
                                                   aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP)
        self.assertIsInstance(aResourceRaw, substance.resource.SBSResource)

        aGroup = sbsDoc.getSBSGroup(aResource.mIdentifier + '_Resources')
        aGraph = sbsDoc.getSBSGraph('Graph')
        self.assertEqual(sbsDoc.getObjectInternalPath(aUID=aResource.mUID, addDependencyUID=False), 'pkg:///PsdResource_0')
        self.assertEqual(sbsDoc.getObjectInternalPath(aUID=aGroup.mUID, addDependencyUID=False),
                          'pkg:///PsdResource_0_Resources')

        aPos = [0, 0, 0]
        xOffset = [150, 0, 0]

        psdLayers = psdparser.getLayers(sbsDoc.mContext, aPsdFileAbsPath=aPsdPath)
        for aLayer in aGroup.getSBSResourceList():
            aPsdLayer = psdparser.getPsdLayerFromList(aPsdLayerList=psdLayers,
                                                      aLayerName=psdparser.getPsdLayerNameFromResource(aLayer))
            aNode = aGraph.createBitmapNode(sbsDoc,
                                            aResourcePath=aLayer.getPkgResourcePath(),
                                            aGUIPos=aPos,
                                            aResourceGroup=aGroup,
                                            aParameters={
                                                sbsenum.CompNodeParamEnum.COLOR_MODE: aPsdLayer.getFilterParamColor(),
                                                sbsenum.CompNodeParamEnum.OUTPUT_SIZE: aPsdLayer.getFilterParamSize()},
                                            aInheritance={
                                                sbsenum.CompNodeParamEnum.OUTPUT_SIZE: sbsenum.ParamInheritanceEnum.ABSOLUTE})

            self.assertIsNone(aLayer.getAttribute(sbsenum.AttributesEnum.Description))
            aPos = aNode.getOffsetPosition(xOffset)

        self.assertEqual(len(aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BITMAP)), 5)

        self.assertTrue(sbsDoc.writeDoc())
        resDoc = substance.SBSDocument(aContext=context.Context(), aFileAbsPath=destAbsPath)
        self.assertTrue(resDoc.parseDoc())

        allResources = resDoc.getSBSResourceList()
        self.assertEqual(len(allResources), 7)
        aGroup = resDoc.getSBSGroup(aGroupIdentifier='PsdResource_0_Resources')
        self.assertIsInstance(aGroup, substance.SBSGroup)
        psdResources = aGroup.getSBSResourceList()
        self.assertEqual(len(psdResources), 5)

        refDoc = self.openTestDocument('refCreatePsdResource.sbs')
        aRefGroup = refDoc.getSBSGroup(aGroupIdentifier='PsdResource_0_Resources')
        self.assertTrue(aRefGroup.equals(aGroup))

        self.assertTrue(refDoc.getSBSGraph('Graph').equals(resDoc.getSBSGraph('Graph')))
        os.remove(destAbsPath)


    def test_CreateImportedResourcePsd(self):
        """
        This test checks the creation of linked PSD resource
        """
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testImportPsdResource.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath=destAbsPath,
                                                aGraphIdentifier='Graph')
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath('PsdResource.0.psd')
        aResource = sbsDoc.createImportedResource(aResourcePath=aRelPath, aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP)
        self.assertIsInstance(aResource, substance.resource.SBSResource)

        # Check that the folder .resources has been created
        aResourceDir = sbsDoc.buildAbsPathFromRelToMePath('testImportPsdResource.resources')
        self.assertTrue(os.path.isdir(aResourceDir))
        self.assertTrue(os.path.exists(aResource.mFileAbsPath))

        self.assertTrue(sbsDoc.writeDoc())
        resDoc = substance.SBSDocument(aContext=context.Context(), aFileAbsPath=destAbsPath)
        self.assertTrue(resDoc.parseDoc())

        # Check the number of resources created
        allResources = resDoc.getSBSResourceList()
        self.assertEqual(len(allResources), 6)
        aGroup = resDoc.getSBSGroup(aGroupIdentifier='PsdResource_0_Resources')
        self.assertIsInstance(aGroup, substance.SBSGroup)
        psdResources = aGroup.getSBSResourceList()
        self.assertEqual(len(psdResources), 5)

        # Compare the result with the reference doc refImportPsdResource.sbs
        refDoc = self.openTestDocument('refImportPsdResource.sbs')
        aRefResources = refDoc.getSBSResourceList()

        for aRes, aRef in zip(allResources, aRefResources):
            self.assertEqual(aRes.mIdentifier, aRef.mIdentifier)
            self.assertEqual(aRes.mType, aRef.mType)
            self.assertEqual(aRes.mFormat, aRef.mFormat)
            self.assertTrue(os.path.exists(aRes.mFileAbsPath))
            self.assertTrue(os.path.exists(sbsDoc.buildAbsPathFromRelToMePath(aRes.getResolvedFilePath())))

        os.remove(destAbsPath)
        shutil.rmtree(aResourceDir)


    def test_CreateGraphFromTemplatePSD(self):
        """
        This test checks the ability to create a Substance graph from a template
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/graphFromTemplate.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), aFileAbsPath=fileAbsPath)

        # Template with PSD resources
        aGraph = sbsDoc.createGraph(aGraphIdentifier='Graph',
                                    aTemplate=sbsDoc.buildAbsPathFromRelToMePath('refCreatePsdResource.sbs/Graph'))
        self.assertEqual(len(aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BITMAP)), 5)
        self.assertEqual(len(sbsDoc.getSBSResourceList()), 6)

        # Final check
        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 0)
        self.assertEqual(len(sbsDoc.getSBSResourceList()), 6)
        self.assertEqual(len(sbsDoc.getSBSGroupList()), 2)
        self.assertEqual(len(sbsDoc.getSBSGraphList()), 1)
        self.assertEqual(len(sbsDoc.getMDLGraphList()), 0)
        self.assertEqual(len(sbsDoc.getSBSFunctionList()), 0)
        self.assertEqual(len(sbsDoc.getAllInternalReferences()), 5)

        sbsDoc.writeDoc()
        resDoc = substance.SBSDocument(context.Context(), aFileAbsPath=sbsDoc.mFileAbsPath)
        self.assertTrue(resDoc.parseDoc())

        refDocPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/refCreatePsdResource.sbs')
        refDoc = substance.SBSDocument(context.Context(), aFileAbsPath=refDocPath)
        self.assertTrue(refDoc.parseDoc())
        resGraph = resDoc.getSBSGraph('Graph')
        refGraph = refDoc.getSBSGraph('Graph')
        self.assertTrue(refGraph.equals(resGraph))
        resGroup = resDoc.getSBSGroup('PsdResource_0_Resources')
        refGroup = refDoc.getSBSGroup('PsdResource_0_Resources')
        self.assertTrue(refGroup.equals(resGroup))

        os.remove(sbsDoc.mFileAbsPath)


if __name__ == '__main__':
    log.info("Test PSD Resources")
    unittest.main()
