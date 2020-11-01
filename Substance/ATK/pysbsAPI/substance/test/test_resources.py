# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import shutil
import sys

from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers
from pysbs import sbsgenerator
from pysbs import sbsenum
from pysbs import context
from pysbs import substance
from pysbs import compnode
from pysbs import graph

testModule = sys.modules[__name__]

class SBSResourceTests(unittest.TestCase):

    def openTestDocument(self, aFilename):
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/' + aFilename)
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        self.assertTrue(sbsDoc.parseDoc())
        return sbsDoc


    def test_CreateLinkedResource(self):
        """
        This test checks the creation of linked resources
        """
        sbsDoc = self.openTestDocument('testResources.sbs')
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath('Craters.png')
        aResource = sbsDoc.createLinkedResource(aResourcePath=aRelPath,
                                                  aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP,
                                                  aAttributes={sbsenum.AttributesEnum.Label:u'Cratères'})
        self.assertIsInstance(aResource, substance.resource.SBSResource)
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.Label), u'Cratères')
        self.assertIsNone(aResource.getAttribute(sbsenum.AttributesEnum.Author))
        aResource.setAttribute(sbsenum.AttributesEnum.UserTags, u'<one> &second \\t\'tag\'')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.UserTags), u'<one> &second \\t\'tag\'')

        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testCreateImportedResource.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destAbsPath))

        resDoc = self.openTestDocument('testCreateImportedResource.sbs')
        self.assertTrue(resDoc.equals(sbsDoc))
        os.remove(destAbsPath)

        # test linked with relative to cwd path
        sbsDoc = self.openTestDocument('testResources.sbs')
        aRelPath = 'resources/Craters.png'
        aResource = sbsDoc.createLinkedResource(aResourcePath=aRelPath,
                                                  aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP,
                                                  aAttributes={sbsenum.AttributesEnum.Label:u'Cratères'})
        self.assertIsInstance(aResource, substance.resource.SBSResource)
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.Label), u'Cratères')
        self.assertIsNone(aResource.getAttribute(sbsenum.AttributesEnum.Author))
        aResource.setAttribute(sbsenum.AttributesEnum.UserTags, u'<one> &second \\t\'tag\'')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.UserTags), u'<one> &second \\t\'tag\'')

        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testCreateImportedResource.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destAbsPath))

        resDoc = self.openTestDocument('testCreateImportedResource.sbs')
        self.assertTrue(resDoc.equals(sbsDoc))
        os.remove(destAbsPath)

        sbsDoc = self.openTestDocument('testResources.sbs')
        udimMaps =  python_helpers.getAbsPathFromModule(testModule, './resources/chars_bot42_shade_1001_BaseColor.png')
        aResUdim = sbsDoc.createLinkedResource(udimMaps, aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP, isUdim=True)
        self.assertIsInstance(aResUdim, substance.resource.SBSResource)
        self.assertEqual(aResUdim.mIdentifier, "chars_bot42_shade_[udim]_BaseColor")
        
        # test linked with relative to sbs package path
        sbsDoc = self.openTestDocument('testResources.sbs')
        aRelPath = 'Craters.png'
        aResource = sbsDoc.createLinkedResource(aResourcePath=aRelPath,
                                                aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP,
                                                aAttributes={sbsenum.AttributesEnum.Label:u'Cratères'},
                                                isRelToPackage=True)
        self.assertIsInstance(aResource, substance.resource.SBSResource)
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.Label), u'Cratères')
        self.assertIsNone(aResource.getAttribute(sbsenum.AttributesEnum.Author))
        aResource.setAttribute(sbsenum.AttributesEnum.UserTags, u'<one> &second \\t\'tag\'')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.UserTags), u'<one> &second \\t\'tag\'')

        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testCreateImportedResource.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destAbsPath))

        resDoc = self.openTestDocument('testCreateImportedResource.sbs')
        self.assertTrue(resDoc.equals(sbsDoc))
        os.remove(destAbsPath)

    def test_CreateLinkedOtherResource(self):
        res_path = python_helpers.getAbsPathFromModule(testModule, './resources/anOtherResource.json')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testCreateLinkedOtherResource.sbs')
        sbs_doc = sbsgenerator.createSBSDocument(context.Context(), destAbsPath)
        res = sbs_doc.createLinkedResource(res_path, sbsenum.ResourceTypeEnum.OTHER)
        same_res = sbs_doc.createLinkedResource(res_path, sbsenum.ResourceTypeEnum.NONE)
        sbs_doc.writeDoc()
        with open(sbs_doc.mFileAbsPath, 'r') as f:
            self.assertEqual('<type v=""/>' in f.readline(), True)
        os.remove(destAbsPath)

    def test_CreateImportedResource(self):
        """
        This test checks the creation of imported resources
        """
        sbsDoc = self.openTestDocument('testResources.sbs')
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath('Craters.png')
        aResource = sbsDoc.createImportedResource(aResourcePath=aRelPath,
                                                  aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP,
                                                  aAttributes={sbsenum.AttributesEnum.Label:u'Cratères'})
        self.assertIsInstance(aResource, substance.resource.SBSResource)
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.Label), u'Cratères')
        self.assertIsNone(aResource.getAttribute(sbsenum.AttributesEnum.Author))
        aResource.setAttribute(sbsenum.AttributesEnum.UserTags, u'<one> &second \\t\'tag\'')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.UserTags), u'<one> &second \\t\'tag\'')

        aResourceDir = sbsDoc.buildAbsPathFromRelToMePath('testResources.resources')
        self.assertTrue(os.path.isdir(aResourceDir))
        self.assertTrue(os.path.exists(aResource.mFileAbsPath))
        self.assertTrue(os.path.exists(sbsDoc.buildAbsPathFromRelToMePath(aResource.getResolvedFilePath())))
        self.assertTrue(os.path.isabs(aResource.mFileAbsPath))
        self.assertFalse(os.path.isabs(aResource.getResolvedFilePath()))

        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testCreateImportedResource.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destAbsPath))

        resDoc = self.openTestDocument('testCreateImportedResource.sbs')
        self.assertTrue(resDoc.equals(sbsDoc))

        os.remove(destAbsPath)
        shutil.rmtree(aResourceDir)

        # TODO:
        # test imported with relative to cwd

        # TODO:
        # test imported with relative to sbs package path

    def test_SetVariousBitmapAttribute(self):
        """
        test. setColorSpace, setPremultipliedAlpha, setCookedFormat
        """
        sbsDoc = self.openTestDocument('testResources.sbs')
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath('Craters.png')
        aResource = sbsDoc.createImportedResource(aResourcePath=aRelPath,
                                                  aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP,
                                                  aAttributes={sbsenum.AttributesEnum.Label:u'Cratères'})
        ctx = context.Context()
        ctx.getProjectMgr().setOcioConfigFilePath(python_helpers.getAbsPathFromModule(testModule, './resources/config.ocio'))
        aResource.setColorSpace("Rec2020", ctx)
        aResource.setCookedFormat(sbsenum.BitmapFormatEnum.JPG)
        aResource.setPremultipliedAlpha(False)
        sbsDoc.writeDoc(python_helpers.getAbsPathFromModule(testModule, './resources/tmp.sbs'))
        sbsDoc = self.openTestDocument('tmp.sbs')
        aResource = sbsDoc.getSBSResourceList()[0]
        self.assertEqual(aResource.mPremultipliedAlpha, "0")
        self.assertEqual(aResource.mColorSpace, "Rec2020")
        self.assertEqual(aResource.mCookedFormat, "4")
        os.remove(python_helpers.getAbsPathFromModule(testModule, './resources/tmp.sbs'))

    def test_CreateResourceSVG(self):
        """
        This test checks the creation of imported and linked resources SVG
        """
        sbsDoc = self.openTestDocument('testResources.sbs')
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath('SD_Icon_Color.svg')
        aResource = sbsDoc.createImportedResource(aResourcePath=aRelPath,
                                                  aResourceTypeEnum=sbsenum.ResourceTypeEnum.SVG)
        self.assertIsInstance(aResource, substance.resource.SBSResource)

        aGraph = sbsDoc.getSBSGraphList()[0]
        aGraph.createSvgNode(aSBSDocument=sbsDoc, aResourcePath=aRelPath)
        self.assertEqual(2, len(sbsDoc.getSBSResourceList()))

        aGraph.createSvgNode(aSBSDocument=sbsDoc, aResourcePath=aResource.getPkgResourcePath())
        self.assertEqual(2, len(sbsDoc.getSBSResourceList()))

        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testCreateImportedResourceSVG.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destAbsPath))

        resDoc = self.openTestDocument('testCreateImportedResourceSVG.sbs')
        refDoc = self.openTestDocument('refSVGResource.sbs')

        self.assertTrue(resDoc.equals(refDoc))
        os.remove(destAbsPath)


    def test_CreateResourceFont(self):
        """
        This test checks the creation of imported and linked resources of kind FONT
        """
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testFontResource.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath=destAbsPath, aGraphIdentifier=u'Héto<t$&oö')
        aRelPath = sbsDoc.buildAbsPathFromRelToMePath('FontResource.otf')
        aGraph = sbsDoc.getSBSGraph(u'Héto_t__oö')

        aResourceDir = sbsDoc.buildAbsPathFromRelToMePath('testFontResource.resources')
        if os.path.exists(aResourceDir):
            shutil.rmtree(aResourceDir)

        # Link a Font
        aResourceLinked = sbsDoc.createLinkedResource(aResourcePath=aRelPath,
                                                      aResourceTypeEnum=sbsenum.ResourceTypeEnum.FONT)
        self.assertIsInstance(aResourceLinked, substance.resource.SBSResource)

        # Import twice the same Font
        aResourceImported = sbsDoc.createImportedResource(aResourcePath=aRelPath,
                                                          aResourceTypeEnum=sbsenum.ResourceTypeEnum.FONT)
        self.assertIsInstance(aResourceImported, substance.resource.SBSResource)

        aResourceImported2 = sbsDoc.createImportedResource(aResourcePath=aRelPath,
                                                          aResourceTypeEnum=sbsenum.ResourceTypeEnum.FONT)
        self.assertIsInstance(aResourceImported2, substance.resource.SBSResource)
        self.assertEqual(3, len(sbsDoc.getSBSResourceList()))

        # Create two text nodes
        aTextNodeLink = aGraph.createTextNode(aFontFamily = aResourceLinked.getPkgResourcePath(),
                                              aParameters = {sbsenum.CompNodeParamEnum.TEXT:u'Il \'était" une fois\n<Link>'})
        self.assertIsInstance(aTextNodeLink, compnode.SBSCompNode)

        aTextNodeImport = aGraph.createTextNode(aFontFamily = aResourceImported.getPkgResourcePath(),
                                                aParameters = {sbsenum.CompNodeParamEnum.TEXT:u'Il \'était" une fois\n<Import>'})
        self.assertIsInstance(aTextNodeImport, compnode.SBSCompNode)

        # Check that the folder .resources has been created
        self.assertTrue(os.path.isdir(aResourceDir))
        self.assertTrue(os.path.exists(aResourceLinked.mFileAbsPath))
        self.assertTrue(os.path.exists(aResourceImported.mFileAbsPath))
        self.assertTrue(os.path.exists(aResourceImported2.mFileAbsPath))

        # Check serialization & deserialization
        self.assertTrue(sbsDoc.writeDoc())
        resDoc = self.openTestDocument('testFontResource.sbs')

        # Check resources
        aResource1 = resDoc.getSBSResource('FontResource')
        self.assertEqual(aResource1.mType, 'font')
        self.assertEqual(aResource1.mFormat, 'otf')
        self.assertEqual(aResource1.mFilePath, 'FontResource.otf')
        self.assertEqual(aResource1.getResolvedFilePath(), 'FontResource.otf')
        self.assertIsNone(aResource1.mSource)

        aResource1 = resDoc.getSBSResource('FontResource_1')
        self.assertEqual(aResource1.mType, 'font')
        self.assertEqual(aResource1.mFormat, 'otf')
        self.assertEqual(aResource1.getResolvedFilePath(), 'testFontResource.resources/FontResource.otf')
        self.assertIsNotNone(aResource1.mSource)

        aResource2 = resDoc.getSBSResource('FontResource_2')
        self.assertEqual(aResource2.mType, 'font')
        self.assertEqual(aResource2.mFormat, 'otf')
        self.assertEqual(aResource2.getResolvedFilePath(), 'testFontResource.resources/1-FontResource.otf')
        self.assertIsNotNone(aResource2.mSource)

        os.remove(destAbsPath)
        shutil.rmtree(aResourceDir)


    def test_RelocateResource(self):
        """
        This test checks relocating a resource
        """
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/relocateResource.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath=destAbsPath, aGraphIdentifier='Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')
        self.assertIsInstance(aGraph, graph.SBSGraph)

        fontRes = sbsDoc.createLinkedResource(sbsDoc.buildAbsPathFromRelToMePath('FontResource.otf'), aResourceTypeEnum=sbsenum.ResourceTypeEnum.FONT)
        aGraph.createTextNode(aFontFamily=fontRes.getPkgResourcePath())

        aGraph.createBitmapNode(aSBSDocument=sbsDoc, aResourcePath=sbsDoc.buildAbsPathFromRelToMePath('Craters.png'))
        linkedRes = sbsDoc.getSBSResource('Craters')

        aGraph.createSvgNode(aSBSDocument=sbsDoc, aResourcePath=sbsDoc.buildAbsPathFromRelToMePath('SD_Icon_Color.svg'))
        svgRes = sbsDoc.getSBSResource('SD_Icon_Color')

        importedRes = sbsDoc.createImportedResource(sbsDoc.buildAbsPathFromRelToMePath('Craters.png'), aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP)

        sceneRes = sbsDoc.createSceneResource(sbsDoc.buildAbsPathFromRelToMePath('cube_low.FBX'), aIdentifier="Cube", isUDIM=True)
        self.assertIsInstance(sceneRes, substance.SBSResourceScene)
        self.assertEqual(sceneRes.mIsUdim, '1')

        # Check invalid extension at resource creation
        with self.assertRaises(SBSImpossibleActionError):
            sbsDoc.createImportedResource(sbsDoc.buildAbsPathFromRelToMePath('Craters.png'), aResourceTypeEnum=sbsenum.ResourceTypeEnum.SVG)
        with self.assertRaises(SBSImpossibleActionError):
            sbsDoc.createLinkedResource(sbsDoc.buildAbsPathFromRelToMePath('Craters.png'), aResourceTypeEnum=sbsenum.ResourceTypeEnum.SCENE)

        # Check invalid cases at resource relocating
        with self.assertRaises(SBSImpossibleActionError):   # Imported resource
            sbsDoc.relocateResource(aResource=importedRes, aNewPath=sbsDoc.buildAbsPathFromRelToMePath('invalid.svg'))
        with self.assertRaises(IOError):                    # File not found
            sbsDoc.relocateResource(aResource=svgRes, aNewPath=sbsDoc.buildAbsPathFromRelToMePath('invalid.svg'))
        with self.assertRaises(SBSImpossibleActionError):   # Invalid extension
            sbsDoc.relocateResource(aResource=svgRes, aNewPath=sbsDoc.buildAbsPathFromRelToMePath('Craters.png'))
        with self.assertRaises(SBSImpossibleActionError):   # Invalid extension
            sbsDoc.relocateResource(aResource=linkedRes, aNewPath=sbsDoc.buildAbsPathFromRelToMePath('SD_Icon_Color.svg'))
        with self.assertRaises(SBSImpossibleActionError):   # Invalid extension
            sbsDoc.relocateResource(aResource=fontRes, aNewPath=sbsDoc.buildAbsPathFromRelToMePath('SD_Icon_Color.svg'))

        testRelocate = [(svgRes,   u'NüSVG.svg'),
                        (sceneRes, u'NüCube.FBX')]
        for t in testRelocate:
            newResPath = sbsDoc.buildAbsPathFromRelToMePath(t[1])
            shutil.copy(t[0].mFileAbsPath, newResPath)
            self.assertTrue(sbsDoc.relocateResource(t[0], newResPath))
            self.assertEqual(t[0].mFileAbsPath,  os.path.normpath(newResPath))
            self.assertEqual(t[0].mFilePath, t[1])

        self.assertTrue(sbsDoc.relocateResource(linkedRes.getPkgResourcePath(), aNewPath=sbsDoc.buildAbsPathFromRelToMePath('Craters.png')))

        self.assertTrue(sbsDoc.writeDoc())
        self.openTestDocument('relocateResource.sbs')

        os.remove(sbsDoc.mFileAbsPath)
        shutil.rmtree(os.path.join(sbsDoc.mDirAbsPath,'relocateResource.resources'))
        os.remove(svgRes.mFileAbsPath)
        os.remove(sceneRes.mFileAbsPath)


    def test_UdimResource(self):
        """
        This test checks operations related to a mesh resource with Udims
        """
        aContext = context.Context()
        sbsDoc = sbsgenerator.createSBSDocument(aContext, aFileAbsPath=python_helpers.getAbsPathFromModule(testModule, './resources/testSubstanceWithUdimMesh.sbs'),
                                                aGraphIdentifier='New_Graph')
        graph1 = sbsDoc.getSBSGraph(aGraphIdentifier='New_Graph')
        graph1.createOutputNode(aIdentifier='Output')
        graph2 = sbsDoc.createGraph(aGraphIdentifier='New_Graph', aTemplate=sbsDoc.getSBSGraphInternalPath(graph1.mUID, addDependencyUID=False))
        resMesh = sbsDoc.createSceneResource(aResourcePath = sbsDoc.buildAbsPathFromRelToMePath('cube_low.FBX'), isUDIM=True)

        resMesh.setMaterialMapEntries(aMaterialsList = [''], nbUVSet=1)
        matEntries = resMesh.getMaterialMapEntries()
        self.assertEqual(len(matEntries), 1)
        matMap = resMesh.getMaterialMapEntries()[0]
        self.assertEqual(matMap, matEntries[0])
        self.assertIsInstance(matMap, substance.SBSSceneMaterialMapEntry)

        path1 = sbsDoc.getSBSGraphInternalPath(aUID=graph1.mUID, addDependencyUID=True)
        path2 = sbsDoc.getSBSGraphInternalPath(aUID=graph2.mUID, addDependencyUID=True)

        # Check invalid UV-set
        with self.assertRaises(SBSImpossibleActionError):
            matMap.assignDefaultSBSGraph(aGraphPath=path2, aUVSet=2)

        # Assign all to graph2
        assign = matMap.assignDefaultSBSGraph(aGraphPath=path2)
        self.assertEqual(len(matMap.getUVSetMaterialMapEntries()), 1)
        self.assertEqual(assign.mUVTiles, 'all')
        self.assertEqual(assign.getGraphPath(), path2)

        # Assign all to graph1 => check that we still have only one entry
        assign = matMap.assignDefaultSBSGraph(aGraphPath=path1)
        self.assertEqual(len(matMap.getUVSetMaterialMapEntries()), 1)
        self.assertEqual(assign.mUVTiles, 'all')
        self.assertEqual(assign.getGraphPath(), path1)

        # Assign '1001' to graph2 => check that we have 2 entries, correctly set
        assign = matMap.assignSBSGraphToUVTile(aGraphPath=path2, aUVTile='1001')
        self.assertEqual(len(matMap.getUVSetMaterialMapEntries()), 2)
        self.assertEqual(assign.mUVTiles, '0x0')
        self.assertEqual(assign.getGraphPath(), path2)

        # Assign '1001','1002' to graph2 => check that we have 3 entries
        assign = matMap.assignSBSGraphToUVTiles(aGraphPath=path2, aUVTileList=[(0,0),(1,0)])
        self.assertEqual(len(matMap.getUVSetMaterialMapEntries()), 3)
        self.assertEqual(len(assign), 2)
        self.assertEqual(assign[0].mUVTiles, '0x0')
        self.assertEqual(assign[0].getGraphPath(), path2)
        self.assertEqual(assign[1].mUVTiles, '1x0')
        self.assertEqual(assign[1].getGraphPath(), path2)

        # Assign '1011','1012' to graph1 => check the entries by graph
        assign = matMap.assignSBSGraphToUVTiles(aGraphPath=path1, aUVTileList=['1011','1012'])
        self.assertEqual(len(matMap.getUVSetMaterialMapEntries()), 5)
        self.assertEqual(len(assign), 2)
        self.assertEqual(matMap.getAllUVTilesAssociatedToGraph(path1, sbsenum.UVTileFormat.UV_LIST), ['all', [0,1], [1,1]])
        self.assertEqual(matMap.getAllUVTilesAssociatedToGraph(path2, sbsenum.UVTileFormat.UDIM), ['1001','1002'])

        # Remove assignments
        self.assertFalse(matMap.removeUVTileAssignation(aUVTile='u1_v2'))
        self.assertEqual(matMap.removeUVTilesAssignation(aUVTileList=['1011','1012']), 2)
        self.assertEqual(matMap.removeDefaultUVTileAssignation(), True)
        self.assertEqual(matMap.removeAllAssignationsToGraph(aGraphPath=path2), 2)
        self.assertEqual(matMap.getAllUVTilesAssociatedToGraph(path1), [])

        matMap.assignDefaultSBSGraph(aGraphPath=path1)
        matMap.assignSBSGraphToUVTile(aGraphPath=path2, aUVTile='1001')

        # Write this document
        sbsDoc.writeDoc()

        # Open reference doc created with SD
        refDoc = self.openTestDocument('refWithUdimMesh.sbs')
        self.assertTrue(refDoc.parseDoc)
        # Check serialization / deserialization keeps everything
        self.assertTrue(refDoc.writeDoc(refDoc.buildAbsPathFromRelToMePath('checkWithUdimMesh.sbs')))
        checkDoc = self.openTestDocument('checkWithUdimMesh.sbs')
        self.assertTrue(checkDoc.parseDoc)
        self.assertTrue(refDoc.equals(checkDoc))

        # Check the material map assignation
        refMeshRes = refDoc.getSBSResourceList()[0]
        self.assertIsInstance(refMeshRes, substance.SBSResourceScene)
        refMatMap = refMeshRes.getMaterialMapEntries()[0]
        self.assertTrue(matMap.equals(refMatMap))

        os.remove(checkDoc.mFileAbsPath)
        os.remove(sbsDoc.mFileAbsPath)

if __name__ == '__main__':
    log.info("Test Resources")
    unittest.main()
