# coding: utf-8
"""
Module **sbsbakerslibrary** provides the libraries of Bakers and their parameters that are defined in the
modules :mod:`.sbsbakersdef` and :mod:`.sbsbakingparameters`.

    * **Libraries:**
        * __library_Bakers: the library of Bakers, identified by :class:`.BakerEnum`
"""

from __future__ import unicode_literals
import re
import sys

from pysbs.api_decorators import doc_module_attributes,handle_exceptions,checkFirstParamIsAString
from pysbs import python_helpers
from . import sbsbakersenum
from . import sbsbakersdef



# Library of Bakers
__library_Bakers = {
    sbsbakersenum.BakerEnum.AMBIENT_OCCLUSION             : sbsbakersdef.baker_AMBIENT_OCCLUSION               ,
    sbsbakersenum.BakerEnum.AMBIENT_OCCLUSION_FROM_MESH   : sbsbakersdef.baker_AMBIENT_OCCLUSION_FROM_MESH     ,
    sbsbakersenum.BakerEnum.BENT_NORMALS_FROM_MESH        : sbsbakersdef.baker_BENT_NORMALS_FROM_MESH          ,
    sbsbakersenum.BakerEnum.COLOR_MAP_FROM_MESH           : sbsbakersdef.baker_COLOR_MAP_FROM_MESH             ,
    sbsbakersenum.BakerEnum.CONVERT_UV_TO_SVG             : sbsbakersdef.baker_CONVERT_UV_TO_SVG               ,
    sbsbakersenum.BakerEnum.CURVATURE                     : sbsbakersdef.baker_CURVATURE                       ,
    sbsbakersenum.BakerEnum.CURVATURE_MAP_FROM_MESH       : sbsbakersdef.baker_CURVATURE_MAP_FROM_MESH         ,
    sbsbakersenum.BakerEnum.HEIGHT_MAP_FROM_MESH          : sbsbakersdef.baker_HEIGHT_MAP_FROM_MESH            ,
    sbsbakersenum.BakerEnum.NORMAL_MAP_FROM_MESH          : sbsbakersdef.baker_NORMAL_MAP_FROM_MESH            ,
    sbsbakersenum.BakerEnum.OPACITY_MASK_FROM_MESH        : sbsbakersdef.baker_OPACITY_MASK_FROM_MESH          ,
    sbsbakersenum.BakerEnum.POSITION                      : sbsbakersdef.baker_POSITION                        ,
    sbsbakersenum.BakerEnum.POSITION_MAP_FROM_MESH        : sbsbakersdef.baker_POSITION_MAP_FROM_MESH          ,
    sbsbakersenum.BakerEnum.THICKNESS_MAP_FROM_MESH       : sbsbakersdef.baker_THICKNESS_MAP_FROM_MESH         ,
    sbsbakersenum.BakerEnum.TRANSFERRED_TEXTURE_FROM_MESH : sbsbakersdef.baker_TRANSFERRED_TEXTURE_FROM_MESH   ,
    sbsbakersenum.BakerEnum.WORLD_SPACE_DIRECTION         : sbsbakersdef.baker_WORLD_SPACE_DIRECTION           ,
    sbsbakersenum.BakerEnum.WORLD_SPACE_NORMALS           : sbsbakersdef.baker_WORLD_SPACE_NORMALS
}


@handle_exceptions()
def getBakerDefinition(aBaker):
    """
    getBakerDefinition(aBaker)
    Get the definition of the given baker identifier (from its ConverterID or identifier)

    :param aBaker: baker identifier
    :type aBaker: :class:`.BakerEnum` or str (ConverterID or identifier)
    :return: a :class:`.BakingConverter` object if found, None otherwise
    """
    if isinstance(aBaker, bytes) and not python_helpers.isStringOrUnicode(aBaker):
        aBaker = aBaker.decode()
    if python_helpers.isStringOrUnicode(aBaker):
        aBaker = getBakerEnum(aBaker)
    return __library_Bakers[aBaker]

@handle_exceptions()
def getBakerDefaultIdentifier(aBaker):
    """
    getBakerDefaultIdentifier(aBaker)
    Get the default string identifier of the given baker (from its ConverterID or identifier)

    :param aBaker: baker identifier
    :type aBaker: :class:`.BakerEnum` or str (ConverterID or identifier)
    :return: the default identifier as a string
    """
    aBakerDef = getBakerDefinition(aBaker)
    return aBakerDef.mIdentifier

@handle_exceptions()
@checkFirstParamIsAString
def getBakerEnum(aBakerID):
    """
    getBakerEnum(aBakerID)
    Get the enum value of the given baker (from its ConverterID or identifier)

    :param aBakerID: baker ConverterID (ex: 'BakerMeshConverterGLMapBakerManager.Curvature') or identifier (ex: 'Curvature [2]')
    :type aBakerID: str
    :return: the baker as a :class:`.BakerEnum`
    """
    match = re.search(' \[[0-9]+\]', aBakerID)
    if match is not None:       aBakerIdentifier = aBakerID[0:match.start()]
    else:                       aBakerIdentifier = aBakerID

    return next((key for key, value in __library_Bakers.items()
                 if value.mConverterID == aBakerID or value.mIdentifier == aBakerIdentifier ), None)



doc_module_attributes(sys.modules[__name__])
