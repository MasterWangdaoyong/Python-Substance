# coding: utf-8
"""
Module **sbslibclasses** provides all the classes used by the library for the definition of Filters, Functions,
FxMap nodes and Widgets.
"""

from __future__ import unicode_literals
import abc

from pysbs import sbsenum
from pysbs import python_helpers, api_helpers
from pysbs.api_decorators import doc_inherit, handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError

from . import sbsdictionaries


class LibObject(object):
    """
    Base class of all library classes.
    """
    __metaclass__ = abc.ABCMeta


class NodeLibObject(LibObject):
    """
    Base class of all library classes related to nodes (input, outputs, parameters, node definition).
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(NodeLibObject, self).__init__()
        self._dictGetInputEnumFct = None
        self._dictGetInputNameFct = None
        self._dictGetOutputEnumFct = None
        self._dictGetOutputNameFct = None
        self._dictGetParamEnumFct = None
        self._dictGetParamNameFct = None


class NodeInput(NodeLibObject):
    """
    Base class of :class:`.CompNodeInput` and :class:`.FunctionInput`.

    Members:
        * mIdentifier   (int or str): identifier of the input.
        * mType         (:class:`.ParamTypeEnum`): type of the input.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aIdentifier, aType = sbsenum.ParamTypeEnum.ENTRY_VARIANT):
        super(NodeInput, self).__init__()
        self.mIdentifier = aIdentifier
        self.mType = aType

    @handle_exceptions()
    def getIdentifier(self):
        """
        getIdentifier()
        Get the input identifier as an enum value if possible, or as a string if it is a custom input

        :return: the input identifier as an integer if possible, or as a string otherwise
        """
        res = None
        if python_helpers.isStringOrUnicode(self.mIdentifier):
            res = self._dictGetInputEnumFct(self.mIdentifier)
        return res if res is not None else self.mIdentifier

    @handle_exceptions()
    def getIdentifierStr(self):
        """
        getIdentifierStr()
        Get the input identifier as a string

        :return: the input identifier as a string
        """
        if python_helpers.isStringOrUnicode(self.mIdentifier) or self._dictGetInputNameFct is None:
            return self.mIdentifier
        return self._dictGetInputNameFct(self.mIdentifier)


class NodeOutput(NodeLibObject):
    """
    Base class of :class:`.CompNodeOutput` and :class:`.FunctionOutput`.

    Members:
        * mIdentifier   (int or str): identifier of the output.
        * mType         (:class:`.ParamTypeEnum`): type of the output.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aIdentifier, aType = sbsenum.ParamTypeEnum.ENTRY_VARIANT):
        super(NodeOutput, self).__init__()
        self.mIdentifier = aIdentifier
        self.mType = aType

    @handle_exceptions()
    def getIdentifier(self):
        """
        getIdentifier()
        Get the output identifier as an enum value if possible, or as a string if it is a custom output

        :return: the output identifier as an integer if possible, or as a string otherwise
        """
        res = None
        if python_helpers.isStringOrUnicode(self.mIdentifier):
            res = self._dictGetOutputEnumFct(self.mIdentifier)
        return res if res is not None else self.mIdentifier

    @handle_exceptions()
    def getIdentifierStr(self):
        """
        getIdentifierStr()
        Get the output identifier as a string

        :return: the output identifier as a string
        """
        if python_helpers.isStringOrUnicode(self.mIdentifier) or self._dictGetOutputNameFct is None:
            return self.mIdentifier
        return self._dictGetOutputNameFct(self.mIdentifier)


class NodeParam(NodeLibObject):
    """
    Base class of :class:`.CompNodeParam` and :class:`.FunctionParam`.

    Members:
        * mParameter    (int): identifier of the parameter.
        * mType         (:class:`.ParamTypeEnum`): type of the parameter.
        * mDefaultValue (depends on the type): default value of the parameter.
        * mIsConnectable (bool): Whether this parameter is connectable
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aParameter, aType, aDefaultValue = '', aIsConnectable = False):
        super(NodeParam, self).__init__()
        self.mParameter = aParameter
        self.mType = aType
        self.mDefaultValue = aDefaultValue
        self.mIsConnectable = aIsConnectable

    @handle_exceptions()
    def getIdentifier(self):
        """
        getIdentifier()
        Get the parameter identifier as an enum value if possible, or as a string if it is a custom parameter

        :return: the parameter identifier as an integer if possible, or as a string otherwise
        """
        res = None
        if python_helpers.isStringOrUnicode(self.mParameter):
            res = self._dictGetParamEnumFct(self.mParameter)
        return res if res is not None else self.mParameter

    @handle_exceptions()
    def getIdentifierStr(self):
        """
        getIdentifierStr()
        Get the parameter identifier as a string

        :return: the parameter identifier as a string
        """
        if python_helpers.isStringOrUnicode(self.mParameter) or self._dictGetParamNameFct is None:
            return self.mParameter
        return self._dictGetParamNameFct(self.mParameter)

    def getIsConnectable(self):
        """
        getIsConnectable()
        Returns True if the input is connectable

        :return: (bool)
        """
        return self.mIsConnectable

