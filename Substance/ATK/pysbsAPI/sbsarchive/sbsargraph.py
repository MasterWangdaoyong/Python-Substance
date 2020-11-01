# coding: utf-8
"""
Module **sbsargraph** aims to define SBSARObjects that are relative to a graph as saved in a .sbsar file,
mostly :class:`.SBSARGraph`, :class:`.SBSARInput`, :class:`.SBSAROutput`, :class:`.SBSARPreset` and :class:`.SBSARPresetInput`.
"""

from __future__ import unicode_literals
from pysbs import sbsenum
from pysbs import api_helpers
from pysbs.api_decorators import doc_inherit,handle_exceptions,deprecated
from pysbs.common_interfaces import SBSARObject, Graph, ParamInput, GraphOutput, Preset, PresetInput
from .sbsarenum import SBSARTypeEnum, convertSbsarType2SbsType
from .sbsargui import SBSARInputGui, SBSAROutputGui, SBSARGuiGroup


# =======================================================================
@doc_inherit
class SBSARInput(SBSARObject, ParamInput):
    """
    Class that contains information on a graph input as defined in a .sbsar file

    Members:
        * mIdentifier   (str): identifier of the input.
        * mUID          (str): uid of the input.
        * mType         (:class:`.SBSARTypeEnum`): data type, among the enumeration :class:`.SBSARTypeEnum`
        * mAlterOutputs (List[str]): collection of graph outputs UID which are impacted anytime this input value is modified.
        * mAlterNodes   (str): ???.
        * mDefault      (str, optional): Default value.
        * mUserTag      (str, optional): user textual tags
        * mInputGui     (:class:`.SBSARInputGui`, optional): GUI widget of the input
    """
    def __init__(self,
                 aUID           = '',
                 aIdentifier    = '',
                 aType          = 0,
                 aAlterOutputs  = '',
                 aAlterNodes    = '',
                 aDefault       = None,
                 aUserTag       = None,
                 aInputGui      = None):
        SBSARObject.__init__(self)
        ParamInput.__init__(self, aUID, aIdentifier)
        self.mDefault      = aDefault
        self.mType         = aType
        self.mAlterOutputs = aAlterOutputs
        self.mAlterNodes   = aAlterNodes
        self.mUserTag      = aUserTag
        self.mInputGui     = aInputGui

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID          = aSBSParser.getXmlElementAttribValue(aXmlNode,            'uid'          )
        self.mIdentifier   = aSBSParser.getXmlElementAttribValue(aXmlNode,            'identifier'   )
        self.mDefault      = aSBSParser.getXmlElementAttribValue(aXmlNode,            'default'      )
        self.mType         = int(aSBSParser.getXmlElementAttribValue(aXmlNode,        'type'         ))
        self.mAlterOutputs = aSBSParser.getXmlElementAttribValue(aXmlNode,            'alteroutputs' ).split(',')
        self.mAlterNodes   = aSBSParser.getXmlElementAttribValue(aXmlNode,            'alternodes'   )
        self.mUserTag      = aSBSParser.getXmlElementAttribValue(aXmlNode,            'usertag'      )
        self.mInputGui     = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'inputgui'     , SBSARInputGui)

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        if aAttributeIdentifier == sbsenum.AttributesEnum.UserTags:
            return self.mUserTag
        return self.mInputGui.getAttribute(aAttributeIdentifier) if self.mInputGui is not None else None

    @handle_exceptions()
    def getInputGui(self):
        """
        getInputGui()
        Get the input GUI associated to this input

        :return: a :class:`.SBSARInputGui` object if defined, None otherwise
        """
        return self.mInputGui

    @handle_exceptions()
    def getGroup(self):
        """
        getGroup()
        Get the input GUI group containing this input

        :return: the GUI group as a string if defined, None otherwise
        """
        return self.getInputGui().getGroup() if self.getInputGui() is not None else None

    @handle_exceptions()
    def getClamp(self):
        """
        getClamp()

        :return: the clamp as a boolean if defined for this parameter, None if not defined
        """
        return self.getInputGui().getClamp() if self.isAnInputParameter() else None

    @handle_exceptions()
    def getMinValue(self, asList = False):
        """
        getMinValue(asList = False)

        :param asList: True to get the result as a list of minimum values accordingly to the number of values of this parameter, False to have only one value returned. Default to False
        :type asList: bool, optional
        :return: the minimum parameter value in the type of the parameter (int or float), as a list or not, None if not defined
        """
        if self.isAnInputParameter():
            aValues = self.getInputGui().getMinValue()
            if aValues is not None:
                aValues = aValues.split(',')
                if asList:
                    return [self.formatValueToType(aValue) for aValue in aValues]
                else:
                    return self.formatValueToType(aValues[0])
        return None

    @handle_exceptions()
    def getMaxValue(self, asList = False):
        """
        getMaxValue(asList= False)

        :param asList: True to get the result as a list of maximum values accordingly to the number of values of this parameter, False to have only one value returned. Default to False
        :type asList: bool, optional
        :return: the maximum parameter value in the type of the parameter (int or float), as a list or not, None if not defined
        """
        if self.isAnInputParameter():
            aValues = self.getInputGui().getMaxValue()
            if aValues is not None:
                aValues = aValues.split(',')
                if asList:
                    return [self.formatValueToType(aValue) for aValue in aValues]
                else:
                    return self.formatValueToType(aValues[0])
        return None

    @handle_exceptions()
    def getDefaultValue(self):
        """
        getDefaultValue()

        :return: the default value as a value or a list of values in the type of the parameter (bool, int or float), None if not defined
        """
        if self.mDefault is not None:
            aDefaultValue = self.mDefault.split(',')
            if aDefaultValue:
                res = [self.formatValueToType(aValue) for aValue in aDefaultValue]
                return res if len(res) > 1 else res[0]
        return None

    @handle_exceptions()
    def getDropDownList(self):
        """
        getDropDownList()

        :return: the map{value(int):label(str)} corresponding to the drop down definition if defined for this parameter, None otherwise.
        """
        return self.getInputGui().getDropDownList() if self.isAnInputParameter() else None

    @handle_exceptions()
    def getLabels(self):
        """
        getLabels()

        :return: the list of all labels defined for this parameter, in the right order, as a list of strings. None if not defined
        """
        return self.getInputGui().getLabels() if self.isAnInputParameter() else None

    @handle_exceptions()
    def getStep(self):
        """
        getStep()

        :return: the step value (in the type of the parameter) of the widget for this parameter, None if not defined
        """
        return self.formatValueToType(self.getInputGui().getStep()) if self.isAnInputParameter() else None

    @handle_exceptions()
    def getUsages(self):
        """
        getUsages()
        Get the usages of this param input

        :return: the list of :class:`.SBSARUsage` defined on this image input
        """
        return self.getInputGui().getUsages() if self.isAnInputImage() else None

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this image input

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this param input, False otherwise
        """
        return self.getInputGui().hasUsage(aUsage) if self.isAnInputImage() else None

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Get the type of the input among the list defined in :class:`.ParamTypeEnum`.
        Please be careful, it does not match the enumeration of type in a .sbsar format.
        To get the type as a :class:`.SBSARTypeEnum`, just access the mType member

        :return: The type of the parameter as a :class:`.ParamTypeEnum`
        """
        if self.isAnInputImage():
            aWidgetImage = self.getInputGui().getWidget()
            if aWidgetImage.mColorType == 'grayscale':
                return sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE
            else:
                return sbsenum.ParamTypeEnum.ENTRY_COLOR
        else:
            return convertSbsarType2SbsType(self.mType)

    @handle_exceptions()
    def getWidget(self):
        """
        getWidget()
        Get the widget associated to this input

        :return: a :class:`.SBSARObject` object if defined, None otherwise
        """
        return self.getInputGui() is not None and self.getInputGui().getWidget()

    @handle_exceptions()
    def isAnInputImage(self):
        """
        isAnInputImage()
        Check if this input is of kind image.

        :return: True if this is an input image, False otherwise
        """
        return self.getInputGui() is not None and self.getInputGui().isAnInputImage()

    @handle_exceptions()
    def isAnInputParameter(self):
        """
        isAnInputParameter()
        Check if this input is a parameter.

        :return: True if this is an input parameter, False otherwise
        """
        return self.getInputGui() is not None and self.getInputGui().isAnInputParameter()

    def getIsConnectable(self):
        """
        getIsConnectable()
        Check if this input is connectable as an input.

        :return: True if it's connectable, False otherwise
        """
        return self.mInputGui.mShowas == SBSARInputGui.sPinIdentifier

    @handle_exceptions()
    def getLabelFalse(self):
        """
        getLabelFalse()
        Returns the label for the false option if it's valid for this input

        :return: str with the label if it's a button, otherwise None
        """
        return self.mInputGui.getLabelFalse() if self.isAnInputParameter() else None

    @handle_exceptions()
    def getLabelTrue(self):
        """
        getLabelTrue()
        Returns the label for the true option if it's valid for this input

        :return: str with the label if it's a button, otherwise None
        """
        return self.mInputGui.getLabelTrue() if self.isAnInputParameter() else None


