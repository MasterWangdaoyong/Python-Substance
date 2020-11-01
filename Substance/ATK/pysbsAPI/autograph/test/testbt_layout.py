import unittest
import logging
import sys
import os

log = logging.getLogger(__name__)
from pysbs import python_helpers
from pysbs import substance
from pysbs import context
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.autograph import layoutDoc, layoutGraph, GraphLayoutAlignment, GUIElementsToKeepEnum
from pysbs.autograph.ag_layout import _createNodeFinder, _clearNodes, NodesToKeepEnum

testModule = sys.modules[__name__]


class aglayoutTest(unittest.TestCase):
    @staticmethod
    def openTestDocument():
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/layoutme.sbs')
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    # This file tries to identify two identical files with differences in line ending conventions
    def compareDocumentByContent(self, a, b):
        with open(a) as af:
            with open(b) as bf:
                al = af.readlines()
                bl = bf.readlines()
                self.assertEqual(len(al), len(bl))
                for i in range(len(al)):
                    self.assertEqual(al[i], bl[i])

    def test_Layout(self):
        for alignment in [GraphLayoutAlignment.OUTPUTS, GraphLayoutAlignment.INPUTS]:
            test_doc = self.openTestDocument()
            layoutDoc(
                test_doc,
                nodesToKeep=NodesToKeepEnum.KEEP_COMPUTED_AND_INPUT_NODES,
                layoutAlignment=alignment,
                commentsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                framesToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                navigationPinsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
            )
            layoutedPath = python_helpers.getAbsPathFromModule(testModule, './resources/layouted.sbs')
            test_doc.writeDoc(aNewFileAbsPath=layoutedPath)
            refFileName = 'refLayoutedOut.sbs' if alignment == GraphLayoutAlignment.OUTPUTS else 'refLayoutedIn.sbs'
            refAbsPath = python_helpers.getAbsPathFromModule(testModule,
                                                             os.path.join('./resources', refFileName))
            self.compareDocumentByContent(refAbsPath, layoutedPath)
            os.remove(layoutedPath)

    @staticmethod
    def openErrorDocument():
        docAbsPath = python_helpers.getAbsPathFromModule(testModule, './resources/errors.sbs')
        sbsDoc = substance.SBSDocument(context.Context(), docAbsPath)
        sbsDoc.parseDoc()
        return sbsDoc

    class _nullWith:
        """
        Class doing nothing when used in a with statement
        """

        def __init__(self):
            pass

        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def test_Errors(self):
        for keepNodes in [NodesToKeepEnum.KEEP_COMPUTED_AND_INPUT_NODES, NodesToKeepEnum.KEEP_ALL_NODES,
                          NodesToKeepEnum.KEEP_COMPUTED_NODES]:
            test_doc = self.openErrorDocument()
            all_graphs = test_doc.getSBSGraphList()
            all_graphs += test_doc.getMDLGraphList()
            all_graphs += test_doc.getSBSFunctionList()
            graphs_with_dyn_params = test_doc.getSBSGraphList()

            for comp_graph in test_doc.getSBSGraphList():
                for node in comp_graph.getNodeList():
                    if node.isAFxMap() and node.getFxMapGraph() is not None:
                        fx_graph = node.getFxMapGraph()
                        all_graphs.append(fx_graph)
                        graphs_with_dyn_params.append(fx_graph)
                    elif node.isAPixelProcessor():
                        pp_fun = node.getPixProcFunction(createIfEmtpy=False)
                        if pp_fun:
                            all_graphs.append(pp_fun)
            for graph in graphs_with_dyn_params:
                for node in graph.getNodeList():
                    for dyn_param in node.getDynamicParameters():
                        all_graphs.append(dyn_param.getDynamicValue())
            for g in all_graphs:
                with self._nullWith() if keepNodes is NodesToKeepEnum.KEEP_ALL_NODES else self.assertRaises(
                        SBSImpossibleActionError):
                    layoutGraph(
                        g,
                        nodesToKeep=keepNodes,
                        layoutAlignment=GraphLayoutAlignment.OUTPUTS,
                        commentsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                        framesToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                        navigationPinsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                    )
        test_doc = self.openErrorDocument()
        with self._nullWith() if keepNodes is NodesToKeepEnum.KEEP_ALL_NODES else self.assertRaises(
                SBSImpossibleActionError):
            layoutDoc(test_doc,
                      nodesToKeep=keepNodes,
                      layoutAlignment=GraphLayoutAlignment.OUTPUTS,
                      commentsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                      framesToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                      navigationPinsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
                      )

    def test_node_finder(self):
        test_doc = self.openTestDocument()
        for graph in test_doc.getSBSGraphList():
            node_finder = _createNodeFinder(graph)
            nodeUids = [node.mUID for node in graph.getNodeList()]
            selected, discarded = node_finder.findAncestorsOfOutputs()
            self.assertEqual(set(nodeUids), set(selected + discarded))
            for node in graph.getNodeList():
                parents = node_finder.getParentUidsOfNode(node)
                self.assertEqual(set(parents), {node.mUID for node in graph.getNodesConnectedTo(node)})
                children = node_finder.getChildrenUidsOfNode(node)
                self.assertEqual(set(children), {node.mUID for node in graph.getNodesConnectedFrom(node)})

    def test_clear_node(self):
        for clear_mode in [NodesToKeepEnum.KEEP_COMPUTED_NODES, NodesToKeepEnum.KEEP_ALL_NODES,
                           NodesToKeepEnum.KEEP_COMPUTED_AND_INPUT_NODES]:
            test_doc = self.openTestDocument()
            for graph_idx, graph in enumerate(test_doc.getSBSGraphList()):
                original_output_nodes = graph.getAllOutputNodes()
                original_input_nodes = graph.getAllInputNodes()
                original_nodes = graph.getNodeList()
                kept_nodes = set(_clearNodes(graph, clear_mode))

                # All cases have all output nodes
                for output_node in original_output_nodes:
                    self.assertIn(output_node.mUID, kept_nodes)

                # Make sure all inputs are around when explicitly keeping them
                if clear_mode is NodesToKeepEnum.KEEP_COMPUTED_AND_INPUT_NODES or clear_mode is NodesToKeepEnum.KEEP_ALL_NODES:
                    for input_node in original_input_nodes:
                        self.assertIn(input_node.mUID, kept_nodes)

                # Make sure we didn't remove anything when keeping all nodes
                if clear_mode is NodesToKeepEnum.KEEP_ALL_NODES:
                    for node in original_nodes:
                        self.assertIn(node.mUID, kept_nodes)
                    self.assertEqual(len(kept_nodes), len(original_nodes))

                # Make sure we removed unconnected inputs when only keeping
                # things connected to outputs
                if clear_mode is NodesToKeepEnum.KEEP_COMPUTED_NODES:
                    # These two nodes has empty inputs that should be cleaned out
                    if graph_idx in [0, 3]:
                        self.assertLess(len(graph.getAllInputNodes()), len(original_input_nodes))


if __name__ == '__main__':
    unittest.main()
