# coding: utf-8
"""
Module **sbsfilter** provides the library of substance filters and their definition (inputs, outputs, parameters):

    * filter_BITMAP
    * filter_BLEND
    * filter_BLUR
    * filter_COMPINSTANCE
    * filter_CURVE
    * filter_DIRECTIONALMOTIONBLUR
    * filter_DIRECTIONALWARP
    * filter_DISTANCE
    * filter_DYNAMICGRADIENT
    * filter_EMBOSS
    * filter_FXMAPS
    * filter_GRADIENT
    * filter_GRAYSCALECONVERSION
    * filter_HSL
    * filter_LEVELS
    * filter_NORMAL
    * filter_PIXEL_PROCESSOR
    * filter_SHARPEN
    * filter_SHUFFLE
    * filter_SVG
    * filter_TEXT
    * filter_TRANSFORMATION
    * filter_UNIFORM
    * filter_VALUE_PROCESSOR
    * filter_WARP

It also provides the definition of the compositing node input and output:

    * def_InputBridge
    * def_OutputBridge


.. note:: Note that in addition to their specific parameters, Filters and FxMaps node have this set of BaseParameters:

    - CompNodeParam(sbsenum.CompNodeParamEnum.OUTPUT_SIZE,   sbsenum.ParamTypeEnum.INTEGER2, '0 0'                                 )
    - CompNodeParam(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT, sbsenum.ParamTypeEnum.INTEGER1, sbsenum.OutputFormatEnum.FORMAT_8BITS )
    - CompNodeParam(sbsenum.CompNodeParamEnum.PIXEL_SIZE,    sbsenum.ParamTypeEnum.FLOAT2  , '1.0 1.0'                             )
    - CompNodeParam(sbsenum.CompNodeParamEnum.PIXEL_RATIO,   sbsenum.ParamTypeEnum.INTEGER1, sbsenum.PixelRatioEnum.SQUARE         )
    - CompNodeParam(sbsenum.CompNodeParamEnum.TILING_MODE,   sbsenum.ParamTypeEnum.INTEGER1, sbsenum.TilingEnum.H_AND_V_TILING     )
    - CompNodeParam(sbsenum.CompNodeParamEnum.QUALITY,       sbsenum.ParamTypeEnum.INTEGER1, sbsenum.QualityEnum.MEDIUM            )
    - CompNodeParam(sbsenum.CompNodeParamEnum.RANDOM_SEED,   sbsenum.ParamTypeEnum.INTEGER1, '0'
"""

from __future__ import unicode_literals
import sys

from pysbs import sbsenum
from pysbs.api_decorators import doc_module_attributes

from .sbslibclasses import CompNodeDef,CompNodeInput,CompNodeOutput,CompNodeParam


def_OutputBridge = CompNodeDef(
    aIdentifier='output',
    aOutputs=[CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs=[CompNodeInput(sbsenum.InputEnum.INPUT_NODE_OUTPUT, sbsenum.TypeMasksEnum.OUTPUT_DEF, True)],
    aParameters=[])

def_InputBridge = CompNodeDef(
    aIdentifier='input',
    aOutputs=[CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs=[],
    aParameters=[CompNodeParam(sbsenum.CompNodeParamEnum.BITMAP_RESOURCE_PATH, sbsenum.ParamTypeEnum.PATH, '')],
    aInheritance=[sbsenum.ParamInheritanceEnum.PARENT, sbsenum.ParamInheritanceEnum.ABSOLUTE])

def_IterationParamInput = CompNodeParam(sbsenum.CompNodeParamEnum.ITERATION, sbsenum.ParamTypeEnum.INTEGER1, '0')



filter_BITMAP = CompNodeDef(
    aIdentifier = 'bitmap',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE, sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.ColorModeEnum.COLOR),
                   CompNodeParam(sbsenum.CompNodeParamEnum.BITMAP_RESOURCE_PATH, sbsenum.ParamTypeEnum.PATH, '' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.BITMAP_RESIZE_METHOD, sbsenum.ParamTypeEnum.INTEGER1, sbsenum.BitmapResizeMethodEnum.SMOOTH_STRETCH)],
    aInheritance= [sbsenum.ParamInheritanceEnum.PARENT, sbsenum.ParamInheritanceEnum.ABSOLUTE])

