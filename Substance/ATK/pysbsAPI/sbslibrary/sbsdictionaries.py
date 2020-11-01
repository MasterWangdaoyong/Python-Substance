# coding: utf-8
"""
Module **sbsdictionaries** provides the dictionaries to have the mapping between the enumerations in :mod:`.sbsenum` and the
corresponding string identifier used by Substance Designer.

    * **Dictionaries:**
        * __dict_Attributes: dictionary relative to :class:`.AttributesEnum`
        * __dict_CommonUsageComponents: dictionary relative to :class:`.ComponentsEnum`
        * __dict_CommonUsages: dictionary relative to :class:`.UsageEnum`
        * __dict_CompNodeInputs: dictionary relative to :class:`.InputEnum`
        * __dict_CompNodeOutputs: dictionary relative to :class:`.OutputEnum`
        * __dict_CompNodeParameters: dictionary relative to :class:`.CompNodeParamEnum`
        * __dict_CurveTypes: dictionary relative to :class:`.CurveTypeEnum`
        * __dict_FunctionInputs: dictionary relative to :class:`.FunctionInputEnum`
        * __dict_GUIObjectTypes: dictionary relative to :class:`.GUIObjectTypeEnum`
        * __dict_ResourceTypes: dictionary relative to :class:`.ResourceTypeEnum`
        * __dict_WidgetTypes: dictionary relative to :class:`.WidgetTypeEnum`
        * __dict_WidgetOptions: dictionary relative to :class:`.WidgetOptionEnum`
        * __dict_SubstanceGraphTemplate: dictionary relative to :class:`.GraphTemplateEnum`
"""

from __future__ import unicode_literals
import sys
import math

from pysbs import sbsenum
from pysbs.api_decorators import doc_module_attributes,handle_exceptions,checkFirstParamIsAString


# Default attributes tags
__dict_Attributes = {
    sbsenum.AttributesEnum.Category      : 'category'     ,
    sbsenum.AttributesEnum.Label         : 'label'        ,
    sbsenum.AttributesEnum.Author        : 'author'       ,
    sbsenum.AttributesEnum.AuthorURL     : 'authorURL'    ,
    sbsenum.AttributesEnum.Tags          : 'tags'         ,
    sbsenum.AttributesEnum.Description   : 'description'  ,
    sbsenum.AttributesEnum.UserTags      : 'usertags'     ,
    sbsenum.AttributesEnum.Icon          : 'icon'         ,
    sbsenum.AttributesEnum.HideInLibrary : 'hideInLibrary',
    sbsenum.AttributesEnum.PhysicalSize  : 'physicalSize'
}

# Dictionary of the available inputs on Filters and FxMaps node
__dict_CompNodeInputs = {
    sbsenum.InputEnum.BACKGROUND        : 'background'      ,
    sbsenum.InputEnum.DESTINATION       : 'destination'     ,
    sbsenum.InputEnum.INPUT             : 'input'           ,
    sbsenum.InputEnum.INPUT1            : 'input1'          ,
    sbsenum.InputEnum.INPUT2            : 'input2'          ,
    sbsenum.InputEnum.INPUT_GRADIENT    : 'inputgradient'   ,
    sbsenum.InputEnum.INPUT_INTENSITY   : 'inputintensity'  ,
    sbsenum.InputEnum.INPUT_NODE_OUTPUT : 'inputNodeOutput' ,
    sbsenum.InputEnum.INPUT_PATTERN     : 'inputpattern'    ,
    sbsenum.InputEnum.MASK              : 'mask'            ,
    sbsenum.InputEnum.OPACITY           : 'opacity'         ,
    sbsenum.InputEnum.SOURCE            : 'source'
}

# Dictionary of the available outputs on Filters and FxMaps node
__dict_CompNodeOutputs = {
    sbsenum.OutputEnum.OUTPUT  : 'output'   ,
    sbsenum.OutputEnum.OUTPUT0 : 'output0'  ,
    sbsenum.OutputEnum.OUTPUT1 : 'output1'  ,
    sbsenum.OutputEnum.OUTPUT2 : 'output2'  ,
    sbsenum.OutputEnum.OUTPUT3 : 'output3'  ,
    sbsenum.OutputEnum.OUTPUTN : 'outputn'  ,
}

