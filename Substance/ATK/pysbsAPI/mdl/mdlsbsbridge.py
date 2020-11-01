# coding: utf-8
"""
Module **mdlsbsbridge** aims to define SBSObjects that are relative to a Substance graph instance in a MDL graph, mostly:

- :class:`.MDLParameter`
- :class:`.MDLParamValue`
- :class:`.MDLInputBridging`
- :class:`.MDLOutputBridging`
"""
from __future__ import unicode_literals

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject
from pysbs import api_helpers
from pysbs import sbsenum



# ==============================================================================
@doc_inherit
class MDLParameter(SBSObject):
    """
    Class that contains information of a parameter of a Substance Graph instance inserted in a MDLGraph.

    Members:
        * mName  (str): name of the parameter.
        * mValue (:class:`MDLParamValue`): value of this parameter.
        * mIsDefaultValue (str, optional): boolean indicating if the value of this parameter is the default one. Default to False
    """
    def __init__(self,
                 aName = '',
                 aValue = None,
                 aIsDefaultValue = None):
        super(MDLParameter, self).__init__()
        self.mName  = aName
        self.mValue = aValue
        self.mIsDefaultValue = aIsDefaultValue

        self.mMembersForEquality = ['mName',
                                    'mValue',
                                    'mIsDefaultValue']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName           = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'name'            )
        self.mValue          = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'value'           , MDLParamValue)
        self.mIsDefaultValue = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'is_default_value')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mName          , 'name'             )
        aSBSWriter.writeSBSNode(aXmlNode             ,  self.mValue         , 'value'            )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIsDefaultValue, 'is_default_value' )

    @handle_exceptions()
    def isDefaultValue(self):
        """
        isDefaultValue()

        :return: True if this value is the default value of the parameter
        """
        if self.mIsDefaultValue:
            return api_helpers.getTypedValueFromStr(aValue=self.mIsDefaultValue, aType=sbsenum.ParamTypeEnum.BOOLEAN)
        return False

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this parameter

        :return: the value as a string if it exists, None otherwise
        """
        return self.mValue.getValue() if self.mValue is not None else None

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Get the type of this parameter

        :return: the type of this parameter as a :class:`.ParamTypeEnum` if possible, None otherwise
        """
        return self.mValue.getType() if self.mValue is not None else None

    @handle_exceptions()
    def getTypedValue(self):
        """
        getTypedValue()
        Get the value in the type of the parameter (bool, int, ...).

        :return: The value in the type of the parameter if defined, None otherwise
        """
        return self.mValue.getTypedValue() if self.mValue is not None else None

    @handle_exceptions()
    def setIsDefaultValue(self, isDefaultValue):
        """
        setIsDefaultValue(isDefaultValue)
        Set if this parameter has the default value or not.

        :param isDefaultValue: True to define that this parameter has the default value.
        :type isDefaultValue: bool
        """
        self.mIsDefaultValue = '1' if isDefaultValue else None

    @handle_exceptions()
    def setValue(self, aValue, aType=None):
        """
        setValue(aValue, aType=None)
        Set the value of this parameter, and if aType is specified, set its type too, otherwise let the current type.

        :param aValue: the value to affect
        :param aType: the type to affect
        :type aValue: any type, depends on the parameter type
        :type aType: :class:`.ParamTypeEnum`
        """
        if self.mValue is None:
            self.mValue = MDLParamValue()
        self.mValue.setValue(aValue, aType)



