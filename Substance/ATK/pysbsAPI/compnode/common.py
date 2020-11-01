# coding: utf-8
"""
Module **compnode.common** provides the definition of :class:`.SBSCompOutput`, :class:`.SBSOutputBridging` and
:class:`.SBSCompImplWithParams`, which are used in the other modules in :mod:`.compnode`
"""
from __future__ import unicode_literals
import abc

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSLibraryError
from pysbs.common_interfaces import SBSObject
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import params



# =======================================================================
@doc_inherit
class SBSCompOutput(SBSObject):
    """
    Class that contains information on a compositing node output as defined in a .sbs file

    Members:
        * mUID      (str): node output unique identifier in the /compNodes/compOutputs/ context.
        * mCompType (str): return type of the output (color or grayscale). Type definition: :class:`.ParamTypeEnum`
    """
    def __init__(self,
                 aUID      = '',
                 aCompType = None):
        super(SBSCompOutput, self).__init__()
        self.mUID       = aUID
        self.mCompType  = aCompType

        self.mMembersForEquality = ['mCompType']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID      = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'uid'     )
        self.mCompType = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'comptype')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID     , 'uid'     )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mCompType, 'comptype')

@doc_inherit
class SBSCompInputValue(SBSObject):
    """
    Class that contains information about an input value in a .sbs file

    Members:
        * mIdentifier (str): Identifier for the input value.
        * mType       (str): Type for the value. Type definition: :class:`.ParamTypeEnum`
    """
    def __init__(self,
                 aIdentifier = '',
                 aType       = None):
        super(SBSCompInputValue, self).__init__()
        self.mIdentifier = aIdentifier
        self.mType       = aType

        self.mMembersForEquality = ['mIdentifier',
                                    'mType']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'identifier')
        self.mType      = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'type'      )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier, 'identifier')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType      , 'type'      )



# =======================================================================
@doc_inherit
class SBSOutputBridging(SBSObject):
    """
    Class that contains information on an output bridging as defined in a .sbs file

    Members:
        * mUID        (str): uid of the compositing node output (/compNode/compOutputs/compOutput/uid).
        * mIdentifier (str): graph definition output identifier (/graph/graphOutputs/graphOutput/identifier)
    """
    def __init__(self,
                 aUID = '',
                 aIdentifier = ''):
        super(SBSOutputBridging, self).__init__()
        self.mUID           = aUID
        self.mIdentifier    = aIdentifier

        self.mMembersForEquality = ['mIdentifier']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'uid'        )
        self.mIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'identifier' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID       , 'uid'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier, 'identifier' )



