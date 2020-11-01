# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import sys
import json

from pysbs.api_exceptions import SBSImpossibleActionError, SBSLibraryError, SBSMissingDependencyError
from pysbs import python_helpers
from pysbs import sbsenum
from pysbs import context
from pysbs import substance
from pysbs import sbsarchive
from pysbs import compnode

from pysbs.sbsenum import ParamTypeEnum

testModule = sys.modules[__name__]

class SBSArchiveTests(unittest.TestCase):

    __TYPE2LABEL = {
        ParamTypeEnum.DUMMY_TYPE         : 'DUMMY_TYPE',
        ParamTypeEnum.ENTRY_COLOR        : 'ENTRY_COLOR',
        ParamTypeEnum.ENTRY_GRAYSCALE    : 'ENTRY_GRAYSCALE',
        ParamTypeEnum.ENTRY_VARIANT      : 'ENTRY_VARIANT',
        ParamTypeEnum.BOOLEAN            : 'BOOLEAN',
        ParamTypeEnum.INTEGER1           : 'INTEGER1',
        ParamTypeEnum.INTEGER2           : 'INTEGER2',
        ParamTypeEnum.INTEGER3           : 'INTEGER3',
        ParamTypeEnum.INTEGER4           : 'INTEGER4',
        ParamTypeEnum.FLOAT1             : 'FLOAT1',
        ParamTypeEnum.FLOAT2             : 'FLOAT2',
        ParamTypeEnum.FLOAT3             : 'FLOAT3',
        ParamTypeEnum.FLOAT4             : 'FLOAT4',
        ParamTypeEnum.FLOAT_VARIANT      : 'FLOAT_VARIANT',
        ParamTypeEnum.ENTRY_COLOR_OPT    : 'ENTRY_COLOR_OPT',
        ParamTypeEnum.ENTRY_GRAYSCALE_OPT: 'ENTRY_GRAYSCALE_OPT',
        ParamTypeEnum.ENTRY_VARIANT_OPT  : 'ENTRY_VARIANT_OPT',
        ParamTypeEnum.ENTRY_PARAMETER    : 'ENTRY_PARAMETER',
        ParamTypeEnum.COMPLEX            : 'COMPLEX',
        ParamTypeEnum.STRING             : 'STRING',
        ParamTypeEnum.PATH               : 'PATH',
        ParamTypeEnum.VOID_TYPE          : 'VOID_TYPE',
        ParamTypeEnum.TEMPLATE1          : 'TEMPLATE1',
        ParamTypeEnum.TEMPLATE2          : 'TEMPLATE2',
    }

    def test_SBSAR(self):
        """
        This test checks the parsing of a SBSAR file.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testSBSARParsing.sbsar')
        aContext = context.Context()

        doc = sbsarchive.SBSArchive(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())

        # Check graphs
        aGraphs = doc.getSBSGraphList()
        self.assertEqual(len(aGraphs), 4)
        aGraph = doc.getSBSGraph(aGraphIdentifier='New_Graph')
        self.assertIsInstance(aGraph, sbsarchive.SBSARGraph)
        aGraph2 = doc.getSBSGraphFromPkgUrl(aPkgUrl='pkg://MyFolder/New_Graph')

        # Check color space on this graph
        aOutput_0 = aGraph2.getGraphOutput('output')
        usages = aOutput_0.getUsages()
        self.assertEqual(len(usages), 2)
        self.assertEqual(usages[0].mColorSpace, '')
        self.assertEqual(usages[1].mColorSpace, 'banana')

        from pysbs import sbslibrary
        aOutput_1 = aGraph2.getGraphOutput('output_1')
        usages = aOutput_1.getUsages()
        self.assertEqual(len(usages), 1)
        self.assertEqual(usages[0].mColorSpace, sbslibrary.getColorSpace(sbsenum.ColorSpacesEnum.SRGB))

        aInput = aGraph2.getInputImage('inputImage')
        usages = aInput.getUsages()
        self.assertEqual(len(usages), 2)
        self.assertEqual(usages[0].mColorSpace, 'myColorSpace')
        self.assertEqual(usages[1].mColorSpace, '')

        self.assertEqual(aGraph, aGraph2)
        aGraph2 = doc.getSBSGraph(aGraphIdentifier='New_Graph_1')
        self.assertEqual(aGraph2.mPkgUrl, 'pkg://New_Graph')
        aGraph2 = doc.getSBSGraph(aGraphIdentifier='NoGraph')
        self.assertIsNone(aGraph2)

        # Check GuiGroup
        aGuiGroups = aGraph.getAllGuiGroups()
        self.assertEqual(len(aGuiGroups), 1)

        # Check inputs
        aAllInputs = aGraph.getAllInputs()
        self.assertEqual(len(aAllInputs), 20)

        self.assertEqual(len(aGraph.getAllInputsInGroup('aGroup')), 0)

        aMyGroupInputs = aGraph.getAllInputsInGroup('MyGroup')
        self.assertEqual(len(aMyGroupInputs), 3)
        self.assertEqual(aMyGroupInputs, aGraph.getAllInputsInGroup(aGuiGroups[0]))
        for aInput in aMyGroupInputs:
            self.assertEqual(aInput, aGraph.getInput(aInputIdentifier=aInput.mIdentifier))

        # Check that all attributes can be accessed
        for aInput in aAllInputs:
            self.assertIsInstance(aInput, sbsarchive.SBSARInput)

            aInput.getClamp()
            aInput.getStep()
            aInput.getDefaultValue()
            aInput.getDropDownList()
            aInput.getGroup()
            aInput.getLabels()
            aInput.getMinValue()
            aInput.getMaxValue()
            aInput.getType()
            aInput.getUsages()
            aInput.getWidget()

        # slider int 1
        aInput = aGraph.getInputParameter('input_5')
        self.assertIsInstance(aInput.getClamp(), bool)

        # dropdown list
        aInput = aGraph.getInputParameter('input_6')
        self.assertIsInstance(aInput.getDropDownList(), dict)

        # slider int 3
        aInput = aGraph.getInputParameter('input_9')
        self.assertEqual(aInput.getDimension(), 3)
        self.assertIsInstance(aInput.getMaxValue(), int)
        self.assertEqual(len(aInput.getMaxValue(asList=True)), 3)

        # slider float 4
        aInput = aGraph.getInputParameter('input_12')
        self.assertEqual(aInput.getDimension(), 4)
        self.assertIsInstance(aInput.getMinValue(), float)
        self.assertEqual(len(aInput.getMinValue(asList=True)), 4)

        # boolean
        aInput = aGraph.getInputParameter('input_16')
        self.assertEqual(aInput.getLabelTrue(), 'Yes')
        self.assertEqual(aInput.getLabelFalse(), 'No')

        # Check outputs
        aOutput = aGraph.getGraphOutput(aOutputIdentifier='output')
        self.assertEqual(aGraph.getGraphOutputWithUsage('diffuse'), aOutput)
        self.assertEqual(aGraph.getGraphOutputWithUsage('baseColor'), aOutput)
        self.assertEqual(aGraph.getGraphOutputWithUsage(sbsenum.UsageEnum.BASECOLOR), aOutput)

        aOutput = aGraph.getGraphOutput(aOutputIdentifier='output_1')
        self.assertEqual(aGraph.getGraphOutputWithUsage(aUsage='myusage'), aOutput)

        self.assertIsNone(aGraph.getGraphOutput(aOutputIdentifier='BadOutput'))
        self.assertIsNone(aGraph.getGraphOutputWithUsage(aUsage='BadUsage'))

        with self.assertRaises(SBSLibraryError):
            aGraph.getGraphOutputWithUsage(aUsage=1000)


    def test_DepWithSBSAR(self):
        """
        This test checks the parsing of a package with a SBSAR dependencies.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDepSBSAR.sbs')
        aContext = context.Context()

        sbsDoc = substance.SBSDocument(aContext, fileAbsPath)
        self.assertTrue(sbsDoc.parseDoc())

        depList = sbsDoc.getSBSDependencyList()
        self.assertEqual(len(depList), 2)
        aGraph = sbsDoc.getSBSGraphList()[0]
        # test graph doesn't exist
        with self.assertRaises(SBSMissingDependencyError):
            aGraph.createCompInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='./testSBSARParsing.sbsar/_dummy_')
        # test the first one graph available
        aGraph.createCompInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='./testSBSARParsing.sbsar')
        # Add instance nodes of the already existing dependency:
        aInstance1 = aGraph.createCompInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='./testSBSARParsing.sbsar/New_Graph')
        self.assertIsInstance(aInstance1, compnode.SBSCompNode)

        aInstance2 = aGraph.createCompInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='./testSBSARParsing.sbsar/testSBSARParsingGraph',
                                                           aGUIPos=aInstance1.getOffsetPosition(aOffset=[150,0]))

        aGraph.createCompInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='./testSBSARParsing.sbsar/testSBSARParsingGraph',
                                              aGUIPos=aInstance1.getOffsetPosition(aOffset=[150,0]))

        self.assertIsInstance(aInstance2, compnode.SBSCompNode)

        # Connect nodes
        aGraph.connectNodes(aLeftNode  = aInstance1, aRightNode = aInstance2)
        aOutputNode = aGraph.getAllOutputNodes()[0]
        aGraph.connectNodes(aLeftNode = aInstance2, aRightNode = aOutputNode)

        destAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testDepSBSAR_result.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destAbsPath))
        os.remove(destAbsPath)


    def test_Attributes(self):
        """
        This test checks getting attributes of a SBSAR file.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testSBSARParsing.sbsar')
        aContext = context.Context()

        doc = sbsarchive.SBSArchive(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())

        aGraph = doc.getSBSGraph('testSBSARParsingGraph')
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.Icon))
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.AuthorURL), 'is it an URL ?')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.Description), 'A graph description')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.Label), 'Why a label AND an identifier ?')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.HideInLibrary), True)
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.Category), 'A category name')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.Tags), 'testing API sbsar')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.UserTags), 'I don\'t have any data :(')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.PhysicalSize), [18.0, 0, 0])

        aOutput = aGraph.getGraphOutput('output')
        self.assertIsNone(aOutput.getAttribute(sbsenum.AttributesEnum.Icon))
        self.assertIsNone(aOutput.getAttribute(sbsenum.AttributesEnum.Author))
        self.assertIsNone(aOutput.getAttribute(sbsenum.AttributesEnum.AuthorURL))
        self.assertIsNone(aOutput.getAttribute(sbsenum.AttributesEnum.HideInLibrary))
        self.assertIsNone(aOutput.getAttribute(sbsenum.AttributesEnum.Category))
        self.assertEqual(aOutput.getAttribute(sbsenum.AttributesEnum.Description), None) # Should be: 'An output description'
        self.assertEqual(aOutput.getAttribute(sbsenum.AttributesEnum.Label), 'Why a label AND an identifier')
        self.assertEqual(aOutput.getAttribute(sbsenum.AttributesEnum.UserTags), 'still no data')
        self.assertEqual(aOutput.getAttribute(sbsenum.AttributesEnum.PhysicalSize), None)

        aGraph = doc.getSBSGraph('New_Graph')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.Label), 'New_Graph')
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.Icon))
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.Author))
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.AuthorURL))
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.HideInLibrary))
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.Category))
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.Description))
        self.assertIsNone(aGraph.getAttribute(sbsenum.AttributesEnum.UserTags))
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.PhysicalSize), None)

        aInputParam = aGraph.getInputParameter('input_1')
        self.assertIsNone(aInputParam.getAttribute(sbsenum.AttributesEnum.Icon))
        self.assertIsNone(aInputParam.getAttribute(sbsenum.AttributesEnum.Author))
        self.assertIsNone(aInputParam.getAttribute(sbsenum.AttributesEnum.AuthorURL))
        self.assertIsNone(aInputParam.getAttribute(sbsenum.AttributesEnum.HideInLibrary))
        self.assertIsNone(aInputParam.getAttribute(sbsenum.AttributesEnum.Category))
        self.assertEqual(aInputParam.getAttribute(sbsenum.AttributesEnum.Description), 'Angle description')
        self.assertEqual(aInputParam.getAttribute(sbsenum.AttributesEnum.Label), 'MyAngle')
        self.assertEqual(aInputParam.getAttribute(sbsenum.AttributesEnum.UserTags), 'no data, don\'t know what to put here')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.PhysicalSize), None)


    def test_NewCompression(self):
        """
        This test checks the parsing of a SBSAR file.
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/sbsarNewCompression.sbsar')
        aContext = context.Context()

        doc = sbsarchive.SBSArchive(aContext, fileAbsPath)
        self.assertTrue(doc.parseDoc())


    def test_v7Engine(self):
        """
        This test checks if we are able to successfully load a SBSAR which uses v7 nodes (e.g. input/output values)
        """
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/sample_value_node.sbsar')
        aContext = context.Context()

        sbsar = sbsarchive.SBSArchive(aContext, fileAbsPath)
        self.assertTrue(sbsar.parseDoc())

        for graph in sbsar.getSBSGraphList():
            self.assertIsNotNone(graph.mIdentifier)

            for input in graph.getAllInputs():
                print('\t Input  [{: <15}] - {: <15}'.format(SBSArchiveTests.__TYPE2LABEL.get(input.getType(), None), input.mIdentifier))
                self.assertIsNotNone(input.mIdentifier)
                self.assertIsNotNone(input.getType())

            for output in graph.getGraphOutputs():
                print('\t Output [{: <15}] - {: <15}'.format(SBSArchiveTests.__TYPE2LABEL.get(output.getType(), None), output.mIdentifier))
                self.assertIsNotNone(output.mIdentifier)
                self.assertIsNotNone(output.getType())


    def test_MetaData(self):
        # extract json
        fileAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testSBSARMetaData.sbsar')
        sbsar = sbsarchive.SBSArchive(context.Context(), fileAbsPath)
        aDestPath = python_helpers.getAbsPathFromModule(testModule, './resources')
        aJsonPath = sbsar.extractSbsarMetaDataJson(aDestPath)
        with open(aJsonPath, 'r') as f:
            aDict = json.load(f)
            self.assertEqual(aDict, {"bitmap": "resources/0/corsica_beach.exr", "foo": "bar", "other": "resources/1/untitled.blend"})
        # read all metadata as dict
        aDict = sbsar.getAllMetaData()
        self.assertEqual(aDict, {"bitmap": "resources/0/corsica_beach.exr", "foo": "bar", "other": "resources/1/untitled.blend"})
        # extract file from metadata
        aPath = sbsar.extractSbsarMetaDataResource(aDestPath, "resources/1/untitled.blend")
        self.assertEqual(python_helpers.getAbsPathFromModule(testModule, './resources/untitled.blend').replace("\\", "/"), aPath.replace("\\", "/"))
        # extract a metadata pack
        extractFiles = sbsar.extractSbsarMetaDataPack(aDestPath)
        extractFiles.sort()
        compareList = [os.path.join(aDestPath, 'corsica_beach.exr'), os.path.join(aDestPath, 'metadata.json'), os.path.join(aDestPath, 'untitled.blend')]
        for i, path in enumerate(extractFiles):
            self.assertEqual(path.replace("\\", "/"), extractFiles[i].replace("\\", "/"))
        for aFile in extractFiles:
            os.remove(aFile)


if __name__ == '__main__':
    log.info("Test SBSArchive")
    unittest.main()
