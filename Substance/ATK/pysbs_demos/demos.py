# coding: utf-8
"""
Module **demos** provides samples of usage of Pysbs.
"""
from __future__ import unicode_literals

import logging
log = logging.getLogger(__name__)
import os
import glob
import sys

try:
    import pysbs
except ImportError:
    try:
        pysbsPath = bytes(__file__).decode(sys.getfilesystemencoding())
    except:
        pysbsPath = bytes(__file__, sys.getfilesystemencoding()).decode(sys.getfilesystemencoding())
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(pysbsPath)[0], '..')))

from pysbs.api_decorators import doc_source_code
from pysbs import python_helpers
from pysbs import base
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import substance
from pysbs import sbsbakers
from pysbs import sbsexporter
from pysbs import sbsgenerator
from pysbs import mdl


@doc_source_code
def demoReadWriteSBS(aContext, aFileAbsPath = '', aDestFileAbsPath = ''):
    """
    Allow to validate the deserialization and serialization of a .sbs without doing any modification on it.

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aFileAbsPath == '' or aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        return False

    try:
        # Parse document
        sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
        sbsDoc.parseDoc()

        # Display its dependencies and resources
        log.info("Dependencies: ")
        for s in sbsDoc.getSBSDependencyList():
            log.info(s.mFileAbsPath)
        log.info("\nResources: ")
        for s in sbsDoc.getSBSResourceList():
            log.info(s.getResolvedFilePath())
            log.info(s.mFileAbsPath)

        # Write the document
        sbsDoc.writeDoc(aNewFileAbsPath = aDestFileAbsPath)
        log.info("\n=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoHelloWorld] Failed to create the new package")
        raise error


@doc_source_code
def demoCreation(aContext, aDestFileAbsPath=''):
    """
    Demonstrates all what is possible to create using this API:
        - A new substance from scratch
        - Compositing graph (all filters, instance of graphs, inputs and outputs...)
        - Function graph (all functions, instance of functions, ...)
        - Definition of input parameters for graphs and functions
        - Definition of a dynamic parameter

    :param aContext: Execution context
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        return False

    try:
        # Create a new package
        sbsDoc = sbsgenerator.createSBSDocument(aContext, aDestFileAbsPath)

        aGraph = sbsDoc.createGraph(aGraphIdentifier = 'MyGraph',
                                    aParameters = {sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.OutputFormatEnum.FORMAT_16BITS},
                                    aInheritance= {sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.ParamInheritanceEnum.ABSOLUTE})
        aSubGraph = sbsDoc.createGraph(aGraphIdentifier = 'MySubGraph')
        aFunction = sbsDoc.createFunction(aFunctionIdentifier = 'MyFunction')
        aResourceGroup = sbsDoc.createGroup( aParentFolder = 'MyResources', aGroupIdentifier = 'Bitmaps' )

        startPos = [48,  48,  0]
        xOffset  = [192,  0,  0]
        yOffset  = [0,  192,  0]
        xyOffset = [192, 96,  0]

        # ------------------------------------------------------------------------------------------
        # Create the graph 'MySubGraph'
        # ------------------------------------------------------------------------------------------

        # Create Input parameters for MySubGraph
        # - Parameter InputColor(RGBA)
        aSubGraph.addInputParameter(aIdentifier   = 'InputColor',
                            aWidget       = sbsenum.WidgetEnum.COLOR_FLOAT4,
                            aDefaultValue = [1,1,1,1],
                            aLabel        = 'Input Color')

        # - Parameter Blending(DropDown list)
        aParam = aSubGraph.addInputParameter(aIdentifier = 'Blending',
                            aWidget = sbsenum.WidgetEnum.DROPDOWN_INT1,
                            aLabel  = 'Blending')
        aParam.setDropDownList(aValueMap={sbsenum.BlendBlendingModeEnum.MULTIPLY: 'Multiply',
                                          sbsenum.BlendBlendingModeEnum.OVERLAY: 'Overlay',
                                          sbsenum.BlendBlendingModeEnum.SOFT_LIGHT: 'Soft Light'})
        aParam.setDefaultValue(sbsenum.BlendBlendingModeEnum.MULTIPLY)

        # Create the content of the graph MySubGraph
        # - Uniform color filter
        aUniformColor = aSubGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.UNIFORM,
                            aParameters = {sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.COLOR,
                                           sbsenum.CompNodeParamEnum.OUTPUT_COLOR: [0.54,0.063,0,1]},
                            aGUIPos=startPos)

        # - Input node color
        aInputNode = aSubGraph.createInputNode(aIdentifier = 'MyInput',
                            aColorMode   = sbsenum.ColorModeEnum.COLOR,
                            aGUIPos      = aUniformColor.getOffsetPosition(yOffset),
                            aAttributes  = {sbsenum.AttributesEnum.Label: 'My Input'},
                            aUsages      = {sbsenum.UsageEnum.BASECOLOR:{sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGB}})

        # - Blend filter
        aBlendNode = aSubGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.BLEND,
                            aGUIPos      = aUniformColor.getOffsetPosition(xyOffset),
                            aParameters  = {sbsenum.CompNodeParamEnum.BLENDING_MODE: sbsenum.BlendBlendingModeEnum.MULTIPLY,
                                            sbsenum.CompNodeParamEnum.OPACITY: 0.67},
                            aInheritance = {sbsenum.CompNodeParamEnum.OUTPUT_SIZE: sbsenum.ParamInheritanceEnum.PARENT})

        # - Output node
        aOutputNode = aSubGraph.createOutputNode(aIdentifier = 'MyOutput',
                            aGUIPos       = aBlendNode.getOffsetPosition(xOffset),
                            aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,
                            aAttributes   = {sbsenum.AttributesEnum.Description: 'SubGraph Output'},
                            aUsages       = {sbsenum.UsageEnum.BASECOLOR: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})

        # Connect the nodes
        aSubGraph.connectNodes(aLeftNode  = aInputNode, aRightNode = aBlendNode,
                            aRightNodeInput = sbsenum.InputEnum.DESTINATION)
        aSubGraph.connectNodes(aLeftNode  = aUniformColor, aRightNode = aBlendNode,
                            aRightNodeInput = sbsenum.InputEnum.SOURCE)
        aSubGraph.connectNodes(aLeftNode  = aBlendNode, aRightNode = aOutputNode,
                            aRightNodeInput = sbsenum.InputEnum.INPUT_NODE_OUTPUT)

        # Define some dynamic parameters, handled by the input parameters defined in SubGraph:
        aDynFunction = aUniformColor.setDynamicParameter(sbsenum.CompNodeParamEnum.OUTPUT_COLOR)
        aDynFunction.setToInputParam(aParentGraph = aSubGraph, aInputParamIdentifier = 'InputColor')

        aDynFunction = aBlendNode.setDynamicParameter(sbsenum.CompNodeParamEnum.BLENDING_MODE)
        aDynFunction.setToInputParam(aParentGraph = aSubGraph, aInputParamIdentifier = 'Blending')


        # ------------------------------------------------------------------------------------------
        # Create the function 'MyFunction'
        # ------------------------------------------------------------------------------------------
        aFunction.initFunction()

        # - Definition of the function input parameter: BlurIntensity
        aParamBlur = 'BlurIntensity'
        aFunction.addInputParameter(aIdentifier = aParamBlur,
                            aWidget = sbsenum.WidgetEnum.SLIDER_FLOAT1)

        # - Function node Get_Float(BlurIntensity)
        aNodeGet = aFunction.createFunctionNode(aFunction = sbsenum.FunctionEnum.GET_FLOAT1,
                            aParameters = {sbsenum.FunctionEnum.GET_FLOAT1: aParamBlur},
                            aGUIPos=startPos)

        # - Function node Pi (instance included in package sbs://functions.sbs)
        aNodePi = aFunction.createFunctionInstanceNodeFromPath(aSBSDocument = sbsDoc,
                            aPath = 'sbs://functions.sbs/Functions/Math/Pi',
                            aGUIPos = aNodeGet.getOffsetPosition(yOffset))

        # - Function node Mul
        aNodeMult = aFunction.createFunctionNode(aFunction = sbsenum.FunctionEnum.MUL,
                            aGUIPos = aNodeGet.getOffsetPosition(xyOffset))

        # Connect the nodes
        aFunction.connectNodes(aLeftNode = aNodeGet, aRightNode= aNodeMult, aRightNodeInput = sbsenum.FunctionInputEnum.A)
        aFunction.connectNodes(aLeftNode = aNodePi, aRightNode = aNodeMult, aRightNodeInput = sbsenum.FunctionInputEnum.B)
        aFunction.setOutputNode(aNodeMult)


        # ------------------------------------------------------------------------------------------
        # Create the graph 'MyGraph'
        # ------------------------------------------------------------------------------------------

        # Create Input parameters for MyGraph
        aParam = aGraph.addInputParameter(aIdentifier = aParamBlur,
                            aWidget = sbsenum.WidgetEnum.SLIDER_FLOAT1,
                            aLabel  = 'Blur Intensity')
        aParam.setDefaultValue(0.5)
        aParam.setMaxValue(3)

        # Create the content of MyGraph

        # - FxMap Node
        aFxMapNode = aGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.FXMAPS,
                            aParameters={sbsenum.CompNodeParamEnum.COLOR_MODE: sbsenum.ColorModeEnum.GRAYSCALE,
                                         sbsenum.CompNodeParamEnum.RANDOM_SEED: 5},
                            aGUIPos=startPos)

        #  - Creation of the FxMap graph:
        aFxMapGraph = aFxMapNode.getFxMapGraph()

        #   - First Quadrant node (root)
        aQuadrant1 = aFxMapGraph.createFxMapNode(aFxMapNode = sbsenum.FxMapNodeEnum.QUADRANT)
        aFxMapGraph.setRootNode(aQuadrant1)

        #   - Second Quadrant node
        aQuadrant2 = aFxMapGraph.createFxMapNode(aFxMapNode = sbsenum.FxMapNodeEnum.QUADRANT,
                            aGUIPos = aQuadrant1.getOffsetPosition(yOffset))

        #   - Third Quadrant node
        aQuadrant3 = aFxMapGraph.createFxMapNode(aFxMapNode = sbsenum.FxMapNodeEnum.QUADRANT,
                            aGUIPos = aQuadrant2.getOffsetPosition(yOffset),
                            aParameters = {sbsenum.CompNodeParamEnum.FX_PATTERN_TYPE: sbsenum.FX_PatternType.PYRAMID})

        #   - Define several functions for the third quadrant node
        #    => Random luminosity (Float1 between 0 and 1)
        aFuncLum = aQuadrant3.setDynamicParameter(sbsenum.CompNodeParamEnum.FX_COLOR_LUM)
        aFloatNode = aFuncLum.createFunctionNode(aFunction = sbsenum.FunctionEnum.CONST_FLOAT,
                            aParameters = {sbsenum.FunctionEnum.CONST_FLOAT: 1})
        aRandNode = aFuncLum.createFunctionNode(aFunction = sbsenum.FunctionEnum.RAND,
                            aGUIPos = aFloatNode.getOffsetPosition(xOffset))

        aFuncLum.connectNodes(aLeftNode=aFloatNode, aRightNode=aRandNode)
        aFuncLum.setOutputNode(aRandNode)

        #    => Random pattern rotation (Float1 between 0 and 1)
        aFuncRotation = aFuncLum.copy()
        aQuadrant3.setParameterValue(sbsenum.CompNodeParamEnum.FX_PATTERN_ROTATION, aFuncRotation)

        #    => Random pattern offset (Float2 between -1 and 1)
        aFuncOffset = aQuadrant3.setDynamicParameter(sbsenum.CompNodeParamEnum.FX_PATTERN_OFFSET)
        aRandNode = aFuncOffset.createFunctionInstanceNodeFromPath(aSBSDocument=sbsDoc,
                            aPath   = 'sbs://functions.sbs/Functions/Random/Uniform_[-1,1[')
        aRandNode2 = aFuncOffset.createFunctionInstanceNodeFromPath(aSBSDocument=sbsDoc,
                            aPath   = 'sbs://functions.sbs/Functions/Random/Uniform_[-1,1[',
                            aGUIPos = aRandNode.getOffsetPosition(yOffset))

        aVec2Node = aFuncOffset.createFunctionNode(aFunction = sbsenum.FunctionEnum.VECTOR2,
                            aGUIPos = aRandNode.getOffsetPosition(xyOffset))

        aFuncOffset.connectNodes(aLeftNode = aRandNode, aRightNode = aVec2Node,
                            aRightNodeInput = sbsenum.FunctionInputEnum.COMPONENTS_IN)
        aFuncOffset.connectNodes(aLeftNode = aRandNode2, aRightNode = aVec2Node,
                            aRightNodeInput = sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        aFuncOffset.setOutputNode(aVec2Node)

        #    => Random pattern size (Float2 between 0.5 and 2)
        aFuncSize = aQuadrant3.setDynamicParameter(sbsenum.CompNodeParamEnum.FX_PATTERN_SIZE)
        aFloatNode1 = aFuncSize.createFunctionNode(aFunction = sbsenum.FunctionEnum.CONST_FLOAT,
                            aParameters = {sbsenum.FunctionEnum.CONST_FLOAT: 0.5})
        aFloatNode2 = aFuncSize.createFunctionNode(aFunction = sbsenum.FunctionEnum.CONST_FLOAT,
                            aParameters = {sbsenum.FunctionEnum.CONST_FLOAT: 2},
                            aGUIPos = aFloatNode1.getOffsetPosition(yOffset))
        aRandNode = aFuncSize.createFunctionInstanceNodeFromPath(aSBSDocument=sbsDoc,
                            aPath   = 'sbs://functions.sbs/Functions/Random/Uniform_[A,B[',
                            aGUIPos = aFloatNode1.getOffsetPosition(xyOffset))
        aVec2Node = aFuncSize.createFunctionNode(aFunction = sbsenum.FunctionEnum.VECTOR2,
                            aGUIPos = aRandNode.getOffsetPosition(xOffset))

        aFuncSize.connectNodes(aLeftNode = aFloatNode1, aRightNode = aRandNode, aRightNodeInput = 'A')
        aFuncSize.connectNodes(aLeftNode = aFloatNode2, aRightNode = aRandNode, aRightNodeInput = 'B')
        aFuncSize.connectNodes(aLeftNode = aRandNode, aRightNode = aVec2Node, aRightNodeInput = sbsenum.FunctionInputEnum.COMPONENTS_IN)
        aFuncSize.connectNodes(aLeftNode = aRandNode, aRightNode = aVec2Node, aRightNodeInput = sbsenum.FunctionInputEnum.COMPONENTS_LAST)
        aFuncSize.setOutputNode(aVec2Node)

        #   - Fourth and Fifth Quadrant nodes, copies of the third one
        aQuadrant4 = aFxMapGraph.duplicateNode(aQuadrant3, aGUIOffset = yOffset)
        aQuadrant5 = aFxMapGraph.duplicateNode(aQuadrant4, aGUIOffset = yOffset)

        #   - Connections of the quadrant nodes
        aFxMapGraph.connectNodes(aTopNode = aQuadrant1, aBottomNode = aQuadrant2)
        aFxMapGraph.connectNodes(aTopNode = aQuadrant2, aBottomNode = aQuadrant3)
        aFxMapGraph.connectNodes(aTopNode = aQuadrant3, aBottomNode = aQuadrant4)
        aFxMapGraph.connectNodes(aTopNode = aQuadrant4, aBottomNode = aQuadrant5)


        # - Gradient Filter with key values
        gradientKeyValues = [sbslibrary.GradientKey(aPosition = 0,     aValue = [0,0,0,1]),
                             sbslibrary.GradientKey(aPosition = 0.330, aValue = [1,1,1,1])]
        aGradientNode = aGraph.createGradientMapNode(aGUIPos = aFxMapNode.getOffsetPosition(xOffset),
                                                     aKeyValues = gradientKeyValues,
                                                     aParameters= {sbsenum.CompNodeParamEnum.GRADIENT_ADDRESSING: sbsenum.GradientAddressingEnum.REPEAT})

        # - Instance of graph SubGraph created previously
        aInstanceNode = aGraph.createCompInstanceNode(aSBSDocument = sbsDoc,
                            aGraph  = aSubGraph,
                            aGUIPos = aGradientNode.getOffsetPosition(xOffset))

        # - Instance of substance Blur_Hq included in the default package sbs://
        aBlurHQNode = aGraph.createCompInstanceNodeFromPath(aSBSDocument= sbsDoc,
                            aPath       = 'sbs://blur_hq.sbs/blur_hq',
                            aGUIPos     = aInstanceNode.getOffsetPosition(xOffset),
                            aParameters = {'Intensity':2.8})

        #   - Definition of a dynamic parameter for the Blur_Hq Intensity parameter:
        aBlurFunction = aBlurHQNode.setDynamicParameter(aParameter = 'Intensity')
        aGetFloatNode = aBlurFunction.createFunctionNode(aFunction = sbsenum.FunctionEnum.GET_FLOAT1,
                            aParameters = {sbsenum.FunctionEnum.GET_FLOAT1: aParamBlur})

        #   - Creation of an instance of function MyFunction defined previously:
        aFctInstanceNode = aBlurFunction.createFunctionInstanceNode(aSBSDocument = sbsDoc,
                            aFunction = aFunction,
                            aGUIPos   = aGetFloatNode.getOffsetPosition(xOffset))

        #   - Connect the nodes
        aBlurFunction.connectNodes(aLeftNode = aGetFloatNode, aRightNode = aFctInstanceNode)
        aBlurFunction.setOutputNode(aFctInstanceNode)

        # - SVG node
        aSvgPath = sbsDoc.buildAbsPathFromRelToMePath('Bitmaps/SD_Icon_Color.svg' )
        aSVGNode = aGraph.createSvgNode(aSBSDocument = sbsDoc,
                            aResourcePath  = aSvgPath,
                            aResourceGroup = aResourceGroup,
                            aGUIPos        = aBlurHQNode.getOffsetPosition(xOffset),
                            aParameters    = {sbsenum.CompNodeParamEnum.COLOR_MODE:sbsenum.ColorModeEnum.COLOR,
                                              sbsenum.CompNodeParamEnum.OUTPUT_SIZE:[sbsenum.OutputSizeEnum.SIZE_1024,sbsenum.OutputSizeEnum.SIZE_1024],
                                              sbsenum.CompNodeParamEnum.TILING_MODE:sbsenum.TilingEnum.NO_TILING},
                            aInheritance   = {sbsenum.CompNodeParamEnum.OUTPUT_SIZE:sbsenum.ParamInheritanceEnum.ABSOLUTE,
                                              sbsenum.CompNodeParamEnum.TILING_MODE:sbsenum.ParamInheritanceEnum.INPUT},
                            aCookedQuality = 0.5)

        # - Output node
        aOutputNode = aGraph.createOutputNode(aIdentifier = 'MainOutput',
                            aGUIPos       = aSVGNode.getOffsetPosition(xOffset),
                            aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,
                            aAttributes   = {sbsenum.AttributesEnum.Description: 'Main Output'},
                            aMipmaps      = sbsenum.MipmapEnum.LEVELS_12,
                            aUsages       = {sbsenum.UsageEnum.BASECOLOR: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA}})

        # Connect the nodes
        aGraph.connectNodes(aLeftNode = aFxMapNode,    aRightNode = aGradientNode)
        aGraph.connectNodes(aLeftNode = aGradientNode, aRightNode = aInstanceNode, aRightNodeInput = 'MyInput')
        aGraph.connectNodes(aLeftNode = aInstanceNode, aRightNode = aBlurHQNode)
        aGraph.connectNodes(aLeftNode = aBlurHQNode,   aRightNode = aSVGNode)
        aGraph.connectNodes(aLeftNode = aSVGNode,      aRightNode = aOutputNode)

        # Tweak parameters
        aInstanceNode.getParameterValue('InputColor')
        aInstanceNode.setParameterValue('InputColor', [1, 0, 0, 1])
        aInstanceNode.setParameterValue('Blending', sbsenum.BlendBlendingModeEnum.OVERLAY)

        # Set graph attributes and icon
        aGraph.setAttribute(aAttributeIdentifier = sbsenum.AttributesEnum.Author, aAttributeValue = 'Substance Designer API')
        aGraph.setIcon(aIconAbsPath = sbsDoc.buildAbsPathFromRelToMePath('Bitmaps/graphIcon.jpg'))

        # Write the document structure into the destination .sbs file
        sbsDoc.writeDoc()

        log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoCreation] Failed to create the new package")
        raise error


