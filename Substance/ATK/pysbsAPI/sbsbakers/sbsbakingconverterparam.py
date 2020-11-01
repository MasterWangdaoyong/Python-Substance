# coding: utf-8
"""
Module **sbsbakingconverterparam** provides the definition of the BakingConverterParam object.
"""
from __future__ import unicode_literals
import abc

from pysbs.api_decorators import doc_inherit
from pysbs import api_helpers
from pysbs import qtclasses
from pysbs.sbscommon.values import SBSOption

from . import sbsbakersdictionaries
from .sbsbakersenum import ConverterParamEnum


class BakingParam(object):
    """
    This class provide the common interface for BakingConverterParam and BakingGlobalParam

    Members
        * mIdentifier (:class:`.ConverterParamEnum`): identifier of the property
        * mQtVariant (:class:`.QtVariant`): value of the property (type + value)
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, aIdentifier, aQtVariant):
        super(BakingParam, self).__init__()
        self.mIdentifier = aIdentifier
        self.mQtVariant = aQtVariant

    def getType(self):
        """
        getType()
        Get the type of the :class:`.QtVariant` object

        :return: The type of the :class:`.QtVariant` object, as a :class:`.QtVariantTypeEnum`
        """
        return self.mQtVariant.mType

    def getValue(self):
        """
        getValue()
        Get the value of the :class:`.QtVariant` object

        :return: The value of the :class:`.QtVariant` object
        """
        return self.mQtVariant.getValue()

    def getValueStr(self):
        """
        getValueStr()
        Get the value of the :class:`.QtVariant` object converted into a string

        :return: The value of the :class:`.QtVariant` object as a string
        """
        return self.mQtVariant.getValueStr()

    def setValue(self, aValue):
        """
        setValue(aValue)
        Set the value of the :class:`.QtVariant` object

        :param aValue: The value to set
        :type aValue: any type compatible with the type of the :class:`.QtVariant` object
        """
        self.mQtVariant.setValue(aValue)

    def isAResourceParam(self):
        """
        isAResourceParam()
        Return True if this BakingConverterParam is a resource parameter (e.g. Normal map, Texture file, Direction file, Cage file) with a type STRING.

        :return: True if it is a resource parameter, False otherwise
        """
        aResourceParamList = [ConverterParamEnum.MESH__CAGE_PATH,
                              ConverterParamEnum.MESH__SKEW_PATH,
                              ConverterParamEnum.ADDITIONAL__NORMAL_MAP,
                              ConverterParamEnum.DETAIL_TEXTURE__TEXTURE_FILE,
                              ConverterParamEnum.WORLD_DIRECTION__DIRECTION_MAP]
        #TODO: Add skew map?
        return self.mIdentifier in aResourceParamList and self.getType() == qtclasses.QtVariantTypeEnum.STRING


    def fromSBSTree(self, aOptionPrefix, aSBSTree):
        """
        fromSBSTree(aOptionPrefix, aSBSTree)
        Read options from aSBSTree

        :param aOptionPrefix: the option prefix
        :param aSBSTree: the tree of options
        :type aOptionPrefix: str
        :type aSBSTree: :class:`.SBSTree`
        :return: True if success, False otherwise
        """
        pass

    def toSBSOptionList(self, aOptionPrefix):
        """
        toSBSOptionList(aOptionPrefix)
        Convert this property into a list of SBSOption.

        :param aOptionPrefix: the option prefix
        :type aOptionPrefix: str
        :return: a list of :class:`.SBSOption` allowing to fully declare this parameter
        """
        pass

@doc_inherit
class BakingConverterParam(BakingParam):
    """
    This class provide the definition of a BakingConverterParam

    Members
        * mIdentifier (:class:`.ConverterParamEnum`): identifier of the property
        * mQtVariant (:class:`.QtVariant`): value of the property (type + value)
    """
    def __init__(self, aIdentifier, aQtVariant):
        super(BakingConverterParam, self).__init__(aIdentifier, aQtVariant)

    def toSBSOptionList(self, aOptionPrefix):
        """
        toSBSOptionList(aOptionPrefix)
        Convert this property into a tree of options.

        :param aOptionPrefix: the option prefix
        :type aOptionPrefix: str
        :return: a list of :class:`.SBSOption` allowing to fully declare this parameter
        """
        aOptionPrefix += 'value'

        # Particular case of string list: indicate the size of the list
        if self.getType() == qtclasses.QtVariantTypeEnum.STRING_LIST:
            stringList = self.getValue()
            aOptionList = []
            # If the list is not empty, create each item with an option 'prefix/value/x/itemName'
            if len(stringList) > 0:
                aItemTag = sbsbakersdictionaries.getConverterParamName(self.mIdentifier+1)
                for i, aString in enumerate(stringList):
                    aOptionList.append(SBSOption(aName=aOptionPrefix+str(i)+'/'+aItemTag, aValue=stringList[i]))
                aOptionList.append(SBSOption(aName=aOptionPrefix+'/size', aValue=str(len(stringList))))

            return aOptionList

        # Build an option with 'prefix/value' and the parameter value as a string
        else:
            aValue = self.getValueStr()
            # In case of an empty string, do not create an option
            if self.getType() == qtclasses.QtVariantTypeEnum.STRING or \
                self.getType() == qtclasses.QtVariantTypeEnum.URL  or \
                self.getType() == qtclasses.QtVariantTypeEnum.SIZE:
                if not aValue:
                    return []
            return [SBSOption(aName=aOptionPrefix, aValue=aValue)]


@doc_inherit
class BakingGlobalParam(BakingParam):
    """
    This class provide the definition of a property of a Global Baking parameter

    Members
        * mIdentifier (:class:`.ConverterParamEnum`): identifier of the property
        * mQtVariant (:class:`.QtVariant`): value of the property (type + value)
    """
    def __init__(self, aIdentifier, aQtVariant):
        super(BakingGlobalParam, self).__init__(aIdentifier, aQtVariant)

    def fromSBSTree(self, aOptionPrefix, aSBSTree):
        """
        fromSBSTree(aOptionPrefix, aSBSOptions)
        Search in the given SBSOptions the entries that allow initializing this property.

        :param aOptionPrefix: the option prefix
        :param aSBSTree: the list of options
        :type aOptionPrefix: str
        :type aSBSTree: :class:`.SBSTree`
        :return: True if success, False otherwise
        """
        # Particular case of string list: get the size of the list
        if self.getType() == qtclasses.QtVariantTypeEnum.STRING_LIST:
            aOptionPrefix += sbsbakersdictionaries.getGlobalParamName(self.mIdentifier) + '/'
            nbItem = api_helpers.popOption(aOptionPrefix + 'size', aSBSTree)
            # If the list is not empty, get each item with the option name 'prefix/paramName/x/itemName'
            if nbItem is not None and int(nbItem) > 0:
                aStringList = []
                aItemTag = sbsbakersdictionaries.getGlobalParamName(self.mIdentifier+1)
                for i in range(1, int(nbItem)+1):
                    optName = aOptionPrefix + str(i) + '/' + aItemTag
                    option = api_helpers.popOption(optName, aSBSTree)
                    if option is not None:
                        aStringList.append(option)
                self.setValue(aStringList)
                return True
        # All other cases, search for the option 'prefix/paramName'
        else:
            optName = aOptionPrefix + sbsbakersdictionaries.getGlobalParamName(self.mIdentifier)
            option = api_helpers.popOption(optName, aSBSTree)
            if option is not None:
                self.setValue(option)
                return True

        return False

    def fromSBSTree(self, aTree):
        """
        fromSBSTree(aTree)
        Initialize the baking settings from the given tree.

        :param aTree: the tree of options
        :type aTree: tree of options of :class:`.SBSTree`
        :return: True if success, False otherwise
        """
        # Move in the tree to find the right child
        optName = sbsbakersdictionaries.getConverterParamName(self.mIdentifier)
        option = aTree.getChildByPath(optName)
        if not option:
            return False

        # Particular case of string list: get the size of the list
        if self.getType() == qtclasses.QtVariantTypeEnum.STRING_LIST:
            elements = option.mElements[0].mTreeElements
            if len(elements) > 0:
                aStringList = []
                for i in elements:
                    if option is not None:
                        aStringList.append(option.mName)
                self.setValue(aStringList)
                return True
        # All other cases, search for the option 'prefix/paramName'
        else:
            self.setValue(option.mValue)
            return True
        return False


    def toSBSOptionList(self, aOptionPrefix):
        """
        toSBSOptionList(aOptionPrefix)
        Convert this property into am options tree.

        :param aOptionPrefix: the option prefix
        :type aOptionPrefix: str
        :return: a list of :class:`.SBSOption` allowing to fully declare this parameter
        """
        # Particular case of string list: indicate the size of the list
        if self.getType() == qtclasses.QtVariantTypeEnum.STRING_LIST:
            stringList = self.getValue()
            aOptionPrefix += sbsbakersdictionaries.getConverterParamName(self.mIdentifier) + '/'
            # If the list is not empty, create each item with an option 'prefix/paramName/x/itemName'
            if len(stringList) > 0:
                aOptionList = []
                aItemTag = sbsbakersdictionaries.getConverterParamName(self.mIdentifier+1)
                for i, aString in enumerate(stringList):
                    aOptionList.append(SBSOption(aName=aOptionPrefix+str(i+1)+'/'+aItemTag, aValue=stringList[i]))
                aOptionList.append(SBSOption(aName=aOptionPrefix+'size', aValue=str(len(stringList))))
            else:
                aOptionList = [SBSOption(aName=aOptionPrefix + 'size', aValue='-1')]

            return aOptionList

        # Build an option with 'prefix/paramName' and the parameter value as a string
        else:
            # In case of an empty string, do not create an option
            if self.getType() == qtclasses.QtVariantTypeEnum.STRING or \
                self.getType() == qtclasses.QtVariantTypeEnum.URL  or \
                self.getType() == qtclasses.QtVariantTypeEnum.SIZE:
                if not self.getValue():
                    return []
            return [SBSOption(aName=aOptionPrefix + sbsbakersdictionaries.getConverterParamName(self.mIdentifier),
                              aValue=self.getValueStr())]