filter_BLEND = CompNodeDef(
    aIdentifier = 'blend',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)]   ,
    aInputs =     [CompNodeInput(sbsenum.InputEnum.SOURCE,      sbsenum.ParamTypeEnum.ENTRY_VARIANT  , True  ),
                   CompNodeInput(sbsenum.InputEnum.DESTINATION, sbsenum.ParamTypeEnum.ENTRY_VARIANT  , False ),
                   CompNodeInput(sbsenum.InputEnum.OPACITY,     sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE, False )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.OPACITY,        sbsenum.ParamTypeEnum.FLOAT1  , '1.0'                                     ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.ALPHA_BLENDING, sbsenum.ParamTypeEnum.INTEGER1, sbsenum.AlphaBlendingEnum.USE_SOURCE_ALPHA),
                   CompNodeParam(sbsenum.CompNodeParamEnum.BLENDING_MODE,  sbsenum.ParamTypeEnum.INTEGER1, sbsenum.BlendBlendingModeEnum.COPY        ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.CROPPING_AREA,  sbsenum.ParamTypeEnum.FLOAT4  , '0.0 1.0 0.0 1.0'                        )])

filter_BLUR = CompNodeDef(
    aIdentifier = 'blur',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_VARIANT    , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.INTENSITY, sbsenum.ParamTypeEnum.FLOAT1  , '10.0' )])

filter_COMPINSTANCE = CompNodeDef(
    aIdentifier = 'compinstance',
    aOutputs =    [],
    aInputs =     [],
    aParameters = [],
    aInheritance= [sbsenum.ParamInheritanceEnum.PARENT, sbsenum.ParamInheritanceEnum.ABSOLUTE])

filter_CURVE = CompNodeDef(
    aIdentifier = 'curve',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_COLOR)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_VARIANT  , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.GRADIENT_ADDRESSING, sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.GradientAddressingEnum.CLAMP)])

filter_DIRECTIONALMOTIONBLUR = CompNodeDef(
    aIdentifier = 'dirmotionblur',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)] ,
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_VARIANT   , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.INTENSITY,  sbsenum.ParamTypeEnum.FLOAT1, '10.0' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.BLUR_ANGLE, sbsenum.ParamTypeEnum.FLOAT1, '0.0'  )])

filter_DIRECTIONALWARP = CompNodeDef(
    aIdentifier = 'directionalwarp',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,          sbsenum.ParamTypeEnum.ENTRY_VARIANT  , True  ),
                   CompNodeInput(sbsenum.InputEnum.INPUT_INTENSITY, sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE, False )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.INTENSITY,  sbsenum.ParamTypeEnum.FLOAT1, '10.0'    ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.WARP_ANGLE, sbsenum.ParamTypeEnum.FLOAT1, '0.0'     )])

filter_DISTANCE = CompNodeDef(
    aIdentifier = 'distance',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.MASK,     sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE   , True      ),
                   CompNodeInput(sbsenum.InputEnum.SOURCE,   sbsenum.ParamTypeEnum.ENTRY_VARIANT     , False )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE,       sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.ColorModeEnum.GRAYSCALE    ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.MAX_DISTANCE,     sbsenum.ParamTypeEnum.FLOAT1 , '10.0'                             ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.COMBINE_DISTANCE, sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.CombineDistanceEnum.COMBINE)])

filter_DYNAMICGRADIENT = CompNodeDef(
    aIdentifier = 'dyngradient',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE   , True      ),
                   CompNodeInput(sbsenum.InputEnum.INPUT2,   sbsenum.ParamTypeEnum.ENTRY_VARIANT     , False )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.GRADIENT_ADDRESSING,  sbsenum.ParamTypeEnum.BOOLEAN,  sbsenum.GradientAddressingEnum.CLAMP),
                   CompNodeParam(sbsenum.CompNodeParamEnum.GRADIENT_ORIENTATION, sbsenum.ParamTypeEnum.INTEGER1, sbsenum.GradientOrientationEnum.HORIZONTAL),
                   CompNodeParam(sbsenum.CompNodeParamEnum.GRADIENT_POSITION,    sbsenum.ParamTypeEnum.FLOAT1  , '0.0'                                    )])

filter_EMBOSS = CompNodeDef(
    aIdentifier = 'emboss',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,         sbsenum.ParamTypeEnum.ENTRY_VARIANT  , True  ),
                   CompNodeInput(sbsenum.InputEnum.INPUT_GRADIENT, sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE, False )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.INTENSITY,       sbsenum.ParamTypeEnum.FLOAT1       , '5.0'             ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.LIGHT_ANGLE,     sbsenum.ParamTypeEnum.FLOAT1       , '0.0'             ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.HIGHLIGHT_COLOR, sbsenum.ParamTypeEnum.FLOAT_VARIANT, '1.0 1.0 1.0 1.0' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.SHADOW_COLOR,    sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 0.0' )])

