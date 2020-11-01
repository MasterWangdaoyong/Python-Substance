# coding: utf-8
"""
Module **inputparameters** provides the definition of :class:`.SBSWidget` and :class:`.SBSParamInput`,
which allow the definition of the Input Parameters of a graph in Substance Designer.
"""
from __future__ import unicode_literals
import weakref

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject, ParamInput, Preset, PresetInput
from pysbs import python_helpers, api_helpers
from pysbs import sbscommon
from pysbs import params
from pysbs import sbsenum
from pysbs import sbslibrary

from .output import SBSUsage

# ==============================================================================
@doc_inherit
class SBSWidget(SBSObject):
    """
    Class that contains information on a Widget as defined in a .sbs file.
    A widget describes the way an input parameter will be displayed in Substance Designer.

    Members:
        * mName    (str): name of the widget used to visualize the entry, among the list defined in :attr:`sbslibrary.__dict_WidgetTypes`
        * mOptions (list of :class:`.SBSOption`): list of specific options of the widget type.
    """
    def __init__(self,
                 aName    = '',
                 aOptions = None):
        super(SBSWidget, self).__init__()
        self.mName      = aName
        self.mOptions   = aOptions

        self.mMembersForEquality = ['mName',
                                    'mOptions']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName    = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'name'   )
        self.mOptions = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'options', 'option', sbscommon.SBSOption)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName,     'name'    )
        aSBSWriter.writeListOfSBSNode(aXmlNode,        self.mOptions, 'options' , 'option')

    @handle_exceptions()
    def getOptions(self):
        """
        getOptions()

        :return: all the options of this widget as a list of :class:`.SBSOption`
        """
        return self.mOptions if self.mOptions else []

    @handle_exceptions()
    def getOption(self, aOptionId):
        """
        getOption(aOptionId)

        :param aOptionId: The option to look for, among the list defined in :class:`.WidgetOptionEnum`
        :type aOptionId:  :class:`.WidgetOptionEnum`
        :return: the requested option as a :class:`.SBSOption` if found, None otherwise
        """
        aOptionName = sbslibrary.getWidgetOptionName(aOptionId)
        return next((aOption for aOption in self.getOptions() if aOption.mName == aOptionName), None)

    @handle_exceptions()
    def getMinValue(self):
        """
        getMinValue()

        :return: the minimum value as a string if defined for this widget, None otherwise
        """
        aOption = self.getOption(sbsenum.WidgetOptionEnum.MIN)
        return aOption.mValue if aOption else None

    @handle_exceptions()
    def getMaxValue(self):
        """
        getMaxValue()

        :return: the maximum value as a string if defined for this widget, None otherwise
        """
        aOption = self.getOption(sbsenum.WidgetOptionEnum.MAX)
        return aOption.mValue if aOption else None

    @handle_exceptions()
    def getDefaultValue(self):
        """
        getDefaultValue()

        :return: the default value as a string or a list of strings if defined for this widget, None otherwise
        """
        if self.mName == sbslibrary.getWidgetName(sbsenum.WidgetTypeEnum.DROP_DOWN_LIST):
            aOption = self.getOption(sbsenum.WidgetOptionEnum.PARAMETERS)
            return aOption.mValue.split(';')[0] if aOption else None
        else:
            aOption = self.getOption(sbsenum.WidgetOptionEnum.DEFAULT)
            if aOption:
                defaultValue = aOption.mValue.split(';')
                return defaultValue if len(defaultValue) > 1 else defaultValue[0]
        return None

    @handle_exceptions()
    def getClamp(self):
        """
        getClamp()

        :return: the clamp as a boolean if defined for this widget, None otherwise
        """
        aOption = self.getOption(sbsenum.WidgetOptionEnum.CLAMP)
        return bool(int(aOption.mValue)) if aOption else None

    @handle_exceptions()
    def getStep(self):
        """
        getStep()

        :return: the step as a string if defined for this widget, None otherwise
        """
        aOption = self.getOption(sbsenum.WidgetOptionEnum.STEP)
        return aOption.mValue if aOption else None

    @handle_exceptions()
    def getLabels(self):
        """
        getLabels()

        :return: the list of all labels defined for this widget, in the right order, as a list of strings.
        """
        aLabels = []
        for i in range(4):
            aOption = self.getOption(sbsenum.WidgetOptionEnum.LABEL0 + i)
            if aOption:
                aLabels.append(aOption.mValue)
            else:
                break
        return aLabels

    @handle_exceptions()
    def getDropDownList(self):
        """
        getDropDownList()

        :return: the map{value(int):label(str)} corresponding to the drop down definition if defined in this widget, None otherwise.
        """
        aOption = self.getOption(sbsenum.WidgetOptionEnum.PARAMETERS)
        if aOption:
            aParams = aOption.mValue.split(';')
            aParams = aParams[1:]
            aMap = {}
            for i in range(len(aParams))[::2]:
                aMap[int(aParams[i])] = str(aParams[i+1])
            return aMap
        return None

    @handle_exceptions()
    def getWidgetType(self):
        """
        getWidgetType()

        :return: the kind of widget, as a :class:`.WidgetTypeEnum`
        """
        return sbslibrary.getWidgetTypeEnum(aWidgetName = self.mName)

    @handle_exceptions()
    def isInRange(self, aValue):
        """
        isInRange(aValue)

        :param aValue: The value to check
        :type aValue: int or float
        :return: True if the given value is allowed for this widget. Will return True if there is no range, or if the clamping is disabled.
        """
        aClamp = self.getClamp()
        aMin = self.getMinValue()
        aMax = self.getMaxValue()
        if aClamp is True and aMin is not None and aMax is not None:
            return float(aMin) <= float(aValue) <= float(aMax)
        return True

    @handle_exceptions()
    def setOption(self, aOptionId, aValue):
        """
        setOption(aOptionId, aValue)

        :param aOptionId: The option to look for, among the list defined in :class:`.WidgetOptionEnum`
        :param aValue: The value to set
        :type aOptionId:  :class:`.WidgetOptionEnum`
        :type aValue: string
        """
        aOption = self.getOption(aOptionId)
        if aOption is None:
            raise SBSImpossibleActionError('The option '+str(aOptionId)+' cannot be set on this widget')
        aOption.mValue = python_helpers.castStr(aValue)

    @handle_exceptions()
    def setClamp(self, aClamp):
        """
        setClamp(aClamp)

        :param aClamp: The clamp option for this widget (True to clamp)
        :type aClamp: boolean
        """
        aValue = api_helpers.formatValueForTypeStr(aClamp, sbsenum.ParamTypeEnum.BOOLEAN)
        self.setOption(sbsenum.WidgetOptionEnum.CLAMP, aValue)

    @handle_exceptions()
    def setDefaultValue(self, aDefaultValue, aType):
        """
        setDefaultValue(aDefaultValue, aType)

        :param aDefaultValue: The default values for this widget
        :type aDefaultValue: list of int or list of float
        :param aType: The type of this widget (BOOL , INT1 .. INT4 , FLOAT1 .. FLOAT4)
        :type aType: :class:`.ParamTypeEnum`
        """
        # Particular case of the drop down list, where the default value is the first value of the 'Parameters' option
        if self.mName == sbslibrary.getWidgetName(sbsenum.WidgetTypeEnum.DROP_DOWN_LIST):
            aOption = self.getOption(sbsenum.WidgetOptionEnum.PARAMETERS)

            # Check that the given default value is one of the drop down values
            aParameters = aOption.mValue.split(';')
            aValues = [aValue for aValue in aParameters[1:][::2]]
            aValue = api_helpers.formatValueForTypeStr(aDefaultValue, aType)
            if aValue not in aValues:
                raise SBSImpossibleActionError('The provided value ' + str(aValue) + ' does not match any of the drop down list values')

            aParameters[0] = aValue
            self.setOption(sbsenum.WidgetOptionEnum.PARAMETERS, ';'.join(aParameters))
        else:
            if self.mName != sbslibrary.getWidgetName(sbsenum.WidgetTypeEnum.TEXT):
                if not isinstance(aDefaultValue, list):
                    aDefaultValue = [aDefaultValue]
                for aValue in aDefaultValue:
                    if not self.isInRange(float(aValue)):
                        raise SBSImpossibleActionError('The provided value '+str(aValue)+' is not is the allowed range for this widget')
            aValue = api_helpers.formatValueForTypeStr(aDefaultValue, aType, aSep=';')
            self.setOption(sbsenum.WidgetOptionEnum.DEFAULT, aValue)

    @handle_exceptions()
    def setDropDownList(self, aValueMap):
        """
        setDropDownList(aValueMap)

        :param aValueMap: The drop down values, as a map in the format key(int):value(string)
        :type aValueMap: a dictionary in the format {key(int):value(string)}
        :raise: SBSImpossibleActionError
        """
        aCurrentParams = self.getOption(sbsenum.WidgetOptionEnum.PARAMETERS)
        if aCurrentParams is None:
            raise SBSImpossibleActionError('This widget cannot be defined by a drop down list')

        aParameters = []
        for aKey,aLabel in sorted(aValueMap.items()):
            aParameters.append(str(aKey))
            aParameters.append(str(aLabel))

        aDefaultValue = aCurrentParams.mValue.split(';')[0]
        if int(aDefaultValue) not in aValueMap.keys():
            aDefaultValue = aParameters[0]
        aParameters.insert(0, aDefaultValue)
        self.setOption(sbsenum.WidgetOptionEnum.PARAMETERS, ';'.join(aParameters))

    @handle_exceptions()
    def setLabels(self, aLabels):
        """
        setLabels(aLabels)

        :param aLabels: The labels for this widget
        :type aLabels: list of string
        """
        for i,aLabel in enumerate(aLabels[:4]):
            aValue = api_helpers.formatValueForTypeStr(aLabel, sbsenum.ParamTypeEnum.STRING)
            self.setOption(sbsenum.WidgetOptionEnum.LABEL0+i, aValue)

    @handle_exceptions()
    def setMinValue(self, aMinValue, aType):
        """
        setMinValue(aMinValue, aType)

        :param aMinValue: The minimum value to set on this widget
        :type aMinValue: int or float
        :param aType: The type of the values for this widget (int or float)
        :type aType: :class:`.ParamTypeEnum`
        """
        # Check that min < max
        aMaxValue = self.getMaxValue()
        if aMaxValue and float(aMinValue) > float(aMaxValue):
            raise SBSImpossibleActionError('The minimum value provided is greater than the current maximum value for this widget')

        # Check the range validity
        if self.getWidgetType() == sbsenum.WidgetTypeEnum.COLOR and not 0 <= aMinValue <= 1:
            raise SBSImpossibleActionError('A color is restricted to [0,1], '+str(aMinValue)+' is not included in this range')

        self.setOption(sbsenum.WidgetOptionEnum.MIN, api_helpers.formatValueForTypeStr(aMinValue, aType))

    @handle_exceptions()
    def setMaxValue(self, aMaxValue, aType):
        """
        setMaxValue(aMaxValue, aType)

        :param aMaxValue: The maximum value to set on this widget
        :type aMaxValue: int or float
        :param aType: The type of the values for this widget (int or float)
        :type aType: :class:`.ParamTypeEnum`
        """
        # Check that min < max
        aMinValue = self.getMinValue()
        if aMinValue and float(aMaxValue) < float(aMinValue):
            raise SBSImpossibleActionError('The maximum value provided is lower than the current minimum value for this widget')

        # Check the range validity
        if self.getWidgetType() == sbsenum.WidgetTypeEnum.COLOR and not 0 <= aMaxValue <= 1:
            raise SBSImpossibleActionError('A color is restricted to [0,1], '+str(aMinValue)+' is not included in this range')

        self.setOption(sbsenum.WidgetOptionEnum.MAX, api_helpers.formatValueForTypeStr(aMaxValue, aType))

    @handle_exceptions()
    def setStep(self, aStep, aType):
        """
        setStep(aStep, aType)

        :param aStep: The step value for this widget
        :type aStep: int or float
        :param aType: The type of the values for this widget (int or float)
        :type aType: :class:`.ParamTypeEnum`
        """
        aValue = api_helpers.formatValueForTypeStr(aStep, aType)
        self.setOption(sbsenum.WidgetOptionEnum.STEP, aValue)


