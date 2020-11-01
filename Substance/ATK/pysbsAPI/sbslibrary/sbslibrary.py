# coding: utf-8
"""
Module **sbslibrary** provides the libraries of Filters, Functions, FxMap nodes and Widgets that are defined in the
modules :mod:`.sbsfilters`, :mod:`.sbsfunctions`, :mod:`.sbsfxmapnodes` and :mod:`.sbswidgets`.

    * **Libraries:**
        * __library_Filters: the library of Filters, identified by :class:`.FilterEnum`
        * __library_FxMapNodes: the library of FxMap node, identified by :class:`.FxMapNodeEnum`
        * __library_Functions: the library of Function node, identified by :class:`.FunctionEnum`
        * __library_Widgets: the library of GUI widgets, identified by :class:`.WidgetEnum`
"""

from __future__ import unicode_literals
import sys
import math

from pysbs import sbsenum
from pysbs import python_helpers
from pysbs.api_decorators import doc_module_attributes,handle_exceptions,checkFirstParamIsAString
from . import sbsfilters
from . import sbsfxmapnodes
from . import sbsfunctions
from . import sbswidgets


# Library of Filters
__library_Filters = {
    sbsenum.FilterEnum.BITMAP                : sbsfilters.filter_BITMAP                 ,
    sbsenum.FilterEnum.BLEND                 : sbsfilters.filter_BLEND                  ,
    sbsenum.FilterEnum.BLUR                  : sbsfilters.filter_BLUR                   ,
    sbsenum.FilterEnum.COMPINSTANCE          : sbsfilters.filter_COMPINSTANCE           ,
    sbsenum.FilterEnum.CURVE                 : sbsfilters.filter_CURVE                  ,
    sbsenum.FilterEnum.DIRECTIONALMOTIONBLUR : sbsfilters.filter_DIRECTIONALMOTIONBLUR  ,
    sbsenum.FilterEnum.DIRECTIONALWARP       : sbsfilters.filter_DIRECTIONALWARP        ,
    sbsenum.FilterEnum.DISTANCE              : sbsfilters.filter_DISTANCE               ,
    sbsenum.FilterEnum.DYNAMICGRADIENT       : sbsfilters.filter_DYNAMICGRADIENT        ,
    sbsenum.FilterEnum.EMBOSS                : sbsfilters.filter_EMBOSS                 ,
    sbsenum.FilterEnum.FXMAPS                : sbsfilters.filter_FXMAPS                 ,
    sbsenum.FilterEnum.GRADIENT              : sbsfilters.filter_GRADIENT               ,
    sbsenum.FilterEnum.GRAYSCALECONVERSION   : sbsfilters.filter_GRAYSCALECONVERSION    ,
    sbsenum.FilterEnum.HSL                   : sbsfilters.filter_HSL                    ,
    sbsenum.FilterEnum.LEVELS                : sbsfilters.filter_LEVELS                 ,
    sbsenum.FilterEnum.NORMAL                : sbsfilters.filter_NORMAL                 ,
    sbsenum.FilterEnum.PIXEL_PROCESSOR       : sbsfilters.filter_PIXEL_PROCESSOR        ,
    sbsenum.FilterEnum.SHARPEN               : sbsfilters.filter_SHARPEN                ,
    sbsenum.FilterEnum.SHUFFLE               : sbsfilters.filter_SHUFFLE                ,
    sbsenum.FilterEnum.SVG                   : sbsfilters.filter_SVG                    ,
    sbsenum.FilterEnum.TEXT                  : sbsfilters.filter_TEXT                   ,
    sbsenum.FilterEnum.TRANSFORMATION        : sbsfilters.filter_TRANSFORMATION         ,
    sbsenum.FilterEnum.UNIFORM               : sbsfilters.filter_UNIFORM                ,
    sbsenum.FilterEnum.WARP                  : sbsfilters.filter_WARP                   ,
    sbsenum.FilterEnum.VALUE_PROCESSOR       : sbsfilters.filter_VALUE_PROCESSOR        ,
    sbsenum.FilterEnum.PASSTHROUGH           : sbsfilters.filter_PASSTHROUGH            ,
}

