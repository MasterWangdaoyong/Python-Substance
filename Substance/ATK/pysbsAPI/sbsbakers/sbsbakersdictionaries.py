# coding: utf-8
"""
Module **sbsbakersdictionaries** provides the dictionaries to have the mapping between the enumerations in
:mod:`.sbsbakersenum` and the corresponding string identifiers used by Substance Designer.

    * **Dictionaries:**
        * __dict_BakingStructureTags: dictionary relative to :class:`.BakingStructureTagEnum`
        * __dict_BakerOutputFormats: dictionary relative to :class:`.BakerOutputFormatEnum`
        * __dict_ConverterParameters: dictionary relative to :class:`.ConverterParamEnum`
        * __dict_CommonToDefault: dictionary that relates specific baker options to global options relative to :class:`.ConverterParamEnum`
"""

from __future__ import unicode_literals
import sys

from pysbs.api_decorators import doc_module_attributes,handle_exceptions,checkFirstParamIsAString
from . import sbsbakersenum


# Dictionary of baker attributes
__dict_BakingStructureTags = {
    sbsbakersenum.BakingStructureTagEnum.BAKING                         : 'baking',
    sbsbakersenum.BakingStructureTagEnum.RESOURCE_MODEL                 : 'bakingresourcemodel',
    sbsbakersenum.BakingStructureTagEnum.RESOURCE_DEFAULT_VALUES_MODEL  : 'bakingresourcedefaultvaluesmodel',
    sbsbakersenum.BakingStructureTagEnum.RESOURCE_MESHES_MODEL          : 'bakingresourcemeshesmodel',
    sbsbakersenum.BakingStructureTagEnum.RESOURCE_OUTPUT_MODEL          : 'bakingresourceoutputmodel',
    sbsbakersenum.BakingStructureTagEnum.CONVERTERS                     : 'converters',
    sbsbakersenum.BakingStructureTagEnum.FIRST                          : 'first',
    sbsbakersenum.BakingStructureTagEnum.FORMAT                         : 'format',
    sbsbakersenum.BakingStructureTagEnum.GUI_PROPERTIES                 : 'guiProperties',
    sbsbakersenum.BakingStructureTagEnum.IDENTIFIER                     : 'identifier',
    sbsbakersenum.BakingStructureTagEnum.IS_SELECTED                    : 'isselected',
    sbsbakersenum.BakingStructureTagEnum.IS_OVERRIDEN                   : 'isOverriden',
    sbsbakersenum.BakingStructureTagEnum.MESH_CONVERTER_ID              : 'converterid',
    sbsbakersenum.BakingStructureTagEnum.PROPERTIES                     : 'properties',
    sbsbakersenum.BakingStructureTagEnum.SCENE_SELECTION_MODE           : 'objectSelectionMode',    #To be confirmed
    sbsbakersenum.BakingStructureTagEnum.SECOND                         : 'second',
    sbsbakersenum.BakingStructureTagEnum.SELECTIONS                     : 'selections',
    sbsbakersenum.BakingStructureTagEnum.SUBMESH_COLORS                 : 'colors',
    sbsbakersenum.BakingStructureTagEnum.SUBMESH_COLOR                  : 'color',
}


# Dictionary of baker output format
__dict_BakerOutputFormats = {
    sbsbakersenum.BakerOutputFormatEnum.PSD       : 'Adobe Photoshop (*.psd)',
    sbsbakersenum.BakerOutputFormatEnum.DDS       : 'DirectDraw Surface (*.dds)',
    sbsbakersenum.BakerOutputFormatEnum.WEBP      : 'Google WebP image format (*.webp)',
    sbsbakersenum.BakerOutputFormatEnum.HDR       : 'High Dynamic Range Image (*.hdr)',
    sbsbakersenum.BakerOutputFormatEnum.EXR       : 'ILM OpenEXR (*.exr)',
    sbsbakersenum.BakerOutputFormatEnum.JPEG      : 'JPEG - JFIF Compliant (*.jpg *.jif *.jpeg *.jpe)',
    sbsbakersenum.BakerOutputFormatEnum.JPEG_XR   : 'JPEG XR image format (*.jxr *.wdp *.hdp)',
    sbsbakersenum.BakerOutputFormatEnum.JPEG_2000 : 'JPEG-2000 File format (*.jp2)',
    sbsbakersenum.BakerOutputFormatEnum.PNG       : 'Portable Network Graphics (*.png)',
    sbsbakersenum.BakerOutputFormatEnum.SVG       : 'SVG (*.svg)',
    sbsbakersenum.BakerOutputFormatEnum.TIF       : 'Tagged Image File Format (*.tif *.tiff)',
    sbsbakersenum.BakerOutputFormatEnum.TGA       : 'Truevision Targa (*.tga *.targa)',
    sbsbakersenum.BakerOutputFormatEnum.ICO       : 'Windows Icon (*.ico)',
    sbsbakersenum.BakerOutputFormatEnum.BMP       : 'Windows or OS/2 Bitmap (*.bmp)',
    sbsbakersenum.BakerOutputFormatEnum.WAP       : 'Wireless Bitmap (*.wap *.wbmp *.wbm)'
}