# Dictionary of the available parameters on Filters and FxMaps node
__dict_CompNodeParameters = {
    sbsenum.CompNodeParamEnum.OUTPUT_FORMAT         : 'format'              ,
    sbsenum.CompNodeParamEnum.OUTPUT_SIZE           : 'outputsize'          ,
    sbsenum.CompNodeParamEnum.PIXEL_SIZE            : 'pixelsize'           ,
    sbsenum.CompNodeParamEnum.PIXEL_RATIO           : 'pixelratio'          ,
    sbsenum.CompNodeParamEnum.QUALITY               : 'quality'             ,
    sbsenum.CompNodeParamEnum.RANDOM_SEED           : 'randomseed'          ,
    sbsenum.CompNodeParamEnum.TILING_MODE           : 'tiling'              ,
    sbsenum.CompNodeParamEnum.ITERATION             : 'iteration'           ,
    sbsenum.CompNodeParamEnum.ALPHA_BLENDING        : 'alphablending'       ,
    sbsenum.CompNodeParamEnum.BACKGROUND            : 'background'          ,
    sbsenum.CompNodeParamEnum.BACKGROUND_VALUE      : 'mattelevel'          ,
    sbsenum.CompNodeParamEnum.BITMAP_RESOURCE_PATH  : 'bitmapresourcepath'  ,
    sbsenum.CompNodeParamEnum.BITMAP_RESIZE_METHOD  : 'resizemethod'        ,
    sbsenum.CompNodeParamEnum.BLENDING_MODE         : 'blendingmode'        ,
    sbsenum.CompNodeParamEnum.BLUR_ANGLE            : 'mblurangle'          ,
    sbsenum.CompNodeParamEnum.CHANNEL_ALPHA         : 'channelalpha'        ,
    sbsenum.CompNodeParamEnum.CHANNEL_BLUE          : 'channelgreen'        ,
    sbsenum.CompNodeParamEnum.CHANNEL_GREEN         : 'channelblue'         ,
    sbsenum.CompNodeParamEnum.CHANNEL_RED           : 'channelred'          ,
    sbsenum.CompNodeParamEnum.CHANNELS_WEIGHTS      : 'channelsweights'     ,
    sbsenum.CompNodeParamEnum.CLAMP_IN_TERM         : 'clampinterm'         ,
    sbsenum.CompNodeParamEnum.COLOR_MODE            : 'colorswitch'         ,
    sbsenum.CompNodeParamEnum.COMBINE_DISTANCE      : 'combinedistance'     ,
    sbsenum.CompNodeParamEnum.CROPPING_AREA         : 'maskrectangle'       ,
    sbsenum.CompNodeParamEnum.FILTERING             : 'filtering'           ,
    sbsenum.CompNodeParamEnum.FLATTEN_ALPHA         : 'alphamult'           ,
    sbsenum.CompNodeParamEnum.GRADIENT_ADDRESSING   : 'addressingrepeat'    ,
    sbsenum.CompNodeParamEnum.GRADIENT_ORIENTATION  : 'uvselector'          ,
    sbsenum.CompNodeParamEnum.GRADIENT_POSITION     : 'coordinate'          ,
    sbsenum.CompNodeParamEnum.HIGHLIGHT_COLOR       : 'highlightcolor'      ,
    sbsenum.CompNodeParamEnum.HUE                   : 'hue'                 ,
    sbsenum.CompNodeParamEnum.INTENSITY             : 'intensity'           ,
    sbsenum.CompNodeParamEnum.NORMAL_FORMAT         : 'inversedy'           ,
    sbsenum.CompNodeParamEnum.LEVEL_IN_HIGH         : 'levelinhigh'         ,
    sbsenum.CompNodeParamEnum.LEVEL_IN_LOW          : 'levelinlow'          ,
    sbsenum.CompNodeParamEnum.LEVEL_IN_MID          : 'levelinmid'          ,
    sbsenum.CompNodeParamEnum.LEVEL_OUT_HIGH        : 'levelouthigh'        ,
    sbsenum.CompNodeParamEnum.LEVEL_OUT_LOW         : 'leveloutlow'         ,
    sbsenum.CompNodeParamEnum.LIGHT_ANGLE           : 'lightangle'          ,
    sbsenum.CompNodeParamEnum.LIGHTNESS             : 'luminosity'          ,
    sbsenum.CompNodeParamEnum.MIPMAP_LEVEL          : 'manualmiplevel'      ,
    sbsenum.CompNodeParamEnum.MATTE_COLOR           : 'mattecolor'          ,
    sbsenum.CompNodeParamEnum.MAX_DISTANCE          : 'distance'            ,
    sbsenum.CompNodeParamEnum.MIPMAP_MODE           : 'mipmapmode'          ,
    sbsenum.CompNodeParamEnum.OPACITY               : 'opacitymult'         ,
    sbsenum.CompNodeParamEnum.OFFSET                : 'offset'              ,
    sbsenum.CompNodeParamEnum.OUTPUT_COLOR          : 'outputcolor'         ,
    sbsenum.CompNodeParamEnum.PER_PIXEL             : 'perpixel'            ,
    sbsenum.CompNodeParamEnum.FUNCTION              : 'function'            ,
    sbsenum.CompNodeParamEnum.RENDER_REGION         : 'renderroi'           ,
    sbsenum.CompNodeParamEnum.ROUGHNESS             : 'hurst'               ,
    sbsenum.CompNodeParamEnum.SATURATION            : 'saturation'          ,
    sbsenum.CompNodeParamEnum.SHADOW_COLOR          : 'shadowcolor'         ,
    sbsenum.CompNodeParamEnum.SVG_RESOURCE_PATH     : 'vectorresourcepath'  ,
    sbsenum.CompNodeParamEnum.TEXT                  : 'text'                ,
    sbsenum.CompNodeParamEnum.TEXT_ALIGN            : 'alignment'           ,
    sbsenum.CompNodeParamEnum.TEXT_FONT             : 'fontdata'            ,
    sbsenum.CompNodeParamEnum.TEXT_FONT_SIZE        : 'fontsize'            ,
    sbsenum.CompNodeParamEnum.TEXT_FONT_COLOR       : 'frontcolor'          ,
    sbsenum.CompNodeParamEnum.TEXT_POSITION         : 'position'            ,
    sbsenum.CompNodeParamEnum.TILING_REGION         : 'tilingroi'           ,
    sbsenum.CompNodeParamEnum.TRANSFORM_MATRIX      : 'matrix22'            ,
    sbsenum.CompNodeParamEnum.WARP_ANGLE            : 'warpangle'           ,
    sbsenum.CompNodeParamEnum.NORMAL_ALPHA_CHANNEL  : 'input2alpha'         ,
    sbsenum.CompNodeParamEnum.FX_BLENDING_MODE      : 'blendingmode'        ,
    sbsenum.CompNodeParamEnum.FX_BRANCH_OFFSET      : 'branchoffset'        ,
    sbsenum.CompNodeParamEnum.FX_COLOR_LUM          : 'opacity'             ,
    sbsenum.CompNodeParamEnum.FX_IMAGE_ALPHA_PREMUL : 'imagepremul'         ,
    sbsenum.CompNodeParamEnum.FX_IMAGE_FILTERING    : 'imagefiltering'      ,
    sbsenum.CompNodeParamEnum.FX_IMAGE_INDEX        : 'imageindex'          ,
    sbsenum.CompNodeParamEnum.FX_ITERATIONS         : 'numberadded'         ,
    sbsenum.CompNodeParamEnum.FX_PATTERN_OFFSET     : 'frameoffset'         ,
    sbsenum.CompNodeParamEnum.FX_PATTERN_ROTATION   : 'patternrotation'     ,
    sbsenum.CompNodeParamEnum.FX_PATTERN_SIZE       : 'patternsize'         ,
    sbsenum.CompNodeParamEnum.FX_PATTERN_TYPE       : 'patterntype'         ,
    sbsenum.CompNodeParamEnum.FX_PATTERN_VARIATION  : 'patternsuppl'        ,
    sbsenum.CompNodeParamEnum.FX_RANDOM_INHERITED   : 'randominherited'     ,
    sbsenum.CompNodeParamEnum.FX_RANDOM_SEED        : 'randomseed'          ,
    sbsenum.CompNodeParamEnum.FX_SELECTOR           : 'switch'
}

