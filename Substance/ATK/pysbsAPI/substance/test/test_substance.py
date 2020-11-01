# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import shutil
import sys
import datetime

from pysbs.api_exceptions import SBSImpossibleActionError, SBSIncompatibleVersionError, SBSUninitializedError, \
    SBSMissingDependencyError, SBSMetaDataTreeNameConflict
from pysbs import python_helpers
from pysbs import common_interfaces
from pysbs import sbsgenerator
from pysbs import sbsenum
from pysbs import context
from pysbs import substance
from pysbs import graph
from pysbs import compnode
from pysbs import sbsexporter

import pysbs_demos

testModule = sys.modules[__name__]


class SBSSubstanceTests(unittest.TestCase):

    def test_UniqueIdentifier(self):
        """
        This test checks the uniqueness of identifiers on SBSContent, SBSGraph, SBSFunction
        """
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './myDoc.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath, 'Id')
        aGraph = sbsDoc.getSBSGraph('Id')
        aGraph2 = sbsDoc.createGraph('Id')
        self.assertEqual(aGraph2.mIdentifier, 'Id_1')
        aGraph3 = sbsDoc.createGraph('Id_1')
        self.assertEqual(aGraph3.mIdentifier, 'Id_2')
        aGraph4 = sbsDoc.createGraph('Id[1]')
        self.assertEqual(aGraph4.mIdentifier, 'Id[1]')

        aGroup1 = sbsDoc.createGroup('Id_1')
        self.assertEqual(aGroup1.mIdentifier, 'Id_3')

        aGroup2 = sbsDoc.createGroup('Id_1', aParentFolder=aGroup1)
        self.assertEqual(aGroup2.mIdentifier, 'Id_1')
        aGraph4 = sbsDoc.createGraph('Id', aParentFolder=aGroup1)
        self.assertEqual(aGraph4.mIdentifier, 'Id')

        aFct1 = sbsDoc.createFunction('Id', aParentFolder=aGroup1.mIdentifier)
        self.assertEqual(aFct1.mIdentifier, 'Id_2')

        aFct2 = sbsDoc.createFunction('Id_1', 'NewGroup')
        self.assertEqual(aFct2.mIdentifier, 'Id_1')

        aGraph.createInputNode('MyInput')
        self.assertEqual(aGraph.mParamInputs[-1].mIdentifier, 'MyInput')
        aGraph.createInputNode('MyInput')
        self.assertEqual(aGraph.mParamInputs[-1].mIdentifier, 'MyInput_1')
        aGraph.createInputNode('MyInput')
        self.assertEqual(aGraph.mParamInputs[-1].mIdentifier, 'MyInput_2')
        aGraph.createInputNode('MyInput_1')
        self.assertEqual(aGraph.mParamInputs[-1].mIdentifier, 'MyInput_3')
        aGraph.createInputNode('MyInput_4')
        self.assertEqual(aGraph.mParamInputs[-1].mIdentifier, 'MyInput_4')

        aGraph.createOutputNode('MyOutput')
        self.assertEqual(aGraph.mGraphOutputs[-1].mIdentifier, 'MyOutput')
        aGraph.createOutputNode('Id')
        self.assertEqual(aGraph.mGraphOutputs[-1].mIdentifier, 'Id')
        aGraph.createOutputNode('MyInput')
        self.assertEqual(aGraph.mGraphOutputs[-1].mIdentifier, 'MyInput')

        aGraph.createOutputNode('MyOutput')
        self.assertEqual(aGraph.mGraphOutputs[-1].mIdentifier, 'MyOutput_1')
        aGraph.createOutputNode('MyOutput_2')
        self.assertEqual(aGraph.mGraphOutputs[-1].mIdentifier, 'MyOutput_2')


    def test_Dependencies(self):
        """
        This test checks the creation of dependencies
        """
        aDestPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDependencies.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath=aDestPath, aGraphIdentifier='Graph1')
        aGraph1 = sbsDoc.getSBSGraph('Graph1')
        aGraph2 = sbsDoc.createGraph(aGraphIdentifier='Graph2')

        aResourcePath = r'sbs://'
        aPath = aResourcePath + r'auto_levels.sbs'
        aGraph1.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath)
        aGraph2.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath)
        aPath = os.path.join(sbsDoc.mContext.getUrlAliasMgr().getAliasAbsPath('sbs'), 'auto_levels.sbs')
        aGraph2.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath+'/auto_levels')

        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 1)

        aPath = sbsDoc.buildAbsPathFromRelToMePath(r'testResources.sbs')
        aGraph1.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath)
        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 2)

        aPath += '/New_Graph'
        aGraph1.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath)
        aGraph2.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath)
        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 2)

        aPath += '__'
        with self.assertRaises(SBSMissingDependencyError):
            aGraph1.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath)
        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 2)

        aPath = sbsDoc.buildAbsPathFromRelToMePath(r'testResources2.sbs')
        aGraph1.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc, aPath = aPath)
        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 3)


    def test_WriteToFolder(self):
        """
        This test checks the fact to write a document into a different path, and the changes in the relative paths
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refWriteToFolder/resultDemoCreation.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testChangeFolder.sbs')

        doc = substance.SBSDocument(context.Context(), fileAbsPath)
        self.assertTrue(doc.parseDoc())
        self.assertTrue(doc.writeDoc(aNewFileAbsPath=destAbsPath, aUpdateRelativePaths=True))

        docRef = substance.SBSDocument(context.Context(), fileAbsPath)
        self.assertTrue(docRef.parseDoc())
        docDest = substance.SBSDocument(context.Context(), destAbsPath)
        self.assertTrue(docDest.parseDoc())

        resourceListRef = docRef.getSBSResourceList()
        resourceListDest = docDest.getSBSResourceList()
        for (aResRef, aResDest) in zip(resourceListRef, resourceListDest):
            self.assertEqual(aResRef.mFileAbsPath, aResDest.mFileAbsPath)
            self.assertTrue(os.path.isfile(docDest.mContext.getUrlAliasMgr().toAbsPath(aResDest.mFilePath, docDest.mDirAbsPath)))

        depListRef = docRef.getSBSDependencyList()
        depListDest = docDest.getSBSDependencyList()
        for (aDepRef, aDepDest) in zip(depListRef, depListDest):
            self.assertEqual(aDepRef.mFileAbsPath, aDepDest.mFileAbsPath)
            self.assertTrue(os.path.isfile(docDest.mContext.getUrlAliasMgr().toAbsPath(aDepDest.mFilename, docDest.mDirAbsPath)))

        os.remove(destAbsPath)

        # Check with an invalid folder
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './invalidFolder/testChangeFolder.sbs')
        with self.assertRaises(IOError):
            doc.writeDoc(aNewFileAbsPath=destAbsPath, aUpdateRelativePaths=False)
        with self.assertRaises(IOError):
            doc.writeDoc(aNewFileAbsPath=destAbsPath, aUpdateRelativePaths=True)


    def test_MissingDependency(self):
        """
        This test checks the behavior when parsing a substance with missing dependencies
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testMissingDependencies.sbs')
        doc = substance.SBSDocument(context.Context(), fileAbsPath)
        self.assertTrue(doc.parseDoc())


    def test_ExportWithDependenciesNoAlias(self):
        """
        This test checks the export of a package with its dependencies, without any alias.
        It also checks the export as an archive.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testExportWithDep.sbs')
        exportPath = python_helpers.getAbsPathFromModule(testModule, './resources/exportFolder')
        resourceSamplePath = python_helpers.getAbsPathFromModule(testModule, './resources/refExportWithDep')

        aContext = context.Context()
        aContext.getUrlAliasMgr().setAliasAbsPath(aAliasName = 'api', aAbsPath = resourceSamplePath)
        doc = substance.SBSDocument(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())

        aExporter = sbsexporter.SBSExporter()

        # Check bad behavior
        with self.assertRaises(SBSImpossibleActionError):
            aExporter.export(aSBSDocument=doc, aExportFolder=exportPath)

        # Export without alias
        with python_helpers.createTempFolders(exportPath):
            aExporter.export(aSBSDocument=doc, aExportFolder=exportPath)
            self.__checkPackagesAndResources(aExporter, doc, aNbDirectPackages=8,   aNbDirectResources=7,
                                                         aNbExportedPackages=5, aNbExportedResources=5,
                                                         aNbMissingPackages=0,  aNbMissingResources=0,
                                                         aNbTotalPackages=34,   aNbTotalResources=7)

        # Create archive
        with python_helpers.createTempFolders(exportPath):
            aExportedArchive = aExporter.export(aSBSDocument=doc, aExportFolder=exportPath, aBuildArchive=True)
            self.assertTrue(os.path.exists(aExportedArchive))                          # Check archive exists
            self.assertFalse(os.path.exists(os.path.splitext(aExportedArchive)[0]))    # Check export folder has been removed
            self.assertEqual(os.path.splitext(aExportedArchive)[1], '.zip')            # Check archive extension
            self.assertTrue(aExportedArchive.startswith(exportPath))                   # Check archive path
            aArchiveName = os.path.splitext(os.path.basename(aExportedArchive))[0]
            aDocName = os.path.splitext(os.path.basename(doc.mFileAbsPath))[0]
            self.assertTrue(aArchiveName.startswith(aDocName))                         # Check archive name
            datetime.datetime.strptime(aArchiveName[-20:], '_%Y_%m_%d_%H-%M-%S')       # Check archive timestamp format

            aExportedArchive = aExporter.export(aSBSDocument=doc, aExportFolder=exportPath, aBuildArchive=True, aArchiveFormat='tar')
            self.assertTrue(os.path.exists(aExportedArchive))
            self.assertEqual(os.path.splitext(aExportedArchive)[1], '.tar')


    def test_ExportWithDependenciesOneAlias(self):
        """
        This test checks the export of a package with its dependencies, without one alias.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testExportWithDep.sbs')
        exportPath = python_helpers.getAbsPathFromModule(testModule, './resources/exportFolder')
        resourceSamplePath = python_helpers.getAbsPathFromModule(testModule, './resources/refExportWithDep')

        aContext = context.Context()
        aContext.getUrlAliasMgr().setAliasAbsPath(aAliasName = 'api', aAbsPath = resourceSamplePath)
        doc = substance.SBSDocument(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())

        # Export with alias 'api' only
        aExporter = sbsexporter.SBSExporter()
        with python_helpers.createTempFolders(exportPath):
            aExporter.export(aSBSDocument=doc, aExportFolder=exportPath, aAliasesToExport=['api'])
            self.__checkPackagesAndResources(aExporter, doc, aNbDirectPackages=8,   aNbDirectResources=7,
                                                         aNbExportedPackages=9, aNbExportedResources=6,
                                                         aNbMissingPackages=0,  aNbMissingResources=0,
                                                         aNbTotalPackages=34,   aNbTotalResources=7)

    def test_ExportWithDependenciesAllAlias(self):
        """
        This test checks the export of a package with its dependencies, without all aliases.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testExportWithDep.sbs')
        exportPath = python_helpers.getAbsPathFromModule(testModule, './resources/exportFolder')
        resourceSamplePath = python_helpers.getAbsPathFromModule(testModule, './resources/refExportWithDep')

        aContext = context.Context()
        aContext.getUrlAliasMgr().setAliasAbsPath(aAliasName = 'api', aAbsPath = resourceSamplePath)
        doc = substance.SBSDocument(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())

        # Export with alias 'api' and 'sbs'
        with python_helpers.createTempFolders(exportPath):
            aExporter = sbsexporter.SBSExporter()
            aExporter.export(aSBSDocument=doc, aExportFolder=exportPath, aBuildArchive=False, aAliasesToExport=['sbs','api'])
            self.__checkPackagesAndResources(aExporter, doc, aNbDirectPackages=8,    aNbDirectResources=7,
                                                         aNbExportedPackages=34, aNbExportedResources=6,
                                                         aNbMissingPackages=0,   aNbMissingResources=0,
                                                         aNbTotalPackages=34,    aNbTotalResources=7)


    def test_ExportWithDependenciesMissingResources(self):
        """
        This test checks the export of a package with its dependencies, having missing dependencies and resources.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testExportWithDep.sbs')
        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/invalidRefSubstance.sbs')
        exportPath = python_helpers.getAbsPathFromModule(testModule, './resources/exportFolder')
        resourceSamplePath = python_helpers.getAbsPathFromModule(testModule, './resources/refExportWithDep')

        aContext = context.Context()
        aContext.getUrlAliasMgr().setAliasAbsPath(aAliasName = 'api', aAbsPath = resourceSamplePath)
        doc = substance.SBSDocument(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())

        # Change the path of one resource to make it invalid
        aResourceCrater = doc.getSBSResource(aResourceIdentifier = 'Craters')
        self.assertIsInstance(aResourceCrater, substance.SBSResource)
        aResourceCrater.mFilePath = aResourceCrater.mFilePath.replace('Craters', 'NoCraters')
        aResourceCrater.mFileAbsPath = aResourceCrater.mFileAbsPath.replace('Craters', 'NoCraters')

        # Change the path of one dependency to make it invalid
        aDep = doc.getDependencyFromPath(aPath='./aSubstanceWithSBSARDep.sbs')
        self.assertIsInstance(aDep, substance.SBSDependency)
        aDep.mFilename = aDep.mFilename.replace('aSubstanceWithSBSARDep', 'Invalid')
        aDep.mFileAbsPath = aDep.mFileAbsPath.replace('aSubstanceWithSBSARDep', 'Invalid')

        # Change the path of one dependency to make it invalid
        aDep = doc.getDependencyFromPath(aPath='api://resultTerrainMultiFractal.sbs')
        self.assertIsInstance(aDep, substance.SBSDependency)
        aDep.mFilename = aDep.mFilename.replace('resultTerrainMultiFractal', 'Invalid')
        aDep.mFileAbsPath = aDep.mFileAbsPath.replace('resultTerrainMultiFractal', 'Invalid')

        self.assertTrue(doc.writeDoc(aNewFileAbsPath=destAbsPath))

        aContext2 = context.Context()
        aContext2.getUrlAliasMgr().setAliasAbsPath(aAliasName = 'api', aAbsPath = resourceSamplePath)
        doc2 = substance.SBSDocument(aContext2, destAbsPath)
        self.assertTrue(doc2.parseDoc())

        aExporter = sbsexporter.SBSExporter()

        # Export with one missing resource
        with python_helpers.createTempFolders(exportPath):
            aExporter.export(aSBSDocument=doc2, aExportFolder=exportPath, aAliasesToExport=['api'])
            self.__checkPackagesAndResources(aExporter, doc, aNbDirectPackages=8,   aNbDirectResources=7,
                                                         aNbExportedPackages=6, aNbExportedResources=5,
                                                         aNbMissingPackages=2,  aNbMissingResources=1,
                                                         aNbTotalPackages=34,   aNbTotalResources=7)
        os.remove(destAbsPath)



    def test_IncompatibleSBS(self):
        """
        This test checks that a package created with a previous version of Designer raises an exception at Parse.
        """
        # Check opening an old package
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/alveolus_SD5.sbs')
        aContext = context.Context()
        doc = substance.SBSDocument(aContext, fileAbsPath)
        with self.assertRaises(SBSIncompatibleVersionError):
            doc.parseDoc()
        self.assertIsNone(aContext.getPackage(fileAbsPath))

        # Check adding an old package as an instance into a SBSDocument
        newPackagePath = python_helpers.getAbsPathFromModule(testModule, './resources/test_NewPackage.sbs')
        newDoc = sbsgenerator.createSBSDocument(aContext, aFileAbsPath = newPackagePath, aGraphIdentifier = 'MyGraph')
        aGraph = newDoc.getSBSGraph('MyGraph')
        aInstancePath = os.path.join(fileAbsPath, 'alveolus')
        with self.assertRaises(SBSMissingDependencyError):
            aGraph.createCompInstanceNodeFromPath(aSBSDocument = newDoc, aPath = aInstancePath)


    def test_UnparsedSBS(self):
        """
        This test checks that an exception is raised when requesting info of a package that has not been parsed yet.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testResources.sbs')
        aContext = context.Context()
        doc = substance.SBSDocument(aContext, fileAbsPath)
        with self.assertRaises(SBSUninitializedError):      doc.getSBSGraph('Graph')
        with self.assertRaises(SBSUninitializedError):      doc.getResourcePathList()
        with self.assertRaises(SBSUninitializedError):      doc.getDependencyFromPath('./dep.sbs')
        with self.assertRaises(SBSUninitializedError):      doc.createGroup()
        with self.assertRaises(SBSUninitializedError):      doc.createLinkedResource('res', sbsenum.ResourceTypeEnum.BITMAP)

        doc = substance.SBSDocument(aContext, 'newSubstance.sbs')
        with self.assertRaises(SBSUninitializedError):      doc.getContent()


    def test_UnicodePath(self):
        failing_path = u'sbs://multi_material_blend.sbs'
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/fail.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(),
                                                aFileAbsPath=fileAbsPath,
                                                aGraphIdentifier='ComposeStyles')
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier='ComposeStyles')
        composer = aGraph.createCompInstanceNodeFromPath(sbsDoc, aPath=failing_path)
        self.assertIsInstance(composer, compnode.SBSCompNode)

        testDir = python_helpers.getAbsPathFromModule(testModule, u'./resources/tàèt')
        rscFile = sbsDoc.buildAbsPathFromRelToMePath(u'Craters.png')
        destPath = os.path.join(testDir, u'àçé_.bmp')
        with python_helpers.createTempFolders(testDir):
            shutil.copy(rscFile, destPath)
            aResource = sbsDoc.createLinkedResource(aResourcePath=destPath, aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP)
            self.assertEqual(aResource.mFilePath, u'tàèt/àçé_.bmp')


    def test_CreateGraphFromTemplate(self):
        """
        This test checks the ability to create a Substance graph from a template
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/graphFromTemplate.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), aFileAbsPath=fileAbsPath)

        # Template with instances from alias sbs, and output nodes
        aGraph = sbsDoc.createGraph(aGraphIdentifier='copiedScanMetallicRoughness',
                                    aTemplate=sbsenum.GraphTemplateEnum.SCAN_PBR_SPECULAR_GLOSSINESS,
                                    aParameters={sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.OutputFormatEnum.FORMAT_32BITS_FLOAT,
                                                 sbsenum.CompNodeParamEnum.OUTPUT_SIZE:[sbsenum.OutputSizeEnum.SIZE_1024,sbsenum.OutputSizeEnum.SIZE_1024]},
                                    aInheritance={sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.ParamInheritanceEnum.ABSOLUTE,
                                                  sbsenum.CompNodeParamEnum.OUTPUT_SIZE: sbsenum.ParamInheritanceEnum.ABSOLUTE})
        self.assertEqual(len(aGraph.getAllOutputNodes()), 5)
        self.assertEqual(len(aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.COMPINSTANCE)), 5)
        self.assertEqual(len(aGraph.getNodeList()), 12)

        self.assertEqual(aGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE), '10 10')
        self.assertEqual(aGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT), str(sbsenum.OutputFormatEnum.FORMAT_32BITS_FLOAT))

        for output in ['diffuse','normal','height','specular','glossiness']:
            self.assertIsInstance((aGraph.getGraphOutput(aOutputIdentifier=output)), graph.SBSGraphOutput)
            self.assertIsInstance((aGraph.getGraphOutputNode(aOutputIdentifier=output)), compnode.SBSCompNode)

        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 5)

        # Template with imported resources
        aGraph = sbsDoc.createGraph(aGraphIdentifier='SVGResources',
                                    aTemplate=sbsDoc.buildAbsPathFromRelToMePath('refSVGResource.sbs/New_Graph'))
        self.assertEqual(len(aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.SVG)), 2)
        self.assertEqual(len(aGraph.getAllReferencesOnDependency(sbsDoc.getHimselfDependency())), 2)
        self.assertEqual(len(sbsDoc.getSBSResourceList()), 2)

        # Template from demoCreation
        demoCreationPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/refGraphFromTemplate/resultDemoCreation.sbs')
        templateGraphPath = demoCreationPath+'/MyGraph'
        aGraph = sbsDoc.createGraph(aGraphIdentifier='demoCreation',
                                    aTemplate=templateGraphPath,
                                    copyInternalReferencedObjects=False)
        depDemoCreation = sbsDoc.getDependencyFromPath(demoCreationPath)
        self.assertIsInstance(depDemoCreation, substance.SBSDependency)
        self.assertEqual(len(aGraph.getAllReferencesOnDependency(aDependency=depDemoCreation)), 2)

        sbsDoc.createGraph(aGraphIdentifier='demoCreation', aTemplate=templateGraphPath)
        sbsDoc.createGraph(aGraphIdentifier='demoCreation', aTemplate=templateGraphPath)

        # Final check
        self.assertEqual(len(sbsDoc.getSBSDependencyList()), 8)
        self.assertEqual(len(sbsDoc.getSBSResourceList()), 3)
        self.assertEqual(len(sbsDoc.getSBSGroupList()), 3)
        self.assertEqual(len(sbsDoc.getSBSGraphList()), 6)
        self.assertEqual(len(sbsDoc.getMDLGraphList()), 0)
        self.assertEqual(len(sbsDoc.getSBSFunctionList()), 1)
        self.assertEqual(len(sbsDoc.getAllInternalReferences()), 9)

        sbsDoc.writeDoc()
        resDoc = substance.SBSDocument(context.Context(), aFileAbsPath=sbsDoc.mFileAbsPath)
        self.assertTrue(resDoc.parseDoc())

        refDocPath = python_helpers.getAbsPathFromModule(testModule, u'./resources/refGraphFromTemplate.sbs')
        refDoc = substance.SBSDocument(context.Context(), aFileAbsPath=refDocPath)
        self.assertTrue(refDoc.parseDoc())
        self.assertTrue(refDoc.equals(resDoc))

        os.remove(sbsDoc.mFileAbsPath)


    def test_DefaultParentSize(self):
        """
        This simple test checks that a new SBS created with the API is correctly initialized
        """
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './testSimpleSBS.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), aFileAbsPath=docAbsPath, aGraphIdentifier='Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')
        size = aGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE)
        self.assertEqual(size, '0 0')
        self.assertIsNone(aGraph.getOption('defaultParentSize'))
        self.assertEqual(aGraph.getDefaultParentSize(), [8, 8])

        aGraph.setDefaultParentSize(aWidth=10, aHeight=6)
        self.assertEqual(aGraph.getDefaultParentSize(), [10, 6])
        aGraph.setDefaultParentSize(aWidth=8, aHeight=10)
        self.assertEqual(aGraph.getDefaultParentSize(), [8, 10])


    def test_PSDExporter(self):
        """
        This test checks that the PSD exporter options are correctly serialized
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/sbsPsdExporter.sbs')
        doc = substance.SBSDocument(context.Context(), fileAbsPath)
        self.assertTrue(doc.parseDoc())

        self.assertEqual(len(doc.getSBSGraph('New_Graph').getPsdExporterOptions()), 23)

        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testSbsPsdExporter.sbs')
        self.assertTrue(doc.writeDoc(aNewFileAbsPath=destAbsPath))
        resDoc = substance.SBSDocument(context.Context(), destAbsPath)
        self.assertTrue(resDoc.parseDoc())

        self.assertEqual(len(resDoc.getSBSGraph('New_Graph').getPsdExporterOptions()), 23)
        self.assertTrue(doc.equals(resDoc))
        os.remove(destAbsPath)

    def test_MetaData(self):
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testMetaData.sbs')
        sbs_doc = sbsgenerator.createSBSDocument(context.Context(), fileAbsPath)
        # create metadataURL
        res_path = python_helpers.getAbsPathFromModule(testModule, './resources/Craters.png')
        res = sbs_doc.createLinkedResource(aResourceTypeEnum=sbsenum.ResourceTypeEnum.BITMAP, aResourcePath=res_path)
        sbs_doc.createMetaDataUrl("baz", res)
        # create metadataStr
        sbs_doc.createMetaDataStr("foo", "bar")
        # raise metadataUrl/Str wrong type
        with self.assertRaises(TypeError):
            sbs_doc.createMetaDataStr("bad", 1)
            sbs_doc.createMetaDataUrl("foobad", "res")
        # test create metadata with same key/name
        with self.assertRaises(SBSMetaDataTreeNameConflict):
            sbs_doc.createMetaDataStr("foo", "baz")
        # get a metadata
        meta_srt = sbs_doc.getMetaData("foo")
        meta_url = sbs_doc.getMetaData("baz")
        # modify metadata value
        meta_srt.setValue("barfoo")
        with self.assertRaises(TypeError):
            meta_url.setValue("buk")
        # modify metadata name
        meta_srt.setName("foobar")
        meta_url.setName("badfoo")
        # delete a metadata
        self.assertEqual(sbs_doc.deleteMetaData("badfoo"), True)
        sbs_doc.createMetaDataUrl("baz", res)
        # write sbs
        sbs_doc.writeDoc()
        # open and read metadata
        sbs_doc = substance.SBSDocument(context.Context(), fileAbsPath)
        sbs_doc.parseDoc()
        self.assertEqual(sbs_doc.deleteMetaData("baz"), True)
        self.assertEqual(sbs_doc.getAllMetaData(), {'foobar': 'barfoo'})
        os.remove(fileAbsPath)

    def test_DeleteSBSGraph(self):
        sbs_doc = sbsgenerator.createSBSDocument(context.Context(), 'temp.sbs')
        a = sbs_doc.createGraph('a')
        b = sbs_doc.createGraph('b')
        b.createCompInstanceNode(sbs_doc, a)
        self.assertFalse(sbs_doc.deleteSBSGraph(a))
        self.assertTrue(sbs_doc.deleteSBSGraph(a, force=True))
        self.assertTrue(sbs_doc.deleteSBSGraph(b))

    #==========================================================================
    # Private
    #==========================================================================
    def __checkPackagesAndResources(self, aExporter, aDocument, aNbDirectPackages, aNbDirectResources,
                                    aNbExportedPackages, aNbExportedResources,
                                    aNbMissingPackages, aNbMissingResources,
                                    aNbTotalPackages, aNbTotalResources):
        sbsPath = aDocument.mContext.getUrlAliasMgr().getAliasAbsPath('sbs')
        apiPath = aDocument.mContext.getUrlAliasMgr().getAliasAbsPath('api')

        # Check directly included resources & dependencies
        aResources = aDocument.getSBSResourceList()
        self.assertEqual(len(aResources), aNbDirectResources)
        aPackages = aDocument.getSBSDependencyList()
        self.assertEqual(len(aPackages), aNbDirectPackages)

        # Check exported resources
        exportedResources = aExporter.getExportedResources()
        missingResources = aExporter.getMissingResources()
        self.assertEqual(len(exportedResources), aNbExportedResources)
        for aRes in aResources:
            if aRes.mFileAbsPath not in exportedResources:
                self.assertTrue(aRes.mFileAbsPath.startswith(sbsPath) or aRes.mFileAbsPath.startswith(apiPath) or \
                                aRes.mFileAbsPath in missingResources)

        # Check exported packages
        exportedPackages = aExporter.getExportedPackages()
        missingPackages = aExporter.getMissingPackages()
        self.assertEqual(len(exportedPackages), aNbExportedPackages)
        for aDep in aPackages:
            if aDep.mFileAbsPath not in exportedPackages:
                self.assertTrue(aDep.mFileAbsPath.startswith(sbsPath) or aDep.mFileAbsPath.startswith(apiPath) or \
                                aDep.mFileAbsPath in missingPackages)

        # Check that old and new packages are registered in the context
        for oldPath, newPath in exportedPackages.items():
            self.assertIsInstance(aDocument.mContext.getPackage(oldPath), common_interfaces.Package)
            self.assertIsInstance(aDocument.mContext.getPackage(newPath), common_interfaces.Package)

        # Check getting all dependencies
        aAllPackagePath = aDocument.getDependencyPathList(aRecurseOnPackages=True)
        self.assertEqual(len(aAllPackagePath), aNbTotalPackages)
        for aPath in aAllPackagePath:
            self.assertTrue(aDocument.mContext.getPackage(aPath) is not None or aPath in missingPackages)

        # Check getting all resources
        aAllResourcePath = aDocument.getResourcePathList(aRecurseOnPackages=True)
        self.assertEqual(len(aAllResourcePath), aNbTotalResources)

        # Check missing resources and dependencies
        self.assertEqual(len(missingPackages), aNbMissingPackages)
        self.assertEqual(len(missingResources), aNbMissingResources)


if __name__ == '__main__':
    log.info("Test Substance")
    unittest.main()
