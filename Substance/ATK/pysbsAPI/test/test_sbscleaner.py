# coding: utf-8
import unittest
import sys

from pysbs import python_helpers
from pysbs import sbscleaner
from pysbs import context
from pysbs import substance
from pysbs import sbsenum

testModule = sys.modules[__name__]

class SBSCleanerTests(unittest.TestCase):

    @staticmethod
    def openTestDocument(aFileName):
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/' + aFileName)
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    def test_CleanGraphNodes(self):
        """
        This test checks the cleaning of useless compositing graph nodes
        """
        sbsDoc = SBSCleanerTests.openTestDocument('AllNodes.sbs')
        aGraph = sbsDoc.getSBSGraph('AllNodes')
        aNodes = sbscleaner.getUselessNodesInGraph(aGraph)
        self.assertEqual(aNodes, set([]))

        aBlurNode = aGraph.getAllFiltersOfKind(sbsenum.FilterEnum.BLUR)[0]
        aLeftNode = aGraph.getNodesConnectedTo(aBlurNode)[0]
        aGraph.disconnectNodes(aLeftNode=aLeftNode, aRightNode=aBlurNode)

        self.assertEqual(aBlurNode.getConnections(), [])

        aNodes = sbscleaner.getUselessNodesInGraph(aGraph)
        self.assertEqual(len(aNodes), 4)
        countNodes = len(aGraph.mCompNodes)
        sbscleaner.cleanUselessNodesInGraph(aGraph)
        self.assertEqual(len(aGraph.mCompNodes), countNodes-4)

    def test_CleanFunctionNodes(self):
        """
        This test checks the cleaning of useless function nodes
        """
        sbsDoc = SBSCleanerTests.openTestDocument('Functions.sbs')
        aFunction = sbsDoc.getSBSFunction('Function')
        aNodes = sbscleaner.getUselessNodesInFunction(aFunction)
        self.assertEqual(aNodes, set([]))

        aFunction = sbsDoc.getSBSFunction('Function2')
        aNodes = sbscleaner.getUselessNodesInFunction(aFunction)
        self.assertEqual(len(aNodes), 1)

        aFunction = sbsDoc.getSBSFunction('Function3')
        aNodes = sbscleaner.getUselessNodesInFunction(aFunction)
        self.assertEqual(len(aNodes), 5)
        nbNodes = len(aFunction.getDynamicValue().mParamNodes)
        sbscleaner.cleanUselessNodesInFunction(aFunction)
        self.assertEqual(len(aFunction.getDynamicValue().mParamNodes), nbNodes-5)

    def test_CleanGraphParams(self):
        """
        This test checks the cleaning of useless compositing graph input parameters
        """
        sbsDoc = SBSCleanerTests.openTestDocument('testCleaner.sbs')
        aGraph = sbsDoc.getSBSGraph('Graph')
        aUselessParams = sbscleaner.getUselessParametersInGraph(aGraph)
        self.assertEqual(aUselessParams, [aGraph.getInputParameter('uselessInput')])

        self.assertEqual(len(aGraph.getInputParameters()), 7)
        sbscleaner.cleanUselessParametersInGraph(aGraph)
        self.assertEqual(len(aGraph.getInputParameters()), 6)

    def test_CleanFunctionParams(self):
        """
        This test checks the cleaning of useless function input parameters
        """
        sbsDoc = SBSCleanerTests.openTestDocument('Functions.sbs')
        aFunction = sbsDoc.getSBSFunction('Function3')
        aUselessParams = sbscleaner.getUselessParametersInFunction(aFunction)
        self.assertEqual(len(aUselessParams), 2)

        self.assertEqual(len(aFunction.getInputParameters()), 3)
        sbscleaner.cleanUselessParametersInFunction(aFunction)
        self.assertEqual(len(aFunction.getInputParameters()), 1)


if __name__ == '__main__':
    unittest.main()