# ==============================================================================
@doc_inherit
class MDLParamValue(SBSObject):
    """
    Class that contains information on a MDL parameter value as defined in a .sbs file

    Members:
        * mValue   (str): value of the parameter.
        * mTagName (str): the tag name associated to this parameter in the .sbs file (bool, int1,.., int4, float1,.., float4, string)
    """

    def __init__(self,
                 aValue=None,
                 aTagName=''):
        super(MDLParamValue, self).__init__()
        self.mValue = aValue
        self.mTagName = aTagName

        self.mMembersForEquality = ['mValue',
                                    'mTagName']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        aChildren = list(aXmlNode)
        if not aChildren or aChildren[0] is None:
            return

        self.mTagName = aChildren[0].tag
        self.mValue  = aSBSParser.getXmlElementVAttribValue(aXmlNode, self.mTagName)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mValue, self.mTagName )

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value.

        :return: The value as a string if defined, None otherwise
        """
        return self.mValue

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Get the type of this value

        :return: The type as a :class:`.ParamTypeEnum` if success, None otherwise
        """
        if   self.mTagName.endswith('bool'):            return sbsenum.ParamTypeEnum.BOOLEAN
        elif self.mTagName.endswith('int1'):            return sbsenum.ParamTypeEnum.INTEGER1
        elif self.mTagName.endswith('int2'):            return sbsenum.ParamTypeEnum.INTEGER2
        elif self.mTagName.endswith('int3'):            return sbsenum.ParamTypeEnum.INTEGER3
        elif self.mTagName.endswith('int4'):            return sbsenum.ParamTypeEnum.INTEGER4
        elif self.mTagName.endswith('float1'):          return sbsenum.ParamTypeEnum.FLOAT1
        elif self.mTagName.endswith('float2'):          return sbsenum.ParamTypeEnum.FLOAT2
        elif self.mTagName.endswith('float3'):          return sbsenum.ParamTypeEnum.FLOAT3
        elif self.mTagName.endswith('float4'):          return sbsenum.ParamTypeEnum.FLOAT4
        elif self.mTagName.endswith('string'):          return sbsenum.ParamTypeEnum.STRING
        return None

    @handle_exceptions()
    def getTypedValue(self):
        """
        getTypedValue()
        Get the value in the type of the parameter (bool, int, ...).

        :return: The value in the type of the parameter if defined, None otherwise
        """
        return api_helpers.getTypedValueFromStr(aValue=self.getValue(), aType=self.getType())

    @handle_exceptions()
    def setValue(self, aValue, aType=None):
        """
        setValue(aValue, aType=None)
        Set the value, and if aType is specified, set the tagname accordingly to the type of the value.
        If aType is let None, keep the current type.

        :param aValue: the value to set
        :param aType: type of the value
        :type aValue: str
        :type aType: :class:`.ParamTypeEnum`, optional
        """
        if aType is None:
            aType = self.getType()
        elif aType == sbsenum.ParamTypeEnum.BOOLEAN:        self.mTagName = 'bool'
        elif aType == sbsenum.ParamTypeEnum.INTEGER1:       self.mTagName = 'int1'
        elif aType == sbsenum.ParamTypeEnum.INTEGER2:       self.mTagName = 'int2'
        elif aType == sbsenum.ParamTypeEnum.INTEGER3:       self.mTagName = 'int3'
        elif aType == sbsenum.ParamTypeEnum.INTEGER4:       self.mTagName = 'int4'
        elif aType == sbsenum.ParamTypeEnum.FLOAT1:         self.mTagName = 'float1'
        elif aType == sbsenum.ParamTypeEnum.FLOAT2:         self.mTagName = 'float2'
        elif aType == sbsenum.ParamTypeEnum.FLOAT3:         self.mTagName = 'float3'
        elif aType == sbsenum.ParamTypeEnum.FLOAT4:         self.mTagName = 'float4'
        elif aType == sbsenum.ParamTypeEnum.STRING:         self.mTagName = 'string'
        elif aType == sbsenum.ParamTypeEnum.PATH:           self.mTagName = 'string'
        elif aType == sbsenum.ParamTypeEnum.FLOAT_VARIANT:
            if isinstance(aValue, int) or isinstance(aValue, float):
                self.mTagName = 'float1'
            else:
                self.mTagName = 'float4'
        else:
            raise SBSImpossibleActionError('Cannot set the value, unknown type: '+str(aType))

        if aType is None:
            raise SBSImpossibleActionError('Cannot set the value, unknown type')

        self.mValue = api_helpers.formatValueForTypeStr(aValue, aType)



# ==============================================================================
@doc_inherit
class MDLInputBridging(SBSObject):
    """
    Class that contains information of an input bridging of a MDLImplSBSInstance as defined in a .sbs file.

    Members:
        * mLocalIdentifier (str): Local identifier of the input
        * mIdentifier      (str): Identifier of the input
    """
    def __init__(self,
                 aLocalIdentifier = '',
                 aIdentifier      = ''):
        super(MDLInputBridging, self).__init__()
        self.mLocalIdentifier = aLocalIdentifier
        self.mIdentifier      = aIdentifier

        self.mMembersForEquality = ['mIdentifier']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mLocalIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'local_identifier')
        self.mIdentifier      = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'identifier'      )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mLocalIdentifier, 'local_identifier' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier     , 'identifier'       )



# ==============================================================================
@doc_inherit
class MDLOutputBridging(SBSObject):
    """
    Class that contains information of an output bridging of a MDLImplSBSInstance as defined in a .sbs file.

    Members:
        * mUID        (str): UID of the output
        * mIdentifier (str): Identifier of the output
    """
    def __init__(self,
                 aUID        = '',
                 aIdentifier = ''):
        super(MDLOutputBridging, self).__init__()
        self.mUID        = aUID
        self.mIdentifier = aIdentifier

        self.mMembersForEquality = ['mIdentifier']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'uid'        )
        self.mIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'identifier' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID       , 'uid'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier, 'identifier' )
