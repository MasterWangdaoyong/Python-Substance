# coding: utf-8
"""
Module **mdllibclasses** provides all the classes used by the MDL library for the definition of all MDL entities.
In particular, it defines the classes:

- :class:`.MDLNodeDef`
- :class:`.MDLNodeDefInput`
- :class:`.MDLNodeDefOutput`
- :class:`.MDLNodeDefParam`
- :class:`.MDLNodeDefParamValue`
"""

from __future__ import unicode_literals
import abc
import copy
import random
import string

from pysbs.api_decorators import handle_exceptions, doc_inherit
from pysbs import api_helpers
from pysbs.sbsenum import ParamTypeEnum
from . import mdl_helpers
from . import mdloperand
from . import mdlannotation
from . import mdlenum
from . import mdldictionaries


class MDLLibObject(object):
    """
    Base class of all MDL library classes.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def fromJSON(self, jsonData):
        """
        fromJSON(jsonData)
        Build the object from the given JSON data

        :param jsonData: JSON data
        :type jsonData: dict
        """
        pass

@doc_inherit
class MDLTypeDef(MDLLibObject):
    """
    This class contains the definition of a MDL type.

    Members:
        * mPath                (str): mdl path of the type
        * mKind                (:class:`.MDLTypeDefKindEnum`): kind of type ('atomic', 'enum', 'struct', 'vector', ...)
        * mComponentType       (str, optional): For compound types, mdl path of the type of component
        * mComponentCount      (int, optional): For compound types, the number of components required
        * mRowCount            (int, optional): For matrix type, the number of rows
        * mColumnCount         (int, optional): For matrix type, the number of columns
        * mArrayDeferredSize   (bool, optional): For array type, defines if the size is known or deferred
        * mArraySizeIdentifier (str, optional): For array type, the size identifier
        * mEnumValues          (dict {key(str):value(int)}, optional: enumeration type definition
        * mStructMembers       (list of :class:`.MDLTypeStructMemberDef`, optional): struct type definition
        * mTextureShape        (str, optional): For texture type, the shape of the texture
    """
    def __init__(self, aPath = '',
                       aKind = mdlenum.MDLTypeDefKindEnum.UNKNOWN,
                       aComponentType = None,
                       aComponentCount = -1,
                       aRowCount = -1,
                       aColumnCount = -1,
                       aArrayDeferredSize = False,
                       aArraySizeIdentifier = None,
                       aEnumValues = None,
                       aStructMembers = None,
                       aTextureShape = None):
        super(MDLTypeDef, self).__init__()
        self.mPath = aPath
        self.mKind = aKind
        self.mEnumValues = aEnumValues or {}
        self.mComponentType = aComponentType
        self.mComponentCount = aComponentCount
        self.mRowCount = aRowCount
        self.mColumnCount = aColumnCount
        self.mArrayDeferredSize = aArrayDeferredSize
        self.mArraySizeIdentifier = aArraySizeIdentifier
        self.mStructMembers = aStructMembers or []
        self.mTextureShape = aTextureShape

    def fromJSON(self, jsonData):
        self.mPath = jsonData.get('mdl_path', '')
        self.mKind = mdldictionaries.getMDLTypeDefKindEnum(jsonData.get('type', 'unknown'))

        self.mEnumValues = {}
        jsonEnum = jsonData.get('enum', None)
        jsonEnumValues = jsonEnum.get('enumerators', []) if jsonEnum else []
        for aEnum in jsonEnumValues:
            if aEnum.get('name', None) is not None and aEnum.get('value', None) is not None:
                self.mEnumValues[aEnum['name']] = api_helpers.getTypedValueFromStr(aEnum['value'], ParamTypeEnum.INTEGER1)

        # Parse vector, matrix, color and array info
        jsonStruct = jsonData.get('vector', None)
        if jsonStruct is None:
            jsonStruct = jsonData.get('matrix', None)
        if jsonStruct is None:
            jsonStruct = jsonData.get('array', None)
        if jsonStruct is None:
            jsonStruct = jsonData.get('color', None)
        if jsonStruct is not None:
            jsonCompound = jsonStruct.get('compound', None)
            if jsonCompound:
                self.mComponentCount = api_helpers.getTypedValueFromStr(jsonCompound.get('component_count', '-1'), ParamTypeEnum.INTEGER1)
                self.mComponentType = jsonCompound.get('component_mdl_path', None)

            self.mColumnCount = api_helpers.getTypedValueFromStr(jsonStruct.get('column_count', '-1'), ParamTypeEnum.INTEGER1)
            self.mRowCount = api_helpers.getTypedValueFromStr(jsonStruct.get('row_count', '-1'), ParamTypeEnum.INTEGER1)
            self.mArrayDeferredSize = api_helpers.getTypedValueFromStr(jsonStruct.get('is_deferred_size', "false"),
                                                                       ParamTypeEnum.BOOLEAN)
            self.mArraySizeIdentifier = jsonStruct.get('size_identifier', None)

        self.mStructMembers = []
        jsonStruct = jsonData.get('struct', None)
        jsonStructMembers = jsonStruct.get('struct_members', []) if jsonStruct else []
        for jsonMember in jsonStructMembers:
            aMember = MDLTypeStructMemberDef()
            aMember.fromJSON(jsonMember)
            self.mStructMembers.append(aMember)

        jsonTexture = jsonData.get('texture', None)
        if jsonTexture:
            self.mTextureShape = jsonTexture.get('shape', None)

    def isArray(self):
        """
        isArray()
        Check whether the type is an array.

        :return: True if the type is an array, False otherwise
        """
        return self.mKind == mdlenum.MDLTypeDefKindEnum.ARRAY

    def isAtomic(self):
        """
        isAtomic()
        Check whether the type is atomic.

        :return: True if the type is atomic, False otherwise
        """
        return self.mKind == mdlenum.MDLTypeDefKindEnum.ATOMIC

    def isCall(self):
        """
        Check whether the type is a call.

        :return: True if the type is a call, False otherwise
        """
        return self.mPath.startswith(mdldictionaries.getMDLPredefTypePath(mdlenum.MDLPredefTypes.CALL))

    def isCompound(self):
        """
        isCompound()
        Check whether the type is a compound (vector, color, matrix).

        :return: True if the type is a compound, False otherwise
        """
        return self.mKind in [mdlenum.MDLTypeDefKindEnum.VECTOR,
                              mdlenum.MDLTypeDefKindEnum.MATRIX,
                              mdlenum.MDLTypeDefKindEnum.COLOR]

    def isEnum(self):
        """
        isEnum()
        Check whether the type an enum.

        :return: True if the type is an enum, False otherwise
        """
        return self.mKind == mdlenum.MDLTypeDefKindEnum.ENUM

    def isMaterial(self):
        """
        isMaterial()
        Check whether the type is a material.

        :return: True if the type is a material, False otherwise
        """
        return self.mPath == mdldictionaries.getMDLPredefTypePath(mdlenum.MDLPredefTypes.MATERIAL)

    def isReference(self):
        """
        isReference()
        Check whether the type is a reference.

        :return: True if the type is a reference, False otherwise
        """
        return self.mKind in [mdlenum.MDLTypeDefKindEnum.PARAM_REFERENCE,
                              mdlenum.MDLTypeDefKindEnum.REFERENCE] or \
                self.isResource()

    def isResource(self):
        """
        isResource()
        Check whether the type is a resource of any kind (texture, bsdf_measurement, ...).

        :return: True if the type is a resource, False otherwise
        """
        return self.mKind in [mdlenum.MDLTypeDefKindEnum.BSDF_MEASURE,
                              mdlenum.MDLTypeDefKindEnum.LIGHT_PROFILE,
                              mdlenum.MDLTypeDefKindEnum.RESOURCE,
                              mdlenum.MDLTypeDefKindEnum.TEXTURE]

    def isString(self):
        """
        isString()
        Check whether the type is a string.

        :return: True if the type is a string, False otherwise
        """
        return self.mPath == mdldictionaries.getMDLPredefTypePath(mdlenum.MDLPredefTypes.STRING)

    def isStruct(self):
        """
        isStruct()
        Check whether the type is a struct.

        :return: True if the type is a struct, False otherwise
        """
        return self.mKind == mdlenum.MDLTypeDefKindEnum.STRUCT

    def getModuleName(self):
        """
        getModuleName()
        Get the module name, which is the last part of the type's mdl path

        :return: The module name as a string
        """
        return mdl_helpers.getModuleName(self.mPath)

    def getModulePath(self):
        """
        getModulePath()
        Get the module path, which is the beginning of the type's mdl path, without the last module name

        :return: The module path as a string
        """
        return mdl_helpers.getModulePath(self.mPath)

    def toMDLOperand(self, aName = None):
        """
        toMDLOperand(aName = None)
        Convert this type definition to the appropriate MDLOperand, with the given name.

        :param aName: name of the operand. If None, the default name is used
        :type aName: str, optional
        :return: a :class:`.MDLOperand`
        """
        from . import MDLManager

        if aName is None:
            aName = self.getModuleName()

        # Create a MDLOperandValue with a default value depending on the type
        if self.isAtomic() or self.isCall() or self.isCompound() or self.isEnum() or self.isReference():
            aValue = mdl_helpers.formatValueForMdlTypeStr(aValue=None, aTypeDef=self)
            return mdloperand.MDLOperandValue(aName=aName, aType=self.mPath, aValue=aValue)

        # Create a MDLOperandArray with an empty item list
        elif self.isArray():
            return mdloperand.MDLOperandArray(aName=aName, aType=self.mPath, aItems=mdloperand.MDLOperands())

        # Create a MDLOperandStruct with default values in each member
        elif self.isStruct():
            membersOperands = []
            for aMember in self.mStructMembers:
                aTypeDef = MDLManager.getMDLTypeDefinition(aMember.mType)
                if aTypeDef:
                    aMemberOperand = aTypeDef.toMDLOperand(aMember.mName)
                    membersOperands.append(aMemberOperand)
            return mdloperand.MDLOperandStruct(aName=aName, aType=self.mPath, aMembers=mdloperand.MDLOperands(membersOperands))

        return None


@doc_inherit
class MDLTypeStructMemberDef(MDLLibObject):
    """
    This class contains the definition of a MDL type of kind struct.

    Members:
        * mName (str): name of the struct member
        * mType (str): mdl path of the type
    """
    def __init__(self, aName='', aType=None):
        super(MDLTypeStructMemberDef, self).__init__()
        self.mName = aName
        self.mType = aType

    def fromJSON(self, jsonData):
        self.mName = jsonData.get('name', '')
        self.mType = jsonData.get('type_mdl_path', '')


@doc_inherit
class MDLNodeDefType(MDLLibObject):
    """
    This class contains the definition of a MDL type.

    Members:
        * mName      (str): name of the parameter
        * mPath      (str): value of the parameter
        * mModifier  (str, optional): type of the parameter. Default to 'auto'
    """
    def __init__(self, aName = '',
                       aPath = '',
                       aModifier = 'auto'):
        super(MDLNodeDefType, self).__init__()
        self.mName = aName
        self.mPath = aPath
        self.mModifier = aModifier

    def fromJSON(self, jsonData):
        self.mName = jsonData.get('type_mdl_name', '')
        self.mPath = jsonData.get('type_mdl_path', '')
        self.mModifier = jsonData.get('type_modifier', 'auto')


@doc_inherit
class MDLAnnotationDef(MDLLibObject):
    """
    This class contains the definition of a MDL node annotation.

    Members:
        * mPath        (str): path of the mdl node
        * mParameters  (list of :class:`.MDLNodeDefParamValue`): the parameters available on this node.
    """
    def __init__(self, aPath = '',
                       aParameters = None):
        super(MDLAnnotationDef, self).__init__()
        self.mPath = aPath
        self.mParameters = aParameters

    def fromJSON(self, jsonData):
        self.mPath = jsonData.get('mdl_path', '')
        parameters = jsonData.get('parameters', [])
        self.mParameters = []
        for param in parameters:
            paramDef = MDLNodeDefParamValue()
            paramDef.fromJSON(param)
            self.mParameters.append(paramDef)

    def fromMDLAnnotation(self, aAnnotation):
        """
        fromMDLAnnotation(aAnnotation)
        Build the MDLAnnotationDef from a MDLAnnotation object

        :param aAnnotation: The operand to use to build this parameter
        :type aAnnotation: :class:`.MDLAnnotation`
        """
        self.mPath = aAnnotation.mPath
        self.mParameters = []
        for aOperand in aAnnotation.mOperands.getAllOperands():
            param = MDLNodeDefParamValue()
            param.mName = aOperand.mName
            param.mType = aOperand.mType
            param.mValue = aOperand.getValue()
            self.mParameters.append(param)

    def toMDLAnnotation(self):
        """
        toMDLAnnotation()
        Build the MDLAnnotation from this MDLAnnotationDef object

        :return: a :class:`.MDLAnnotation` object
        """
        from . import MDLManager

        aOperands = []
        for aParam in self.mParameters:
            aTypeDef = MDLManager.getMDLTypeDefinition(aParam.mType)
            if aTypeDef:
                aOperand = aTypeDef.toMDLOperand(aName=aParam.mName)
                if aParam.mValue != '':
                    aOperand.setValue(aParam.mValue)
                aOperands.append(aOperand)

        return mdlannotation.MDLAnnotation(aPath=self.mPath,
                                           aOperands=mdloperand.MDLOperands(aOperands))


@doc_inherit
class MDLNodeDefParam(MDLLibObject):
    """
    This class contains the definition of a MDL node parameter.

    Members:
        * mName         (str): name of the parameter
        * mAnnotations  (list of :class:`.MDLAnnotationDef`): annotations associated to this parameter
        * DefaultValue  (str or :class:`.MDLOperand`):  the default value of this parameter
        * mType         (:class:`.MDLNodeDefType`): type of the parameter
    """
    def __init__(self, aName = '',
                       aAnnotations = None,
                       aDefaultMDLValue = None,
                       aDefaultValue = None,
                       aDefaultValueType = None,
                       aTypeName = '',
                       aTypePath = '',
                       aTypeModifier = ''):
        super(MDLNodeDefParam, self).__init__()
        self.mName = aName
        self.mAnnotations = aAnnotations
        self.mDefaultMDLValue = aDefaultMDLValue
        self.mDefaultValue = aDefaultValue
        self.mDefaultValueType = aDefaultValueType
        self.mType = MDLNodeDefType(aTypeName, aTypePath, aTypeModifier)

    def fromJSON(self, jsonData):

        self.mName = jsonData.get('name', '')
        self.mType = MDLNodeDefType()
        self.mType.fromJSON(jsonData)
        self.mDefaultValueType = jsonData.get('default_value_type')
        self.mDefaultMDLValue = jsonData.get('default_value')

        annotations = jsonData.get('annotations', [])
        self.mAnnotations = []
        for annot in annotations:
            annotDef = MDLAnnotationDef()
            annotDef.fromJSON(annot)
            self.mAnnotations.append(annotDef)

    def fromMDLOperand(self, aOperand, copyValue=False):
        """
        fromMDLOperand(aOperand, copyValue=False)
        Build the MDLNodeDefParam from a MDLOperand object

        :param aOperand: The operand to use to build this parameter
        :param copyValue: True to set the value of the operand as the default parameter value. Default to False
        :type aOperand: :class:`.MDLOperand`
        :type copyValue: bool, optional
        """
        self.mName = aOperand.mName
        self.mType = MDLNodeDefType(aPath=aOperand.mType, aName=mdl_helpers.getModuleName(aOperand.mType))
        self.mDefaultValue = aOperand.getValue() if copyValue else None

    def fromMDLParameter(self, aParameter, copyValue=False):
        """
        fromSBSParameter(aParameter, copyValue=False)
        Build the MDLNodeDefParam from a MDLParameter object

        :param aParameter: The operand to use to build this parameter
        :param copyValue: True to set the value of the parameter as the default parameter value. Default to False
        :type aParameter: :class:`.MDLParameter`
        :type copyValue: bool, optional
        """
        self.mName = aParameter.mName
        aType = mdl_helpers.convertParamTypeEnumToMDLType(aParameter.getType())
        self.mType = MDLNodeDefType(aPath=aType, aName=mdl_helpers.getModuleName(aType))
        self.mDefaultValue = aParameter.getValue() if copyValue else None

    def getAnnotation(self, aAnnotation):
        """
        getAnnotation(aAnnotation)
        Get the annotation definition of the given annotation if defined in the parameter definition

        :param aAnnotation: The annotation to look for
        :type aAnnotation: :class:`.MDLAnnotationEnum`
        :return: The annotation as a :class:`.MDLAnnotationDef` if found, None otherwise
        """
        if not self.mAnnotations:
            return None
        if isinstance(aAnnotation, int):
            aAnnotation = mdldictionaries.getAnnotationPath(aAnnotation)
        return next((annot for annot in self.mAnnotations if annot.mPath == aAnnotation), None)

    def getDefaultValue(self):
        """
        getDefaultValue()
        Get the default value of this parameter

        :return: The default value
        """
        return self.mDefaultValue

    def getType(self):
        """
        getType()
        Get the mdl path of the type of this parameter

        :return: The mdl type as a string
        """
        return self.mType.mPath if self.mType else None

    def toMDLOperand(self):
        """
        toMDLOperand()
        Convert this parameter definition to the appropriate MDLOperand.

        :return: a :class:`.MDLOperand`
        """
        from . import MDLManager

        aType = self.mType.mPath if self.mDefaultValueType is None else self.mDefaultValueType
        aTypeDef = MDLManager.getMDLTypeDefinition(aType)
        if aTypeDef is None:
            return None
        aOperand = aTypeDef.toMDLOperand(aName = self.mName) if aTypeDef is not None else None

        # Init the default value from mdltools information
        if self.mDefaultValue is None and self.mDefaultMDLValue is not None and self.mDefaultValueType is not None:
            aOperand.setValue(self.__getDefaultMDLValue(self.mDefaultValueType, self.mDefaultMDLValue))
        # Set the default value
        if self.mDefaultValue is not None:
            aOperand.mValue = copy.deepcopy(self.mDefaultValue)
            aOperand.setIsDefaultValue(True)
        return aOperand


    def __getDefaultMDLValue(self, aType, aDefaultValue):
        """
        Get the default value as provided by mdltools, in a format appropriate to the type of parameter (string or MDLOperand)
        """
        from . import MDLManager

        aTypeDef = MDLManager.getMDLTypeDefinition(aType)
        if aTypeDef:
            if aTypeDef.isStruct():
                aOperand = aTypeDef.toMDLOperand(self.mName)
                members = MDLNodeDefParam.__parseDefaultMDLValue(aDefaultValue)

                if len(members) == len(aOperand.getMembers()):
                    for member, operand in zip(members, aOperand.getMembers()):
                        operand.setValue(self.__getDefaultMDLValue(operand.getType(), member))
                return aOperand

            elif aTypeDef.isArray():
                return []

            elif aTypeDef.isCall():
                posId = aDefaultValue.rfind('_')
                if posId != -1:
                    return aDefaultValue[0:posId+1] + ''.join(random.choice(string.digits) for _ in range(8))

        return aDefaultValue

    @staticmethod
    def __parseDefaultMDLValue(aDefaultValueString):
        """
        Parse the default value as returned by mdltools, to get a single value or a list of members, all as strings
        """
        if not aDefaultValueString:
            return aDefaultValueString

        members = []
        defaultString = aDefaultValueString

        # Struct members are surrounded by brackets
        while defaultString:
            if defaultString[0] != '[':
                return aDefaultValueString

            bracketStackSize = i = 1
            while i < len(defaultString):
                if defaultString[i] == '[':
                    bracketStackSize += 1
                elif defaultString[i] == ']':
                    bracketStackSize -= 1
                if bracketStackSize == 0:
                    break
                i += 1

            members.append(defaultString[1:i])
            defaultString = defaultString[i+1:]
        return members



@doc_inherit
class MDLNodeDefParamValue(MDLLibObject):
    """
    This class contains the definition of a MDL node parameter value.

    Members:
        * mName     (str): name of the parameter
        * mValue    (str): value of the parameter
        * mType     (str): type of the parameter
    """
    def __init__(self, aName = '',
                       aValue = '',
                       aType = ''):
        super(MDLNodeDefParamValue, self).__init__()
        self.mName = aName
        self.mValue = aValue
        self.mType = aType

    def fromJSON(self, jsonData):
        self.mName = jsonData.get('name', '')
        self.mValue = jsonData.get('value', '')
        self.mType = jsonData.get('value_type_mdl_path', '')

    def getType(self):
        """
        getType()
        Get the mdl path of the type of this parameter

        :return: The mdl type as a string
        """
        return self.mType


@doc_inherit
class MDLNodeDefInput(MDLLibObject):
    """
    This class contains the definition of a MDL node input.

    Members:
        * mIdentifier  (str): identifier of the output
        * mType        (:class:`.MDLNodeDefType`): type of the output
    """
    def __init__(self, aIdentifier = 'input',
                       aType = None):
        super(MDLNodeDefInput, self).__init__()
        self.mIdentifier = aIdentifier
        self.mType = aType

    def fromJSON(self, jsonData):
        self.mIdentifier = jsonData.get('name', '')
        self.mType = MDLNodeDefType()
        self.mType.fromJSON(jsonData)

    def fromMDLOperand(self, aOperand):
        """
        fromMDLOperand(aOperand)
        Build the MDLNodeDefInput from a MDLOperand object

        :param aOperand: The operand to use to build this input
        :type aOperand: :class:`.MDLOperand`
        """
        self.mIdentifier = aOperand.mName
        self.mType = MDLNodeDefType(aPath=aOperand.mType)

    def fromMDLInputBridging(self, aInputBridging):
        """
        fromMDLInputBridging(aInputBridging, aSBSGraph)
        Build the MDLNodeDefInput from a MDLInputBridging object

        :param aInputBridging: The operand to use to build this input
        :type aInputBridging: :class:`.MDLInputBridging`
        """
        self.mIdentifier = aInputBridging.mIdentifier
        aTypePath = 'mdl::texture_2d'
        self.mType = MDLNodeDefType(aPath=aTypePath, aName=mdl_helpers.getModuleName(aTypePath))

    def getType(self):
        """
        getType()
        Get the mdl path of the type of this input

        :return: The mdl type as a string
        """
        return self.mType.mPath if self.mType else None

    def getIdentifierStr(self):
        """
        getIdentifierStr()
        Gets the identifier of the input

        :return: The identifier as a string
        """
        return self.mIdentifier

@doc_inherit
class MDLNodeDefOutput(MDLLibObject):
    """
    This class contains the definition of a MDL node output.

    Members:
        * mIdentifier  (str): identifier of the output
        * mType        (:class:`.MDLNodeDefType`): type of the output
    """
    def __init__(self, aIdentifier = 'output',
                       aType = None):
        super(MDLNodeDefOutput, self).__init__()
        self.mType = aType
        self.mIdentifier = aIdentifier

    def fromJSON(self, jsonData):
        self.mType = MDLNodeDefType()
        self.mType.fromJSON(jsonData)

    def getType(self):
        """
        getType()
        Get the mdl path of the type of this output

        :return: The mdl type as a string
        """
        return self.mType.mPath if self.mType else None

    def fromMDLOutputBridging(self, aOutputBridging, aSBSGraph):
        """
        fromMDLOutputBridging(aOutputBridging, aSBSGraph)
        Build the MDLNodeDefOutput from a MDLOutputBridging object

        :param aOutputBridging: The operand to use to build this input
        :param aSBSGraph: The Substance Graph referenced by the input bridging
        :type aOutputBridging: :class:`.MDLInputBridging`
        :type aSBSGraph: :class:`.SBSGraph`
        """
        def isANormalOutput(output):
            return next((True for u in output.getUsages() if 'normal' in u.mName.lower()), False)

        self.mIdentifier = aOutputBridging.mIdentifier
        aOutput = aSBSGraph.getGraphOutput(self.mIdentifier)
        if aOutput is not None:
            if isANormalOutput(aOutput):
                aType = ParamTypeEnum.FLOAT3
            else:
                aType = aSBSGraph.getGraphOutputType(self.mIdentifier)
            aTypePath = mdl_helpers.convertParamTypeEnumToMDLType(aType)
            self.mType = MDLNodeDefType(aPath=aTypePath, aName=mdl_helpers.getModuleName(aTypePath))

    def getIdentifierStr(self):
        """
        getIdentifierStr()
        Gets the identifier of the output

        :return: The identifier as a string
        """
        return self.mIdentifier


@doc_inherit
class MDLNodeDef(MDLLibObject):
    """
    This class contains the definition of a MDL node.

    Members:
        * mPath          (str): path of the mdl node
        * mAnnotations   (list of :class:`.MDLAnnotation`): the annotations of the node.
        * mParameters    (list of :class:`.MDLNodeDefParam`): the parameters available on this node.
        * mInputs        (list of :class:`.MDLNodeDefInput`): the outputs of this node.
        * mOutputs       (list of :class:`.MDLNodeDefOutput`): the outputs of this node.
        * mIsSelector    (bool): Define if this node is a selector node
        * mIsMaterial    (bool): Define if this node is a material
        * mIsPassthrough (bool): Define if this node is a passthrough node (NOTE: not an actual MDL definition)
    """
    def __init__(self, aPath = '',
                       aAnnotations = None,
                       aParameters = None,
                       aInputs = None,
                       aOutputs = None,
                       aIsSelector = False,
                       aIsMaterial = False,
                       aIsPassthrough = False):
        super(MDLNodeDef, self).__init__()
        self.mPath = aPath
        self.mAnnotations = aAnnotations or []
        self.mParameters = aParameters or []
        self.mInputs = aInputs or []
        self.mOutputs = aOutputs or []
        self.mIsSelector = aIsSelector
        self.mIsMaterial = aIsMaterial
        self.mIsPassthrough = aIsPassthrough

    def fromJSON(self, jsonData):
        self.mPath = jsonData.get('mdl_path', '')
        self.mIsSelector = api_helpers.getTypedValueFromStr(jsonData.get('is_selector', '0'), ParamTypeEnum.BOOLEAN)

        annotations = jsonData.get('annotations', [])
        self.mAnnotations = []
        for annot in annotations:
            annotDef = MDLAnnotationDef()
            annotDef.fromJSON(annot)
            self.mAnnotations.append(annotDef)

        parameters = jsonData.get('parameters', [])
        self.mParameters = []
        for param in parameters:
            paramDef = MDLNodeDefParam()
            paramDef.fromJSON(param)
            self.mParameters.append(paramDef)

            inputDef = MDLNodeDefInput()
            inputDef.fromJSON(param)
            self.mInputs.append(inputDef)

        aOutput = MDLNodeDefOutput()
        aOutput.fromJSON(jsonData.get('return_desc', {}))
        self.mOutputs = [aOutput]

    @handle_exceptions()
    def getAllInputs(self):
        """
        getAllInputs()
        Get all the inputs in this node definition

        :return: a list of :class:`.MDLNodeDefInput`
        """
        return self.mInputs if self.mInputs else []

    @handle_exceptions()
    def getAllInputIdentifiers(self):
        """
        getAllInputIdentifiers()
        Get all the input identifiers as strings of this node definition

        :return: a list of string
        """
        return [aInput.mIdentifier for aInput in self.getAllInputs()]

    @handle_exceptions()
    def getAllOutputs(self):
        """
        getAllOutputs()
        Get all the outputs in this node definition

        :return: a list of :class:`.MDLNodeDefOutput`
        """
        return self.mOutputs if self.mOutputs else []

    @handle_exceptions()
    def getAllOutputIdentifiers(self):
        """
        getAllOutputIdentifiers()
        Get all the output identifiers as strings of this node definition

        :return: a list of string
        """
        return [aOutput.mIdentifier for aOutput in self.getAllOutputs()]

    @handle_exceptions()
    def getAllParameters(self):
        """
        getAllParameters()
        Get all the parameters in this node definition

        :return: a list of :class:`.MDLNodeDefParam`
        """
        return self.mParameters if self.mParameters else []

    @handle_exceptions()
    def getAllParameterIdentifiers(self):
        """
        getAllParameterIdentifiers()
        Get all the parameter identifiers as strings of this node definition

        :return: a list of string
        """
        return [aParam.mIdentifier for aParam in self.getAllParameters()]

    @handle_exceptions()
    def getDefaultOperands(self, aCheckType=False):
        """
        getDefaultOperands()
        Get the list of default operands corresponding to the parameters available on this node definition

        :param aCheckType: True to check the default connection visibility depending on the type of the operand. Default to False
        :type aCheckType: bool, optional
        :return: a list of :class:`.MDLOperand`
        """
        from .mdlmanager import MDLManager

        operandList = []
        paramListContainsRefOrMat = self.__paramListContainsRefOrMaterial() if aCheckType else False
        for aParam in self.mParameters:
            aOperand = aParam.toMDLOperand()
            if aOperand:
                aInput = self.getInput(aParam.mName)
                if aInput is not None:
                    annotVisible = aParam.getAnnotation(mdlenum.MDLAnnotationEnum.VISIBLE_BY_DEFAULT)
                    if annotVisible is not None:
                        aOperand.setConnectionAccepted(annotVisible.toMDLAnnotation().getValue() == 'true')
                    elif aCheckType:
                        aOperand.setConnectionAccepted(MDLManager.getAcceptConnectionByDefaultForType(aOperand.getType(),paramListContainsRefOrMat))
                    else:
                        aOperand.setConnectionAccepted(True)
                operandList.append(aOperand)
        return operandList

    @handle_exceptions()
    def getFirstInputOfType(self, aType):
        """
        getFirstInputOfType(aType)
        Get the first MDLInputDef with the given type.

        :param aType: mdl path of the required type
        :type aType: str
        :return: a :class:`.MDLInputDef` object if found, None otherwise
        """
        return next((i for i in self.getAllInputs() if i.getType() == aType), None)

    @handle_exceptions()
    def getFirstOutputOfType(self, aType):
        """
        getFirstOutputOfType(aType)
        Get the first MDLOutputDef with the given type.

        :param aType: mdl path of the required type
        :type aType: str
        :return: a :class:`.MDLOutputDef` object if found, None otherwise
        """
        return next((o for o in self.getAllOututs() if o.getType() == aType), None)

    @handle_exceptions()
    def getInput(self, aInput):
        """
        getInput(aInput)
        Get the input with the given identifier.

        :param aInput: The required input
        :type aInput: str
        :return: a :class:`.MDLNodeDefInput` if found, None otherwise
        """
        return next((i for i in self.getAllInputs() if i.mIdentifier == aInput), None)

    @handle_exceptions()
    def getOutput(self, aOutput = None):
        """
        getOutput(aOutput = None)
        Get the output with the given identifier. If aOutput is None, return the first output if it exists.

        :param aOutput: The required output
        :type aOutput: str
        :return: a :class:`.MDLNodeDefOutput` if found, None otherwise
        """
        if aOutput:
            return next((o for o in self.getAllOutputs() if o.mIdentifier == aOutput), None)
        else:
            return self.mOutputs[0] if self.mOutputs else None

    @handle_exceptions()
    def getParameter(self, aParameter):
        """
        getParameter(aParameter)
        Get the required parameter

        :param aParameter: The name of the parameter to get
        :type aParameter: str
        :return: a :class:`.MDLNodeDefParam` object if found, None otherwise
        """
        return next((param for param in self.getAllParameters() if param.mName == aParameter), None)


    def __paramListContainsRefOrMaterial(self):
        from .mdlmanager import MDLManager
        for p in self.getAllParameters():
            typeDef = MDLManager.getMDLTypeDefinition(p.mDefaultValueType or p.getType())
            if typeDef is not None and (typeDef.isReference() or (typeDef.isStruct() and typeDef.isMaterial())):
                return True
        return False
