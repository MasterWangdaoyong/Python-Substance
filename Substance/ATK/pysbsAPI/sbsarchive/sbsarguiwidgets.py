# coding: utf-8
"""
Module **sbsarguiwidget** aims to define SBSARObjects that are relative to the GUI widget as saved in a .sbsar file:
- :class:`.SBSARGuiWidget`
- :class:`.SBSARGuiAngle`
- :class:`.SBSARGuiComboBox`
- :class:`.SBSARGuiComboBoxItem`
- :class:`.SBSARGuiSlider`
- :class:`.SBSARGuiImage`
- :class:`.SBSARUsage`
"""
from __future__ import unicode_literals
import abc

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs import python_helpers
from pysbs.common_interfaces import SBSARObject
from pysbs import sbslibrary


# =======================================================================
@doc_inherit
class SBSARGuiWidget(SBSARObject):
    """
    Class that contains information on a GUI widget of an input parameter as defined in a .sbsar file.
    Base class for :class:`.SBSARGuiAngle`, :class:`.SBSARGuiColor`, :class:`.SBSARGuiSlider`

    Members:
        * mMin        (str): Minimum value
        * mMax        (str): Maximum value
        * mStep       (str): Defines step value for the slider.
        * mClamp      (str, optional): Defines if the values are clamped to [min,max] range or not ('on','off'). Default to off.
        * mLabel0     (str, optional): First value label
        * mLabel1     (str, optional): Second value label
        * mLabel2     (str, optional): Third value label
        * mLabel3     (str, optional): Fourth value label
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 aMin           = None,
                 aMax           = None,
                 aStep          = None,
                 aClamp         = None,
                 aComboBoxItems = None,
                 aLabel0        = None,
                 aLabel1        = None,
                 aLabel2        = None,
                 aLabel3        = None):
        super(SBSARGuiWidget, self).__init__()
        self.mMin           = aMin
        self.mMax           = aMax
        self.mStep          = aStep
        self.mClamp         = aClamp
        self.mComboBoxItems = aComboBoxItems
        self.mLabel0        = aLabel0
        self.mLabel1        = aLabel1
        self.mLabel2        = aLabel2
        self.mLabel3        = aLabel3

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        aMin           = aSBSParser.getXmlElementAttribValue(aXmlNode, 'min'   )
        aMax           = aSBSParser.getXmlElementAttribValue(aXmlNode, 'max'   )
        aClamp         = aSBSParser.getXmlElementAttribValue(aXmlNode, 'clamp' )
        aStep          = aSBSParser.getXmlElementAttribValue(aXmlNode, 'step'  )
        aLabel0        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label0' )
        aLabel1        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label1' )
        aLabel2        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label2' )
        aLabel3        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label3' )
        aComboBoxItems = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'guicomboboxitem', SBSARGuiComboBoxItem)
        self.mMin           = aMin           if aMin           is not None else self.mMin
        self.mMax           = aMax           if aMax           is not None else self.mMax
        self.mClamp         = aClamp         if aClamp         is not None else self.mClamp
        self.mStep          = aStep          if aStep          is not None else self.mStep
        self.mLabel0        = aLabel0        if aLabel0        is not None else self.mLabel0
        self.mLabel1        = aLabel1        if aLabel1        is not None else self.mLabel1
        self.mLabel2        = aLabel2        if aLabel2        is not None else self.mLabel2
        self.mLabel3        = aLabel3        if aLabel3        is not None else self.mLabel3
        self.mComboBoxItems = aComboBoxItems if aComboBoxItems is not None else self.mComboBoxItems

    @handle_exceptions()
    def convertValueToBool(self, aValue):
        """
        convertValueToBool(aValue)
        Converts the given value to a boolean, if the conversion is possible.

        :param aValue: The value to convert
        :type aValue: str
        :return: a boolean if the conversion is possible, the given aValue as is otherwise
        """
        if python_helpers.isStringOrUnicode(aValue):
            if   aValue == 'on':    return True
            elif aValue == 'off':   return False
        try:
            return bool(int(aValue))
        except:
            return aValue

    @handle_exceptions()
    def getMinValue(self):
        """
        getMinValue()

        :return: the minimum value as a string if defined for this widget, None otherwise
        """
        return self.mMin

    @handle_exceptions()
    def getMaxValue(self):
        """
        getMaxValue()

        :return: the maximum value as a string if defined for this widget, None otherwise
        """
        return self.mMax

    @handle_exceptions()
    def getClamp(self):
        """
        getClamp()

        :return: the clamp as a boolean if defined for this widget, None otherwise
        """
        return self.convertValueToBool(self.mClamp)

    @handle_exceptions()
    def getStep(self):
        """
        getStep()

        :return: the step as a string if defined for this widget, None otherwise
        """
        return self.mStep

    @handle_exceptions()
    def getLabels(self):
        """
        getLabels()

        :return: the list of all labels defined for this widget, in the right order, as a list of strings.
        """
        aLabels = []
        i = 0
        aMember = 'mLabel'+str(i)
        if self.getMinValue() and hasattr(self, aMember) and getattr(self, aMember) is not None:
            nbLabels = len(self.getMinValue().split(','))
            while i<nbLabels and hasattr(self, aMember) and getattr(self, aMember) is not None:
                aLabels.append(getattr(self, aMember))
                i += 1
                aMember = 'mLabel'+str(i)
        return aLabels

    @handle_exceptions()
    def getDropDownList(self):
        """
        getDropDownList()

        :return: the map{value(int):label(str)} corresponding to the drop down definition if defined in this widget, None otherwise.
        """
        if self.mComboBoxItems:
            aMap = {}
            for aItem in self.mComboBoxItems:
                aMap[int(aItem.mValue)] = aItem.mText
            return aMap
        return None


# =======================================================================
@doc_inherit
class SBSARGuiAngle(SBSARGuiWidget):
    """
    Class that contains information on the GUI slider widget of an input parameter as defined in a .sbsar file

    Members:
        * mMin   (str): Minimum value
        * mMax   (str): Maximum value
        * mClamp (str, optional): Defines if the values are clamped to [min,max] range or not ('on','off'). Default to off.
        * mStep  (str, optional): Defines step value for the widget.
        * mUnit  (str, optional): Unit of the angle ('degrees','radians','turns')
    """
    def __init__(self,
                 aMin   = '',
                 aMax   = '',
                 aClamp = None,
                 aStep  = None,
                 aUnit  = None
                 ):
        super(SBSARGuiAngle, self).__init__(aMin = aMin, aMax = aMax, aClamp = aClamp, aStep = aStep)
        self.mUnit  = aUnit

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSARGuiAngle, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mUnit  = aSBSParser.getXmlElementAttribValue(aXmlNode, 'unit'  )


# =======================================================================
@doc_inherit
class SBSARGuiComboBox(SBSARGuiWidget):
    """
    Class that contains information on the GUI combo box widget of an input parameter as defined in a .sbsar file

    Members:
        * mComboBoxItems (list of :class:`.SBSARGuiComboBoxItem`): The items in the combo box menu
    """
    def __init__(self,
                 aComboBoxItems = None):
        super(SBSARGuiComboBox, self).__init__(aComboBoxItems = aComboBoxItems)
        #self.mComboBoxItems = aComboBoxItems

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSARGuiComboBox, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        #self.mComboBoxItems = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'guicomboboxitem', SBSARGuiComboBoxItem)


# =======================================================================
@doc_inherit
class SBSARGuiComboBoxItem(SBSARObject):
    """
    Class that contains information on the GUI combo box widget of an input parameter as defined in a .sbsar file

    Members:
        * mValue (str): Drop down value (integer)
        * mText  (str): Associated label
    """
    def __init__(self,
                 aValue  = '',
                 aText   = ''):
        super(SBSARGuiComboBoxItem, self).__init__()
        self.mValue = aValue
        self.mText  = aText

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mValue = aSBSParser.getXmlElementAttribValue(aXmlNode, 'value' )
        self.mText  = aSBSParser.getXmlElementAttribValue(aXmlNode, 'text'  )


# =======================================================================
@doc_inherit
class SBSARGuiSlider(SBSARGuiWidget):
    """
    Class that contains information on the GUI angle widget of an input parameter as defined in a .sbsar file

    Members:
        * mMin        (str): Minimum value
        * mMax        (str): Maximum value
        * mStep       (str): Defines step value for the slider.
        * mClamp      (str, optional): Defines if the values are clamped to [min,max] range or not ('on','off'). Default to off.
        * mLabel0     (str, optional): First value label
        * mLabel1     (str, optional): Second value label
        * mLabel2     (str, optional): Third value label
        * mLabel3     (str, optional): Fourth value label
        * mSuffix     (str, optional): Suffix
        * mValueScale (str, optional): Value scale
    """
    def __init__(self,
                 aMin        = '',
                 aMax        = '',
                 aStep       = '',
                 aClamp      = 'off',
                 aLabel0     = 'X',
                 aLabel1     = 'Y',
                 aLabel2     = 'Z',
                 aLabel3     = 'W',
                 aSuffix     = None,
                 aValueScale = None
                 ):
        super(SBSARGuiSlider, self).__init__(aMin = aMin, aMax = aMax, aClamp = aClamp, aStep = aStep,
                                            aLabel0 = aLabel0, aLabel1 = aLabel1, aLabel2 = aLabel2, aLabel3 = aLabel3)
        self.mSuffix     = aSuffix
        self.mValueScale = aValueScale

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSARGuiSlider, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mSuffix     = aSBSParser.getXmlElementAttribValue(aXmlNode, 'suffix' )
        self.mValueScale = aSBSParser.getXmlElementAttribValue(aXmlNode, 'valuescale' )


# =======================================================================
@doc_inherit
class SBSARGuiImage(SBSARObject):
    """
    Class that contains information on the GUI image widget of an input as defined in a .sbsar file

    Members:
        * mColorType (str): Color mode, 'color' or 'grayscale'
        * mUsages    (list of :class:`.SBSARUsage`): usages of this input image ('<channels>' in the .sbsar file)
    """
    def __init__(self,
                 aColorType = '',
                 aUsages    = None):
        super(SBSARGuiImage, self).__init__()
        self.mColorType = aColorType
        self.mUsages    = aUsages if aUsages is not None else []

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mColorType = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'colortype'  )
        self.mUsages    = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'channels',  'channel', SBSARUsage)

    @handle_exceptions()
    def getUsages(self):
        """
        getUsages()
        Get the usages of this param input

        :return: the list of :class:`.SBSARUsage` defined on this image input
        """
        return self.mUsages if self.mUsages is not None else []

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this image input

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this param input, False otherwise
        """
        if isinstance(aUsage, int):
            aUsage = sbslibrary.getUsage(aUsage)
        return next((True for usage in self.getUsages() if aUsage == usage.mName), False)

    @handle_exceptions()
    def isColor(self):
        """
        isColor()
        Check if the image is in color

        :return: True if this is a color image, False otherwise
        """
        return self.mColorType == 'color'

    @handle_exceptions()
    def isGrayscale(self):
        """
        isGrayscale()
        Check if the image is in grayscale

        :return: True if this is a grayscale image, False otherwise
        """
        return self.mColorType == 'grayscale'