# Dictionary of converter properties
__dict_ConverterParameters = {
    sbsbakersenum.ConverterParamEnum.ADDITIONAL__INVERT_GREEN                           : 'Additional.InvertGreen',
    sbsbakersenum.ConverterParamEnum.ADDITIONAL__NORMAL_MAP                             : 'Additional.NormalMap',
    sbsbakersenum.ConverterParamEnum.ADDITIONAL__NORMAL_WORLD_SPACE                     : 'Additional.NormalWorldSpace',
    sbsbakersenum.ConverterParamEnum.COMMON__APPLY_DIFFUSION                            : 'Common.ApplyDiffusion',
    sbsbakersenum.ConverterParamEnum.COMMON__DILATION_WIDTH                             : 'Common.DilationWidth',
    sbsbakersenum.ConverterParamEnum.COMMON__UV_TILE                                    : 'Common.UVTile',
    sbsbakersenum.ConverterParamEnum.COMMON__UVSET                                      : 'Common.UVSet',
    sbsbakersenum.ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER                    : 'Curvature.CurvMult',
    sbsbakersenum.ConverterParamEnum.CURVATURE__ENABLE_SEAMS                            : 'Curvature.EnableSeams',
    sbsbakersenum.ConverterParamEnum.CURVATURE__PER_VERTEX                              : 'Curvature.PerVertex',
    sbsbakersenum.ConverterParamEnum.CURVATURE__SEAMS_POWER                             : 'Curvature.SeamsPower',
    sbsbakersenum.ConverterParamEnum.DETAIL__FILTER_METHOD                              : 'Detail.FilterMethod',
    sbsbakersenum.ConverterParamEnum.DETAIL__IGNORE_BACKFACE                            : 'Detail.IgnoreBackface',
    sbsbakersenum.ConverterParamEnum.DETAIL__INVERT_SKEW_CORRECTION                     : 'Detail.InvertSkewCorrection',
    sbsbakersenum.ConverterParamEnum.DETAIL__LOW_AS_HIGH                                : 'Detail.LowAsHigh',
    sbsbakersenum.ConverterParamEnum.DETAIL__MAX_DEPTH                                  : 'Detail.MaxDepth',
    sbsbakersenum.ConverterParamEnum.DETAIL__MAX_HEIGHT                                 : 'Detail.MaxHeight',
    sbsbakersenum.ConverterParamEnum.DETAIL__RELATIVE_SCALE                             : 'Detail.RelativeScale',
    sbsbakersenum.ConverterParamEnum.DETAIL__SKEW_CORRECTION                            : 'Detail.SkewCorrection',
    sbsbakersenum.ConverterParamEnum.DETAIL__SKEW_MAP                                   : 'Detail.SkewMap',
    sbsbakersenum.ConverterParamEnum.DETAIL__SMOOTH_NORMALS                             : 'Detail.SmoothNormals',
    sbsbakersenum.ConverterParamEnum.DETAIL__SUB_SAMPLING                               : 'Detail.SubSampling',
    sbsbakersenum.ConverterParamEnum.DETAIL__USE_CAGE                                   : 'Detail.UseCage',
    sbsbakersenum.ConverterParamEnum.DETAIL_AO__ATTENUATION                             : 'Detail.AO.Attenuation',
    sbsbakersenum.ConverterParamEnum.DETAIL_COLOR__COLOR_GENERATOR                      : 'Detail.Color.ColorGenerator',
    sbsbakersenum.ConverterParamEnum.DETAIL_COLOR__COLOR_SOURCE                         : 'Detail.Color.ColorSource',
    sbsbakersenum.ConverterParamEnum.DETAIL_CURVATURE__INTENSITY                        : 'Detail.Curvature.Intensity',
    sbsbakersenum.ConverterParamEnum.DETAIL_CURVATURE__MAXIMIZE_RANGE                   : 'Detail.Curvature.MaximizeRange',
    sbsbakersenum.ConverterParamEnum.DETAIL_CURVATURE__SOFT_SATURATE                    : 'Detail.Curvature.SoftSaturate',
    sbsbakersenum.ConverterParamEnum.DETAIL_DISTANCE__MAXIMIZE_RANGE                    : 'Detail.Distance.MaximizeRange',
    sbsbakersenum.ConverterParamEnum.DETAIL_NORMAL_COMMON__INVERT_GREEN                 : 'Detail.NormalCommon.InvertGreen',
    sbsbakersenum.ConverterParamEnum.DETAIL_NORMAL_COMMON__RESULT_TYPE                  : 'Detail.NormalCommon.ResultType',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__DISTRIBUTION              : 'Detail.SecondaryCommon.Distribution',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__FILTER_METHOD             : 'Detail.SecondaryCommon.FilterMethodSecondary',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__IGNORE_BACKFACE_SECONDARY : 'Detail.SecondaryCommon.IgnoreBackfaceSecondary',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__MAX_DISTANCE              : 'Detail.SecondaryCommon.MaxDistance',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__MIN_DISTANCE              : 'Detail.SecondaryCommon.MinDistance',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__NB_SECONDARY              : 'Detail.SecondaryCommon.NbSecondary',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__RELATIVE_SCALE            : 'Detail.SecondaryCommon.MaxDistanceRelativeScale',
    sbsbakersenum.ConverterParamEnum.DETAIL_SECONDARY_COMMON__SPREAD                    : 'Detail.SecondaryCommon.Spread',
    sbsbakersenum.ConverterParamEnum.DETAIL_TEXTURE__FILTERING_MODE                     : 'Detail.Texture.FilteringMode',
    sbsbakersenum.ConverterParamEnum.DETAIL_TEXTURE__HIGH_POLY_UV_SET                   : 'Detail.Texture.HighPolyUVSet',
    sbsbakersenum.ConverterParamEnum.DETAIL_TEXTURE__IS_NORMAL_MAP                      : 'Detail.Texture.IsNormalMap',
    sbsbakersenum.ConverterParamEnum.DETAIL_TEXTURE__TEXTURE_FILE                       : 'Detail.Texture.TextureFileName',
    sbsbakersenum.ConverterParamEnum.NORMAL_WORLD_SPACE__BAKE_TYPE                      : 'NWS.BakeType',
    sbsbakersenum.ConverterParamEnum.POSITION__AXIS                                     : 'Position.Axis',
    sbsbakersenum.ConverterParamEnum.POSITION__MODE                                     : 'Position.Mode',
    sbsbakersenum.ConverterParamEnum.POSITION__NORMALIZATION                            : 'Position.Normalization',
    sbsbakersenum.ConverterParamEnum.POSITION__NORMALIZATION_SCALE                      : 'Position.NormalizationScale',
    sbsbakersenum.ConverterParamEnum.SEAO__DISTANCE_FADE                                : 'SeAO.DistanceFade',
    sbsbakersenum.ConverterParamEnum.SEAO__ERROR_BIAS                                   : 'SeAO.ErrorBias',
    sbsbakersenum.ConverterParamEnum.SEAO__INVERT_NORMALS                               : 'SeAO.InvertNormals',
    sbsbakersenum.ConverterParamEnum.SEAO__QUALITY                                      : 'SeAO.Quality',
    sbsbakersenum.ConverterParamEnum.SEAO__USE_NEIGHBORS                                : 'SeAO.UseNeighbors',
    sbsbakersenum.ConverterParamEnum.UV2SVG__COLOR_MODE                                 : 'UV2Svg.ColorMode',
    sbsbakersenum.ConverterParamEnum.UV2SVG__PADDING                                    : 'UV2Svg.Padding',
    sbsbakersenum.ConverterParamEnum.WORLD_DIRECTION__CONST_DIRECTION                   : 'WorldDirection.ConstDirection',
    sbsbakersenum.ConverterParamEnum.WORLD_DIRECTION__DIRECTION_MAP                     : 'WorldDirection.DirectionMap',
    sbsbakersenum.ConverterParamEnum.WORLD_DIRECTION__X                                 : 'WorldDirection.X',
    sbsbakersenum.ConverterParamEnum.WORLD_DIRECTION__Y                                 : 'WorldDirection.Y',
    sbsbakersenum.ConverterParamEnum.WORLD_DIRECTION__Z                                 : 'WorldDirection.Z',
    sbsbakersenum.ConverterParamEnum.DEFAULT__APPLY_DIFFUSION                           : 'applyDiffusion',
    sbsbakersenum.ConverterParamEnum.DEFAULT__AVERAGE_NORMALS                           : 'averageNormals',
    sbsbakersenum.ConverterParamEnum.DEFAULT__DILATION_WIDTH                            : 'dilationWidth',
    sbsbakersenum.ConverterParamEnum.DEFAULT__FORMAT                                    : 'format',
    sbsbakersenum.ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT                             : 'outputSize/width',
    sbsbakersenum.ConverterParamEnum.DEFAULT__OUTPUT_WIDTH                              : 'outputSize/height',
    sbsbakersenum.ConverterParamEnum.DEFAULT__SUB_SAMPLING                              : 'subsampling',
    sbsbakersenum.ConverterParamEnum.DEFAULT__UV_TILE                                   : 'uvTiles',
    sbsbakersenum.ConverterParamEnum.DEFAULT__UVSET                                     : 'uvSet',
    sbsbakersenum.ConverterParamEnum.MESH__CAGE_PATH                                    : 'cagepath',
    sbsbakersenum.ConverterParamEnum.MESH__DISTANCE_WITH                                : 'distanceWith',
    sbsbakersenum.ConverterParamEnum.MESH__HIGH_DEF_MESHES                              : 'meshes',
    sbsbakersenum.ConverterParamEnum.MESH__HIGH_DEF_MESHES_MESH                         : 'mesh',
    sbsbakersenum.ConverterParamEnum.MESH__IGNORE_BACKFACE                              : 'ignoreBackface',
    sbsbakersenum.ConverterParamEnum.MESH__INVERT_SKEW_CORRECTION                       : 'invertSkew',
    sbsbakersenum.ConverterParamEnum.MESH__MATCH_METHOD                                 : 'matchBy',
    sbsbakersenum.ConverterParamEnum.MESH__MAX_FRONTAL_DISTANCE                         : 'frontal',
    sbsbakersenum.ConverterParamEnum.MESH__MAX_REAR_DISTANCE                            : 'rear',
    sbsbakersenum.ConverterParamEnum.MESH__RELATIVE_TO_BB                               : 'relativeToBb',
    sbsbakersenum.ConverterParamEnum.MESH__SKEW_PATH                                    : 'skewpath',
    sbsbakersenum.ConverterParamEnum.MESH__USE_CAGE                                     : 'useCage',
    sbsbakersenum.ConverterParamEnum.MESH__USE_LOW_AS_HIGH_POLY                         : 'useLowAsHighPoly',
    sbsbakersenum.ConverterParamEnum.MESH__USE_SKEW                                     : 'useSkew',
    sbsbakersenum.ConverterParamEnum.OUTPUT__FOLDER                                     : 'folder',
    sbsbakersenum.ConverterParamEnum.OUTPUT__IN_SUBFOLDER                               : 'placeIntoSpecificFolder',
    sbsbakersenum.ConverterParamEnum.OUTPUT__RESOURCE_METHOD                            : 'resourceMethod',
    sbsbakersenum.ConverterParamEnum.OUTPUT__RESOURCE_NAME                              : 'nameScheme'
}


