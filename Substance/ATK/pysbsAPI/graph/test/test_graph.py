# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import copy
import os
import sys
import inspect

from pysbs.api_exceptions import SBSLibraryError, SBSImpossibleActionError
from pysbs import api_helpers, python_helpers
from pysbs.common_interfaces import Package
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import context
from pysbs import substance
from pysbs import sbsarchive
from pysbs import sbsgenerator
from pysbs import params
from pysbs import graph
from pysbs import sbscommon
from pysbs import compnode

from pysbs.sbsenum import ParamTypeEnum

testModule = sys.modules[__name__]

class SBSGraphTests(unittest.TestCase):

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

    @staticmethod
    def isPrivateMember(aMemberName):
        return aMemberName.startswith('__') and aMemberName.endswith('__')

    @staticmethod
    def openTestDocument(aFileName):
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/' + aFileName)
        if Package.isAnArchive(docAbsPath):
            sbsDoc = sbsarchive.SBSArchive(context.Context(), docAbsPath)
        else:
            sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    def test_getAllNodes(self):
        """
        This test checks the 'getAll...' functions of a graph
        """
        log.info("Test Graph: Get all nodes functions")
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')
        allNodeGraph = sbsDoc.getSBSGraph('AllNodes')
        inputNodes = allNodeGraph.getAllInputNodes()
        self.assertEqual(len(inputNodes), 2)
        self.assertTrue(inputNodes[0].isAnInputBridge())
        self.assertTrue(inputNodes[1].isAnInputBridge())

        outputNodes = allNodeGraph.getAllOutputNodes()
        self.assertEqual(len(outputNodes), 4)
        self.assertTrue(outputNodes[0].isAnOutputBridge())
        self.assertTrue(outputNodes[1].isAnOutputBridge())
        self.assertTrue(outputNodes[2].isAnOutputBridge())
        self.assertTrue(outputNodes[3].isAnOutputBridge())

        allFilters = inspect.getmembers(sbsenum.FilterEnum)
        enumValues = [aFilter for aFilterName, aFilter in allFilters
                      if not SBSGraphTests.isPrivateMember(aFilterName) and
                        aFilter != sbsenum.FilterEnum.GRAYSCALECONVERSION and aFilter != sbsenum.FilterEnum.DIRECTIONALMOTIONBLUR]

        for enumValue in enumValues:
            filterNodes = allNodeGraph.getAllFiltersOfKind(enumValue)
            self.assertEqual(len(filterNodes), 1)
            if enumValue != sbsenum.FilterEnum.COMPINSTANCE:
                self.assertTrue(filterNodes[0].isAFilter())
                self.assertEqual(filterNodes[0].mCompImplementation.mCompFilter.mFilter, sbslibrary.getFilterDefinition(enumValue).mIdentifier)
            else:
                self.assertTrue(filterNodes[0].isAnInstance())

        grayscaleConvNodes = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.GRAYSCALECONVERSION)
        self.assertEqual(len(grayscaleConvNodes), 4)

        instanceNodes1 = allNodeGraph.getAllNodeInstancesOf(sbsDoc, 'sbs://curvature.sbs/curvature')
        instanceNodes2 = allNodeGraph.getAllNodeInstancesOf(sbsDoc, 'sbs://curvature.sbs')
        self.assertEqual(len(instanceNodes1), 1)
        self.assertEqual(instanceNodes1, instanceNodes2)

        subGraph = sbsDoc.getSBSGraph('SubGraph')
        allNodeGraph.createCompInstanceNode(sbsDoc, subGraph)
        instanceNodes1 = allNodeGraph.getAllNodeInstancesOf(sbsDoc, api_helpers.getPkgPrefix() + subGraph.mIdentifier)
        self.assertEqual(len(instanceNodes1), 1)

        newDocAbsPath = sbsDoc.buildAbsPathFromRelToMePath('NewGraph.sbs')
        newDoc = sbsgenerator.createSBSDocument(context.Context(), newDocAbsPath, 'NewGraph')
        newGraph = newDoc.getSBSGraph('NewGraph')
        aInput = newGraph.createInputNode('input')
        aOutput = newGraph.createOutputNode('output')
        newGraph.connectNodes(aLeftNode=aInput, aRightNode=aOutput)
        newDoc.writeDoc()

        allNodeGraph.createCompInstanceNodeFromPath(sbsDoc, 'NewGraph.sbs')
        instanceNodes1 = allNodeGraph.getAllNodeInstancesOf(sbsDoc, 'NewGraph.sbs')
        instanceNodes2 = allNodeGraph.getAllNodeInstancesOf(sbsDoc, newDocAbsPath)
        self.assertEqual(len(instanceNodes1), 1)
        self.assertEqual(instanceNodes1, instanceNodes2)

        os.remove(newDocAbsPath)
        log.info("Test Graph: Get all nodes functions: OK\n")


    def test_BaseParameters(self):
        """
        This test checks getting and setting BaseParameters on a graph
        """
        log.info("Test Graph: Base parameters")
        xOffset = [150, 0]
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')

        # Set a param already defined
        allNodeGraph = sbsDoc.getSBSGraph('AllNodes')
        aFormat = allNodeGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT)
        self.assertEqual(aFormat, str(sbsenum.OutputFormatEnum.FORMAT_8BITS))

        allNodeGraph.setBaseParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT, sbsenum.OutputFormatEnum.FORMAT_16BITS)
        aFormat = allNodeGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT)
        self.assertEqual(aFormat, str(sbsenum.OutputFormatEnum.FORMAT_16BITS))

        # Set a new param
        seed = allNodeGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.RANDOM_SEED)
        self.assertEqual(seed, str(0))

        allNodeGraph.setBaseParameterValue(sbsenum.CompNodeParamEnum.RANDOM_SEED, 153)
        seed = allNodeGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.RANDOM_SEED)
        self.assertEqual(seed, str(153))

        # Set as dynamic
        aDynValue = allNodeGraph.setDynamicBaseParameter(sbsenum.CompNodeParamEnum.RANDOM_SEED)
        self.assertIsInstance(aDynValue, params.SBSDynamicValue)
        aDynValue = allNodeGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.RANDOM_SEED)
        self.assertIsInstance(aDynValue, params.SBSDynamicValue)

        aFloatNode = aDynValue.createFunctionNode(aFunction = sbsenum.FunctionEnum.RAND,
                                                  aParameters={sbsenum.FunctionEnum.CONST_FLOAT: 1000})
        aRandNode = aDynValue.createFunctionNode(aFunction = sbsenum.FunctionEnum.RAND,
                                                 aGUIPos = aFloatNode.getOffsetPosition(xOffset))
        aToIntNode = aDynValue.createFunctionNode(aFunction = sbsenum.FunctionEnum.TO_INT,
                                                  aGUIPos = aRandNode.getOffsetPosition(xOffset))
        aDynValue.connectNodes(aLeftNode = aFloatNode, aRightNode = aRandNode)
        aDynValue.connectNodes(aLeftNode = aRandNode, aRightNode = aToIntNode)
        aDynValue.setOutputNode(aToIntNode)
        aType = aDynValue.getOutputType()
        self.assertEqual(aType, sbsenum.ParamTypeEnum.INTEGER1)

        # Behavior with invalid parameters
        self.assertIsNone(allNodeGraph.getBaseParameterValue(sbsenum.CompNodeParamEnum.BLENDING_MODE))
        with self.assertRaises(SBSLibraryError):
            allNodeGraph.setBaseParameterValue(sbsenum.CompNodeParamEnum.BLENDING_MODE, sbsenum.BlendBlendingModeEnum.COPY)
        with self.assertRaises(SBSLibraryError):
            allNodeGraph.setDynamicBaseParameter(sbsenum.CompNodeParamEnum.CHANNEL_ALPHA)
        with self.assertRaises(ValueError):
            allNodeGraph.setBaseParameterValue(sbsenum.CompNodeParamEnum.RANDOM_SEED, 'InvalidValue')
        with self.assertRaises(SBSLibraryError):
            allNodeGraph.setBaseParameterValue('InvalidParam', 0)

        log.info("Test Graph: Base parameters: OK\n")


    def test_InputParameters(self):
        """
        This test checks adding, getting and deleting input parameters on a graph
        """
        log.info("Test Graph: Input parameters")
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')

        aGraph = sbsDoc.getSBSGraph('AllNodes')
        inputParams = aGraph.getInputParameters()
        self.assertEqual(len(inputParams), 1)
        aGraph.deleteInputParameter(inputParams[0])
        inputParams = aGraph.getInputParameters()
        self.assertEqual(inputParams, [])

        # Check adding of input parameters and input nodes
        param1 = aGraph.addInputParameter(aIdentifier=u'MyInput', aWidget=sbsenum.WidgetEnum.SLIDER_FLOAT1)
        param2 = aGraph.addInputParameter(aIdentifier='MyInput', aWidget=sbsenum.WidgetEnum.SLIDER_FLOAT2)
        self.assertIsInstance(param1, graph.SBSParamInput)
        self.assertIsInstance(param2, graph.SBSParamInput)
        self.assertEqual(param1.mIdentifier, 'MyInput')
        self.assertEqual(param2.mIdentifier, u'MyInput_1')

        self.assertFalse(param1.getIsConnectable())
        param1.setIsConnectable(True)
        self.assertTrue(param1.getIsConnectable())
        param1.setIsConnectable(False)
        self.assertFalse(param1.getIsConnectable())

        inputParams = aGraph.getInputParameters()
        self.assertEqual(len(inputParams), 2)

        aGraph.createInputNode('MyInput')
        inputEntries = aGraph.getInputImages()
        self.assertEqual(len(inputEntries), 2)
        self.assertEqual(inputEntries[1].mIdentifier, 'MyInput_2')
        self.assertTrue(inputEntries[1].getIsConnectable())

        self.assertTrue(aGraph.deleteInputParameter(param2))

        aGraph.createInputNode('MyInput', aIsConnectable=False)
        inputEntries = aGraph.getInputImages()
        self.assertEqual(len(inputEntries), 3)
        self.assertEqual(inputEntries[2].mIdentifier, 'MyInput_1')
        self.assertFalse(inputEntries[2].getIsConnectable())

        with self.assertRaises(SBSImpossibleActionError):   aGraph.deleteInputParameter('Invalid')
        with self.assertRaises(SBSImpossibleActionError):   aGraph.deleteInputParameter(None)
        with self.assertRaises(SBSImpossibleActionError):   aGraph.deleteInputParameter(param2)

        # Check setting the order of the parameters
        aGraph.setInputImageIndex('MyInput_1', 0)
        self.assertEqual(aGraph.getInputImages()[0].mIdentifier, 'MyInput_1')
        self.assertEqual(aGraph.getInputImageIndex(u'MyInput_1'), 0)

        aGraph.setInputImageIndex('MyInput_1', 1)
        self.assertEqual(aGraph.getInputImages()[1].mIdentifier, 'MyInput_1')
        self.assertEqual(aGraph.getInputImageIndex('MyInput_1'), 1)

        aGraph.setInputImageIndex(u'MyInput_1', 2)
        self.assertEqual(aGraph.getInputImages()[2].mIdentifier, 'MyInput_1')
        self.assertEqual(aGraph.getInputImageIndex('MyInput_1'), 2)

        with self.assertRaises(Exception):                  aGraph.setInputImageIndex('MyInput_1', 'o')
        with self.assertRaises(SBSImpossibleActionError):   aGraph.setInputImageIndex('MyInput_1', -1)
        with self.assertRaises(SBSImpossibleActionError):   aGraph.setInputImageIndex('MyInput_1', 3)

        param2 = aGraph.addInputParameter(aIdentifier='ParamInput', aWidget=sbsenum.WidgetEnum.ANGLE_FLOAT1)
        param3 = aGraph.addInputParameter(aIdentifier='ParamInput', aWidget=sbsenum.WidgetEnum.BUTTON_BOOL)
        self.assertEqual(len(aGraph.getInputParameters()), 3)

        aGraph.setInputParameterIndex(param2.mIdentifier, 2)
        self.assertEqual(aGraph.getInputParameters()[2].mIdentifier, param2.mIdentifier)
        self.assertEqual(aGraph.getInputParameterIndex(param2.mIdentifier), 2)
        aGraph.setInputParameterIndex(param3.mIdentifier, 0)
        self.assertEqual(aGraph.getInputParameters()[0].mIdentifier, param3.mIdentifier)
        self.assertEqual(aGraph.getInputParameterIndex(param3.mIdentifier), 0)

        with self.assertRaises(Exception):                  aGraph.setInputImageIndex(param2.mIdentifier, 'o')
        with self.assertRaises(SBSImpossibleActionError):   aGraph.setInputImageIndex(param2.mIdentifier, -1)
        with self.assertRaises(SBSImpossibleActionError):   aGraph.setInputImageIndex(param2.mIdentifier, 6)

        log.info("Test Graph: Input parameters: OK\n")

    @staticmethod
    def getNodeIndex(graphList, n):
        for i, nn in enumerate(graphList):
            if nn == n:
                return i
        raise BaseException('Banantroll')

    def test_SortAsDAG(self):
        """
        This test checks sorting the nodes of a graph
        """
        log.info("Test Graph: Sort as DAG")
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')

        allNodeGraph = sbsDoc.getSBSGraph('AllNodes')
        unsortedNodes = copy.copy(allNodeGraph.getNodeList())
        sortedNodes = allNodeGraph.sortNodesAsDAG()
        self.assertEqual(allNodeGraph.getNodeList(), sortedNodes)

        # run this manually to update refSortedIndices
        # t = []
        # for i, node in enumerate(sortedNodes):
        #     if node in unsortedNodes:
        #         t.append(unsortedNodes.index(node))
        # print(t)

        refSortedIndices = [0, 33, 2, 31, 25, 30, 3, 32, 17, 1, 18, 29, 23, 4, 5, 28, 6, 8, 7, 9, 10, 12, 11, 13, 14, 20, 21, 22, 16, 26, 19, 15, 27, 24]

        for i, index in enumerate(refSortedIndices):
            self.assertEqual(sortedNodes[i], unsortedNodes[index])
        log.info("Test Graph: Sort as DAG: OK\n")


    def test_Usages(self):
        """
        This test checks getting and adding usages on a graph output
        """
        log.info("Test Graph: Usages")
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')

        aGraph = sbsDoc.getSBSGraph('AllNodes')
        graphOutputs = aGraph.getGraphOutputs()
        # Check existing usages
        for output in graphOutputs:
            if output.hasUsage(sbsenum.UsageEnum.NORMAL):
                self.assertTrue(output.hasUsage(sbslibrary.getUsage(sbsenum.UsageEnum.NORMAL)))
            elif output.hasUsage(sbsenum.UsageEnum.BASECOLOR):
                self.assertTrue(output.hasUsage(sbslibrary.getUsage(sbsenum.UsageEnum.BASECOLOR)))
            elif output.hasUsage(sbsenum.UsageEnum.EMISSIVE):
                self.assertTrue(output.hasUsage(sbslibrary.getUsage(sbsenum.UsageEnum.EMISSIVE)))
            else:
                self.assertTrue(output.hasUsage('curvature'))

        # Check non existing or invalid usages
        self.assertFalse(graphOutputs[0].hasUsage(sbsenum.UsageEnum.AMBIENT))
        self.assertFalse(graphOutputs[0].hasUsage('diffuse'))
        self.assertFalse(graphOutputs[0].hasUsage('myUsage'))
        with self.assertRaises(SBSLibraryError):
            graphOutputs[0].hasUsage(1000)

        # Check adding usage
        graphOutputs[0].addUsage(aUsage = sbsenum.UsageEnum.DIFFUSE, aComponents = sbsenum.ComponentsEnum.RGB)
        self.assertTrue(graphOutputs[0].hasUsage('diffuse'))
        graphOutputs[0].addUsage('myUsage')
        self.assertTrue(graphOutputs[0].hasUsage(u'myUsage'))
        graphOutputs[0].addUsage(u'üsage')
        self.assertTrue(graphOutputs[0].hasUsage(u'üsage'))

        # Add outputs node
        aGraph.createOutputNode(aIdentifier=u'newOutput')
        aGraph.createOutputNode(aIdentifier='newOutput',
                                aUsages={'nothing': {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA}})
        aGraph.createOutputNode(aIdentifier='newOutput',
                                aUsages={sbsenum.UsageEnum.ANY: {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA}})
        aGraph.createOutputNode(aIdentifier='newOutput',
                                aUsages={sbsenum.UsageEnum.NORMAL: {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA,
                                                                    sbsenum.UsageDataEnum.COLOR_SPACE: sbsenum.ColorSpacesEnum.NORMAL_XYZ_RIGHT}})
        aGraph.createOutputNode(aIdentifier='newOutput',
                                aUsages={sbsenum.UsageEnum.BUMP: {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA,
                                                                  sbsenum.UsageDataEnum.COLOR_SPACE: 'superCustomColorSpace'}})

        output1 = aGraph.getGraphOutput(aOutputIdentifier='newOutput')
        self.assertEqual(output1.getUsages(), [])
        output2 = aGraph.getGraphOutput(aOutputIdentifier='newOutput_1')
        self.assertEqual(len(output2.getUsages()), 1)
        self.assertTrue(output2.hasUsage('nothing'))
        output3 = aGraph.getGraphOutput(aOutputIdentifier='newOutput_2')
        self.assertEqual(len(output3.getUsages()), 1)
        self.assertTrue(output3.hasUsage(sbsenum.UsageEnum.ANY))
        output4 = aGraph.getGraphOutput(aOutputIdentifier='newOutput_3')
        self.assertEqual(len(output4.getUsages()), 1)
        self.assertTrue(output4.hasUsage(sbsenum.UsageEnum.NORMAL))
        output5 = aGraph.getGraphOutput(aOutputIdentifier='newOutput_4')
        self.assertEqual(len(output5.getUsages()), 1)
        self.assertTrue(output5.hasUsage(sbsenum.UsageEnum.BUMP))

        self.assertEqual(aGraph.getGraphOutputWithUsage('diffuse'), graphOutputs[0])
        self.assertEqual(aGraph.getGraphOutputWithUsage('nothing'), output2)
        self.assertEqual(aGraph.getGraphOutputWithUsage(sbsenum.UsageEnum.ANY), output3)
        self.assertIsNone(aGraph.getGraphOutputWithUsage(sbsenum.UsageEnum.PANORAMA))

        # Add inputs node
        aGraph.createInputNode(aIdentifier=u'newInput')
        aGraph.createInputNode(aIdentifier='newInput', aUsages={'nothing': {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA}})
        aGraph.createInputNode(aIdentifier='newInput',
                               aUsages={sbsenum.UsageEnum.ANY: {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA}})
        aGraph.createInputNode(aIdentifier='newInput',
                               aUsages={sbsenum.UsageEnum.NORMAL: {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA,
                                                                   sbsenum.UsageDataEnum.COLOR_SPACE: sbsenum.ColorSpacesEnum.NORMAL_XYZ_LEFT}})
        aGraph.createInputNode(aIdentifier='newInput',
                               aUsages={sbsenum.UsageEnum.BUMP: {sbsenum.UsageDataEnum.COMPONENTS: sbsenum.ComponentsEnum.RGBA,
                                                                 sbsenum.UsageDataEnum.COLOR_SPACE: 'superCustomColorspace'}})

        input1 = aGraph.getInputImage(aInputImageIdentifier ='newInput')
        self.assertEqual(input1.getUsages(), [])
        input2 = aGraph.getInputImage(aInputImageIdentifier='newInput_1')
        self.assertEqual(len(input2.getUsages()), 1)
        self.assertTrue(input2.hasUsage('nothing'))
        input3 = aGraph.getInputImage(aInputImageIdentifier=u'newInput_2')
        self.assertEqual(len(input3.getUsages()), 1)
        self.assertTrue(input3.hasUsage(sbsenum.UsageEnum.ANY))
        input4 = aGraph.getInputImage(aInputImageIdentifier=u'newInput_3')
        self.assertEqual(len(input4.getUsages()), 1)
        self.assertTrue(input4.hasUsage(sbsenum.UsageEnum.NORMAL))
        input5 = aGraph.getInputImage(aInputImageIdentifier=u'newInput_4')
        self.assertEqual(len(input5.getUsages()), 1)
        self.assertTrue(input5.hasUsage(sbsenum.UsageEnum.BUMP))

        self.assertEqual(aGraph.getInputImageWithUsage('nothing'), input2)
        self.assertEqual(aGraph.getInputImageWithUsage(sbsenum.UsageEnum.ANY), input3)
        self.assertIsNone(aGraph.getInputImageWithUsage(sbsenum.UsageEnum.PANORAMA))

        log.info("Test Graph: Usages: OK\n")


    def test_ConnectDisconnect(self):
        """
        This test checks connecting and disconnecting nodes
        """
        log.info("Test Graph: Connect / Disconnect Nodes")
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')

        aGraph = sbsDoc.getSBSGraph('AllNodes')
        colorNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.UNIFORM)[0]
        blendNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BLEND)[0]
        self.assertTrue(blendNode.isConnectedTo(colorNode))

        # Check behavior with invalid cases:
        # - Invalid input
        with self.assertRaises(SBSImpossibleActionError):
            aGraph.connectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= sbsenum.InputEnum.INPUT1)
        with self.assertRaises(SBSLibraryError):
            aGraph.connectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= 1000)

        #  - Two nodes of two different graphs
        aSubGraph = sbsDoc.getSBSGraph('SubGraph')
        inputNode = aSubGraph.getAllInputNodes()[0]
        with self.assertRaises(SBSImpossibleActionError):
            aGraph.connectNodes(aLeftNode=inputNode, aRightNode=blendNode, aRightNodeInput=sbsenum.InputEnum.SOURCE)

        #  - Cycle creation in the graph
        blurNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BLUR)[0]
        with self.assertRaises(SBSImpossibleActionError):
            aGraph.connectNodes(aLeftNode=blurNode, aRightNode=blendNode)

        curvNode = aGraph.getAllNodeInstancesOf(sbsDoc, 'sbs://curvature.sbs')[0]
        with self.assertRaises(SBSImpossibleActionError):
            aGraph.connectNodes(aLeftNode=curvNode, aRightNode=blendNode)

        # Check behavior with valid cases:
        aGraph.disconnectNodes(aLeftNode = colorNode, aRightNode = blendNode)
        self.assertFalse(blendNode.isConnectedTo(colorNode))

        aGraph.connectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= sbsenum.InputEnum.SOURCE)
        aGraph.connectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= sbsenum.InputEnum.DESTINATION)
        self.assertTrue(blendNode.isConnectedTo(colorNode))

        aGraph.disconnectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= sbsenum.InputEnum.SOURCE)
        self.assertTrue(blendNode.isConnectedTo(colorNode))
        aGraph.disconnectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= sbsenum.InputEnum.DESTINATION)
        self.assertFalse(blendNode.isConnectedTo(colorNode))

        aGraph.connectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= sbsenum.InputEnum.SOURCE)
        aGraph.connectNodes(aLeftNode=colorNode, aRightNode=blendNode, aRightNodeInput= sbsenum.InputEnum.DESTINATION)
        aGraph.disconnectNodes(aLeftNode = colorNode, aRightNode = blendNode)
        self.assertFalse(blendNode.isConnectedTo(colorNode))

        #Test connecting to a non-existing input on the right
        composer = aGraph.createCompInstanceNodeFromPath(sbsDoc, aPath='sbs://multi_material_blend.sbs')
        with self.assertRaises(SBSImpossibleActionError):
            aGraph.connectNodes(aLeftNode=composer, aRightNode=blendNode, aLeftNodeOutput='Banana')

        log.info("Test Graph: Connect / Disconnect Nodes: OK\n")


    def test_dynamicNbInputs(self):
        """
        This test checks the dynamic number of inputs of FxMap and Pixel Processor Nodes
        """
        log.info("Test Graph: Dynamic nb inputs")
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')
        allNodeGraph = sbsDoc.getSBSGraph('AllNodes')

        # Check dynamic inputs on a Pixel processor
        pixProc = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.PIXEL_PROCESSOR)[0]
        hsl = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.HSL)[0]

        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput=sbsenum.InputEnum.INPUT),
                              sbscommon.SBSConnection)
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:1'),
                              sbscommon.SBSConnection)
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:2'),
                              sbscommon.SBSConnection)
        with self.assertRaises(SBSImpossibleActionError):
                allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:4')

        allNodeGraph.disconnectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:1')

        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:3'),
                              sbscommon.SBSConnection)
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:1'),
                              sbscommon.SBSConnection)

        # Check rectangle size
        rect = pixProc.getRect()
        self.assertEqual(round(rect.mHeight,3), 138.667)
        self.assertEqual(rect.mWidth, 96.0)

        allNodeGraph.disconnectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input')
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:3'),
                              sbscommon.SBSConnection)
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:4'),
                              sbscommon.SBSConnection)
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input'),
                              sbscommon.SBSConnection)

        allNodeGraph.disconnectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:3')
        allNodeGraph.disconnectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:4')
        with self.assertRaises(SBSImpossibleActionError):
            allNodeGraph.connectNodes(aLeftNode=hsl, aRightNode=pixProc, aRightNodeInput='input:4')

        # Check rectangle size
        self.assertEqual(round(pixProc.getRect().mHeight,3), 117.333)

        # Check dynamic inputs on a FxMap
        fxMap = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.FXMAPS)[0]
        distance = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.DISTANCE)[0]
        curve = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.CURVE)[0]

        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=distance, aRightNode=fxMap, aRightNodeInput=sbsenum.InputEnum.INPUT_PATTERN),
                              sbscommon.SBSConnection)
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=distance, aRightNode=fxMap, aRightNodeInput='inputpattern:1'),
                              sbscommon.SBSConnection)
        self.assertIsInstance(allNodeGraph.connectNodes(aLeftNode=curve, aRightNode=fxMap, aRightNodeInput='inputpattern:2'),
                              sbscommon.SBSConnection)
        with self.assertRaises(SBSImpossibleActionError):
                allNodeGraph.connectNodes(aLeftNode=distance, aRightNode=fxMap, aRightNodeInput='inputpattern:4')



    def test_DeleteNode(self):
        """
        This test checks deleting a node and its connections
        """
        log.info("Test Graph: Delete Node")
        sbsDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')

        aGraph = sbsDoc.getSBSGraph('AllNodes')
        warpNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.WARP)[0]
        curvNode = aGraph.getAllNodeInstancesOf(sbsDoc, 'sbs://curvature.sbs')[0]
        outputNode = aGraph.getGraphOutputNode(aOutputIdentifier='output')

        self.assertTrue(curvNode.isConnectedTo(warpNode))
        self.assertTrue(outputNode.isConnectedTo(warpNode))

        # Delete Warp
        self.assertTrue(aGraph.deleteNode(warpNode))
        self.assertIsNone(aGraph.getNode(warpNode))
        self.assertIsNone(aGraph.getNode(warpNode.mUID))
        self.assertFalse(curvNode.isConnectedTo(warpNode))
        self.assertFalse(outputNode.isConnectedTo(warpNode))
        self.assertEqual(len(curvNode.mConnections), 0)
        self.assertEqual(len(outputNode.mConnections), 0)

        bitmapNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BITMAP)[0]
        blendNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BLEND)[0]
        grayscaleConvNodes = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.GRAYSCALECONVERSION)
        grayscaleConvNode = next(aNode for aNode in grayscaleConvNodes if aNode.isConnectedTo(bitmapNode))
        self.assertTrue(blendNode.isConnectedTo(bitmapNode))
        self.assertEqual(len(blendNode.mConnections), 3)
        self.assertTrue(grayscaleConvNode.isConnectedTo(bitmapNode))

        # Delete Bitmap
        self.assertTrue(aGraph.deleteNode(bitmapNode))
        self.assertIsNone(aGraph.getNode(bitmapNode))
        self.assertFalse(blendNode.isConnectedTo(bitmapNode))
        self.assertFalse(grayscaleConvNode.isConnectedTo(bitmapNode))
        self.assertEqual(len(blendNode.mConnections), 2)
        self.assertEqual(len(grayscaleConvNode.mConnections), 0)

        # Delete Input
        aInputNode = aGraph.getGraphInputNode('input')
        self.assertTrue(aGraph.deleteNode(aInputNode))
        self.assertIsNone(aGraph.getInputImageFromInputNode(aInputNode))

        aInputNode = aGraph.createInputNode(aIdentifier='input')
        self.assertIsInstance(aGraph.getInputImageFromInputNode(aInputNode), graph.SBSParamInput)
        self.assertTrue(aGraph.deleteInputParameter('input'))
        self.assertIsNone(aGraph.getInputImageFromInputNode(aInputNode))
        self.assertIsNone(aGraph.getGraphInputNode(aInputImageIdentifier='input'))
        self.assertIsNone(aGraph.getInput(aInputIdentifier='input'))

        # Delete Output
        aOutput = aGraph.getGraphOutputWithUsage(aUsage=sbsenum.UsageEnum.NORMAL)
        aOutputNode = aGraph.getGraphOutputNode(aOutput.mIdentifier)
        self.assertIsNotNone(aGraph.mRoot.getRootOutput(aOutput.mUID))
        aGraph.deleteNode(aOutputNode)
        self.assertIsNone(aGraph.getGraphOutput(aOutput.mIdentifier))
        self.assertIsNone(aGraph.mRoot.getRootOutput(aOutput.mUID))

        log.info("Test Graph: Delete Node: OK\n")

    def test_CurveNode(self):
        """
        This test checks creating a curve node with curves definition
        """
        log.info("Test Graph: Curve Node")
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testCurveNode.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath=docAbsPath, aGraphIdentifier='Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')

        # Curve definition
        aCurve = sbslibrary.CurveDefinition.initCurve(aIdentifier = sbsenum.CurveTypeEnum.LUMINANCE)
        aCurveKey = sbslibrary.CurveKey(aPosition=[0.5,0.5], aLeft=[0.4,0.5], aRight=[0.6,0.5])
        aCurve.addCurveKey(aCurveKey)
        aCurveNode = aGraph.createCurveNode(aCurveDefinitions=[aCurve])
        paramArrays = aCurveNode.getCompFilter().mParamArrays
        self.assertEqual(len(paramArrays), 1)
        self.assertEqual(len(paramArrays[0].mParamsArrayCells), 3)

        aCurve.moveKeyTo(aCurveKey=aCurveKey, aPosition=[0.6,0.6])
        self.assertEqual(aCurve.mCurveKeys[2].mPosition, [0.6,0.6])

        aCurveKey2 = sbslibrary.CurveKey(aPosition=[0.5,0.5], aLeft=[0.4,0.5], aRight=[0.6,0.5])
        aCurve.addCurveKey(aCurveKey2)
        aCurve.moveKeyTo(aCurveKey=aCurveKey2, aPosition=[0.7,0.6])
        self.assertEqual(aCurve.mCurveKeys[3].mPosition, [0.6,0.6])

        aCurveNode.setCurveDefinition(aCurveDefinition=aCurve)
        paramArrays = aCurveNode.getCompFilter().mParamArrays
        self.assertEqual(len(paramArrays), 1)
        self.assertEqual(len(paramArrays[0].mParamsArrayCells), 4)

        aCurve = sbslibrary.CurveDefinition.initCurve(aIdentifier = sbsenum.CurveTypeEnum.RED)
        aCurveKey = sbslibrary.CurveKey(aPosition=[0.5,0.5],
                                        aLeft=[0.4,0.5],
                                        aRight=[0.6,0.5])
        aCurve.addCurveKey(aCurveKey)
        aCurveNode.setCurveDefinition(aCurveDefinition=aCurve)
        paramArrays = aCurveNode.getCompFilter().mParamArrays
        self.assertEqual(len(paramArrays), 2)

        self.assertTrue(sbsDoc.writeDoc())

        destDoc = substance.SBSDocument(context.Context(), docAbsPath)
        self.assertTrue(destDoc.parseDoc())

        refAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refCurveNode.sbs')
        refDoc = substance.SBSDocument(context.Context(), refAbsPath)
        self.assertTrue(refDoc.parseDoc())

        self.assertTrue(refDoc.equals(destDoc))
        os.remove(sbsDoc.mFileAbsPath)

    def test_TextNode(self):
        """
        This test checks creating a text node with text/font definition
        """
        log.info("Test Graph: Text Node")
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testTextNode.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(aContext=context.Context(), aFileAbsPath=docAbsPath, aGraphIdentifier='Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')

        # Create a first empty text node
        aTextNode1 = aGraph.createTextNode()

        # Create a 2nd text node connected to a uniform color
        aUniformColor = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.UNIFORM,
                                                    aParameters={sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [0,0.5,0,1],
                                                                 sbsenum.CompNodeParamEnum.OUTPUT_FORMAT: sbsenum.OutputFormatEnum.FORMAT_16BITS_FLOAT},
                                                    aInheritance={sbsenum.CompNodeParamEnum.OUTPUT_FORMAT: sbsenum.ParamInheritanceEnum.ABSOLUTE})

        aTextNode2 = aGraph.createTextNode(aFontFamily='Calibri',
                                          aFontSubFamily='Bold Italic',
                                          aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE:    sbsenum.ColorModeEnum.COLOR,
                                                       sbsenum.CompNodeParamEnum.TEXT:          "A first' text",
                                                       sbsenum.CompNodeParamEnum.TEXT_ALIGN:    sbsenum.TextAlignEnum.LEFT,
                                                       sbsenum.CompNodeParamEnum.TEXT_POSITION: [-0.5,0],
                                                       sbsenum.CompNodeParamEnum.TEXT_FONT_SIZE: 0.15,
                                                       sbsenum.CompNodeParamEnum.TILING_MODE:   sbsenum.TilingEnum.NO_TILING},
                                          aInheritance={sbsenum.CompNodeParamEnum.TILING_MODE: sbsenum.ParamInheritanceEnum.ABSOLUTE},
                                          aGUIPos=aUniformColor.getOffsetPosition([150,0]))

        self.assertFalse(aTextNode1.hasIdenticalParameters(aTextNode2))

        # Duplicate the 2nd text node and check that the parameters are identical
        aTextNode3 = aGraph.duplicateNode(aTextNode2, aGUIOffset=[150,0])
        self.assertTrue(aTextNode2.hasIdenticalParameters(aTextNode3))

        # Change some parameters
        aTextNode2.setParameterValue(sbsenum.CompNodeParamEnum.TEXT, u'My &text\nis <very> "simple\'é€$çà')
        self.assertFalse(aTextNode2.hasIdenticalParameters(aTextNode3))
        aTextNode2.setParameterValue(sbsenum.CompNodeParamEnum.TRANSFORM_MATRIX, [0.5,0.02,-1,1.5])
        self.assertFalse(aTextNode2.hasIdenticalParameters(aTextNode3))

        # Delete the 3rd text node
        aGraph.deleteNode(aTextNode3)

        aGraph.connectNodes(aLeftNode=aUniformColor, aRightNode=aTextNode2)

        # Add a String input parameter to the graph and set it as the value of the 1st text node
        aParam = aGraph.addInputParameter(aIdentifier='TextInput',
                                          aWidget=sbsenum.WidgetEnum.TEXT_STRING,
                                          aDefaultValue=u'<hey>& what ? éà@')
        dynFunction = aTextNode1.setDynamicParameter(sbsenum.CompNodeParamEnum.TEXT)
        dynFunction.setToInputParam(aParentGraph=aGraph, aInputParamIdentifier=aParam.mIdentifier)

        self.assertTrue(sbsDoc.writeDoc())
        destDoc =  substance.SBSDocument(context.Context(), docAbsPath)
        self.assertTrue(destDoc.parseDoc())

        refAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/refTextNode.sbs')
        refDoc = substance.SBSDocument(context.Context(), refAbsPath)
        self.assertTrue(refDoc.parseDoc())

        self.assertTrue(refDoc.equals(destDoc))
        refNode = refDoc.getSBSGraph('Graph').getAllFiltersOfKind(sbsenum.FilterEnum.TEXT)[1]
        destNode = destDoc.getSBSGraph('Graph').getAllFiltersOfKind(sbsenum.FilterEnum.TEXT)[1]
        self.assertTrue(refNode.hasIdenticalParameters(destNode))

        os.remove(sbsDoc.mFileAbsPath)

    def test_Widget(self):
        """
        This test checks adding, getting and setting the widget of an input parameter
        """
        log.info("Test Graph: Input parameters widget")
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/AllInputParameters.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath, 'AllInputParameters')
        aGraph = sbsDoc.getSBSGraph('AllInputParameters')

        # Retrieve enumeration values
        members = inspect.getmembers(sbsenum.WidgetEnum)
        widgetEnumValues = [memberValue for memberName,memberValue in members if not SBSGraphTests.isPrivateMember(memberName)]

        for aWidgetKind in sorted(widgetEnumValues):
            aGraph.addInputParameter(aIdentifier='inputWidget_'+str(aWidgetKind), aWidget=aWidgetKind)

        for aWidgetKind in sorted(widgetEnumValues):
            aParam = aGraph.getInputParameter(aInputParamIdentifier='inputWidget_'+str(aWidgetKind))
            aWidgetDef = sbslibrary.getDefaultWidget(aWidget=aWidgetKind)

            aClamp = aParam.getClamp()
            if aWidgetDef.hasOption(sbsenum.WidgetOptionEnum.CLAMP):    self.assertIsInstance(aClamp, bool)
            else:                                                       self.assertIsNone(aClamp)

            aStep = aParam.getStep()
            if aWidgetDef.hasOption(sbsenum.WidgetOptionEnum.STEP):     self.assertTrue(isinstance(aStep, int) or isinstance(aStep, float))
            else:                                                       self.assertIsNone(aStep)

            aMin = aParam.getMinValue()
            if aWidgetDef.hasOption(sbsenum.WidgetOptionEnum.MIN):      self.assertTrue(isinstance(aMin, int) or isinstance(aMin, float))
            else:                                                       self.assertIsNone(aMin)

            aMax = aParam.getMaxValue()
            if aWidgetDef.hasOption(sbsenum.WidgetOptionEnum.MAX):      self.assertTrue(isinstance(aMax, int) or isinstance(aMax, float))
            else:                                                       self.assertIsNone(aMax)

            self.assertIsNotNone(aParam.getDefaultValue())
            self.assertIsInstance(aParam.getLabels(), list)
            self.assertEqual(aParam.getWidgetType(), aWidgetDef.mWidget)

        self.assertTrue(sbsDoc.writeDoc())

        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        self.assertTrue(sbsDoc.parseDoc())
        aGraph = sbsDoc.getSBSGraph('AllInputParameters')

        # Bool
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.BUTTON_BOOL))
        self.assertEqual(aParam.getDimension(), 1)
        self.assertEqual(aParam.getDefaultValue(), False)
        self.assertEqual(aParam.getMinValue(), None)
        self.assertEqual(aParam.getMaxValue(), None)
        self.assertEqual(aParam.getClamp(), None)
        self.assertEqual(aParam.getStep(), None)
        self.assertEqual(aParam.getLabels(), ['False','True'])

        # int1 slider
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.SLIDER_INT1))
        self.assertEqual(aParam.getDefaultValue(), 1)
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMaxValue(), 10)
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), 1)
        self.assertEqual(aParam.getLabels(), [])

        # int1 drop down
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.DROPDOWN_INT1))
        self.assertEqual(aParam.getDefaultValue(), 0)
        self.assertEqual(aParam.getMinValue(), None)
        self.assertEqual(aParam.getMaxValue(), None)
        self.assertEqual(aParam.getClamp(), None)
        self.assertEqual(aParam.getStep(), None)
        self.assertEqual(aParam.getLabels(), [])
        self.assertEqual(aParam.getDropDownList(), {0:'0'})

        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([1])    # invalid value
        aParam.setDropDownList({0:'First',1:'Second'})
        aParam.setDefaultValue([1])
        self.assertEqual(aParam.getDefaultValue(), 1)
        self.assertEqual(aParam.mDefaultValue.getValue(), '1')
        aParam.setDropDownList({0: 'First', 2: 'Third'})
        self.assertEqual(aParam.getDefaultValue(), 0)
        self.assertEqual(aParam.mDefaultValue.getValue(), '0')

        # int2 slider
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.SLIDER_INT2))
        self.assertEqual(aParam.getDefaultValue(), [1,1])
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMaxValue(), 10)
        self.assertEqual(aParam.getMaxValue(asList=True), [10,10])
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), 1)
        self.assertEqual(aParam.getLabels(), ['X','Y'])

        # float1 slider
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.SLIDER_FLOAT1))
        self.assertEqual(aParam.getDefaultValue(), 1)
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMaxValue(), 1)
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), 0.01)
        self.assertEqual(aParam.getLabels(), [])

        # float2 slider
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.SLIDER_FLOAT2))
        self.assertEqual(aParam.getDefaultValue(), [1,1])
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMinValue(asList=True), [0.0,0.0])
        self.assertEqual(aParam.getMaxValue(), 1)
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), 0.01)
        self.assertEqual(aParam.getLabels(), ['X','Y'])

        aParam.setMinValue(-1)
        aParam.setMaxValue(10)
        aParam.setClamp(True)
        aParam.setLabels(['A', 'B'])
        aParam.setDefaultValue([0.1,2.0,3.4])
        self.assertEqual(aParam.getDefaultValue(), [0.1,2])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2')
        aParam.setStep(0.1)
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([11.2,0.5])     # invalid range
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([1.2,-1.5])     # invalid range
        self.assertEqual(aParam.getDefaultValue(), [0.1,2])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2')

        # float3 color
        aParam = aGraph.getInputParameter('inputWidget_' + str(sbsenum.WidgetEnum.COLOR_FLOAT3))
        self.assertEqual(aParam.getDimension(), 3)
        self.assertEqual(aParam.getDefaultValue(), [1, 1, 1])
        self.assertEqual(aParam.getMinValue(), 0.0)
        self.assertEqual(aParam.getMaxValue(), 1.0)
        self.assertEqual(aParam.getClamp(), True)
        self.assertEqual(aParam.getStep(), None)
        self.assertEqual(aParam.getLabels(), [])

        aParam.setClamp(True)
        aParam.setDefaultValue([0.1,0.0,0.440])
        self.assertEqual(aParam.getDefaultValue(), [0.1,0,0.44])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 0 0.44')
        with self.assertRaises(SBSImpossibleActionError):   aParam.setStep(1)                       # invalid option
        with self.assertRaises(SBSImpossibleActionError):   aParam.setLabels(['X','Y','Z'])         # invalid option
        with self.assertRaises(SBSImpossibleActionError):   aParam.setMinValue(-1)                  # invalid range
        with self.assertRaises(SBSImpossibleActionError):   aParam.setMaxValue(10)                  # invalid range
        with self.assertRaises(SBSImpossibleActionError):   aParam.setMinValue(12)                  # min > max
        with self.assertRaises(SBSImpossibleActionError):   aParam.setMaxValue(-5)                  # max < min
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([0.1,2,3.4])    # invalid range

        # transform
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.MATRIX_INVERSE_FLOAT4))
        self.assertEqual(aParam.getDefaultValue(), [1,0,0,1])
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMinValue(asList=True), [0.0,0.0,0.0,0.0])
        self.assertEqual(aParam.getMaxValue(), 1)
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), None)
        self.assertEqual(aParam.getLabels(), [])

        aParam.setMinValue(-1)
        aParam.setMaxValue(10)
        aParam.setClamp(True)
        with self.assertRaises(SBSImpossibleActionError):
            aParam.setLabels(['A', 'B', 'C', 'D'])
        aParam.setDefaultValue([0.1,2.0,3.4,4.4,5.5])
        self.assertEqual(aParam.getDefaultValue(), [0.1,2.0,3.4,4.4])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2 3.4 4.4')
        with self.assertRaises(SBSImpossibleActionError):
            aParam.setStep(0.1)
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([11.2,0.5,10,10])     # invalid range
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([1.2,-1.5,-10,-10])     # invalid range
        self.assertEqual(aParam.getDefaultValue(), [0.1,2,3.4,4.4])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2 3.4 4.4')

        # transform forward
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.MATRIX_FORWARD_FLOAT4))
        self.assertEqual(aParam.getDefaultValue(), [1,0,0,1])
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMinValue(asList=True), [0.0,0.0,0.0,0.0])
        self.assertEqual(aParam.getMaxValue(), 1)
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), None)
        self.assertEqual(aParam.getLabels(), [])

        aParam.setMinValue(-1)
        aParam.setMaxValue(10)
        aParam.setClamp(True)
        with self.assertRaises(SBSImpossibleActionError):
            aParam.setLabels(['A', 'B', 'C', 'D'])
        aParam.setDefaultValue([0.1,2.0,3.4,4.4,5.5])
        self.assertEqual(aParam.getDefaultValue(), [0.1,2.0,3.4,4.4])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2 3.4 4.4')
        with self.assertRaises(SBSImpossibleActionError):
            aParam.setStep(0.1)
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([11.2,0.5,10,10])     # invalid range
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([1.2,-1.5,-10,-10])     # invalid range
        self.assertEqual(aParam.getDefaultValue(), [0.1,2,3.4,4.4])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2 3.4 4.4')

        # string text
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.TEXT_STRING))
        self.assertEqual(aParam.getDefaultValue(), '')
        aParam.setDefaultValue('')
        self.assertEqual(aParam.getDefaultValue(), '')
        aParam.setDefaultValue('yeah')
        self.assertEqual(aParam.getDefaultValue(), 'yeah')
        aParam.setDefaultValue(10)
        self.assertEqual(aParam.getDefaultValue(), '10')
        aParam.setDefaultValue(u'yeah<div>\n\'\téàç')
        self.assertEqual(aParam.getDefaultValue(), u'yeah<div>\n\'\téàç')

        # position float 2
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.POSITION_FLOAT2))
        self.assertEqual(aParam.getDefaultValue(), [0,0])
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMinValue(asList=True), [0.0,0.0])
        self.assertEqual(aParam.getMaxValue(), 1)
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), 0.01)
        self.assertEqual(aParam.getLabels(), ['X','Y'])

        aParam.setMinValue(-1)
        aParam.setMaxValue(10)
        aParam.setClamp(True)
        aParam.setLabels(['A', 'B'])
        aParam.setDefaultValue([0.1,2.0,3.4])
        self.assertEqual(aParam.getDefaultValue(), [0.1,2])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2')
        aParam.setStep(0.1)
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([11.2,0.5])     # invalid range
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([1.2,-1.5])     # invalid range
        self.assertEqual(aParam.getDefaultValue(), [0.1,2])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2')

        # offset float 2
        aParam = aGraph.getInputParameter('inputWidget_'+str(sbsenum.WidgetEnum.OFFSET_FLOAT2))
        self.assertEqual(aParam.getDefaultValue(), [0,0])
        self.assertEqual(aParam.getMinValue(), 0)
        self.assertEqual(aParam.getMinValue(asList=True), [0.0,0.0])
        self.assertEqual(aParam.getMaxValue(), 1)
        self.assertEqual(aParam.getClamp(), False)
        self.assertEqual(aParam.getStep(), 0.01)
        self.assertEqual(aParam.getLabels(), ['X','Y'])

        aParam.setMinValue(-1)
        aParam.setMaxValue(10)
        aParam.setClamp(True)
        aParam.setLabels(['A', 'B'])
        aParam.setDefaultValue([0.1,2.0,3.4])
        self.assertEqual(aParam.getDefaultValue(), [0.1,2])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2')
        aParam.setStep(0.1)
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([11.2,0.5])     # invalid range
        with self.assertRaises(SBSImpossibleActionError):   aParam.setDefaultValue([1.2,-1.5])     # invalid range
        self.assertEqual(aParam.getDefaultValue(), [0.1,2])
        self.assertEqual(aParam.mDefaultValue.getValue(), '0.1 2')


        # Check serialization
        self.assertTrue(sbsDoc.writeDoc())
        os.remove(docAbsPath)

        log.info("Test Graph: Input parameters widget: OK\n")


    def test_Attribute(self):
        """
        This test checks getting and setting the attributes of a graph
        """
        log.info("Test Graph: Attributes")
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testAttributes.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath, 'Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')
        aGroup = sbsDoc.createGroup('MyGroup')

        sbsDoc.setDescription('M&y\n"pretty\'|\n<Description>$')
        aGroup.setDescription(u"éà&\n<group>'\n45€$")

        aGraph.setAttribute(sbsenum.AttributesEnum.Author, '<div>&\\n</div>')
        aGraph.setAttribute(sbsenum.AttributesEnum.AuthorURL, 'this& is not an URL !<div>')
        aGraph.setAttribute(sbsenum.AttributesEnum.Category, "C&at['etogy']<div>")
        aGraph.setAttribute(sbsenum.AttributesEnum.Description, 'M&y\n"pretty\'|\n<Attributes>$')
        aGraph.setAttribute(sbsenum.AttributesEnum.HideInLibrary, True)
        aGraph.setAttribute(sbsenum.AttributesEnum.Label, 'L&abelou123456<div>')
        aGraph.setAttribute(sbsenum.AttributesEnum.Tags, u"on&e éà'\"<div\>\\n/ tag\\t")
        aGraph.setAttribute(sbsenum.AttributesEnum.UserTags, 'D&on\'t know what to say\nIs there a new line ?\n<div>')
        aGraph.setAttribute(sbsenum.AttributesEnum.PhysicalSize, [8, 22, 10.5])
        self.assertTrue(aGraph.mAttributes.hasAttributes())

        aFunction = sbsDoc.createFunction(aFunctionIdentifier='Function')
        aFunction.setAttribute(sbsenum.AttributesEnum.Author, u'éà\'"<div\>\\n/')
        aFunction.setAttribute(sbsenum.AttributesEnum.AuthorURL, u'éà\'"<div\>\\n/')
        aFunction.setAttribute(sbsenum.AttributesEnum.Category, u"éà'\"<div\>\\n/")
        aFunction.setAttribute(sbsenum.AttributesEnum.Description, u'"a\n"Des<div>cript&ion\'')
        aFunction.setAttribute(sbsenum.AttributesEnum.HideInLibrary, True)
        aFunction.setAttribute(sbsenum.AttributesEnum.Label, u'éà\'"<div\>\\n/')
        aFunction.setAttribute(sbsenum.AttributesEnum.Tags, u"one éà'\"<div\>\\n/ tag\\t")
        aFunction.setAttribute(sbsenum.AttributesEnum.UserTags, 'Don\\\'t know what to say\\nIs there a new line ?\\n<div>')

        aGraph.addInputParameter(aIdentifier = u'$éàlors!ù1€£-+',
                                 aWidget     = sbsenum.WidgetEnum.SLIDER_FLOAT1,
                                 aDescription= 'M&y\n"pretty\'|\n<Attributes>$',
                                 aLabel      = u'on&e éà\'"<div\>\\n/ tag\\t',
                                 aGroup      = u'on&e éà\'"<div\>\\n/ tag\\t',
                                 aUserData   = 'D&on\'t know what to say\\nIs there a new line ?\\n<div>',
                                 aVisibleIf  = u"on&e éà'\"<div\>\\n/ tag\\t")

        aGraph.createOutputNode(aIdentifier = u'$éàlors!ù1€£-+',
                                aAttributes = {sbsenum.AttributesEnum.Label: 'My label',
                                               sbsenum.AttributesEnum.UserTags: u'&Don\\\'t know whàt to say\\nIs thére a new line ?\\n<div>'},
                                aGroup = u'a<Group> \\t &àù$€\'"',
                                aVisibleIf = u'on&e éà\'"<div\>\\n/ tag\\t')
        aGraphOutput = aGraph.getGraphOutput(aOutputIdentifier=u'_éàlors!ù1__-+')
        aGraphOutput.setAttribute(sbsenum.AttributesEnum.Label, u'éà\'"<div\>\\n/')
        aGraphOutput.setAttribute(sbsenum.AttributesEnum.Description, 'M&y\n"pretty\'|\n<Attributes>$')

        with self.assertRaises(SBSImpossibleActionError):   aGraphOutput.setAttribute(sbsenum.AttributesEnum.HideInLibrary, True)
        with self.assertRaises(SBSImpossibleActionError):   aGraphOutput.setAttribute(sbsenum.AttributesEnum.Author, 'Author')

        aGraph.createInputNode(aIdentifier = u'$éàlors!ù1€£-+',
                               aAttributes = {sbsenum.AttributesEnum.Label: 'My label',
                                               sbsenum.AttributesEnum.UserTags: u'&Don\\\'t know whàt to say\nIs thére a new line ?\n<div>'},
                               aGroup = u'a<Group> \\t &àù$€\'"',
                               aVisibleIf = u'on&e éà\'"<div\>\\n/ tag\\t')

        aInputImage = aGraph.getInputImage(aInputImageIdentifier=u'_éàlors!ù1__-+_1')
        aInputImage.setAttribute(sbsenum.AttributesEnum.Label, u'éà\'"<div\>\\n/')
        aInputImage.setAttribute(sbsenum.AttributesEnum.Description, 'M&y\n"pretty\'|\n<Attributes>$')

        aGraph.createBitmapNode(aSBSDocument=sbsDoc,
                                aResourcePath=sbsDoc.buildAbsPathFromRelToMePath('Craters.png'),
                                aParameters={sbsenum.CompNodeParamEnum.OUTPUT_SIZE:[10,10]},
                                aAttributes={sbsenum.AttributesEnum.UserTags:u'<A>\\nUser\'data\'é@à',
                                             sbsenum.AttributesEnum.HideInLibrary:True},
                                aResourceGroup=None,
                                aAutodetectImageParameters=True)
        aResource = sbsDoc.getSBSResource('Craters')
        self.assertEqual(sbsDoc.getObjectInternalPath(aResource.mUID, addDependencyUID=False), 'pkg:///Craters')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.UserTags), u'<A>\\nUser\'data\'é@à')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.HideInLibrary), True)

        aGroup = sbsDoc.createGroup('Resources')
        sbsDoc.moveObjectUnderGroup(aResource, aGroup)

        self.assertTrue(sbsDoc.writeDoc())
        resDoc = SBSGraphTests.openTestDocument('testAttributes.sbs')

        refDoc = SBSGraphTests.openTestDocument('refAttributes.sbs')
        self.assertTrue(resDoc.equals(refDoc))

        aGraph = resDoc.getSBSGraph('Graph')
        self.assertEqual(resDoc.getDescription(), 'M&y\n"pretty\'|\n<Description>$')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.Author), '<div>&\\n</div>')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.HideInLibrary), True)
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.UserTags), 'D&on\'t know what to say\nIs there a new line ?\n<div>')
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.Tags), u"on&e éà'\"<div\>\\n/ tag\\t")
        self.assertEqual(aGraph.getAttribute(sbsenum.AttributesEnum.PhysicalSize), [8, 22, 10.5])

        aResource = sbsDoc.getSBSResource('Craters')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.UserTags), u'<A>\\nUser\'data\'é@à')
        self.assertEqual(aResource.getAttribute(sbsenum.AttributesEnum.HideInLibrary), True)

        os.remove(resDoc.mFileAbsPath)

    def test_Icon(self):
        """
        This test checks setting an icon as an attributes of a graph
        """
        log.info("Test Graph: Set Icon")
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, 'resources/testIcon.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath, 'Graph')

        aGraph = sbsDoc.getSBSGraph('Graph')
        iconPath = python_helpers.getAbsPathFromModule(testModule, 'resources/Craters.png')
        aIcon = aGraph.setIcon(iconPath)
        self.assertIsInstance(aIcon, sbscommon.SBSIcon)
        self.assertEqual(aIcon, aGraph.getIcon())
        self.assertEqual(aIcon.mFormat, 'png')

        aGraph2 = sbsDoc.createGraph(aGraphIdentifier='Graph2')
        iconPath = python_helpers.getAbsPathFromModule(testModule, 'resources/Craters_rect.jpg')
        aIcon = aGraph2.setIcon(iconPath)
        self.assertIsInstance(aIcon, sbscommon.SBSIcon)
        self.assertEqual(aIcon.mFormat, 'jpg')

        iconPath = python_helpers.getAbsPathFromModule(testModule, 'resources/errorFile.png')
        with self.assertRaises(IOError):
            aGraph.setIcon(iconPath)

        self.assertTrue(sbsDoc.writeDoc())

        resDoc = substance.SBSDocument(context.Context(), sbsDoc.mFileAbsPath)
        self.assertTrue(resDoc.parseDoc())

        refDoc = substance.SBSDocument(context.Context(), resDoc.buildAbsPathFromRelToMePath('refIcon.sbs'))
        self.assertTrue(refDoc.parseDoc())
        self.assertTrue(resDoc.equals(refDoc))

        os.remove(sbsDoc.mFileAbsPath)

    def test_Preset(self):
        """
        This test checks the editing functionalities of embedded presets within a graph
        """
        log.info("Test Graph: Presets")

        labels = ["preset0", "preset1", "preset2"]
        usertags = ["blue", "green", "red"]
        uids = [["1283618323", "1283618329"],
                ["1283618323", "1283618329"],
                ["1283618323", "1283618329"]]
        identifiers = [["colorswitch", "outputcolor"],
                       ["colorswitch", "outputcolor"],
                       ["colorswitch", "outputcolor"]]
        values = [["1", "0 0 1 1"],
                  ["1", "0 1 0 1"],
                  ["1", "1 0 0 1"]]
        types = [[16, 2048],
                 [16, 2048],
                 [16, 2048]]

        refDoc = SBSGraphTests.openTestDocument('refPresets.sbs')
        aGraph = refDoc.getSBSGraph('New_Graph')

        self.assertEqual(3, len(aGraph.getAllPresets()))
        for i in range(3):
            aPreset = aGraph.mPresets[i]
            aCheck = aGraph.getPreset(aPresetLabel=labels[i])
            self.assertEqual(aPreset, aCheck)
            self.assertEqual(2, len(aPreset.mPresetInputs))
            self.assertEqual(labels[i], aPreset.mLabel)
            self.assertEqual(usertags[i], aPreset.mUsertags)
            for j in range(2):
                aPresetInput = aPreset.mPresetInputs[j]
                self.assertEqual(uids[i][j], aPresetInput.mUID)
                self.assertEqual(identifiers[i][j], aPresetInput.mIdentifier)
                self.assertEqual(values[i][j], aPresetInput.mValue.getValue())
                self.assertEqual(types[i][j], aPresetInput.getType())

    def test_PresetCommonInterface(self):
        """
        This test checks the common interface for preset between SBSObject and SBSARObject
        """
        sbsDoc = SBSGraphTests.openTestDocument('Presets.sbs')
        sbsGraph = sbsDoc.getSBSGraph('Presets')

        sbsarFile = sbsDoc.buildAbsPathFromRelToMePath('Presets.sbsar')
        sbsarDoc = sbsarchive.SBSArchive(context.Context(), sbsarFile)
        sbsarDoc.parseDoc()
        sbsarGraph = sbsarDoc.getSBSGraph('Presets')

        self.assertEqual(len(sbsGraph.getAllPresets()), len(sbsarGraph.getAllPresets()))
        for sbsPreset in sbsGraph.getAllPresets():
            sbsarPreset = sbsarGraph.getPreset(sbsPreset.mLabel)
            self.assertEqual(len(sbsPreset.mPresetInputs), len(sbsarPreset.mPresetInputs))
            for sbsPresetInput in sbsPreset.getPresetInputs():
                sbsarPresetInput = sbsarPreset.getPresetInputFromIdentifier(aInputParamIdentifier=sbsPresetInput.mIdentifier)
                self.assertEqual(sbsarPresetInput.getTypedValue(), sbsPresetInput.getTypedValue())

        aPreset = sbsGraph.getPreset(u'Preset1&<div>_&$')
        self.assertEqual(aPreset.mUsertags, u'test\ntag\né&é\'\n<div>\n')

        inputParams = sbsGraph.getInputParameters()

        # Create an empty preset, and set the preset values
        aEmptyPreset = sbsGraph.createPreset(aLabel=u'<&EmptyPreset>', aUsertags='First Tag Cool')
        self.assertEqual(len(aEmptyPreset.getPresetInputs()), 0)

        # - Set values on an empty preset
        values = [True,
                  [1,2],
                  [0.5,0.8,0.03],
                  12.5,
                  'test']
        for i,aInputParam in enumerate(inputParams):
            aEmptyPreset.setPresetInput(aInputParam=aInputParam, aPresetValue=values[i])
        self.assertEqual(len(aEmptyPreset.getPresetInputs()), len(values))

        # - Check values
        for i,aInputParam in enumerate(inputParams):
            aPresetInput = aEmptyPreset.getPresetInput(aInputParam)
            self.assertEqual(aPresetInput.getTypedValue(), values[i])

        # Create a preset initialized with the current input parameters values
        aNewPreset = sbsGraph.createPreset(aLabel='NewPreset', aUsertags='First Tag Cool', setCurrentDefaultValues=True)
        self.assertEqual(len(aNewPreset.getPresetInputs()), len(inputParams))

        # - Check that values are identical to the default parameters values
        for i,aInputParam in enumerate(inputParams):
            aPresetInput = aNewPreset.getPresetInput(aInputParam)
            self.assertEqual(aPresetInput.getTypedValue(), aInputParam.getDefaultValue())

        # - Set values on an already filled preset
        values = [False,
                  [1,2],
                  [0.5,0.8,0.03],
                  12.5,
                  u'<&test>']
        for i,aInputParam in enumerate(inputParams):
            aNewPreset.setPresetInput(aInputParam=aInputParam, aPresetValue=values[i])
        self.assertEqual(len(aNewPreset.getPresetInputs()), len(values))

        # - Check values
        for i,aInputParam in enumerate(inputParams):
            aPresetInput = aNewPreset.getPresetInput(aInputParam)
            self.assertEqual(aPresetInput.getTypedValue(), values[i])

        # Check delete functions
        for aInputParam in inputParams:
            self.assertTrue(aEmptyPreset.deletePresetInput(aInputParam))
        self.assertEqual(len(aEmptyPreset.getPresetInputs()), 0)

        self.assertEqual(len(sbsGraph.getAllPresets()), 4)
        sbsGraph.deletePreset(aEmptyPreset.mLabel)
        self.assertEqual(len(sbsGraph.getAllPresets()), 3)

        with self.assertRaises(SBSImpossibleActionError):
            sbsGraph.deletePreset(aEmptyPreset)

        # Check serialization
        destPath = sbsDoc.buildAbsPathFromRelToMePath('testPreset.sbs')
        self.assertTrue(sbsDoc.writeDoc(aNewFileAbsPath=destPath))

        resDoc = substance.SBSDocument(context.Context(), destPath)
        self.assertTrue(resDoc.parseDoc())
        resGraph = resDoc.getSBSGraph(sbsGraph.mIdentifier)
        self.assertEqual(len(resGraph.getAllPresets()), 3)
        resPreset = resGraph.getPreset(aPresetLabel=aNewPreset.mLabel)
        self.assertIsNotNone(resPreset)
        for aPresetInput in aNewPreset.getPresetInputs():
            resPresetInput = resPreset.getPresetInput(aPresetInput.mUID)
            self.assertEqual(resPresetInput.mUID, aPresetInput.mUID)
            self.assertEqual(resPresetInput.mIdentifier, aPresetInput.mIdentifier)
            self.assertEqual(resPresetInput.getValue(), aPresetInput.getValue())
            self.assertEqual(resPresetInput.getTypedValue(), aPresetInput.getTypedValue())
        os.remove(destPath)

    def test_GuiObjects(self):
        """
        This test checks the creation/edition/removal of GUI Objects.
        It also checks getting the nodes included in a frame
        """
        log.info("Test Graph: GUI Objects operation")

        docAbsPath = python_helpers.getAbsPathFromModule(testModule, 'resources/testGUIObjects.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath, 'Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')
        aPixProcNode = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.PIXEL_PROCESSOR, aGUIPos=[1488, -144, 0])

        # Check creation of GUIObjects
        grComment1 = aGraph.createComment(aGUIPos = [-1184, -192, 0])
        grComment2 = aGraph.createComment(aCommentText = u'Test <div>\n&é""\'(-è\içà)=$^*ù!:', aGUIPos = [-176, -48, -100], aLinkToNode=aPixProcNode)
        grFrame1 = aGraph.createFrame(aGUIPos=[-1104, -622, 0], aSize=[565, 384])
        grFrame2 = aGraph.createFrame(aFrameTitle=u'é<div>\\t$£€&1', aCommentText=u'\n<is>à', aGUIPos=[206, -448, -100], aSize=[789, 138], aColor=[0.13, 0.66, 0, 0.1])
        grPin    = aGraph.createNavigationPin(aPinText=u'<éà>&i', aGUIPos=[-410, -564, 0])
        self.assertTrue(grComment1.isAComment())
        self.assertTrue(grComment2.isAComment())
        self.assertTrue(grFrame1.isAFrame())
        self.assertTrue(grFrame2.isAFrame())
        self.assertTrue(grPin.isANavigationPin())
        self.assertEqual(aGraph.getNodeAssociatedToComment(aComment=grComment2), aPixProcNode)
        self.assertEqual(aGraph.getNodeAssociatedToComment(aComment=grComment1), None)
        self.assertEqual(aGraph.getCommentsAssociatedToNode(aPixProcNode)[0], grComment2)

        self.assertTrue(sbsDoc.writeDoc())

        # Check getting GUIObjects
        refDoc = SBSGraphTests.openTestDocument('AllNodes.sbs')
        allNodeGraph = refDoc.getSBSGraph('AllNodes')
        aGUIObjects = allNodeGraph.getAllGUIObjects()
        refComments = allNodeGraph.getAllComments()
        refFrames = allNodeGraph.getAllFrames()
        refPins = allNodeGraph.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 6)
        self.assertEqual(len(refComments), 2)
        self.assertEqual(len(refFrames), 3)
        self.assertEqual(len(refPins), 1)

        # Compare created GUIObject with their reference in AllNodes graph
        resDoc = substance.SBSDocument(aContext=context.Context(), aFileAbsPath=docAbsPath)
        self.assertTrue(resDoc.parseDoc())
        resGraph = resDoc.getSBSGraph('Graph')
        aGUIObjects = resGraph.getAllGUIObjects()
        resComments = resGraph.getAllComments()
        resFrames = resGraph.getAllFrames()
        resPins = resGraph.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 5)
        self.assertEqual(len(resComments), 2)
        self.assertEqual(len(resFrames), 2)
        self.assertEqual(len(resPins), 1)

        self.assertTrue(resFrames[0].equals(refFrames[0]))
        self.assertTrue(resFrames[1].equals(refFrames[1]))
        self.assertTrue(resComments[0].equals(refComments[0]))
        self.assertTrue(resComments[1].equals(refComments[1]))
        self.assertTrue(resPins[0].equals(refPins[0]))

        # Check getting nodes in the ROI of a frame
        refFrame = next((aFrame for aFrame in refFrames if aFrame.mTitle == 'Frame'), None)
        self.assertIsNotNone(refFrame)
        inFrameNodes = allNodeGraph.getNodesInFrame(refFrame)
        self.assertEqual(len(inFrameNodes), 5)
        aNode = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BITMAP)[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BLEND)[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.UNIFORM)[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.TEXT)[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.GRAYSCALECONVERSION)[0]
        self.assertTrue(aNode in inFrameNodes)

        aOutputs = allNodeGraph.getAllOutputNodes()
        aOutputFrame = allNodeGraph.createFrameAroundNodes(aNodeList = aOutputs, aFrameTitle='The outputs', aColor=[0, 0.75, 0.75, 0.19])
        refOutputFrame = next((aFrame for aFrame in refFrames if aFrame.mTitle == 'The outputs'), None)
        self.assertTrue(aOutputFrame.equals(refOutputFrame))
        self.assertTrue(aOutputFrame.mGUILayout.equals(refOutputFrame.mGUILayout))

        aOutputsUID = [aNode.mUID for aNode in aOutputs]
        aOutputFrame2 = allNodeGraph.createFrameAroundNodes(aNodeList = aOutputsUID, aFrameTitle='The outputs', aColor=[0, 0.75, 0.75, 0.19])
        self.assertEqual(aOutputFrame.getRect(), aOutputFrame2.getRect())

        self.assertIsInstance(allNodeGraph.getRect(), sbscommon.Rect)

        # Check deleting GUIObjects
        aGraph.deleteComment(grComment1)
        aGraph.deleteComment(grComment2.mUID)
        aGraph.deleteFrame(grFrame1)
        aGraph.deleteFrame(grFrame2.mUID)
        aGraph.deleteNavigationPin(grPin)
        self.assertEqual(len(aGraph.getAllGUIObjects()), 0)
        self.assertEqual(len(aGraph.getAllComments()), 0)
        self.assertEqual(len(aGraph.getAllFrames()), 0)
        self.assertEqual(len(aGraph.getAllNavigationPins()), 0)

        os.remove(docAbsPath)
        log.info("Test Graph: GUI Objects: OK\n")

    def test_MoveConnections(self):
        """
        This test checks the facilities to get and modify existing connections
        """
        destPath = python_helpers.getAbsPathFromModule(testModule, './resources/testMoveConnections.sbs')

        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath, 'Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')

        # Start from connections on R, and move them to G:
        # RGBA - R--------Gradient     =>        R
        #        G    |---Blend        =>        G--------Gradient
        #        B                     =>        B    |---Blend
        #        A--------Emboss       =>        A--------Emboss
        rgbaNode = aGraph.createCompInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='sbs://rgba_split.sbs')
        rgbaNode2 = aGraph.createCompInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='sbs://rgba_split.sbs')
        bitmap = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.BITMAP)
        inputNode = aGraph.createInputNode("toto")
        aGraph.connectNodes(inputNode, rgbaNode)
        blendNode    = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.BLEND)
        gradientNode = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.GRADIENT)
        embossNode   = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.EMBOSS)
        uniformNode  = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.UNIFORM)
        grayscaleNode  = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.GRAYSCALECONVERSION)

        self.assertIsInstance(rgbaNode, compnode.SBSCompNode)
        self.assertIsInstance(blendNode, compnode.SBSCompNode)
        self.assertIsInstance(gradientNode, compnode.SBSCompNode)
        self.assertIsInstance(embossNode, compnode.SBSCompNode)
        self.assertIsInstance(uniformNode, compnode.SBSCompNode)
        self.assertIsInstance(grayscaleNode, compnode.SBSCompNode)

        self.assertIsInstance(aGraph.connectNodes(aLeftNode=rgbaNode, aRightNode=blendNode, aLeftNodeOutput='R', aRightNodeInput=sbsenum.InputEnum.OPACITY),
                              sbscommon.SBSConnection)
        self.assertIsInstance(aGraph.connectNodes(aLeftNode=rgbaNode, aRightNode=blendNode, aLeftNodeOutput='R', aRightNodeInput=sbsenum.InputEnum.DESTINATION),
                              sbscommon.SBSConnection)
        self.assertIsInstance(aGraph.connectNodes(aLeftNode=rgbaNode, aRightNode=gradientNode, aLeftNodeOutput='R'),
                              sbscommon.SBSConnection)
        self.assertIsInstance(aGraph.connectNodes(aLeftNode=rgbaNode, aRightNode=embossNode, aLeftNodeOutput='A'),
                              sbscommon.SBSConnection)
        self.assertTrue(blendNode.isConnectedTo(rgbaNode))
        self.assertTrue(gradientNode.isConnectedTo(rgbaNode))
        self.assertTrue(embossNode.isConnectedTo(rgbaNode))

        ######################
        # Check output getters
        o1 = blendNode.getCompOutputFromIdentifier()
        o2 = blendNode.getCompOutputFromIdentifier(sbslibrary.getCompNodeOutput(sbsenum.OutputEnum.OUTPUT))
        o3 = blendNode.getCompOutputFromIdentifier(sbsenum.OutputEnum.OUTPUT)
        self.assertIsInstance(o1, compnode.SBSCompOutput)
        self.assertEqual(o1, o2)
        self.assertEqual(o1, o3)
        self.assertEqual(blendNode.getCompOutput(aCompOutputUID=o1.mUID), o1)

        o1 = rgbaNode.getCompOutputFromIdentifier()
        o2 = rgbaNode.getCompOutputFromIdentifier('R')
        o3 = rgbaNode.getCompOutputFromIdentifier('G')
        self.assertIsInstance(o1, compnode.SBSCompOutput)
        self.assertEqual(o1, o2)
        self.assertNotEqual(o1, o3)
        self.assertEqual(rgbaNode.getCompOutput(aCompOutputUID=o1.mUID), o1)
        self.assertEqual(rgbaNode.getCompOutput(aCompOutputUID=o3.mUID), o3)

        # Check output connections getters
        self.assertEqual(len(aGraph.getConnectionsFromNode(aLeftNode=rgbaNode)), 4)
        nbConnections = {'R':3, 'G':0, 'B':0, 'A':1}
        for output,nb in list(nbConnections.items()):
            self.assertEqual(len(aGraph.getConnectionsFromNode(aLeftNode=rgbaNode, aLeftNodeOutput=output)), nb)

        self.assertEqual(len(aGraph.getNodesConnectedFrom(aLeftNode=rgbaNode)), 3)
        nbNodesConnected = {'R':2, 'G':0, 'B':0, 'A':1}
        for output,nb in list(nbNodesConnected.items()):
            self.assertEqual(len(aGraph.getNodesConnectedFrom(aLeftNode=rgbaNode, aLeftNodeOutput=output)), nb)

        self.assertEqual(aGraph.getNodesConnectedFrom(aLeftNode=blendNode, aLeftNodeOutput=sbsenum.OutputEnum.OUTPUT), [])

        # Move the connections of an output pin to another
        aGraph.moveConnectionsOnPinOutput(aInitialNode=rgbaNode, aInitialNodeOutput='R', aTargetNode=rgbaNode, aTargetNodeOutput='G')

        self.assertEqual(len(aGraph.getConnectionsFromNode(aLeftNode=rgbaNode)), 4)
        nbConnections = {'R':0, 'G':3, 'B':0, 'A':1}
        for output,nb in list(nbConnections.items()):
            self.assertEqual(len(aGraph.getConnectionsFromNode(aLeftNode=rgbaNode, aLeftNodeOutput=output)), nb)

        self.assertEqual(len(aGraph.getNodesConnectedFrom(aLeftNode=rgbaNode)), 3)
        nbNodesConnected = {'R':0, 'G':2, 'B':0, 'A':1}
        for output,nb in list(nbNodesConnected.items()):
            self.assertEqual(len(aGraph.getNodesConnectedFrom(aLeftNode=rgbaNode, aLeftNodeOutput=output)), nb)

        # Check incompatible connections
        with self.assertRaises(SBSImpossibleActionError):       # invalid target output
            aGraph.moveConnectionsOnPinOutput(aInitialNode=rgbaNode, aInitialNodeOutput='G', aTargetNode=rgbaNode,aTargetNodeOutput='invalid')
        with self.assertRaises(SBSImpossibleActionError):       # invalid initial output
            aGraph.moveConnectionsOnPinOutput(aInitialNode=rgbaNode, aInitialNodeOutput='invalid', aTargetNode=rgbaNode,aTargetNodeOutput='B')
        with self.assertRaises(SBSImpossibleActionError):       # incompatible output types
            aGraph.moveConnectionsOnPinOutput(aInitialNode=rgbaNode, aInitialNodeOutput='G', aTargetNode=uniformNode)

        #################################
        # Check input connections getters
        self.assertEqual(len(aGraph.getNodesConnectedTo(aRightNode=blendNode)), 1)
        self.assertEqual(len(aGraph.getConnectionsToNode(aRightNode=blendNode)), 2)
        self.assertEqual(aGraph.getNodesConnectedTo(aRightNode=blendNode, aRightNodeInput=sbsenum.InputEnum.DESTINATION)[0], rgbaNode)

        # Move the connections of an input pin to another
        aGraph.moveConnectionOnPinInput(aInitialNode=blendNode, aInitialNodeInput=sbsenum.InputEnum.DESTINATION,
                                        aTargetNode=blendNode, aTargetNodeInput=sbsenum.InputEnum.SOURCE)

        self.assertEqual(len(aGraph.getNodesConnectedTo(aRightNode=blendNode)), 1)
        self.assertEqual(len(aGraph.getConnectionsToNode(aRightNode=blendNode)), 2)
        self.assertEqual(aGraph.getNodesConnectedTo(aRightNode=blendNode, aRightNodeInput=sbsenum.InputEnum.DESTINATION), [])
        self.assertEqual(aGraph.getNodesConnectedTo(aRightNode=blendNode, aRightNodeInput=sbsenum.InputEnum.SOURCE)[0], rgbaNode)

        # Check incompatible connections
        with self.assertRaises(SBSImpossibleActionError):   # initial connection not found
            aGraph.moveConnectionOnPinInput(aInitialNode=blendNode, aInitialNodeInput=sbsenum.InputEnum.DESTINATION,
                                            aTargetNode=blendNode, aTargetNodeInput=sbsenum.InputEnum.SOURCE)
        with self.assertRaises(SBSImpossibleActionError):   # incompatible types
            aGraph.moveConnectionOnPinInput(aInitialNode=blendNode, aInitialNodeInput=sbsenum.InputEnum.SOURCE,
                                            aTargetNode=grayscaleNode)

        self.assertEqual(len(aGraph.getNodesConnectedTo(aRightNode=blendNode)), 1)
        self.assertEqual(len(aGraph.getConnectionsToNode(aRightNode=blendNode)), 2)
        aGraph.moveConnectionOnPinInput(aInitialNode=blendNode, aInitialNodeInput=sbsenum.InputEnum.OPACITY,
                                        aTargetNode=embossNode, aTargetNodeInput=sbsenum.InputEnum.INPUT_GRADIENT)

        self.assertEqual(len(aGraph.getNodesConnectedTo(aRightNode=blendNode)), 1)
        self.assertEqual(len(aGraph.getConnectionsToNode(aRightNode=blendNode)), 1)


        # move connections on other node type
        aGraph.moveConnectionsOnPinOutput(aInitialNode=rgbaNode, aInitialNodeOutput='G', aTargetNode=rgbaNode2, aTargetNodeOutput='R')
        self.assertEqual(aGraph.getNodesConnectedTo(aRightNode=blendNode)[0], rgbaNode2)
        aGraph.moveConnectionsOnPinOutput(aInitialNode=inputNode, aInitialNodeOutput='output', aTargetNode=bitmap, aTargetNodeOutput='output')
        self.assertEqual(aGraph.getNodesConnectedTo(aRightNode=rgbaNode)[0], bitmap)

        sbsDoc.writeDoc()
        os.remove(sbsDoc.mFileAbsPath)


    def test_GetGroups(self):
        """
        This test checks sorting the nodes of a graph
        """
        log.info("Test Graph: GetGroups")
        sbsDoc = SBSGraphTests.openTestDocument('manyGroups.sbs')
        graph = sbsDoc.getSBSGraph('Graph')
        groups = graph.getAllInputGroups()
        self.assertEqual(len(groups), 11)

        sbsDoc = SBSGraphTests.openTestDocument('manyGroups.sbsar')
        graph = sbsDoc.getSBSGraph('ceramic_tiles_copper')
        groups = graph.getAllInputGroups()
        self.assertEqual(len(groups), 11)

    def test_v7ValueInputOutputs(self):
        """
        This if we can successfully parse and introspect input / values with a substance containing v7 engine nodes
        """
        log.info("Test Graph: value inputs/outputs")
        sbs = SBSGraphTests.openTestDocument('sample_value_node.sbs')

        for graph in sbs.getSBSGraphList():
            self.assertIsNotNone(graph.mIdentifier)

            for input in graph.getAllInputs():
                print('\t Input  [{: <15}] - {: <15}'.format(SBSGraphTests.__TYPE2LABEL.get(input.getType(), None), input.mIdentifier))
                self.assertIsNotNone(input.mIdentifier)
                self.assertIsNotNone(input.getType())

            for output in graph.getGraphOutputs():
                print('\t Output [{: <15}] - {: <15}'.format(SBSGraphTests.__TYPE2LABEL.get(output.getType(), None), output.mIdentifier))
                self.assertIsNotNone(output.mIdentifier)
                self.assertIsNotNone(output.getType())

    def test_variant(self):
        destPath = python_helpers.getAbsPathFromModule(testModule, './resources/ignore.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath, 'Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')
        uniformColor = aGraph.createCompFilterNode(
            aFilter=sbsenum.FilterEnum.UNIFORM,
            aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.COLOR,
                         sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [0, 0, 0, 1]},
        )
        uniformGrayscale = aGraph.createCompFilterNode(
            aFilter=sbsenum.FilterEnum.UNIFORM,
            aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
                         sbsenum.CompNodeParamEnum.OUTPUT_COLOR: 1},
        )
        blend = aGraph.createCompFilterNode(
            aFilter=sbsenum.FilterEnum.BLEND,
            aParameters={sbsenum.CompNodeParamEnum.BLENDING_MODE: sbsenum.BlendBlendingModeEnum.COPY,
                         sbsenum.CompNodeParamEnum.OPACITY: 1},
            aInheritance={sbsenum.CompNodeParamEnum.OUTPUT_SIZE: sbsenum.ParamInheritanceEnum.PARENT}
        )


        # Make sure the node get output type color if setting a color as input
        aGraph.connectNodes(aLeftNode=uniformColor, aRightNode=blend, aRightNodeInput=sbsenum.InputEnum.SOURCE)
        aGraph.connectNodes(aLeftNode=uniformColor, aRightNode=blend, aRightNodeInput=sbsenum.InputEnum.DESTINATION)
        self.assertEqual(blend.getCompOutput().mCompType, str(sbsenum.ParamTypeEnum.ENTRY_COLOR))

        # Make sure the node doesn't change type when the opacity is set to a grayscale
        aGraph.connectNodes(aLeftNode=uniformGrayscale, aRightNode=blend, aRightNodeInput=sbsenum.InputEnum.OPACITY)
        self.assertEqual(blend.getCompOutput().mCompType, str(sbsenum.ParamTypeEnum.ENTRY_COLOR))

        # Make sure the node changes type when connecting grayscale inputs
        aGraph.connectNodes(aLeftNode=uniformGrayscale, aRightNode=blend, aRightNodeInput=sbsenum.InputEnum.SOURCE)
        aGraph.connectNodes(aLeftNode=uniformGrayscale, aRightNode=blend, aRightNodeInput=sbsenum.InputEnum.DESTINATION)
        self.assertEqual(blend.getCompOutput().mCompType, str(sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE))

        # Test color mode constants
        color_mode_nodes = [aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.UNIFORM,
                                                        aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE:
                                                                         sbsenum.ColorModeEnum.GRAYSCALE}),
                            aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.DISTANCE,
                                                        aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE:
                                                                         sbsenum.ColorModeEnum.GRAYSCALE})
                            ]
        for node in color_mode_nodes:
            # Check that the constructor parameter changes the type
            self.assertEqual(node.getCompOutputType(), sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE)

            # Update color mode to color
            node.setParameterValue(aParameter=sbsenum.CompNodeParamEnum.COLOR_MODE,
                                   aParamValue=sbsenum.ColorModeEnum.COLOR)
            self.assertEqual(node.getCompOutputType(), sbsenum.ParamTypeEnum.ENTRY_COLOR)

            # Update color mode to grayscale
            node.setParameterValue(aParameter=sbsenum.CompNodeParamEnum.COLOR_MODE,
                                   aParamValue=sbsenum.ColorModeEnum.GRAYSCALE)
            self.assertEqual(node.getCompOutputType(), sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE)

            # Testing warning message when making color mode to dynamic parameter
            import pysbs.test.utilities as tu
            interceptor = tu.logging_messages_interceptor()
            logger = logging.getLogger('pysbs.compnode.compnode')
            logger.addHandler(interceptor)
            try:
                with interceptor:
                    node.setDynamicParameter(aParameter=sbsenum.CompNodeParamEnum.COLOR_MODE)
                    interceptor.assertEqualMessageCount(self, 1, 'No warning when setting COLOR_MODE to dynamic')
            finally:
                logger.removeHandler(interceptor)


    def test_UserData(self):
        """
        Test behavior to set / get userData / userTags of a compnode.
        """
        sbs = sbsgenerator.createSBSDocument(context.Context(), python_helpers.getAbsPathFromModule(testModule, './resources/userdata.sbs'))
        graph = sbs.createGraph('bar')
        graph2 = sbs.createGraph('foo')
        node = graph.createOutputNode('foo')
        node_i = graph.createInputNode('foo_i')
        node_ins = graph.createCompInstanceNodeFromPath(sbs, 'sbs://height_extrude.sbs')
        self.assertEqual(graph.setUserData(node, "foobar"), True)
        self.assertEqual(graph2.setUserData(node, "foobar"), False)
        self.assertEqual(graph.setUserData(node_i, "foobar"), True)
        self.assertEqual(graph.setUserData(node_ins, "foobar"), False)
        sbs.writeDoc()
        sbs = substance.SBSDocument(context.Context(), python_helpers.getAbsPathFromModule(testModule, './resources/userdata.sbs'))
        sbs.parseDoc()
        graph = sbs.getSBSGraph('bar')
        node = graph.getNode(node.mUID)
        node_i = graph.getNode(node.mUID)
        self.assertEqual(graph.getUserData(node),  "foobar")
        self.assertEqual(graph2.getUserData(node), None)
        self.assertEqual(graph.getUserData(node_i), "foobar")
        self.assertEqual(graph.getUserData(node_ins), None)
        os.remove(sbs.mFileAbsPath)


if __name__ == '__main__':
    unittest.main()
