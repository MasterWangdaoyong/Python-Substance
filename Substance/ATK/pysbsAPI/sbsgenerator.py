# coding: utf-8
"""
Module **sbsgenerator** aims to provide useful functions to create/duplicate/connect SBSObjects
"""

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import copy
import io
import os
import shutil
import uuid
import zlib
import base64
import struct
from random import randint

from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import psdparser
from pysbs import python_helpers, api_helpers
from pysbs.api_decorators import handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import UIDGenerator
from pysbs import freeimagebindings


@handle_exceptions()
def createSBSDocument(aContext, aFileAbsPath, aGraphIdentifier = None, aParameters = None, aInheritance = None):
    """
    createSBSDocument(aContext, aFileAbsPath, aGraphIdentifier = None, aParameters = None, aInheritance = None)
    Create a new sbs document.

    :param aContext: initialized context (contains alias information)
    :param aFileAbsPath: destination file of the sbs document (.sbs extension)
    :param aGraphIdentifier: name of the graph to create by default. if None, no graph is created
    :param aParameters: parameters of the graph (among the sbslibrary.sbslibclasses.BaseParameters only)
    :param aInheritance: Inheritance of the parameters
    :type aContext: :class:`.Context`
    :type aFileAbsPath: str
    :type aGraphIdentifier: str, optional
    :type aParameters: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
    :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
    :return: The new :class:`.SBSDocument` object
    """
    from pysbs import substance
    if aParameters is None: aParameters = {}
    if aInheritance is None: aInheritance = {}

    aContent = substance.SBSContent()
    aSBSDocument = substance.SBSDocument(aContext,
                                         aFileAbsPath,
                                         aIdentifier     = 'Unsaved Package',
                                         aFormatVersion  = aContext.getSBSFormatVersion(),
                                         aUpdaterVersion = aContext.getSBSUpdaterVersion(),
                                         aFileUID        = '{' + str(uuid.uuid1()) + '}',
                                         aVersionUID     = '0',
                                         aDependencies   = [],
                                         aContent        = aContent)
    aSBSDocument.setInitialized()

    if aGraphIdentifier is not None:
        aGraph = createGraph(aParentObject = aSBSDocument,
                             aGraphIdentifier = api_helpers.formatIdentifier(aGraphIdentifier),
                             aParameters = aParameters,
                             aInheritance = aInheritance)
        aContent.mGraphs = [aGraph]

    return aSBSDocument


@handle_exceptions()
def createGraph(aParentObject, aGraphIdentifier, aParameters = None, aInheritance = None):
    """
    createGraph(aParentObject, aGraphIdentifier, aParameters = None, aInheritance = None)
    Create a new graph.

    :param aParentObject: reference to the parent object that will contain this graph
    :param aGraphIdentifier: name of the graph
    :param aParameters: parameters of the graph (among the sbslibrary.sbslibclasses.BaseParameters only)
    :param aInheritance: Inheritance of the parameters

    :type aParentObject: :class:`.SBSDocument` or :class:`.SBSContent`
    :type aGraphIdentifier: str
    :type aParameters: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
    :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
    :return: The new :class:`.SBSGraph` object
    """
    from pysbs import params
    from pysbs import graph

    if aParameters is None: aParameters = {}
    if aInheritance is None: aInheritance = {}

    # Generate a new UID
    aUID = UIDGenerator.generateUID(aParentObject)

    # Set the BaseParameter of the graph
    aBaseParams = []
    aNewGraphDefaultParams = sbslibrary.getFilterDefinition(sbsenum.FilterEnum.COMPINSTANCE)
    if aNewGraphDefaultParams is None:
        return None

    for paramKey,paramValue in aParameters.items():
        aBaseParam = aNewGraphDefaultParams.getParameter(paramKey)
        if aBaseParam is not None:
            aParamValue = params.SBSParamValue()
            aParamValue.setConstantValue(aType = aBaseParam.mType, aValue = paramValue)

            # Handle parameter Inheritance
            aRelativeTo = aNewGraphDefaultParams.mInheritance[0]
            for inheritKey,inheritValue in aInheritance.items():
                # Check that the defined Inheritance is allowed
                if inheritKey == paramKey and inheritValue in aNewGraphDefaultParams.mInheritance:
                    aRelativeTo = inheritValue
                    break

            aBaseParam = params.SBSParameter(aName = sbslibrary.getCompNodeParam(aBaseParam.mParameter),
                                             aParamValue = aParamValue,
                                             aRelativeTo = str(aRelativeTo))
            aBaseParams.append(aBaseParam)

    # Create the graph
    aGraph = graph.SBSGraph(aIdentifier = aGraphIdentifier,
                            aUID = aUID,
                            aBaseParameters = aBaseParams,
                            aRoot = graph.SBSRoot())
    return aGraph


@handle_exceptions()
def createMDLGraph(aParentObject, aGraphIdentifier, aCreateOutputNode = True):
    """
    createMDLGraph(aParentObject, aGraphIdentifier)
    Create a new MDL graph with an output node.

    :param aParentObject: reference to the parent object that will contain this graph
    :param aGraphIdentifier: name of the graph
    :param aCreateOutputNode: True to create the output node. Default to True
    :type aParentObject: :class:`.SBSDocument` or :class:`.SBSContent`
    :type aGraphIdentifier: str
    :type aCreateOutputNode: bool
    :return: The new :class:`.SBSGraph` object
    """
    from pysbs import mdl

    # Generate a new UID
    aUID = UIDGenerator.generateUID(aParentObject)

    # Init all the graph annotations
    aAnnotationsDef = mdl.MDLManager.getGraphDefaultAnnotations()
    aAnnotations = [annot.toMDLAnnotation() for annot in aAnnotationsDef]

    # Create the graph
    mdlGraph = mdl.MDLGraph(aIdentifier = aGraphIdentifier,
                            aUID = aUID,
                            aNodes = [],
                            aAnnotations = aAnnotations,
                            aParamInputs = [])

    # Create an output material node
    if aCreateOutputNode:
        mdlGraph.createMDLNodeOutput()

    return mdlGraph


@handle_exceptions()
def createGroup(aParentObject, aGroupIdentifier):
    """
    createGroup(aParentObject, aGroupIdentifier)
    Create a new group.

    :param aParentObject: reference to the parent object that will contain this graph
    :param aGroupIdentifier: name of the group
    :type aParentObject: :class:`.SBSObject`
    :type aGroupIdentifier: str
    :return: The new :class:`.SBSGroup` object
    """
    from pysbs import substance

    # Generate a new UID
    aUID = UIDGenerator.generateUID(aParentObject)

    # Create the group
    aGroup = substance.SBSGroup(aIdentifier = aGroupIdentifier,
                                aUID = aUID,
                                aContent = substance.SBSContent())
    return aGroup


@handle_exceptions()
def createFunction(aParentObject, aFunctionIdentifier):
    """
    createFunction(aParentObject, aFunctionIdentifier)
    Create a new function.

    :param aParentObject: reference to the parent object that will contain this function
    :param aFunctionIdentifier: name of the function
    :type aParentObject: :class:`.SBSObject`
    :type aFunctionIdentifier: str
    :return: The new :class:`.SBSFunction` object
    """
    from pysbs import graph

    # Generate a new UID
    aUID = UIDGenerator.generateUID(aParentObject)

    # Create and init the function
    aFunction = graph.SBSFunction(aIdentifier = aFunctionIdentifier,
                                  aUID = aUID,
                                  aType = str(sbsenum.ParamTypeEnum.VOID_TYPE))
    aFunction.initFunction()
    return aFunction


@handle_exceptions()
def createInputParameter(aUID,
                         aIdentifier,
                         aWidget,
                         aDefaultValue = None,
                         aIsConnectable = None,
                         aOptions = None,
                         aDescription = None,
                         aLabel = None,
                         aGroup = None,
                         aUserData = None,
                         aVisibleIf = None):
    """
    createInputParameter(aUID, aIdentifier, aWidget, aDefaultValue = None, aOptions = None, aDescription = None, aLabel = None, aGroup = None, aUserData = None, aVisibleIf = None)
    Create a :class:`.SBSParamInput` with the given parameters.

    :param aUID: UID of the input parameter
    :param aIdentifier: identifier of the input parameter
    :param aWidget: widget to use for this parameter
    :param aDefaultValue: default value
    :param aIsConnectable: Whether this parameter can be connected for value computation
    :param aOptions: options
    :param aDescription: textual description
    :param aLabel: GUI label for this input parameter
    :param aGroup: string that contains a group name. Can uses path with '/' separators.
    :param aUserData: user tags
    :param aVisibleIf: string boolean expression based on graph inputs values
    :type aUID: str
    :type aIdentifier: str
    :type aWidget: :class:`.WidgetEnum`
    :type aDefaultValue: str, optional
    :type aIsConnectable: bool, optional
    :type aOptions: dictionary in the format {:class:`.WidgetOptionEnum`: value(str)}, optional
    :type aDescription: str, optional
    :type aLabel: str, optional
    :type aGroup: str, optional
    :type aUserData: str, optional
    :type aVisibleIf: str, optional

    :return: The created :class:`.SBSParamInput` object
    :raise: :class:`api_exceptions.SBSImpossibleActionError`
    """
    from pysbs import sbscommon
    from pysbs import graph

    if aOptions is None: aOptions = {}

    # Get default widget definition from the library
    aDefaultWidgetParams = sbslibrary.getDefaultWidget(aWidget)
    if aDefaultWidgetParams is None:
        raise SBSImpossibleActionError('Cannot create the input parameter, the widget '+str(aWidget)+' doesn\'t exist')

    # Handle type
    aType = str(aDefaultWidgetParams.mType)

    # Handle default value (for tag <defaultValue> and inside the widget options)
    # Retrieve the default value from the input default value, the input options or from the default widget definition
    if aDefaultValue is not None:
        defaultValue = aDefaultValue
    else:
        if sbsenum.WidgetOptionEnum.DEFAULT in aOptions:
            defaultValue = aOptions[sbsenum.WidgetOptionEnum.DEFAULT]
        else:
            defaultValue = aDefaultWidgetParams.getDefaultValue()

    defaultValue = api_helpers.formatValueForTypeStr(defaultValue, aDefaultWidgetParams.mType)

    # Create the DefaultValue object
    aDefaultValueObject = sbscommon.SBSConstantValue()
    aDefaultValueObject.setConstantValue(aType = aDefaultWidgetParams.mType,
                                         aValue = defaultValue,
                                         aInt1 = True)

    # Format default for the options
    if aDefaultWidgetParams.mType != sbsenum.ParamTypeEnum.STRING:
        aDefaultValueFormatStr = defaultValue.replace(" ", ";")
    else:
        aDefaultValueFormatStr = defaultValue

    # Create the options: get the value from the given options or from the default option definition
    aWidgetOptions = []
    for aOptionDef in aDefaultWidgetParams.mOptions:
        if aOptionDef.mOption == sbsenum.WidgetOptionEnum.DEFAULT:
            aWidgetOption = sbscommon.SBSOption(aName = sbslibrary.getWidgetOptionName(sbsenum.WidgetOptionEnum.DEFAULT),
                                                aValue = aDefaultValueFormatStr)
        elif aOptionDef.mOption in aOptions:
            aValue = api_helpers.formatValueForTypeStr(aOptions[aOptionDef.mOption], aOptionDef.mType, aSep = ';')
            aWidgetOption = sbscommon.SBSOption(aName = sbslibrary.getWidgetOptionName(aOptionDef.mOption),
                                                aValue = aValue)
        else:
            aWidgetOption = sbscommon.SBSOption(aName = sbslibrary.getWidgetOptionName(aOptionDef.mOption),
                                                aValue = str(aOptionDef.mValue))
        aWidgetOptions.append(aWidgetOption)

    # Create the widget
    aDefaultWidget = graph.SBSWidget(aName = sbslibrary.getWidgetName(aDefaultWidgetParams.mWidget),
                                     aOptions = aWidgetOptions)

    # Create the input parameter
    aParamInput = graph.SBSParamInput(aIdentifier = aIdentifier,
                                      aUID = aUID,
                                      aIsConnectable=aIsConnectable,
                                      aType = aType,
                                      aDefaultValue = aDefaultValueObject,
                                      aDefaultWidget = aDefaultWidget,
                                      aGroup = aGroup,
                                      aVisibleIf =  aVisibleIf)

    # Handle attributes
    if aLabel is not None:          aParamInput.setAttribute(sbsenum.AttributesEnum.Label, aLabel)
    if aDescription is not None:    aParamInput.setAttribute(sbsenum.AttributesEnum.Description, aDescription)
    if aUserData is not None:       aParamInput.setAttribute(sbsenum.AttributesEnum.UserTags, aUserData)

    return aParamInput