# Library of FxMaps nodes
__library_FxMapNodes = {
    sbsenum.FxMapNodeEnum.ITERATE     : sbsfxmapnodes.fxmap_ITERATE  ,
    sbsenum.FxMapNodeEnum.QUADRANT    : sbsfxmapnodes.fxmap_QUADRANT ,
    sbsenum.FxMapNodeEnum.SWITCH      : sbsfxmapnodes.fxmap_SWITCH,
    sbsenum.FxMapNodeEnum.PASSTHROUGH : sbsfxmapnodes.fxmap_PASSTHROUGH
 }

# Library of Functions
__library_Functions = {
    sbsenum.FunctionEnum.SEQUENCE      : sbsfunctions.function_SEQUENCE      ,
    sbsenum.FunctionEnum.IF_ELSE       : sbsfunctions.function_IF_ELSE       ,
    sbsenum.FunctionEnum.SET           : sbsfunctions.function_SET           ,
    sbsenum.FunctionEnum.GET_BOOL      : sbsfunctions.function_GET_BOOL      ,
    sbsenum.FunctionEnum.GET_INTEGER1  : sbsfunctions.function_GET_INTEGER1  ,
    sbsenum.FunctionEnum.GET_INTEGER2  : sbsfunctions.function_GET_INTEGER2  ,
    sbsenum.FunctionEnum.GET_INTEGER3  : sbsfunctions.function_GET_INTEGER3  ,
    sbsenum.FunctionEnum.GET_INTEGER4  : sbsfunctions.function_GET_INTEGER4  ,
    sbsenum.FunctionEnum.GET_FLOAT1    : sbsfunctions.function_GET_FLOAT1    ,
    sbsenum.FunctionEnum.GET_FLOAT2    : sbsfunctions.function_GET_FLOAT2    ,
    sbsenum.FunctionEnum.GET_FLOAT3    : sbsfunctions.function_GET_FLOAT3    ,
    sbsenum.FunctionEnum.GET_FLOAT4    : sbsfunctions.function_GET_FLOAT4    ,
    sbsenum.FunctionEnum.GET_STRING    : sbsfunctions.function_GET_STRING    ,
    sbsenum.FunctionEnum.CONST_BOOL    : sbsfunctions.function_CONST_BOOL    ,
    sbsenum.FunctionEnum.CONST_INT     : sbsfunctions.function_CONST_INT     ,
    sbsenum.FunctionEnum.CONST_INT2    : sbsfunctions.function_CONST_INT2    ,
    sbsenum.FunctionEnum.CONST_INT3    : sbsfunctions.function_CONST_INT3    ,
    sbsenum.FunctionEnum.CONST_INT4    : sbsfunctions.function_CONST_INT4    ,
    sbsenum.FunctionEnum.CONST_FLOAT   : sbsfunctions.function_CONST_FLOAT   ,
    sbsenum.FunctionEnum.CONST_FLOAT2  : sbsfunctions.function_CONST_FLOAT2  ,
    sbsenum.FunctionEnum.CONST_FLOAT3  : sbsfunctions.function_CONST_FLOAT3  ,
    sbsenum.FunctionEnum.CONST_FLOAT4  : sbsfunctions.function_CONST_FLOAT4  ,
    sbsenum.FunctionEnum.CONST_STRING  : sbsfunctions.function_CONST_STRING  ,
    sbsenum.FunctionEnum.INSTANCE      : sbsfunctions.function_INSTANCE      ,
    sbsenum.FunctionEnum.VECTOR2       : sbsfunctions.function_VECTOR2       ,
    sbsenum.FunctionEnum.VECTOR3       : sbsfunctions.function_VECTOR3       ,
    sbsenum.FunctionEnum.VECTOR4       : sbsfunctions.function_VECTOR4       ,
    sbsenum.FunctionEnum.SWIZZLE1      : sbsfunctions.function_SWIZZLE1      ,
    sbsenum.FunctionEnum.SWIZZLE2      : sbsfunctions.function_SWIZZLE2      ,
    sbsenum.FunctionEnum.SWIZZLE3      : sbsfunctions.function_SWIZZLE3      ,
    sbsenum.FunctionEnum.SWIZZLE4      : sbsfunctions.function_SWIZZLE4      ,
    sbsenum.FunctionEnum.VECTOR_INT2   : sbsfunctions.function_VECTOR_INT2   ,
    sbsenum.FunctionEnum.VECTOR_INT3   : sbsfunctions.function_VECTOR_INT3   ,
    sbsenum.FunctionEnum.VECTOR_INT4   : sbsfunctions.function_VECTOR_INT4   ,
    sbsenum.FunctionEnum.SWIZZLE_INT1  : sbsfunctions.function_SWIZZLE_INT1  ,
    sbsenum.FunctionEnum.SWIZZLE_INT2  : sbsfunctions.function_SWIZZLE_INT2  ,
    sbsenum.FunctionEnum.SWIZZLE_INT3  : sbsfunctions.function_SWIZZLE_INT3  ,
    sbsenum.FunctionEnum.SWIZZLE_INT4  : sbsfunctions.function_SWIZZLE_INT4  ,
    sbsenum.FunctionEnum.TO_INT        : sbsfunctions.function_TO_INT        ,
    sbsenum.FunctionEnum.TO_INT2       : sbsfunctions.function_TO_INT2       ,
    sbsenum.FunctionEnum.TO_INT3       : sbsfunctions.function_TO_INT3       ,
    sbsenum.FunctionEnum.TO_INT4       : sbsfunctions.function_TO_INT4       ,
    sbsenum.FunctionEnum.TO_FLOAT      : sbsfunctions.function_TO_FLOAT      ,
    sbsenum.FunctionEnum.TO_FLOAT2     : sbsfunctions.function_TO_FLOAT2     ,
    sbsenum.FunctionEnum.TO_FLOAT3     : sbsfunctions.function_TO_FLOAT3     ,
    sbsenum.FunctionEnum.TO_FLOAT4     : sbsfunctions.function_TO_FLOAT4     ,
    sbsenum.FunctionEnum.ADD           : sbsfunctions.function_ADD           ,
    sbsenum.FunctionEnum.SUB           : sbsfunctions.function_SUB           ,
    sbsenum.FunctionEnum.MUL           : sbsfunctions.function_MUL           ,
    sbsenum.FunctionEnum.MUL_SCALAR    : sbsfunctions.function_MUL_SCALAR    ,
    sbsenum.FunctionEnum.DIV           : sbsfunctions.function_DIV           ,
    sbsenum.FunctionEnum.NEG           : sbsfunctions.function_NEG           ,
    sbsenum.FunctionEnum.MOD           : sbsfunctions.function_MOD           ,
    sbsenum.FunctionEnum.DOT           : sbsfunctions.function_DOT           ,
    sbsenum.FunctionEnum.CROSS         : sbsfunctions.function_CROSS         ,
    sbsenum.FunctionEnum.AND           : sbsfunctions.function_AND           ,
    sbsenum.FunctionEnum.OR            : sbsfunctions.function_OR            ,
    sbsenum.FunctionEnum.NOT           : sbsfunctions.function_NOT           ,
    sbsenum.FunctionEnum.EQ            : sbsfunctions.function_EQ            ,
    sbsenum.FunctionEnum.NOT_EQ        : sbsfunctions.function_NOT_EQ        ,
    sbsenum.FunctionEnum.GREATER       : sbsfunctions.function_GREATER       ,
    sbsenum.FunctionEnum.GREATER_EQUAL : sbsfunctions.function_GREATER_EQUAL ,
    sbsenum.FunctionEnum.LOWER         : sbsfunctions.function_LOWER         ,
    sbsenum.FunctionEnum.LOWER_EQUAL   : sbsfunctions.function_LOWER_EQUAL   ,
    sbsenum.FunctionEnum.ABS           : sbsfunctions.function_ABS           ,
    sbsenum.FunctionEnum.FLOOR         : sbsfunctions.function_FLOOR         ,
    sbsenum.FunctionEnum.CEIL          : sbsfunctions.function_CEIL          ,
    sbsenum.FunctionEnum.COS           : sbsfunctions.function_COS           ,
    sbsenum.FunctionEnum.SIN           : sbsfunctions.function_SIN           ,
    sbsenum.FunctionEnum.SQRT          : sbsfunctions.function_SQRT          ,
    sbsenum.FunctionEnum.LOG           : sbsfunctions.function_LOG           ,
    sbsenum.FunctionEnum.LOG2          : sbsfunctions.function_LOG2          ,
    sbsenum.FunctionEnum.EXP           : sbsfunctions.function_EXP           ,
    sbsenum.FunctionEnum.POW2          : sbsfunctions.function_POW2          ,
    sbsenum.FunctionEnum.TAN           : sbsfunctions.function_TAN           ,
    sbsenum.FunctionEnum.ATAN2         : sbsfunctions.function_ATAN2         ,
    sbsenum.FunctionEnum.CARTESIAN     : sbsfunctions.function_CARTESIAN     ,
    sbsenum.FunctionEnum.LERP          : sbsfunctions.function_LERP          ,
    sbsenum.FunctionEnum.MIN           : sbsfunctions.function_MIN           ,
    sbsenum.FunctionEnum.MAX           : sbsfunctions.function_MAX           ,
    sbsenum.FunctionEnum.RAND          : sbsfunctions.function_RAND          ,
    sbsenum.FunctionEnum.SAMPLE_LUM    : sbsfunctions.function_SAMPLE_LUM    ,
    sbsenum.FunctionEnum.SAMPLE_COL    : sbsfunctions.function_SAMPLE_COL    ,
    sbsenum.FunctionEnum.PASSTHROUGH   : sbsfunctions.function_PASSTHROUGH   ,
}

