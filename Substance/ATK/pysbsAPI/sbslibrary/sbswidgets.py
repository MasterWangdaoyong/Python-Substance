# coding: utf-8
"""
Module **sbswidgets** provides the library of GUI widgets available when defining a graph input parameter:

    * widget_Button_Bool
    * widget_Slider_Int1
    * widget_Slider_Int2
    * widget_Slider_Int3
    * widget_Slider_Int4
    * widget_Slider_Float1
    * widget_Slider_Float2
    * widget_Slider_Float3
    * widget_Slider_Float4
    * widget_DropDown_Int1
    * widget_Size_Pow2_Int2
    * widget_Angle_Float1
    * widget_Color_Float1
    * widget_Color_Float3
    * widget_Color_Float4
    * widget_Matrix_Inverse_Float4
    * widget_Matrix_Forward_Float4
    * widget_Position_Float2
    * widget_Offset_Float2
    * widget_Text_String
"""

from __future__ import unicode_literals
import sys

from pysbs import sbsenum
from pysbs.api_decorators import doc_module_attributes

from .sbslibclasses import InputParamWidget,WidgetOption


widget_Button_Bool = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.BUTTON,
    aType    = sbsenum.ParamTypeEnum.BOOLEAN,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.BOOL_EDITOR_TYPE, sbsenum.ParamTypeEnum.STRING,  'pushbuttons'),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT         , sbsenum.ParamTypeEnum.BOOLEAN, '0'          ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0          , sbsenum.ParamTypeEnum.STRING,  'False'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1          , sbsenum.ParamTypeEnum.STRING,  'True'       )])

widget_Slider_Int1 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.INTEGER1,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.INTEGER1, '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.INTEGER1, '10'     ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.INTEGER1, '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.INTEGER1, '1'      )])

widget_Slider_Int2 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.INTEGER2,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.INTEGER2, '1;1'    ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.INTEGER1, '10'     ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.INTEGER1, '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.INTEGER1, '1'      )])

widget_Slider_Int3 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.INTEGER3,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.INTEGER3, '1;1;1'  ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL2    , sbsenum.ParamTypeEnum.STRING,   'Z'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.INTEGER1, '10'     ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.INTEGER1, '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.INTEGER1, '1'      )])

widget_Slider_Int4 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.INTEGER4,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.INTEGER4, '1;1;1;1'),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL2    , sbsenum.ParamTypeEnum.STRING,   'Z'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL3    , sbsenum.ParamTypeEnum.STRING,   'W'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.INTEGER1, '10'     ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.INTEGER1, '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.INTEGER1, '1'      )])

widget_Slider_Float1 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.FLOAT1,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.FLOAT1,   '0.01'   )])

widget_Slider_Float2 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.FLOAT2,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT2,   '1;1'    ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.FLOAT1,   '0.01'   )])

widget_Slider_Float3 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.FLOAT3,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT3,   '1;1;1'  ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL2    , sbsenum.ParamTypeEnum.STRING,   'Z'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.FLOAT1,   '0.01'   )])

widget_Slider_Float4 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SLIDER,
    aType    = sbsenum.ParamTypeEnum.FLOAT4,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT4,   '1;1;1;1'),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL2    , sbsenum.ParamTypeEnum.STRING,   'Z'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL3    , sbsenum.ParamTypeEnum.STRING,   'W'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.FLOAT1,   '0.01'   )])

widget_DropDown_Int1 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.DROP_DOWN_LIST,
    aType    = sbsenum.ParamTypeEnum.INTEGER1,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.PARAMETERS, sbsenum.ParamTypeEnum.STRING,   '0;0;0'  )])

widget_Size_Pow2_Int2= InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.SIZE_POW_2,
    aType    = sbsenum.ParamTypeEnum.INTEGER2,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.INTEGER2, '1;1'    ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.INTEGER1, '12'     ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.INTEGER1, '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION, sbsenum.ParamTypeEnum.STRING, 'sizepow2' )])

widget_Angle_Float1 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.ANGLE,
    aType    = sbsenum.ParamTypeEnum.FLOAT1,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION, sbsenum.ParamTypeEnum.STRING, 'angle' )])

widget_Color_Float1 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.COLOR,
    aType    = sbsenum.ParamTypeEnum.FLOAT1,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION, sbsenum.ParamTypeEnum.STRING, 'color' )])

widget_Color_Float3 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.COLOR,
    aType    = sbsenum.ParamTypeEnum.FLOAT3,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT3,   '1;1;1'  ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION, sbsenum.ParamTypeEnum.STRING, 'color' )])

widget_Color_Float4 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.COLOR,
    aType    = sbsenum.ParamTypeEnum.FLOAT4,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT4,   '1;1;1;1'),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION, sbsenum.ParamTypeEnum.STRING, 'color' )])

widget_Matrix_Inverse_Float4 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.TRANSFORMATION_INVERSE,
    aType    = sbsenum.ParamTypeEnum.FLOAT4,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT4,   '1;0;0;1'),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION, sbsenum.ParamTypeEnum.STRING, 'matrix' )])

widget_Matrix_Forward_Float4 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.TRANSFORMATION_FORWARD,
    aType    = sbsenum.ParamTypeEnum.FLOAT4,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT4,   '1;0;0;1'),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.VALUE_INTERPRETATION, sbsenum.ParamTypeEnum.STRING, 'matrix' )])

widget_Position_Float2 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.POSITION,
    aType    = sbsenum.ParamTypeEnum.FLOAT2,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT2,   '0;0'    ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.FLOAT1,   '0.01'   )])

widget_Offset_Float2 = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.OFFSET,
    aType    = sbsenum.ParamTypeEnum.FLOAT2,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.CLAMP     , sbsenum.ParamTypeEnum.BOOLEAN,  '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.FLOAT2,   '0;0'    ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL0    , sbsenum.ParamTypeEnum.STRING,   'X'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.LABEL1    , sbsenum.ParamTypeEnum.STRING,   'Y'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MAX       , sbsenum.ParamTypeEnum.FLOAT1,   '1'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.MIN       , sbsenum.ParamTypeEnum.FLOAT1,   '0'      ),
                WidgetOption(sbsenum.WidgetOptionEnum.STEP      , sbsenum.ParamTypeEnum.FLOAT1,   '0.01'   )])

widget_Text_String = InputParamWidget(
    aWidget  = sbsenum.WidgetTypeEnum.TEXT,
    aType    = sbsenum.ParamTypeEnum.STRING,
    aOptions = [WidgetOption(sbsenum.WidgetOptionEnum.DEFAULT   , sbsenum.ParamTypeEnum.STRING,   '' )])


doc_module_attributes(sys.modules[__name__])
