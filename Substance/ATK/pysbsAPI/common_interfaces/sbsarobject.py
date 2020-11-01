# coding: utf-8
"""
Module **sbsarobject** provides the definition of a SBSARObject, the base class for all objects of a .sbsar package.
"""

from __future__ import unicode_literals
import abc
import re

from pysbs.api_decorators import handle_exceptions
from pysbs import python_helpers

class SBSARObject:
    """
    Abstract class used to provide a common interface for all derived SBSARObject,
    and to ensure that each derived object implements the function 'parse'
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        """
        parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        Parse recursively the given xml node to retrieve the content of the SBSObject.

        :param aContext: execution context
        :param aDirAbsPath: the absolute directory containing the current parsed package (.sbs file)
        :param aSBSParser: the substance parser
        :param aXmlNode: the xml node to parse
        :type aContext: :class:`.Context`
        :type aDirAbsPath: str
        :type aSBSParser: :class:`.SBSParser`
        :type aXmlNode: :class:`xml.etree.ElementTree`
        """
        pass

    @handle_exceptions()
    def _computeUniqueIdentifier(self, aIdentifier, aListsToCheck, aSuffixId=0):
        """
        _computeUniqueIdentifier(aIdentifier, aListsToCheck, aSuffixId=0)
        Parse the lists of object to find an object with the given identifier, and compute a unique identifier if it is not unique.

        :param aIdentifier:
        :param aListsToCheck: The list of lists of SBSObject that must be taken in account to ensure identifier uniqueness
        :type aIdentifier: str
        :type aListsToCheck: list of lists of :class:`.SBSObject`
        :return: A unique identifier in the context of the given lists. It can be the given aIdentifier, or aIdentifier_Suffix
        """
        if aSuffixId == 0:
            match = re.search(r'_[0-9]+$', aIdentifier)
            if match:
                aSuffix = aIdentifier[match.start():]
                aSuffixId = int(aSuffix[1:])
                aIdentifier = aIdentifier[0:match.start()]
            else:
                aSuffix = ''
        else:
            aSuffix = '_' + str(aSuffixId)
        aIdentifierToCheck = aIdentifier + aSuffix

        for aList, aObject in [(aList, aObject) for aList in aListsToCheck if aList is not None for aObject in aList]:
            if python_helpers.isStringOrUnicode(aObject):
                if aObject == aIdentifierToCheck:
                    return self._computeUniqueIdentifier(aIdentifier, aListsToCheck, aSuffixId + 1)
            elif aObject.mIdentifier == aIdentifierToCheck:
                return self._computeUniqueIdentifier(aIdentifier, aListsToCheck, aSuffixId + 1)

        return aIdentifierToCheck