# Common usage tags
__dict_CommonUsages = {
    sbsenum.UsageEnum.DIFFUSE           : 'diffuse'         ,
    sbsenum.UsageEnum.BASECOLOR         : 'baseColor'       ,
    sbsenum.UsageEnum.OPACITY           : 'opacity'         ,
    sbsenum.UsageEnum.EMISSIVE          : 'emissive'        ,
    sbsenum.UsageEnum.AMBIENT           : 'ambient'         ,
    sbsenum.UsageEnum.AMBIENT_OCCLUSION : 'ambientOcclusion',
    sbsenum.UsageEnum.MASK              : 'mask'            ,
    sbsenum.UsageEnum.NORMAL            : 'normal'          ,
    sbsenum.UsageEnum.BUMP              : 'bump'            ,
    sbsenum.UsageEnum.HEIGHT            : 'height'          ,
    sbsenum.UsageEnum.DISPLACEMENT      : 'displacement'    ,
    sbsenum.UsageEnum.SPECULAR          : 'specular'        ,
    sbsenum.UsageEnum.SPECULAR_LEVEL    : 'specularLevel'   ,
    sbsenum.UsageEnum.SPECULAR_COLOR    : 'specularColor'   ,
    sbsenum.UsageEnum.GLOSSINESS        : 'glossiness'      ,
    sbsenum.UsageEnum.ROUGHNESS         : 'roughness'       ,
    sbsenum.UsageEnum.ANISOTROPY_LEVEL  : 'anisotropyLevel' ,
    sbsenum.UsageEnum.ANISOTROPY_ANGLE  : 'anisotropyAngle' ,
    sbsenum.UsageEnum.TRANSMISSIVE      : 'transmissive'    ,
    sbsenum.UsageEnum.REFLECTION        : 'reflection'      ,
    sbsenum.UsageEnum.REFRACTION        : 'refraction'      ,
    sbsenum.UsageEnum.ENVIRONMENT       : 'environment'     ,
    sbsenum.UsageEnum.IOR               : 'IOR'             ,
    sbsenum.UsageEnum.SCATTERING0       : 'scattering0'     ,
    sbsenum.UsageEnum.SCATTERING1       : 'scattering1'     ,
    sbsenum.UsageEnum.SCATTERING2       : 'scattering2'     ,
    sbsenum.UsageEnum.SCATTERING3       : 'scattering3'     ,
    sbsenum.UsageEnum.ANY               : 'any'             ,
    sbsenum.UsageEnum.METALLIC          : 'metallic'        ,
    sbsenum.UsageEnum.PANORAMA          : 'panorama'
}