class BaseNodeDef(NodeLibObject):
    """
    This class contains the base definition of a node, with an identifier, inputs and outputs.
    Base class of :class:`.NodeDef` and :class:`.FunctionNodeDef`

    Members:
        * mIdentifier (string): identifier of the node
        * mInputs     (list of :class:`.CompNodeInput`): the input entries of the node.
        * mOutputs    (list of :class:`.CompNodeOutput`): the outputs of the node.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aIdentifier,
                 aOutputs = None,
                 aInputs = None,):
        super(BaseNodeDef, self).__init__()
        self.mIdentifier = aIdentifier
        self.mOutputs    = aOutputs if aOutputs is not None else []         # List of NodeOutput
        self.mInputs     = aInputs if aInputs is not None else []           # List of NodeInput

    def getIdentifier(self):
        """
        getIdentifier()

        :return: The identifier of the node definition as a string
        """
        return self.mIdentifier

    @handle_exceptions()
    def getAllInputs(self):
        """
        getAllInputs()
        Get all the inputs of this node definition

        :return: a list of :class:`.NodeInput` if found
        """
        return self.mInputs if self.mInputs else []

    @handle_exceptions()
    def getAllInputIdentifiers(self):
        """
        getAllInputIdentifiers()
        Get all the input identifiers as strings of this node definition

        :return: a list of string
        """
        return [aInput.getIdentifierStr() for aInput in self.getAllInputs()]

    @handle_exceptions()
    def getInput(self, aInput):
        """
        getInput(aInput)
        Get the input with the given identifier

        :param aInput: The required input
        :type aInput: :class:`.InputEnum` or str
        :return: a :class:`.NodeInput` if found, None otherwise
        """
        if not python_helpers.isStringOrUnicode(aInput) and self._dictGetInputNameFct is not None:
            aInput = self._dictGetInputNameFct(aInput)
        return next((i for i in self.getAllInputs() if i.getIdentifierStr() == aInput), None)

    @handle_exceptions()
    def getAllOutputs(self):
        """
        getAllOutputs()
        Get all the outputs of this node definition

        :return: a list of :class:`.NodeOutput` if found
        """
        return self.mOutputs if self.mOutputs else []

    @handle_exceptions()
    def getAllOutputIdentifiers(self):
        """
        getAllOutputIdentifiers()
        Get all the output identifiers as strings of this node definition

        :return: a list of string
        """
        return [aOutput.getIdentifierStr() for aOutput in self.getAllOutputs()]

    @handle_exceptions()
    def getOutput(self, aOutput):
        """
        getOutput(aOutput)
        Get the output with the given identifier

        :param aOutput: The required output
        :type aOutput: :class:`.OutputEnum` or str
        :return: a :class:`.NodeOutput` if found, None otherwise
        """
        if not python_helpers.isStringOrUnicode(aOutput) and self._dictGetOutputNameFct is not None:
            aOutput = self._dictGetOutputNameFct(aOutput)
        return next((o for o in self.getAllOutputs() if o.getIdentifierStr() == aOutput), None)

    @handle_exceptions()
    def getFirstInputOfType(self, aType):
        """
        getFirstInputOfType(aType)
        Get the first NodeInput with the given type. This considers the variant types as compatible types.

        :param aType: The required type
        :type aType: sbsenum.ParamTypeEnum
        :return: a :class:`.NodeInput` object if found, None otherwise
        """
        intType = int(aType)
        if self.mInputs:
            return next((i for i in self.mInputs if i.mType & intType), None)
        return None

    @handle_exceptions()
    def getFirstOutputOfType(self, aType):
        """
        getFirstOutputOfType(aType)
        Get the first NodeOutput with the given type. This considers the variant types as compatible types.

        :param aType: The required type
        :type aType: sbsenum.ParamTypeEnum
        :return: a :class:`.NodeOutput` object if found, None otherwise
        """
        intType = int(aType)
        if self.mOutputs:
            return next((o for o in self.mOutputs if o.mType & intType), None)
        return None

    @handle_exceptions()
    def setInputs(self, aInputs):
        self.mInputs = aInputs if aInputs is not None else []

    @handle_exceptions()
    def setOutputs(self, aOutputs):
        self.mOutputs = aOutputs if aOutputs is not None else []


@doc_inherit
class NodeDef(BaseNodeDef):
    """
    This class contains the definition of a node with parameters.
    Base class for :class:`.CompNodeDef` and :class:`.FxMapNodeDef`

    Members:
        * mIdentifier (:class:`.FilterEnum` or :class:`.FxMapNodeEnum` or string): identifier of the node
        * mInputs     (list of :class:`.NodeInput`): the input entries of the node.
        * mOutputs    (list of :class:`.NodeOutput`): the outputs of the node.
        * mParameters (list of :class:`.NodeParam`): the parameters available on this node.
        * mInheritance(list of :class:`.ParamInheritanceEnum`): the available inheritance property on this node
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aIdentifier,
                 aOutputs = None,
                 aInputs = None,
                 aParameters = None,
                 aInheritance = None):
        super(NodeDef, self).__init__(aIdentifier, aOutputs, aInputs)
        self.mParameters = aParameters if aParameters is not None else []   # List of NodeParam
        if aInheritance is not None:
            self.mInheritance = aInheritance                                # List of sbsenum.ParamInheritanceEnum
        else:
            self.mInheritance = [sbsenum.ParamInheritanceEnum.INPUT,
                                 sbsenum.ParamInheritanceEnum.PARENT,
                                 sbsenum.ParamInheritanceEnum.ABSOLUTE]

    @handle_exceptions()
    def getAllParameters(self):
        """
        getAllParameters()
        Get all the parameters of this node definition

        :return: a list of :class:`.NodeParam`
        """
        return self.mParameters if self.mParameters else []

    @handle_exceptions()
    def getAllParameterIdentifiers(self):
        """
        getAllParameterIdentifiers()
        Get all the parameter identifiers as strings of this node definition

        :return: a list of string
        """
        return [aParam.getIdentifierStr() for aParam in self.getAllParameters()]

    @handle_exceptions()
    def getParameter(self, aParameter):
        """
        getParameter(aParameter)
        Get the required parameter

        :param aParameter: The parameter
        :type aParameter: :class:`.NodeParamEnum` or str
        :return: a :class:`.NodeParam` object if found, None otherwise
        """
        if not python_helpers.isStringOrUnicode(aParameter) and self._dictGetParamNameFct is not None:
            aParameter = self._dictGetParamNameFct(aParameter)
        return next((param for param in self.getAllParameters() if param.getIdentifierStr() == aParameter), None)

    @handle_exceptions()
    def isVariant(self):
        """
        isVariant()
        Check if at least one NodeOutput has a variant type.

        :return: True if there is at least one variant output and no COLOR_MODE parameter, False otherwise
        """
        if self.mOutputs:
            if next((o for o in self.mOutputs if o.mType == sbsenum.ParamTypeEnum.ENTRY_VARIANT), None) is not None:
                return self.getParameter(sbsenum.CompNodeParamEnum.COLOR_MODE) is None
        return False