# =======================================================================
@doc_inherit
class SBSCompImplWithParams(SBSObject):
    """
    This class allows to gather the parameter management for classes :class:`.SBSCompFilter`, :class:`.SBSCompInstance`,
    :class:`.SBSCompInputBridge` and :class:`.SBSParamsGraphData`

    Members:
        * mParameters (list of :class:`.SBSParameter`): input parameters list.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 aParameters = None):
        super(SBSCompImplWithParams, self).__init__()
        self.mParameters    = aParameters if aParameters is not None else []

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mParameters = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'parameters', 'parameter', params.SBSParameter)

    @abc.abstractmethod
    def getDisplayName(self):
        """
        getDisplayName()
        Get the display name of this node

        :return: the display name as a string
        """
        return str(self)

    @abc.abstractmethod
    def getDefinition(self):
        """
        getDefinition()
        Get the definition of the node (Inputs, Outputs, Parameters)

        :return: a :class:`.CompNodeDef` object
        """
        pass

    @handle_exceptions()
    def getParameterValue(self, aParameter):
        """
        getParameterValue(aParameter)
        Find a parameter with the given name/id among the overloaded parameters and the default node parameters,
        and return its value.

        :param aParameter: Parameter identifier
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: The parameter value if found (string or :class:`.SBSDynamicValue`, None otherwise
        """
        if not python_helpers.isStringOrUnicode(aParameter):
            aParameterName = sbslibrary.getCompNodeParam(aParameter)
        else:
            aParameterName = aParameter

        # Parse the parameters overloaded on the CompFilter node
        if self.mParameters:
            param = next((param for param in self.mParameters if param.mName == aParameterName), None)
            if param is not None:
                return param.mParamValue.getValue()

        # Parse the default parameters of this filter
        nodeDef = self.getDefinition()
        defaultParam = nodeDef.getParameter(aParameter)
        if defaultParam is not None:
            return defaultParam.mDefaultValue

        return None

    @handle_exceptions()
    def hasIdenticalParameters(self, other):
        """
        hasIdenticalParameters(self, other)
        Allows to check if two nodes has the same parameters defined with the same values.

        :param other: the node to compare with
        :type other: :class:`.SBSCompImplWithParams`
        :return: True if the two nodes has the same parameters, False otherwise
        """
        if len(self.mParameters) != len(other.mParameters):
            return False
        for aParam in self.mParameters:
            aParamOther = next((p for p in other.mParameters if p.mName == aParam.mName), None)
            if aParamOther is None:
                return False
            if aParam.mParamValue.mTagName != aParamOther.mParamValue.mTagName:
                return False
            if aParam.mParamValue.getTypedConstantValue() != aParamOther.mParamValue.getTypedConstantValue():
                return False
        return True

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue, aRelativeTo = None):
        """
        setParameterValue(aParameter, aParamValue, aRelativeTo = None)
        Set the value of the given parameter to the given value, if compatible with this node.

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :param aRelativeTo: Inheritance of the parameter. Default is ABSOLUTE

        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aParamValue: :class:`.SBSDynamicValue` or any parameter type
        :type aRelativeTo: :class:`.ParamInheritanceEnum`

        :return: True if succeed, False otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        # Get Parameter name
        if not python_helpers.isStringOrUnicode(aParameter):
            aParameterName = sbslibrary.getCompNodeParam(aParameter)
        else:
            aParameterName = aParameter
        if aParameterName is None:
            raise SBSLibraryError('Parameter '+str(aParameter)+' cannot be set on '+self.getDisplayName())

        # Parse the default input parameter of the input node
        nodeDef = self.getDefinition()
        defaultParam = nodeDef.getParameter(aParameter)
        aType = defaultParam.mType if defaultParam is not None else None
        if aType is None:
            raise SBSLibraryError('Parameter '+aParameterName+' cannot be set on '+self.getDisplayName())

        isDynamic = isinstance(aParamValue, params.SBSDynamicValue)
        isDefaultValue = False

        # Ensure having a correctly formatted value
        if not isDynamic:
            aParamValue = api_helpers.formatValueForTypeStr(aParamValue, defaultParam.mType)
            isDefaultValue = aParamValue == api_helpers.formatValueForTypeStr(defaultParam.mDefaultValue, defaultParam.mType)

        # Handle inheritance
        # - Default Inheritance for this filter is applied by default
        aRelTo = nodeDef.mInheritance[0] if nodeDef.isBaseParameter(defaultParam) else sbsenum.ParamInheritanceEnum.ABSOLUTE
        # - If overloaded, check that this Inheritance is compatible with this filter
        if aRelativeTo is not None and aRelativeTo in nodeDef.mInheritance:
            isDefaultValue = isDefaultValue and aRelTo == aRelativeTo
            aRelTo = aRelativeTo

        # Parse the parameters already defined on this comp filter and modify it if found
        if self.mParameters:
            param = next((param for param in self.mParameters if param.mName == aParameterName), None)
            if param is not None:
                param.mRelativeTo = str(aRelTo)
                if isDynamic:           param.mParamValue.setDynamicValue(aParamValue)      # Set the dynamic value
                elif isDefaultValue:    self.mParameters.remove(param)                      # Remove the parameter
                else:                   param.mParamValue.updateConstantValue(aParamValue)  # Set the new parameter value
                return True

        # Create a new parameter
        if not isDefaultValue:
            aSBSParamValue = params.SBSParamValue()
            if isDynamic:   aSBSParamValue.setDynamicValue(aParamValue)
            else:           aSBSParamValue.setConstantValue(aType, aParamValue)
            aNewParam = params.SBSParameter(aName = aParameterName, aRelativeTo = str(aRelTo), aParamValue = aSBSParamValue)
            api_helpers.addObjectToList(self, 'mParameters', aNewParam)
        return True

    @handle_exceptions()
    def setDynamicParameter(self, aParameter, aRelativeTo = None):
        """
        setDynamicParameter(aParameter, aRelativeTo = None)
        Set the given parameter as dynamic, to init its params.SBSDynamicValue.
        If Inheritance is None, the default Inheritance for this node is set.

        :param aParameter: identifier of the parameter
        :param aRelativeTo: Inheritance of the parameter
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aRelativeTo: :class:`.ParamInheritanceEnum`
        :return: the :class:`.SBSDynamicValue` object if succeed, None otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        # Get Parameter name
        if not python_helpers.isStringOrUnicode(aParameter):
            aParameterName = sbslibrary.getCompNodeParam(aParameter)
        else:
            aParameterName = aParameter
        if aParameterName is None:
            raise SBSLibraryError('Parameter '+str(aParameter)+' cannot be set on '+self.getDisplayName())

        # Parse the parameters already defined on this comp filter and modify it if found
        if self.mParameters:
            param = next((param for param in self.mParameters if param.mName == aParameterName), None)
            if param is not None:
                return param.createEmptyDynamicValue()

        # Parse the default input parameter of an input bridge
        nodeDef = self.getDefinition()
        defaultParam = nodeDef.getParameter(aParameter)
        if defaultParam is None:
            raise SBSLibraryError('Parameter '+aParameterName+' cannot be set on '+self.getDisplayName())

        # Handle inheritance
        # - Default Inheritance for this filter is applied by default
        aRelTo = nodeDef.mInheritance[0] if nodeDef.isBaseParameter(defaultParam) else sbsenum.ParamInheritanceEnum.ABSOLUTE
        # - If overloaded, check that this Inheritance is compatible with this filter
        aRelTo = aRelativeTo if aRelativeTo is not None and aRelativeTo in nodeDef.mInheritance else aRelTo

        # Create a new parameter
        aNewParam = params.SBSParameter(aName = aParameterName, aRelativeTo = str(aRelTo))
        aDynValue = aNewParam.createEmptyDynamicValue()
        api_helpers.addObjectToList(self, 'mParameters', aNewParam)
        return aDynValue

    @handle_exceptions()
    def unsetParameter(self, aParameter):
        """
        unsetParameter(aParameter)
        Unset the given parameter so that it is reset to its default value.

        :param aParameter: identifier of the parameter to set
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: True if succeed, False otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        # Get Parameter name
        if not python_helpers.isStringOrUnicode(aParameter):
            aParameterName = sbslibrary.getCompNodeParam(aParameter)
        else:
            aParameterName = aParameter
        if aParameterName is None:
            raise SBSLibraryError('Parameter ' + str(aParameter) + ' cannot be unset on '+self.getDisplayName())

        # Parse the default input parameter of the input node
        nodeDef = self.getDefinition()
        defaultParam = nodeDef.getParameter(aParameter)
        if defaultParam is None:
            raise SBSLibraryError('Parameter ' + aParameterName + ' cannot be unset on '+self.getDisplayName())

        # Parse the parameters defined on this comp filter to find the given parameter
        if self.mParameters:
            param = next((param for param in self.mParameters if param.mName == aParameterName), None)
            if param is not None:
                self.mParameters.remove(param)
                return True

        return False