# Library of Widgets
__library_Widgets = {
    sbsenum.WidgetEnum.BUTTON_BOOL            : sbswidgets.widget_Button_Bool          ,
    sbsenum.WidgetEnum.SLIDER_INT1            : sbswidgets.widget_Slider_Int1          ,
    sbsenum.WidgetEnum.SLIDER_INT2            : sbswidgets.widget_Slider_Int2          ,
    sbsenum.WidgetEnum.SLIDER_INT3            : sbswidgets.widget_Slider_Int3          ,
    sbsenum.WidgetEnum.SLIDER_INT4            : sbswidgets.widget_Slider_Int4          ,
    sbsenum.WidgetEnum.SLIDER_FLOAT1          : sbswidgets.widget_Slider_Float1        ,
    sbsenum.WidgetEnum.SLIDER_FLOAT2          : sbswidgets.widget_Slider_Float2        ,
    sbsenum.WidgetEnum.SLIDER_FLOAT3          : sbswidgets.widget_Slider_Float3        ,
    sbsenum.WidgetEnum.SLIDER_FLOAT4          : sbswidgets.widget_Slider_Float4        ,
    sbsenum.WidgetEnum.DROPDOWN_INT1          : sbswidgets.widget_DropDown_Int1        ,
    sbsenum.WidgetEnum.SIZE_POW2_INT2         : sbswidgets.widget_Size_Pow2_Int2       ,
    sbsenum.WidgetEnum.ANGLE_FLOAT1           : sbswidgets.widget_Angle_Float1         ,
    sbsenum.WidgetEnum.COLOR_FLOAT1           : sbswidgets.widget_Color_Float1         ,
    sbsenum.WidgetEnum.COLOR_FLOAT3           : sbswidgets.widget_Color_Float3         ,
    sbsenum.WidgetEnum.COLOR_FLOAT4           : sbswidgets.widget_Color_Float4         ,
    sbsenum.WidgetEnum.MATRIX_INVERSE_FLOAT4  : sbswidgets.widget_Matrix_Inverse_Float4,
    sbsenum.WidgetEnum.MATRIX_FORWARD_FLOAT4  : sbswidgets.widget_Matrix_Forward_Float4,
    sbsenum.WidgetEnum.TEXT_STRING            : sbswidgets.widget_Text_String          ,
    sbsenum.WidgetEnum.POSITION_FLOAT2        : sbswidgets.widget_Position_Float2      ,
    sbsenum.WidgetEnum.OFFSET_FLOAT2          : sbswidgets.widget_Offset_Float2
}