@doc_inherit
class CompNodeInput(NodeInput):
    """
    This class contains the definition of an input of a Compositing node.

    Members:
        * mIdentifier   (:class:`.InputEnum` or str): identifier of the input.
        * mType         (:class:`.ParamTypeEnum`): type of the input.
        * mIsPrimary    (bool): defines if the input is the primary input of the node
    """
    def __init__(self, aIdentifier, aType=sbsenum.ParamTypeEnum.ENTRY_VARIANT, aIsPrimary=True, aIsMultiInput=False):
        super(CompNodeInput, self).__init__(aIdentifier, aType)
        self.mIsPrimary = aIsPrimary
        self.mIsMultiInput = aIsMultiInput
        self._dictGetInputNameFct = sbsdictionaries.getCompNodeInput
        self._dictGetInputEnumFct = sbsdictionaries.getCompNodeInputEnum

    @handle_exceptions()
    def isVariant(self):
        """
        isVariant()
        Check if input has a variant type.

        :return: True if this input is variant, False otherwise.
        """
        return (self.mType & sbsenum.ParamTypeEnum.ENTRY_VARIANT) == sbsenum.ParamTypeEnum.ENTRY_VARIANT


@doc_inherit
class CompNodeOutput(NodeOutput):
    """
    This class contains the definition of an output of a Compositing node.

    Members:
        * mIdentifier   (:class:`.OutputEnum` or str): identifier of the output.
        * mType         (:class:`.ParamTypeEnum`): type of the output.
    """
    def __init__(self, aIdentifier, aType=sbsenum.ParamTypeEnum.ENTRY_VARIANT):
        super(CompNodeOutput, self).__init__(aIdentifier, aType)
        self._dictGetOutputNameFct = sbsdictionaries.getCompNodeOutput
        self._dictGetOutputEnumFct = sbsdictionaries.getCompNodeOutputEnum

