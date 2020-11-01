# coding: utf-8
"""
Module **qtvariantwriter** provides the class QtVariantWriter which allows the serialization of a QVariant object.
"""
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import io
import struct
import base64

from pysbs.api_decorators import handle_exceptions
from pysbs import python_helpers
from .qtclasses import QtVariantTypeEnum


class QtVariantWriter(object):
    """
    Class QtVariantWriter allows to write (serialize) a :class:`.QtVariant` object into a Byte Array or a base64 encoded string.
    """
    def __init__(self):
        self.mStream = io.BytesIO()
        self.mVersion = 17

    def toByteArrayString(self, aQtVariant):
        """
        toByteArrayString(aVariant)
        Write the given QtVariant object into a byte array.

        :param aQtVariant: The QtVariant object to write in a ByteArray string
        :type aQtVariant: :class:`.QtVariant`
        :return: The bytearray string
        """
        # Write version
        self.writeInt(self.mVersion)
        # Write all content
        self.writeQtVariantValue(aQtVariant)
        # Get result and close stream
        self.mStream.flush()
        val = self.mStream.getvalue()
        self.mStream.close()
        return val

    def toBase64String(self, aQtVariant):
        """
        toBase64String(aQtVariant)
        Write the given QtVariant object into a base64 encoded string.

        :param aQtVariant: The QtVariant object to write in a base64 string
        :type aQtVariant: :class:`.QtVariant`
        :return: The base64 encoded string
        """
        aBytes = self.toByteArrayString(aQtVariant)
        aByteArray = bytearray(aBytes)
        aEncoded = base64.b64encode(aByteArray)
        if not python_helpers.isStringOrUnicode(aEncoded):
            aEncoded = aEncoded.decode()
        return aEncoded

    @staticmethod
    def boolToBytes(aBool):
        """
        boolToBytes(aBool)
        Convert the given boolean into in bytes

        :param aBool: The boolean to convert into bytes
        :type aBool: bool
        :return: the result of the conversion as a string
        """
        return struct.pack(str('>?'), aBool)

    @staticmethod
    def charToBytes(aChar):
        """
        charToBytes(aChar)
        Convert the given character in bytes

        :param aChar: The character to convert into bytes
        :type aChar: char
        :return: the result of the conversion as a string
        """
        return struct.pack(str('>c'), aChar.encode())

    @staticmethod
    def int8ToBytes(aInt):
        """
        int8ToBytes(aInt)
        Convert the given integer into in bytes

        :param aInt: The integer to convert into bytes
        :type aInt: integer
        :return: the result of the conversion as a string
        """
        return struct.pack(str('>B'), aInt)

    @staticmethod
    def int16ToBytes(aInt):
        """
        int16ToBytes(aInt)
        Convert the given integer into in bytes

        :param aInt: The integer to convert into bytes
        :type aInt: integer
        :return: the result of the conversion as a string
        """
        return struct.pack(str('>H'), aInt)

    @staticmethod
    def int32ToBytes(aInt):
        """
        int32ToBytes(aInt)
        Convert the given integer into in bytes

        :param aInt: The integer to convert into bytes
        :type aInt: integer
        :return: the result of the conversion as a string
        """
        return struct.pack(str('>i'), aInt)

    @staticmethod
    def doubleToBytes(aDouble):
        """
        doubleToBytes(aDouble)
        Convert the given double into in bytes

        :param aDouble: The double to convert into bytes
        :type aDouble: double
        :return: the result of the conversion as a string
        """
        return struct.pack(str('>d'), aDouble)

    @handle_exceptions()
    def writeBool(self, aBool):
        """
        writeBool(aBool)
        Write the given Boolean into 1 byte

        :param aBool: The boolean to write
        :type aBool: bool
        """
        aStr = QtVariantWriter.boolToBytes(aBool)
        self.mStream.write(aStr)

    @handle_exceptions()
    def writeByteArray(self, aByteArray):
        """
        writeByteArray(aByteArray)
        Write the given ByteArray with its size

        :param aByteArray: The ByteArray to write
        :type aByteArray: ByteArray
        """
        # Write the byte array size, the content itself
        self.writeInt(len(aByteArray))
        if not isinstance(aByteArray, bytes):
            aByteArray = aByteArray.encode()
        self.mStream.write(aByteArray)

    @handle_exceptions()
    def writeChar(self, aChar):
        """
        writeChar(aChar)
        Write the given char into 1 byte

        :param aChar: The character to write
        :type aChar: char
        """
        aStr = QtVariantWriter.charToBytes(aChar)
        self.mStream.write(aStr)

    @handle_exceptions()
    def writeDouble(self, aDouble):
        """
        writeDouble(aDouble)
        Write the given double into 8 bytes

        :param aDouble: The double to write
        :type aDouble: double
        """
        aStr = QtVariantWriter.doubleToBytes(aDouble)
        self.mStream.write(aStr)

    @handle_exceptions()
    def writeInt(self, aInt):
        """
        writeInt(aInt)
        Write the given integer into 4 bytes

        :param aInt: The integer to write
        :type aInt: integer
        """
        aStr = QtVariantWriter.int32ToBytes(aInt)
        self.mStream.write(aStr)

    @handle_exceptions()
    def writeInt16(self, aInt):
        """
        writeInt16(aInt)
        Write the given integer into 2 bytes

        :param aInt: The integer to write
        :type aInt: integer
        """
        aStr = QtVariantWriter.int16ToBytes(aInt)
        self.mStream.write(aStr)

    @handle_exceptions()
    def writeInt8(self, aInt):
        """
        writeInt8(aInt)
        Write the given integer into 1 byte

        :param aInt: The integer to write
        :type aInt: integer
        """
        aStr = QtVariantWriter.int8ToBytes(aInt)
        self.mStream.write(aStr)

    @handle_exceptions()
    def writeQtVariantList(self, aList):
        """
        writeQtVariantList(aList)
        Write the given variant list

        :param aList: The variant list to write
        :type aList: list of :class:`.QtVariant`
        """
        # Write list size
        self.writeInt(len(aList))

        # Write list items
        for aItem in aList:
            self.writeQtVariant(aItem)

    @handle_exceptions()
    def writeQtVariantMap(self, aMap):
        """
        writeQtVariantMap(aMap)
        Write the given variant map

        :param aMap: The variant map to write
        :type aMap: :class:`.QtVariantMap`
        """
        # Write map size
        self.writeInt(aMap.getSize())

        # Write map items
        for aKey,aItem in sorted(aMap.mMap.items(), reverse=True):
            self.writeQtVariantString(aKey)
            self.writeQtVariant(aItem)

    @handle_exceptions()
    def writeQtVariantString(self, aStr):
        """
        writeQtVariantString(aStr)
        Write the given string with its size

        :param aStr: The string to write
        :type aStr: str
        """
        if len(aStr) == 0:
            self.writeInt(-1)
        else:
            # Write string size
            self.writeInt(2*len(aStr))
            # Write string
            self.writeString(aStr)

    @handle_exceptions()
    def writeURL(self, aURL):
        """
        writeURL(aURL)
        Write the given URL with its size

        :param aURL: The url to write
        :type aURL: str
        """
        # Write the Url size, then the Url itself
        self.writeInt(len(aURL))
        if not isinstance(aURL, bytes):
            aURL = aURL.encode()
        self.mStream.write(aURL)

    @handle_exceptions()
    def writeSize(self, aSize):
        """
        writeSize(aSize)
        Write the given size

        :param aSize: The size to write
        :type aSize: tuple of two int
        """
        # Write the size
        self.writeInt(aSize[0])
        self.writeInt(aSize[1])

    @handle_exceptions()
    def writeString(self, aStr):
        """
        writeString(aStr)
        Write the given string into 2*len(aStr) bytes

        :param aStr: The string to write
        :type aStr: string
        """
        aRes = b''
        for aChar in aStr:
            aRes += b'\x00'
            aRes += QtVariantWriter.charToBytes(aChar)
        self.mStream.write(aRes)

    @handle_exceptions()
    def writeStringList(self, aStringList):
        """
        writeStringList(aStringList)
        Write the given string list

        :param aStringList: The list of strings to write
        :type aStringList: list of string
        """
        # Write list size
        self.writeInt(len(aStringList))

        # Write list items
        for aStr in aStringList:
            self.writeQtVariantString(aStr)

    @handle_exceptions()
    def writeQtVariant(self, aQtVariant):
        """
        writeQtVariant(aQtVariant)
        Write the given variant item (=type + value)

        :param aQtVariant: The variant object to write
        :type aQtVariant: :class:`.QtVariant`
        """
        # Write type
        self.writeInt(aQtVariant.mType)
        # Write one null byte
        self.mStream.write(b'\x00')
        # Write value
        self.writeQtVariantValue(aQtVariant)

    @handle_exceptions()
    def writeQtVariantValue(self, aQtVariant):
        """
        writeQtVariantValue(aQtVariant)
        Write the given variant item value, according to the given type

        :param aQtVariant: The object to write
        :type aQtVariant: :class:`.QtVariant`
        """
        # Write value depending on type
        if aQtVariant.mType == QtVariantTypeEnum.BOOL:
            self.writeBool(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.INT:
            self.writeInt(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.DOUBLE:
            self.writeDouble(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.VARIANT_MAP:
            self.writeQtVariantMap(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.VARIANT_LIST:
            self.writeQtVariantList(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.STRING:
            self.writeQtVariantString(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.STRING_LIST:
            self.writeStringList(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.BYTE_ARRAY:
            self.writeByteArray(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.URL:
            self.writeURL(aQtVariant.mValue)
        elif aQtVariant.mType == QtVariantTypeEnum.SIZE:
            self.writeSize(aQtVariant.mValue)
        else:
            log.error("Unsupported type: %s", str(aQtVariant.mType))