# ==============================================================================
@doc_inherit
class SBSParamInput(SBSObject, ParamInput):
    """
    Class that contains information on an input parameter of a graph, as defined in a .sbs file

    Members:
        * mIdentifier    (str): identifier of this input.
        * mUID           (str): unique identifier in the /graph/ context.
        * mAttributes    (:class:`.SBSAttributes`): various attributes
        * mDisabled      (str, optional): this input is NOT used ("1" / None)
        * mUsages        (list of :class:`.SBSUsage`): usages of this input
        * mType          (str): type of the input
        * mDefaultValue  (:class:`.SBSConstantValue`): default value, depend on the type.
        * mWidget        (:class:`.SBSWidget`): default widget used to visualize the entry.
        * mGroup         (str, optional): string that contains a group name. Can uses path with '/' separators.
        * mVisibleIf     (str, optional): string boolean expression based on graph inputs values
        * mIsConnectable (str, optional): Flag saying whether the input is possible to connect to the input
    """
    __sAttributes = [sbsenum.AttributesEnum.Label, sbsenum.AttributesEnum.Description, sbsenum.AttributesEnum.UserTags]

    def __init__(self,
                 aIdentifier    = '',
                 aUID           = '',
                 aAttributes    = None,
                 aDisabled      = None,
                 aIsConnectable = None,
                 aUsages        = None,
                 aType          = '',
                 aDefaultValue  = None,
                 aDefaultWidget = None,
                 aGroup         = None,
                 aVisibleIf     = None):
        SBSObject.__init__(self)
        ParamInput.__init__(self, aUID, aIdentifier)
        self.mAttributes    = aAttributes
        self.mIsConnectable = aIsConnectable
        self.mDisabled      = aDisabled
        self.mUsages        = aUsages
        self.mType          = aType
        self.mDefaultValue  = aDefaultValue
        self.mWidget        = aDefaultWidget
        self.mGroup         = aGroup
        self.mVisibleIf     = aVisibleIf
        self.mMembersForEquality = ['mIdentifier',
                                    'mAttributes',
                                    'mIsConnectable',
                                    'mDisabled',
                                    'mUsages',
                                    'mType',
                                    'mDefaultValue',
                                    'mWidget',
                                    'mGroup',
                                    'mVisibleIf']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier    = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'identifier'   )
        self.mUID           = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'          )
        self.mAttributes    = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'attributes'   , sbscommon.SBSAttributes)
        self.mIsConnectable = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'isConnectable')
        self.mDisabled      = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'disabled'     )
        self.mUsages        = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'usages'       , 'usage', SBSUsage)
        self.mType          = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'type'         )
        self.mDefaultValue  = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'defaultValue' , sbscommon.SBSConstantValue)
        self.mWidget        = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'defaultWidget', SBSWidget)
        self.mGroup         = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'group'        )
        self.mVisibleIf     = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'visibleIf'    )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIdentifier     , 'identifier'     )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUID            , 'uid'            )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mAttributes     , 'attributes'     )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIsConnectable  , 'isConnectable'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mDisabled       , 'disabled'       )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mUsages         , 'usages'         , 'usage')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mType           , 'type'           )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mDefaultValue   , 'defaultValue'   )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mWidget         , 'defaultWidget'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mGroup          , 'group'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mVisibleIf      , 'visibleIf'      )

    @handle_exceptions()
    def getAllowedAttributes(self):
        """
        getAllowedAttributes()
        Get the attributes allowed on a SBSParamInput

        :return: the list of attribute enumeration allowed (:class:`.AttributesEnum`)
        """
        return SBSParamInput.__sAttributes

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        return self.mAttributes.getAttribute(aAttributeIdentifier) if self.mAttributes is not None else None

    @handle_exceptions()
    def setAttribute(self, aAttributeIdentifier, aAttributeValue):
        """
        setAttribute(aAttributeIdentifier, aAttributeValue)
        Set the given attribute

        :param aAttributeIdentifier: The attribute identifier to set
        :param aAttributeValue: The attribute value to set
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :type aAttributeValue: str
        """
        if self.mAttributes is None:
            self.mAttributes = sbscommon.SBSAttributes()
        self.mAttributes.setAttribute(aAttributeIdentifier, aAttributeValue, self)

    @handle_exceptions()
    def setAttributes(self, aAttributes):
        """
        setAttributes(aAttributes)
        Set the given attributes

        :param aAttributes: The attributes to set
        :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value}
        """
        if self.mAttributes is None:
            self.mAttributes = sbscommon.SBSAttributes()
        self.mAttributes.setAttributes(aAttributes, self)

    @handle_exceptions()
    def getGroup(self):
        """
        getGroup()
        Get the group associated to this parameter

        :return: the group of this parameter as a string if it has one, None otherwise
        """
        return self.mGroup

    @handle_exceptions()
    def getUsages(self):
        """
        getUsages()
        Get the usages of this param input

        :return: the list of :class:`.SBSUsage` defined on this param input
        """
        return self.mUsages if self.mUsages is not None else []

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this param input

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this param input, False otherwise
        """
        if isinstance(aUsage, int):
            aUsage = sbslibrary.getUsage(aUsage)
        return next((True for usage in self.getUsages() if aUsage == usage.mName), False)

    @handle_exceptions()
    def addUsage(self, aUsage, aComponents=sbsenum.ComponentsEnum.RGBA):
        """
        addUsage(aUsage, aComponents=sbsenum.ComponentsEnum.RGBA)
        Add the given usage on this param input

        :param aUsage: The usage to set
        :param aComponents: The components associated to this usage. Default to sbsenum.ComponentsEnum.RGBA
        :type aUsage: str or :class:`.UsageEnum`
        :type aComponents: :class:`.ComponentsEnum`, optional
        :return: the create :class:`.SBSUsage` object
        """
        if isinstance(aUsage, int):
            aUsage = sbslibrary.getUsage(aUsage)
        aUsage = SBSUsage(aComponents=aComponents, aName=aUsage)
        api_helpers.addObjectToList(self, 'mUsages', aUsage)

    @handle_exceptions()
    def getClamp(self):
        """
        getClamp()

        :return: the clamp as a boolean if defined for this parameter, None if not defined
        """
        return self.mWidget.getClamp() if self.isAnInputParameter() else None

    @handle_exceptions()
    def getMinValue(self, asList = False):
        """
        getMinValue(asList = False)

        :return: the minimum parameter value in the type of the parameter (int or float), None if not defined
        """
        if self.isAnInputParameter():
            aValue = self.formatValueToType(self.mWidget.getMinValue())
            if asList:
                return [aValue for _ in range(self.getDimension())]
            else:
                return aValue
        return None

    @handle_exceptions()
    def getMaxValue(self, asList = False):
        """
        getMaxValue(asList = False)

        :return: the maximum parameter value in the type of the parameter (int or float), None if not defined
        """
        if self.isAnInputParameter():
            aValue = self.formatValueToType(self.mWidget.getMaxValue())
            if asList:
                return [aValue for _ in range(self.getDimension())]
            else:
                return aValue
        return None

    @handle_exceptions()
    def getDefaultValue(self):
        """
        getDefaultValue()

        :return: the default value as a value or a list of values in the type of the parameter (bool, int or float), None if not defined
        """
        if self.isAnInputParameter():
            if self.mDefaultValue:
                return api_helpers.getTypedValueFromStr(aValue=self.mDefaultValue.getValue(), aType=self.mDefaultValue.getType())
            else:
                aDefaultValue = self.mWidget.getDefaultValue()
                if aDefaultValue:
                    if isinstance(aDefaultValue, list):
                        return [self.formatValueToType(aValue) for aValue in aDefaultValue]
                    else:
                        return self.formatValueToType(aDefaultValue)
        return None

    @handle_exceptions()
    def getDropDownList(self):
        """
        getDropDownList()

        :return: the map{value(int):label(str)} corresponding to the drop down definition if defined for this parameter, None otherwise.
        """
        return self.mWidget.getDropDownList() if self.isAnInputParameter() else None

    @handle_exceptions()
    def getIsConnectable(self):
        """
        getIsConnectable()

        :return: bool
        """
        # Note, None means false here
        return True if self.mIsConnectable == "1" else False

    @handle_exceptions()
    def getLabels(self):
        """
        getLabels()

        :return: the list of all labels defined for this parameter, in the right order, as a list of strings. None if not defined
        """
        return self.mWidget.getLabels() if self.isAnInputParameter() else None

    @handle_exceptions()
    def getStep(self):
        """
        getStep()

        :return: the step value (in the type of the parameter) of the widget for this parameter, None if not defined
        """
        return self.formatValueToType(self.mWidget.getStep()) if self.isAnInputParameter() else None

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Get the type of the input among the list defined in :class:`.ParamTypeEnum`

        :return: The type of the parameter as a :class:`.ParamTypeEnum`
        """
        return int(self.mType)

    @handle_exceptions()
    def getWidget(self):
        """
        getWidget()

        :return: The widget used for this parameter, as a :class:`.SBSDefaultWidget`. None if not defined
        """
        return self.mWidget if self.isAnInputParameter() else None

    @handle_exceptions()
    def getWidgetType(self):
        """
        getWidgetType()

        :return: the kind of widget used for this parameter, as a :class:`.WidgetTypeEnum`. None if not defined
        """
        return self.mWidget.getWidgetType() if self.isAnInputParameter() else None

    @handle_exceptions()
    def isAnInputImage(self):
        """
        isAnInputImage()
        Return True if this input is an input Entry (kind ENTRY_COLOR | ENTRY_GRAYSCALE | ENTRY_VARIANT)

        :return: True if it is an input entry, False otherwise
        """
        return self.getType() & sbsenum.ParamTypeEnum.ENTRY_VARIANT

    @handle_exceptions()
    def isAnInputParameter(self):
        """
        isAnInputParameter()
        Return True if this input is a parameter (numeric value)

        :return: True if it is an input parameter, False otherwise
        """
        return not self.isAnInputImage() and self.mWidget

    @handle_exceptions()
    def setClamp(self, aClamp):
        """
        setClamp(aClamp)
        Set the clamp option for the widget of this parameter

        :param aClamp: The clamp option for the parameter widget (True to clamp)
        :type aClamp: boolean
        :raise: SBSImpossibleActionError
        """
        if not self.isAnInputParameter():
            raise SBSImpossibleActionError('This input param is of kind Entry, cannot set an attribute relative to its widget')
        self.mWidget.setClamp(aClamp)

    @handle_exceptions()
    def setDefaultValue(self, aDefaultValue):
        """
        setDefaultValue(aDefaultValue)
        Set the default value of the widget

        :param aDefaultValue: The default value for the parameter widget
        :type aDefaultValue: depend on the widget type (single value or list)
        :raise: SBSImpossibleActionError
        """
        if not self.isAnInputParameter():
            raise SBSImpossibleActionError('This input param is of kind Entry, cannot set an attribute relative to its widget')
        self.mWidget.setDefaultValue(aDefaultValue, self.getType())
        self.__setDefaultValueAsWidget()

    @handle_exceptions()
    def setDropDownList(self, aValueMap):
        """
        setDropDownList(aValueMap)
        Set the drop down value map for a DropDown widget.

        :param aValueMap: The drop down values as a map
        :type aValueMap: dictionary in the format {key(int):value(string)}
        :raise: SBSImpossibleActionError
        """
        if not self.isAnInputParameter():
            raise SBSImpossibleActionError('This input param is of kind Entry, cannot set an attribute relative to its widget')

        self.mWidget.setDropDownList(aValueMap)
        self.__setDefaultValueAsWidget()

    @handle_exceptions()
    def setIsConnectable(self, aIsConnectable):
        """
        setIsConnectable(aIsConnectable)
        Set whether the input is connectable

        :param aIsConnectable: Whether the input is connectable or not
        :type aIsConnectable: bool or None
        :raise: SBSImpossibleActionError
        """
        # None means removing the property meaning it's false
        self.mIsConnectable = "1" if aIsConnectable else "0"

    @handle_exceptions()
    def setLabels(self, aLabels):
        """
        setLabels(aLabels)
        Set the labels associated to the different values for the widget of this parameter

        :param aLabels: The labels for the parameter widget
        :type aLabels: list of string
        :raise: SBSImpossibleActionError
        """
        if not self.isAnInputParameter():
            raise SBSImpossibleActionError('This input param is of kind Entry, cannot set an attribute relative to its widget')
        self.mWidget.setLabels(aLabels)

    @handle_exceptions()
    def setMinValue(self, aMinValue):
        """
        setMinValue(aMinValue)
        Set the minimum value for the widget of this parameter

        :param aMinValue: The minimum value to set
        :type aMinValue: int or float
        :raise: SBSImpossibleActionError
        """
        if not self.isAnInputParameter():
            raise SBSImpossibleActionError('This input param is of kind Entry, cannot set an attribute relative to its widget')
        self.mWidget.setMinValue(aMinValue, self.__getUnitType())

    @handle_exceptions()
    def setMaxValue(self, aMaxValue):
        """
        setMaxValue(aMaxValue)
        Set the maximum value for the widget of this parameter

        :param aMaxValue: The maximum value to set
        :type aMaxValue: int or float
        :raise: SBSImpossibleActionError
        """
        if not self.isAnInputParameter():
            raise SBSImpossibleActionError('This input param is of kind Entry, cannot set an attribute relative to its widget')
        self.mWidget.setMaxValue(aMaxValue, self.__getUnitType())

    @handle_exceptions()
    def setStep(self, aStep):
        """
        setStep(aStep)
        Set the step option for the widget of this parameter

        :param aStep: The step value for the parameter widget
        :type aStep: int or float
        :raise: SBSImpossibleActionError
        """
        if not self.isAnInputParameter():
            raise SBSImpossibleActionError('This input param is of kind Entry, cannot set an attribute relative to its widget')
        self.mWidget.setStep(aStep, self.__getUnitType())

    #==========================================================================
    # Private
    #==========================================================================
    @handle_exceptions()
    def __getUnitType(self):
        aType = self.getType()
        if aType & sbsenum.TypeMasksEnum.INTEGER:
            aType = sbsenum.ParamTypeEnum.INTEGER1
        elif aType & sbsenum.TypeMasksEnum.FLOAT:
            aType = sbsenum.ParamTypeEnum.FLOAT1
        return aType

    @handle_exceptions()
    def __setDefaultValueAsWidget(self):
        aType = self.getType()
        aCstValue = api_helpers.formatValueForTypeStr(aValue=self.mWidget.getDefaultValue(), aType=aType)
        self.mDefaultValue.setConstantValue(aValue=aCstValue, aType=aType, aInt1=True)

    @handle_exceptions()
    def getUID(self):
        return int(self.mUID)

    @handle_exceptions()
    def setUID(self, aUID):
        self.mUID = str(aUID)