@handle_exceptions()
def createPreset(aParentGraph, aLabel, aUsertags=None):
    """
    createPreset(aParentGraph, aLabel, aUsertags=None)
    Create a new empty preset with the given label and usertags.

    :param aParentGraph: The graph associated to the preset to create
    :param aLabel: The label of this preset
    :param aUsertags: The usertags of this preset
    :type aParentGraph: :class:`.SBSGraph`
    :type aLabel: str
    :type aUsertags: str, optional
    :return: the created preset as a :class:`.SBSPreset`
    """
    from pysbs import graph

    aPreset = graph.SBSPreset(aLabel=aLabel, aUsertags=aUsertags, aPresetInputs=[], aRefGraph=aParentGraph)
    return aPreset

@handle_exceptions()
def createCompFilterNode(aParentGraph, aFilter, aParameters = None, aInheritance = None):
    """
    createCompFilterNode(aParentGraph, aFilter, aParameters = None, aInheritance = None)
    Create a new compositing node filter with the given parameters.
    For a Bitmap or Svg node, use createResourceNode instead.

    :param aParentGraph: graph which will contain the created CompFilter node
    :param aFilter: type of filter to create
    :param aParameters: parameters of the filter node
    :param aInheritance: Inheritance of the parameters

    :type aParentGraph: :class:`.SBSGraph`
    :type aFilter: :class:`.FilterEnum` or str
    :type aParameters: dictionary in the format {parameterName(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
    :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional

    :return: The new :class:`.SBSCompNode` object
    """
    from pysbs import sbscommon
    from pysbs import compnode

    if aParameters is None: aParameters = {}
    if aInheritance is None: aInheritance = {}

    # Get the appropriate filter parameters
    aCompNodeDef = sbslibrary.getFilterDefinition(aFilter)

    # Create the SBSCompNode with a Filter implementation
    aNodeUID     = UIDGenerator.generateUID(aParentGraph)
    aCompFilter  = compnode.SBSCompFilter(aCompNodeDef.mIdentifier)
    aCompImpl    = compnode.SBSCompImplementation(aCompFilter = aCompFilter)
    aCompNode    = compnode.SBSCompNode(aUID = aNodeUID,
                                        aGUILayout = sbscommon.SBSGUILayout(),
                                        aCompImplementation = aCompImpl)

    # Set the parameters with their Inheritance
    for paramKey,paramValue in aParameters.items():
        aCompFilter.setParameterValue(aParameter = paramKey, aParamValue = paramValue,
                                      aRelativeTo = aInheritance[paramKey] if paramKey in aInheritance else None)

    # Set the Inheritance
    for paramKey,inheritValue in aInheritance.items():
        if paramKey not in aParameters and paramKey in aCompNodeDef.mInheritance:
            aDefaultParam = aCompNodeDef.getParameter(paramKey)
            aCompFilter.setParameterValue(aParameter = paramKey, aParamValue = aDefaultParam.mDefaultValue,
                                          aRelativeTo = inheritValue)

    # Deduce the output type of the node
    aForcedOutputType = None
    colorParam = aCompFilter.getParameterValue(sbsenum.CompNodeParamEnum.COLOR_MODE)
    if colorParam is not None:
        if int(colorParam) == sbsenum.ColorModeEnum.COLOR: aForcedOutputType = sbsenum.ParamTypeEnum.ENTRY_COLOR
        else                                             : aForcedOutputType = sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE

    # Create the CompOutput of the node with the appropriate output type
    for aFilterOutput in aCompNodeDef.mOutputs:
        aOutputUID = UIDGenerator.generateUID(aCompNode)
        if aForcedOutputType is not None:
            aType = aForcedOutputType
        elif aFilterOutput.mType == sbsenum.ParamTypeEnum.ENTRY_VARIANT:
            aType = sbsenum.ParamTypeEnum.ENTRY_COLOR
        else:
            aType = aFilterOutput.mType
        aCompOutput     = compnode.SBSCompOutput(aUID = aOutputUID, aCompType = str(aType))
        api_helpers.addObjectToList(aCompNode, 'mCompOutputs', aCompOutput)

    # In the case of a FxMap Filter, init its graph
    if aCompFilter.isAFxMap():
        aCompNode.initFxMapGraph()

    return aCompNode


@handle_exceptions()
def createResourceNode(aFilter,
                       aSBSDocument,
                       aParentGraph,
                       aResourcePath,
                       aParameters = None,
                       aInheritance = None,
                       aResourceGroup = 'Resources',
                       aCookedFormat = None,
                       aCookedQuality = None,
                       aAttributes = None,
                       aAutodetectImageParameters = False):
    """
    createResourceNode(aFilter, aSBSDocument, aParentGraph, aResourcePath, aParameters = None, aInheritance = None, aResourceGroup = 'Resources', aCookedFormat = None, aCookedQuality = None, aAttributes = None)
    Create a new 'bitmap' node using the provided resourcePath. Create the referenced resource if necessary.

    :param aFilter: Filter type: BITMAP or SVG
    :param aSBSDocument: reference document
    :param aParentGraph: graph which will contain the created Bitmap node
    :param aResourcePath: internal (*pkg:///MyGroup/MyResourceIdentifier*), relative (to the current package) or absolute path to the bitmap resource to use as resource
    :param aParameters: parameters of the Bitmap node
    :param aInheritance: Inheritance of the parameters
    :param aResourceGroup: SBSGroup or identifier of the group where the resource will be added (the group is created if necessary). \
    Default to 'Resources'. Put None to create the resource at the root of the package.
    :param aCookedFormat: resource bitmap format (JPEG/RAW). default value is RAW
    :param aCookedQuality: resource bitmap compression quality. default value is 0
    :param aAttributes: attributes of the resource
    :param aAutodetectImageParameters: Autodetect and set resolution and bitdepth for the bitmap. Default to False

    :type aFilter: :class:`.FilterEnum`
    :type aSBSDocument: :class:`.SBSDocument`
    :type aParentGraph: :class:`.SBSGraph`
    :type aResourcePath: str
    :type aParameters: dictionary in the format {parameterName(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
    :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
    :type aResourceGroup: :class:`.SBSGroup` or str, optional
    :type aCookedFormat: :class:`.BitmapFormatEnum`, optional
    :type aCookedQuality: float between 0 and 1, optional
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
    :type aAutodetectImageParameters: bool, optional

    :return: The new :class:`.SBSCompNode` object
    :raise: :class:`api_exceptions.SBSImpossibleActionError`
    """
    if aFilter != sbsenum.FilterEnum.BITMAP and aFilter != sbsenum.FilterEnum.SVG:
        raise SBSImpossibleActionError('A resource node is either a BITMAP filter or a SVG filter')

    if aParameters is None: aParameters = {}
    if aInheritance is None: aInheritance = {}


    # Check if the ?himself dependency already exists, otherwise add it
    if aSBSDocument.getHimselfDependency() is None:
       aSBSDocument.createHimselfDependency()

    if api_helpers.hasPkgPrefix(aResourcePath):
        # Get the resource from the package
        aResource = aSBSDocument.getObjectFromInternalPath(aResourcePath)

    else:
        # Check cooking values
        if aCookedQuality is not None:
            if python_helpers.isStringOrUnicode(aCookedQuality):
                aCookedQuality = float(aCookedQuality)
            aCookedQuality = max(min(aCookedQuality, 1.0), 0.0)

        if aFilter == sbsenum.FilterEnum.BITMAP:
            aResourceType = sbsenum.ResourceTypeEnum.BITMAP
            if aCookedFormat is not None and aCookedFormat != sbsenum.BitmapFormatEnum.RAW and aCookedFormat != sbsenum.BitmapFormatEnum.JPG:
                aCookedFormat = sbsenum.BitmapFormatEnum.RAW

        else:
            aResourceType = sbsenum.ResourceTypeEnum.SVG
            aCookedFormat = None

        # Create resource with external link ref
        aResource = createLinkedResource(aSBSDocument = aSBSDocument,
                                         aResourcePath = aResourcePath,
                                         aResourceTypeEnum = aResourceType,
                                         aResourceGroup = aResourceGroup,
                                         aAttributes = aAttributes,
                                         aCookedFormat = aCookedFormat,
                                         aCookedQuality = aCookedQuality)

    if not aResource:
        raise SBSImpossibleActionError('Failed to create the resource '+aResourcePath)

    # Autodetect image parameters if requested
    if aAutodetectImageParameters:
        if not freeimagebindings.HasFreeImage(aSBSDocument.mContext):
            log.warning('Freeimage not loaded, auto detection will be skipped')
        else:
            try:
                # Read image parameters
                width, height, colorMode, outputFormat = freeimagebindings.GetImageInformation(aResourcePath,
                                                                                               aSBSDocument.mContext)

                # Update output size
                if sbsenum.CompNodeParamEnum.OUTPUT_SIZE not in aParameters.keys():
                    aParameters[sbsenum.CompNodeParamEnum.OUTPUT_SIZE] = [width, height]
                    aInheritance[sbsenum.CompNodeParamEnum.OUTPUT_SIZE] = sbsenum.ParamInheritanceEnum.ABSOLUTE
                else:
                    log.warning('Output size provided as a parameter, skipping auto detection')

                # Update output format
                if sbsenum.CompNodeParamEnum.OUTPUT_FORMAT not in aParameters.keys():
                    aParameters[sbsenum.CompNodeParamEnum.OUTPUT_FORMAT] = outputFormat
                    aInheritance[sbsenum.CompNodeParamEnum.OUTPUT_FORMAT] = sbsenum.ParamInheritanceEnum.ABSOLUTE
                else:
                    log.warning('Output format provided as a parameter, skipping auto detection')

                # Update color mode
                if sbsenum.CompNodeParamEnum.COLOR_MODE not in aParameters.keys():
                    aParameters[sbsenum.CompNodeParamEnum.COLOR_MODE] = colorMode
                else:
                    log.warning('Color mode provided as a parameter, skipping auto detection')
            except IOError as e:
                # Log warning but don't send exception to the user,
                # This is a supported error state and it will fallback to the same behavior as
                # before this feature was introduced
                log.warning(e)

    # Create comp node filter bitmap
    aCompNode = createCompFilterNode(aParentGraph = aParentGraph,
                                     aFilter = aFilter,
                                     aParameters = aParameters,
                                     aInheritance = aInheritance)
    # Set the parameter *bitmap resource path* of the resource
    if aFilter == sbsenum.FilterEnum.BITMAP:    aParam = sbsenum.CompNodeParamEnum.BITMAP_RESOURCE_PATH
    else:                                       aParam = sbsenum.CompNodeParamEnum.SVG_RESOURCE_PATH
    aCompNode.setParameterValue(aParam, aResource.getPkgResourcePath())

    return aCompNode