@doc_source_code
def demoCreationMDL(aContext, aDestFileAbsPath=''):
    """
    Demonstrates the MDL graph creation using this API:
        - MDL Graph
        - MDL Nodes of any kind (constants, native mdl nodes, mdl graph instances, ...)
        - Declaring the input of the graph
        - Setting parameters and annotations
        - Create resources dedicated to MDL graphs (light profile or bsdf measurement)

    :param aContext: Execution context
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        return False

    try:
        startPos = [48,  48,  0]
        xOffset  = [192,  0,  0]
        yOffset  = [0,  192,  0]
        xyOffset = [192, 96,  0]

        # Create a new package and a MDL graph
        sbsDoc = sbsgenerator.createSBSDocument(aContext, aDestFileAbsPath)
        mdlGraph = sbsDoc.createMDLGraph(aGraphIdentifier='DemoMDLGraph', aCreateOutputNode=True)

        # Create a new Substance graph, which will be used in the MDL graph
        sbsGraph = sbsDoc.createGraph(aGraphIdentifier='SBSGraph')
        aNode = sbsGraph.createCompFilterNode(aFilter=sbsenum.FilterEnum.UNIFORM,
                                            aParameters={sbsenum.CompNodeParamEnum.OUTPUT_COLOR:[0,0,1,1]},
                                            aGUIPos=startPos)
        aOutput = sbsGraph.createOutputNode(aIdentifier='Output',
                                            aGUIPos=aNode.getOffsetPosition(xOffset))
        sbsGraph.connectNodes(aLeftNode=aNode, aRightNode=aOutput)


        # Create the microfacet ggx branch
        inputRoughness = mdlGraph.createMDLNodeConst(aName='roughness', aConstTypePath='mdl::float', aExposed=True,
                                            aValue=0.5,
                                            aAnnotations={mdl.mdlenum.MDLAnnotationEnum.DISPLAY_NAME:'Roughness',
                                                          mdl.mdlenum.MDLAnnotationEnum.GAMMA_TYPE:1,
                                                          mdl.mdlenum.MDLAnnotationEnum.SAMPLER_USAGE:'roughness',
                                                          mdl.mdlenum.MDLAnnotationEnum.HARD_RANGE:[0,1]},
                                            aGUIPos=startPos)
        sbsInstance = mdlGraph.createMDLNodeSBSGraphInstance(aSBSDocument=sbsDoc,
                                                             aGraph=sbsGraph,
                                                             aGUIPos=inputRoughness.getOffsetPosition(yOffset))

        mulNode = mdlGraph.createMDLNodeInstance(aPath='mdl::operator*(float,float)',
                                                 aGUIPos=inputRoughness.getOffsetPosition(xOffset))

        ggxNode = mdlGraph.createMDLNodeInstance(aPath='mdl::df::microfacet_ggx_smith_bsdf(float,float,color,float3,::df::scatter_mode,string)',
                                                 aGUIPos=mulNode.getOffsetPosition(xyOffset))
        mdlGraph.connectNodes(aLeftNode=inputRoughness, aRightNode=mulNode, aRightNodeInput='x')
        mdlGraph.connectNodes(aLeftNode=inputRoughness, aRightNode=mulNode, aRightNodeInput='y')
        mdlGraph.connectNodes(aLeftNode=mulNode, aRightNode=ggxNode, aRightNodeInput='roughness_u')
        mdlGraph.connectNodes(aLeftNode=mulNode, aRightNode=ggxNode, aRightNodeInput='roughness_v')
        mdlGraph.connectNodes(aLeftNode=sbsInstance, aRightNode=ggxNode, aRightNodeInput='tint')


        # Create a new light profile resource
        aPath = sbsDoc.buildAbsPathFromRelToMePath('Bitmaps/Comet.IES')
        aRes = sbsDoc.createLinkedResource(aResourcePath=aPath,aResourceTypeEnum=sbsenum.ResourceTypeEnum.LIGHT_PROFILE)

        # Create a IES profile node that uses this resource and generate a 'material_emission'
        iesNode = mdlGraph.createMDLNodeInstance(aPath='mdl::light_profile(string)',
                                                 aGUIPos=sbsInstance.getOffsetPosition(yOffset))
        iesNode.setParameterValue(aParameter='name', aParamValue=aRes.getPkgResourcePath())

        edfNode = mdlGraph.createMDLNodeInstance(aPath='mdl::df::measured_edf(light_profile,float,bool,float3x3,float3,string)',
                                                 aParameters={'multiplier':0.01},
                                                 aGUIPos=iesNode.getOffsetPosition(xOffset))
        matEmissionNode = mdlGraph.createMDLNodeInstance(aPath='mdl::material_emission(edf,color,intensity_mode)',
                                                         aParameters={'intensity':[0.000619,0.000387,0.000077]},
                                                         aGUIPos=edfNode.getOffsetPosition(xOffset))

        mdlGraph.connectNodes(aLeftNode=iesNode, aRightNode=edfNode)
        mdlGraph.connectNodes(aLeftNode=edfNode, aRightNode=matEmissionNode)

        # Handle the material_geometry
        stateNormal = mdlGraph.createMDLNodeInstance(aPath='mdl::state::normal()',
                                                     aGUIPos=iesNode.getOffsetPosition(yOffset))

        inputNormal =  mdlGraph.createMDLNodeConst(aName='normal', aConstTypePath='mdl::float3', aExposed=True,
                                            aAnnotations={mdl.mdlenum.MDLAnnotationEnum.DISPLAY_NAME:'Normal',
                                                          mdl.mdlenum.MDLAnnotationEnum.GAMMA_TYPE:1,
                                                          mdl.mdlenum.MDLAnnotationEnum.SAMPLER_USAGE:'normal'},
                                            aGUIPos=stateNormal.getOffsetPosition(xOffset))

        matGeometryNode = mdlGraph.createMDLNodeInstance(aPath='mdl::material_geometry(float3,float,float3)',
                                                         aGUIPos=inputNormal.getOffsetPosition(xOffset))

        mdlGraph.connectNodes(aLeftNode=stateNormal, aRightNode=inputNormal)
        mdlGraph.connectNodes(aLeftNode=inputNormal, aRightNode=matGeometryNode, aRightNodeInput='normal')

        # Create the material_surface
        matSurfaceNode = mdlGraph.createMDLNodeInstance(aPath='mdl::material_surface(bsdf,material_emission)',
                                                        aGUIPos=ggxNode.getOffsetPosition(xyOffset))
        matSurfaceNode.setPinVisibilityForParameter(aParameter='emission', aVisible=True)

        mdlGraph.connectNodes(aLeftNode=ggxNode, aRightNode=matSurfaceNode)
        mdlGraph.connectNodes(aLeftNode=matEmissionNode, aRightNode=matSurfaceNode)

        # Get the output node
        outputNode = mdlGraph.getGraphOutput()
        outputNode.setPosition(matSurfaceNode.getOffsetPosition(xyOffset))

        mdlGraph.connectNodes(aLeftNode=matSurfaceNode, aRightNode=outputNode)
        mdlGraph.connectNodes(aLeftNode=matGeometryNode, aRightNode=outputNode)

        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc(aNewFileAbsPath=aDestFileAbsPath)

        del sbsDoc
        log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoCreationMDL] Failed to modify package")
        raise error


@doc_source_code
def demoMassiveModification(aContext, aFileAbsPath = '', aDestFileAbsPath = ''):
    """
    Demonstrates the massive modification of a Substance.
    In this sample, a substance containing 3 graph with lots of Input nodes will be modified so that all Graphs and Input
    nodes pixel format are set to 16 bits per channel, without inheritance from parent.

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aFileAbsPath == '' or aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        return False

    try:
        # Parse the .sbs file and provide the object structure of the entire substance
        sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
        sbsDoc.parseDoc()

        # Parse all graphs
        for aGraph in sbsDoc.getSBSGraphList():

            # Set pixel format and output size of the graph
            aGraph.setBaseParameterValue(aParameter  = sbsenum.CompNodeParamEnum.OUTPUT_FORMAT,
                                         aParamValue = sbsenum.OutputFormatEnum.FORMAT_16BITS,
                                         aRelativeTo = sbsenum.ParamInheritanceEnum.ABSOLUTE)
            aGraph.setBaseParameterValue(aParameter  = sbsenum.CompNodeParamEnum.OUTPUT_SIZE,
                                         aParamValue = [sbsenum.OutputSizeEnum.SIZE_1024,sbsenum.OutputSizeEnum.SIZE_1024],
                                         aRelativeTo = sbsenum.ParamInheritanceEnum.ABSOLUTE)

            # Set pixel format for all input nodes
            inputNodes = aGraph.getAllInputNodes()
            for inputNode in inputNodes:
                inputNode.setParameterValue(aParameter  = sbsenum.CompNodeParamEnum.OUTPUT_FORMAT,
                                            aParamValue = sbsenum.OutputFormatEnum.FORMAT_16BITS,
                                            aRelativeTo = sbsenum.ParamInheritanceEnum.ABSOLUTE)

        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc(aNewFileAbsPath = aDestFileAbsPath)

        del sbsDoc
        log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoMassiveModification] Failed to modify package")
        raise error