filter_FXMAPS = CompNodeDef(
    aIdentifier = 'fxmaps',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.BACKGROUND,    sbsenum.ParamTypeEnum.ENTRY_VARIANT , True  ),
                   CompNodeInput(sbsenum.InputEnum.INPUT_PATTERN, sbsenum.ParamTypeEnum.ENTRY_VARIANT , False, True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE,   sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.ColorModeEnum.COLOR),
                   CompNodeParam(sbsenum.CompNodeParamEnum.BACKGROUND,   sbsenum.ParamTypeEnum.FLOAT4 , '0.0 0.0 0.0 0.0'          ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.RENDER_REGION,sbsenum.ParamTypeEnum.FLOAT4 , '0.0 1.0 0.0 1.0'          ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TILING_REGION,sbsenum.ParamTypeEnum.FLOAT4 , '0.0 1.0 0.0 1.0'          ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.ROUGHNESS,    sbsenum.ParamTypeEnum.FLOAT1 , '1.0'                      ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.OPACITY,      sbsenum.ParamTypeEnum.FLOAT1 , '1.0'                      )])

filter_GRADIENT = CompNodeDef(
    aIdentifier = 'gradient',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_COLOR)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE  , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE,          sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.ColorModeEnum.COLOR),
                   CompNodeParam(sbsenum.CompNodeParamEnum.GRADIENT_ADDRESSING, sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.GradientAddressingEnum.CLAMP)])

filter_GRAYSCALECONVERSION = CompNodeDef(
    aIdentifier = 'grayscaleconversion',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_COLOR      , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.CHANNELS_WEIGHTS, sbsenum.ParamTypeEnum.FLOAT4 , '0.33 0.33 0.33 0.0' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.FLATTEN_ALPHA,    sbsenum.ParamTypeEnum.BOOLEAN, '0'                  ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.BACKGROUND_VALUE, sbsenum.ParamTypeEnum.FLOAT1 , '1.0'                )])

filter_HSL = CompNodeDef(
    aIdentifier = 'hsl',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_COLOR)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_COLOR     , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.HUE,        sbsenum.ParamTypeEnum.FLOAT1, '0.5' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.SATURATION, sbsenum.ParamTypeEnum.FLOAT1, '0.5' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.LIGHTNESS,  sbsenum.ParamTypeEnum.FLOAT1, '0.5' )])

filter_LEVELS = CompNodeDef(
    aIdentifier = 'levels',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_VARIANT     , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.LEVEL_IN_LOW,   sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 0.0' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.LEVEL_IN_HIGH,  sbsenum.ParamTypeEnum.FLOAT_VARIANT, '1.0 1.0 1.0 1.0' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.LEVEL_IN_MID,   sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.5 0.5 0.5 0.5' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.LEVEL_OUT_LOW,  sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 0.0' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.LEVEL_OUT_HIGH, sbsenum.ParamTypeEnum.FLOAT_VARIANT, '1.0 1.0 1.0 1.0' ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.CLAMP_IN_TERM,  sbsenum.ParamTypeEnum.BOOLEAN      , '1'              )])

filter_NORMAL = CompNodeDef(
    aIdentifier = 'normal',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_COLOR)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE   , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.INTENSITY,     sbsenum.ParamTypeEnum.FLOAT1 , '1.0'                            ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.NORMAL_FORMAT, sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.NormalFormatEnum.DIRECTX),
                   CompNodeParam(sbsenum.CompNodeParamEnum.NORMAL_ALPHA_CHANNEL,
                                 sbsenum.ParamTypeEnum.BOOLEAN,
                                 sbsenum.NormalAlphaChannelContentEnum.INPUT_ALPHA)])

filter_PIXEL_PROCESSOR = CompNodeDef(
    aIdentifier = 'pixelprocessor',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)] ,
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT,    sbsenum.ParamTypeEnum.ENTRY_VARIANT   , True, True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE,sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.ColorModeEnum.COLOR),
                   CompNodeParam(sbsenum.CompNodeParamEnum.PER_PIXEL, sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 1.0' )],
    aInheritance= [sbsenum.ParamInheritanceEnum.PARENT, sbsenum.ParamInheritanceEnum.ABSOLUTE])

filter_SHARPEN = CompNodeDef(
    aIdentifier = 'sharpen',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_VARIANT  , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.INTENSITY, sbsenum.ParamTypeEnum.FLOAT1, '1.0'     )])

filter_SHUFFLE = CompNodeDef(
    aIdentifier = 'shuffle',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_COLOR)] ,
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_VARIANT , True  ),
                   CompNodeInput(sbsenum.InputEnum.INPUT2,   sbsenum.ParamTypeEnum.ENTRY_VARIANT , False )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.CHANNEL_RED,   sbsenum.ParamTypeEnum.INTEGER1, sbsenum.ChannelShuffleEnum.INPUT1_RED   ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.CHANNEL_GREEN, sbsenum.ParamTypeEnum.INTEGER1, sbsenum.ChannelShuffleEnum.INPUT1_GREEN ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.CHANNEL_BLUE,  sbsenum.ParamTypeEnum.INTEGER1, sbsenum.ChannelShuffleEnum.INPUT1_BLUE  ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.CHANNEL_ALPHA, sbsenum.ParamTypeEnum.INTEGER1, sbsenum.ChannelShuffleEnum.INPUT1_ALPHA )])