@handle_exceptions()
def _resolveUsage(usage, usageData):
    from pysbs import graph
    if python_helpers.isStringOrUnicode(usage):
        aUsage = usage
    else:
        aUsage = sbslibrary.getUsage(usage)
    colorspace = usageData.get(sbsenum.UsageDataEnum.COLOR_SPACE, None)
    if colorspace is not None:
        colorspace = colorspace if python_helpers.isStringOrUnicode(colorspace) else sbslibrary.getColorSpace(
            colorspace)
    return graph.SBSUsage(aComponents=sbslibrary.getComponents(usageData.get(sbsenum.UsageDataEnum.COMPONENTS)),
                          aColorSpace=colorspace,
                          aName=aUsage)


@handle_exceptions()
def createOutputNode(aParentGraph,
                     aIdentifier,
                     aAttributes = None,
                     aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,
                     aMipmaps = None,
                     aUsages = None,
                     aGroup = None,
                     aVisibleIf = None):
    """
    createOutputNode(aParentGraph, aIdentifier, aAttributes = None, aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT, aMipmaps = None, aUsages = None, aGroup = None, aVisibleIf = None)
    Create a new compositing node output.
    Declare the new :class:`.SBSRootOutput` and :class:`.SBSGraphOutput`

    :param aParentGraph: graph which will contain the created Output node
    :param aIdentifier: output identifier
    :param aAttributes: attributes of the output node
    :param aOutputFormat: output format. default value is DEFAULT_FORMAT
    :param aMipmaps: default value is FULL_PYRAMID
    :param aUsages: usages of this output
    :param aGroup: GUI group of this output
    :param aVisibleIf: Condition of visibility of this output

    :type aParentGraph: :class:`.SBSGraph`
    :type aIdentifier: str
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
    :type aOutputFormat: :class:`.TextureFormatEnum`, optional
    :type aMipmaps: :class:`.MipmapEnum`, optional
    :type aUsages: dictionary in the format: {:class:`.UsageEnum` : {:class:`.UsageDataEnum` : string}, optional
    :type aGroup: str, optional
    :type aVisibleIf: str, optional

    :return: The new :class:`.SBSCompNode` object
    """
    from pysbs import sbscommon
    from pysbs import compnode
    from pysbs import graph

    # Create the compositing node of kind CompOutputBridge
    aNodeUID = UIDGenerator.generateUID(aParentGraph)
    aCompNode   = compnode.SBSCompNode(aUID = aNodeUID, aGUILayout = sbscommon.SBSGUILayout())

    aOutputUID  = UIDGenerator.generateUID(aCompNode)
    aCompOutput = compnode.SBSCompOutputBridge(aOutput = aOutputUID)
    aCompImpl   = compnode.SBSCompImplementation(aCompOutputBridge = aCompOutput)
    aCompNode.mCompImplementation = aCompImpl

    # Declare a new graph output, with the given
    outputUsages = None
    if aUsages is not None:
        outputUsages = [_resolveUsage(usg, usageDict) for usg, usageDict in aUsages.items()]
    aGraphOutput = graph.SBSGraphOutput(aIdentifier = aIdentifier,
                                        aUID        = aOutputUID,
                                        aUsages     = outputUsages,
                                        aGroup      = aGroup,
                                        aVisibleIf  = aVisibleIf)
    # Handle the attributes
    aUserTags = ''
    if aAttributes is not None:
        aUserTags = aAttributes.pop(sbsenum.AttributesEnum.UserTags, '')
        aGraphOutput.setAttributes(aAttributes)

    api_helpers.addObjectToList(aParentGraph, 'mGraphOutputs', aGraphOutput)

    # Declare the root output of the graph, considering the output format and mipmaps level
    if hasattr(aParentGraph, 'mRoot'):
        aRootOutput = graph.SBSRootOutput(aOutput  = aOutputUID,
                                          aFormat  = str(aOutputFormat),
                                          aMipmaps = str(aMipmaps) if aMipmaps is not None else None,
                                          aUserTag = aUserTags)
        api_helpers.addObjectToList(aParentGraph.mRoot, 'mRootOutputs', aRootOutput)

    return aCompNode


@handle_exceptions()
def createInputNode(aParentGraph,
                    aIdentifier,
                    aColorMode = sbsenum.ColorModeEnum.COLOR,
                    aAttributes = None,
                    aIsConnectable = True,
                    aUsages = None,
                    aSetAsPrimary = False,
                    aParameters = None,
                    aInheritance = None,
                    aGroup = None,
                    aVisibleIf = None):
    """
    createInputNode(aParentGraph, aIdentifier, aColorMode = sbsenum.ColorModeEnum.COLOR, aAttributes = None, aUsages = None, aSetAsPrimary = False, aParameters = None, aInheritance = None, aGroup = None, aVisibleIf = None)
    Create a new compositing node input with the appropriate color.
    Declare it as PrimaryInput if this is the first input node.
    Declare the new :class:`.SBSParamInput`

    :param aParentGraph: graph which will contain the created Output node
    :param aIdentifier: output identifier
    :param aColorMode: color or grayscale. Default is color
    :param aAttributes: attributes of the output node
    :param aUsages: usages of this output
    :param aSetAsPrimary: True to define this input as the PrimaryInput of the graph. Even if False, the input will be set as the PrimaryInput if this is the first input of the graph. Default to False
    :param aParameters: parameters of the input node
    :param aInheritance: Inheritance of the parameters
    :param aGroup: GUI group name. Can uses path with '/' separators.
    :param aVisibleIf: Condition of visibility of this input

    :type aParentGraph: :class:`.SBSGraph`
    :type aIdentifier: str
    :type aColorMode: :class:`.ColorModeEnum`, optional
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
    :type aUsages: dictionary in the format: {:class:`.UsageEnum` : {:class:`.UsageDataEnum` : string}, optional
    :type aSetAsPrimary: bool, optional
    :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
    :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
    :type aGroup: str, optional
    :type aVisibleIf: str, optional

    :return: The new :class:`.SBSCompNode` object
    """
    from pysbs import sbscommon
    from pysbs import compnode
    from pysbs import graph

    if aParameters is None: aParameters = {}
    if aInheritance is None: aInheritance = {}

    # Create the compositing node of kind CompInputBridge
    aNodeUID = UIDGenerator.generateUID(aParentGraph)
    aCompNode   = compnode.SBSCompNode(aUID = aNodeUID, aGUILayout = sbscommon.SBSGUILayout())

    aInputUID  = UIDGenerator.generateUID(aParentGraph)
    aCompInput = compnode.SBSCompInputBridge(aEntry = aInputUID)
    aCompImpl   = compnode.SBSCompImplementation(aCompInputBridge = aCompInput)
    aCompNode.mCompImplementation = aCompImpl

    # Get the definition of the input node parameters
    defaultParams = sbslibrary.getInputBridgeDefinition()

    # Set the parameters with their Inheritance
    for paramKey,paramValue in aParameters.items():
        aCompInput.setParameterValue(aParameter = paramKey, aParamValue = paramValue,
                                     aRelativeTo = aInheritance[paramKey] if paramKey in aInheritance else None)

    # Set the Inheritance
    for paramKey,inheritValue in aInheritance.items():
        if paramKey not in aParameters and paramKey in defaultParams.mInheritance:
            aDefaultParam = defaultParams.getParameter(paramKey)
            aCompInput.setParameterValue(aParameter = paramKey, aParamValue = aDefaultParam.mDefaultValue,
                                         aRelativeTo = inheritValue)

    # Declare a new graph param input, with the given attributes and usages
    inputUsages = None
    if aUsages is not None:
        inputUsages = [_resolveUsage(usg, usageDict) for usg, usageDict in aUsages.items()]

    aInputType = sbsenum.ParamTypeEnum.ENTRY_COLOR if aColorMode == sbsenum.ColorModeEnum.COLOR else sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE
    aParamInput = graph.SBSParamInput(aIdentifier    = aIdentifier,
                                      aUID           = aInputUID,
                                      aIsConnectable = "1" if aIsConnectable else "0",
                                      aType          = str(aInputType),
                                      aUsages        = inputUsages,
                                      aDefaultWidget = graph.SBSWidget(aName = '', aOptions = []),
                                      aGroup         = aGroup,
                                      aVisibleIf     = aVisibleIf)
    # Handle attributes
    if aAttributes is not None:
        aParamInput.setAttributes(aAttributes)

    api_helpers.addObjectToList(aParentGraph, 'mParamInputs', aParamInput)

    # Create the CompOutput of the node with the appropriate output type
    aInputDefaultParams = sbslibrary.getInputBridgeDefinition()
    for _ in aInputDefaultParams.mOutputs:
        aOutputUID      = UIDGenerator.generateUID(aCompNode)
        aCompOutput     = compnode.SBSCompOutput(aUID = aOutputUID, aCompType = str(aInputType))
        api_helpers.addObjectToList(aCompNode, 'mCompOutputs', aCompOutput)

    # Handle the primary input of the graph
    if aSetAsPrimary or aParentGraph.getPrimaryInput() is None:
        aParentGraph.setPrimaryInput(aInputUID)

    return aCompNode



@handle_exceptions()
def createCompInstanceNode(aParentGraph, aGraph, aDependency, aPath, aParameters = None, aInheritance = None):
    """
    createCompInstanceNode(aParentGraph, aGraph, aDependency, aPath, aParameters = None, aInheritance = None)
    Create a new compositing node instance with the given parameters.

    :param aParentGraph: graph which will contain the created comp instance node
    :param aGraph: graph to instantiate in the compositing node
    :param aDependency: dependency associated to the referenced object (himself or external)
    :param aPath: path of the graph definition
    :param aParameters: parameters of the filter node
    :param aInheritance: Inheritance of the parameters

    :type aParentGraph: :class:`.SBSGraph`
    :type aGraph: :class:`.SBSGraph`
    :type aDependency: :class:`.SBSDependency`
    :type aPath: str
    :type aParameters: dictionary in the format {parameterName(:class:`.CompNodeParamEnum`) : parameterValue(str)}
    :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}

    :return: The new :class:`.SBSCompNode` object
    """
    from pysbs import sbscommon
    from pysbs import compnode

    if aParameters is None: aParameters = {}
    if aInheritance is None: aInheritance = {}

    # Create the SBSCompNode with a Instance implementation
    aNodeUID      = UIDGenerator.generateUID(aParentGraph)
    aCompInstance = compnode.SBSCompInstance(aPath = aPath,
                                             aRefGraph = aGraph,
                                             aRefDependency = aDependency)
    aCompImpl     = compnode.SBSCompImplementation(aCompInstance = aCompInstance)
    aCompNode     = compnode.SBSCompNode(aUID = aNodeUID,
                                         aGUILayout = sbscommon.SBSGUILayout(),
                                         aCompImplementation = aCompImpl)

    aInstanceDefinition = aCompNode.getDefinition()

    # Set the parameters with their Inheritance
    for paramKey,paramValue in aParameters.items():
        aCompInstance.setParameterValue(aParameter = paramKey, aParamValue = paramValue,
                                        aRelativeTo = aInheritance[paramKey] if paramKey in aInheritance else None)

    # Set the Inheritance
    for paramKey, inheritValue in aInheritance.items():
        if paramKey not in aParameters and paramKey in aInstanceDefinition.mInheritance:
            aDefaultParam = aInstanceDefinition.getParameter(paramKey)
            aCompInstance.setParameterValue(aParameter=paramKey, aParamValue=aDefaultParam.mDefaultValue,
                                            aRelativeTo=inheritValue)

    # Create the node outputs and the comp instance output bridgings
    for aOutput in aGraph.getGraphOutputs():
        aOutputUID = UIDGenerator.generateUID(aCompNode)
        aOutputBridging = compnode.SBSOutputBridging(aUID = aOutputUID, aIdentifier = aOutput.mIdentifier)
        api_helpers.addObjectToList(aCompInstance, 'mOutputBridgings', aOutputBridging)

        aType = aGraph.getGraphOutputType(aOutputIdentifier = aOutput.mIdentifier)
        aCompOutput     = compnode.SBSCompOutput(aUID = aOutputUID, aCompType = str(aType))
        api_helpers.addObjectToList(aCompNode, 'mCompOutputs', aCompOutput)

    return aCompNode