#=======================================================================
@doc_inherit
class SBSPresetInput(SBSObject, PresetInput):
    """
    Class for manipulating embedded user-defined preset input inside a .sbs file

    Members:
        * mUID        (str): uid of the input parameter targeted by this preset input
        * mIdentifier (str): identifier of the input parameter targeted by this preset input
        * mType       (str): type of the input
        * mValue      (:class:`.SBSParamValue`): value, depend on the type.
    """
    def __init__(self, aUID='', aIdentifier='', aValue=None, aType=''):
        SBSObject.__init__(self)
        PresetInput.__init__(self, aUID=aUID,
                                    aIdentifier=aIdentifier,
                                    aValue=aValue,
                                    aType=aType)

        self.mMembersForEquality = ['mUID', 'mIdentifier', 'mValue', 'mType']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID        = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'uid'       )
        self.mIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'identifier')
        self.mType       = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'type'      )
        self.mValue      = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'paramValue', params.SBSParamValue)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID,        'uid'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier, 'identifier'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType,       'type'         )
        aSBSWriter.writeSBSNode(aXmlNode, self.mValue,                   'paramValue'   )

    @handle_exceptions()
    def getValue(self):
        return self.mValue.getValue()

    @handle_exceptions()
    def getType(self):
        return int(self.mType)

    @handle_exceptions()
    def getTypedValue(self):
        return api_helpers.getTypedValueFromStr(aValue = self.mValue.getValue(), aType=self.getType())

    @handle_exceptions()
    def setValue(self, aValue):
        """
        setValue(aValue)
        Set the value of the input parameter in the preset

        :param aValue: The value to set
        :type aValue: any type
        """
        formattedValue = api_helpers.formatValueForTypeStr(aType=self.getType(), aValue= aValue)
        self.mValue.setConstantValue(aType=self.getType(), aValue=formattedValue)

    @handle_exceptions()
    def getUID(self):
        return int(self.mUID)

    @handle_exceptions()
    def setUID(self, aUID):
        self.mUID = str(aUID)

    @handle_exceptions()
    def setType(self, aType):
        """
        setType(aType)
        Set the type of this preset input

        :param aType: The type to set
        :type aType: :class:`.ParamTypeEnum`
        """
        self.mType = str(aType)