# =======================================================================
@doc_inherit
class SBSARUsage(SBSARObject):
    """
    Class that contains information on the channels of an input or output texture as defined in a .sbsar file

    Members:
        * mName       (str): Drop down value (integer)
        * mComponents (str, optional): Color components. Default to 'RGBA'
        * mColorSpace (str, optional): Color space for the channel
    """
    def __init__(self,
                 aName = '',
                 aComponents = '',
                 aColorSpace = None):
        super(SBSARUsage, self).__init__()
        self.mName       = aName
        self.mComponents = aComponents
        self.mColorSpace = aColorSpace

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName       = aSBSParser.getXmlElementAttribValue(aXmlNode, 'names')
        self.mComponents = aSBSParser.getXmlElementAttribValue(aXmlNode, 'components')
        self.mColorSpace = aSBSParser.getXmlElementAttribValue(aXmlNode, 'colorspace')

@doc_inherit
class SBSARGuiButton(SBSARGuiWidget):
    """
    Class that contains information on the GUI button widget of an input parameter as defined in a .sbsar file

    """
    def __init__(self,
                 aLabel0 = '',
                 aLabel1 = ''):
        super(SBSARGuiButton, self).__init__(aLabel0 = aLabel0, aLabel1 = aLabel1)

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSARGuiButton, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