# =======================================================================
@doc_inherit
class SBSAROutput(SBSARObject, GraphOutput):
    """
    Class that contains information on a graph output as defined in a .sbsar file

    Members:
        * mUID         (str): uid of the output.
        * mIdentifier  (str): identifier of the output.
        * mType        (:class:`.SBSARTypeEnum`): data type, among the enumeration :class:`.SBSARTypeEnum`
        * mWidth       (str): width of the output.
        * mHeight      (str): height of the output.
        * mMipMaps     (str): mipmap level.
        * mDynamicSize (str): dynamic size.
        * mUserData    (str): user textual tags
        * mOutputGui   (:class:`.SBSAROutputGui`): GUI widget of the output
    """
    def __init__(self,
                 aUID         = '',
                 aIdentifier  = '',
                 aType        = '',
                 aWidth       = '',
                 aHeight      = '',
                 aMipMaps     = '',
                 aDynamicSize = None,
                 aUserData    = None,
                 aOutputGui   = None):
        SBSARObject.__init__(self)
        GraphOutput.__init__(self, aUID, aIdentifier)
        self.mType        = aType
        self.mWidth       = aWidth
        self.mHeight      = aHeight
        self.mMipMaps     = aMipMaps
        self.mDynamicSize = aDynamicSize
        self.mUserData    = aUserData
        self.mOutputGui   = aOutputGui

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID         = aSBSParser.getXmlElementAttribValue(aXmlNode,            'uid'          )
        self.mIdentifier  = aSBSParser.getXmlElementAttribValue(aXmlNode,            'identifier'   )

        valueType = aSBSParser.getXmlElementAttribValue(aXmlNode, 'type')
        if valueType is not None:
            # NOTE Engine v7+
            if int(valueType) == SBSARTypeEnum.IMAGE:
                aFormat = int(aSBSParser.getXmlElementAttribValue(aXmlNode, 'format'))
                self.mType = sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE if aFormat & 0xC else sbsenum.ParamTypeEnum.ENTRY_COLOR
            else:
                self.mType = convertSbsarType2SbsType(valueType)
        else:
            # NOTE Engine <v7
            aFormat = int(aSBSParser.getXmlElementAttribValue(aXmlNode, 'format'))
            self.mType = sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE if aFormat & 0xC else sbsenum.ParamTypeEnum.ENTRY_COLOR

        self.mWidth       = aSBSParser.getXmlElementAttribValue(aXmlNode,            'width'        )
        self.mHeight      = aSBSParser.getXmlElementAttribValue(aXmlNode,            'height'       )
        self.mMipMaps     = aSBSParser.getXmlElementAttribValue(aXmlNode,            'mipmaps'      )
        self.mDynamicSize = aSBSParser.getXmlElementAttribValue(aXmlNode,            'dynamicsize'  )
        self.mUserData    = aSBSParser.getXmlElementAttribValue(aXmlNode,            'usertag'      )
        self.mOutputGui   = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'outputgui'    , SBSAROutputGui)

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        if aAttributeIdentifier == sbsenum.AttributesEnum.UserTags:
            return self.mUserData
        return self.mOutputGui.getAttribute(aAttributeIdentifier) if self.mOutputGui is not None else None

    @handle_exceptions()
    def getUsages(self):
        """
        getUsages()
        Get the usages of this graph output

        :return: the list of :class:`.SBSARUsage` defined on this graph output
        """
        return self.mOutputGui.getUsages() if self.mOutputGui is not None else []

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this graph output

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this graph output, False otherwise
        """
        return self.mOutputGui.hasUsage(aUsage) if self.mOutputGui is not None else False

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Get the output type of this GraphOutput.

        :return: the output type in the format :class:`.ParamTypeEnum` if found, None otherwise
        """
        return self.mType

    @handle_exceptions()
    @deprecated(__name__, '2019.1.0', 'Renamed for consistency with SBSARInput.getType()', 'Please use getType instead')
    def getOutputType(self):
        """
        getOutputType()
        Get the output type of this GraphOutput.

        :return: the output type in the format :class:`.ParamTypeEnum` if found, None otherwise
        """
        return self.getType()

