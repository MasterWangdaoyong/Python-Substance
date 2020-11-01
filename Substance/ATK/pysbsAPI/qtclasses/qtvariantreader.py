# coding: utf-8
"""
Module **qtvariantreader** provides the class QtVariantReader which allows the deserialization of a QVariant object.
"""
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import io
import struct
import base64

from pysbs.api_decorators import handle_exceptions
from pysbs import python_helpers
from .qtclasses import QtVariantTypeEnum, QtVariant, QtVariantMap


class QtVariantReader(object):
    """
    Class QtVariantReader allows to read (deserialize) a :class:`.QtVariant` object from a Byte Array or a base64 encoded string.
    """
    def __init__(self):
        self.mStream = None
        self.mVersion = None

    @handle_exceptions()
    def getFromByteArray(self, aByteArray, aType):
        """
        getFromByteArray(aByteArray, aType)
        Read the given byte array and return the included QtVariant which must be of the given type

        :param aByteArray: The byte array to read
        :type aByteArray: bytearray or str
        :param aType: Type of the QtVariant included in the byte array
        :type aType: :class:`.QtVariantTypeEnum`
        :return: The :class:`.QtVariant` object
        """
        self.mStream = io.BytesIO(aByteArray)
        aVersion = self.readInt()
        self.mVersion = aVersion
        return self.readQtVariantValue(aType)

    @handle_exceptions()
    def getFromBase64String(self, aEncodedString, aType):
        """
        getFromBase64String(aEncodedString, aType)
        Read the given base64 encoded string and return the included QtVariant which must be of the given type

        :param aEncodedString: The string to read
        :type aEncodedString: str
        :param aType: Type of the QtVariant included in the byte array
        :type aType: :class:`.QtVariantTypeEnum`
        :return: The :class:`.QtVariant` object
        """
        if python_helpers.isStringOrUnicode(aEncodedString):
            aByteArray = bytearray(aEncodedString, 'utf-8')
        else:
            aByteArray = aEncodedString
        aDecoded = base64.b64decode(aByteArray)
        aDecodedByteArray = bytearray(aDecoded)
        return self.getFromByteArray(aDecodedByteArray, aType)

    @staticmethod
    @handle_exceptions()
    def bytesToInt(aStr):
        """
        bytesToInt(aStr)
        Convert the given string in hexadecimal into an integer

        :param aStr: The string to convert
        :type aStr: bytes
        :return: The result of the conversion as an integer
        """
        return struct.unpack(str('>i'), aStr)[0]

    @staticmethod
    @handle_exceptions()
    def bytesToInt16(aStr):
        """
        bytesToInt16(aStr)
        Convert the given string in hexadecimal into an integer

        :param aStr: The string to convert
        :type aStr: bytes
        :return: The result of the conversion as an integer
        """
        return struct.unpack(str('>H'), aStr)[0]

    @staticmethod
    @handle_exceptions()
    def bytesToInt8(aStr):
        """
        bytesToInt8(aStr)
        Convert the given string in hexadecimal into an integer

        :param aStr: The string to convert
        :type aStr: bytes
        :return: The result of the conversion as an integer
        """
        return struct.unpack(str('>B'), aStr)[0]

    @staticmethod
    @handle_exceptions()
    def bytesToBool(aStr):
        """
        bytesToBool(aStr)
        Convert the given string in hexadecimal into a bool

        :param aStr: The string to convert
        :type aStr: bytes
        :return: The result of the conversion as a bool
        """
        return struct.unpack(str('>?'), aStr)[0]

    @staticmethod
    @handle_exceptions()
    def bytesToChar(aStr):
        """
        bytesToChar(aStr)
        Convert the given string in hexadecimal into a char

        :param aStr: The string to convert
        :type aStr: bytes
        :return: The result of the conversion as a char
        """
        return struct.unpack(str('>c'), aStr)[0].decode()

    @handle_exceptions()
    def readBool(self):
        """
        readBool()
        Read 1 bytes as a Boolean

        :return: The next boolean as a Boolean
        """
        aStr = self.mStream.read(1)
        return QtVariantReader.bytesToBool(aStr)

    @handle_exceptions()
    def readByteArray(self):
        """
        readByteArray()
        Read the next ByteArray

        :return: The ByteArray as a String
        """
        # Read the byte array size, then the string
        aArraySize = self.readInt()
        return self.mStream.read(aArraySize)

    @handle_exceptions()
    def readChar(self):
        """
        readChar()
        Read 1 bytes as a char

        :return: The next character as a string
        """
        aStr = self.mStream.read(1)
        return QtVariantReader.bytesToChar(aStr)

    @handle_exceptions()
    def readInt(self):
        """
        readInt()
        Read 4 bytes as an integer

        :return: The next integer as an Integer
        """
        aStr = self.mStream.read(4)
        return QtVariantReader.bytesToInt(aStr)

    @handle_exceptions()
    def readInt16(self):
        """
        readInt16()
        Read 2 bytes as an integer

        :return: The next integer as an Integer
        """
        aStr = self.mStream.read(2)
        return QtVariantReader.bytesToInt16(aStr)

    @handle_exceptions()
    def readInt8(self):
        """
        readInt8()
        Read 1 byte as an integer

        :return: The next integer as an Integer
        """
        aStr = self.mStream.read(1)
        return QtVariantReader.bytesToInt8(aStr)

    @handle_exceptions()
    def readDouble(self):
        """
        readDouble()
        Read 8 bytes as a double

        :return: The next double as an Double
        """
        aStr = self.mStream.read(8)
        return struct.unpack(str('>d'), aStr)[0]

    @handle_exceptions()
    def readString(self, aSize):
        """
        readString()
        Read aSize bytes as a string

        :return: The bytes as a String
        """
        aStr = ''
        for i in range(int(aSize / 2)):
            self.mStream.read(1)
            aStr += self.readChar()
        return aStr

    @handle_exceptions()
    def readStringList(self):
        """
        readStringList()
        Read the next string list

        :return: The string map as a list of string
        """
        # Read list size
        aListSize = self.readInt()
        aList = []
        # Read list items
        for i in range(aListSize):
            aString = self.readQtVariantString()
            aList.append(aString)

        return aList

    @handle_exceptions()
    def readQtVariantList(self):
        """
        readQtVariantList()
        Read the next variant list

        :return: The variant map as a list of QtVariant
        """
        # Read list size
        aListSize = self.readInt()
        aList = []
        # Read map items
        for i in range(aListSize):
            aQtVariant = self.readQtVariant()
            aList.append(aQtVariant)

        return aList

    @handle_exceptions()
    def readQtVariantMap(self):
        """
        readQtVariantMap()
        Read the next variant map

        :return: The variant map as a dictionary of QtVariant
        """
        # Read map size
        aMapSize = self.readInt()
        aMap = {}
        # Read map items
        for i in range(aMapSize):
            aKey = self.readKey()
            aQtVariant = self.readQtVariant()
            aMap[aKey] = aQtVariant

        aQtVariantMap = QtVariantMap(aMap=aMap)
        return aQtVariantMap

    @handle_exceptions()
    def readQtVariantString(self):
        """
        readQtVariantString()
        Read the next string

        :return: The bytes as a String
        """
        # Read the string size, then the string itself
        aStrSize = self.readInt()
        if aStrSize != -1:
            return self.readString(aStrSize)
        return ''

    @handle_exceptions()
    def readURL(self):
        """
        readURL()
        Read the next URL

        :return: The url as a string
        """
        # Read the Url size, then the Url itself
        aUrlSize = self.readInt()
        return self.mStream.read(aUrlSize)

    @handle_exceptions()
    def readSize(self):
        """
        readSize()
        Read the next size object

        :return: The size as a tuple(int width,int height)
        """
        # Read the size as a tuple of two int
        w = self.readInt()
        h = self.readInt()
        return w,h

    @handle_exceptions()
    def readKey(self):
        """
        readKey()
        Read the next key (=size of the key + string)

        :return: The key as a String
        """
        # Read the key size, then the key itself
        aKeySize = self.readInt()
        return self.readString(aKeySize)

    @handle_exceptions()
    def readQtVariant(self):
        """
        readQtVariant()
        Read the next variant item (=type + value)

        :return: The variant item as a QtVariant
        """
        # Read type
        aType = self.readInt()
        # Read one byte
        self.mStream.read(1)
        # Read value
        return self.readQtVariantValue(aType)

    @handle_exceptions()
    def readQtVariantValue(self, aType):
        """
        readQtVariantValue()
        Read the next variant item value, according to the given type

        :return: The variant item as a QtVariant
        """
        # Read value depending on type
        aValue = None
        if aType == QtVariantTypeEnum.BOOL:
            aValue = self.readBool()
        elif aType == QtVariantTypeEnum.INT:
            aValue = self.readInt()
        elif aType == QtVariantTypeEnum.DOUBLE:
            aValue = self.readDouble()
        elif aType == QtVariantTypeEnum.VARIANT_MAP:
            aValue = self.readQtVariantMap()
        elif aType == QtVariantTypeEnum.VARIANT_LIST:
            aValue = self.readQtVariantList()
        elif aType == QtVariantTypeEnum.STRING:
            aValue = self.readQtVariantString()
        elif aType == QtVariantTypeEnum.STRING_LIST:
            aValue = self.readStringList()
        elif aType == QtVariantTypeEnum.BYTE_ARRAY:
            aValue = self.readByteArray()
        elif aType == QtVariantTypeEnum.URL:
            aValue = self.readURL()
        elif aType == QtVariantTypeEnum.SIZE:
            aValue = self.readSize()
        else:
            log.error("Unsupported type: %s", str(aType))

        return QtVariant(aType=aType, aValue=aValue)
