# coding: utf-8
"""
Module **sbsarenum** provides all the enumeration used in the SBSAR file format
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_source_code_enum, handle_exceptions
from pysbs import python_helpers
from pysbs import sbsenum


@doc_source_code_enum
class SBSARTypeEnum:
    """
    Enumeration of all the input types as saved in a .sbsar file
    """
    FLOAT1   ,\
    FLOAT2   ,\
    FLOAT3   ,\
    FLOAT4   ,\
    INTEGER1 ,\
    IMAGE    ,\
    STRING   ,\
    FONT     ,\
    INTEGER2 ,\
    INTEGER3 ,\
    INTEGER4 ,\
    = range(11)


@handle_exceptions()
def convertSbsarType2SbsType(aType):
    """
    convertSbsarType2SbsType()
    Convert the given SBSAR parameter type into SBS parameter type

    :param aType: the type to convert
    :type aType: :class:`.SBSARTypeEnum`
    :return: the type as a :class:`.ParamTypeEnum`
    """
    if python_helpers.isStringOrUnicode(aType):
        aType = int(aType)
    if aType == SBSARTypeEnum.FLOAT1:      return sbsenum.ParamTypeEnum.FLOAT1
    elif aType == SBSARTypeEnum.FLOAT2:    return sbsenum.ParamTypeEnum.FLOAT2
    elif aType == SBSARTypeEnum.FLOAT3:    return sbsenum.ParamTypeEnum.FLOAT3
    elif aType == SBSARTypeEnum.FLOAT4:    return sbsenum.ParamTypeEnum.FLOAT4
    elif aType == SBSARTypeEnum.INTEGER1:  return sbsenum.ParamTypeEnum.INTEGER1
    elif aType == SBSARTypeEnum.INTEGER2:  return sbsenum.ParamTypeEnum.INTEGER2
    elif aType == SBSARTypeEnum.INTEGER3:  return sbsenum.ParamTypeEnum.INTEGER3
    elif aType == SBSARTypeEnum.INTEGER4:  return sbsenum.ParamTypeEnum.INTEGER4
    elif aType == SBSARTypeEnum.STRING:    return sbsenum.ParamTypeEnum.STRING
    return aType
