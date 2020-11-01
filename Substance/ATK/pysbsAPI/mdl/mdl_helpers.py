# coding: utf-8

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)

from pysbs.api_decorators import handle_exceptions
from pysbs import sbsenum
from pysbs import api_helpers

from . import mdlenum


__SbsTypeToMdlTypeMap={
    sbsenum.ParamTypeEnum.ENTRY_COLOR:          'mdl::color'    ,
    sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE:      'mdl::float'    ,
    sbsenum.ParamTypeEnum.BOOLEAN:              'mdl::bool'     ,
    sbsenum.ParamTypeEnum.INTEGER1:             'mdl::int'      ,
    sbsenum.ParamTypeEnum.INTEGER2:             'mdl::int2'     ,
    sbsenum.ParamTypeEnum.INTEGER3:             'mdl::int3'     ,
    sbsenum.ParamTypeEnum.INTEGER4:             'mdl::int4'     ,
    sbsenum.ParamTypeEnum.FLOAT1:               'mdl::float'    ,
    sbsenum.ParamTypeEnum.FLOAT2:               'mdl::float2'   ,
    sbsenum.ParamTypeEnum.FLOAT3:               'mdl::float3'   ,
    sbsenum.ParamTypeEnum.FLOAT4:               'mdl::float4'   ,
    sbsenum.ParamTypeEnum.STRING:               'mdl::string'   ,
    sbsenum.ParamTypeEnum.PATH:                 'mdl::string'
}

__MdlTypeToSbsTypeMap={
    'mdl::bool'     :   sbsenum.ParamTypeEnum.BOOLEAN  ,
    'mdl::int'      :   sbsenum.ParamTypeEnum.INTEGER1 ,
    'mdl::int2'     :   sbsenum.ParamTypeEnum.INTEGER2 ,
    'mdl::int3'     :   sbsenum.ParamTypeEnum.INTEGER3 ,
    'mdl::int4'     :   sbsenum.ParamTypeEnum.INTEGER4 ,
    'mdl::float'    :   sbsenum.ParamTypeEnum.FLOAT1   ,
    'mdl::float2'   :   sbsenum.ParamTypeEnum.FLOAT2   ,
    'mdl::float3'   :   sbsenum.ParamTypeEnum.FLOAT3   ,
    'mdl::float4'   :   sbsenum.ParamTypeEnum.FLOAT4   ,
    'mdl::double'   :   sbsenum.ParamTypeEnum.FLOAT1   ,
    'mdl::double2'  :   sbsenum.ParamTypeEnum.FLOAT2   ,
    'mdl::double3'  :   sbsenum.ParamTypeEnum.FLOAT3   ,
    'mdl::double4'  :   sbsenum.ParamTypeEnum.FLOAT4   ,
    'mdl::string'   :   sbsenum.ParamTypeEnum.STRING
}

@handle_exceptions()
def convertParamTypeEnumToMDLType(aType):
    """
    convertParamTypeEnumToMDLType(aType)
    Convert the given substance type into a mdl type

    :param aType: The type as a :class:`.ParamTypeEnum`
    :type aType: :class:`.ParamTypeEnum`
    :return: the corresponding mdl type as a string if possible, None otherwise
    """
    return __SbsTypeToMdlTypeMap.get(aType, None)


@handle_exceptions()
def formatValueForMdlTypeStr(aValue, aTypeDef):
    """
    formatValueForMdlTypeStr(aValue, aTypeDef)
    Format the given value to respect the .sbs format according to the expected mdl type.

    :param aValue: input value
    :param aTypeDef: required type definition
    :type aValue: any type
    :type aTypeDef: :class:`.MDLTypeDef`
    :return: The value correctly formatted for the required type as a string, as this type is saved in .sbs format, if possible, None otherwise
    """
    aRes = aValue
    aDimension = -1
    if aTypeDef.isAtomic():
        aType = __MdlTypeToSbsTypeMap.get(aTypeDef.mPath, None)
    elif aTypeDef.isEnum():
        aType = sbsenum.ParamTypeEnum.INTEGER1
    elif aTypeDef.isCompound():
        aType = __MdlTypeToSbsTypeMap.get(aTypeDef.mComponentType, None)
        if aTypeDef.mKind == mdlenum.MDLTypeDefKindEnum.MATRIX:
            aDimension = aTypeDef.mRowCount * aTypeDef.mColumnCount
        else:
            aDimension = aTypeDef.mComponentCount
    elif aTypeDef.isReference():
        aType = sbsenum.ParamTypeEnum.STRING
    else:
        aType = None

    if aType is not None:
        aRes = api_helpers.formatValueForTypeStr(aValue, aType, aSep=';', aDimension=aDimension, aBooleanAsString=True)

    return aRes


@handle_exceptions()
def getTypedValueFromMdlStr(aValue, aTypeDef):
    """
    getTypedValueFromMdlStr(aValue, aTypeDef)
    Get the typed value from a string formatted as in .sbs format in MDL nodes.

    :param aValue: input value
    :param aTypeDef: required type definition
    :type aValue: str
    :type aTypeDef: :class:`.MDLTypeDef`
    :return: The value correctly typed considering the required type
    """
    if aTypeDef.isAtomic():
        aType = __MdlTypeToSbsTypeMap.get(aTypeDef.mPath, None)
    elif aTypeDef.isEnum():
        aType = sbsenum.ParamTypeEnum.INTEGER1
    elif aTypeDef.isCompound():
        aType = __MdlTypeToSbsTypeMap.get(aTypeDef.mComponentType, None)
    elif aTypeDef.isReference() or aTypeDef.isCall():
        aType = sbsenum.ParamTypeEnum.STRING
    else:
        aType = sbsenum.ParamTypeEnum.STRING
        log.warning('getTypedValueFromMdlStr, unknown type: '+aTypeDef.mPath)

    return api_helpers.getTypedValueFromStr(aValue, aType, aSep=';')

@handle_exceptions()
def getModuleName(aPath):
    """
    getModuleName(aPath)
    Get the module name, which is the last part of the given mdl path

    :param aPath: The input path
    :param aPath: str
    :return: The module name as a string
    """
    pos = aPath.rfind('::')
    return aPath[pos+2:] if pos >= 0 else aPath

@handle_exceptions()
def getModulePath(aPath):
    """
    getModulePath(aPath)
    Get the module path, which is the beginning of the given mdl path, without the last module name

    :param aPath: The input path
    :param aPath: str
    :return: The module path as a string
    """
    pos = aPath.rfind('::')
    return aPath[0:pos] if pos >= 0 else aPath

@handle_exceptions()
def pathHasSignature(aPath):
    """
    pathHasSignature(aPath)
    Check if the given mdl path has a complete signature or not

    :param aPath: The path to check
    :param aPath: str
    :return: True if the given path has a complete signature, False otherwise
    """
    if '$' in aPath:
        dollarPosition = aPath.find('$')
        beginP = aPath.find('(')
        endP = aPath.rfind(')')
        return 0 < dollarPosition < beginP < endP == len(aPath)-1
    else:
        beginP = aPath.find('(')
        endP = aPath.rfind(')')
        return 0 < beginP < endP == len(aPath)-1

@handle_exceptions()
def removePathSignature(aPath):
    """
    removePathSignature(aPath)
    Remove the signature part of the given mdl

    :param aPath: The path to modify
    :param aPath: str
    :return: the modified path
    """
    if '$' in aPath:
        return aPath[:aPath.find('$')]
    elif pathHasSignature(aPath):
        return aPath[:aPath.find('(')]
    else:
        aPath