#=======================================================================
@doc_inherit
class SBSPreset(SBSObject, Preset):
    """
    Class for manipulating embedded user-defined presets inside a .sbs file

    Members:
        * mLabel        (str): label of the preset
        * mUsertags     (str): user-defined tags
        * mPresetInputs (list of :class:`.SBSPresetInput`): list of preset inputs
    """
    def __init__(self, aLabel=None, aUsertags=None, aPresetInputs=None, aRefGraph=None):
        SBSObject.__init__(self)
        Preset.__init__(self, aLabel=aLabel,
                              aUsertags=aUsertags,
                              aPresetInputs=aPresetInputs if aPresetInputs is not None else [])

        self.mRefGraph = None
        self.setRefGraph(aRefGraph)
        self.mMembersForEquality = ['mLabel', 'mUsertags', 'mPresetInputs']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mLabel = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'label')
        self.mUsertags = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'usertags')
        self.mPresetInputs = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'presetinputs', 'presetinput', SBSPresetInput)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mLabel, 'label')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUsertags, 'usertags')
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mPresetInputs, 'presetinputs', 'presetinput')

    @handle_exceptions()
    def deletePresetInput(self, aInputParam):
        """
        deletePresetInput(aInputParam)
        Delete the preset input associated to the given input parameter.

        :param aInputParam: the input parameter to delete in this preset, as a SBSParamInput object or a UID
        :type aInputParam: :class:`.SBSParamInput` or str
        :return: True if the preset input has been found and deleted, False otherwise
        """
        aPresetInput = self.getPresetInput(aInputParam)
        if aPresetInput:
            self.mPresetInputs.remove(aPresetInput)
            return True
        return False

    @handle_exceptions()
    def getPresetInput(self, aInputParam):
        """
        getPresetInput(aInputParam)
        Get the preset input corresponding to the given input parameter.

        :param aInputParam: the input parameter to get in this preset, as a SBSParamInput object or a UID
        :type aInputParam: :class:`.SBSParamInput` or str
        :return: a :class:`.SBSPresetInput` if found, None otherwise
        """
        if isinstance(aInputParam, SBSParamInput):
            aInputParam = aInputParam.mUID
        return next((aPresetInput for aPresetInput in self.getPresetInputs() if aPresetInput.mUID==aInputParam), None)

    @handle_exceptions()
    def getPresetInputFromIdentifier(self, aInputParamIdentifier):
        """
        getPresetInputFromIdentifier(aInputParamIdentifier)
        Get the preset input with the given input UID defined in this preset

        :param aInputParamIdentifier: the identifier of the input parameter to get in this preset
        :type aInputParamIdentifier: str
        :return: a :class:`.SBSPresetInput` if found, None otherwise
        """
        return next((aPresetInput for aPresetInput in self.getPresetInputs() if aPresetInput.mIdentifier==aInputParamIdentifier), None)

    @handle_exceptions()
    def getPresetInputs(self):
        """
        getPresetInputs()
        Get all the preset inputs defined in this preset

        :return: a list of :class:`.SBSPresetInput`
        """
        return self.mPresetInputs if self.mPresetInputs is not None else []

    @handle_exceptions()
    def setPresetInput(self, aInputParam, aPresetValue):
        """
        setPresetInput(aInputParam, aPresetValue)
        Set the preset value for the given graph input parameter.

        :param aInputParam: the input parameter to set in this preset, as a SBSParamInput object or a UID
        :param aPresetValue: the value of this input parameter in this preset
        :type aInputParam: :class:`.SBSParamInput` or str
        :type aPresetValue: any type
        """
        if isinstance(aInputParam, SBSParamInput):
            aUID = aInputParam.mUID
            aInputParam = self.mRefGraph().getInputParameterFromUID(aInputParam.mUID)
        else:
            aUID = aInputParam
            aInputParam = self.mRefGraph().getInputParameterFromUID(aUID)

        if not aInputParam:
            raise SBSImpossibleActionError('Failed to set a preset for the input parameter '+str(aUID)+', can\'t find it in the graph')

        aPresetInput = self.getPresetInput(aInputParam=aInputParam)
        if aPresetInput is None:
            aPresetInput = SBSPresetInput(aUID        = aUID,
                                          aIdentifier = aInputParam.mIdentifier,
                                          aValue      = params.SBSParamValue())
            api_helpers.addObjectToList(self, 'mPresetInputs', aPresetInput)
        aPresetInput.setType(aInputParam.getType())
        aPresetInput.setValue(aPresetValue)

    def setRefGraph(self, aRefGraph):
        """
        setRefGraph(aRefGraph)
        Set the parent graph of this preset

        :param aRefGraph: The parent graph
        :type aRefGraph: :class:`.SBSGraph`
        """
        self.mRefGraph = weakref.ref(aRefGraph) if aRefGraph is not None else None