@handle_exceptions()
def getFilterDefinition(aFilter):
    """
    getFilterDefinition(aFilter)
    Get the definition of the given filter (inputs, outputs, parameters)

    :param aFilter: filter identifier
    :type aFilter: :class:`.FilterEnum` or str
    :return: a :class:`.CompNodeDef` object if found, None otherwise
    """
    aKey = __convertToEnum(aFilter, getFilterEnum)
    return __library_Filters[aKey]

@handle_exceptions()
def getInputBridgeDefinition():
    """
    getInputBridgeDefinition()
    Get the definition of an input bridge node (inputs, outputs, parameters)

    :return: a :class:`.CompNodeDef` object if found, None otherwise
    """
    return sbsfilters.def_InputBridge

@handle_exceptions()
def getOutputBridgeDefinition():
    """
    getOutputBridgeDefinition()
    Get the definition of an output bridge node (inputs, outputs, parameters)

    :return: a :class:`.CompNodeDef` object if found, None otherwise
    """
    return sbsfilters.def_OutputBridge


@handle_exceptions()
def getFunctionDefinition(aFunction):
    """
    getFunctionDefinition(aFunction)
    Get the definition of the given function (inputs, outputs, parameters)

    :param aFunction: function identifier
    :type aFunction: :class:`.FunctionEnum` or str
    :return: a :class:`.FunctionDef` object if found, None otherwise
    """
    aKey = __convertToEnum(aFunction, getFunctionEnum)
    return __library_Functions[aKey]