@doc_inherit
class CompNodeParam(NodeParam):
    """
    This class contains the definition of a parameter of a Compositing node.

    Members:
        * mParameter     (:class:`.CompNodeParamEnum`): identifier of the parameter.
        * mType          (:class:`.ParamTypeEnum`): type of the parameter.
        * mDefaultValue  (depends on the type): default value of the parameter.
        * mIsConnectable boolean. decides whether the param is connectable in a graph
    """
    def __init__(self,
                 aParameter,
                 aType = sbsenum.ParamTypeEnum.FLOAT1,
                 aDefaultValue = '',
                 aIsConnectable = False):
        super(CompNodeParam, self).__init__(aParameter, aType, aDefaultValue, aIsConnectable)
        self._dictGetParamNameFct = sbsdictionaries.getCompNodeParam
        self._dictGetParamEnumFct = sbsdictionaries.getCompNodeParamEnum

# Base parameters of all compositing nodes
BaseParameters = [
    CompNodeParam(sbsenum.CompNodeParamEnum.OUTPUT_SIZE,   sbsenum.ParamTypeEnum.INTEGER2, '0 0'                                 ),
    CompNodeParam(sbsenum.CompNodeParamEnum.OUTPUT_FORMAT, sbsenum.ParamTypeEnum.INTEGER1, sbsenum.OutputFormatEnum.FORMAT_8BITS ),
    CompNodeParam(sbsenum.CompNodeParamEnum.PIXEL_SIZE,    sbsenum.ParamTypeEnum.FLOAT2  , '1.0 1.0'                             ),
    CompNodeParam(sbsenum.CompNodeParamEnum.PIXEL_RATIO,   sbsenum.ParamTypeEnum.INTEGER1, sbsenum.PixelRatioEnum.SQUARE         ),
    CompNodeParam(sbsenum.CompNodeParamEnum.TILING_MODE,   sbsenum.ParamTypeEnum.INTEGER1, sbsenum.TilingEnum.H_AND_V_TILING     ),
    CompNodeParam(sbsenum.CompNodeParamEnum.QUALITY,       sbsenum.ParamTypeEnum.INTEGER1, sbsenum.QualityEnum.MEDIUM            ),
    CompNodeParam(sbsenum.CompNodeParamEnum.RANDOM_SEED,   sbsenum.ParamTypeEnum.INTEGER1, '0'                                   )
]