# Common usage components tags
__dict_CommonUsageComponents = {
    sbsenum.ComponentsEnum.RGBA : 'RGBA',
    sbsenum.ComponentsEnum.RGB  : 'RGB' ,
    sbsenum.ComponentsEnum.R    : 'R'   ,
    sbsenum.ComponentsEnum.G    : 'G'   ,
    sbsenum.ComponentsEnum.B    : 'B'   ,
    sbsenum.ComponentsEnum.A    : 'A'
}

# Common usage color space tags
__dict_CommonColorSpaces = {
    sbsenum.ColorSpacesEnum.SRGB             : 'sRGB',
    sbsenum.ColorSpacesEnum.LINEAR           : 'Linear',
    sbsenum.ColorSpacesEnum.PASSTHRU         : 'Passthru',
    sbsenum.ColorSpacesEnum.SNORM            : 'SNorm',
    sbsenum.ColorSpacesEnum.NORMAL_XYZ_LEFT  : 'NormalXYZLeft',
    sbsenum.ColorSpacesEnum.NORMAL_XYZ_RIGHT : 'NormalXYZRight'
}

# Dictionary of the curve names in the Curve filter
__dict_CurveTypes = {
    sbsenum.CurveTypeEnum.LUMINANCE : 'curveluminance',
    sbsenum.CurveTypeEnum.RED       : 'curvered',
    sbsenum.CurveTypeEnum.GREEN     : 'curvegreen',
    sbsenum.CurveTypeEnum.BLUE      : 'curveblue',
    sbsenum.CurveTypeEnum.ALPHA     : 'curvealpha',
}

