# coding: utf-8
"""
Module **sbsbakersdef** provides the definition of all the bakers (:class:`.BakingConverter`) available in Substance Designer.

.. note::
    Note that in addition to their specific properties, all bakers have a list of 'Output' properties and 'Common to all bakers' properties, which are defined in the module :mod:`.sbsbakersdefaultprops`

* baker_AMBIENT_OCCLUSION
* baker_AMBIENT_OCCLUSION_FROM_MESH
* baker_BENT_NORMALS_FROM_MESH
* baker_COLOR_MAP_FROM_MESH
* baker_CONVERT_UV_TO_SVG
* baker_CURVATURE
* baker_CURVATURE_MAP_FROM_MESH
* baker_HEIGHT_MAP_FROM_MESH
* baker_NORMAL_MAP_FROM_MESH
* baker_OPACITY_MASK_FROM_MESH
* baker_POSITION
* baker_POSITION_MAP_FROM_MESH
* baker_THICKNESS_MAP_FROM_MESH
* baker_TRANSFERRED_TEXTURE_FROM_MESH
* baker_WORLD_SPACE_DIRECTION
* baker_WORLD_SPACE_NORMALS

"""

from __future__ import unicode_literals
import sys

from pysbs.api_decorators import doc_module_attributes
from pysbs.qtclasses import QtVariantTypeEnum, QtVariant

from . import sbsbakersdefaultprops
from . import sbsbakersdictionaries as bakersdict
from .sbsbakersenum import *
from .sbsbakingconverterparam import BakingConverterParam
from .sbsbakingconverter import BakingConverter



baker_AMBIENT_OCCLUSION= BakingConverter(
    aIdentifier = 'Ambient Occlusion',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.SeAO',
    aProperties = [
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__INVERT_GREEN, QtVariant(QtVariantTypeEnum.INT, BakerNormalOrientationEnum.DIRECTX)),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__NORMAL_MAP,         QtVariant(QtVariantTypeEnum.STRING, '')),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__NORMAL_WORLD_SPACE,          QtVariant(QtVariantTypeEnum.BOOL, False)),
        BakingConverterParam(ConverterParamEnum.SEAO__INVERT_NORMALS      ,  QtVariant(QtVariantTypeEnum.BOOL,   False)),
        BakingConverterParam(ConverterParamEnum.SEAO__QUALITY             ,  QtVariant(QtVariantTypeEnum.INT,    BakerAOQualityEnum.MEDIUM)),
        BakingConverterParam(ConverterParamEnum.SEAO__USE_NEIGHBORS,  QtVariant(QtVariantTypeEnum.BOOL,   False)),
        BakingConverterParam(ConverterParamEnum.SEAO__DISTANCE_FADE       ,  QtVariant(QtVariantTypeEnum.DOUBLE, 0.01)),
        BakingConverterParam(ConverterParamEnum.SEAO__ERROR_BIAS      ,  QtVariant(QtVariantTypeEnum.DOUBLE, 0.6))
    ])

baker_AMBIENT_OCCLUSION_FROM_MESH= BakingConverter(
    aIdentifier = 'Ambient Occlusion Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.AOFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = sbsbakersdefaultprops.sSecondaryRayCommonProperties +
    [
        BakingConverterParam(ConverterParamEnum.DETAIL_AO__ATTENUATION, QtVariant(QtVariantTypeEnum.INT, BakerAOAttenuationEnum.LINEAR)),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__INVERT_GREEN, QtVariant(QtVariantTypeEnum.INT,    BakerNormalOrientationEnum.DIRECTX)),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__NORMAL_MAP,         QtVariant(QtVariantTypeEnum.STRING, '')),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__NORMAL_WORLD_SPACE,          QtVariant(QtVariantTypeEnum.BOOL,   False))
    ])

baker_BENT_NORMALS_FROM_MESH= BakingConverter(
    aIdentifier = 'Bent Normals Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.BentNormalsFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = sbsbakersdefaultprops.sSecondaryRayCommonProperties +
                  sbsbakersdefaultprops.sNormalBakersCommonProperties
    )