@doc_inherit
class CompNodeDef(NodeDef):
    """
    This class contains the definition of a Compositing node.

    Members:
        * mIdentifier (:class:`.FilterEnum`): identifier of the compositing node
        * mInputs     (list of :class:`.CompNodeInput`): the input entries of the node.
        * mOutputs    (list of :class:`.CompNodeOutput`): the outputs of the node.
        * mParameters (list of :class:`.CompNodeParam`): the parameters available on this node.
        * mInheritance(list of :class:`.ParamInheritanceEnum`): the available inheritance property on this compositing node
    """
    def __init__(self, aIdentifier,
                 aOutputs = None,
                 aInputs = None,
                 aParameters = None,
                 aInheritance = None):
        super(CompNodeDef, self).__init__(aIdentifier, aOutputs, aInputs, aParameters, aInheritance)
        self.addBaseParameters()
        self._dictGetInputEnumFct = sbsdictionaries.getCompNodeInputEnum
        self._dictGetInputNameFct = sbsdictionaries.getCompNodeInput
        self._dictGetOutputEnumFct = sbsdictionaries.getCompNodeOutputEnum
        self._dictGetOutputNameFct = sbsdictionaries.getCompNodeOutput
        self._dictGetParamEnumFct = sbsdictionaries.getCompNodeParamEnum
        self._dictGetParamNameFct = sbsdictionaries.getCompNodeParam

    def addBaseParameters(self):
        """
        addBaseParameters()
        Add all the base parameters to the CompNode definition
        """
        self.mParameters.extend(BaseParameters)

    @staticmethod
    def isBaseParameter(aParam):
        """
        isBaseParameter(aParam)
        Check if the given parameter is one of the base parameter or not (Output size, Pixel format, ...)

        :param aParam: The parameter to check
        :type aParam: :class:`.CompNodeParamEnum` or :class:`.NodeParam`
        :return: True if there is at least one variant output and no COLOR_MODE parameter, False otherwise
        """
        if isinstance(aParam, NodeParam):
            aParam = aParam.mParameter

        return next((aBaseParam for aBaseParam in BaseParameters if aBaseParam.mParameter == aParam), None) is not None

    def getFirstInputOfType(self, aType):
        """
        getFirstInputOfType(aType)
        Gets the first imput of a specific type, checks both inputs and connectable parameters

        :param aType: The type to look for
        :type aType: :class:`.ParamTypeEnum`
        :return: :class:`.NodeInput` or :class:`.CompNodeParam` object if found, None otherwise
        """

        # check ordinary inputs
        inputMatch = NodeDef.getFirstInputOfType(self, aType)

        # Check parameters if not found
        if inputMatch is None:
            intType = int(aType)
            if self.mInputs:
                return next((i for i in self.mParameters if ((i.mType & intType) and i.getIsConnectable())), None)
            return None
        return inputMatch

@doc_inherit
class FxMapNodeDef(NodeDef):
    """
    This class contains the definition of a FxMap node.

    Members:
        * mIdentifier (:class:`.FxMapNodeEnum`): identifier of the compositing node
        * mInputs     (list of :class:`.CompNodeInput`): the input entries of the node.
        * mOutputs    (list of :class:`.CompNodeOutput`): the outputs of the node.
        * mParameters (list of :class:`.CompNodeParam`): the parameters available on this node.
        * mInheritance(list of :class:`.ParamInheritanceEnum`): the available inheritance property on this compositing node
    """
    def __init__(self, aIdentifier,
                 aOutputs = None,
                 aInputs = None,
                 aParameters = None,
                 aInheritance = None):
        super(FxMapNodeDef, self).__init__(aIdentifier, aOutputs, aInputs, aParameters, aInheritance)
        self._dictGetInputEnumFct = sbsdictionaries.getCompNodeInputEnum
        self._dictGetInputNameFct = sbsdictionaries.getCompNodeInput
        self._dictGetOutputEnumFct = sbsdictionaries.getCompNodeOutputEnum
        self._dictGetOutputNameFct = sbsdictionaries.getCompNodeOutput
        self._dictGetParamEnumFct = sbsdictionaries.getCompNodeParamEnum
        self._dictGetParamNameFct = sbsdictionaries.getCompNodeParam

    @staticmethod
    def isBaseParameter(aParam):
        """
        isBaseParameter(aParam)
        Check if the given parameter is one of the base parameter or not (Output size, Pixel format, ...)

        :param aParam: The parameter to check
        :type aParam: :class:`.NodeParam`
        :return: False, there is no base parameters on the FxMap nodes
        """
        return False


@doc_inherit
class FunctionInput(NodeInput):
    """
    This class contains the definition of an input of a Function node.

    Members:
        * mIdentifier   (:class:`.FunctionInputEnum` or str): identifier of the input.
        * mType         (:class:`.ParamTypeEnum`): type of the output.
    """
    def __init__(self, aIdentifier, aType = sbsenum.ParamTypeEnum.ENTRY_VARIANT):
        super(FunctionInput, self).__init__(aIdentifier, aType)
        self._dictGetInputNameFct = sbsdictionaries.getFunctionInput
        self._dictGetInputEnumFct = sbsdictionaries.getFunctionInputEnum