filter_SVG = CompNodeDef(
    aIdentifier = 'svg',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.BACKGROUND, sbsenum.ParamTypeEnum.ENTRY_VARIANT, True  )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE,        sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.ColorModeEnum.COLOR),
                   CompNodeParam(sbsenum.CompNodeParamEnum.BACKGROUND,        sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 0.0'    ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.SVG_RESOURCE_PATH, sbsenum.ParamTypeEnum.PATH,    ''                         )])

filter_TEXT = CompNodeDef(
    aIdentifier = 'text',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.BACKGROUND, sbsenum.ParamTypeEnum.ENTRY_VARIANT, True  )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.BACKGROUND,      sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 1.0'               ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE,      sbsenum.ParamTypeEnum.BOOLEAN      , sbsenum.ColorModeEnum.GRAYSCALE ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TEXT,            sbsenum.ParamTypeEnum.STRING       , ''                              ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TEXT_ALIGN,      sbsenum.ParamTypeEnum.INTEGER1     , sbsenum.TextAlignEnum.CENTER    ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TEXT_FONT,       sbsenum.ParamTypeEnum.STRING       , ''                              ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TEXT_FONT_COLOR, sbsenum.ParamTypeEnum.FLOAT_VARIANT, '1.0 1.0 1.0 1.0'               ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TEXT_FONT_SIZE,  sbsenum.ParamTypeEnum.FLOAT1       , '0.25'                          ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TEXT_POSITION,   sbsenum.ParamTypeEnum.FLOAT2       , '0.0 0.0'                       ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.TRANSFORM_MATRIX,sbsenum.ParamTypeEnum.FLOAT4       , '1.0 0.0 0.0 1.0'               )])

filter_TRANSFORMATION = CompNodeDef(
    aIdentifier = 'transformation',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,   sbsenum.ParamTypeEnum.ENTRY_VARIANT     , True )],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.TRANSFORM_MATRIX,sbsenum.ParamTypeEnum.FLOAT4    , '1.0 0.0 0.0 1.0'                ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.OFFSET,       sbsenum.ParamTypeEnum.FLOAT2       , '0.0 0.0'                        ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.MIPMAP_MODE,  sbsenum.ParamTypeEnum.INTEGER1     , sbsenum.MipMapModeEnum.AUTOMATIC ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.MIPMAP_LEVEL, sbsenum.ParamTypeEnum.INTEGER1     , '0'                              ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.MATTE_COLOR,  sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 0.0'                ),
                   CompNodeParam(sbsenum.CompNodeParamEnum.FILTERING,    sbsenum.ParamTypeEnum.INTEGER1     , sbsenum.FilteringEnum.BILINEAR   )])

filter_UNIFORM = CompNodeDef(
    aIdentifier = 'uniform',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.COLOR_MODE,   sbsenum.ParamTypeEnum.BOOLEAN, sbsenum.ColorModeEnum.COLOR),
                   CompNodeParam(sbsenum.CompNodeParamEnum.OUTPUT_COLOR, sbsenum.ParamTypeEnum.FLOAT_VARIANT, '0.0 0.0 0.0 1.0' )],
    aInheritance= [sbsenum.ParamInheritanceEnum.PARENT, sbsenum.ParamInheritanceEnum.ABSOLUTE])

filter_VALUE_PROCESSOR = CompNodeDef(
    aIdentifier = 'valueprocessor',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.FLOAT1)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT, sbsenum.TypeMasksEnum.NUMERIC, True, True)],
    aInheritance= [sbsenum.ParamInheritanceEnum.PARENT, sbsenum.ParamInheritanceEnum.ABSOLUTE])

filter_WARP = CompNodeDef(
    aIdentifier = 'warp',
    aOutputs =    [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs =     [CompNodeInput(sbsenum.InputEnum.INPUT1,         sbsenum.ParamTypeEnum.ENTRY_VARIANT  , True ),
                   CompNodeInput(sbsenum.InputEnum.INPUT_GRADIENT, sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE, False)],
    aParameters = [CompNodeParam(sbsenum.CompNodeParamEnum.INTENSITY,sbsenum.ParamTypeEnum.FLOAT1, '1.0'       )])

filter_PASSTHROUGH = CompNodeDef(
    aIdentifier = 'passthrough',
    aOutputs = [CompNodeOutput(sbsenum.OutputEnum.OUTPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT)],
    aInputs = [CompNodeInput(sbsenum.InputEnum.INPUT, sbsenum.ParamTypeEnum.ENTRY_VARIANT, True, True)])

doc_module_attributes(sys.modules[__name__])