baker_COLOR_MAP_FROM_MESH= BakingConverter(
    aIdentifier = 'Color Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.ColorFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = [
        BakingConverterParam(ConverterParamEnum.DETAIL_COLOR__COLOR_GENERATOR,    QtVariant(QtVariantTypeEnum.INT, BakerColorGeneratorEnum.HUE_SHIFT)),
        BakingConverterParam(ConverterParamEnum.DETAIL_COLOR__COLOR_SOURCE,       QtVariant(QtVariantTypeEnum.INT, BakerColorSourceEnum.VERTEX_COLOR))
    ])
# Force an override on the SubSampling parameter
baker_COLOR_MAP_FROM_MESH.setParameterValue(ConverterParamEnum.DETAIL__SUB_SAMPLING, BakerFromMeshSubSamplingEnum.NONE)

baker_CONVERT_UV_TO_SVG= BakingConverter(
    aIdentifier = 'Convert UV to SVG',
    aConverterID = 'VectorialMeshConverter',
    aForcedOutputFormat = bakersdict.getBakerOutputFormatName(BakerOutputFormatEnum.SVG),
    aBakerType = 'vectorialmeshconverter',
    aProperties = [
        BakingConverterParam(ConverterParamEnum.UV2SVG__COLOR_MODE, QtVariant(QtVariantTypeEnum.INT, BakerColorModeEnum.HUE_SHIFT)),
        BakingConverterParam(ConverterParamEnum.UV2SVG__PADDING,    QtVariant(QtVariantTypeEnum.INT, 0))
    ])

baker_CURVATURE = BakingConverter(
    aIdentifier = 'Curvature',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.Curvature',
    aProperties = [
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__INVERT_GREEN,                QtVariant(QtVariantTypeEnum.INT,    BakerNormalOrientationEnum.DIRECTX)),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__NORMAL_MAP,                        QtVariant(QtVariantTypeEnum.STRING, '')),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__NORMAL_WORLD_SPACE,                         QtVariant(QtVariantTypeEnum.BOOL,   False)),
        BakingConverterParam(ConverterParamEnum.CURVATURE__PER_VERTEX,    QtVariant(QtVariantTypeEnum.INT,    BakerCurvatureAlgoEnum.PER_PIXEL)),
        BakingConverterParam(ConverterParamEnum.CURVATURE__CURVATURE_MULTIPLIER,      QtVariant(QtVariantTypeEnum.DOUBLE, 0.5)),
        BakingConverterParam(ConverterParamEnum.CURVATURE__ENABLE_SEAMS, QtVariant(QtVariantTypeEnum.BOOL,   True)),
        BakingConverterParam(ConverterParamEnum.CURVATURE__SEAMS_POWER,  QtVariant(QtVariantTypeEnum.DOUBLE, 1.0))
    ])

baker_CURVATURE_MAP_FROM_MESH = BakingConverter(
    aIdentifier = 'Curvature Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.CurvatureFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = [
        BakingConverterParam(ConverterParamEnum.DETAIL_CURVATURE__INTENSITY,      QtVariant(QtVariantTypeEnum.DOUBLE,    1.0)),
        BakingConverterParam(ConverterParamEnum.DETAIL_CURVATURE__SOFT_SATURATE,  QtVariant(QtVariantTypeEnum.BOOL,      True)),
        BakingConverterParam(ConverterParamEnum.DETAIL_CURVATURE__MAXIMIZE_RANGE, QtVariant(QtVariantTypeEnum.BOOL,     False))
    ])

baker_HEIGHT_MAP_FROM_MESH = BakingConverter(
    aIdentifier = 'Height Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.HeightFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = sbsbakersdefaultprops.sDistanceCommonProperties
    )

baker_NORMAL_MAP_FROM_MESH = BakingConverter(
    aIdentifier = 'Normal Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.NormalFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = sbsbakersdefaultprops.sNormalBakersCommonProperties
    )

baker_OPACITY_MASK_FROM_MESH = BakingConverter(
    aIdentifier = 'Opacity Mask from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.MaskFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = []
    )

