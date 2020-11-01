# coding: utf-8

import os
import sys
import unittest

import pysbs
from pysbs import *

testModule = sys.modules[__name__]


class CommonNodeTest(unittest.TestCase):

    def test_passthrough_node(self):
        """
        Test passthrough (dot) node for different graph type
        """
        sbs_path = python_helpers.getAbsPathFromModule(testModule, 'resources/passthrough_node.sbs')
        a_doc = substance.SBSDocument(pysbs.context.Context(), sbs_path)
        a_doc.parseDoc()
        a_graph = a_doc.createGraph(aGraphIdentifier='test')
        pass_node = a_graph.createCompFilterNode(aFilter=sbsenum.FilterEnum.PASSTHROUGH)
        uni_node = a_graph.createCompFilterNode(aFilter=sbsenum.FilterEnum.UNIFORM)
        uni_node.setParameterValue(aParameter=sbsenum.CompNodeParamEnum.COLOR_MODE,
                                   aParamValue=sbsenum.ColorModeEnum.GRAYSCALE)
        uni_node.mCompOutputs[0].mCompType = str(sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE)

        blur_node = a_graph.createCompFilterNode(aFilter=sbsenum.FilterEnum.BLUR)
        blur_node2 = a_graph.createCompFilterNode(aFilter=sbsenum.FilterEnum.BLUR)
        a_graph.connectNodes(aLeftNode=uni_node, aRightNode=pass_node)
        a_graph.disconnectNodes(aLeftNode=uni_node, aRightNode=pass_node)
        a_graph.connectNodes(aLeftNode=pass_node, aRightNode=blur_node)
        a_graph.disconnectNodes(aLeftNode=pass_node, aRightNode=blur_node)
        a_graph.connectNodes(aLeftNode=pass_node, aRightNode=blur_node2)
        a_graph.disconnectNodes(aLeftNode=pass_node, aRightNode=blur_node2)

        func_graph = a_doc.createFunction()
        pass_node = func_graph.createFunctionNode(sbsenum.FunctionEnum.PASSTHROUGH)
        float_node = func_graph.createFunctionNode(sbsenum.FunctionEnum.CONST_FLOAT)
        func_graph.connectNodes(aLeftNode=float_node, aRightNode=pass_node,
                                aRightNodeInput=sbsenum.FunctionInputEnum.INPUT)
        func_graph.disconnectNodes(aLeftNode=float_node, aRightNode=pass_node,
                                aRightNodeInput=sbsenum.FunctionInputEnum.INPUT)
        vec_float = func_graph.createFunctionNode(sbsenum.FunctionEnum.VECTOR2)
        func_graph.connectNodes(aLeftNode=pass_node, aRightNode=vec_float,
                                aRightNodeInput=sbsenum.FunctionInputEnum.COMPONENTS_IN)
        func_graph.disconnectNodes(aLeftNode=pass_node, aRightNode=vec_float,
                                aRightNodeInput=sbsenum.FunctionInputEnum.COMPONENTS_IN)

        fx_node = a_graph.createCompFilterNode(sbsenum.FilterEnum.FXMAPS)
        fx_graph = fx_node.getFxMapGraph()
        fx_quadrant = fx_graph.createFxMapNode(aFxMapNode=sbsenum.FxMapNodeEnum.QUADRANT)
        fx_graph.setRootNode(fx_quadrant)
        fx_passthrough = fx_graph.createFxMapNode(aFxMapNode=sbsenum.FxMapNodeEnum.PASSTHROUGH)
        fx_graph.connectNodes(aTopNode=fx_quadrant, aBottomNode=fx_passthrough)
        fx_graph.disconnectNodes(aTopNode=fx_quadrant, aBottomNode=fx_passthrough)