@handle_exceptions()
def createMDLNode(aParentGraph, aImplementationKind,
                  aPath = None,
                  aParameters = None,
                  aCstAnnotations = None,
                  aCstIsExposed = False,
                  aCstName = None,
                  aCstValue = None,
                  aCstTypeModifier = None,
                  aInstanceOfGraph = None,
                  aInstanceDependency = None):
    """
    createMDLNode(aParentGraph, aPath, aParameters = None)
    Create a new MDL node with the given parameters.

    :param aParentGraph: graph which will contain the created MDL node
    :param aImplementationKind: kind of mdl node implementation to create
    :param aPath: mdl path of the node to create
    :param aParameters: parameters of the mdl node
    :param aCstAnnotations: for a constant: annotations of the mdl node
    :param aCstIsExposed: for a constant: defines if this constant is exposed as an input parameter of the graph
    :param aCstName: for a constant: name of the constant. If None, a name is affected by default using the constant type
    :param aCstValue: for a constant: value of the constant
    :param aCstTypeModifier: for a constant: type modifier to set. Default to 'auto'
    :param aInstanceOfGraph: for a Substance or MDL graph instance: the instantiated graph
    :param aInstanceDependency: for a Substance or MDL graph instance: the associated dependency

    :type aParentGraph: :class:`.MDLGraph`
    :type aImplementationKind: :class:`.MDLImplementationKindEnum`
    :type aPath: str, optional
    :type aParameters: dictionary in the format {parameterName(str) : parameterValue(str)}, optional
    :type aCstAnnotations: dictionary in the format {annotation(:class:`.MDLAnnotationEnum`),annotationValue(str)}, optional
    :type aCstIsExposed: bool, optional
    :type aCstName: str, optional
    :type aCstValue: any type, optional
    :type aCstTypeModifier: :class:`.MDLTypeModifierEnum`
    :type aInstanceOfGraph: :class:`.BaseGraph`
    :type aInstanceDependency: :class:`.SBSDependency`

    :return: The new :class:`.MDLNode` object
    :raise: :class:`.SBSImpossibleActionError`
    """
    from pysbs import sbscommon
    from pysbs import mdl
    from pysbs.mdl import mdlenum

    if aParameters is None: aParameters = {}
    if aCstAnnotations is None: aCstAnnotations = {}

    aMDLConstant = aMDLSelector = aMDLInstance = aMDLGraphInstance = aSBSInstance = aMDLPassThrough = None

    # MDL Constant
    if aImplementationKind == mdl.mdlenum.MDLImplementationKindEnum.CONSTANT:
        # Get the mdl type definition, and create the corresponding MDLOperands
        typeDef = mdl.MDLManager.getMDLTypeDefinition(aPath)
        if not typeDef:
            raise SBSImpossibleActionError("Failed to create MDL node, the type "+python_helpers.castStr(aPath)+" is not known by the MDL library")
        aOperand = typeDef.toMDLOperand(aName=aCstName)
        if aCstValue:
            aOperand.setValue(aCstValue)

        # Create the default annotations
        aAnnotationDefs = mdl.MDLManager.getConstantDefaultAnnotations(aTypePath=aPath, aExposed=aCstIsExposed)

        aCstTypeModifier = str(mdlenum.MDLTypeModifierEnum.AUTO) if aCstTypeModifier is None else str(aCstTypeModifier)

        aMDLConstant = mdl.MDLImplConstant(aIdentifier  = aOperand.mName,
                                           aOperands    = mdl.MDLOperands([aOperand]),
                                           aAnnotations = [annot.toMDLAnnotation() for annot in aAnnotationDefs],
                                           aTypeModifier= aCstTypeModifier)

        # Finalize the constant
        aMDLConstant.setExposed(aCstIsExposed)
        for annotKey,annotValue in aCstAnnotations.items():
            aMDLConstant.setAnnotation(aAnnotation = annotKey, aAnnotationValue = annotValue)

    # MDL Selector
    elif aImplementationKind == mdl.mdlenum.MDLImplementationKindEnum.SELECTOR:
        aMDLSelector = mdl.MDLImplSelector()

    # MDL Instance
    elif aImplementationKind == mdl.mdlenum.MDLImplementationKindEnum.MDL_INSTANCE:
        # Get the mdl instance definition
        nodeDef = mdl.MDLManager.getMDLNodeDefinition(aPath)
        if nodeDef is None:
            raise SBSImpossibleActionError("Failed to create MDL node, the node "+python_helpers.castStr(aPath)+" is not known by the MDL library")

        aOperands = nodeDef.getDefaultOperands()
        aMDLInstance = mdl.MDLImplMDLInstance(aPath=aPath, aOperands=mdl.MDLOperands(aOperands))

    # MDL Graph Instance
    elif aImplementationKind == mdl.mdlenum.MDLImplementationKindEnum.MDL_GRAPH_INSTANCE:
        aMDLGraphInstance = mdl.MDLImplMDLGraphInstance(aPath          = aPath,
                                                        aRefDependency = aInstanceDependency,
                                                        aRefGraph      = aInstanceOfGraph)
        # Get the mdl graph instance definition
        nodeDef = aMDLGraphInstance.getDefinition()
        if nodeDef is None:
            raise SBSImpossibleActionError("Failed to create MDL node, the node "+python_helpers.castStr(aPath)+" is not known by the MDL library")

        aMDLGraphInstance.mOperands = mdl.MDLOperands(nodeDef.getDefaultOperands(aCheckType=False))

    # Substance Graph Instance
    elif aImplementationKind == mdl.mdlenum.MDLImplementationKindEnum.SBS_INSTANCE:
        aSBSInstance = mdl.MDLImplSBSInstance(aPath          = aPath,
                                              aRefDependency = aInstanceDependency,
                                              aRefGraph      = aInstanceOfGraph)

    # Passthrough node
    elif aImplementationKind == mdl.mdlenum.MDLImplementationKindEnum.PASSTHROUGH:
        aMDLPassThrough = mdl.MDLImplPassThrough()

    # Create the MDLNode with the appropriate implementation
    aNodeUID = UIDGenerator.generateUID(aParentGraph)
    aMDLImpl = mdl.MDLImplementation(aImplConstant         = aMDLConstant,
                                     aImplSelector         = aMDLSelector,
                                     aImplMDLInstance      = aMDLInstance,
                                     aImplMDLGraphInstance = aMDLGraphInstance,
                                     aImplSBSInstance      = aSBSInstance,
                                     aImplPassThrough      = aMDLPassThrough)
    aMDLNode = mdl.MDLNode(aUID=aNodeUID, aMDLImplementation=aMDLImpl, aGUILayout=sbscommon.SBSGUILayout())

    # Set the parameters
    for paramPath,paramValue in aParameters.items():
        aMDLNode.setParameterValue(aParameter = paramPath, aParamValue = paramValue)

    return aMDLNode



@handle_exceptions()
def createLinkedResource(aSBSDocument,
                         aResourcePath,
                         aResourceTypeEnum = sbsenum.ResourceTypeEnum.BITMAP,
                         aResourceGroup = 'Resources',
                         aIdentifier = None,
                         aAttributes = None,
                         aCookedFormat = None,
                         aCookedQuality = None,
                         isUDIM = False,
                         aForceNew = False,
                         isRelToPackage = False):
    """
    createLinkedResource(aSBSDocument, aResourcePath, aResourceTypeEnum = sbsenum.ResourceTypeEnum.BITMAP, aResourceGroup = 'Resources', aIdentifier = None, aAttributes = None, aCookedFormat = None, aCookedQuality = None, isUDIM = False, aForceNew = False)
    Process the given resource: Create a new SBSResource in the folder ResourceGroup if the resource is not already in.
    Create the SBSGroup ResourceGroup if necessary.

    :param aSBSDocument: reference document
    :param aResourcePath: relative or absolute path to the resource
    :param aResourceTypeEnum: type of the resource (BITMAP/SVG/SCENE). Default is BITMAP
    :param aResourceGroup: :class:`.SBSGroup` or identifier of the group where the resource will be added (the group is created if necessary). \
    'Resources' by default. None to put the resource at the root of the package.
    :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
    :param aAttributes: attributes of the resource
    :param aCookedFormat: bitmap format (JPEG/RAW) (only for BITMAP). Default value is RAW
    :param aCookedQuality: bitmap compression quality (only for BITMAP and SVG). Default value is 0
    :param isUDIM: (only for SCENE) True to use UDIMs on this scene resource. Default to False
    :param aForceNew: True to force the resource creation even if it is already included in the package. Default to False
    :param isRelToPackage: the given path is relative, if isRelToPackage is True it is relative to the sbs package otherwise it is relative to cwd.

    :type aSBSDocument: :class:`.SBSDocument`
    :type aResourcePath: str
    :type aResourceTypeEnum: :class:`.ResourceTypeEnum`
    :type aResourceGroup: :class:`.SBSGroup` or str, optional
    :type aIdentifier: str, optional
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
    :type aCookedFormat: :class:`.BitmapFormatEnum`, optional
    :type aCookedQuality: float between 0 and 1, optional
    :type isUDIM: bool, optional
    :type aForceNew: bool, optional
    :type isRelToPackage: bool, optional

    :return: The new :class:`.SBSResource` object
    """
    aAliasMgr = aSBSDocument.mContext.getUrlAliasMgr()
    aResolvedPath = os.path.abspath(aResourcePath) if not isRelToPackage and not aAliasMgr.getAliasInPath(aResourcePath) else aResourcePath
    aFileAbsPath= aAliasMgr.toAbsPath(aResolvedPath, aSBSDocument.mDirAbsPath)
    aRelPath    = aAliasMgr.toRelPath(aResolvedPath, aSBSDocument.mDirAbsPath)

    # Check if the Resources group already exists, otherwise create it
    parentContent = aSBSDocument.getOrCreateGroup(aResourceGroup) if aResourceGroup is not None else aSBSDocument

    aResource = __createLinkedResource(aSBSDocument      = aSBSDocument,
                                       aFileAbsPath      = aFileAbsPath,
                                       aFileRelPath      = aRelPath,
                                       aResourceTypeEnum = aResourceTypeEnum,
                                       aParentContent    = parentContent,
                                       aIdentifier       = aIdentifier,
                                       aAttributes       = aAttributes,
                                       aCookedFormat     = aCookedFormat,
                                       aCookedQuality    = aCookedQuality,
                                       isUDIM            = isUDIM,
                                       aForceNew         = aForceNew)

    # PSD resource case: create one subgroup of resource, and add each layer as a new bitmap resource
    if aResource.mFormat.lower() == 'psd':
        psdLayers = psdparser.getLayers(aContext = aSBSDocument.mContext, aPsdFileAbsPath = aResource.mFileAbsPath)
        if psdLayers:
            # First create a new group for the psd resources
            aPsdGroup = aSBSDocument.createGroup(aGroupIdentifier = aResource.mIdentifier+'_Resources', aParentFolder = aResourceGroup)

            # Create a resource for each psd resource
            for aLayer in reversed(psdLayers):
                layerFilename = aLayer.mName+'.'+aLayer.mFormat
                __createLinkedResource(aSBSDocument      = aSBSDocument,
                                       aFileAbsPath      = os.path.join(aResource.mFileAbsPath, layerFilename),
                                       aFileRelPath      = os.path.join(aRelPath, layerFilename),
                                       aResourceTypeEnum = sbsenum.ResourceTypeEnum.BITMAP,
                                       aParentContent    = aPsdGroup,
                                       aIdentifier       = aLayer.mName,
                                       aAttributes       = None,
                                       aCookedFormat     = aCookedFormat,
                                       aCookedQuality    = aCookedQuality,
                                       isUDIM            = isUDIM,
                                       aForceNew         = aForceNew)
    return aResource


