# coding: utf-8
"""
Module **sbsbakersenum** provides all the enumeration used by the bakers in Substance Designer.
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_source_code_enum


@doc_source_code_enum
class BakerEnum:
    """
    Enumeration of the available bakers of a Scene resource in Substance Designer
    """
    AMBIENT_OCCLUSION             ,\
    AMBIENT_OCCLUSION_FROM_MESH   ,\
    BENT_NORMALS_FROM_MESH        ,\
    COLOR_MAP_FROM_MESH           ,\
    CONVERT_UV_TO_SVG             ,\
    CURVATURE                     ,\
    CURVATURE_MAP_FROM_MESH       ,\
    HEIGHT_MAP_FROM_MESH          ,\
    NORMAL_MAP_FROM_MESH          ,\
    OPACITY_MASK_FROM_MESH        ,\
    POSITION                      ,\
    POSITION_MAP_FROM_MESH        ,\
    THICKNESS_MAP_FROM_MESH       ,\
    TRANSFERRED_TEXTURE_FROM_MESH ,\
    WORLD_SPACE_DIRECTION         ,\
    WORLD_SPACE_NORMALS           ,\
    = range(16)

@doc_source_code_enum
class BakingStructureTagEnum:
    """
    Enumeration of the properties available on a Converter
    """
    BAKING                        ,\
    RESOURCE_MODEL                ,\
    RESOURCE_DEFAULT_VALUES_MODEL ,\
    RESOURCE_MESHES_MODEL         ,\
    RESOURCE_OUTPUT_MODEL         ,\
    CONVERTERS                    ,\
    FIRST                         ,\
    FORMAT                        ,\
    GUI_PROPERTIES                ,\
    IDENTIFIER                    ,\
    IS_OVERRIDEN                  ,\
    IS_SELECTED                   ,\
    MESH_CONVERTER_ID             ,\
    PROPERTIES                    ,\
    SCENE_SELECTION_MODE          ,\
    SECOND                        ,\
    SELECTIONS                    ,\
    SUBMESH_COLORS                ,\
    SUBMESH_COLOR                 ,\
    = range(19)


@doc_source_code_enum
class ConverterParamEnum:
    """
    Enumeration of the properties available on a Converter
    """
    ADDITIONAL__INVERT_GREEN                           , \
    ADDITIONAL__NORMAL_MAP                             , \
    ADDITIONAL__NORMAL_WORLD_SPACE                     , \
    COMMON__APPLY_DIFFUSION                            , \
    COMMON__DILATION_WIDTH                             , \
    COMMON__UV_TILE                                    , \
    COMMON__UVSET                                      , \
    CURVATURE__CURVATURE_MULTIPLIER                    , \
    CURVATURE__ENABLE_SEAMS                            , \
    CURVATURE__PER_VERTEX                              , \
    CURVATURE__SEAMS_POWER                             , \
    DEFAULT__APPLY_DIFFUSION                           , \
    DEFAULT__AVERAGE_NORMALS                           , \
    DEFAULT__DILATION_WIDTH                            , \
    DEFAULT__FORMAT                                    , \
    DEFAULT__OUTPUT_HEIGHT                             , \
    DEFAULT__OUTPUT_WIDTH                              , \
    DEFAULT__SUB_SAMPLING                              , \
    DEFAULT__UV_TILE                                   , \
    DEFAULT__UVSET                                     , \
    DETAIL__FILTER_METHOD                              , \
    DETAIL__IGNORE_BACKFACE                            , \
    DETAIL__INVERT_SKEW_CORRECTION                     , \
    DETAIL__LOW_AS_HIGH                                , \
    DETAIL__MAX_DEPTH                                  , \
    DETAIL__MAX_HEIGHT                                 , \
    DETAIL__RELATIVE_SCALE                             , \
    DETAIL__SKEW_CORRECTION                            , \
    DETAIL__SKEW_MAP                                   , \
    DETAIL__SMOOTH_NORMALS                             , \
    DETAIL__SUB_SAMPLING                               , \
    DETAIL__USE_CAGE                                   , \
    DETAIL_AO__ATTENUATION                             , \
    DETAIL_COLOR__COLOR_GENERATOR                      , \
    DETAIL_COLOR__COLOR_SOURCE                         , \
    DETAIL_CURVATURE__INTENSITY                        , \
    DETAIL_CURVATURE__MAXIMIZE_RANGE                   , \
    DETAIL_CURVATURE__SOFT_SATURATE                    , \
    DETAIL_DISTANCE__MAXIMIZE_RANGE                    , \
    DETAIL_NORMAL_COMMON__INVERT_GREEN                 , \
    DETAIL_NORMAL_COMMON__RESULT_TYPE                  , \
    DETAIL_SECONDARY_COMMON__DISTRIBUTION              , \
    DETAIL_SECONDARY_COMMON__FILTER_METHOD             , \
    DETAIL_SECONDARY_COMMON__IGNORE_BACKFACE_SECONDARY , \
    DETAIL_SECONDARY_COMMON__MAX_DISTANCE              , \
    DETAIL_SECONDARY_COMMON__MIN_DISTANCE              , \
    DETAIL_SECONDARY_COMMON__NB_SECONDARY              , \
    DETAIL_SECONDARY_COMMON__RELATIVE_SCALE            , \
    DETAIL_SECONDARY_COMMON__SPREAD                    , \
    DETAIL_TEXTURE__FILTERING_MODE                     , \
    DETAIL_TEXTURE__HIGH_POLY_UV_SET                   , \
    DETAIL_TEXTURE__IS_NORMAL_MAP                      , \
    DETAIL_TEXTURE__TEXTURE_FILE                       , \
    MESH__CAGE_PATH                                    , \
    MESH__DISTANCE_WITH                                , \
    MESH__HIGH_DEF_MESHES                              , \
    MESH__HIGH_DEF_MESHES_MESH                         , \
    MESH__IGNORE_BACKFACE                              , \
    MESH__INVERT_SKEW_CORRECTION                       , \
    MESH__MATCH_METHOD                                 , \
    MESH__MAX_FRONTAL_DISTANCE                         , \
    MESH__MAX_REAR_DISTANCE                            , \
    MESH__RELATIVE_TO_BB                               , \
    MESH__SKEW_PATH                                    , \
    MESH__USE_CAGE                                     , \
    MESH__USE_LOW_AS_HIGH_POLY                         , \
    MESH__USE_SKEW                                     , \
    NORMAL_WORLD_SPACE__BAKE_TYPE                      , \
    OUTPUT__FOLDER                                     , \
    OUTPUT__IN_SUBFOLDER                               , \
    OUTPUT__RESOURCE_METHOD                            , \
    OUTPUT__RESOURCE_NAME                              , \
    POSITION__AXIS                                     , \
    POSITION__MODE                                     , \
    POSITION__NORMALIZATION                            , \
    POSITION__NORMALIZATION_SCALE                      , \
    SEAO__DISTANCE_FADE                                , \
    SEAO__ERROR_BIAS                                   , \
    SEAO__INVERT_NORMALS                               , \
    SEAO__QUALITY                                      , \
    SEAO__USE_NEIGHBORS                                , \
    UV2SVG__COLOR_MODE                                 , \
    UV2SVG__PADDING                                    , \
    WORLD_DIRECTION__CONST_DIRECTION                   , \
    WORLD_DIRECTION__DIRECTION_MAP                     , \
    WORLD_DIRECTION__X                                 , \
    WORLD_DIRECTION__Y                                 , \
    WORLD_DIRECTION__Z                                 ,\
    = range(88)

@doc_source_code_enum
class SceneSelectionModeEnum:
    """
    Enumeration of the scene resource selection mode option
    """
    SUB_MESH ,\
    MATERIAL ,\
    = range(2)

@doc_source_code_enum
class BakerAOAttenuationEnum:
    """
    Enumeration of the Attenuation option in the Ambient Occlusion From Mesh Baker
    """
    NONE   ,\
    SMOOTH ,\
    LINEAR ,\
    = range(3)

@doc_source_code_enum
class BakerAOQualityEnum:
    """
    Enumeration of the Quality option in the Ambient Occlusion Baker
    """
    LOW      ,\
    MEDIUM   ,\
    HIGH     ,\
    VERYHIGH ,\
    = range(4)

@doc_source_code_enum
class BakerBakingTypeEnum:
    """
    Enumeration of the Baking Type option in the World Space Normals Baker
    """
    NORMAL   ,\
    TANGENT  ,\
    BINORMAL ,\
    = range(3)

@doc_source_code_enum
class BakerColorGeneratorEnum:
    """
    Enumeration of the Color Generator option in the Color Map Baker
    """
    RANDOM    ,\
    HUE_SHIFT ,\
    GREYSCALE ,\
    = range(3)

@doc_source_code_enum
class BakerColorModeEnum:
    """
    Enumeration of the Color Mode option in the Converter UV to SVG Baker
    """
    RANDOM      ,\
    HUE_SHIFT   ,\
    GREYSCALE   ,\
    UNIFORM     ,\
    MATERIAL_ID ,\
    = range(5)

@doc_source_code_enum
class BakerColorSourceEnum:
    """
    Enumeration of the Color Source option in the Color Map Baker
    """
    VERTEX_COLOR         ,\
    MATERIAL_COLOR       ,\
    MESH_ID              ,\
    POLYGROUP_SUBMESH_ID ,\
    = range(4)

@doc_source_code_enum
class BakerCurvatureAlgoEnum:
    """
    Enumeration of the Algorithm option in the Curvature Baker
    """
    PER_PIXEL  ,\
    PER_VERTEX ,\
    = range(2)

@doc_source_code_enum
class BakerDistributionEnum:
    """
    Enumeration of the Distribution option in the Bakers
    """
    UNIFORM  ,\
    COSINE   ,\
    = range(2)

@doc_source_code_enum
class BakerFilteringModeEnum:
    """
    Enumeration of the Filtering mode option in the Bakers
    """
    NEAREST  ,\
    BILINEAR ,\
    = range(2)

@doc_source_code_enum
class BakerFromMeshDistanceWithEnum:
    """
    Enumeration of the 'Set distance with' option in the Mesh options
    """
    VALUES    ,\
    CAGE      ,\
    = range(2)

@doc_source_code_enum
class BakerFromMeshMatchEnum:
    """
    Enumeration of the Match method option in the 'from mesh' Bakers (Used for Match and SelfOcclusion)
    """
    ALWAYS       ,\
    BY_MESH_NAME ,\
    = range(2)

@doc_source_code_enum
class BakerFromMeshSubSamplingEnum:
    """
    Enumeration of the Antialiasing option in the 'from mesh' Bakers
    """
    NONE            ,\
    SUBSAMPLING_2x2 ,\
    SUBSAMPLING_4x4 ,\
    SUBSAMPLING_8x8 ,\
    = range(4)

@doc_source_code_enum
class BakerInputDirectionEnum:
    """
    Enumeration of the Input Direction option in the World Space Direction Baker
    """
    FROM_TEXTURE        ,\
    FROM_UNIFORM_VECTOR ,\
    = range(2)

@doc_source_code_enum
class BakerMapTypeEnum:
    """
    Enumeration of the Map type option in the Bakers
    """
    WORLD_SPACE   ,\
    TANGENT_SPACE ,\
    = range(2)

@doc_source_code_enum
class BakerNormalOrientationEnum:
    """
    Enumeration of the normal format for the Bakers
    """
    OPENGL  ,\
    DIRECTX ,\
    = range(2)

@doc_source_code_enum
class BakerOutputFormatEnum:
    """
    Enumeration of the output Format option of the Bakers
    """
    PSD       ,\
    DDS       ,\
    WEBP      ,\
    HDR       ,\
    EXR       ,\
    JPEG      ,\
    JPEG_XR   ,\
    JPEG_2000 ,\
    PNG       ,\
    SVG       ,\
    TIF       ,\
    TGA       ,\
    ICO       ,\
    BMP       ,\
    WAP       ,\
    = range(15)

@doc_source_code_enum
class BakerPositionAxisEnum:
    """
    Enumeration of the Axis option in the Position Bakers
    """
    AXIS_X ,\
    AXIS_Y ,\
    AXIS_Z ,\
    = range(3)

@doc_source_code_enum
class BakerPositionModeEnum:
    """
    Enumeration of the Mode option in the Position Bakers
    """
    ALL_AXIS ,\
    ONE_AXIS ,\
    = range(2)

@doc_source_code_enum
class BakerPositionNormalizationEnum:
    """
    Enumeration of the Normalization option in the Position Bakers
    """
    BBOX    ,\
    BSPHERE ,\
    = range(2)

@doc_source_code_enum
class BakerResourceMethodEnum:
    """
    Enumeration of the Resource method option in the Bakers
    """
    EMBEDDED ,\
    LINKED   ,\
    = range(2)

@doc_source_code_enum
class BakerUVSetEnum:
    """
    Enumeration of the UV set option in the Bakers
    """
    UV_0 ,\
    UV_1 ,\
    UV_2 ,\
    UV_3 ,\
    UV_4 ,\
    UV_5 ,\
    UV_6 ,\
    UV_7 ,\
    = range(8)
