# -*- coding: utf-8 -*-
import unittest
import logging
log = logging.getLogger(__name__)
import os
import sys
import tempfile

from pysbs.api_exceptions import SBSLibraryError, SBSImpossibleActionError
from pysbs import python_helpers
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import context
from pysbs import substance
from pysbs import params
from pysbs import compnode
from pysbs import sbsgenerator


testModule = sys.modules[__name__]


class SBSCompNodeTests(unittest.TestCase):

    @staticmethod
    def openTestDocument():
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/AllNodes.sbs')
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    def test_Parameters(self):
        """
        This test checks getting and setting Parameters on CompNodes
        """
        log.info("Test CompNodes: Parameters")
        sbsDoc = SBSCompNodeTests.openTestDocument()
        allNodeGraph = sbsDoc.getSBSGraph(u'AllNodes')

        # Case of a filter
        # Check getter
        uniform = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.UNIFORM)[0]
        colorValue = uniform.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR)
        self.assertIsInstance(colorValue, str)
        colors = colorValue.split()
        self.assertEqual(len(colors), 4)
        self.assertEqual(colorValue, uniform.getParameterValue(sbslibrary.getCompNodeParam(sbsenum.CompNodeParamEnum.OUTPUT_COLOR)))

        # Check setter with correct values
        colorValue = '0.2 0.3 1 0'
        uniform.setParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR, colorValue)
        self.assertEqual(colorValue, uniform.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR))
        uniform.setParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR, u'[0.2,0.3,1,0]')
        self.assertEqual(colorValue, uniform.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR))
        uniform.setParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR, [0.2,0.3,1,0])
        self.assertEqual(colorValue, uniform.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR))
        self.assertTrue(uniform.unsetParameter(sbsenum.CompNodeParamEnum.OUTPUT_COLOR))
        self.assertEqual('0.0 0.0 0.0 1.0', uniform.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_COLOR))

        # Check setter with incorrect values
        self.assertIsNone(uniform.getParameterValue('InvalidValue'))
        with self.assertRaises(SBSLibraryError): uniform.getParameterValue(1000)
        with self.assertRaises(SBSLibraryError): uniform.unsetParameter(1000)

        # Check setting base parameter
        uniform.setParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE, '1 1', sbsenum.ParamInheritanceEnum.ABSOLUTE)
        self.assertEqual(uniform.mCompImplementation.mCompFilter.mParameters[0].mRelativeTo, str(sbsenum.ParamInheritanceEnum.ABSOLUTE))
        uniform.setParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE, '1 1', sbsenum.ParamInheritanceEnum.INPUT)
        self.assertEqual(uniform.mCompImplementation.mCompFilter.mParameters[0].mRelativeTo, str(sbsenum.ParamInheritanceEnum.PARENT))
        uniform.setParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE, '1 1', sbsenum.ParamInheritanceEnum.PARENT)
        self.assertEqual(uniform.mCompImplementation.mCompFilter.mParameters[0].mRelativeTo, str(sbsenum.ParamInheritanceEnum.PARENT))

        self.assertEqual(uniform.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE), '1 1')
        uniform.setParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE, 0, sbsenum.ParamInheritanceEnum.ABSOLUTE)
        self.assertEqual(uniform.mCompImplementation.mCompFilter.mParameters[0].mRelativeTo, str(sbsenum.ParamInheritanceEnum.ABSOLUTE))
        self.assertEqual(uniform.getParameterValue(sbsenum.CompNodeParamEnum.OUTPUT_SIZE), '0 0')

        # Case of an instance
        # Check getter
        curvNode = allNodeGraph.getAllNodeInstancesOf(sbsDoc, 'sbs://curvature.sbs')[0]
        self.assertEqual('1', curvNode.getParameterValue('intensity'))
        curvNode.setParameterValue('intensity', 2.5)
        self.assertEqual('2.5', curvNode.getParameterValue('intensity'))

        # Check setter with correct values
        aDynValue = curvNode.setDynamicParameter('intensity')
        self.assertIsInstance(curvNode.getParameterValue('intensity'), params.SBSDynamicValue)

        # Check dynamic value definition
        allNodeGraph.addInputParameter(aIdentifier = 'InputParam', aWidget = sbsenum.WidgetEnum.SLIDER_FLOAT1)
        aDynValue.setToInputParam(aParentGraph = allNodeGraph, aInputParamIdentifier = 'InputParam')
        getFloatNodes = aDynValue.getAllFunctionsOfKind(sbsenum.FunctionEnum.GET_FLOAT1)
        self.assertEqual(len(getFloatNodes), 1)
        self.assertEqual(aDynValue.getOutputNode(), getFloatNodes[0])

        self.assertTrue(curvNode.unsetParameter('intensity'))
        self.assertEqual('1', curvNode.getParameterValue('intensity'))

        # Check creation of instance with params
        aInstance = allNodeGraph.createCompInstanceNodeFromPath(sbsDoc, aPath='sbs://multi_material_blend.sbs',
                                                            aParameters={'diffuse': False, u'ambient_occlusion': True})
        self.assertTrue(aInstance.isAnInstance())
        self.assertEqual(aInstance.getParameterValue('diffuse'), '0')
        self.assertEqual(aInstance.getParameterValue('ambient_occlusion'), '1')
        with self.assertRaises(SBSLibraryError):
            allNodeGraph.createCompInstanceNodeFromPath(sbsDoc, aPath='sbs://multi_material_blend.sbs',
                                                                aParameters={'diffuse': False, 'invalid': False})
        with self.assertRaises(SBSLibraryError):
            allNodeGraph.createCompInstanceNodeFromPath(sbsDoc, aPath='sbs://multi_material_blend.sbs',
                                                                aParameters={u'diffuse': False, u'àéù': False})

        log.info("Test CompNodes: Parameters: OK\n")


    def test_FxMapGraph(self):
        """
        This test checks creation and remove of FxMap nodes
        """
        log.info("Test CompNodes: FxMap Graph")
        sbsDoc = SBSCompNodeTests.openTestDocument()
        allNodeGraph = sbsDoc.getSBSGraph('AllNodes')
        fxMapNode = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.FXMAPS)[0]
        self.assertTrue(fxMapNode.isAFxMap())

        fxMapGraph = fxMapNode.getFxMapGraph()
        self.assertIsInstance(fxMapGraph, compnode.SBSParamsGraph)
        quadrantNode1 = fxMapGraph.getAllNodesOfKind(sbsenum.FxMapNodeEnum.QUADRANT)[0]
        quadrantNode2 = fxMapGraph.duplicateNode(quadrantNode1)
        self.assertTrue(fxMapGraph.connectNodes(aTopNode = quadrantNode1, aBottomNode = quadrantNode2))
        self.assertEqual(len(quadrantNode1.getConnections()), 4)

        quadrantNode3 = fxMapGraph.duplicateNode(quadrantNode2)
        self.assertTrue(fxMapGraph.connectNodes(aTopNode = quadrantNode2, aBottomNode = quadrantNode3))
        self.assertEqual(len(quadrantNode2.getConnections()), 4)

        self.assertEqual(len(fxMapGraph.getAllNodesOfKind(sbsenum.FxMapNodeEnum.QUADRANT)), 3)
        fxMapGraph.deleteNode(quadrantNode2)
        self.assertEqual(len(fxMapGraph.getAllNodesOfKind(sbsenum.FxMapNodeEnum.QUADRANT)), 2)

        self.assertEqual(len(quadrantNode1.getConnections()), 0)
        self.assertEqual(len(quadrantNode3.getConnections()), 0)
        self.assertIsNone(fxMapGraph.getNode(quadrantNode2.mUID))

        log.info("Test CompNodes: FxMap Graph: OK")

    def test_FxMapGraph_ConnectDisconnect(self):
        """
        This test checks connecting and disconnecting nodes of an FxMap graph
        """
        log.info("Test CompNodes: Connect / Disconnect Nodes")
        sbsDoc = SBSCompNodeTests.openTestDocument()
        aGraph = sbsDoc.getSBSGraph('AllNodes')
        fxMapNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.FXMAPS)[0]
        fxMapGraph = fxMapNode.getFxMapGraph()
        quadrantNode1 = fxMapGraph.getAllNodesOfKind(sbsenum.FxMapNodeEnum.QUADRANT)[0]
        quadrantNode2 = fxMapGraph.duplicateNode(quadrantNode1)
        self.assertTrue(fxMapGraph.connectNodes(aTopNode = quadrantNode1, aBottomNode = quadrantNode2))
        self.assertTrue(quadrantNode1.isConnectedTo(quadrantNode2))
        self.assertFalse(quadrantNode2.isConnectedTo(quadrantNode1))

        # Check behavior with invalid cases:
        # - Invalid output
        with self.assertRaises(SBSImpossibleActionError):
           fxMapGraph.connectNodes(aTopNode = quadrantNode1, aBottomNode = quadrantNode2, aTopNodeOutput=sbsenum.OutputEnum.OUTPUT)
        with self.assertRaises(SBSLibraryError):
           fxMapGraph.connectNodes(aTopNode = quadrantNode1, aBottomNode = quadrantNode2, aTopNodeOutput=1000)

        # - Two nodes of two different graphs
        fxMapNode2 = aGraph.duplicateNode(fxMapNode)
        fxMapGraph2 = fxMapNode2.getFxMapGraph()
        quadrantNode3 = fxMapGraph2.getAllNodesOfKind(sbsenum.FxMapNodeEnum.QUADRANT)[0]
        with self.assertRaises(SBSImpossibleActionError):
            fxMapGraph2.connectNodes(aTopNode=quadrantNode3, aBottomNode=quadrantNode2)

        #  - Cycle creation in the graph
        with self.assertRaises(SBSImpossibleActionError):
            self.assertTrue(fxMapGraph.connectNodes(aTopNode = quadrantNode2, aBottomNode = quadrantNode1))

        # Check behavior with valid cases:
        fxMapGraph.disconnectNodes(aTopNode=quadrantNode1, aBottomNode=quadrantNode2, aTopNodeOutput=sbsenum.OutputEnum.OUTPUT0)
        self.assertTrue(quadrantNode1.isConnectedTo(quadrantNode2))
        fxMapGraph.disconnectNodes(aTopNode=quadrantNode1, aBottomNode=quadrantNode2)
        self.assertFalse(quadrantNode1.isConnectedTo(quadrantNode2))

        self.assertTrue(fxMapGraph.connectNodes(aTopNode = quadrantNode1, aBottomNode = quadrantNode2, aTopNodeOutput=sbsenum.OutputEnum.OUTPUT1))
        self.assertTrue(quadrantNode1.isConnectedTo(quadrantNode2))


        log.info("Test CompNodes: Connect / Disconnect Nodes: OK\n")


    def test_FxMapGraph_GuiObjects(self):
        """
        This test checks the creation/edition/removal of GUI Objects in a FxMap graph.
        It also checks getting the nodes included in a frame
        """
        log.info("Test Graph: GUI Objects operation")
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testGUIObjects.sbs')

        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath, 'Graph')
        aGraph = sbsDoc.getSBSGraph('Graph')
        aFxMap = aGraph.createCompFilterNode(aFilter= sbsenum.FilterEnum.FXMAPS)
        aFxMapGraph = aFxMap.getFxMapGraph()

        # Check creation of GUIObjects
        grComment = aFxMapGraph.createComment(aCommentText = 'not used', aGUIPos = [288,32,-100])
        grFrame   = aFxMapGraph.createFrame(aFrameTitle='<Input>', aCommentText='<nodescription>', aGUIPos=[-144,-96,-100], aSize=[298,160], aColor=[0.9, 0.9, 0, 0.26])
        grPin     = aFxMapGraph.createNavigationPin(aPinText=u'<é@&>!', aGUIPos=[166,118,0])
        self.assertTrue(grComment.isAComment())
        self.assertTrue(grFrame.isAFrame())
        self.assertTrue(grPin.isANavigationPin())

        self.assertTrue(sbsDoc.writeDoc())

        # Check getting GUIObjects
        refDoc = SBSCompNodeTests.openTestDocument()
        allNodeGraph = refDoc.getSBSGraph('AllNodes')
        refFxMapGraph = allNodeGraph.getAllFiltersOfKind(sbsenum.FilterEnum.FXMAPS)[0].getFxMapGraph()
        aGUIObjects = refFxMapGraph.getAllGUIObjects()
        refComments = refFxMapGraph.getAllComments()
        refFrames = refFxMapGraph.getAllFrames()
        refPins = refFxMapGraph.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 4)
        self.assertEqual(len(refComments), 1)
        self.assertEqual(len(refFrames), 2)
        self.assertEqual(len(refPins), 1)

        # Compare created GUIObject with their reference in AllNodes graph
        resDoc = substance.SBSDocument(aContext=context.Context(), aFileAbsPath=docAbsPath)
        self.assertTrue(resDoc.parseDoc())
        resGraph = resDoc.getSBSGraph('Graph')
        resFxMapGraph = resGraph.getAllFiltersOfKind(sbsenum.FilterEnum.FXMAPS)[0].getFxMapGraph()
        aGUIObjects = resFxMapGraph.getAllGUIObjects()
        resComments = resFxMapGraph.getAllComments()
        resFrames = resFxMapGraph.getAllFrames()
        resPins = resFxMapGraph.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 3)
        self.assertEqual(len(resComments), 1)
        self.assertEqual(len(resFrames), 1)
        self.assertEqual(len(resPins), 1)

        self.assertTrue(resFrames[0].equals(refFrames[0]))
        self.assertTrue(resComments[0].equals(refComments[0]))
        self.assertTrue(resPins[0].equals(refPins[0]))

        # Check getting nodes in the ROI of a frame
        refFrame = refFrames[0]
        inFrameNodes = refFxMapGraph.getNodesInFrame(refFrame)
        self.assertEqual(len(inFrameNodes), 1)
        aNode = refFxMapGraph.getAllNodesOfKind(sbsenum.FxMapNodeEnum.QUADRANT)[0]
        self.assertTrue(aNode in inFrameNodes)

        aOutputs = [refFxMapGraph.getAllNodesOfKind(sbsenum.FxMapNodeEnum.ITERATE)[0],
                    refFxMapGraph.getAllNodesOfKind(sbsenum.FxMapNodeEnum.SWITCH)[0]]
        aOutputFrame = refFxMapGraph.createFrameAroundNodes(aNodeList = aOutputs, aDisplayTitle=False, aColor=[1, 0, 0, 0.4])
        refOutputFrame = refFrames[1]
        self.assertTrue(aOutputFrame.equals(refOutputFrame))
        self.assertTrue(aOutputFrame.mGUILayout.equals(refOutputFrame.mGUILayout))

        # Check deleting GUIObjects
        aFxMapGraph.deleteComment(grComment)
        aFxMapGraph.deleteFrame(grFrame)
        aFxMapGraph.deleteNavigationPin(grPin)
        self.assertEqual(len(aFxMapGraph.getAllGUIObjects()), 0)
        self.assertEqual(len(aFxMapGraph.getAllComments()), 0)
        self.assertEqual(len(aFxMapGraph.getAllFrames()), 0)
        self.assertEqual(len(aFxMapGraph.getAllNavigationPins()), 0)

        os.remove(docAbsPath)
        log.info("Test FxMapGraph: GUI Objects: OK\n")


    def test_NodePosition(self):
        """
        This test checks the GUI position accessors
        """
        log.info("Test CompNodes: Nodes position")
        sbsDoc = SBSCompNodeTests.openTestDocument()
        aGraph = sbsDoc.getSBSGraph('AllNodes')
        bitmapNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BITMAP)[0]
        aPos = [-624, -336, 0]
        self.assertEqual(bitmapNode.getPosition(), aPos)
        bitmapNode.setPosition(aPos)
        self.assertEqual(bitmapNode.getPosition(), aPos)
        bitmapNode.setPosition('-624.0 -336 0')
        self.assertEqual(bitmapNode.getPosition(), aPos)

        with self.assertRaises(ValueError): bitmapNode.setPosition('invalid')


    def test_CreateInputValue(self):
        """
        Create SBSCompInputValue
        """
        # create
        doc = sbsgenerator.createSBSDocument(context.Context(), os.path.join(tempfile.gettempdir(), "inputvalue.sbs"))
        graph = doc.createGraph()
        val_node = graph.createCompInstanceNodeFromPath(doc, "sbs://pbr_base_material.sbs")
        val_node.createInputValue("kikoo", sbsenum.ParamTypeEnum.FLOAT1)
        val_node.createInputValue("#kikoo", sbsenum.InputValueTypeEnum.FLOAT1)
        val_node.createInputValue("kikoo", sbsenum.InputValueTypeEnum.FLOAT1)
        val_node.createInputValue("#kikoo", sbsenum.InputValueTypeEnum.FLOAT1)
        doc.writeDoc()
        # read back
        doc = substance.SBSDocument(context.Context(), os.path.join(tempfile.gettempdir(), "inputvalue.sbs"))
        doc.parseDoc()
        graph = doc.getSBSGraphList()[0]
        node = graph.getAllNodes()[0]
        self.assertEqual(len(node.mInputValues), 4)
        # get only one, with and without #
        self.assertEqual(node.getInputValue("kikoo").mIdentifier, "#kikoo")
        self.assertEqual(node.getInputValue("#kikoo").mIdentifier, "#kikoo")
        self.assertEqual(node.getInputValue("#kikoo_1").mIdentifier, "#kikoo_1")
        self.assertEqual(node.getInputValue("kikoo_2").mIdentifier, "#kikoo_2")



if __name__ == '__main__':
    unittest.main()