@handle_exceptions()
def __createLinkedResource(aSBSDocument,
                           aFileRelPath,
                           aFileAbsPath,
                           aResourceTypeEnum,
                           aParentContent,
                           aIdentifier,
                           aAttributes,
                           aCookedFormat,
                           aCookedQuality,
                           isUDIM,
                           aForceNew):
    """
    __createLinkedResource(aSBSDocument, aFileRelPath, aFileAbsPath, aResourceTypeEnum, aResourceGroup, aIdentifier, aAttributes, aCookedFormat, aCookedQuality, isUDIM, aForceNew)
    Process the given resource: Create a new SBSResource in the folder ResourceGroup if the resource is not already in.

    :param aSBSDocument: reference document
    :param aFileRelPath: relative path to the resource
    :param aFileAbsPath: absolute path of the resource
    :param aResourceTypeEnum: type of the resource (BITMAP/SVG/SCENE).
    :param aParentContent: :class:`.SBSGroup` or :class:`.SBSDocument` where the resource will be added.
    :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
    :param aAttributes: attributes of the resource
    :param aCookedFormat: bitmap format (JPEG/RAW) (only for BITMAP).
    :param aCookedQuality: bitmap compression quality (only for BITMAP and SVG).
    :param isUDIM: (only for SCENE) True to use UDIMs on this scene resource.
    :param aForceNew: True to force the resource creation even if it is already included in the package.

    :type aSBSDocument: :class:`.SBSDocument`
    :type aFileRelPath: str
    :type aFileAbsPath: str
    :type aResourceTypeEnum: :class:`.ResourceTypeEnum`
    :type aParentContent: :class:`.SBSGroup` or :class:`.SBSDocument`
    :type aIdentifier: str
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}
    :type aCookedFormat: :class:`.BitmapFormatEnum`
    :type aCookedQuality: float between 0 and 1
    :type isUDIM: bool
    :type aForceNew: bool

    :return: The new :class:`.SBSResource` object
    """
    from pysbs import substance

    # Create the resource
    aFilename, aExtension = api_helpers.splitExtension(aFileAbsPath)
    resIdentifier = aIdentifier if aIdentifier is not None else aFilename
    resIdentifier = api_helpers.formatIdentifier(resIdentifier) if resIdentifier != '' else 'Untitled_Resource'

    if not substance.SBSResource.isAllowedExtension(aResourceTypeEnum, aExtension):
        raise SBSImpossibleActionError('File extension ('+aExtension+') not supported for this kind of resource ('+
                                       sbslibrary.getResourceTypeName(aResourceTypeEnum)+')')

    resourceClass = substance.SBSResourceScene if aResourceTypeEnum == sbsenum.ResourceTypeEnum.SCENE else substance.SBSResource
    aResource = resourceClass(aIdentifier    = resIdentifier,
                              aUID           = UIDGenerator.generateUID(aSBSDocument),
                              aType          = sbslibrary.getResourceTypeName(aResourceTypeEnum),
                              aFormat        = aExtension[1:],
                              aFilePath      = aFileRelPath,
                              aCookedFormat  = str(aCookedFormat) if aCookedFormat is not None else None,
                              aCookedQuality = str(aCookedQuality) if aCookedQuality is not None else None,
                              aFileAbsPath   = aFileAbsPath,
                              aRefDocument   = aSBSDocument)

    if resourceClass == substance.SBSResourceScene:
        if isUDIM:
            aResource.mIsUdim = api_helpers.formatValueForTypeStr(isUDIM, sbsenum.ParamTypeEnum.BOOLEAN)
        aResource.mSceneMaterialMap = [
            substance.SBSSceneMaterialMapEntry(aUVSetMaterialMapList=[
                substance.SBSUVSetMaterialMap(aEntries=[
                    substance.SBSUVSetMaterialMapEntry(aUVTiles='all', aMaterial=substance.SBSUVSetMaterial())])])]

    if aResourceTypeEnum == sbsenum.ResourceTypeEnum.BITMAP:
        if isUDIM:
            aResource.mFileAbsPath = api_helpers.convertUVTileToUdimPattern(aResource.mFileAbsPath)
            aResource.mFilePath = api_helpers.convertUVTileToUdimPattern(aResource.mFileAbsPath)
            aResource.mIdentifier = api_helpers.formatIdentifier(api_helpers.splitExtension(aResource.mFileAbsPath)[0]) if aResource.mIdentifier == aFilename else aResource.mIdentifier

    # Handle attributes
    if aAttributes is not None:
        aResource.setAttributes(aAttributes)

    # Check if this resource already exists in the package => return it directly
    if not aForceNew:
        existingRes = aSBSDocument.getSBSResourceFromPath(aPath=aResource.mFileAbsPath, isLinkedResource=True)
        if existingRes is not None:
            return existingRes

    # Ensure having a unique identifier
    if isinstance(aParentContent, substance.SBSGroup):
        internalPath = aSBSDocument.getSBSGroupInternalPath(aParentContent.mUID) + '/' + aResource.mIdentifier
    else:
        internalPath = api_helpers.getPkgPrefix() + aResource.mIdentifier
    if aSBSDocument.getObjectFromInternalPath(internalPath) is not None:
        aResource.mIdentifier = aParentContent.getContent().computeUniqueIdentifier(aResource.mIdentifier, aSuffixId = 1)

    # Register the new resource and return it
    memberName = 'mResourcesScene' if isinstance(aResource, substance.SBSResourceScene) else 'mResources'
    api_helpers.addObjectToList(aParentContent.getContent(), memberName, aResource)

    return aResource


@handle_exceptions()
def createImportedBitmap(aSBSDocument,
                         aResourcePath,
                         aResourceGroup = 'Resources',
                         aIdentifier = None,
                         aAttributes = None,
                         aCookedFormat = None,
                         aCookedQuality = None):
    """
    createImportedBitmap(aSBSDocument, aResourcePath, aResourceGroup = 'Resources',  aIdentifier = None, aAttributes = None, aCookedFormat = None, aCookedQuality = None)
    Process the given resource: Create a new SBSResource in the folder ResourceGroup if the resource is not already in.
    Create the SBSGroup ResourceGroup if necessary.

    :param aSBSDocument: reference document
    :param aResourcePath: relative or absolute path to the resource
    :param aResourceGroup: :class:`.SBSGroup` or identifier of the group where the resource will be added (the group is created if necessary). \
    'Resources' by default. Put None to create the resource at the root of the package.
    :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
    :param aAttributes: attributes of the resource
    :param aCookedFormat: bitmap format (JPEG/RAW) (only for BITMAP). Default value is RAW
    :param aCookedQuality: bitmap compression quality (only for BITMAP and SVG). Default value is 0

    :type aSBSDocument: :class:`.SBSDocument`
    :type aResourcePath: str
    :type aResourceGroup: :class:`.SBSGroup` or str, optional
    :type aIdentifier: str, optional
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
    :type aCookedFormat: :class:`.BitmapFormatEnum`, optional
    :type aCookedQuality: float between 0 and 1, optional

    :return: The new :class:`.SBSResource` object
    """
    # Check file
    aFileAbsPath= aSBSDocument.mContext.getUrlAliasMgr().toAbsPath(aResourcePath, aSBSDocument.mDirAbsPath)
    if not os.path.exists(aFileAbsPath):
        raise SBSImpossibleActionError('Failed to import the resource '+aFileAbsPath+', it does not exist on disk')

    # Get or create the physical folder where the initial resource file must be copied to
    aResourceFolderName = os.path.splitext(os.path.basename(aSBSDocument.mFileAbsPath))[0] + '.resources'
    aFolderPath = os.path.join(aSBSDocument.mDirAbsPath, aResourceFolderName)
    try:
        os.makedirs(aFolderPath)
    except OSError:
        if not os.path.isdir(aFolderPath):
            raise SBSImpossibleActionError('Failed to create the resource directory '+aFolderPath)

    # Check if the Resources group already exists, otherwise create it
    parentContent = aSBSDocument.getOrCreateGroup(aResourceGroup) if aResourceGroup is not None else aSBSDocument

    resIdentifier,aExtension = api_helpers.splitExtension(aFileAbsPath)

    # Particular case of a psd resource: extract the composite resource and each layer into the resource folder
    if aExtension.lower() == '.psd':
        compositePath = psdparser.extractCompositeTo(aContext=aSBSDocument.mContext, aPsdFileAbsPath=aFileAbsPath, aDestinationFolder=aFolderPath)
        aFilename, aExtension = api_helpers.splitExtension(compositePath)
        aNewFilename = api_helpers.buildUniqueFilePart(6) + '-' + aFilename[:-4] + aExtension
        aNewPath = os.path.join(os.path.dirname(compositePath), aNewFilename)
        os.rename(compositePath, aNewPath)

        aPsdResource = __createImportedResource(aSBSDocument  = aSBSDocument,
                                                aFileAbsPath  = aNewPath,
                                                aFileRelPath  = aSBSDocument.mContext.getUrlAliasMgr().toRelPath(aNewPath, aSBSDocument.mDirAbsPath),
                                                aResourceType = sbsenum.ResourceTypeEnum.BITMAP,
                                                aParentContent= parentContent,
                                                aIdentifier   = aIdentifier if aIdentifier is not None else resIdentifier,
                                                aAttributes   = aAttributes,
                                                aCookedFormat = aCookedFormat,
                                                aCookedQuality= aCookedQuality)

        psdLayers = psdparser.getLayers(aContext = aSBSDocument.mContext, aPsdFileAbsPath = aFileAbsPath)
        if psdLayers:
            # First create a new group for the psd resources
            aPsdGroup = aSBSDocument.createGroup(aGroupIdentifier = aPsdResource.mIdentifier+'_Resources', aParentFolder = aResourceGroup)

            # Create a resource for each psd resource
            for aLayer in reversed(psdLayers):
                layerPath = psdparser.extractLayerTo(aContext=aSBSDocument.mContext, aPsdFileAbsPath=aFileAbsPath, aLayer=aLayer, aDestinationFolder=aFolderPath)

                aNewFilename = api_helpers.buildUniqueFilePart(6) + '-' + aLayer.mName + '.' + aLayer.mFormat
                aNewPath = os.path.join(os.path.dirname(layerPath), aNewFilename)
                os.rename(layerPath, aNewPath)

                __createImportedResource(aSBSDocument  = aSBSDocument,
                                         aFileAbsPath  = aNewPath,
                                         aFileRelPath  = aSBSDocument.mContext.getUrlAliasMgr().toRelPath(aNewPath, aSBSDocument.mDirAbsPath),
                                         aResourceType = sbsenum.ResourceTypeEnum.BITMAP,
                                         aParentContent= aPsdGroup,
                                         aIdentifier   = aLayer.mName,
                                         aAttributes   = aAttributes,
                                         aCookedFormat = aCookedFormat,
                                         aCookedQuality= aCookedQuality)
            return aPsdResource

    # Other bitmap format
    else:
        # Build external resource destination path
        aResourceFileName = os.path.basename(aFileAbsPath)
        aExternalCopyPath = aResourceFolderName + '/' + api_helpers.buildUniqueFilePart(6) + '-' + aResourceFileName
        aExternalCopyAbsPath = aSBSDocument.mContext.getUrlAliasMgr().toAbsPath(aExternalCopyPath, aSBSDocument.mDirAbsPath)

        # Copy the resource
        try:
            shutil.copyfile(aFileAbsPath, aExternalCopyAbsPath)
        except:
            raise SBSImpossibleActionError('Failed to copy '+aFileAbsPath+' to '+aExternalCopyAbsPath)

        return __createImportedResource(aSBSDocument  = aSBSDocument,
                                        aFileAbsPath  = aExternalCopyAbsPath,
                                        aFileRelPath  = aExternalCopyPath,
                                        aResourceType = sbsenum.ResourceTypeEnum.BITMAP,
                                        aParentContent= parentContent,
                                        aIdentifier   = aIdentifier,
                                        aAttributes   = aAttributes,
                                        aCookedFormat = aCookedFormat,
                                        aCookedQuality= aCookedQuality)