@handle_exceptions()
def getFxMapNodeDefinition(aFxMapNode):
    """
    getFxMapNodeDefinition(aFxMapNode)
    Get the definition of the given FxMap node (inputs, outputs, parameters)

    :param aFxMapNode: FxMap node identifier
    :type aFxMapNode: :class:`.FxMapNodeEnum` or str
    :return: a :class:`.CompNodeDef` object if found, None otherwise
    """
    aKey = __convertToEnum(aFxMapNode, getFxMapNodeEnum)
    return __library_FxMapNodes[aKey]


@handle_exceptions()
def getIterationParamInput():
    """
    getIterationParamInput()
    Get the description of the 'iteration' parameter

    :return: the :class:`.CompNodeParam` describing this parameter
    """
    return sbsfilters.def_IterationParamInput

@handle_exceptions()
@checkFirstParamIsAString
def getFilterEnum(aFilterName):
    """
    getFilterEnum(aFilterName)
    Get the enum value of the given filter

    :param aFilterName: filter identifier
    :type aFilterName: str
    :return: the filter as a :class:`.FilterEnum`
    """
    return next((key for key, value in __library_Filters.items() if value.mIdentifier == aFilterName), None)


@handle_exceptions()
@checkFirstParamIsAString
def getFunctionEnum(aFunctionName):
    """
    getFunctionEnum(aFunctionName)
    Get the enum value of the given function

    :param aFunctionName: function identifier
    :type aFunctionName: str
    :return: the function as a :class:`.FunctionEnum`
    """
    return next((key for key, value in __library_Functions.items() if value.mIdentifier == aFunctionName), None)


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
@checkFirstParamIsAString
def getFxMapNodeEnum(aFxMapNodeName):
    """
    getFxMapNodeEnum(aFxMapNodeName)
    Get the enum value of the given function

    :param aFxMapNodeName: FxMap node identifier
    :type aFxMapNodeName: str
    :return: the FxMap node as a :class:`.FxMapNodeEnum`
    """
    return next((key for key, value in __library_FxMapNodes.items() if value.mIdentifier == aFxMapNodeName), None)

@handle_exceptions()
def getDefaultWidget(aWidget):
    """
    getDefaultWidget(aWidget)
    Get the given widget

    :param aWidget: widget identifier
    :type aWidget: :class:`.WidgetEnum`
    :return: the widget as a :class:`.InputParamWidget`
    """
    return __library_Widgets[aWidget]


# ==========================================================================
# Private
# ==========================================================================
def __convertToEnum(aKey, aGetEnumFunction):
    if python_helpers.isStringOrUnicode(aKey):
        aKeyName = aKey
        aKey = aGetEnumFunction(aKeyName)
        if aKey is None:
            raise KeyError(aKeyName)
    return aKey


doc_module_attributes(sys.modules[__name__])