@doc_inherit
class FunctionOutput(NodeOutput):
    """
    This class contains the definition of an output of a Function node.

    Members:
        * mIdentifier   (:class:`.OutputEnum` or str): identifier of the output.
        * mType         (:class:`.ParamTypeEnum`): type of the output.
    """
    def __init__(self, aIdentifier, aType=sbsenum.ParamTypeEnum.ENTRY_VARIANT):
        super(FunctionOutput, self).__init__(aIdentifier, aType)
        self._dictGetOutputNameFct = sbsdictionaries.getFunctionOutput
        self._dictGetOutputEnumFct = sbsdictionaries.getFunctionOutputEnum


@doc_inherit
class FunctionParam(NodeParam):
    """
    This class contains the definition of a parameter of a Function node.

    Members:
        * mParameter    (:class:`.FunctionEnum`): identifier of the parameter.
        * mType         (:class:`.ParamTypeEnum`): type of the parameter.
        * mDefaultValue (depends on the type): default value of the parameter.
    """
    def __init__(self, aParameter, aType = sbsenum.ParamTypeEnum.FLOAT1, aDefaultValue = ''):
        super(FunctionParam, self).__init__(aParameter, aType, aDefaultValue)

    @handle_exceptions()
    def getIdentifier(self):
        """
        getIdentifier()
        Get the parameter identifier as an enum value if possible, or as a string if it is a custom parameter

        :return: the parameter identifier as an integer if possible, or as a string otherwise
        """
        from . import sbslibrary
        res = None
        if python_helpers.isStringOrUnicode(self.mParameter):
            res = sbslibrary.getFunctionEnum(self.mParameter)
        return res if res is not None else self.mParameter

    @handle_exceptions()
    def getIdentifierStr(self):
        """
        getIdentifierStr()
        Get the parameter identifier as a string

        :return: the parameter identifier as a string
        """
        from . import sbslibrary
        if python_helpers.isStringOrUnicode(self.mParameter):
            return self.mParameter

        fct = sbslibrary.getFunctionDefinition(self.mParameter)
        if fct is not None:
            return fct.getIdentifier()
        return self.mParameter

@doc_inherit
class FunctionDef(BaseNodeDef):
    """
    This class contains the definition of a Function node.

    Members:
        * mIdentifier    (:class:`.FunctionEnum`): identifier of the function node
        * mInputs        (list of :class:`.FunctionInput`): the inputs of the node.
        * mOutputs       (list of :class:`.FunctionOutput`): the outputs of the node.
        * mFunctionDatas (list of :class:`.FunctionParam`): the parameters available on this node.
        * mTemplate1     (:class:`.ParamTypeEnum`): for a function with a variant type, provide the allowed types.
    """
    def __init__(self, aIdentifier,
                 aOutputs = None,
                 aInputs = None,
                 aFunctionDatas = None,
                 aTemplate1 = None):
        super(FunctionDef, self).__init__(aIdentifier, aOutputs, aInputs)
        self.mFunctionDatas = aFunctionDatas if aFunctionDatas is not None else []    # List of FunctionParam
        self.mTemplate1     = aTemplate1                                              # sbsenum.ParamTypeEnum

        self._dictGetInputEnumFct = sbsdictionaries.getFunctionInputEnum
        self._dictGetInputNameFct = sbsdictionaries.getFunctionInput
        self._dictGetOutputEnumFct = sbsdictionaries.getFunctionOutputEnum
        self._dictGetOutputNameFct = sbsdictionaries.getFunctionOutput
        self._dictGetParamEnumFct = None
        self._dictGetParamNameFct = None

    @handle_exceptions()
    def getAllParameters(self):
        """
        getAllParameters()
        Get all the parameters of this node definition

        :return: a list of :class:`.NodeParam`
        """
        return self.mFunctionDatas if self.mFunctionDatas else []

    @handle_exceptions()
    def getAllParameterIdentifiers(self):
        """
        getAllParameterIdentifiers()
        Get all the parameter identifiers as strings of this node definition

        :return: a list of string
        """
        return [aParam.getIdentifierStr() for aParam in self.getAllParameters()]

    @handle_exceptions()
    def getParameter(self, aParameter):
        """
        getParameter(aParameter)
        Get the required parameter

        :param aParameter: The parameter
        :type aParameter: :class:`.FunctionEnum` or str
        :return: a :class:`.FunctionParam` object if found, None otherwise
        """
        from . import sbslibrary
        if not self.mFunctionDatas:
            return None

        if python_helpers.isStringOrUnicode(aParameter):
            aParameter = sbslibrary.getFunctionEnum(aParameter)
        else: # Check validity and eventually raise error
            sbslibrary.getFunctionDefinition(aParameter)

        return next((param for param in self.mFunctionDatas if param.mParameter == aParameter), None)

    @handle_exceptions()
    def getInputType(self, aInput, aResolved = False):
        """
        getInputType(aInput, aResolved = False)
        Get the input type of the input with the given identifier

        :param aInput: The required input
        :param aResolved: In the case of a Template type, True to return the value of the template, False to get TEMPLATE1
        :type aInput: :class:`.FunctionInputEnum` or str
        :type aResolved: bool
        :return: a :class:`.ParamTypeEnum` if found, None otherwise
        """
        aIn = self.getInput(aInput)
        if aIn is not None:
            if aResolved and aIn.mType == sbsenum.ParamTypeEnum.TEMPLATE1:
                return self.mTemplate1
            else:
                return aIn.mType
        return None