@handle_exceptions()
def createImportedResource(aSBSDocument,
                           aResourceTypeEnum,
                           aResourcePath,
                           aResourceGroup = 'Resources',
                           aIdentifier = None,
                           aAttributes = None):
    """
    createImportedResource(aSBSDocument, aResourceTypeEnum, aResourcePath, aResourceGroup = 'Resources', aIdentifier = None, aAttributes = None)
    Process the given resource (font, light profile or bsdf measurement): Create a new SBSResource in the folder ResourceGroup if the resource is not already in.
    Create the SBSGroup ResourceGroup if necessary.

    :param aSBSDocument: reference document
    :param aResourceTypeEnum: resource kind, among FONT/LIGHT_PROFILE/M_BSDF
    :param aResourcePath: relative or absolute path to the resource
    :param aResourceGroup: :class:`.SBSGroup` or identifier of the group where the resource will be added (the group is created if necessary).\
    Default to 'Resources'. Put None to create the resource at the root of the package.
    :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
    :param aAttributes: attributes of the resource

    :type aSBSDocument: :class:`.SBSDocument`
    :type aResourceTypeEnum: :class:`.ResourceKindEnum`
    :type aResourcePath: str
    :type aResourceGroup: :class:`.SBSGroup` or str, optional
    :type aIdentifier: str, optional
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional

    :return: The new :class:`.SBSResource` object
    """
    if aResourceTypeEnum not in [sbsenum.ResourceTypeEnum.FONT,sbsenum.ResourceTypeEnum.M_BSDF,sbsenum.ResourceTypeEnum.LIGHT_PROFILE]:
        raise SBSImpossibleActionError('The method createImportedResource() can be used only for a resource of kind Font, Light or BSDF measurement.')

    # Check file
    aFileAbsPath= aSBSDocument.mContext.getUrlAliasMgr().toAbsPath(aResourcePath, aSBSDocument.mDirAbsPath)
    if not os.path.exists(aFileAbsPath):
        raise SBSImpossibleActionError('Failed to import the resource '+aFileAbsPath+', it does not exist on disk')

    # Get or create the physical folder where the initial resource file must be copied to
    aResourceFolderName = os.path.splitext(os.path.basename(aSBSDocument.mFileAbsPath))[0] + '.resources'
    aFolderPath = os.path.join(aSBSDocument.mDirAbsPath, aResourceFolderName)
    try:
        os.makedirs(aFolderPath)
    except OSError:
        if not os.path.isdir(aFolderPath):
            raise SBSImpossibleActionError('Failed to create the resource directory '+aFolderPath)

    # Check if the Resources group already exists, otherwise create it
    parentContent = aSBSDocument.getOrCreateGroup(aResourceGroup) if aResourceGroup is not None else aSBSDocument

    # Build external resource destination path
    aResourceFileName = os.path.basename(aFileAbsPath)
    if aIdentifier is None:
        aIdentifier = api_helpers.splitExtension(aResourceFileName)[0]

    aResourceFileName = api_helpers.buildUniqueFilePathWithPrefix(aFolderPath, aResourceFileName)
    aExternalCopyPath = aResourceFolderName + '/' + aResourceFileName
    aExternalCopyAbsPath = os.path.join(aFolderPath, aResourceFileName)

    # Copy the resource
    try:
        shutil.copyfile(aFileAbsPath, aExternalCopyAbsPath)
    except:
        raise SBSImpossibleActionError('Failed to copy '+aFileAbsPath+' to '+aExternalCopyAbsPath)

    return __createImportedResource(aSBSDocument   = aSBSDocument,
                                    aFileAbsPath   = aExternalCopyAbsPath,
                                    aFileRelPath   = aExternalCopyPath,
                                    aResourceType  = aResourceTypeEnum,
                                    aParentContent = parentContent,
                                    aIdentifier    = aIdentifier,
                                    aAttributes    = aAttributes)


@handle_exceptions()
def __createImportedResource(aSBSDocument,
                             aFileAbsPath,
                             aFileRelPath,
                             aResourceType,
                             aParentContent,
                             aIdentifier=None,
                             aAttributes=None,
                             aCookedFormat=None,
                             aCookedQuality=None):
    """
    __createImportedResource(aSBSDocument, aFileAbsPath, aFileRelPath, aResourceType, aResourceGroup, aIdentifier, aAttributes = None, aCookedFormat = None, aCookedQuality = None)
    Process the given resource: Create a new SBSResource in the folder ResourceGroup if the resource is not already in.

    :param aSBSDocument: reference document
    :param aFileAbsPath: absolute path to the resource
    :param aFileRelPath: relative path to the resource
    :param aResourceType: the kind of resource
    :param aParentContent: :class:`.SBSGroup` or :class:`.SBSDocument` where the resource will be added.
    :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
    :param aAttributes: attributes of the resource
    :param aCookedFormat: bitmap format (JPEG/RAW) (only for BITMAP). Default value is RAW
    :param aCookedQuality: bitmap compression quality (only for BITMAP and SVG). Default value is 0

    :type aSBSDocument: :class:`.SBSDocument`
    :type aFileAbsPath: str
    :type aFileRelPath: str
    :type aResourceType: :class:`.ResourceTypeEnum`
    :type aParentContent: :class:`.SBSGroup` or :class:`.SBSDocument`
    :type aIdentifier: str, optional
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
    :type aCookedFormat: :class:`.BitmapFormatEnum`, optional
    :type aCookedQuality: float between 0 and 1, optional

    :return: The new :class:`.SBSResource` object
    """
    from pysbs import substance

    aFileRelPath = aFileRelPath.replace('\\', '/')

    # Create a Source object
    aExternalCopy = substance.resource.SBSSourceExternalCopy(aFilename=aFileRelPath)
    aSource = substance.resource.SBSSource(aExternalCopy=aExternalCopy)

    # Create the resource
    aFilename, aExtension = api_helpers.splitExtension(aFileAbsPath)
    resIdentifier = aIdentifier if aIdentifier is not None else aFilename
    resIdentifier = api_helpers.formatIdentifier(resIdentifier) if resIdentifier != '' else 'Untitled_Resource'
    aFormat = aExtension[1:].upper() if aResourceType == sbsenum.ResourceTypeEnum.BITMAP else aExtension[1:]

    aResource = substance.SBSResource(aIdentifier   = aParentContent.getContent().computeUniqueIdentifier(resIdentifier),
                                      aUID          = UIDGenerator.generateUID(aSBSDocument),
                                      aType         = sbslibrary.getResourceTypeName(aResourceType),
                                      aFormat       = aFormat,
                                      aFilePath     = aFileRelPath,
                                      aSource       = aSource,
                                      aCookedFormat = str(aCookedFormat) if aCookedFormat is not None else None,
                                      aCookedQuality= str(aCookedQuality) if aCookedQuality is not None else None,
                                      aFileAbsPath  = aFileAbsPath,
                                      aRefDocument  = aSBSDocument)

    # Handle attributes
    if aAttributes:
        aResource.setAttributes(aAttributes)

    # Register the new resource and return it
    api_helpers.addObjectToList(aParentContent.getContent(), 'mResources', aResource)
    return aResource


@handle_exceptions()
def createEmbeddedSVG(aSBSDocument,
                      aResourcePath,
                      aResourceGroup = 'Resources',
                      aIdentifier = None,
                      aAttributes = None,
                      aCookedQuality = None):
    """
    createEmbeddedSVG(aSBSDocument, aResourcePath, aResourceGroup = 'Resources',  aIdentifier = None, aAttributes = None, aCookedQuality = None)
    Process the given resource: Create a new SBSResource in the folder ResourceGroup if the resource is not already in.
    Create the SBSGroup ResourceGroup if necessary.
    Create the dependency '?himself' if necessary.

    :param aSBSDocument: reference document
    :param aResourcePath: relative or absolute path to the resource
    :param aResourceGroup: :class:`.SBSGroup` or identifier of the group where the resource will be added (the group is created if necessary).\
    Default to 'Resources'. Put None to create the resource at the root of the package.
    :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
    :param aAttributes: attributes of the resource
    :param aCookedQuality: bitmap compression quality (only for BITMAP and SVG). Default value is 0

    :type aSBSDocument: :class:`.SBSDocument`
    :type aResourcePath: str
    :type aResourceGroup: :class:`.SBSGroup` or str, optional
    :type aIdentifier: str, optional
    :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
    :type aCookedQuality: float between 0 and 1, optional

    :return: The new :class:`.SBSResource` object
    """
    from pysbs import substance

    aFileAbsPath= aSBSDocument.mContext.getUrlAliasMgr().toAbsPath(aResourcePath, aSBSDocument.mDirAbsPath)
    aRelPath    = aSBSDocument.mContext.getUrlAliasMgr().toRelPath(aResourcePath, aSBSDocument.mDirAbsPath)

    # Build external resource destination path
    aResourceFileName = os.path.basename(aFileAbsPath)
    aFilename, aExtension = api_helpers.splitExtension(aResourceFileName)

    # Check extension
    if not substance.SBSResource.isAllowedExtension(sbsenum.ResourceTypeEnum.SVG, aExtension):
        raise SBSImpossibleActionError('File extension ('+aExtension+') not supported for this kind of resource ('+
                                       sbslibrary.getResourceTypeName(sbsenum.ResourceTypeEnum.SVG)+')')

    # Check if the Resources group already exists, otherwise create it
    parentContent = aSBSDocument.getOrCreateGroup(aResourceGroup) if aResourceGroup is not None else aSBSDocument

    # Get SVG content
    aDataLength, base64SVGData = __getBase64CompressedContent(aFileAbsPath, aBinaryFile=False)

    # Create a Source object
    aBinEmbedded = substance.resource.SBSSourceBinembedded(aDatalength=str(aDataLength), aStrdata=base64SVGData)
    aSource = substance.resource.SBSSource(aBinEmbedded=aBinEmbedded)

    # Create the resource
    resIdentifier = aIdentifier if aIdentifier is not None else aFilename
    resIdentifier = api_helpers.formatIdentifier(resIdentifier)

    aResource = substance.SBSResource(aIdentifier    = parentContent.getContent().computeUniqueIdentifier(resIdentifier),
                                      aUID           = UIDGenerator.generateUID(aSBSDocument),
                                      aType          = sbslibrary.getResourceTypeName(sbsenum.ResourceTypeEnum.SVG),
                                      aFormat        = aExtension[1:],
                                      aFilePath      = aRelPath,
                                      aSource        = aSource,
                                      aCookedQuality = str(aCookedQuality) if aCookedQuality is not None else None,
                                      aFileAbsPath   = aFileAbsPath,
                                      aRefDocument   = aSBSDocument)

    # Handle attributes
    if aAttributes is not None:
        aResource.setAttributes(aAttributes)

    # Register the new resource and return it
    api_helpers.addObjectToList(parentContent.getContent(), 'mResources', aResource)
    return aResource