# =======================================================================
@doc_inherit
class SBSARPreset(SBSARObject, Preset):
    """
    Class that contains information on a graph parameter preset as defined in a .sbsar file

    Members:
        * mLabel        (str): identifier of the preset.
        * mPresetInputs (list of :class:`.SBSARPresetInput`): list of preset parameters.
    """

    def __init__(self, aLabel='', aUsertags = None, aPresetInputs=None):
        SBSARObject.__init__(self)
        Preset.__init__(self,
                        aLabel=aLabel,
                        aUsertags=aUsertags,
                        aPresetInputs=aPresetInputs if aPresetInputs is not None else [])

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mLabel = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label')
        self.mUsertags = aSBSParser.getXmlElementAttribValue(aXmlNode, 'usertags')
        self.mPresetInputs = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'presetinput', SBSARPresetInput)


#=======================================================================
@doc_inherit
class SBSARPresetInput(SBSARObject, PresetInput):
    """
    Class for manipulating embedded user-defined preset input inside a .sbs file

    Members:
        * mUID        (str): uid of the input parameter targeted by this preset input
        * mIdentifier (str): identifier of the input parameter targeted by this preset input
        * mValue      (:class:`.SBSConstantValue`): value, depend on the type.
        * mType       (:class:`.SBSParamValue`): type of the input
    """

    def __init__(self, aUID=None, aIdentifier=None, aValue=None, aType=None):
        SBSARObject.__init__(self)
        PresetInput.__init__(self, aUID=aUID,
                                    aIdentifier=aIdentifier,
                                    aValue=aValue,
                                    aType=aType)

        self.mMembersForEquality = ['mUID', 'mIdentifier', 'mValue', 'mType']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'uid')
        self.mIdentifier = aSBSParser.getXmlElementAttribValue(aXmlNode, 'identifier')
        self.mValue      = aSBSParser.getXmlElementAttribValue(aXmlNode, 'value')
        self.mType       = aSBSParser.getXmlElementAttribValue(aXmlNode, 'type')

    @handle_exceptions()
    def getValue(self):
        return self.mValue

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Get the type of the input among the list defined in :class:`.ParamTypeEnum`.
        Please be careful, it does not match the enumeration of type in a .sbsar format.
        To get the type as a :class:`.SBSARTypeEnum`, just access the mType member

        :return: The type of the parameter as a :class:`.ParamTypeEnum`
        """
        return convertSbsarType2SbsType(self.mType)

    @handle_exceptions()
    def getTypedValue(self):
        return api_helpers.getTypedValueFromStr(aValue = self.mValue, aType=self.getType(), aSep=',')


#=======================================================================
@doc_inherit
class SBSARGraph(SBSARObject, Graph):
    """
    Class that contains information on a compositing graph as defined in a .sbsar file

    Members:
        * mLabel          (str): label of the graph.
        * mPkgUrl         (str): URL of the graph relatively to the package (pkg://graphIdentifier).
        * mGuiGroups      (list of :class:`.SBSARGuiGroup`): List of parameters groups.
        * mParamInputs    (list of :class:`.SBSARInput`): list of parameters and compositing inputs of the graph.
        * mGraphOutputs   (list of :class:`.SBSAROutput`): list of compositing outputs of the graph.
        * mPresets        (list of :class:`.SBSARPreset`): list of presets.
        * mAuthor         (str, optional): Author.
        * mAuthorUrl      (str, optional): Author URL.
        * mCategory       (str, optional): Category.
        * mDescription    (str, optional): Textual graph description.
        * mHideInLibrary  (str, optional): Define if the graph is hidden in the library or not. Default to 'off'
        * mKeywords       (str, optional): List of tags separated by a space.
        * mPhysicalSize   (str, optional): Physical Size attribute
        * mPrimaryInput   (str, optional): The identifier of the primary (image) input.
        * mUserData       (str, optional): Textual user data.
    """
    __sAttributeMap = {
        sbsenum.AttributesEnum.Author:          'mAuthor',
        sbsenum.AttributesEnum.AuthorURL:       'mAuthorUrl',
        sbsenum.AttributesEnum.Category:        'mCategory',
        sbsenum.AttributesEnum.Description:     'mDescription',
        sbsenum.AttributesEnum.HideInLibrary:   'mHideInLibrary',
        sbsenum.AttributesEnum.Label:           'mLabel',
        sbsenum.AttributesEnum.PhysicalSize:    'mPhysicalSize',
        sbsenum.AttributesEnum.Tags:            'mKeywords',
        sbsenum.AttributesEnum.UserTags:        'mUserData'
    }

    def __init__(self,
                 aLabel         = '',
                 aPkgUrl        = '',
                 aGuiGroups     = None,
                 aParamInputs   = None,
                 aGraphOutputs  = None,
                 aPresets       = None,
                 aAuthor        = None,
                 aAuthorUrl     = None,
                 aCategory      = None,
                 aDescription   = None,
                 aHideInLibrary = None,
                 aKeywords      = None,
                 aPhysicalSize  = None,
                 aPrimaryInput  = None,
                 aUserData      = None):
        SBSARObject.__init__(self)
        Graph.__init__(self, aIdentifier = None,
                             aParamInputs = aParamInputs if aParamInputs is not None else [],
                             aPrimaryInput = aPrimaryInput,
                             aGraphOutputs = aGraphOutputs if aGraphOutputs is not None else [],
                             aPresets = aPresets if aPresets is not None else [])

        self.mLabel         = aLabel
        self.mPkgUrl        = aPkgUrl
        self.mGuiGroups     = aGuiGroups if aGuiGroups is not None else []
        self.mPresets       = aPresets if aPresets is not None else []
        self.mAuthor        = aAuthor
        self.mAuthorUrl     = aAuthorUrl
        self.mCategory      = aCategory
        self.mDescription   = aDescription
        self.mHideInLibrary = aHideInLibrary
        self.mKeywords      = aKeywords
        self.mPhysicalSize  = aPhysicalSize
        self.mUserData      = aUserData

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mLabel         = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label'         )
        self.mPkgUrl        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'pkgurl'        )
        self.mGuiGroups     = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'guigroups' , 'guigroup' , SBSARGuiGroup)
        self.mParamInputs   = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'inputs'    , 'input'    , SBSARInput)
        self.mGraphOutputs  = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'outputs'   , 'output'   , SBSAROutput)
        self.mPresets       = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'sbspresets', 'sbspreset', SBSARPreset)
        self.mAuthor        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'author'        )
        self.mAuthorUrl     = aSBSParser.getXmlElementAttribValue(aXmlNode, 'authorurl'     )
        self.mCategory      = aSBSParser.getXmlElementAttribValue(aXmlNode, 'category'      )
        self.mDescription   = aSBSParser.getXmlElementAttribValue(aXmlNode, 'description'   )
        self.mHideInLibrary = aSBSParser.getXmlElementAttribValue(aXmlNode, 'hideInLibrary' )
        self.mKeywords      = aSBSParser.getXmlElementAttribValue(aXmlNode, 'keywords'      )
        self.mPrimaryInput  = aSBSParser.getXmlElementAttribValue(aXmlNode, 'primaryinput'  )
        self.mUserData      = aSBSParser.getXmlElementAttribValue(aXmlNode, 'usertag'       )
        self.mPhysicalSize  = aSBSParser.getXmlElementAttribValue(aXmlNode, 'physicalSize'  )

    @handle_exceptions()
    def getAllGuiGroups(self):
        """
        getAllGuiGroups()
        Get the list of all parameter groups defined on this graph

        :return: a list of :class:`.SBSARGuiGroup`
        """
        return self.mGuiGroups if self.mGuiGroups else []

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        if SBSARGraph.__sAttributeMap.get(aAttributeIdentifier, None) is None or \
            not hasattr(self, SBSARGraph.__sAttributeMap[aAttributeIdentifier]) or \
            getattr(self, SBSARGraph.__sAttributeMap[aAttributeIdentifier]) is None:
            return None

        if aAttributeIdentifier == sbsenum.AttributesEnum.HideInLibrary:
            return api_helpers.getTypedValueFromStr(self.mHideInLibrary, sbsenum.ParamTypeEnum.BOOLEAN)
        elif aAttributeIdentifier == sbsenum.AttributesEnum.PhysicalSize:
            return api_helpers.getTypedValueFromStr(self.mPhysicalSize, sbsenum.ParamTypeEnum.FLOAT3, aSep=',')
        else:
            return getattr(self, SBSARGraph.__sAttributeMap[aAttributeIdentifier])

    @handle_exceptions()
    def getGuiGroup(self, aGroupIdentifier):
        """
        getGuiGroup(aGroupIdentifier)
        Get the SBSARGuiGroup with the given identifier

        :param aGroupIdentifier: group identifier
        :type aGroupIdentifier: str
        :return: a :class:`.SBSARGuiGroup` if found, None otherwise
        """
        return next((aGroup for aGroup in self.getAllGuiGroups() if aGroup.mIdentifier == aGroupIdentifier), None)

    @handle_exceptions()
    def getGraphOutputs(self):
        """
        getGraphOutputs()
        Get all the graph outputs

        :return: the list of :class:`.SBSAROutput` defined on this graph
        """
        return Graph.getGraphOutputs(self)

    @handle_exceptions()
    def getGraphOutput(self, aOutputIdentifier):
        """
        getGraphOutput(aOutputIdentifier)
        Get the graph output with the given identifier

        :param aOutputIdentifier: identifier of the output
        :type aOutputIdentifier: str
        :return: a :class:`.SBSAROutput` object if found, None otherwise
        """
        return Graph.getGraphOutput(self, aOutputIdentifier)

    @handle_exceptions()
    def getGraphOutputWithUsage(self, aUsage):
        """
        getGraphOutputWithUsage(aUsage)
        Get the first GraphOutput which has the given usage defined

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.SBSAROutput` if found, None otherwise
        """
        return Graph.getGraphOutputWithUsage(self, aUsage)

    @handle_exceptions()
    def getGraphOutputType(self, aOutputIdentifier):
        """
        getGraphOutputType(aOutputIdentifier)
        Get the output type of the GraphOutput with the given identifier

        :param aOutputIdentifier: identifier of the output
        :type aOutputIdentifier: str
        :return: the output type in the format :class:`.ParamTypeEnum` if found, None otherwise
        """
        # First get the UID of the OutputBridge which references the given output identifier
        aGraphOutput = self.getGraphOutput(aOutputIdentifier)
        return aGraphOutput.getType() if aGraphOutput is not None else None

    @handle_exceptions()
    def getAllInputs(self):
        """
        getAllInputs()
        Get the list of all inputs (images and parameters) defined on this graph

        :return: a list of :class:`.SBSARInput`
        """
        return Graph.getAllInputs(self)

    @handle_exceptions()
    def getAllInputsInGroup(self, aGroup):
        """
        getAllInputsInGroup(aGroup)
        | Get the list of all inputs (images and parameters) contained in the given group.
        | If aGroup is None, returns all the parameters that are not included in a group.

        :param aGroup: The group of parameter to consider, given a SBSARGuiGroup object or a Group identifier
        :type aGroup: :class:`.SBSARGuiGroup` or str
        :return: a list of :class:`.SBSARInput`
        """
        if isinstance(aGroup, SBSARGuiGroup):
            aGroup = aGroup.mIdentifier
        return [aInput for aInput in self.getAllInputs() if aInput.getGroup() == aGroup]

    @handle_exceptions()
    def getInput(self, aInputIdentifier):
        """
        getInput(aInputIdentifier)
        Get the SBSARInput with the given identifier, among the input images and parameters

        :param aInputIdentifier: input parameter identifier
        :type aInputIdentifier: str
        :return: the corresponding :class:`.SBSARInput` object if found, None otherwise
        """
        return Graph.getInput(self, aInputIdentifier)

    @handle_exceptions()
    def getInputFromUID(self, aInputUID):
        """
        getInputFromUID(aInputUID)
        Get the SBSARInput with the given UID, among the input images and parameters

        :param aInputUID: input parameter UID
        :type aInputUID: str
        :return: the corresponding :class:`.SBSARInput` object if found, None otherwise
        """
        return Graph.getInputFromUID(self, aInputUID)

    @handle_exceptions()
    def getInputImages(self):
        """
        getInputImages()
        Get the list of image inputs

        :return: a list of :class:`.SBSARInput`
        """
        return Graph.getInputImages(self)

    @handle_exceptions()
    def getInputImage(self, aInputImageIdentifier):
        """
        getInputImage(aInputImageIdentifier)
        Get the SBSARInput of kind image with the given identifier

        :param aInputImageIdentifier: input image identifier
        :type aInputImageIdentifier: str
        :return: a :class:`.SBSARInput` if found, None otherwise
        """
        return Graph.getInputImage(self, aInputImageIdentifier)

    @handle_exceptions()
    def getInputImageWithUsage(self, aUsage):
        """
        getInputImageWithUsage(aUsage)
        Get the first SBSARInput of kind image which has the given usage defined

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.SBSARInput` if found, None otherwise
        """
        return Graph.getInputImageWithUsage(self, aUsage)

    @handle_exceptions()
    def getInputParameters(self):
        """
        getInputParameters()
        Get the list of inputs parameters that are not input entries but numerical values

        :return: a list of :class:`.SBSARInput`
        """
        return Graph.getInputParameters(self)

    @handle_exceptions()
    def getInputParameter(self, aInputParamIdentifier):
        """
        getInputParameter(aInputParamIdentifier)
        Get the SBSARInput with the given identifier

        :param aInputParamIdentifier: input parameter identifier
        :type aInputParamIdentifier: str
        :return: the corresponding :class:`.SBSARInput` object if found, None otherwise
        """
        return Graph.getInputParameter(self, aInputParamIdentifier)

    @handle_exceptions()
    def getInputParameterFromUID(self, aInputParamUID):
        """
        getInputParameterFromUID(aInputParamUID)
        Get the SBSARInput with the given UID

        :param aInputParamUID: input parameter UID
        :type aInputParamUID: str
        :return: the corresponding :class:`.SBSARInput` object if found, None otherwise
        """
        return Graph.getInputParameterFromUID(self, aInputParamUID)

    @handle_exceptions()
    def getPrimaryInput(self):
        """
        getPrimaryInput()
        Get the identifier of the primary input of the graph

        :return: The identifier of the primary input as a string if it exists, None otherwise
        """
        return self.mPrimaryInput

    @handle_exceptions()
    def isPrimaryInput(self, aInput):
        """
        isPrimaryInput(aInput)
        Check if the given input is the primary input for this graph or not

        :param aInput: The input to check
        :type aInput: :class:`.SBSARInput`
        :return: True if this is the primary input, False otherwise
        """
        aPrimaryInput = self.getPrimaryInput()
        return aPrimaryInput == aInput.mIdentifier if aPrimaryInput is not None else False