# Dictionary of the available inputs on Functions
__dict_FunctionInputs = {
    sbsenum.FunctionInputEnum.A               : 'a'              ,
    sbsenum.FunctionInputEnum.B               : 'b'              ,
    sbsenum.FunctionInputEnum.COMPONENTS_IN   : 'componentsin'   ,
    sbsenum.FunctionInputEnum.COMPONENTS_LAST : 'componentslast' ,
    sbsenum.FunctionInputEnum.CONDITION       : 'condition'      ,
    sbsenum.FunctionInputEnum.ELSE_PATH       : 'elsepath'       ,
    sbsenum.FunctionInputEnum.ENTRIES         : 'entries'        ,
    sbsenum.FunctionInputEnum.IF_PATH         : 'ifpath'         ,
    sbsenum.FunctionInputEnum.LOOP            : 'loop'           ,
    sbsenum.FunctionInputEnum.POS             : 'pos'            ,
    sbsenum.FunctionInputEnum.RHO             : 'rho'            ,
    sbsenum.FunctionInputEnum.SCALAR          : 'scalar'         ,
    sbsenum.FunctionInputEnum.SEQUENCE_IN     : 'seqin'          ,
    sbsenum.FunctionInputEnum.SEQUENCE_LAST   : 'seqlast'        ,
    sbsenum.FunctionInputEnum.THETA           : 'theta'          ,
    sbsenum.FunctionInputEnum.VALUE           : 'value'          ,
    sbsenum.FunctionInputEnum.VECTOR          : 'vector'         ,
    sbsenum.FunctionInputEnum.X               : 'x'              ,
    sbsenum.FunctionInputEnum.INPUT           : 'input'
}

# Dictionary of GUI Object types
__dict_GUIObjectTypes = {
    sbsenum.GUIObjectTypeEnum.COMMENT : 'COMMENT',
    sbsenum.GUIObjectTypeEnum.PIN     : 'PIN'
}

# Dictionary of resource types
__dict_ResourceTypes = {
    sbsenum.ResourceTypeEnum.NONE           : ''                ,
    sbsenum.ResourceTypeEnum.FONT           : 'font'            ,
    sbsenum.ResourceTypeEnum.SVG            : 'svg'             ,
    sbsenum.ResourceTypeEnum.BITMAP         : 'bitmap'          ,
    sbsenum.ResourceTypeEnum.M_BSDF         : 'bsdfmeasurement' ,
    sbsenum.ResourceTypeEnum.LIGHT_PROFILE  : 'lightprofile'    ,
    sbsenum.ResourceTypeEnum.SCENE          : 'scene'           ,
}

# Dictionary of widget types
__dict_WidgetTypes = {
    sbsenum.WidgetTypeEnum.BUTTON                 : 'buttons'          ,
    sbsenum.WidgetTypeEnum.SLIDER                 : 'slider'           ,
    sbsenum.WidgetTypeEnum.DROP_DOWN_LIST         : 'dropdownlist'     ,
    sbsenum.WidgetTypeEnum.SIZE_POW_2             : 'sizepow2'         ,
    sbsenum.WidgetTypeEnum.ANGLE                  : 'angle'            ,
    sbsenum.WidgetTypeEnum.COLOR                  : 'color'            ,
    sbsenum.WidgetTypeEnum.TEXT                   : 'text'             ,
    sbsenum.WidgetTypeEnum.TRANSFORMATION_INVERSE : 'transformation'   ,
    sbsenum.WidgetTypeEnum.TRANSFORMATION_FORWARD : 'straighttransform',
    sbsenum.WidgetTypeEnum.POSITION               : 'position'         ,
    sbsenum.WidgetTypeEnum.OFFSET                 : 'reverseposition'
}

# Dictionary of widget options
__dict_WidgetOptions = {
    sbsenum.WidgetOptionEnum.BOOL_EDITOR_TYPE     : 'booleditortype'       ,
    sbsenum.WidgetOptionEnum.CLAMP                : 'clamp'                ,
    sbsenum.WidgetOptionEnum.DEFAULT              : 'default'              ,
    sbsenum.WidgetOptionEnum.LABEL0               : 'label0'               ,
    sbsenum.WidgetOptionEnum.LABEL1               : 'label1'               ,
    sbsenum.WidgetOptionEnum.LABEL2               : 'label2'               ,
    sbsenum.WidgetOptionEnum.LABEL3               : 'label3'               ,
    sbsenum.WidgetOptionEnum.MAX                  : 'max'                  ,
    sbsenum.WidgetOptionEnum.MIN                  : 'min'                  ,
    sbsenum.WidgetOptionEnum.PARAMETERS           : 'parameters'           ,
    sbsenum.WidgetOptionEnum.STEP                 : 'step'                 ,
    sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION : 'valueInterpretation'
}


