# coding: utf-8
"""
Module **qtclasses** provides an implementation of a very small subset of classes present in PyQt API, in particular the QVariant object,
in order to handle the objects serialized in the .sbs file from a Qt object, as it is the case for the Baking Parameters.
"""
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
from pysbs.api_decorators import doc_source_code_enum
from pysbs import python_helpers

@doc_source_code_enum
class QtVariantTypeEnum:
    """
    http://pyqt.sourceforge.net/Docs/PyQt4/qvariant.html#QVariantList-typedef
    """
    NONE            = 0
    BOOL            = 1
    INT             = 2
    DOUBLE          = 6
    VARIANT_MAP     = 8
    VARIANT_LIST    = 9
    STRING          = 10
    STRING_LIST     = 11
    BYTE_ARRAY      = 12
    URL             = 17
    SIZE            = 21

class QtVariant:
    """
    Class QtVariant provides the definition of a variant object.

    Members
        * mType (:class:`.QtVariantTypeEnum`): type of the variant object
        * mValue (any type): value
    """
    def __init__(self, aType=None, aValue=None):
        self.mType = aType
        self.mValue = aValue

    def getValue(self):
        """
        getValue()
        Get the value of the variant object

        :return: The value of the variant object
        """
        return self.mValue

    def getValueStr(self):
        """
        getValueStr()
        Get the value of the variant object converted into a string

        :return: The value of the variant object, as a string
        """
        # Write value depending on type
        if self.mType == QtVariantTypeEnum.BOOL:
            aValue = 'true' if self.mValue is True or self.mValue==1 else 'false'

        elif self.mType == QtVariantTypeEnum.INT:
            aValue = str(self.mValue)

        elif self.mType == QtVariantTypeEnum.DOUBLE:
            aValue = str(self.mValue)

        elif self.mType == QtVariantTypeEnum.SIZE:
            if isinstance(self.mValue, tuple):
                aValue = '(' + str(self.mValue[0]) + ',' +str(self.mValue[1]) + ')'
            else:
                aValue = self.mValue
        else:
            aValue = self.mValue

        return aValue

    def setValue(self, aValue):
        """
        setValue(aValue)
        Set the value of the variant object, without modifying its type.

        :param aValue: The value to set
        :type aValue: any type compatible with the current type of the variant object
        :raise: TypeError if the type of the value is incompatible with the type of the variant object
        """
        # Write value depending on type
        if self.mType == QtVariantTypeEnum.BOOL:
            if python_helpers.isStringOrUnicode(aValue):
                if   aValue.lower() == 'true':   aValue = 1
                elif aValue.lower() == 'false':  aValue = 0
                else:                            aValue = int(aValue)
            aValue = True if aValue and aValue > 0 else False

        elif self.mType == QtVariantTypeEnum.INT:
            # Remove decimals to allow int conversion
            if python_helpers.isStringOrUnicode(aValue):
                dotPos = aValue.find('.')
                if dotPos >= 0:
                    aValue = aValue[0:dotPos] if dotPos > 0 else 0
            aValue = int(aValue) if aValue else 0

        elif self.mType == QtVariantTypeEnum.DOUBLE:
            aValue = float(aValue) if aValue else 0.0

        elif self.mType == QtVariantTypeEnum.VARIANT_MAP:
            if isinstance(aValue, dict):
                aValue = QtVariantMap(aMap = aValue)
            if not isinstance(aValue, QtVariantMap):
                raise TypeError('aValue must be a dict or a QtVariantMap')

        elif self.mType == QtVariantTypeEnum.VARIANT_LIST:
            if not isinstance(aValue, list):
                raise TypeError('aValue must be a list')

        elif self.mType == QtVariantTypeEnum.STRING:
            aValue = python_helpers.castStr(aValue)

        elif self.mType == QtVariantTypeEnum.STRING_LIST:
            if not isinstance(aValue, list):
                raise TypeError('aValue must be a list')

        elif self.mType == QtVariantTypeEnum.BYTE_ARRAY:
            aValue = python_helpers.castStr(aValue)

        elif self.mType == QtVariantTypeEnum.URL:
            aValue = python_helpers.castStr(aValue)

        elif self.mType == QtVariantTypeEnum.SIZE:
            if not isinstance(aValue, tuple):
                raise TypeError('aValue must be a tuple')

        else:
            log.error("Unsupported type: %s", str(self.mType))
        self.mValue = aValue