baker_POSITION = BakingConverter(
    aIdentifier = 'Position',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.Position',
    aProperties = sbsbakersdefaultprops.sPositionBakersCommonProperties
    )

baker_POSITION_MAP_FROM_MESH = BakingConverter(
    aIdentifier = 'Position Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.PositionFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = sbsbakersdefaultprops.sPositionBakersCommonProperties
    )

baker_THICKNESS_MAP_FROM_MESH = BakingConverter(
    aIdentifier = 'Thickness Map from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.ThicknessFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = sbsbakersdefaultprops.sSecondaryRayCommonProperties +
                  sbsbakersdefaultprops.sDistanceCommonProperties
    )
# Change Ignore backface secondary default value, set to False
baker_THICKNESS_MAP_FROM_MESH.setParameterValue(ConverterParamEnum.DETAIL_SECONDARY_COMMON__IGNORE_BACKFACE_SECONDARY, False)

baker_TRANSFERRED_TEXTURE_FROM_MESH = BakingConverter(
    aIdentifier = 'Transferred Texture from Mesh',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.TextureFromDetail',
    aCommonProperties = sbsbakersdefaultprops.sDetailBakerCommonProperties,
    aProperties = sbsbakersdefaultprops.sNormalBakersCommonProperties +
    [
        BakingConverterParam(ConverterParamEnum.DETAIL_TEXTURE__FILTERING_MODE,     QtVariant(QtVariantTypeEnum.INT,    BakerFilteringModeEnum.BILINEAR)),
        BakingConverterParam(ConverterParamEnum.DETAIL_TEXTURE__HIGH_POLY_UV_SET,   QtVariant(QtVariantTypeEnum.INT,    0)),
        BakingConverterParam(ConverterParamEnum.DETAIL_TEXTURE__IS_NORMAL_MAP,         QtVariant(QtVariantTypeEnum.BOOL,   False)),
        BakingConverterParam(ConverterParamEnum.DETAIL_TEXTURE__TEXTURE_FILE,       QtVariant(QtVariantTypeEnum.STRING, ''))
    ])

baker_WORLD_SPACE_DIRECTION = BakingConverter(
    aIdentifier = 'World Space Direction',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.WorldDirection',
    aProperties = [
        BakingConverterParam(ConverterParamEnum.WORLD_DIRECTION__CONST_DIRECTION,    QtVariant(QtVariantTypeEnum.INT,    BakerInputDirectionEnum.FROM_UNIFORM_VECTOR)),
        BakingConverterParam(ConverterParamEnum.WORLD_DIRECTION__DIRECTION_MAP,     QtVariant(QtVariantTypeEnum.STRING, '')),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__INVERT_GREEN, QtVariant(QtVariantTypeEnum.INT,    BakerNormalOrientationEnum.DIRECTX)),
        BakingConverterParam(ConverterParamEnum.WORLD_DIRECTION__X,  QtVariant(QtVariantTypeEnum.DOUBLE, 0.0)),
        BakingConverterParam(ConverterParamEnum.WORLD_DIRECTION__Y,  QtVariant(QtVariantTypeEnum.DOUBLE, -1.0)),
        BakingConverterParam(ConverterParamEnum.WORLD_DIRECTION__Z,  QtVariant(QtVariantTypeEnum.DOUBLE, 0.0))
    ])

baker_WORLD_SPACE_NORMALS = BakingConverter(
    aIdentifier = 'World Space Normals',
    aConverterID = 'BakerMeshConverterGLMapBakerManager.NormalWS',
    aProperties = [
        BakingConverterParam(ConverterParamEnum.NORMAL_WORLD_SPACE__BAKE_TYPE,          QtVariant(QtVariantTypeEnum.INT,    BakerBakingTypeEnum.NORMAL)),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__NORMAL_MAP,         QtVariant(QtVariantTypeEnum.STRING, '')),
        BakingConverterParam(ConverterParamEnum.ADDITIONAL__INVERT_GREEN, QtVariant(QtVariantTypeEnum.INT,    BakerNormalOrientationEnum.DIRECTX))
    ])

doc_module_attributes(sys.modules[__name__])
