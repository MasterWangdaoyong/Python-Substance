# coding: utf-8
"""
Module **sbsscenedata** provides the definition of the :class:`.SubMeshColor` and :class:`.SubMeshSelection` objects.
"""
from __future__ import unicode_literals
import copy
from pysbs.api_decorators import handle_exceptions
from pysbs.sbscommon.values import SBSOption

from . import sbsbakersdictionaries as bakersdict
from .sbsbakersenum import *


class SubMeshColor:
    """
    Class that describe the color associated to a Scene object entity

    Members:
        * mEntityId   (int): entity index
        * mSubMeshId  (int): sub mesh index
        * mColor      (str): the hexadecimal color
    """
    def __init__(self, aEntityId=1, aSubMeshId=0, aColor='#ff0000'):
        self.mEntityId = aEntityId
        self.mSubMeshId = aSubMeshId
        self.mColor = aColor

    def fromSBSTree(self, aIndexColor, aSBSTree, removeUsedOptions=False):
        """
        fromSBSTree(aIndexColor, aSBSTree, removeUsedOptions=False)
        Get the content of the given SBSTree to set the SubMeshColor with the given id

        :param aIndexColor: Index of this submesh color in the options
        :param aSBSTree: The options tree to parse to build the Baking Converter
        :param removeUsedOptions: True to allow removing the options used to build this SubMeshColor from the given list. Default to False
        :type aIndexColor: int
        :type aSBSTree: :class:`.SBSTree`
        :type removeUsedOptions: bool, optional
        :return: True if success, False otherwise
        """
        if removeUsedOptions:       aOptions = aSBSTree
        else:                       aOptions = copy.copy(aSBSTree)

        aColorData = aOptions.getChildByName(str(aIndexColor))[0]
        aColor     = aColorData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SUBMESH_COLOR)).mValue
        aEntityId  = aColorData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.FIRST)).mValue
        aSubMeshId = aColorData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SECOND)).mValue
        if aEntityId is not None and aSubMeshId is not None and aColor is not None:
            self.mEntityId = int(aEntityId)
            self.mSubMeshId = int(aSubMeshId)
            self.mColor = aColor
            return True
        return False

    @handle_exceptions()
    def toSBSOptionList(self, aIndexColor):
        """
        toSBSOptionList(aIndexColor)
        Convert the SubMeshColor object into a list of SBSOptions, as it is saved in the .sbs file

        :param aIndexColor: Index of this color in the Baking Parameters
        :type aIndexColor: int
        :return: A list of :class:`.SBSOptions` object with the content of the SubMeshColor
        """
        optionPrefix = bakersdict.getBakingStructureTagName(BakingStructureTagEnum.BAKING)+'/'+\
                       bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MODEL)+'/'+\
                       bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SUBMESH_COLORS)+'/'+str(aIndexColor)+'/'
        aSBSOptionList = list()
        aSBSOptionList.append(SBSOption(aName = optionPrefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SUBMESH_COLOR),
                                     aValue= self.mColor))
        aSBSOptionList.append(SBSOption(aName = optionPrefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.FIRST),
                                     aValue= str(self.mEntityId)))
        aSBSOptionList.append(SBSOption(aName = optionPrefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SECOND),
                                     aValue= str(self.mSubMeshId)))
        return aSBSOptionList

    @handle_exceptions()
    def getColorHexa(self):
        """
        getColorHexa()
        Get the hexadecimal color of this SubMeshColor

        :return: The hexadecimal color as a string if it exists, None otherwise
        """
        return self.mColor

    @handle_exceptions()
    def setColorHexa(self, aColor):
        """
        setColorHexa(aColor)
        Set the given hexadecimal color

        :param aColor: The hexadecimal color
        :type aColor: str
        """
        self.mColor = aColor


class SubMeshSelection:
    """
    Class that describe a Scene selection

    Members:
        * mEntityId   (int): entity index
        * mSubMeshId  (int): sub mesh index
    """
    def __init__(self, aEntityId=1, aSubMeshId=0):
        self.mEntityId = aEntityId
        self.mSubMeshId = aSubMeshId

    def fromSBSTree(self, aIndexSelection, aSBSTree, removeUsedOptions=False):
        """
        fromSBSTree(aColorIndex, aSBSTree, removeUsedOptions=False)
        Get the content of the given SBSTree to set the SubMeshSelection with the given id

        :param aIndexSelection: Index of this submesh selection in the options
        :param aSBSTree: The options to parse to build the Baking Converter
        :param removeUsedOptions: True to allow removing the options used to build this SubMeshColor from the given list. Default to False
        :type aIndexSelection: int
        :type aSBSTree: :class:`.SBSTree`
        :type removeUsedOptions: bool, optional
        :return: True if success, False otherwise
        """
        if removeUsedOptions:       aOptions = aSBSTree
        else:                       aOptions = copy.copy(aSBSTree)

        aSelData = aOptions.getChildByName(str(aIndexSelection))[0]
        aEntityId = aSelData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.FIRST)).mValue
        aSubMeshId = aSelData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SECOND)).mValue

        if aEntityId is not None and aSubMeshId is not None:
            self.mEntityId = aEntityId
            self.mSubMeshId = aSubMeshId
            return True
        return False

    @handle_exceptions()
    def toSBSOptionList(self, aIndexSelection):
        """
        toSBSOptionList(aIndexSelection)
        Convert the SubMeshSelection object into a list of SBSOptions, as it is saved in the .sbs file

        :param aIndexSelection: Index of this selection in the Baking Parameters
        :type aIndexSelection: int
        :return: A list of :class:`.SBSOptions` object with the content of the SubMeshSelection
        """
        optionPrefix = bakersdict.getBakingStructureTagName(BakingStructureTagEnum.BAKING)+'/'+\
                       bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MODEL)+'/'+\
                       bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SELECTIONS)+'/'+str(aIndexSelection)+'/'
        aSBSOptionList = list()
        aSBSOptionList.append(SBSOption(aName = optionPrefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.FIRST),
                                     aValue= str(self.mEntityId)))
        aSBSOptionList.append(SBSOption(aName = optionPrefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SECOND),
                                     aValue= str(self.mSubMeshId)))
        return aSBSOptionList
