# coding: utf-8
"""
Module **sbsbakersdefaultprops** provides the definition of all the common properties of bakers, with their default values.

* sGlobalOutputProperties: Global output properties
* sGlobalBakersDefaultProperties: Global mesh properties
* sGlobalMeshesProperties: Global default properties
* sOverridableProperties: Properties overridable at the level of each baker
* sAllBakersOutputProperties: Output properties registered on all bakers (Size and Format)
* sAllBakersCommonProperties: Properties registered on all bakers
* sDetailBakerCommonProperties: Properties registered on all 'from mesh' bakers
* sDistanceCommonProperties: Properties available for all bakers with distance settings
* sNormalBakersCommonProperties: Properties available for all bakers with normal settings
* sPositionBakersCommonProperties: Properties available for all bakers with position settings
* sSecondaryRayCommonProperties: Properties available for all bakers with secondary ray settings
"""

from __future__ import unicode_literals
import sys

from pysbs.api_decorators import doc_module_attributes
from pysbs.qtclasses import QtVariantTypeEnum, QtVariant
from pysbs.sbsenum import OutputSizeEnum

from .sbsbakingconverterparam import BakingGlobalParam, BakingConverterParam
from .sbsbakersenum import *
from . import sbsbakersdictionaries as bakersdict

# Global output properties
sGlobalOutputProperties = [
    BakingGlobalParam(ConverterParamEnum.OUTPUT__FOLDER,          QtVariant(QtVariantTypeEnum.URL,    ''     )),
    BakingGlobalParam(ConverterParamEnum.OUTPUT__RESOURCE_NAME,   QtVariant(QtVariantTypeEnum.STRING, '$(mesh)_$(bakername)')),
    BakingGlobalParam(ConverterParamEnum.OUTPUT__IN_SUBFOLDER,    QtVariant(QtVariantTypeEnum.BOOL,   False      )),
    BakingGlobalParam(ConverterParamEnum.OUTPUT__RESOURCE_METHOD, QtVariant(QtVariantTypeEnum.INT,    BakerResourceMethodEnum.LINKED))
]

# Global default properties
sGlobalBakersDefaultProperties = [
    BakingGlobalParam(ConverterParamEnum.DEFAULT__APPLY_DIFFUSION, QtVariant(QtVariantTypeEnum.BOOL,   True )),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__AVERAGE_NORMALS, QtVariant(QtVariantTypeEnum.BOOL,   True  )),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__DILATION_WIDTH,  QtVariant(QtVariantTypeEnum.INT,    4     )),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__FORMAT,          QtVariant(QtVariantTypeEnum.STRING, bakersdict.getBakerOutputFormatName(BakerOutputFormatEnum.PNG))),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH,    QtVariant(QtVariantTypeEnum.INT,    OutputSizeEnum.SIZE_2048)),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT,   QtVariant(QtVariantTypeEnum.INT,    OutputSizeEnum.SIZE_2048)),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__SUB_SAMPLING,    QtVariant(QtVariantTypeEnum.INT,    BakerFromMeshSubSamplingEnum.NONE )),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__UVSET,           QtVariant(QtVariantTypeEnum.INT,    BakerUVSetEnum.UV_0))
]

# Global mesh properties
sGlobalMeshesProperties = [
    BakingGlobalParam(ConverterParamEnum.MESH__CAGE_PATH,                 QtVariant(QtVariantTypeEnum.STRING,      ''    )),
    BakingGlobalParam(ConverterParamEnum.MESH__DISTANCE_WITH,             QtVariant(QtVariantTypeEnum.INT,         BakerFromMeshDistanceWithEnum.VALUES )),
    BakingGlobalParam(ConverterParamEnum.MESH__MAX_FRONTAL_DISTANCE,      QtVariant(QtVariantTypeEnum.DOUBLE,      0.01  )),
    BakingGlobalParam(ConverterParamEnum.MESH__IGNORE_BACKFACE,           QtVariant(QtVariantTypeEnum.BOOL,        True  )),
    BakingGlobalParam(ConverterParamEnum.MESH__INVERT_SKEW_CORRECTION,    QtVariant(QtVariantTypeEnum.BOOL,        False )),
    BakingGlobalParam(ConverterParamEnum.MESH__MATCH_METHOD,              QtVariant(QtVariantTypeEnum.INT,         BakerFromMeshMatchEnum.ALWAYS )),
    BakingGlobalParam(ConverterParamEnum.MESH__HIGH_DEF_MESHES,           QtVariant(QtVariantTypeEnum.STRING_LIST, []    )),
    BakingGlobalParam(ConverterParamEnum.MESH__MAX_REAR_DISTANCE,         QtVariant(QtVariantTypeEnum.DOUBLE,      0.01  )),
    BakingGlobalParam(ConverterParamEnum.MESH__RELATIVE_TO_BB,            QtVariant(QtVariantTypeEnum.BOOL,        True  )),
    BakingGlobalParam(ConverterParamEnum.MESH__USE_SKEW,                  QtVariant(QtVariantTypeEnum.STRING,      ''    )),
    BakingGlobalParam(ConverterParamEnum.MESH__USE_LOW_AS_HIGH_POLY, QtVariant(QtVariantTypeEnum.BOOL,        False )),
    BakingGlobalParam(ConverterParamEnum.MESH__SKEW_PATH, QtVariant(QtVariantTypeEnum.STRING, '')),
]


