# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import copy
import sys

from pysbs import python_helpers
from pysbs import sbsenum
from pysbs import sbsgenerator
from pysbs import context

testModule = sys.modules[__name__]

class SBSCommonTests(unittest.TestCase):

    def test_sortDAG(self):
        """
        This test checks the correct sorting of a node list as a DAG
        """
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/myDoc.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(context.Context(), docAbsPath, 'MyGraph')
        aGraph = sbsDoc.getSBSGraph('MyGraph')
        node0 = aGraph.createInputNode('MyInput', sbsenum.ColorModeEnum.GRAYSCALE)
        node1 = aGraph.createOutputNode('AnOutput')
        node2 = aGraph.createCompFilterNode(sbsenum.FilterEnum.TRANSFORMATION)
        node3 = aGraph.createInputNode('AnInput', sbsenum.ColorModeEnum.GRAYSCALE)
        node4 = aGraph.createCompFilterNode(sbsenum.FilterEnum.BLEND)
        node5 = aGraph.createOutputNode('MyOutput')
        node6 = aGraph.createGradientMapNode()
        node7 = aGraph.createBitmapNode(sbsDoc, sbsDoc.buildAbsPathFromRelToMePath('SD_Icon.png'))
        node8 = aGraph.createCompInstanceNodeFromPath(sbsDoc, sbsDoc.buildAbsPathFromRelToMePath('auto_levels.sbs'))

        # Check simple classification first, as nodes are not connected yet
        connections = aGraph.mNodeList.computeConnectionsInsidePattern(aGraph.mCompNodes)
        self.assertEqual(connections, [([],[]) for _ in range(0, len(aGraph.mCompNodes))])
        sortedIndices = aGraph.mNodeList.computeSortedIndicesOfDAG(aGraph.mCompNodes, connections)
        self.assertEqual(sortedIndices, [7, 4, 6, 2, 8, 3, 0, 1, 5])

        # Keep a copy of not connected nodes:
        rawNodes = copy.copy(aGraph.mCompNodes)

        # Connect nodes
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node3, aRightNode = node8))  #Input1 -> Levels
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node8, aRightNode = node5))  #Levels -> Output2
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node0, aRightNode = node6))  #Input2 -> Gradient
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node6, aRightNode = node4, aRightNodeInput = sbsenum.InputEnum.SOURCE))  #Gradient -> Blend
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node7, aRightNode = node2))  #Bitmap -> Transform
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node2, aRightNode = node4, aRightNodeInput = sbsenum.InputEnum.DESTINATION))  #Transform -> Blend
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node4, aRightNode = node1))  #Blend -> Output1
        connections = aGraph.mNodeList.computeConnectionsInsidePattern(aGraph.mCompNodes)

        nbConnections = [(0,1),(1,0),(1,1),(0,1),(2,1),(1,0),(1,1),(0,1),(1,1)]
        for conn, nbConn in zip(connections, nbConnections):
            self.assertEqual(len(conn[0]), nbConn[0])
            self.assertEqual(len(conn[1]), nbConn[1])

        sortedIndices = aGraph.mNodeList.computeSortedIndicesOfDAG(aGraph.mCompNodes, connections)
        self.assertEqual(sortedIndices, [7, 3, 0, 2, 8, 6, 5, 4, 1])

        # Add a second gradient node and connect it between Input1 and Levels
        node9 = aGraph.createGradientMapNode(aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE:sbsenum.ColorModeEnum.GRAYSCALE})
        rawNodes.append(node9)
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node3, aRightNode = node9))  #Input1 -> Gradient2
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node9, aRightNode = node8))  #Gradient2 -> Levels
        connections = aGraph.mNodeList.computeConnectionsInsidePattern(aGraph.mCompNodes)
        sortedIndices = aGraph.mNodeList.computeSortedIndicesOfDAG(aGraph.mCompNodes, connections)
        self.assertEqual(sortedIndices, [7, 3, 0, 2, 9, 6, 8, 4, 5, 1])

        # Now connect Input2 to the second gradient node and reconnect Input1 to Levels
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node3, aRightNode = node8))  #Input1 -> Levels
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node0, aRightNode = node9))  #Input2 -> Gradient2
        self.assertIsNotNone(aGraph.connectNodes(aLeftNode = node9, aRightNode = node4, aRightNodeInput = sbsenum.InputEnum.OPACITY))  #Gradient2 -> Blend
        connections = aGraph.mNodeList.computeConnectionsInsidePattern(aGraph.mCompNodes)
        sortedIndices = aGraph.mNodeList.computeSortedIndicesOfDAG(aGraph.mCompNodes, connections)
        self.assertEqual(sortedIndices, [7, 3, 0, 2, 8, 6, 9, 5, 4, 1])


if __name__ == '__main__':
    log.info("Test SBSCommon")
    unittest.main()