# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import copy
import os
import sys

from pysbs.api_exceptions import SBSLibraryError, SBSImpossibleActionError
from pysbs import python_helpers
from pysbs import context
from pysbs import substance
from pysbs import sbsenum
from pysbs import graph
from pysbs import sbsgenerator
from pysbs import sbscommon
from pysbs import params

testModule = sys.modules[__name__]


class SBSFunctionTests(unittest.TestCase):
    @staticmethod
    def openTestDocument():
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/Functions.sbs')
        aContext = context.Context()
        sbsDoc = substance.SBSDocument(aContext, docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    def test_SortAsDAG(self):
        """
        This test checks sorting the nodes of a graph
        """
        log.info("Test Function: Sort as DAG")
        sbsDoc = SBSFunctionTests.openTestDocument()

        aFunction = sbsDoc.getSBSFunction('Function')
        unsortedNodes = copy.copy(aFunction.getDynamicValue().mParamNodes)
        sortedNodes = aFunction.sortNodesAsDAG()
        self.assertEqual(aFunction.getDynamicValue().mParamNodes, sortedNodes)

        refSortedIndices = [1, 8, 0, 3, 9, 2, 4, 5, 10, 11, 7, 6]
        for i, index in enumerate(refSortedIndices):
            self.assertEqual(sortedNodes[i], unsortedNodes[index])

        log.info("Test Function: Sort as DAG: OK")


    def test_InputParameters(self):
        """
        This test checks adding, getting and deleting input parameters on a function graph
        """
        log.info("Test Function: Input Parameters")
        sbsDoc = SBSFunctionTests.openTestDocument()

        aFunction = sbsDoc.getSBSFunction('Function')
        inputParams = aFunction.getInputParameters()
        self.assertEqual(len(inputParams), 1)

        # Check adding input parameters and their identifier
        param1 = aFunction.addInputParameter(aIdentifier='MyInput', aWidget=sbsenum.WidgetEnum.SLIDER_FLOAT1)
        param2 = aFunction.addInputParameter(aIdentifier='MyInput', aWidget=sbsenum.WidgetEnum.SLIDER_FLOAT2)
        param3 = aFunction.addInputParameter(aIdentifier='MyInput', aWidget=sbsenum.WidgetEnum.TEXT_STRING)
        self.assertIsInstance(param1, graph.SBSParamInput)
        self.assertIsInstance(param2, graph.SBSParamInput)
        self.assertEqual(param1.mIdentifier, 'MyInput')
        self.assertEqual(param2.mIdentifier, 'MyInput_1')
        self.assertEqual(param3.mIdentifier, 'MyInput_2')
        inputParams = aFunction.getInputParameters()
        self.assertEqual(len(inputParams), 4)

        # Check setting the order of the parameters
        aFunction.setInputParameterIndex(param1.mIdentifier, 2)
        self.assertEqual(aFunction.getInputParameters()[2].mIdentifier, param1.mIdentifier)
        self.assertEqual(aFunction.getInputParameterIndex(param1.mIdentifier), 2)

        aFunction.setInputParameterIndex(param1.mIdentifier, 0)
        self.assertEqual(aFunction.getInputParameters()[0].mIdentifier, param1.mIdentifier)
        self.assertEqual(aFunction.getInputParameterIndex(param1.mIdentifier), 0)

        aFunction.setInputParameterIndex(param1.mIdentifier, 1)
        self.assertEqual(aFunction.getInputParameters()[1].mIdentifier, param1.mIdentifier)
        self.assertEqual(aFunction.getInputParameterIndex(param1.mIdentifier), 1)

        with self.assertRaises(Exception):                  aFunction.setInputParameterIndex(param1.mIdentifier, 'bla')
        with self.assertRaises(SBSImpossibleActionError):   aFunction.setInputParameterIndex(param1.mIdentifier, -1)
        with self.assertRaises(SBSImpossibleActionError):   aFunction.setInputParameterIndex(param1.mIdentifier, 4)

        # Check removal of a parameter
        self.assertTrue(aFunction.deleteInputParameter(param2))
        with self.assertRaises(SBSImpossibleActionError):   aFunction.deleteInputParameter('Invalid')
        with self.assertRaises(SBSImpossibleActionError):   aFunction.deleteInputParameter(None)
        with self.assertRaises(SBSImpossibleActionError):   aFunction.deleteInputParameter(param2)

        log.info("Test Function: Input Parameters: OK")


    def test_ConnectDisconnect(self):
        """
        This test checks connecting and disconnecting nodes
        """
        log.info("Test Function: Connect / Disconnect Nodes")
        sbsDoc = SBSFunctionTests.openTestDocument()

        aFunction = sbsDoc.getSBSFunction('Function')
        gtNode = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.GREATER)[0]
        leftNode = gtNode.getConnections()[0].getConnectedNodeUID()

        self.assertTrue(gtNode.isConnectedTo(leftNode))

        # Check behavior with invalid cases:
        # - Invalid input
        with self.assertRaises(SBSImpossibleActionError):
            aFunction.connectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.CONDITION)
        with self.assertRaises(SBSLibraryError):
            aFunction.connectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= 1000)

        # - Two nodes of two different functions
        aFunction2 = sbsDoc.getSBSFunction('Function2')
        addNode = aFunction2.getAllFunctionsOfKind(sbsenum.FunctionEnum.ADD)[0]
        with self.assertRaises(SBSImpossibleActionError):
            aFunction2.connectNodes(aLeftNode=addNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.A)

        #  - Cycle creation in the graph
        ifelseNode = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.IF_ELSE)[0]
        with self.assertRaises(SBSImpossibleActionError):
            aFunction.connectNodes(aLeftNode=ifelseNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.A)

        subNode = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.SUB)[0]
        with self.assertRaises(SBSImpossibleActionError):
            aFunction.connectNodes(aLeftNode=ifelseNode, aRightNode=subNode, aRightNodeInput= sbsenum.FunctionInputEnum.A)


        # Check behavior with valid cases:
        aFunction.disconnectNodes(aLeftNode = leftNode, aRightNode = gtNode)
        self.assertFalse(gtNode.isConnectedTo(leftNode))

        aFunction.connectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.A)
        aFunction.connectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.B)
        self.assertTrue(gtNode.isConnectedTo(leftNode))

        aFunction.disconnectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.A)
        self.assertTrue(gtNode.isConnectedTo(leftNode))
        aFunction.disconnectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.B)
        self.assertFalse(gtNode.isConnectedTo(leftNode))

        aFunction.connectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.A)
        aFunction.connectNodes(aLeftNode=leftNode, aRightNode=gtNode, aRightNodeInput= sbsenum.FunctionInputEnum.B)
        aFunction.disconnectNodes(aLeftNode = leftNode, aRightNode = gtNode)
        self.assertFalse(gtNode.isConnectedTo(leftNode))

        # Check division and Log2 node polymorphic connect behavior
        aFunction3= sbsDoc.getSBSFunction('Function3')
        log2Node= aFunction3.getAllFunctionsOfKind(sbsenum.FunctionEnum.LOG2)[0]
        divNode= aFunction3.getAllFunctionsOfKind(sbsenum.FunctionEnum.DIV)[0]
        constants= [aFunction3.getAllFunctionsOfKind(sbsenum.FunctionEnum.CONST_FLOAT)[0],
                    aFunction3.getAllFunctionsOfKind(sbsenum.FunctionEnum.CONST_FLOAT2)[0],
                    aFunction3.getAllFunctionsOfKind(sbsenum.FunctionEnum.CONST_FLOAT3)[0],
                    aFunction3.getAllFunctionsOfKind(sbsenum.FunctionEnum.CONST_FLOAT4)[0]]

        for idx, c in enumerate(constants):
            # Test connecting constant to log2
            aFunction3.connectNodes(aLeftNode= c, aRightNode= log2Node, aRightNodeInput= sbsenum.FunctionInputEnum.A)
            self.assertTrue(log2Node.isConnectedTo(c))

            # Test connecting inputs of same size to division
            aFunction3.connectNodes(aLeftNode= c, aRightNode= divNode, aRightNodeInput= sbsenum.FunctionInputEnum.A)
            aFunction3.connectNodes(aLeftNode= c, aRightNode= divNode, aRightNodeInput= sbsenum.FunctionInputEnum.B)
            self.assertTrue(divNode.isConnectedTo(c))

        log.info("Test Function: Connect / Disconnect Nodes: OK\n")

    def test_DeleteNode(self):
        """
        This test checks deleting a node and its connections
        """
        log.info("Test Function: Delete node")
        sbsDoc = SBSFunctionTests.openTestDocument()

        aFunction = sbsDoc.getSBSFunction('Function')
        piNode = aFunction.getAllNodeInstancesOf(sbsDoc, 'sbs://functions.sbs/Functions/Math/Pi')[0]
        subNode = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.SUB)[0]
        mulNodes = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.MUL)
        mulNode = next(mulNode for mulNode in mulNodes if mulNode.isConnectedTo(piNode))
        constNodes = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.CONST_FLOAT)
        constNode = next(constNode for constNode in constNodes if mulNode.isConnectedTo(constNode))
        addNodes = aFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.ADD)
        addNode = next(addNode for addNode in addNodes if addNode.isConnectedTo(mulNode))

        self.assertTrue(mulNode.isConnectedTo(piNode))
        self.assertTrue(mulNode.isConnectedTo(constNode))
        self.assertTrue(subNode.isConnectedTo(mulNode))
        self.assertTrue(addNode.isConnectedTo(mulNode))

        conn = aFunction.getNodesConnectedTo(mulNode)
        self.assertEqual(len(conn), 2)
        self.assertEqual(conn, aFunction.getNodesConnectedTo(mulNode.mUID))
        self.assertEqual(len(aFunction.getNodesConnectedTo(constNode)), 0)

        # Delete Mul
        self.assertTrue(aFunction.deleteNode(mulNode))
        self.assertIsNone(aFunction.getNode(mulNode))
        self.assertIsNone(aFunction.getNode(mulNode.mUID))
        self.assertEqual(aFunction.getNodesConnectedTo(mulNode), [])
        self.assertFalse(subNode.isConnectedTo(mulNode))
        self.assertFalse(addNode.isConnectedTo(mulNode))
        self.assertEqual(len(subNode.mConnections), 1)
        self.assertEqual(len(addNode.mConnections), 1)

        log.info("Test Function: Delete node: OK")


    def test_GuiObjects(self):
        """
        This test checks the creation/edition/removal of GUI Objects.
        It also checks getting the nodes included in a frame
        """
        log.info("Test Function: GUI Objects operation")

        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/testGUIObjects.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath)
        aFunction = sbsDoc.createFunction('Function')
        aOutputNode = aFunction.createFunctionNode(aFunction=sbsenum.FunctionEnum.SEQUENCE, aGUIPos=[720,368,0])

        # Check creation of GUIObjects
        grComment = aFunction.createComment(aCommentText='<Output>', aGUIPos=[-48,-100,-100], aLinkToNode=aOutputNode)
        grFrame = aFunction.createFrame(aFrameTitle='<Input>', aCommentText='<nodescription>', aGUIPos=[-512, -192, 0],
                                         aSize=[437,405], aColor=[0, 0.5, 0.03, 0.46])
        grPin = aFunction.createNavigationPin(aPinText=u'<éà>&i', aGUIPos=[16,-116,0])
        self.assertTrue(grComment.isAComment())
        self.assertTrue(grFrame.isAFrame())
        self.assertTrue(grPin.isANavigationPin())
        self.assertEqual(aFunction.getNodeAssociatedToComment(aComment=grComment), aOutputNode)
        self.assertEqual(aFunction.getCommentsAssociatedToNode(aOutputNode)[0], grComment)

        self.assertTrue(sbsDoc.writeDoc())

        # Check getting GUIObjects
        refDoc = SBSFunctionTests.openTestDocument()
        refFunction = refDoc.getSBSFunction('Function')
        aGUIObjects = refFunction.getAllGUIObjects()
        refComments = refFunction.getAllComments()
        refFrames = refFunction.getAllFrames()
        refPins = refFunction.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 4)
        self.assertEqual(len(refComments), 1)
        self.assertEqual(len(refFrames), 2)
        self.assertEqual(len(refPins), 1)

        # Compare created GUIObject with their reference in AllNodes graph
        resDoc = substance.SBSDocument(aContext=context.Context(), aFileAbsPath=docAbsPath)
        self.assertTrue(resDoc.parseDoc())
        resFunction = resDoc.getSBSFunction('Function')
        aGUIObjects = resFunction.getAllGUIObjects()
        resComments = resFunction.getAllComments()
        resFrames = resFunction.getAllFrames()
        resPins = resFunction.getAllNavigationPins()
        self.assertEqual(len(aGUIObjects), 3)
        self.assertEqual(len(resComments), 1)
        self.assertEqual(len(resFrames), 1)
        self.assertEqual(len(resPins), 1)

        self.assertTrue(resFrames[0].equals(refFrames[0]))
        self.assertTrue(resComments[0].equals(refComments[0]))
        self.assertTrue(resPins[0].equals(refPins[0]))

        # Check getting nodes in the ROI of a frame
        refFrame = refFrames[0]
        self.assertIsNotNone(refFrame)
        inFrameNodes = refFunction.getNodesInFrame(refFrame)
        self.assertEqual(len(inFrameNodes), 3)
        aNode = refFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.GET_FLOAT1)[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = refFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.CONST_FLOAT)[0]
        self.assertTrue(aNode in inFrameNodes)
        aNode = refFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.MUL)[0]
        self.assertTrue(aNode in inFrameNodes)

        aOutputs = [refFunction.getOutputNode(), refFunction.getAllFunctionsOfKind(sbsenum.FunctionEnum.GREATER)[0]]

        aOutputFrame = refFunction.createFrameAroundNodes(aNodeList = aOutputs, aFrameTitle='The outputs', aColor=[0, 0.75, 0.75, 0.19])
        refOutputFrame = next((aFrame for aFrame in refFrames if aFrame.mTitle == 'The outputs'), None)
        self.assertTrue(aOutputFrame.equals(refOutputFrame))
        self.assertTrue(aOutputFrame.mGUILayout.equals(refOutputFrame.mGUILayout))


        self.assertIsInstance(refFunction.getRect(), sbscommon.Rect)

        os.remove(docAbsPath)
        log.info("Test Function: GUI Objects: OK\n")


    def test_MoveConnections(self):
        """
        This test checks the facilities to get and modify existing connections
        """
        destPath = python_helpers.getAbsPathFromModule(testModule, './resources/testMoveConnectionsFct.sbs')

        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), destPath)
        aFunction = sbsDoc.createFunction('Function')

        # Start from connections with node mul, and replace by pow:
        # float1-----A mul------- A add     =>      float1-----n pow------- A add
        # float2-----B       |--- B         =>      float2-----x       |--- B
        powNode    = aFunction.createFunctionInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='sbs://functions.sbs/Functions/Math/Pow')
        crossNode  = aFunction.createFunctionInstanceNodeFromPath(aSBSDocument=sbsDoc, aPath='sbs://functions.sbs/Functions/Math/cross_product')
        mulNode    = aFunction.createFunctionNode(aFunction=sbsenum.FunctionEnum.MUL)
        addNode    = aFunction.createFunctionNode(aFunction=sbsenum.FunctionEnum.ADD)
        floatNode1 = aFunction.createFunctionNode(aFunction=sbsenum.FunctionEnum.CONST_FLOAT)
        floatNode2 = aFunction.createFunctionNode(aFunction=sbsenum.FunctionEnum.CONST_FLOAT)
        float3Node = aFunction.createFunctionNode(aFunction=sbsenum.FunctionEnum.CONST_FLOAT3)

        self.assertIsInstance(powNode, params.SBSParamNode)
        self.assertIsInstance(mulNode, params.SBSParamNode)
        self.assertIsInstance(floatNode1, params.SBSParamNode)
        self.assertIsInstance(floatNode2, params.SBSParamNode)
        self.assertIsInstance(float3Node, params.SBSParamNode)
        self.assertIsInstance(crossNode, params.SBSParamNode)

        self.assertIsInstance(aFunction.connectNodes(aLeftNode=floatNode1, aRightNode=mulNode, aRightNodeInput=sbsenum.FunctionInputEnum.A),
                              sbscommon.SBSConnection)
        self.assertIsInstance(aFunction.connectNodes(aLeftNode=floatNode2, aRightNode=mulNode, aRightNodeInput=sbsenum.FunctionInputEnum.B),
                              sbscommon.SBSConnection)
        self.assertIsInstance(aFunction.connectNodes(aLeftNode=mulNode, aRightNode=addNode, aRightNodeInput=sbsenum.FunctionInputEnum.A),
                              sbscommon.SBSConnection)
        self.assertIsInstance(aFunction.connectNodes(aLeftNode=mulNode, aRightNode=addNode, aRightNodeInput=sbsenum.FunctionInputEnum.B),
                              sbscommon.SBSConnection)
        self.assertTrue(mulNode.isConnectedTo(floatNode1))
        self.assertTrue(mulNode.isConnectedTo(floatNode2))
        self.assertTrue(addNode.isConnectedTo(mulNode))

        ######################
        # Check output connections getters
        self.assertEqual(len(aFunction.getConnectionsFromNode(aLeftNode=mulNode)), 2)
        self.assertEqual(len(aFunction.getNodesConnectedFrom(aLeftNode=mulNode)), 1)
        self.assertEqual(len(aFunction.getConnectionsFromNode(aLeftNode=powNode)), 0)

        # Move the connections of an output pin to another
        aFunction.moveConnectionsOnPinOutput(aInitialNode=mulNode, aTargetNode=powNode)

        self.assertEqual(len(aFunction.getConnectionsFromNode(aLeftNode=mulNode)), 0)
        self.assertEqual(len(aFunction.getNodesConnectedFrom(aLeftNode=mulNode)),  0)
        self.assertEqual(len(aFunction.getConnectionsFromNode(aLeftNode=powNode)), 2)
        self.assertEqual(len(aFunction.getNodesConnectedFrom(aLeftNode=powNode)),  1)

        # Check incompatible connections
        with self.assertRaises(SBSImpossibleActionError):       # no more connections
            aFunction.moveConnectionsOnPinOutput(aInitialNode=mulNode, aTargetNode=powNode)
        with self.assertRaises(SBSImpossibleActionError):       # incompatible output types
            aFunction.moveConnectionsOnPinOutput(aInitialNode=powNode, aTargetNode=float3Node)

        #################################
        # Check input connections getters
        self.assertEqual(len(aFunction.getNodesConnectedTo(aRightNode=mulNode)), 2)
        self.assertEqual(len(aFunction.getConnectionsToNode(aRightNode=mulNode)), 2)
        self.assertEqual(aFunction.getNodesConnectedTo(aRightNode=mulNode, aRightNodeInput='a')[0], floatNode1)
        self.assertEqual(aFunction.getNodesConnectedTo(aRightNode=mulNode, aRightNodeInput='b')[0], floatNode2)

        # Move the connections of an input pin to another
        aFunction.moveConnectionOnPinInput(aInitialNode=mulNode, aTargetNode=powNode, aTargetNodeInput='n')
        sbsDoc.writeDoc()

        self.assertEqual(len(aFunction.getNodesConnectedTo(aRightNode=mulNode)), 1)
        self.assertEqual(len(aFunction.getConnectionsToNode(aRightNode=mulNode)), 1)
        self.assertEqual(len(aFunction.getNodesConnectedTo(aRightNode=powNode)), 1)
        self.assertEqual(len(aFunction.getConnectionsToNode(aRightNode=powNode)), 1)
        self.assertEqual(aFunction.getNodesConnectedTo(aRightNode=powNode, aRightNodeInput='n')[0], floatNode1)
        self.assertEqual(aFunction.getNodesConnectedTo(aRightNode=mulNode, aRightNodeInput=sbsenum.FunctionInputEnum.A),    [])
        self.assertEqual(aFunction.getNodesConnectedTo(aRightNode=mulNode, aRightNodeInput=sbsenum.FunctionInputEnum.B)[0], floatNode2)

        aFunction.moveConnectionOnPinInput(aInitialNode=mulNode, aInitialNodeInput=sbsenum.FunctionInputEnum.B,
                                        aTargetNode=powNode, aTargetNodeInput='x')
        self.assertEqual(len(aFunction.getNodesConnectedTo(aRightNode=mulNode)), 0)
        self.assertEqual(len(aFunction.getNodesConnectedTo(aRightNode=powNode)), 2)
        self.assertEqual(len(aFunction.getConnectionsToNode(aRightNode=powNode)), 2)

        # Check incompatible connections
        with self.assertRaises(SBSImpossibleActionError):   # initial connection not found
            aFunction.moveConnectionOnPinInput(aInitialNode=mulNode, aTargetNode=powNode)
        with self.assertRaises(SBSImpossibleActionError):   # incompatible types
            aFunction.moveConnectionOnPinInput(aInitialNode=powNode, aInitialNodeInput=sbsenum.FunctionInputEnum.B,
                                                aTargetNode=crossNode)

        self.assertEqual(len(aFunction.getNodesConnectedTo(aRightNode=powNode)), 2)
        self.assertEqual(len(aFunction.getConnectionsToNode(aRightNode=powNode)), 2)

        sbsDoc.writeDoc()
        os.remove(sbsDoc.mFileAbsPath)

if __name__ == '__main__':
    unittest.main()