@doc_source_code
def demoIteration(aContext, aFileAbsPath = '', aDestFileAbsPath = ''):
    """
    Demonstrates the iteration creation of a single node and of a complete pattern.

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aFileAbsPath == '' or aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        return False

    try:
        # Parse the .sbs file and provide the object structure of the entire substance
        sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
        sbsDoc.parseDoc()

        # Duplicate 5 times a single node
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'DemoIterationSubGraph')
        aGraph.createIterationOnNode(aNbIteration = 5,
                                     aNodeUID = '1255032103')

        # Duplicate 3 times the node (test the automatic detection of compatible inputs / outputs)
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'DemoIterationSubGraphDouble')
        aGraph.createIterationOnNode(aNbIteration = 3,
                                     aNodeUID = '1255523774')

        # Duplicate 3 times the pattern of nodes (test the automatic detection of compatible inputs / outputs)
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier='DemoIterationPattern')
        aGraph.createIterationOnPattern(aNbIteration=3,
                                        aNodeUIDs=['1255034408', '1255026224', '1255029181', '1255029884',
                                                       '1255029987', '1255029994', '1255029049'])

        # Duplicate 3 times the pattern of nodes, specifying way to connect two successive patterns
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'DemoIterationVerticalPattern')
        aGraph.createIterationOnPattern(aNbIteration = 3,
                                        aNodeUIDs = ['1262168894', '1262168896'],
                                        aNodeUIDs_NextPattern = ['1262169024', '1262168960'],
                                        aGUIOffset    = [0, 120])

        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc(aNewFileAbsPath = aDestFileAbsPath)

        del sbsDoc
        log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoIteration] Failed to modify package")
        raise error


@doc_source_code
def demoIterationPixProc(aContext, aFileAbsPath='', aDestFileAbsPath=''):
    """
    Demonstrates the iteration inside a pixel processor.

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aFileAbsPath == '' or aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        pass

    try:
        # Parse the .sbs file and provide the object structure of the entire substance
        sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
        sbsDoc.parseDoc()

        # Get the graph 'TerrainMultiFractal'
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'TerrainMultiFractal')

        # Get the pixel processor node where the iteration will be created, and its dynamic function
        aPixProcNode = aGraph.getNode('1260898088')
        aDynFct = aPixProcNode.getPixProcFunction()

        # Duplicate 10 times the pattern, indicating the way to reconnect to the next pattern
        createdNodes = aDynFct.createIterationOnPattern(aNbIteration = 10,
                            aGUIOffset = [0, 200],
                            aNodeUIDs = ['1263052178', '1263052114' ],
                            aNodeUIDs_NextPattern = ['1263052279', '1263052278'])

        # Connect the last node of the iteration to the end part of the pixel processor function
        aDynFct.connectNodes(aLeftNode=createdNodes[-1], aRightNode='1257621570')
        aDynFct.connectNodes(aLeftNode=createdNodes[-1], aRightNode='1257624564')

        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc(aNewFileAbsPath = aDestFileAbsPath)

        del sbsDoc
        log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoIteration] Failed to modify package")
        raise error


