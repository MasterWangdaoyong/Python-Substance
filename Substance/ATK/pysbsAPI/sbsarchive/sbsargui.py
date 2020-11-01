# coding: utf-8
"""
Module **sbsargui** aims to define SBSARObjects that are relative to the GUI as saved in a .sbsar file,
mostly :class:`.SBSARInputGui`, :class:`.SBSAROutputGui` and :class:`.SBSARGuiGroup`.
"""

from __future__ import unicode_literals
from pysbs import sbslibrary
from pysbs import sbsenum
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.common_interfaces import SBSARObject
from .sbsarguiwidgets import SBSARGuiAngle, SBSARGuiComboBox, SBSARGuiImage, SBSARGuiSlider, SBSARUsage, SBSARGuiButton


# =======================================================================
@doc_inherit
class SBSARInputGui(SBSARObject):
    """
    Class that contains information on the GUI widget of an input as defined in a .sbsar file

    Members:
        * mWidget      (str): Kind of widget associated to this input parameter.
        * mLabel       (str): Label of the input (unique).
        * mDescription (str, optional): Description.
        * mGroup       (str, optional): Group of parameters.
        * mState       (str, optional): State of the input ('visible','hidden','disabled').
        * mOrder       (str, optional): Input order.
        * mVisibleIf   (str, optional): Conditional visibility definition.
        * mGuiAngle    (:class:`.SBSARGuiAngle`, optional): Angle widget definition, if the widget is of kind 'angle'
        * mGuiComboBox (:class:`.SBSARGuiComboBox`, optional): ComboBox widget definition, if the widget is of kind 'combobox'
        * mGuiImage    (:class:`.SBSARGuiImage`, optional): Image widget definition, if the widget is of kind 'image'
        * mGuiSlider   (:class:`.SBSARGuiSlider`, optional): Slider widget definition, if the widget is of kind 'slider'
        * mShowas      (str, optional): defines whether the input is should be shown as a pin or tweakable
    """
    # Widget names
    sDefaultWidget  = 'default'
    sAngleWidget    = 'angle'
    sCheckBoxWidget = 'checkbox'
    sColorWidget    = 'color'
    sComboBoxWidget = 'combobox'
    sImageWidget    = 'image'
    sPointWidget    = 'point'
    sRectWidget     = 'rect'
    sSliderWidget   = 'slider'
    sSpinboxWidget  = 'spinbox'
    sButtonWidget   = 'togglebutton'

    # Attribute names
    sRandomSeedIdentifier   = '$randomseed'
    sOutputSizeIdentifier   = '$outputsize'
    sNormalFormatIdentifier = '$normalformat'
    sTimeIdentifier         = '$time'

    sPinIdentifier   = 'pin'
    aTweakIdentifier = 'tweak'
    def __init__(self,
                 aWidget       = '',
                 aLabel        = '',
                 aDescription  = None,
                 aGroup        = None,
                 aOrder        = None,
                 aState        = None,
                 aVisibleIf    = None,
                 aGuiAngle     = None,
                 aGuiComboBox  = None,
                 aGuiImage     = None,
                 aGuiSlider    = None,
                 aShowas       = None):
        super(SBSARInputGui, self).__init__()
        self.mWidget      = aWidget
        self.mLabel       = aLabel
        self.mDescription = aDescription
        self.mGroup       = aGroup
        self.mOrder       = aOrder
        self.mState       = aState
        self.mVisibleIf   = aVisibleIf
        self.mGuiAngle    = aGuiAngle
        self.mGuiComboBox = aGuiComboBox
        self.mGuiImage    = aGuiImage
        self.mGuiSlider   = aGuiSlider
        self.mShowas      = aShowas

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWidget      = aSBSParser.getXmlElementAttribValue(aXmlNode,            'widget'     )
        self.mLabel       = aSBSParser.getXmlElementAttribValue(aXmlNode,            'label'      )
        self.mDescription = aSBSParser.getXmlElementAttribValue(aXmlNode,            'description')
        self.mGroup       = aSBSParser.getXmlElementAttribValue(aXmlNode,            'group'      )
        self.mOrder       = aSBSParser.getXmlElementAttribValue(aXmlNode,            'order'      )
        self.mState       = aSBSParser.getXmlElementAttribValue(aXmlNode,            'state'      )
        self.mVisibleIf   = aSBSParser.getXmlElementAttribValue(aXmlNode,            'visibleif'  )
        self.mGuiAngle    = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'guiangle'   , SBSARGuiAngle   )
        self.mGuiComboBox = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'guicombobox', SBSARGuiComboBox)
        self.mGuiImage    = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'guiimage'   , SBSARGuiImage   )
        self.mGuiSlider   = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'guislider'  , SBSARGuiSlider  )
        self.mGuiButton   = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'guibutton'  , SBSARGuiButton  )
        self.mShowas      = aSBSParser.getXmlElementAttribValue(aXmlNode,            'showas'     )

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        """
        getAttribute(aAttributeIdentifier)
        Get the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :return: the attribute value if defined, None otherwise
        """
        if   aAttributeIdentifier == sbsenum.AttributesEnum.Label:        return self.mLabel
        elif aAttributeIdentifier == sbsenum.AttributesEnum.Description:  return self.mDescription
        return None

    @handle_exceptions()
    def getGroup(self):
        """
        getGroup()
        Get the GUI group identifier containing this input

        :return: The GUI group as a string if defined, None otherwise
        """
        return self.mGroup

    @handle_exceptions()
    def isAnInputImage(self):
        """
        isAnInputImage()
        Check if this input is of kind image.

        :return: True if this is an input image, False otherwise
        """
        return self.mWidget == SBSARInputGui.sImageWidget and self.mGuiImage is not None

    @handle_exceptions()
    def isAnInputParameter(self):
        """
        isAnInputParameter()
        Check if this input is a parameter.

        :return: True if this is an input parameter, False otherwise
        """
        return self.mWidget is None or self.mWidget != SBSARInputGui.sImageWidget

    @handle_exceptions()
    def isAnAngle(self):
        """
        isAnAngle()
        Check if this input is a parameter with an angle widget.

        :return: True if this is an input parameter with an angle widget, False otherwise
        """
        return self.mWidget == SBSARInputGui.sAngleWidget

    @handle_exceptions()
    def isAButton(self):
        """
        isAButton()
        Check if this input is a parameter with a toggle button widget.

        :return: True if this is an input parameter with a toggle button widget, False otherwise
        """
        return self.mWidget == SBSARInputGui.sButtonWidget

    @handle_exceptions()
    def isAColor(self):
        """
        isAColor()
        Check if this input is a parameter with a color widget.

        :return: True if this is an input parameter with a color widget, False otherwise
        """
        return self.mWidget == SBSARInputGui.sColorWidget

    @handle_exceptions()
    def isAComboBox(self):
        """
        isAComboBox()
        Check if this input is a parameter with a combo box widget.

        :return: True if this is an input parameter with a combo box widget, False otherwise
        """
        return self.mWidget == SBSARInputGui.sComboBoxWidget

    @handle_exceptions()
    def isASlider(self):
        """
        isASlider()
        Check if this input is a parameter with a slider widget.

        :return: True if this is an input parameter with a slider widget, False otherwise
        """
        return self.mWidget == SBSARInputGui.sSliderWidget

    @handle_exceptions()
    def getClamp(self):
        """
        getClamp()

        :return: the clamp as a boolean if defined for this parameter, None if not defined
        """
        return self.getWidget().getClamp() if self.getWidget() is not None else None

    @handle_exceptions()
    def getMinValue(self):
        """
        getMinValue()

        :return: the minimum parameter value in the type of the parameter (int or float), None if not defined
        """
        return self.getWidget().getMinValue() if self.getWidget() is not None else None

    @handle_exceptions()
    def getMaxValue(self):
        """
        getMaxValue()

        :return: the maximum parameter value in the type of the parameter (int or float), None if not defined
        """
        return self.getWidget().getMaxValue() if self.getWidget() is not None else None

    @handle_exceptions()
    def getDropDownList(self):
        """
        getDropDownList()

        :return: the map{value(int):label(str)} corresponding to the drop down definition if defined for this parameter, None otherwise.
        """
        return self.getWidget().getDropDownList() if self.getWidget() is not None else None

    @handle_exceptions()
    def getLabels(self):
        """
        getLabels()

        :return: the list of all labels defined for this parameter, in the right order, as a list of strings. None if not defined
        """
        return self.getWidget().getLabels() if self.getWidget() is not None else None

    @handle_exceptions()
    def getStep(self):
        """
        getStep()

        :return: the step value (in the type of the parameter) of the widget for this parameter, None if not defined
        """
        return self.getWidget().getStep() if self.getWidget() is not None else None

    @handle_exceptions()
    def getWidget(self):
        """
        getWidget()
        Get the GuiWidget object defined on this parameters.
        This will return None for a Button widget, a Transformation widget or a Color widget.

        :return: The widget as a :class:`.SBSARObject` if defined, None otherwise
        """
        if   self.isAnInputImage():     return self.mGuiImage
        elif self.isAnAngle():          return self.mGuiAngle
        elif self.isASlider():          return self.mGuiSlider
        elif self.isAComboBox():        return self.mGuiComboBox
        elif self.isAnInputImage():     return self.mGuiImage
        else:
            return None

    @handle_exceptions()
    def getUsages(self):
        """
        getUsages()
        Get the usages of this param input

        :return: the list of :class:`.SBSARUsage` defined on this image input
        """
        return self.mGuiImage.getUsages() if self.isAnInputImage() else None

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this image input

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this param input, False otherwise
        """
        return self.mGuiImage.hasUsage(aUsage) if self.isAnInputImage() else None

    @handle_exceptions()
    def getLabelFalse(self):
        """
        getLabelFalse()
        Returns the label for the false option if it's valid for this input

        :return: str with the label if it's a button, otherwise None
        """
        return self.mGuiButton.mLabel0 if (self.mGuiButton and self.isAButton()) else None

    @handle_exceptions()
    def getLabelTrue(self):
        """
        getLabelTrue()
        Returns the label for the true option if it's valid for this input

        :return: str with the label if it's a button, otherwise None
        """
        return self.mGuiButton.mLabel1 if (self.mGuiButton and self.isAButton()) else None

# =======================================================================
@doc_inherit
class SBSAROutputGui(SBSARObject):
    """
    Class that contains information on the GUI widget of an input as defined in a .sbsar file

    Members:
        * mLabel       (str): Label of the input (unique).
        * mDescription (str, optional): Description.
        * mGroup       (str, optional): Group of parameters.
        * mVisibleIf   (str, optional): Conditional visibility definition.
        * mUsages      (list of :class:`.SBSARUsage`, optional): Usages of this output ('<channels>' is the .sbsar file)
    """
    def __init__(self,
                 aLabel       = '',
                 aDescription = None,
                 aGroup       = None,
                 aVisibleIf   = None,
                 aUsages      = None):
        super(SBSAROutputGui, self).__init__()
        self.mLabel       = aLabel
        self.mDescription = aDescription
        self.mGroup       = aGroup
        self.mVisibleIf   = aVisibleIf
        self.mUsages      = aUsages if aUsages is not None else []

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mLabel       = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'label'       )
        self.mDescription = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'description' )
        self.mGroup       = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'group'       )
        self.mVisibleIf   = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'visibleif'   )
        self.mUsages      = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'channels', 'channel', SBSARUsage)

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        """
        getAttribute(aAttributeIdentifier)
        Get the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :return: the attribute value if defined, None otherwise
        """
        if   aAttributeIdentifier == sbsenum.AttributesEnum.Label:        return self.mLabel
        elif aAttributeIdentifier == sbsenum.AttributesEnum.Description:  return self.mDescription
        return None

    @handle_exceptions()
    def getUsages(self):
        """
        getUsages()
        Get the usages of this param output

        :return: the list of :class:`.SBSARUsage` defined on this output
        """
        return self.mUsages if self.mUsages is not None else []

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this output

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this output, False otherwise
        """
        if isinstance(aUsage, int):
            aUsage = sbslibrary.getUsage(aUsage)
        return next((True for usage in self.getUsages() if aUsage == usage.mName), False)

# =======================================================================
@doc_inherit
class SBSARGuiGroup(SBSARObject):
    """
    Class that contains information on a GUI group as defined in a .sbsar file

    Members:
        * mIdentifier    (str): Unique identifier of the group of parameter.
        * mLabel         (str): Label of the group of parameter.
        * mDescription   (str, optional): Description
        * mDefaultState  (str, optional): Default state ('folded','unfolded').
        * mOrder         (str, optional): Group order
    """

    def __init__(self,
                 aIdentifier   = '',
                 aLabel        = '',
                 aDescription  = None,
                 aDefaultState = None,
                 aOrder        = None):
        super(SBSARGuiGroup, self).__init__()
        self.mIdentifier   = aIdentifier
        self.mLabel        = aLabel
        self.mDescription  = aDescription
        self.mDefaultState = aDefaultState
        self.mOrder        = aOrder

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier   = aSBSParser.getXmlElementAttribValue(aXmlNode, 'identifier')
        self.mLabel        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label')
        self.mDescription  = aSBSParser.getXmlElementAttribValue(aXmlNode, 'description')
        self.mDefaultState = aSBSParser.getXmlElementAttribValue(aXmlNode, 'defaultstate')
        self.mOrder        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'order')
