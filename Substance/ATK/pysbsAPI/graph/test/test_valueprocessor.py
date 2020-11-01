# coding: utf-8
import unittest
import logging
log = logging.getLogger(__name__)
import os
import sys

from pysbs import python_helpers
from pysbs import sbsenum
from pysbs import context
from pysbs import sbsgenerator
from pysbs import substance
from pysbs.api_exceptions import SBSImpossibleActionError


testModule = sys.modules[__name__]

class SBSValueProcessorTests(unittest.TestCase):
    @staticmethod
    def createTestDoc(graph):
        # Create value processor
        vp_node = graph.createCompFilterNode(sbsenum.FilterEnum.VALUE_PROCESSOR, aGUIPos=[-100, 0, 0])
        output = graph.createOutputNode('output', aGUIPos=[100, 0, 0])
        graph.connectNodes(vp_node, output)

        return vp_node, output


    def test_createValueProcessor(self):
        """
        This test checks creating Value processor nodes34
        """
        log.info("Value Processor: Testing creating a value processor")
        sbs_context = context.Context()
        # Create our target document
        output_file = python_helpers.getAbsPathFromModule(testModule, './resources/testValueProcessor.sbs')
        sbsDoc = sbsgenerator.createSBSDocument(sbs_context,
                                                aFileAbsPath=output_file)
        # Test a graph with an input value
        graph = sbsDoc.createGraph('Test')
        vp_node, output = SBSValueProcessorTests.createTestDoc(graph)
        vp_file = python_helpers.getAbsPathFromModule(testModule, './resources/ValueGraph.sbs/ValueGraph')
        vp_file_sbsar = python_helpers.getAbsPathFromModule(testModule, './resources/ValueGraph.sbsar/ValueGraph')

        value_node = graph.createCompInstanceNodeFromPath(sbsDoc, vp_file)
        value_node_sbsar = graph.createCompInstanceNodeFromPath(sbsDoc, vp_file_sbsar)
        blend_node = graph.createCompFilterNode(sbsenum.FilterEnum.BLEND, aGUIPos=[-200, 0, 0])

        vpfunc = vp_node.getValProcFunction()
        aOutputNode = vpfunc.createFunctionNode(aFunction=sbsenum.FunctionEnum.MUL_SCALAR, aGUIPos=[200, 0, 0])
        aConstant1 = vpfunc.createFunctionNode(aFunction=sbsenum.FunctionEnum.CONST_FLOAT4,
                                               aGUIPos=[0, -80, 0],
                                               aParameters={sbsenum.FunctionEnum.CONST_FLOAT4: [0, 1, 3, 1]})
        aConstant2 = vpfunc.createFunctionNode(aFunction=sbsenum.FunctionEnum.CONST_FLOAT,
                                               aGUIPos=[0, 80, 0],
                                               aParameters={sbsenum.FunctionEnum.CONST_FLOAT: 1.0})
        aConstant3 = vpfunc.createFunctionNode(aFunction=sbsenum.FunctionEnum.CONST_FLOAT3,
                                               aGUIPos=[0, -80, 0],
                                               aParameters={sbsenum.FunctionEnum.CONST_FLOAT3: [0, 1, 3]})
        vpfunc.connectNodes(aConstant3, aOutputNode, sbsenum.FunctionInputEnum.A)
        vpfunc.connectNodes(aConstant2, aOutputNode, sbsenum.FunctionInputEnum.SCALAR)

        # Test changing output node and make sure the type of the value processor node updates
        # Set float 1 as output and make sure it's right
        vpfunc.setOutputNode(aConstant2)
        self.assertEqual(vp_node.getCompOutputType(), aConstant2.getOutputType())

        # Set scalar multiplication as output, make sure it takes the type of the float 3 node
        vpfunc.setOutputNode(aOutputNode)
        self.assertEqual(vp_node.getCompOutputType(), aConstant3.getOutputType())

        # Change input of scalar multiplication to be a float 4 and make sure the
        # value processor is now a float 4
        vpfunc.connectNodes(aConstant1, aOutputNode, sbsenum.FunctionInputEnum.A)
        self.assertEqual(vp_node.getCompOutputType(), aConstant1.getOutputType())

        # Success: Connect value with output node
        graph.connectNodes(vp_node, output)

        for vn in [value_node, value_node_sbsar]:
            # Success: Connect value with both left and right pins specified
            graph.connectNodes(vp_node, vn, aRightNodeInput='inputValue', aLeftNodeOutput=sbsenum.OutputEnum.OUTPUT)

            # Success: Connect value with no left output specified
            # Success: Connect value to preexisting value
            graph.connectNodes(vp_node, vn, aRightNodeInput='inputValue')

            # Success: Connect value with no right input specified
            graph.connectNodes(vp_node, vn, aLeftNodeOutput=sbsenum.OutputEnum.OUTPUT)

            # Success: Connect value with neither input nor output specified
            graph.connectNodes(vp_node, vn)

            # Success: disconnect value
            graph.disconnectNodes(vp_node, vn, aRightNodeInput='inputValue', aLeftNodeOutput=sbsenum.OutputEnum.OUTPUT)

            # Fail: Connect value to a un-connectable value
            with self.assertRaises(SBSImpossibleActionError):
                graph.connectNodes(vp_node, vn, aRightNodeInput='notConnectable')

            # Fail: Connect entry to value
            with self.assertRaises(SBSImpossibleActionError):
                graph.connectNodes(blend_node, vn, aRightNodeInput='inputValue')

            # Fail: Connect value to entry
            with self.assertRaises(SBSImpossibleActionError):
                graph.connectNodes(vp_node, blend_node)

            graph.connectNodes(vn, output)

            # Write and read doc to validate it's writing valid files
            sbsDoc.writeDoc()
            testDoc = substance.SBSDocument(sbs_context, output_file)

            os.remove(output_file)