__dict_CommonToDefault = {
    sbsbakersenum.ConverterParamEnum.DEFAULT__FORMAT         : sbsbakersenum.ConverterParamEnum.DEFAULT__FORMAT,
    sbsbakersenum.ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT  : sbsbakersenum.ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT,
    sbsbakersenum.ConverterParamEnum.DEFAULT__OUTPUT_WIDTH   : sbsbakersenum.ConverterParamEnum.DEFAULT__OUTPUT_WIDTH,
    sbsbakersenum.ConverterParamEnum.COMMON__UV_TILE         : sbsbakersenum.ConverterParamEnum.DEFAULT__UV_TILE,
    sbsbakersenum.ConverterParamEnum.COMMON__UVSET           : sbsbakersenum.ConverterParamEnum.DEFAULT__UVSET,
    sbsbakersenum.ConverterParamEnum.COMMON__APPLY_DIFFUSION : sbsbakersenum.ConverterParamEnum.DEFAULT__APPLY_DIFFUSION,
    sbsbakersenum.ConverterParamEnum.COMMON__DILATION_WIDTH  : sbsbakersenum.ConverterParamEnum.DEFAULT__DILATION_WIDTH,
    sbsbakersenum.ConverterParamEnum.DETAIL__SMOOTH_NORMALS  : sbsbakersenum.ConverterParamEnum.DEFAULT__AVERAGE_NORMALS,
    sbsbakersenum.ConverterParamEnum.DETAIL__SUB_SAMPLING    : sbsbakersenum.ConverterParamEnum.DEFAULT__SUB_SAMPLING,
}