# Dictionary of Substance Graph template
__dict_SubstanceGraphTemplate = {
    sbsenum.GraphTemplateEnum.EMPTY                              : 'sbs://../templates/01_empty.sbs/empty'                                                  ,
    sbsenum.GraphTemplateEnum.PBR_METALLIC_ROUGHNESS             : 'sbs://../templates/02_pbr_metallic_roughness.sbs/pbr_metallic_roughness'                ,
    sbsenum.GraphTemplateEnum.PBR_SPECULAR_GLOSSINESS            : 'sbs://../templates/03_pbr_specular_glossiness.sbs/pbr_specular_glossiness'              ,
    sbsenum.GraphTemplateEnum.STANDARD                           : 'sbs://../templates/04_standard.sbs/standard'                                            ,
    sbsenum.GraphTemplateEnum.SCAN_PBR_METALLIC_ROUGHNESS        : 'sbs://../templates/05_scan_pbr_metallic_roughness.sbs/scan_pbr_metallic_roughness'      ,
    sbsenum.GraphTemplateEnum.SCAN_PBR_SPECULAR_GLOSSINESS       : 'sbs://../templates/06_scan_pbr_specular_glossiness.sbs/scan_pbr_specular_glossiness'    ,
    sbsenum.GraphTemplateEnum.AXF_2_PBR_METALLIC_ROUGHNESS       : 'sbs://../templates/07_axf_to_pbr_metallic_roughness.sbs/axf_to_pbr_metallic_roughness'  ,
    sbsenum.GraphTemplateEnum.AXF_2_PBR_SPECULAR_GLOSSINESS      : 'sbs://../templates/08_axf_to_pbr_specular_glossiness.sbs/axf_to_pbr_specular_glossiness',
    sbsenum.GraphTemplateEnum.STUDIO_PANORAMA                    : 'sbs://../templates/09_studio_panorama.sbs/studio_panorama'                              ,
    sbsenum.GraphTemplateEnum.PAINTER_FILTER_GENERIC             : 'sbs://../templates/10_substance_painter.sbs/sp_filter_generic'                          ,
    sbsenum.GraphTemplateEnum.PAINTER_FILTER_SPECIFIC            : 'sbs://../templates/10_substance_painter.sbs/sp_filter_specific'                         ,
    sbsenum.GraphTemplateEnum.PAINTER_FILTER_SPECIFIC_MORE_MAPS  : 'sbs://../templates/10_substance_painter.sbs/sp_filter_channel_additional_maps'          ,
    sbsenum.GraphTemplateEnum.PAINTER_GENERATOR_MORE_MAPS        : 'sbs://../templates/10_substance_painter.sbs/sp_generator_additional_maps'
}



@handle_exceptions()
def getUsage(aUsage):
    """
    getUsage(aUsage)
    Get the given usage name

    :param aUsage: usage identifier
    :type aUsage: :class:`.UsageEnum`
    :return: the usage as a string
    """
    return __dict_CommonUsages[aUsage]

@handle_exceptions()
def getComponents(aComponents):
    """
    getComponents(aComponents)
    Get the given components name

    :param aComponents: components identifier
    :type aComponents: :class:`.ComponentsEnum`
    :return: the components as a string
    """
    return __dict_CommonUsageComponents[aComponents]


@handle_exceptions()
def getColorSpace(aColorSpace):
    """
    getColorSpace(aColorSpace))
    Get the given color space name

    :param aColorSpace: color space identifier
    :type aColorSpace: :class:`.ColorSpacesEnum`
    :return: the color space as a string
    """
    return __dict_CommonColorSpaces[aColorSpace]


@handle_exceptions()
@checkFirstParamIsAString
def getColorSpaceEnum(aColorSpaceName):
    """
    getColorSpaceEnum(aColorSpaceName)
    Get the enum value of the given parameter

    :param aColorSpaceName: parameter identifier
    :type aColorSpaceName: str
    :return: the parameter as a :class:`.ColorSpacesEnum` if found, None otherwise
    """
    return next((key for key, value in __dict_CommonColorSpaces.items() if value == aColorSpaceName), None)


@handle_exceptions()
def getAttribute(aAttribute):
    """
    getAttribute(aAttribute)
    Get the given attribute name

    :param aAttribute: attribute identifier
    :type aAttribute: :class:`.AttributesEnum`
    :return: the attribute as a string
    """
    return __dict_Attributes[aAttribute]

@handle_exceptions()
def getCompNodeInput(aInput):
    """
    getCompNodeInput(aInput)
    Get the given compositing node input name

    :param aInput: input identifier
    :type aInput: :class:`.InputEnum`
    :return: the input as a string
    """
    return __dict_CompNodeInputs[aInput]

