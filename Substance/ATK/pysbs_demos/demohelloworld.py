# coding: utf-8
"""
Module **demohelloworld** provides a very simple example of usage of the Pysbs, without using argument file.
"""
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import os
import sys

try:
    import pysbs
except ImportError:
    try:
        pysbsPath = bytes(__file__).decode(sys.getfilesystemencoding())
    except:
        pysbsPath = bytes(__file__, sys.getfilesystemencoding()).decode(sys.getfilesystemencoding())
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(pysbsPath)[0], '..')))

from pysbs import python_helpers
from pysbs import context
from pysbs import sbsenum
from pysbs import sbsgenerator
from pysbs.api_decorators import doc_source_code


@doc_source_code
def demoHelloWorld(aDestFileAbsPath):
    """
    Create a substance with a very simple material definition: uniform colors for BaseColor, Roughness and Metallic, and
    save it to 'sample/resultDemoHelloWorld.sbs'

    :param aDestFileAbsPath: The absolute path of the resulting SBS file
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    aContext = context.Context()
    #aContext.getUrlAliasMgr().setAliasAbsPath(aAliasName = 'myAlias', aAbsPath = 'myAliasAbsolutePath')

    startPos = [48, 48, 0]
    xOffset  = [192, 0, 0]
    yOffset  = [0, 192, 0]

    try:
        # Create a new SBSDocument from scratch, with a graph named 'SimpleMaterial'
        sbsDoc = sbsgenerator.createSBSDocument(aContext,
                                aFileAbsPath = aDestFileAbsPath,
                                aGraphIdentifier = 'SimpleMaterial')

        # Get the graph 'SimpleMaterial'
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'SimpleMaterial')

        # Create three Uniform color nodes, for BaseColor, Roughness and Metallic
        baseColor = aGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
                            aParameters = {sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [1, 0, 0, 1]},
                            aGUIPos     = startPos)

        roughness = aGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
                            aParameters = {sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
                                           sbsenum.CompNodeParamEnum.OUTPUT_COLOR: 0.3},
                            aGUIPos     = baseColor.getOffsetPosition(yOffset))

        metallic = aGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
                            aParameters = {sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
                                           sbsenum.CompNodeParamEnum.OUTPUT_COLOR: 0.6},
                            aGUIPos     = roughness.getOffsetPosition(yOffset))

        # Create three Output nodes, for BaseColor, Roughness and Metallic
        outBaseColor = aGraph.createOutputNode(aIdentifier = 'BaseColor',
                            aGUIPos = baseColor.getOffsetPosition(xOffset),
                            aUsages = {sbsenum.UsageEnum.BASECOLOR: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})

        outRoughness = aGraph.createOutputNode(aIdentifier = 'Roughness',
                            aGUIPos = roughness.getOffsetPosition(xOffset),
                            aUsages = {sbsenum.UsageEnum.ROUGHNESS: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})

        outMetallic = aGraph.createOutputNode(aIdentifier = 'Metallic',
                            aGUIPos = metallic.getOffsetPosition(xOffset),
                            aUsages = {sbsenum.UsageEnum.METALLIC: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})

        # Connect the Uniform color nodes to their respective Output node
        # (no need to precise aLeftNodeOutput and aRightNodeInput here as there is no ambiguity)
        aGraph.connectNodes(aLeftNode = baseColor, aRightNode = outBaseColor)
        aGraph.connectNodes(aLeftNode = roughness, aRightNode = outRoughness)
        aGraph.connectNodes(aLeftNode = metallic,  aRightNode = outMetallic)

        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc()
        log.info("=> Resulting substance saved at %s", aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoHelloWorld] Failed to create the new package")
        raise error


if __name__ == "__main__":
    destFileAbsPath = python_helpers.getAbsPathFromModule(sys.modules[__name__], 'sample/resultDemoHelloWorld.sbs')
    demoHelloWorld(aDestFileAbsPath = destFileAbsPath)