@doc_source_code
def demoIterationFlame(aContext, aFileAbsPath = '', aDestFileAbsPath = ''):
    """
    Demonstrates the iteration creation of a pattern inside a Function

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aFileAbsPath == '' or aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        return False

    try:
        # Parse the .sbs file and provide the object structure of the entire substance
        sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
        sbsDoc.parseDoc()

        # Duplicate 63 times the pattern inside function RayMarch
        aFunction = sbsDoc.getSBSFunction(aFunctionIdentifier= 'RayMarch')
        createdNodes = aFunction.createIterationOnPattern(aNbIteration = 63,
                            aGUIOffset            = [0, 200],
                            aNodeUIDs             = ['1262101431', '1262101516'],
                            aNodeUIDs_NextPattern = ['1262101533', '1262101527'])

        # Connect the last created node with the end of the function
        aEndNode = aFunction.getNode('1262095290')
        aFunction.connectNodes(aLeftNode = createdNodes[-1], aRightNode = aEndNode,
                               aRightNodeInput = sbsenum.FunctionInputEnum.SEQUENCE_IN)

        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc(aNewFileAbsPath = aDestFileAbsPath)
        log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoIterationFlame] Failed to create the iterations")
        raise error


@doc_source_code
def demoExportWithDependencies(aContext, aFileAbsPath = '', aDestFolderAbsPath = ''):
    """
    Export the given package into the given destination folder

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the package
    :param aDestFolderAbsPath: The absolute folder where to export the package
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aDestFolderAbsPath: str
    :return: Nothing
    """
    if aFileAbsPath == '' or aDestFolderAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFolderAbsPath")
        return False

    try:
        python_helpers.createFolderIfNotExists(aDestFolderAbsPath)

        # Parse the document to export
        sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
        sbsDoc.parseDoc()

        # Create an exporter
        aExporter = sbsexporter.SBSExporter()

        # Export the package into an archived self-contained package, in the folder aDestFolderAbsPath
        # The resources and dependencies of this package will be included in the archive, including the ones referred by the alias sbs://
        aResultingArchive = aExporter.export(aSBSDocument = sbsDoc, aExportFolder = aDestFolderAbsPath,
                                             aBuildArchive = True, aAliasesToExport = ['sbs'])
        log.info("=> Archive created at %s" % aResultingArchive)

        # Same as before, without archiving the resulting folder
        aResultingPath = aExporter.export(aSBSDocument = sbsDoc, aExportFolder = aDestFolderAbsPath,
                                          aAliasesToExport = ['sbs'])
        log.info("=> Substance exported with its dependencies at %s" % aResultingPath)
        return True

    except BaseException as error:
        log.error("!!! [demoExportWithDependencies] Failed to export the package")
        raise error


@doc_source_code
def demoBuildSBSFromPainterBitmaps(aContext, aDestFileAbsPath = ''):
    """
    Create a graph with as many Bitmap & Output node as picture files in the Painter folder

    :param aContext: Execution context
    :param aDestFileAbsPath: The absolute path of the resulting SBS file
    :type aContext: context.Context
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aDestFileAbsPath")
        return False

    xOffset  = [150, 0, 0]
    yOffset  = [0, 150, 0]
    initPos  = [0,0, 0]

    try:
        # Create a new SBSDocument from scratch
        sbsDoc = sbsgenerator.createSBSDocument(aContext,
                                aFileAbsPath = aDestFileAbsPath,
                                aGraphIdentifier = 'PainterFilter',
                                aParameters  = {sbsenum.CompNodeParamEnum.OUTPUT_SIZE:[sbsenum.OutputSizeEnum.SIZE_1024,sbsenum.OutputSizeEnum.SIZE_1024],
                                                sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.OutputFormatEnum.FORMAT_16BITS},
                                aInheritance = {sbsenum.CompNodeParamEnum.OUTPUT_SIZE:sbsenum.ParamInheritanceEnum.ABSOLUTE,
                                                sbsenum.CompNodeParamEnum.OUTPUT_FORMAT:sbsenum.ParamInheritanceEnum.ABSOLUTE})
        aGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'PainterFilter')

        # Retrieve bitmaps
        aPathOutputs = sbsDoc.mDirAbsPath + os.path.sep
        aListOutputs = glob.glob(aPathOutputs+"*.png")
        log.info(len(aListOutputs))

        for x in range(0,len(aListOutputs)):

            log.info(aListOutputs[x])
            # Create a Bitmap node
            aBitmapNode   = aGraph.createBitmapNode(aSBSDocument = sbsDoc,
                                aResourcePath  = aListOutputs[x],
                                aGUIPos        = [y * x for y in yOffset],
                                aParameters    = {sbsenum.CompNodeParamEnum.COLOR_MODE:True},
                                aCookedFormat  = sbsenum.BitmapFormatEnum.JPG,
                                aCookedQuality = 1)

            aId = aListOutputs[x][aListOutputs[x].rfind(os.path.sep)+1:-4]

            # Create a Output color node
            aOutputNode = aGraph.createOutputNode(aIdentifier = aId,
                                aGUIPos        = map(sum, zip([y * x for y in yOffset], xOffset)),
                                aOutputFormat  = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,
                                aAttributes    = {sbsenum.AttributesEnum.Description: 'Exported from painter: %s' % aId},
                                aMipmaps       = sbsenum.MipmapEnum.LEVELS_12,
                                aUsages        = {sbsenum.UsageEnum.DIFFUSE: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.RGBA},
                                                  sbsenum.UsageEnum.HEIGHT: {sbsenum.UsageDataEnum.COMPONENTS:sbsenum.ComponentsEnum.R}})

            aGraph.connectNodes(aLeftNode  = aBitmapNode, aRightNode = aOutputNode,
                                aRightNodeInput = sbsenum.InputEnum.INPUT_NODE_OUTPUT )

            # Update node position
            initPos += yOffset

        # Write back the document structure into the destination .sbs file
        sbsDoc.writeDoc()
        log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
        return True

    except BaseException as error:
        log.error("!!! [demoBuildSBSFromPainterBitmaps] Failed to create the new package")
        raise error