@handle_exceptions()
def getCompNodeOutput(aOutput):
    """
    getCompNodeOutput(aOutput)
    Get the given compositing node output name

    :param aOutput: output identifier
    :type aOutput: :class:`.OutputEnum`
    :return: the output as a string
    """
    return __dict_CompNodeOutputs[aOutput]

@handle_exceptions()
def getCompNodeParam(aParameter):
    """
    getCompNodeParam(aParameter)
    Get the given compositing node parameter name

    :param aParameter: parameter identifier
    :type aParameter: :class:`.CompNodeParamEnum`
    :return: the parameter as a string
    """
    return __dict_CompNodeParameters[aParameter]

@handle_exceptions()
def getFunctionInput(aInput):
    """
    getFunctionInput(aInput)
    Get the given function node input name

    :param aInput: input identifier
    :type aInput: :class:`.FunctionInputEnum`
    :return: the input as a string
    """
    return __dict_FunctionInputs[aInput]

@handle_exceptions()
def getFunctionOutput(aOutput):
    """
    getFunctionOutput(aOutput)
    Get the given function node output name

    :param aOutput: output identifier
    :type aOutput: :class:`.OutputEnum`
    :return: the input as a string
    """
    return __dict_CompNodeOutputs[aOutput]


@handle_exceptions()
@checkFirstParamIsAString
def getCompNodeParamEnum(aParameterName):
    """
    getCompNodeParamEnum(aParameterName)
    Get the enum value of the given parameter

    :param aParameterName: parameter identifier
    :type aParameterName: str
    :return: the parameter as a :class:`.CompNodeParamEnum` if found, None otherwise
    """
    return next((key for key, value in __dict_CompNodeParameters.items() if value == aParameterName), None)

@handle_exceptions()
@checkFirstParamIsAString
def getCompNodeInputEnum(aInputName):
    """
    getCompNodeInputEnum(aInputName)
    Get the enum value of the given input

    :param aInputName: input identifier
    :type aInputName: str
    :return: the input as a :class:`.InputEnum`
    """
    return next((key for key, value in __dict_CompNodeInputs.items() if value == aInputName), None)

@handle_exceptions()
@checkFirstParamIsAString
def getCompNodeOutputEnum(aOutputName):
    """
    getCompNodeOutputEnum(aOutputName)
    Get the enum value of the given output

    :param aOutputName: output identifier
    :type aOutputName: str
    :return: the output as a :class:`.OutputEnum`
    """
    return next((key for key, value in __dict_CompNodeOutputs.items() if value == aOutputName), None)

@handle_exceptions()
@checkFirstParamIsAString
def getFunctionInputEnum(aInputName):
    """
    getFunctionInputEnum(aInputName)
    Get the enum value of the given function input

    :param aInputName: input identifier
    :type aInputName: str
    :return: the input as a :class:`.FunctionInputEnum`
    """
    return next((key for key, value in __dict_FunctionInputs.items() if value == aInputName), None)

@handle_exceptions()
@checkFirstParamIsAString
def getFunctionOutputEnum(aOutputName):
    """
    getFunctionOutputEnum(aOutputName)
    Get the enum value of the given function output

    :param aOutputName: output identifier
    :type aOutputName: str
    :return: the input as a :class:`.OutputEnum`
    """
    return next((key for key, value in __dict_CompNodeOutputs.items() if value == aOutputName), None)

@handle_exceptions()
def getFunctionGetType(aType):
    """
    getFunctionGetType(aType)
    Get the appropriate function GET_<> depending on the type of the input parameter

    :param aType: the type of data to get
    :type aType: :class:`.ParamTypeEnum`
    :return: the function GET_<> corresponding to the given type if succeed, None otherwise
    """
    aFunction = None
    if aType == sbsenum.ParamTypeEnum.BOOLEAN:
        aFunction = sbsenum.FunctionEnum.GET_BOOL
    elif aType & sbsenum.TypeMasksEnum.INTEGER:
        aFunction = int(sbsenum.FunctionEnum.GET_INTEGER1 + (math.log(aType, 2) - math.log(sbsenum.ParamTypeEnum.INTEGER1, 2)))
    elif aType & sbsenum.TypeMasksEnum.FLOAT:
        aFunction = int(sbsenum.FunctionEnum.GET_FLOAT1 + (math.log(aType, 2) - math.log(sbsenum.ParamTypeEnum.FLOAT1, 2)))
    elif aType == sbsenum.ParamTypeEnum.STRING:
        aFunction = sbsenum.FunctionEnum.GET_STRING
    return aFunction