@handle_exceptions()
def createFunctionNode(aSBSDynamicValue, aFunction, aParameters = None):
    """
    createFunctionNode(aSBSDynamicValue, aFunction, aParameters = None)
    Create a new function node (SBSParamNode) with the given parameters.

    :param aSBSDynamicValue: the dynamic value which will contain the created ParamNode
    :param aFunction: type of function to create
    :param aParameters: parameters of the function node

    :type aSBSDynamicValue: :class:`.SBSDynamicValue`
    :type aFunction: :class:`.FunctionEnum` or str
    :type aParameters: dictionary in the format {parameterName(:class:`.FunctionEnum`) : parameterValue(str)}

    :return: The new :class:`.SBSParamNode` object
    """
    from pysbs import sbscommon
    from pysbs import params

    if aParameters is None: aParameters = {}

    # Get the appropriate filter parameters
    aFunctionDefaultParams = sbslibrary.getFunctionDefinition(aFunction)

    # Create the SBSParamNode
    aNodeUID = UIDGenerator.generateUID(aSBSDynamicValue)
    aParamNode = params.SBSParamNode(aUID = aNodeUID,
                                     aFunction = aFunctionDefaultParams.mIdentifier,
                                     aType = str(aFunctionDefaultParams.mOutputs[0].mType),
                                     aGUILayout = sbscommon.SBSGUILayout())

    # Set the function parameters
    if aFunctionDefaultParams.mFunctionDatas:
        if not aParameters:
            defaultParam = aFunctionDefaultParams.mFunctionDatas[0]
            aParamNode.setParameterValue(defaultParam.mParameter, defaultParam.mDefaultValue)
        else:
            for aParam in aParameters.items():
                aParamNode.setParameterValue(aParam[0], aParam[1])

    return aParamNode


@handle_exceptions()
def createFunctionInstanceNode(aSBSDynamicValue, aFunction, aPath, aDependency):
    """
    createFunctionInstanceNode(aSBSDynamicValue, aFunction, aPath, aDependency)
    Create a new function node instance of the given function, and set the parameters.

    :param aSBSDynamicValue: the dynamic value which will contain the created ParamNode
    :param aFunction: the function that will be instantiated with the instance node
    :param aPath: path of the function definition
    :param aDependency: dependency associated to the referenced object (himself or external)

    :type aSBSDynamicValue: :class:`.SBSDynamicValue`
    :type aFunction: graph.SBSFunction
    :type aPath: str
    :param aDependency: :class:`.SBSDependency`

    :return: The new :class:`.SBSParamNode` object
    """
    from pysbs import sbscommon
    from pysbs import params

    # Create the SBSCompNode with a Instance implementation
    aNodeUID  = UIDGenerator.generateUID(aSBSDynamicValue)
    aInstanceNodeIdentifier = sbslibrary.getFunctionDefinition(sbsenum.FunctionEnum.INSTANCE).mIdentifier
    aType = aFunction.mType if aFunction.mType else sbsenum.TypeMasksEnum.FUNCTION_ALL

    aParamNode = params.SBSParamNode(aUID = aNodeUID,
                                     aFunction = aInstanceNodeIdentifier,
                                     aType = str(aType),
                                     aGUILayout = sbscommon.SBSGUILayout(),
                                     aRefFunction = aFunction,
                                     aRefDependency = aDependency)

    # Set the function parameters: the path to the function
    aParamNode.setParameterValue(aInstanceNodeIdentifier, aPath)

    return aParamNode


@handle_exceptions()
def createIterationOnPattern(aParentObject,
                             aNbIteration,
                             aNodeUIDs,
                             aNodeUIDs_NextPattern = None,
                             aForceRandomSeed = False,
                             aIncrementIteration = False,
                             aGUIOffset = None):
    """
    createIterationOnPattern(aParentObject, aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern = None, aForceRandomSeed = False, aIncrementIteration = False, aGUIOffset = None)
    | Duplicate NbIteration times the given pattern of compositing nodes, and connect each pattern with the previous one
        to create this kind of connection:
    | Pattern -> Pattern_1 -> Pattern_2 -> ... -> Pattern_N
    | It allows to completely define the way two successive patterns are connected.
    | For instance, provide aNodeUIDs = [A, B, C] and aNodeUIDs_NextPattern = [A'],
        if the pattern is A -> B -> C, and if C is connected to A'
    | If aNodeUIDs_NextPattern is let empty, the function will try to connect the successive patterns
        by the most obvious way, respecting the input / output type (color / grayscale)

    :param aParentObject: reference SBSObject where the iteration is created
    :param aNbIteration: number of time the pattern must be duplicated
    :param aNodeUIDs: list of node's UID that constitute the pattern to duplicate
    :param aNodeUIDs_NextPattern: list of node's UID that correspond to the inputs of the next pattern, which must be connected to the given pattern. Default to []
    :param aForceRandomSeed: specify if a different random seed must be generated for each iteration. Default to False
    :param aIncrementIteration: specify if the parameter 'iteration' must be incremented at each iteration. Default to False
    :param aGUIOffset: pattern position offset. Default to [150, 0]

    :type aParentObject: :class:`.SBSGraph` or :class:`.SBSDynamicValue`
    :type aNbIteration: positive integer
    :type aNodeUIDs: list of str
    :type aNodeUIDs_NextPattern: list of str, optional
    :type aForceRandomSeed: bool, optional
    :type aIncrementIteration: bool, optional
    :type aGUIOffset: list of 2 float, optional

    :return: The list of :class:`.SBSCompNode` objects created (including the nodes given in aNodeUIDs_NextPattern), None if failed
    :raise: :class:`api_exceptions.SBSImpossibleActionError`
    """
    ### Helpers ###
    def findIterationNumber(nodeList):
        iteration = None
        for aNode in nodeList:
            iterationParam = int(aNode.getParameterValue(sbsenum.CompNodeParamEnum.ITERATION))
            if iterationParam is not None and (iteration is None or iterationParam > iteration):
                iteration = iterationParam
        return iteration

    def setIterationParameters(nodeList, forceRandomSeed, incrementIteration, iteration):
        if not incrementIteration and not forceRandomSeed:
            return iteration

        randomSeed = randint(0, 10000) if forceRandomSeed else 0
        if aIncrementIteration:
            iteration += 1

        for aNode in nodeList:
            if incrementIteration:
                try:    aNode.setParameterValue(sbsenum.CompNodeParamEnum.ITERATION, str(iteration))
                except: pass
            if forceRandomSeed:
                try:    aNode.setParameterValue(sbsenum.CompNodeParamEnum.RANDOM_SEED, randomSeed)
                except: pass
        return iteration

    def updateListsAccordingToSort(fSortedIndices, fConnectionsInsidePattern, fSortedNodeList, fSortedConnections):
        fSortedConnections.extend([([],[]) for _ in range(len(fConnectionsInsidePattern))])
        for i, (aIndex, aConn) in enumerate(zip(fSortedIndices, fConnectionsInsidePattern)):
            fSortedNodeList.append(aNodeList[aIndex])
            for inConn in aConn[0]:
                fSortedConnections[fSortedIndices.index(i)][0].append((fSortedIndices.index(inConn[0]), inConn[1]))
            for outConn in aConn[1]:
                fSortedConnections[fSortedIndices.index(i)][1].append((fSortedIndices.index(outConn[0]), outConn[1]))
    ### End ###

    if aGUIOffset is None: aGUIOffset = [150, 0]
    if aNodeUIDs_NextPattern is None: aNodeUIDs_NextPattern = []

    # Get the pattern nodes from the given UIDs and get the pattern GUI rectangle
    aNodeList = aParentObject.mNodeList.getNodeList(aNodesList = aNodeUIDs)
    if not aNodeList:
        return None

    aGUIRect = aParentObject.mNodeList.getRect(aNodeList)
    aOffsetPos = [0, 0]
    if aGUIOffset[0] != 0:          aOffsetPos[0] = aGUIRect.mWidth + aGUIOffset[0]
    if aGUIOffset[1] != 0:          aOffsetPos[1] = aGUIRect.mHeight + aGUIOffset[1]

    # Get the nodes defined as the next pattern from the given UIDs
    aNodeList_NextPattern = aParentObject.mNodeList.getNodeList(aNodesList = aNodeUIDs_NextPattern)
    if aNodeList_NextPattern and len(aNodeList) != len(aNodeList_NextPattern):
        raise SBSImpossibleActionError('Cannot create iteration: the length of the first pattern is not equal to the length of the next pattern')

    # Try to find a node in input with a parameter 'Iteration', and get its value
    aIteration = None
    if aIncrementIteration:
        aIteration = findIterationNumber(aNodeList)
        if aIteration is None:
            aIncrementIteration = False

    # Get the list of connections (incoming and outgoing) inside the pattern for each node
    connectionsInsidePattern = aParentObject.mNodeList.computeConnectionsInsidePattern(aNodeList)

    # Sort the node list as a DAG
    sortedIndices = aParentObject.mNodeList.computeSortedIndicesOfDAG(aNodeList, connectionsInsidePattern)
    sortedNodeList = []
    sortedConnections = []
    updateListsAccordingToSort(sortedIndices, connectionsInsidePattern, sortedNodeList, sortedConnections)

    # Get the list of input and output pins of the whole pattern
    # -> An input pin is connected to a node that does not belong to the pattern.
    # -> An output pin is never referenced by the connections inside the pattern.
    patternInputsOutputs = aParentObject.mNodeList.computePatternInputsAndOutputs( sortedNodeList, sortedConnections)

    # If the next pattern is provided, identify the connections inter-pattern, using the inputs and outputs detected previously
    if aNodeUIDs_NextPattern:
        # First, sort the next pattern as a DAG
        connectionsInsidePattern_Next = aParentObject.mNodeList.computeConnectionsInsidePattern(aNodeList)
        sortedIndices_Next = aParentObject.mNodeList.computeSortedIndicesOfDAG(aNodeList_NextPattern, connectionsInsidePattern_Next)
        sortedNodes_Next = [aNodeList_NextPattern[index] for index in sortedIndices_Next]
        aNodeList_NextPattern = sortedNodes_Next

        # Check that the two patterns are equivalent
        if next((aNode for aNode, aNodeNext in zip(sortedNodeList, aNodeList_NextPattern) if not aNode.equals(aNodeNext)), None):
            raise SBSImpossibleActionError('Cannot create iteration: the two provided patterns are not equivalent')

        # Find the connections inter-pattern and tag the relevant inputs with 'connectedTo'
        for inputConn in patternInputsOutputs[0]:
            aNodeInNext = aNodeList_NextPattern[inputConn['index']]
            aConnection = aNodeInNext.getConnectionOnPin(inputConn['identifier'])
            connRef = aConnection.getConnectedNodeUID()
            res = next(((i,aNode) for i,aNode in enumerate(sortedNodeList) if aNode.mUID == connRef), None)
            if res is not None:
                inputConn['connectedTo'] = res[0]

    # Handle the case were the connection between successive patterns is not given in input (aNodeUIDs_NextPattern)
    # We duplicate the first pattern, and connect the two pattern on the first compatible output and input.
    # This allows to fill aNodeList_NextPattern with new nodes, connected to a compatible output of the first pattern.
    else:
        # Duplicate all nodes to create the next pattern
        for aNode in sortedNodeList:
            aNewNode = aParentObject.duplicateNode(aNode, aOffsetPos)
            aNodeList_NextPattern.append(aNewNode)

        # Reconnect nodes inside the new pattern
        for j, conn in enumerate(sortedConnections):
            for inputConn in conn[0]:
                aConnection = aNodeList_NextPattern[j].getConnectionOnPin(inputConn[1]['identifier'])
                aConnection.setConnection(aConnRefValue = aNodeList_NextPattern[inputConn[0]].mUID)

        # Connect the two patterns together, and tag the relevant inputs with 'connectedTo'
        availableInputs = [i for i in range(0,len(patternInputsOutputs[0]))]
        outputMap = {}
        outputUID = None
        for aOutputConn in patternInputsOutputs[1]:
            i = 0
            compatibleInputFound = False
            while i < len(availableInputs):
                aInputConn = patternInputsOutputs[0][availableInputs[i]]
                aConnection = None

                if (isinstance(aInputConn['type'], int) and aInputConn['type'] & aOutputConn['type']) or \
                                aInputConn['type'] == aOutputConn['type']:
                    aConnection = aNodeList_NextPattern[aInputConn['index']].getConnectionOnPin(aInputConn['identifier'])
                    connRef = aConnection.getConnectedNodeUID()
                    if connRef in outputMap:
                        outputUID = outputMap[connRef]['nodeUID']
                    elif not compatibleInputFound:
                        outputUID = sortedNodeList[aOutputConn['index']].mUID
                        aOutputConn['nodeUID'] = outputUID
                    else:
                        aConnection = None

                if aConnection is not None:
                    aConnection.setConnection(aConnRefValue = outputUID,
                                              aConnRefOutputValue = aOutputConn['uid'])
                    aInputConn['connectedTo'] = aOutputConn['index']
                    compatibleInputFound = True
                    availableInputs.pop(i)
                else:
                    i += 1

    # Set the iteration parameters for the next pattern: ITERATION and RANDOM_SEED
    aIteration = setIterationParameters(aNodeList_NextPattern, aForceRandomSeed, aIncrementIteration, aIteration)

    createdNodes = copy.copy(aNodeList_NextPattern)
    sortedNodeList = copy.copy(aNodeList_NextPattern)
    connectionsInterPattern = [inputConn for inputConn in patternInputsOutputs[0] if 'connectedTo' in inputConn]

    # Create all iterations and connections
    for i in range(1, aNbIteration):

        # Duplicate all nodes of pattern
        for j, aNode in enumerate(sortedNodeList):
            aNewNode = aParentObject.duplicateNode(aNode, aOffsetPos)
            aNodeList_NextPattern[j] = aNewNode

        # Set the iteration parameters: ITERATION and RANDOM_SEED
        aIteration = setIterationParameters(aNodeList_NextPattern, aForceRandomSeed, aIncrementIteration, aIteration)

        # Reconnect nodes inside the pattern
        for j, conn in enumerate(sortedConnections):
            for inputConn in conn[0]:
                aConnection = aNodeList_NextPattern[j].getConnectionOnPin(inputConn[1]['identifier'])
                aConnection.setConnection(aConnRefValue = aNodeList_NextPattern[inputConn[0]].mUID)

        # Connect the two successive pattern together
        for inputConn in connectionsInterPattern:
            aConnection = aNodeList_NextPattern[inputConn['index']].getConnectionOnPin(inputConn['identifier'])
            aConnection.setConnection(aConnRefValue = sortedNodeList[inputConn['connectedTo']].mUID)

        createdNodes.extend(aNodeList_NextPattern)
        sortedNodeList = copy.copy(aNodeList_NextPattern)

    return createdNodes