class GradientKey(LibObject):
    """
    Class that provides a description of a gradient key for the Gradient Map filter.

    Members:
        * mPosition (float): the position of the key between 0 and 1
        * mValue    (list of 4 floats): the color value of the key.
        * mMidpoint (float, optional): default is -1
    """
    def __init__(self, aPosition, aValue, aMidpoint = None):
        super(GradientKey, self).__init__()
        self.mPosition = aPosition
        self.mValue = aValue
        self.mMidpoint = aMidpoint if aMidpoint is not None else -1


class CurveKey(LibObject):
    """
    Class that provides a description of a curve key for the Curve filter.

    Members:
        * mPosition       (list of two float) : position of the key in two dimensions between 0 and 1
        * mLeft           (list of two float) : position of the left handle of the key
        * mRight          (list of two float) : position of the right handle of the key
        * mIsLeftBroken   (boolean) : True to set the left handle squared instead of rounded. Default to False
        * mIsRightBroken  (boolean) : True to set the right handle squared instead of rounded. Default to False
        * mIsLocked       (boolean) : True to lock the key handle. Default to True
    """
    def __init__(self, aPosition, aLeft, aRight,
                        aIsLeftBroken = False, aIsRightBroken = False, aIsLocked = True):
        super(CurveKey, self).__init__()
        self.mPosition       = aPosition
        self.mLeft           = aLeft
        self.mRight          = aRight
        self.mIsLeftBroken   = aIsLeftBroken
        self.mIsRightBroken  = aIsRightBroken
        self.mIsLocked       = aIsLocked


class CurveDefinition(LibObject):
    """
    Class that provides a description of a curve for the Curve filter.

    Members:
        * mIdentifier     (:class:`.CurveTypeEnum`): the identifier of the curve
        * mCurveKeys      (list of :class:`.CurveKey`) : the list of keys
    """
    def __init__(self, aIdentifier, aCurveKeys):
        super(CurveDefinition, self).__init__()
        self.mIdentifier = aIdentifier
        self.mCurveKeys  = aCurveKeys

    @handle_exceptions()
    def addCurveKey(self, aCurveKey):
        """
        addCurveKey(aCurveKey)
        Add the given curve key to the curve definition

        :param aCurveKey: The key to add
        :type aCurveKey: :class:`.CurveKey`
        """
        api_helpers.addObjectToList(aObject=self, aMemberListName='mCurveKeys', aObjectToAdd=aCurveKey)

    @staticmethod
    @handle_exceptions()
    def initCurve(aIdentifier):
        """
        initCurve(aIdentifier)
        Create the initial curve with the bottom left and top right keys.

        :param aIdentifier: Identifier of the curve
        :type aIdentifier: :class:`.CurveTypeEnum`
        :return: the :class:`.CurveDefinition` object initialized with the default keys
        """
        bottomLeftKey = CurveKey(aPosition     = [0,0],
                                 aLeft         = [0,0],
                                 aRight        = [0.1,0],
                                 aIsLeftBroken = True,
                                 aIsRightBroken= True,
                                 aIsLocked     = False)
        topRightKey = CurveKey(aPosition     = [1,1],
                               aLeft         = [0.9,1],
                               aRight        = [1,1],
                               aIsLeftBroken = True,
                               aIsRightBroken= True,
                               aIsLocked     = False)
        aCurve = CurveDefinition(aIdentifier=aIdentifier, aCurveKeys=[bottomLeftKey, topRightKey])
        return aCurve

    @handle_exceptions()
    def moveKeyTo(self, aCurveKey, aPosition):
        """
        moveKeyTo(aCurveKey, aPosition)
        Move the given key to the given position.
        The resulting position is clamped to the allowed space for this key, considering the previous and next key.

        :param aCurveKey: The key to move
        :param aPosition: The target position
        :type aCurveKey: :class:`.CurveKey`
        :type aPosition: list of two float between 0 and 1
        :return: The resulting position for this key
        """
        if not aCurveKey in self.mCurveKeys:
            raise SBSImpossibleActionError('The provided key does not belong to this curve')
        aKeyIndex = self.mCurveKeys.index(aCurveKey)

        # Clamp position to the allowed space
        prevPos = 0
        nextPos = 1
        keyPos = aCurveKey.mPosition[0]
        for i, key in enumerate(self.mCurveKeys):
            if i == aKeyIndex:
                continue
            if key.mPosition[0] < keyPos:
                if keyPos-key.mPosition[0] < keyPos-prevPos:
                    prevPos = key.mPosition[0]
            else:
                if key.mPosition[0]-keyPos < nextPos-keyPos:
                    nextPos = key.mPosition[0]
        aPosition[0] = max(prevPos, min(nextPos, aPosition[0]))

        # Move key
        aOffset = [x-y for x,y in zip(aPosition, aCurveKey.mPosition)]
        aCurveKey.mPosition = aPosition
        aCurveKey.mLeft = [x+y for x,y in zip(aCurveKey.mLeft, aOffset)]
        aCurveKey.mRight = [x+y for x,y in zip(aCurveKey.mRight, aOffset)]
        return aPosition