class QtVariantMap:
    """
    Class QtVariantMap provides the definition of a variant map, which has a dictionary associating a key to a :class:`.QtVariant`.

    Members
        * mMap (dictionary with the format {key(str):value(:class:`.QtVariant`)}: the dictionary of variant objects.
    """
    def __init__(self, aMap):
        self.mMap = aMap

    def getItem(self, aKey):
        """
        getItem(aKey)
        Get the variant object of the given key in the map

        :param aKey: The key to look for
        :type aKey: str
        :return: The variant object with this key if found, None otherwise
        """
        return self.mMap.get(aKey)

    def getItemValue(self, aKey):
        """
        getItemValue(aKey)
        Get the value of the given key in the map

        :param aKey: The key to look for
        :type aKey: str
        :return: The value of the variant object with this key if found, None otherwise
        """
        aItem = self.getItem(aKey)
        return aItem.getValue() if aItem is not None else None

    def getSize(self):
        """
        getSize()
        Get the size of the map

        :return: The size of the map as an integer
        """
        return len(self.mMap)

    def setItem(self, aKey, aValue):
        """
        setItem(aKey, aValue)
        Set the given item with the given key

        :param aKey: The key to add
        :param aValue: The item to set
        :type aKey: str
        :type aValue: :class:`.QtVariant`
        :return: The size of the map as an integer
        """
        self.mMap[aKey] = aValue

    def pop(self, aKey, aDefault):
        """
        pop(aKey, aDefault)
        Remove the item at the given key and return it.

        :param aKey: The key to remove
        :param aDefault: The default value to return if not found
        :type aKey: str
        :type aDefault: any type
        :return: The item removed if found, of the given default value if not found
        """
        return self.mMap.pop(aKey, aDefault)


class QtColor:
    """
    Class QtColor provides the definition of a color.

    Members
        * mMode  (:class:`.QtColorModeEnum`)}: the color mode.
        * mAlpha (int): Alpha component value
        * mC1    (int): First component value
        * mC2    (int): Second component value
        * mC3    (int): Third component value
        * mC4    (int): Fourth component value
    """
    @doc_source_code_enum
    class QtColorModeEnum:
        """
        Color mode enumeration
        """
        NONE  = 0
        ARGB  = 1
        AHSV  = 2
        ACMYK = 3
        AHSL  = 4

    def __init__(self, aMode=QtColorModeEnum.ARGB, aAlpha=0, aC1=0, aC2=0, aC3=0, aC4=0):
        self.mMode  = aMode
        self.mAlpha = aAlpha
        self.mC1    = aC1
        self.mC2    = aC2
        self.mC3    = aC3
        self.mC4    = aC4

    def getColor(self):
        """
        getColor()
        Get the color in the appropriate format depending on the color mode (RGB or HSV)

        :return: The color as a list of 4 int [R,G,B,A] or [H,S,V,A]
        """
        to8Bit = 255.0/65535.0
        if self.mMode == QtColor.QtColorModeEnum.ARGB:
            cA = self.mAlpha * to8Bit
            cR = self.mC1 * to8Bit
            cG = self.mC2 * to8Bit
            cB = self.mC3 * to8Bit
            return [cR,cG,cB,cA]
        elif self.mMode == QtColor.QtColorModeEnum.AHSV:
            cA = self.mAlpha * to8Bit
            cH = (self.mC1 / 100.0) * 358.0 / 359.0
            cS = self.mC2 * to8Bit
            cV = self.mC3 * to8Bit
            return [cH,cS,cV,cA]

    def isRGBA(self):
        """
        isRGBA()
        Check if the color is defined as an RGBA color

        :return: True if RGBA, False otherwise
        """
        return self.mMode == QtColor.QtColorModeEnum.ARGB

    def isHSVA(self):
        """
        isHSVA()
        Check if the color is defined as an HSVA color

        :return: True if HSVA, False otherwise
        """
        return self.mMode == QtColor.QtColorModeEnum.AHSV

    def setColorRGBA(self, aColorRGBA):
        """
        setColorRGBA(aColorRGBA)
        Set the RGBA color with the provided values.
        R, G, B, and A component must be in the range [0;255]

        :param aColorRGBA: The RGBA color to set
        :type aColorRGBA: list of 4 int in the range [0;255]
        :return: nothing
        """
        self.mMode = QtColor.QtColorModeEnum.ARGB
        to16Bit = 65535.0/255.0
        self.mC1    = int(aColorRGBA[0] * to16Bit)
        self.mC2    = int(aColorRGBA[1] * to16Bit)
        self.mC3    = int(aColorRGBA[2] * to16Bit)
        self.mAlpha = int(aColorRGBA[3] * to16Bit)

    def setColorHSVA(self, aColorHSVA):
        """
        setColorHSVA(aColorHSVA)
        Set the HSV and Alpha color with the provided values.
        H component must be in the range [0;359]
        S, V, and A component must be in the range [0;255]

        :param aColorHSVA: The HSVA color to set
        :type aColorHSVA: list of 4 int. H in the range [0;359], S, V and A in the range [0;255]
        :return: nothing
        """
        self.mMode = QtColor.QtColorModeEnum.AHSV
        to16Bit = 65535.0 / 255.0
        self.mC1    = int(aColorHSVA[0] * 100.0) * 359.0 / 358.0
        self.mC2    = int(aColorHSVA[1] * to16Bit)
        self.mC3    = int(aColorHSVA[2] * to16Bit)
        self.mAlpha = int(aColorHSVA[3] * to16Bit)