# Properties overridable at the level of each baker
sOverridableProperties = [
    ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT,
    ConverterParamEnum.DEFAULT__OUTPUT_WIDTH,
    ConverterParamEnum.DETAIL__SUB_SAMPLING,
    ConverterParamEnum.DETAIL__SMOOTH_NORMALS,
    ConverterParamEnum.COMMON__UVSET,
    ConverterParamEnum.DEFAULT__FORMAT,
]

# Output properties registered on all bakers
sAllBakersOutputProperties = [
    BakingGlobalParam(ConverterParamEnum.DEFAULT__FORMAT,        QtVariant(QtVariantTypeEnum.STRING, bakersdict.getBakerOutputFormatName(BakerOutputFormatEnum.PNG))),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__OUTPUT_WIDTH,  QtVariant(QtVariantTypeEnum.INT,    OutputSizeEnum.SIZE_2048)),
    BakingGlobalParam(ConverterParamEnum.DEFAULT__OUTPUT_HEIGHT, QtVariant(QtVariantTypeEnum.INT, OutputSizeEnum.SIZE_2048)),
]

# Properties registered on all bakers
sAllBakersCommonProperties = [
    BakingConverterParam(ConverterParamEnum.COMMON__UV_TILE, QtVariant(QtVariantTypeEnum.STRING, ''    )),
    BakingConverterParam(ConverterParamEnum.COMMON__UVSET,      QtVariant(QtVariantTypeEnum.INT,    BakerUVSetEnum.UV_0))
]

# Properties registered on all 'from mesh' bakers
sDetailBakerCommonProperties = [
    BakingConverterParam(ConverterParamEnum.DETAIL__SMOOTH_NORMALS,      QtVariant(QtVariantTypeEnum.BOOL,   False )),
    BakingConverterParam(ConverterParamEnum.DETAIL__SUB_SAMPLING,        QtVariant(QtVariantTypeEnum.INT,    BakerFromMeshSubSamplingEnum.NONE ))
]

# Properties available for all bakers with distance settings
sDistanceCommonProperties = [
    BakingConverterParam(ConverterParamEnum.DETAIL_DISTANCE__MAXIMIZE_RANGE,     QtVariant(QtVariantTypeEnum.BOOL, True))
]

# Properties available for all bakers with normal settings
sNormalBakersCommonProperties = [
    BakingConverterParam(ConverterParamEnum.DETAIL_NORMAL_COMMON__RESULT_TYPE,  QtVariant(QtVariantTypeEnum.INT, BakerMapTypeEnum.TANGENT_SPACE)),
    BakingConverterParam(ConverterParamEnum.DETAIL_NORMAL_COMMON__INVERT_GREEN, QtVariant(QtVariantTypeEnum.INT, BakerNormalOrientationEnum.DIRECTX))
]

# Properties available for all bakers with position settings
sPositionBakersCommonProperties = [
    BakingConverterParam(ConverterParamEnum.POSITION__AXIS,           QtVariant(QtVariantTypeEnum.INT, BakerPositionAxisEnum.AXIS_X)),
    BakingConverterParam(ConverterParamEnum.POSITION__MODE,           QtVariant(QtVariantTypeEnum.INT, BakerPositionModeEnum.ALL_AXIS)),
    BakingConverterParam(ConverterParamEnum.POSITION__NORMALIZATION,  QtVariant(QtVariantTypeEnum.INT, BakerPositionNormalizationEnum.BSPHERE))
    # TODO: Normalization scale
]

# Properties available for all bakers with secondary ray settings
sSecondaryRayCommonProperties = [
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__DISTRIBUTION,              QtVariant(QtVariantTypeEnum.INT,    BakerDistributionEnum.COSINE)),
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__IGNORE_BACKFACE_SECONDARY, QtVariant(QtVariantTypeEnum.BOOL,   True)),
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__MAX_DISTANCE,     QtVariant(QtVariantTypeEnum.DOUBLE, 0.1)),
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__MIN_DISTANCE,     QtVariant(QtVariantTypeEnum.DOUBLE, 1e-05)),
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__NB_SECONDARY,              QtVariant(QtVariantTypeEnum.INT,    64)),
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__RELATIVE_SCALE,            QtVariant(QtVariantTypeEnum.BOOL,   True)),
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__FILTER_METHOD,            QtVariant(QtVariantTypeEnum.INT,    BakerFromMeshMatchEnum.ALWAYS)),
    BakingConverterParam(ConverterParamEnum.DETAIL_SECONDARY_COMMON__SPREAD,              QtVariant(QtVariantTypeEnum.DOUBLE, 180.0))
    # Missing
]

doc_module_attributes(sys.modules[__name__])