@handle_exceptions()
def getBakingStructureTagName(aBakingStructureTag):
    """
    getBakingStructureTagName(aBakingStructureTag)
    Get the name of the given baking structure tag

    :param aBakingStructureTag: baking structure tag
    :type aBakingStructureTag: :class:`.BakingStructureTagEnum`
    :return: the baker attribute as a string
    """
    return __dict_BakingStructureTags[aBakingStructureTag]


@handle_exceptions()
def getBakerOutputFormatName(aBakerOutputFormat):
    """
    getBakerOutputFormatName(aBakerOutputFormat)
    Get the given baker output format name

    :param aBakerOutputFormat: baker output format identifier
    :type aBakerOutputFormat: :class:`.BakerOutputFormatEnum`
    :return: the baker output format as a string
    """
    return __dict_BakerOutputFormats[aBakerOutputFormat]

@handle_exceptions()
def getConverterParamName(aConverterParam):
    """
    getConverterParamName(aConverterParam)
    Get the given baker property name

    :param aConverterParam: converter property identifier
    :type aConverterParam: :class:`.ConverterParamEnum`
    :return: the converter parameter as a string
    """
    return __dict_ConverterParameters[aConverterParam]

@handle_exceptions()
@checkFirstParamIsAString
def getBakingStructureTagEnum(aBakingStructureTagName):
    """
    getBakingStructureTagEnum(aBakingStructureTagName)
    Get the enum value of the given baker attribute

    :param aBakingStructureTagName: Name of the baking structure tag to find
    :type aBakingStructureTagName: str
    :return: the baking structure tag as a :class:`.BakingStructureTagEnum`
    """
    return next((key for key, value in __dict_BakingStructureTags.items() if value == aBakingStructureTagName), None)