@handle_exceptions()
def getWidgetName(aWidgetType):
    """
    getWidgetName(aWidgetType)
    Get the given widget type name

    :param aWidgetType: widget type identifier
    :type aWidgetType: :class:`.WidgetTypeEnum`
    :return: the widget type as a string
    """
    return __dict_WidgetTypes[aWidgetType]

@handle_exceptions()
def getWidgetOptionName(aWidgetOption):
    """
    getWidgetOptionName(aWidgetOption)
    Get the given widget option name

    :param aWidgetOption: widget option identifier
    :type aWidgetOption: :class:`.WidgetOptionEnum`
    :return: the widget option as a string
    """
    return __dict_WidgetOptions[aWidgetOption]

@handle_exceptions()
@checkFirstParamIsAString
def getWidgetTypeEnum(aWidgetName):
    """
    getWidgetTypeEnum(aWidgetName)
    Get the enum value of the given widget name

    :param aWidgetName: widget name
    :type aWidgetName: str
    :return: the widget type as a :class:`.WidgetTypeEnum`
    """
    return next((key for key, value in __dict_WidgetTypes.items() if value == aWidgetName), None)


@handle_exceptions()
def getCurveName(aCurveType):
    """
    getCurveName(aCurveType)
    Get the given curve type name

    :param aCurveType: curve type identifier
    :type aCurveType: :class:`.CurveTypeEnum`
    :return: the curve type as a string
    """
    return __dict_CurveTypes[aCurveType]

@handle_exceptions()
@checkFirstParamIsAString
def getCurveTypeEnum(aCurveName):
    """
    getCurveTypeEnum(aCurveName)
    Get the enum value of the given curve name

    :param aCurveName: curve name
    :type aCurveName: str
    :return: the curve type as a :class:`.CurveTypeEnum`
    """
    return next((key for key, value in __dict_CurveTypes.items() if value == aCurveName), None)

@handle_exceptions()
def getGUIObjectTypeName(aGUIObjectType):
    """
    getGUIObjectTypeName(aGUIObjectType)
    Get the given GUI object type name

    :param aGUIObjectType: GUI object type identifier
    :type aGUIObjectType: :class:`.GUIObjectTypeEnum`
    :return: the GUI object type as a string
    """
    return __dict_GUIObjectTypes[aGUIObjectType]

@handle_exceptions()
@checkFirstParamIsAString
def getGUIObjectTypeEnum(aGUIObjectTypeName):
    """
    getGUIObjectTypeEnum(aGUIObjectTypeName)
    Get the enum value of the given curve name

    :param aGUIObjectTypeName: GUI object type name
    :type aGUIObjectTypeName: str
    :return: the curve type as a :class:`.GUIObjectTypeEnum`
    """
    return next((key for key, value in __dict_GUIObjectTypes.items() if value == aGUIObjectTypeName), None)

@handle_exceptions()
def getResourceTypeName(aResourceType):
    """
    getResourceTypeName(aResourceType)
    Get the given resource type name

    :param aResourceType: resource type identifier
    :type aResourceType: :class:`.ResourceTypeEnum`
    :return: the curve type as a string
    """
    return __dict_ResourceTypes[aResourceType]

@handle_exceptions()
@checkFirstParamIsAString
def getResourceTypeEnum(aResourceName):
    """
    getResourceTypeEnum(aResourceName)
    Get the enum value of the given resource name

    :param aResourceName: resource name
    :type aResourceName: str
    :return: the curve type as a :class:`.ResourceTypeEnum`
    """
    return next((key for key, value in __dict_ResourceTypes.items() if value == aResourceName), None)

@handle_exceptions()
def getSubstanceGraphTemplatePath(aTemplateEnum):
    """
    getSubstanceGraphTemplatePath(aTemplateEnum)
    Get the path of the given Substance Graph template

    :param aTemplateEnum: Substance Graph template
    :type aTemplateEnum: :class:`.GraphTemplateEnum`
    :return: the path to the template as a string
    """
    return __dict_SubstanceGraphTemplate[aTemplateEnum]


doc_module_attributes(sys.modules[__name__])
