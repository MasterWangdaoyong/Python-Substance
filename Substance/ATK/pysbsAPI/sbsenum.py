# coding: utf-8
"""
Module **sbsenum** provides all the enumeration used in Pysbs.
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_source_code_enum

@doc_source_code_enum
class ParamTypeEnum:
    """
    Enumeration of all the types manipulated by Substance Designer
    """
    DUMMY_TYPE          = 0
    ENTRY_COLOR         = 1
    ENTRY_GRAYSCALE     = 2
    ENTRY_VARIANT       = ENTRY_COLOR | ENTRY_GRAYSCALE         # grayscale or color entry
    BOOLEAN             = 4
    INTEGER1            = 16
    INTEGER2            = 32
    INTEGER3            = 64
    INTEGER4            = 128
    FLOAT1              = 256
    FLOAT2              = 512
    FLOAT3              = 1024
    FLOAT4              = 2048
    FLOAT_VARIANT       = FLOAT4 | FLOAT1                       # grayscale or color value
    ENTRY_COLOR_OPT     = ENTRY_COLOR | FLOAT4                  # optional color entry
    ENTRY_GRAYSCALE_OPT = ENTRY_GRAYSCALE | FLOAT1              # optional grayscale entry
    ENTRY_VARIANT_OPT   = ENTRY_COLOR_OPT | ENTRY_GRAYSCALE_OPT
    ENTRY_PARAMETER     = 4096                                  # parameter graph entry (used for fx-map)
    COMPLEX             = 8192
    STRING              = 16384
    PATH                = 32768
    VOID_TYPE           = 65536                                 # no return type, function only
    TEMPLATE1           = 131072                                # Template type 1, function only
    TEMPLATE2           = 262144                                # Template type 2, function only

@doc_source_code_enum
class InputValueTypeEnum:
    """
    Enumeration of all the types compatible with input values
    """
    BOOLEAN             = ParamTypeEnum.BOOLEAN
    INTEGER1            = ParamTypeEnum.INTEGER1
    INTEGER2            = ParamTypeEnum.INTEGER2
    INTEGER3            = ParamTypeEnum.INTEGER3
    INTEGER4            = ParamTypeEnum.INTEGER4
    FLOAT1              = ParamTypeEnum.FLOAT1
    FLOAT2              = ParamTypeEnum.FLOAT2
    FLOAT3              = ParamTypeEnum.FLOAT3
    FLOAT4              = ParamTypeEnum.FLOAT4

@doc_source_code_enum
class TypeMasksEnum:
    """
    Helper masks enumeration
    """
    ENTRY          = ParamTypeEnum.ENTRY_COLOR | ParamTypeEnum.ENTRY_GRAYSCALE
    INTEGER        = ParamTypeEnum.INTEGER1 | ParamTypeEnum.INTEGER2 | ParamTypeEnum.INTEGER3 | ParamTypeEnum.INTEGER4
    SINGLE         = ParamTypeEnum.BOOLEAN | ParamTypeEnum.INTEGER1 | ParamTypeEnum.FLOAT1
    DIM2           = ParamTypeEnum.INTEGER2| ParamTypeEnum.FLOAT2
    DIM3           = ParamTypeEnum.INTEGER3| ParamTypeEnum.FLOAT3
    DIM4           = ParamTypeEnum.INTEGER4| ParamTypeEnum.FLOAT4
    LIST           = DIM2 | DIM3 | DIM4
    FLOAT          = ParamTypeEnum.FLOAT1 | ParamTypeEnum.FLOAT2 | ParamTypeEnum.FLOAT3 | ParamTypeEnum.FLOAT4
    NUMERIC        = ParamTypeEnum.BOOLEAN | INTEGER | FLOAT
    AUTHORING      = ParamTypeEnum.STRING | ParamTypeEnum.PATH
    FUNCTION_ALL   = FLOAT | ParamTypeEnum.BOOLEAN | INTEGER | ParamTypeEnum.VOID_TYPE | ParamTypeEnum.STRING | ParamTypeEnum.PATH   # All functions types
    TEMPLATE_TYPE  = ParamTypeEnum.TEMPLATE1 | ParamTypeEnum.TEMPLATE2                                                               # Type templates (func. only)
    VALUE_TYPES    = NUMERIC | ParamTypeEnum.STRING
    OUTPUT_DEF     = ParamTypeEnum.ENTRY_VARIANT | VALUE_TYPES


@doc_source_code_enum
class AttributesEnum:
    """
    Enumeration of the different attributes available on a :class:`.SBSGraph` or a :class:`.SBSFunction`
    """
    Category     ,\
    Label        ,\
    Author       ,\
    AuthorURL    ,\
    Tags         ,\
    Description  ,\
    UserTags     ,\
    Icon         ,\
    HideInLibrary,\
    PhysicalSize ,\
    = range(10)


@doc_source_code_enum
class BitmapFormatEnum:
    """
    Enumeration of the supported bitmap format
    """
    RAW        ,\
    DDS        ,\
    DDSSTRIPPED,\
    BMP        ,\
    JPG        ,\
    TGA        ,\
    HDR        ,\
    PPM        ,\
    PFM        ,\
    = range(9)


@doc_source_code_enum
class InputEnum:
    """
    Enumeration of the input identifier available on the compositing node filters (:class:`.SBSCompFilter`)
    """
    BACKGROUND       ,\
    DESTINATION      ,\
    INPUT            ,\
    INPUT1           ,\
    INPUT2           ,\
    INPUT_GRADIENT   ,\
    INPUT_INTENSITY  ,\
    INPUT_NODE_OUTPUT,\
    INPUT_PATTERN    ,\
    MASK             ,\
    OPACITY          ,\
    SOURCE           ,\
    = range(12)


@doc_source_code_enum
class OutputEnum:
    """
    Enumeration of the output identifiers
    """
    OUTPUT ,\
    OUTPUT0,\
    OUTPUT1,\
    OUTPUT2,\
    OUTPUT3,\
    OUTPUTN,\
    = range(6)


@doc_source_code_enum
class FilterEnum:
    """
    Enumeration of the available compositing node filters (:class:`.SBSCompFilter`)
    """
    BITMAP               ,\
    BLEND                ,\
    BLUR                 ,\
    COMPINSTANCE         ,\
    CURVE                ,\
    DIRECTIONALMOTIONBLUR,\
    DIRECTIONALWARP      ,\
    DISTANCE             ,\
    DYNAMICGRADIENT      ,\
    EMBOSS               ,\
    FXMAPS               ,\
    GRADIENT             ,\
    GRAYSCALECONVERSION  ,\
    HSL                  ,\
    LEVELS               ,\
    NORMAL               ,\
    PIXEL_PROCESSOR      ,\
    SHARPEN              ,\
    SHUFFLE              ,\
    SVG                  ,\
    TEXT                 ,\
    TRANSFORMATION       ,\
    UNIFORM              ,\
    VALUE_PROCESSOR      ,\
    WARP                 , \
    PASSTHROUGH          ,\
    = range(26)


@doc_source_code_enum
class BaseParamEnum:
    """
    Enumeration of the parameters (:class:`.SBSParameter`) associated to a graph or node
    (:class:`.SBSGraph`), (:class:`.SBSCompFilter`) and FxMap node (:class:`.SBSParamsGraphNode`)
    """
    # Default parameters
    OUTPUT_FORMAT        , \
    OUTPUT_SIZE          , \
    PIXEL_SIZE           , \
    PIXEL_RATIO          , \
    QUALITY              , \
    RANDOM_SEED          , \
    TILING_MODE          , \
    ITERATION            , \
    = range(8)


@doc_source_code_enum
class CompNodeParamEnum:
    """
    Enumeration of the parameters (:class:`.SBSParameter`) associated to the compositing node filters
    (:class:`.SBSCompFilter`) and FxMap node (:class:`.SBSParamsGraphNode`)
    """
    # Default parameters
    OUTPUT_FORMAT        , \
    OUTPUT_SIZE          , \
    PIXEL_SIZE           , \
    PIXEL_RATIO          , \
    QUALITY              , \
    RANDOM_SEED          , \
    TILING_MODE          , \
    ITERATION            , \
 \
    ALPHA_BLENDING       , \
    BACKGROUND           , \
    BACKGROUND_VALUE     , \
    BLENDING_MODE        , \
    BLUR_ANGLE           , \
    BITMAP_RESOURCE_PATH , \
    BITMAP_RESIZE_METHOD , \
    CHANNEL_ALPHA        , \
    CHANNEL_BLUE         , \
    CHANNEL_GREEN        , \
    CHANNEL_RED          , \
    CHANNELS_WEIGHTS     , \
    CLAMP_IN_TERM        , \
    COLOR_MODE           , \
    COMBINE_DISTANCE     , \
    CROPPING_AREA        , \
    FILTERING            , \
    FLATTEN_ALPHA        , \
    GRADIENT_ADDRESSING  , \
    GRADIENT_ORIENTATION , \
    GRADIENT_POSITION    , \
    HIGHLIGHT_COLOR      , \
    HUE                  , \
    INTENSITY            , \
    NORMAL_FORMAT        , \
    LEVEL_IN_HIGH        , \
    LEVEL_IN_LOW         , \
    LEVEL_IN_MID         , \
    LEVEL_OUT_HIGH       , \
    LEVEL_OUT_LOW        , \
    LIGHT_ANGLE          , \
    LIGHTNESS            , \
    MATTE_COLOR          , \
    MAX_DISTANCE         , \
    MIPMAP_MODE          , \
    MIPMAP_LEVEL         , \
    OPACITY              , \
    OFFSET               , \
    OUTPUT_COLOR         , \
    PER_PIXEL            , \
    FUNCTION             , \
    RENDER_REGION        , \
    ROUGHNESS            , \
    SATURATION           , \
    SHADOW_COLOR         , \
    SVG_RESOURCE_PATH    , \
    TEXT                 , \
    TEXT_ALIGN           , \
    TEXT_FONT            , \
    TEXT_FONT_SIZE       , \
    TEXT_FONT_COLOR      , \
    TEXT_POSITION        , \
    TILING_REGION        , \
    TRANSFORM_MATRIX     , \
    WARP_ANGLE           , \
    NORMAL_ALPHA_CHANNEL , \
 \
    FX_BLENDING_MODE      , \
    FX_BRANCH_OFFSET      , \
    FX_COLOR_LUM          , \
    FX_IMAGE_ALPHA_PREMUL , \
    FX_IMAGE_FILTERING    , \
    FX_IMAGE_INDEX        , \
    FX_ITERATIONS         , \
    FX_PATTERN_OFFSET     , \
    FX_PATTERN_ROTATION   , \
    FX_PATTERN_SIZE       , \
    FX_PATTERN_TYPE       , \
    FX_PATTERN_VARIATION  , \
    FX_RANDOM_INHERITED   , \
    FX_RANDOM_SEED        , \
    FX_SELECTOR           ,\
    = range(79)


@doc_source_code_enum
class FunctionEnum:
    """
    Enumeration of the available function nodes (:class:`.SBSParamNode`)
    """
    SEQUENCE      ,\
    IF_ELSE       ,\
    SET           ,\
    GET_BOOL      ,\
    GET_INTEGER1  ,\
    GET_INTEGER2  ,\
    GET_INTEGER3  ,\
    GET_INTEGER4  ,\
    GET_FLOAT1    ,\
    GET_FLOAT2    ,\
    GET_FLOAT3    ,\
    GET_FLOAT4    ,\
    GET_STRING    ,\
    CONST_BOOL    ,\
    CONST_INT     ,\
    CONST_INT2    ,\
    CONST_INT3    ,\
    CONST_INT4    ,\
    CONST_FLOAT   ,\
    CONST_FLOAT2  ,\
    CONST_FLOAT3  ,\
    CONST_FLOAT4  ,\
    CONST_STRING  ,\
    INSTANCE      ,\
    VECTOR2       ,\
    VECTOR3       ,\
    VECTOR4       ,\
    SWIZZLE1      ,\
    SWIZZLE2      ,\
    SWIZZLE3      ,\
    SWIZZLE4      ,\
    VECTOR_INT2   ,\
    VECTOR_INT3   ,\
    VECTOR_INT4   ,\
    SWIZZLE_INT1  ,\
    SWIZZLE_INT2  ,\
    SWIZZLE_INT3  ,\
    SWIZZLE_INT4  ,\
    TO_INT        ,\
    TO_INT2       ,\
    TO_INT3       ,\
    TO_INT4       ,\
    TO_FLOAT      ,\
    TO_FLOAT2     ,\
    TO_FLOAT3     ,\
    TO_FLOAT4     ,\
    ADD           ,\
    SUB           ,\
    MUL           ,\
    MUL_SCALAR    ,\
    DIV           ,\
    NEG           ,\
    MOD           ,\
    DOT           ,\
    CROSS         ,\
    AND           ,\
    OR            ,\
    NOT           ,\
    EQ            ,\
    NOT_EQ        ,\
    GREATER       ,\
    GREATER_EQUAL ,\
    LOWER         ,\
    LOWER_EQUAL   ,\
    ABS           ,\
    FLOOR         ,\
    CEIL          ,\
    COS           ,\
    SIN           ,\
    SQRT          ,\
    LOG           ,\
    LOG2          ,\
    EXP           ,\
    POW2          ,\
    TAN           ,\
    ATAN2         ,\
    CARTESIAN     ,\
    LERP          ,\
    MIN           ,\
    MAX           ,\
    RAND          ,\
    SAMPLE_LUM    ,\
    SAMPLE_COL    ,\
    PASSTHROUGH   ,\
    = range(84)


@doc_source_code_enum
class FunctionInputEnum:
    """
    Enumeration of the input identifier of the function nodes (:class:`.SBSParamNode`)
    """
    A               ,\
    B               ,\
    COMPONENTS_IN   ,\
    COMPONENTS_LAST ,\
    CONDITION       ,\
    ELSE_PATH       ,\
    ENTRIES         ,\
    IF_PATH         ,\
    LOOP            ,\
    POS             ,\
    RHO             ,\
    SCALAR          ,\
    SEQUENCE_IN     ,\
    SEQUENCE_LAST   ,\
    THETA           ,\
    VALUE           ,\
    VECTOR          ,\
    X               ,\
    INPUT           ,\
    = range(19)


@doc_source_code_enum
class FxMapNodeEnum:
    """
    Enumeration of the available FxMap nodes (:class:`.ParamsGraphNode`)
    """
    ITERATE     ,\
    QUADRANT    ,\
    SWITCH      ,\
    PASSTHROUGH ,\
    = range(4)


@doc_source_code_enum
class TextureFormatEnum:
    """
    Enumeration of all the texture formats available in Substance Designer
    """
    DEFAULT_FORMAT ,\
    RGBA           ,\
    LUMINANCE      ,\
    RGBA16         ,\
    LUMINANCE16    ,\
    DXT1           ,\
    DXT2           ,\
    DXT3           ,\
    DXT4           ,\
    DXT5           ,\
    DXT1a          ,\
    ATI1           ,\
    ATI2           ,\
    RGB24          ,\
    RGBA16F        ,\
    LUMINANCE16F   ,\
    RGBA32F        ,\
    LUMINANCE32F   ,\
    = range(18)


@doc_source_code_enum
class MipmapEnum:
    """
    Enumeration of the mipmap format available on an Output node
    """
    FULL_PYRAMID ,\
    NO_MIPMAP    ,\
    LEVELS_2     ,\
    LEVELS_3     ,\
    LEVELS_4     ,\
    LEVELS_5     ,\
    LEVELS_6     ,\
    LEVELS_7     ,\
    LEVELS_8     ,\
    LEVELS_9     ,\
    LEVELS_10    ,\
    LEVELS_11    ,\
    LEVELS_12    ,\
    LEVELS_13    ,\
    LEVELS_14    ,\
    LEVELS_15    ,\
    = range(16)


@doc_source_code_enum
class UsageEnum:
    """
    Enumeration of the usages available on an Output node
    """
    DIFFUSE           ,\
    BASECOLOR         ,\
    OPACITY           ,\
    EMISSIVE          ,\
    AMBIENT           ,\
    AMBIENT_OCCLUSION ,\
    MASK              ,\
    NORMAL            ,\
    BUMP              ,\
    HEIGHT            ,\
    DISPLACEMENT      ,\
    SPECULAR          ,\
    SPECULAR_LEVEL    ,\
    SPECULAR_COLOR    ,\
    GLOSSINESS        ,\
    ROUGHNESS         ,\
    ANISOTROPY_LEVEL  ,\
    ANISOTROPY_ANGLE  ,\
    TRANSMISSIVE      ,\
    REFLECTION        ,\
    REFRACTION        ,\
    ENVIRONMENT       ,\
    IOR               ,\
    SCATTERING0       ,\
    SCATTERING1       ,\
    SCATTERING2       ,\
    SCATTERING3       ,\
    ANY               ,\
    METALLIC          ,\
    PANORAMA          ,\
    = range(30)


@doc_source_code_enum
class ComponentsEnum:
    """
    Enumeration of the components associated to a usage on an Output node
    """
    RGBA ,\
    RGB  ,\
    R    ,\
    G    ,\
    B    ,\
    A    ,\
    = range(6)

@doc_source_code_enum
class ColorSpacesEnum:
    """
    Enumeration of the color spaces associated to a usage on an Output node
    """
    SRGB             ,\
    LINEAR           ,\
    PASSTHRU         ,\
    SNORM            ,\
    NORMAL_XYZ_LEFT  ,\
    NORMAL_XYZ_RIGHT ,\
    = range(6)

@doc_source_code_enum
class UsageDataEnum:
    """
    Enumeration of the data contained in a usage
    """
    COMPONENTS , \
    COLOR_SPACE ,\
    = range(2)


@doc_source_code_enum
class ResourceTypeEnum:
    """
    Enumeration of the kind of resources handled by the application
    """
    NONE            ,\
    FONT            ,\
    SVG             ,\
    BITMAP          ,\
    M_BSDF          ,\
    LIGHT_PROFILE   ,\
    SCENE           ,\
    = range(7)
    OTHER = NONE

@doc_source_code_enum
class ParamInheritanceEnum:
    """
    Enumeration of the Inheritance parameter of filters
    """
    ABSOLUTE ,\
    PARENT   ,\
    INPUT    ,\
    = range(3)


@doc_source_code_enum
class TilingEnum:
    """
    Enumeration of the kind of tiling
    """
    NO_TILING      ,\
    H_TILING       ,\
    V_TILING       ,\
    H_AND_V_TILING ,\
    = range(4)


@doc_source_code_enum
class OutputFormatEnum:
    """
    Enumeration of the output format
    """
    FORMAT_8BITS        ,\
    FORMAT_16BITS       ,\
    FORMAT_16BITS_FLOAT ,\
    FORMAT_32BITS_FLOAT ,\
    = range(4)


@doc_source_code_enum
class OutputSizeEnum:
    """
    Enumeration of the Output size option
    """
    SIZE_1    ,\
    SIZE_2    ,\
    SIZE_4    ,\
    SIZE_8    ,\
    SIZE_16   ,\
    SIZE_32   ,\
    SIZE_64   ,\
    SIZE_128  ,\
    SIZE_256  ,\
    SIZE_512  ,\
    SIZE_1024 ,\
    SIZE_2048 ,\
    SIZE_4096 ,\
    SIZE_8192 ,\
    = range(14)

@doc_source_code_enum
class PixelRatioEnum:
    """
    Enumeration of the pixel ratio option
    """
    STRETCH,\
    SQUARE ,\
    = range(2)


@doc_source_code_enum
class QualityEnum:
    """
    Enumeration of the quality property
    """
    VERY_LOW  ,\
    LOW       ,\
    MEDIUM    ,\
    HIGH      ,\
    VERY_HIGH ,\
    = range(5)


@doc_source_code_enum
class ColorModeEnum:
    """
    Enumeration of the color switch values
    """
    GRAYSCALE ,\
    COLOR     ,\
    = range(2)


@doc_source_code_enum
class BlendBlendingModeEnum:
    """
    Enumeration of the blending mode for the Blend filter
    """
    COPY       ,\
    ADD        ,\
    SUBSTRACT  ,\
    MULTIPLY   ,\
    ADD_SUB    ,\
    MAX        ,\
    MIN        ,\
    SWITCH     ,\
    DIVIDE     ,\
    OVERLAY    ,\
    SCREEN     ,\
    SOFT_LIGHT ,\
    = range(12)


@doc_source_code_enum
class AlphaBlendingEnum:
    """
    Enumeration of the alpha blending mode for the Blend filter
    """
    USE_SOURCE_ALPHA ,\
    IGNORE_ALPHA     ,\
    STRAIGHT_ALPHA   ,\
    PREMULTIPLIED    ,\
    = range(4)


@doc_source_code_enum
class ChannelShuffleEnum:
    """
    Enumeration of the alpha blending mode for the Blend filter
    """
    INPUT1_RED   ,\
    INPUT1_GREEN ,\
    INPUT1_BLUE  ,\
    INPUT1_ALPHA ,\
    INPUT2_RED   ,\
    INPUT2_GREEN ,\
    INPUT2_BLUE  ,\
    INPUT2_ALPHA ,\
    = range(8)


@doc_source_code_enum
class CombineDistanceEnum:
    """
    Enumeration of the ways to combine source / distance in the Distance filter
    """
    ONLY_SOURCE ,\
    COMBINE     ,\
    = range(2)


@doc_source_code_enum
class CurveTypeEnum:
    """
    Enumeration of the kind of curve available in Substance Designer for the Curve filter
    """
    LUMINANCE ,\
    RED       ,\
    GREEN     ,\
    BLUE      ,\
    ALPHA     ,\
    = range(5)


@doc_source_code_enum
class GradientAddressingEnum:
    """
    Enumeration of the gradient addressing for the Dynamic Gradient and Gradient Map filters
    """
    CLAMP  ,\
    REPEAT ,\
    = range(2)


@doc_source_code_enum
class GradientOrientationEnum:
    """
    Enumeration of the gradient orientation for the Dynamic Gradient filter
    """
    HORIZONTAL ,\
    VERTICAL   ,\
    = range(2)


@doc_source_code_enum
class NormalFormatEnum:
    """
    Enumeration of the normal format for the Normal filter
    """
    DIRECTX ,\
    OPENGL  ,\
    = range(2)

@doc_source_code_enum
class NormalAlphaChannelContentEnum:
    """
    Enumeration of the alpha channel content for the Normal filter
    """
    FORCE_TO_ONE ,\
    INPUT_ALPHA  ,\
    = range(2)


@doc_source_code_enum
class MipMapModeEnum:
    """
    Enumeration of the mipmap mode for the Transformation 2D filter
    """
    AUTOMATIC ,\
    MANUAL    ,\
    = range(2)


@doc_source_code_enum
class FilteringEnum:
    """
    Enumeration of the filtering mode for the Transformation 2D filter
    """
    NEAREST   ,\
    BILINEAR  ,\
    = range(2)


@doc_source_code_enum
class TextAlignEnum:
    """
    Enumeration of the text alignment enumeration for the Text filter
    """
    LEFT    ,\
    CENTER  ,\
    RIGHT   ,\
    = range(3)


@doc_source_code_enum
class FX_PatternType:
    """
    Enumeration of the pattern available on the Quadrant node of an FxMap
    """
    NO_PATTERN            ,\
    INPUT_IMAGE           ,\
    SQUARE                ,\
    DISC                  ,\
    PARABOLOID            ,\
    BELL                  ,\
    GAUSSIAN              ,\
    THORN                 ,\
    PYRAMID               ,\
    BRICK                 ,\
    GRADATION             ,\
    WAVES                 ,\
    HALF_BELL             ,\
    RIDGED_BELL           ,\
    CRESCENT              ,\
    CAPSULE               ,\
    CONE                  ,\
    GRADATION_WITH_OFFSET ,\
    = range(18)


@doc_source_code_enum
class FX_BlendingModeEnum:
    """
    Enumeration of the blending mode available on the Quadrant node of an FxMap
    """
    ADD_SUB     ,\
    MAX         ,\
    ALPHA_BLEND ,\
    = range(3)


@doc_source_code_enum
class FX_InputImageAlphaEnum:
    """
    Enumeration of the alpha blending mode available on the Quadrant node of an FxMap
    """
    STRAIGHT      ,\
    PREMULTIPLIED ,\
    = range(2)


@doc_source_code_enum
class FX_InputImageFilteringEnum:
    """
    Enumeration of the filtering mode available on the Quadrant node of an FxMap
    """
    BILINEAR_MIPMAP ,\
    BILINEAR        ,\
    NEAREST         ,\
    = range(3)


@doc_source_code_enum
class FX_SelectorEnum:
    """
    Enumeration of the selector available on the Switch node of an FxMap
    """
    LEFT  ,\
    RIGHT ,\
    = range(2)

@doc_source_code_enum
class BitmapResizeMethodEnum:
    """
    Enumeration of the bitmap resize methods
    """
    SMOOTH_STRETCH  ,\
    NEAREST_STRETCH ,\
    = range(2)


@doc_source_code_enum
class WidgetTypeEnum:
    """
    Enumeration of the kind of widget available in Substance Designer for the parameter definition
    """
    BUTTON                ,\
    SLIDER                ,\
    DROP_DOWN_LIST        ,\
    SIZE_POW_2            ,\
    ANGLE                 ,\
    COLOR                 ,\
    TEXT                  ,\
    TRANSFORMATION_INVERSE,\
    TRANSFORMATION_FORWARD,\
    POSITION              ,\
    OFFSET                ,\
    = range(11)


@doc_source_code_enum
class WidgetOptionEnum:
    """
    enumeration of all the options available among the different kind of widget
    """
    BOOL_EDITOR_TYPE     ,\
    CLAMP                ,\
    DEFAULT              ,\
    LABEL0               ,\
    LABEL1               ,\
    LABEL2               ,\
    LABEL3               ,\
    MAX                  ,\
    MIN                  ,\
    PARAMETERS           ,\
    STEP                 ,\
    VALUE_INTERPRETATION ,\
    = range(12)


@doc_source_code_enum
class WidgetEnum:
    """
    Enumeration of the kind of widget available in Substance Designer for the parameter definition
    """
    BUTTON_BOOL            ,\
    SLIDER_INT1            ,\
    SLIDER_INT2            ,\
    SLIDER_INT3            ,\
    SLIDER_INT4            ,\
    SLIDER_FLOAT1          ,\
    SLIDER_FLOAT2          ,\
    SLIDER_FLOAT3          ,\
    SLIDER_FLOAT4          ,\
    DROPDOWN_INT1          ,\
    SIZE_POW2_INT2         ,\
    ANGLE_FLOAT1           ,\
    COLOR_FLOAT1           ,\
    COLOR_FLOAT3           ,\
    COLOR_FLOAT4           ,\
    MATRIX_INVERSE_FLOAT4  ,\
    MATRIX_FORWARD_FLOAT4  ,\
    TEXT_STRING            ,\
    POSITION_FLOAT2        ,\
    OFFSET_FLOAT2          ,\
    = range(20)


class GUIObjectTypeEnum:
    """
    Enumeration of the type of GUI Objects in a compositing graph or a function graph
    """
    COMMENT ,\
    PIN     ,\
    = range(2)


@doc_source_code_enum
class CompImplementationKindEnum:
    """
    Enumeration of the kind of comp implementation available for a :class:`.SBSCompImplementation`
    """
    FILTER        ,\
    INSTANCE      ,\
    INPUT         ,\
    OUTPUT        ,\
    = range(4)

@doc_source_code_enum
class BatchToolsEnum:
    """
    Enumeration of the different BatchTools
    """
    AXFTOOLS ,\
    BAKER    ,\
    COOKER   ,\
    MDLTOOLS ,\
    MUTATOR  ,\
    RENDER   ,\
    UPDATER  ,\
    = range(7)

@doc_source_code_enum
class GraphTemplateEnum:
    """
    Enumeration of the Substance Graph templates available in Substance Designer
    """
    EMPTY                               ,\
    PBR_METALLIC_ROUGHNESS              ,\
    PBR_SPECULAR_GLOSSINESS             ,\
    STANDARD                            ,\
    SCAN_PBR_METALLIC_ROUGHNESS         ,\
    SCAN_PBR_SPECULAR_GLOSSINESS        ,\
    AXF_2_PBR_METALLIC_ROUGHNESS        ,\
    AXF_2_PBR_SPECULAR_GLOSSINESS       ,\
    STUDIO_PANORAMA                     ,\
    PAINTER_FILTER_GENERIC              ,\
    PAINTER_FILTER_SPECIFIC             ,\
    PAINTER_FILTER_SPECIFIC_MORE_MAPS   ,\
    PAINTER_GENERATOR_MORE_MAPS         ,\
    = range(13)

@doc_source_code_enum
class BaseTypeEnum:
    """
    Enumeration of the base types used in :mod:`.autograph` module
    """
    FLOAT ,\
    INT   ,\
    BOOL  ,\
    = range(3)

@doc_source_code_enum
class UVTileFormat:
    """
    Enumeration of the different UV tiles format supported by the API
    """
    UDIM      = 0 # '1002'
    UxV       = 1 # '1x0'
    uU_vV     = 2 # 'u1_v0'
    UV_LIST   = 3 # [1,0]
    UV_TUPLE  = 4 # (1,0)