@handle_exceptions()
@checkFirstParamIsAString
def getConverterParamEnum(aConverterParamName):
    """
    getConverterParamEnum(aConverterParamName)
    Get the enum value of the given converter property

    :param aConverterParamName: Converter property name
    :type aConverterParamName: str
    :return: the converter parameter as a :class:`.ConverterParamEnum`
    """
    return next((key for key, value in __dict_ConverterParameters.items() if value == aConverterParamName), None)


@handle_exceptions()
@checkFirstParamIsAString
def getBakerOutputFormatEnum(aBakerOutputFormatName):
    """
    getBakerOutputFormatEnum(aBakerOutputFormatName)
    Get the enum value of the given baker output property

    :param aBakerOutputFormatName: Output property name
    :type aBakerOutputFormatName: str
    :return: the converter parameter as a :class:`.ConverterParamEnum`
    """
    return next((key for key, value in __dict_BakerOutputFormats.items() if value == aBakerOutputFormatName), None)


@handle_exceptions()
def getDefaultFromCommon(aCommonProperty):
    """
    getDefaultFromCommon(aCommonProperty)
    Get the corresponding default property from a common property

    :param aCommonProperty: The common property
    :type: :class:`.ConverterParamEnum`
    :return: :class:`.ConverterParamEnum` the corresponding default property
    """
    return __dict_CommonToDefault[aCommonProperty]


doc_module_attributes(sys.modules[__name__])