@handle_exceptions()
def createCurveParamsArray(aCompFilter, aCurveDefinition):
    """
    createCurveParamsArray(aCompFilter, aCurveDefinition)
    Create the hierarchy of SBSObject necessary to describe the given gradient key values.

    :param aCompFilter: the Gradient map filter
    :param aCurveDefinition: the curve definition to set
    :type aCompFilter: :class:`.SBSCompFilter`
    :type aCurveDefinition: :class:`.CurveDefinition`
    :return: the new :class:`.SBSParamsArray` if success, None otherwise
    """
    from pysbs import params

    # Create the ParamArray
    aParamArray = params.SBSParamsArray(aName = sbslibrary.getCurveName(aCurveDefinition.mIdentifier),
                                        aUID  = UIDGenerator.generateUID(aCompFilter),
                                        aParamsArrayCells = [])

    # Add a ParamArrayCell for each given gradient key
    for key in aCurveDefinition.mCurveKeys:
        aParameters = [__createParameter(sbsenum.ParamTypeEnum.FLOAT2, key.mPosition, 'position'),
                       __createParameter(sbsenum.ParamTypeEnum.FLOAT2, key.mLeft, 'left'),
                       __createParameter(sbsenum.ParamTypeEnum.BOOLEAN, key.mIsLeftBroken, 'isLeftBroken'),
                       __createParameter(sbsenum.ParamTypeEnum.FLOAT2, key.mRight, 'right'),
                       __createParameter(sbsenum.ParamTypeEnum.BOOLEAN, key.mIsRightBroken, 'isRightBroken'),
                       __createParameter(sbsenum.ParamTypeEnum.BOOLEAN, key.mIsLocked, 'isLocked')]

        aParamsArrayCell = params.SBSParamsArrayCell(aUID = UIDGenerator.generateUID(aParamArray),
                                                     aParameters = aParameters)

        aParamArray.mParamsArrayCells.append(aParamsArrayCell)

    return aParamArray



@handle_exceptions()
def createGradientMapParamsArray(aCompFilter, aKeyValues):
    """
    createGradientMapParamsArray(aCompFilter, aKeyValues)
    Create the hierarchy of SBSObject necessary to describe the given gradient key values.

    :param aCompFilter: the Gradient map filter
    :param aKeyValues: the gradient map key values to set
    :type aCompFilter: :class:`.SBSCompFilter`
    :type aKeyValues: list of :class:`.GradientKey`
    :return: the new :class:`.SBSParamsArray` if success, None otherwise
    """
    from pysbs import params

    # Create the ParamArray
    aParamArray = params.SBSParamsArray(aName = 'gradientrgba',
                                        aUID  = UIDGenerator.generateUID(aCompFilter),
                                        aParamsArrayCells = [])

    # Add a ParamArrayCell for each given gradient key
    for key in aKeyValues:
        aParameters = [__createParameter(sbsenum.ParamTypeEnum.FLOAT1, key.mPosition, 'position'),
                       __createParameter(sbsenum.ParamTypeEnum.FLOAT1, key.mMidpoint, 'midpoint'),
                       __createParameter(sbsenum.ParamTypeEnum.FLOAT4, key.mValue, 'value')]

        aParamsArrayCell = params.SBSParamsArrayCell(aUID = UIDGenerator.generateUID(aParamArray),
                                                     aParameters = aParameters)

        aParamArray.mParamsArrayCells.append(aParamsArrayCell)

    return aParamArray

@handle_exceptions()
def createIcon(aIconAbsPath):
    """
    createIcon(aIconAbsPath)
    Create a SBSIcon from the given image path

    :param aIconAbsPath: The absolute path of the image to set
    :type aIconAbsPath: str
    :return: The :class:`.SBSIcon` object created
    """
    from pysbs import sbscommon

    # Get compressed image content
    aExtension = api_helpers.splitExtension(aIconAbsPath)[1]
    aDataLength, base64SVGData = __getBase64CompressedContent(aIconAbsPath, aBinaryFile=True)

    # Create a Icon object
    return sbscommon.SBSIcon(aDataLength=str(aDataLength), aFormat=aExtension.lower()[1:], aStrdata=base64SVGData)




@handle_exceptions()
def createGUIObject(aParentObject, aObjectType, aGUIName, aGUIPos, aSize,
                    aGUIDependency = None,
                    aTitle = None,
                    aColor = None,
                    aIsTitleVisible = False,
                    aIsFrameVisible = False):
    """
    createGUIObject(aParentObject, aObjectType, aGUIName, aGUIPos, aSize, aTitle = None, aColor = None, aIsTitleVisible = False, aIsFrameVisible = False)

    :param aParentObject: The parent graph / function that will contain the GUI object
    :param aObjectType: Kind of GUI Object to create
    :param aGUIName: The GUI object textual content
    :param aGUIPos: The position of the GUI object
    :param aGUIDependency: The GUI dependency value ('NODE?<uid>'), if this GUI object is linked to another object in the graph
    :param aSize: The size of the GUI object
    :param aTitle: The title of the GUI object (only for framed comments)
    :param aColor: The color of the GUI object (only for framed comments)
    :param aIsTitleVisible: True to display the title of a framed comment. Default to False
    :param aIsFrameVisible: True in case of a framed comment. Default to False
    :type aParentObject: :class:`.SBSGraph` or :class:`.SBSFunction`
    :type aObjectType: :class:`.GUIObjectTypeEnum`
    :type aGUIName: str
    :type aGUIPos: list of 3 float
    :type aSize: list of 2 float
    :type aGUIDependency: str, optional
    :type aColor: list of 4 float, optional
    :type aIsTitleVisible: boolean, optional
    :type aIsFrameVisible: boolean, optional
    :return: The :class:`.SBSGUIObject` created
    """
    from pysbs import sbscommon

    aLayout = sbscommon.SBSGUILayout(aGPos = aGUIPos, aSize = aSize)

    if aColor is not None:
        aColor = api_helpers.formatValueForTypeStr(aColor, sbsenum.ParamTypeEnum.FLOAT4)

    aIsTitleVisible = api_helpers.formatValueForTypeStr(aIsTitleVisible, sbsenum.ParamTypeEnum.BOOLEAN) if aIsTitleVisible else None
    aIsFrameVisible = api_helpers.formatValueForTypeStr(aIsFrameVisible, sbsenum.ParamTypeEnum.BOOLEAN) if aIsFrameVisible else None

    aGUIObject = sbscommon.SBSGUIObject(aUID            = UIDGenerator.generateUID(aParentObject),
                                        aType           = sbslibrary.getGUIObjectTypeName(aObjectType),
                                        aFrameColor     = aColor,
                                        aGUILayout      = aLayout,
                                        aGUIName        = aGUIName,
                                        aGUIDependency  = aGUIDependency,
                                        aTitle          = aTitle,
                                        aIsFrameVisible = aIsFrameVisible,
                                        aIsTitleVisible = aIsTitleVisible)
    return aGUIObject


def __createParameter(aType, aValue, aParamName):
    """
    __createParameter(aType, aValue, aParamName)
    Create a SBSParamValue of the given type, value, and name

    :param aType: Type of the parameter
    :param aValue: value of the parameter
    :param aParamName: name of the parameter
    :type aType: :class:`.ParamTypeEnum`
    :type aValue: any type
    :type aParamName: str
    :return: a :class:`.SBSParamValue` object
    """
    from pysbs import params

    paramValue = params.SBSParamValue()
    formattedValue = api_helpers.formatValueForTypeStr(aValue, aType)
    paramValue.setConstantValue(aType = aType, aValue = formattedValue)
    return params.SBSParameter(aName = aParamName, aParamValue = paramValue)


@handle_exceptions()
def __getBase64CompressedContent(aFileAbsPath, aBinaryFile):
    """
    __getBase64CompressedContent(aFileAbsPath, aBinaryFile)
    Get the content of the file using zlib compression and then base64 encoding

    :param aFileAbsPath: the absolute path of the file
    :param aBinaryFile: True to read the file as binary content instead of text
    :type aFileAbsPath: str
    :type aBinaryFile: bool
    :return: a tuple(dataLength, compressedData)
    """
    if aBinaryFile:
        aFile = io.open(file=aFileAbsPath, mode='rb')
    else:
        aFile = io.open(file=aFileAbsPath, mode='r')

    aFileContent = aFile.read()
    aFile.close()

    aDataLength = len(aFileContent)

    aHeader = struct.pack(str('>i'), aDataLength)
    if python_helpers.handleBytes() and type(aFileContent) != bytes:
        compressedData = aHeader + zlib.compress(bytearray(aFileContent, 'utf-8'))
    else:
        compressedData = aHeader + zlib.compress(aFileContent)
    base64SVGData = base64.b64encode(compressedData).decode()

    return aDataLength, base64SVGData
