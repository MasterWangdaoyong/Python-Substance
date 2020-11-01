# coding: utf-8
"""
Module **sbsobject** provides the definition of a SBSObject, the base class for all objects of a .sbs package.
"""

from __future__ import unicode_literals
import abc
import time
import ctypes
from collections import OrderedDict

from pysbs.api_decorators import handle_exceptions
from pysbs import python_helpers, api_helpers
from .sbsarobject import SBSARObject

# ==============================================================================
class SBSObject(SBSARObject):
    """
    Abstract class used to provide a common interface for all derived SBSObjects,
    and to ensure that each derived object implements the functions 'parse' and 'write'
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(SBSObject, self).__init__()
        self.mMembersForEquality = []

    def equals(self, other):
        """
        equals(other)
        Check if this SBSObject is equivalent to the other SBSObject.
        Some members may be excluded from this check, the UIDs or GUILayout for instance.

        :param other: The :class:`.SBSObject` to compare to
        :type other: :class:`.SBSObject`
        :return: True if the two :class:`.SBSObject` are similar according to their definition.
        """
        if not type(self) is type(other):
            return False
        for aMember in self.mMembersForEquality:
            if hasattr(self, aMember) != hasattr(other, aMember):
                return False
            try:
                if not SBSObject.__areEqual(getattr(self, aMember), getattr(other, aMember)):
                    return False
            except:
                continue
        return True

    @abc.abstractmethod
    def write(self, aSBSWriter, aXmlNode):
        """
        write(aSBSWriter, aXmlNode)
        Write recursively the content of the SBSObject into the given xml node.

        :param aSBSWriter: the substance writer
        :param aXmlNode: the xml node to fill
        :type aSBSWriter: :class:`.SBSWriter`
        :type aXmlNode: :class:`xml.etree.ElementTree`
        """
        pass

    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Check if the given uid is already used in the context of this SBSObject.

        :param aUID: UID to check
        :type aUID: str
        :return: True if the uid is already used, False otherwise
        :raise: AttributeError if the function getUidIsUsed in not properly overloaded on this SBSObject
        """
        raise AttributeError('Method getUidIsUsed must be defined on a derived SBSObject when necessary')

    #==========================================================================
    # Private
    #==========================================================================
    @staticmethod
    def __areEqual(one, other):
        """
        Test if the two given objects are similar, depending on their type.

        :param one: First object
        :param other: Second object
        :return: True if they are similar, False otherwise
        """
        # Compare types first
        if not type(one) is type(other) and not (python_helpers.isStringOrUnicode(one) and python_helpers.isStringOrUnicode(other)):
            return False

        # SBSObject comparison
        if isinstance(one, SBSObject):
            return one.equals(other)

        # List comparison: check length first and then compare each element in the same order
        elif isinstance(one, list):
            if len(one) != len(other):
                return False
            if len(one) > 0 and isinstance(one[0], SBSObject):
                for i in range(0, len(one)):
                    if not one[i].equals(other[i]):
                        return False
                return True

        # String comparison
        elif python_helpers.isStringOrUnicode(one):
            # Ensure being in unicode
            if python_helpers.UNICODE_EXISTS:
                one = unicode(one)
                other = unicode(other)

            # Remove the UID of the dependency tag to avoid comparing UIDs
            one,oneDep = api_helpers.splitPathAndDependencyUID(one)
            other,otherDep = api_helpers.splitPathAndDependencyUID(other)

            if oneDep is None and otherDep is None:
                # Remove the UID part following NODE? to avoid comparing UIDs
                if one.startswith('NODE?') and other.startswith('NODE?'):
                    one = one[0:5]
                    other = other[0:5]

                # Try converting to float and round the value to avoid inequality due to different number of decimals in the strings
                one = api_helpers.tryConversionToFloat(one)
                other = api_helpers.tryConversionToFloat(other)
        elif isinstance(one, OrderedDict):
            if len(one) != len(other):
                return False
            for k, v in one.items():
                if not v.equals(other[k]):
                    return False
            return True

        return one == other


class UIDGenerator:
    """
    Class used to generate unique ID for new :class:`.SBSObjects`, in the context of their parent.
    """
    _sOffset = 0xF39AC68F

    @staticmethod
    @handle_exceptions()
    def generateUID(aSBSObject):
        """
        generateUID(aSBSObject)
        Generate a unique 10-digit UID in the context of the given :class:`.SBSObject`

        :param aSBSObject: the SBSObject in which the new uid must be unique
        :type aSBSObject: :class:`.SBSObject`
        :return: The UID, as a string
        """
        aUID = UIDGenerator.__generateUID()
        while aSBSObject.getUidIsUsed(str(aUID)) or aUID == 0:
            aUID += (UIDGenerator.__generateUID())&0xFF

        return str(aUID)

    #==========================================================================
    # Private
    #==========================================================================
    @staticmethod
    def __generateUID():
        """
        __generateUID()
        Generate a 10-digit UID

        :return: The UID
        """
        nowTime = int(time.time())
        aTmp = nowTime + UIDGenerator._sOffset
        aUID = ctypes.c_uint32(aTmp)
        UIDGenerator._sOffset = ctypes.c_ulong(UIDGenerator._sOffset + 1).value

        return aUID.value