@doc_source_code
def demoBakingParameters(aContext, aFileAbsPath='', aDestFileAbsPath=''):
    """
    Demonstrates the creation and edition of the baking parameters

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aDestFileAbsPath: The absolute path of the resulting file. Can be the same as aFileAbsPath
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aDestFileAbsPath: str
    :return: Nothing
    """
    if aFileAbsPath == '' or aDestFileAbsPath == '':
        log.error("Please provide the appropriate arguments: aFileAbsPath and aDestFileAbsPath")
        return False

    try:
        # Parse the .sbs file and provide the object structure of the entire substance
        sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
        if sbsDoc.parseDoc():
            # Add a new Scene resource to the document
            aRelPath = sbsDoc.buildAbsPathFromRelToMePath(aRelPathFromPackage='./Models/m41_low.fbx')
            aNewResource = sbsDoc.createLinkedResource(aIdentifier='LowResMesh',
                                                       aResourcePath=aRelPath,
                                                       aResourceTypeEnum=sbsenum.ResourceTypeEnum.SCENE)

            # Create BakingParameters for this resource
            aBakingParams = aNewResource.createBakingParameters()

            # Add a high poly mesh from a file path
            aHighPolyFilePath = sbsDoc.buildAbsPathFromRelToMePath('./Models/m41_high.fbx')
            aBakingParams.addHighDefinitionMeshFromFile(aHighPolyFilePath)

            # Set default Antialiasing value
            aBakingParams.setParameterValue(sbsbakers.ConverterParamEnum.DEFAULT__SUB_SAMPLING, sbsbakers.BakerFromMeshSubSamplingEnum.SUBSAMPLING_4x4)

            # Add a Bent Normal From Mesh baker
            BN_baker = aBakingParams.addBaker(sbsbakers.BakerEnum.BENT_NORMALS_FROM_MESH)

            # Add a Normal Map From Mesh baker
            NM_baker = aBakingParams.addBaker(sbsbakers.BakerEnum.NORMAL_MAP_FROM_MESH)

            # Set Antialiasing value specifically to NormalMap baker
            NM_baker.setParameterValue(aParameter=sbsbakers.ConverterParamEnum.DETAIL__SUB_SAMPLING,
                                       aParamValue=sbsbakers.BakerFromMeshSubSamplingEnum.SUBSAMPLING_2x2)

            # Add an Ambient Occlusion baker which uses the resulting map of the Normal Map From Mesh baker
            AO_baker = aBakingParams.addBaker(sbsbakers.BakerEnum.AMBIENT_OCCLUSION)
            AO_baker.setFileParameterValueFromPreviousBaker(aParameter=sbsbakers.ConverterParamEnum.ADDITIONAL__NORMAL_MAP,
                                                            aPreviousBaker=NM_baker)

            # Set back the baking parameters into the options of the second resource
            aNewResource.setBakingParameters(aBakingParams)

            # Write back the document structure into the destination .sbs file
            sbsDoc.writeDoc(aNewFileAbsPath = aDestFileAbsPath)
            log.info("=> Resulting substance saved at %s" % aDestFileAbsPath)
            return True

    except BaseException as error:
        log.error("!!! [demoBakingParameters] Failed to edit the baking parameters")
        raise error


# ==============================================================================
if __name__ == "__main__":
    base.CommandLineArgsProcessor(__name__).call()