class WidgetOption(LibObject):
    """
    This class provide the definition of an option of a GUI widget associated to an Input Parameter of a Graph.

    Members
        * mOption (:class:`.WidgetOptionEnum`): identifier of the option
        * mType   (:class:`.ParamTypeEnum`): type of the option
        * mValue  (str): value of the option
    """
    def __init__(self, aOption, aType, aValue):
        super(WidgetOption, self).__init__()
        self.mOption  = aOption
        self.mType    = aType
        self.mValue   = aValue


class InputParamWidget(LibObject):
    """
    Class providing the definition of the GUI widget associated to an Input Parameter of a Graph.

    Members:
        * mWidget  (:class:`.WidgetEnum`): identifier of the widget
        * mType    (:class:`.ParamTypeEnum`): type of the value driven by this widget
        * mOptions (list of :class:`.WidgetOption`): options of this widget (min and max values, step, clamp, ...)
    """
    def __init__(self, aWidget, aType, aOptions = None):
        super(InputParamWidget, self).__init__()
        self.mWidget  = aWidget
        self.mType    = aType
        self.mOptions = aOptions if aOptions is not None else []

    def getDefaultValue(self):
        """
        getDefaultValue()
        Get the default value of this widget.

        :return: the default value as a string if it is defined on this widget, None otherwise
        """
        if self.mWidget == sbsenum.WidgetTypeEnum.DROP_DOWN_LIST:
            parametersOpt = self.getOption(sbsenum.WidgetOptionEnum.PARAMETERS)
            if parametersOpt is not None:
                params = parametersOpt.mValue
                return params.split(";")[0]
        else:
           defaultOpt = self.getOption(sbsenum.WidgetOptionEnum.DEFAULT)
           if defaultOpt is not None:
               return defaultOpt.mValue

        return None

    @handle_exceptions()
    def getOptions(self):
        """
        getOptions()
        Get all the options of this widget.

        :return: the options of this widget as a list of :class:`.WidgetOption`
        """
        return self.mOptions if self.mOptions else []

    @handle_exceptions()
    def getOption(self, aOption):
        """
        getOption(aOption)
        Get the given option.

        :param aOption: The option to get
        :type aOption: :class:`.WidgetOptionEnum`
        :return: the option as a :class:`.WidgetOption` if it is defined on this widget, None otherwise
        """
        return next((opt for opt in self.getOptions() if opt.mOption == aOption), None)

    @handle_exceptions()
    def hasOption(self, aOption):
        """
        hasOption(aOption)
        Check if the given option is defined on this widget

        :param aOption: The option to get
        :type aOption: :class:`.WidgetOptionEnum`
        :return: True if the option is defined on this widget, False otherwise
        """
        return self.getOption(aOption) is not None
