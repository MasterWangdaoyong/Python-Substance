# coding: utf-8

"""
Module sbsparser provides the class SBSParser which allows the deserialization of a .sbs file into a :class:`.SBSDocument`

All derived :class:`.SBSObject` have a *parse* function with the same signature than on the base class
:class:`.SBSObject`: :func:`common_interface.SBSObject.parse`
"""
from __future__ import unicode_literals
import os
import logging
log = logging.getLogger(__name__)

import xml.etree.ElementTree as ET
from pysbs import python_helpers
from pysbs.api_decorators import doc_source_code_enum

@doc_source_code_enum
class FileTypeEnum():
    """
    Enumeration of different document types SBSParser can read
    """
    SBS    = 0
    SBSAR  = 1
    SBSPRS = 2
    SBSPRJ = 3

# ==============================================================================
class SBSParser:
    """
    Class used to provide useful functions when parsing a .sbs (=xml) file
    """
    def __init__(self, aFileAbsPath, aContext, aFileType = FileTypeEnum.SBS):
        self.mFileAbsPath = aFileAbsPath
        self.mContext = aContext
        self.mXmlRoot = None
        self.mFileType = aFileType
        self.mIsValid = False

        try:
            tree = ET.parse(self.mFileAbsPath)
            self.mXmlRoot = tree.getroot()
            self.mIsValid = self.isValid()
        except BaseException as error:
            msg = 'Failed to parse '+ python_helpers.castStr(aFileAbsPath) + '\n' + python_helpers.getErrorMsg(error)
            raise ET.ParseError(msg)


    def getRootNode(self):
        """
        Get the .sbs file root node
        :return: element of type etree
        """
        return self.mXmlRoot

    def getAllXmlElementsUnder(self, aXmlElement, aTagName):
        """
        Get the xmlElements with the given tagName under the given xmlElement:

        <xmlElement><tagname>...</tagname><tagname>...</tagname>...</xmlElement>

        :return: A list of xmlElement
        """
        children = []
        for xmlElmtChild in aXmlElement:
            if xmlElmtChild.tag == aTagName:
                children.append(xmlElmtChild)

        return children

    def getXmlElementAttribValue(self, aXmlElement, aAttributeName):
        """
        Get the value of the attribute with the given name on the given xmlElement:

        <xmlElement attributeName=""/>

        :return: The attribute value
        """
        if aXmlElement is None:
            return None
        return aXmlElement.get(aAttributeName)

    def getXmlElementVAttribValue(self, aXmlElementParent, aChildName):
        """
        Get the value of the attribute 'v' on the given child element under xmlElementParent:

        <xmlElementParent><childName v=""/> ... </xmlElementParent>

        :return: The attribute value
        """
        if aXmlElementParent is None:
            return None
        child = aXmlElementParent.find(aChildName)
        if child is None:
            return None
        return self.getXmlElementAttribValue(child, 'v')

    def getXmlFilePathValue(self, aXmlElementParent, aChildName):
        """
        Get the value of the attribute 'v' on the given child element under xmlElementParent:
        <xmlElementParent><childName v=""/> ... </xmlElementParent>
        Then convert attribute path given as a relative path.
        :return: The attribute value
        """
        aFilePath = self.getXmlElementVAttribValue(aXmlElementParent, aChildName)
        aAliasMgr = self.mContext.getUrlAliasMgr()
        if not aFilePath or aFilePath == '?himself':
            return aFilePath
        aRelPath = aAliasMgr.toRelPath(aFilePath, os.path.dirname(self.mFileAbsPath))
        return aRelPath

    def getSBSElementList(self, aContext, aDirAbsPath, aXmlNode, aTagName, aChildTagName, aSBSClass):
        """
        Search for all children with the tag childtagname under the tag tagname under the given xmlNode, and parse them recursively:

        <xmlNode><tagname><childtagname>...</childtagname><childtagname>...</childtagname>... </tagname></xmlNode>

        :return: The list of SBS objects corresponding to the tag childtagname, or [] if not found
        """
        aSBSObjectList = []

        if aXmlNode is None or aSBSClass is None:
            return aSBSObjectList

        aSubNode = aXmlNode.find(aTagName)
        if aSubNode is None:
            return None

        aSBSObjectList = self.getAllSBSElementsIn(aContext, aDirAbsPath, aSubNode, aChildTagName, aSBSClass)
        return aSBSObjectList or []

    def getAllSBSElementsIn(self, aContext, aDirAbsPath, aXmlNode, aTagName, aSBSClass):
        """
        Search for all children with the given tag under the given xmlNode, and parse them recursively

        <xmlNode><tagname>...</tagname><tagname>...</tagname>...</xmlNode>

        :return: The list of SBS objects corresponding to the given tag, or [] if not found
        """
        aSBSObjectList = []

        if aXmlNode is None or aSBSClass is None:
            return aSBSObjectList

        xmlElmtObjectList = self.getAllXmlElementsUnder(aXmlNode, aTagName)
        if xmlElmtObjectList is None:
            return aSBSObjectList

        try:
            for xmlElmtObject in xmlElmtObjectList:
                aSBSObject = aSBSClass()
                aSBSObject.parse(aContext, aDirAbsPath, self, xmlElmtObject)
                aSBSObjectList.append(aSBSObject)
        except AttributeError:
            log.error('[SBSParser.getAllSBSElementsIn] Missing method parse on SBSObject: %s ', aSBSClass.__name__)

        return aSBSObjectList if aSBSObjectList else None

    def getSBSElementIn(self, aContext, aDirAbsPath, aXmlNode, aTagName, aSBSClass):
        """
        Search for first child with the given tag under the given xmlNode, and parse them recursively

        <xmlNode><tagname>...</tagname><tagname>...</tagname>...</xmlNode>

        :return: SBS object corresponding to the given tag, or None if not found
        """
        aSBSObject = None

        if aXmlNode is None or aSBSClass is None:
            return aSBSObject

        xmlElmtObjectList = self.getAllXmlElementsUnder(aXmlNode, aTagName)
        if not xmlElmtObjectList:
            return aSBSObject

        try:
            xmlElmtObject = xmlElmtObjectList[0]
            aSBSObject = aSBSClass()
            aSBSObject.parse(aContext, aDirAbsPath, self, xmlElmtObject)
            aSBSObject = aSBSObject
        except AttributeError:
            log.error('[SBSParser.getAllSBSElementsIn] Missing method parse on SBSObject: %s ', aSBSClass.__name__)

        return aSBSObject if aSBSObject else None

    def isValid(self):
        """
        Check if the package is valid

        :return: True if the package is valid, False otherwise
        """
        if self.mFileType == FileTypeEnum.SBSAR:
            return self.__isValidSBSAR()
        elif self.mFileType == FileTypeEnum.SBSPRS:
            return self.__isValidSBSPRS()
        elif self.mFileType == FileTypeEnum.SBSPRJ:
            return self.__isValidSBSPRJ()
        else:
            return self.__isValidSBS()

    def parseSBSNode(self, aContext, aDirAbsPath, aXmlNode, aTagName, aSBSClass):
        """
        Search for a child node with the given tag in the given XmlNode, and parse the corresponding SBS object

        :return: the SBSObject parsed, or None if not found
        """
        aSubNode = aXmlNode.find(aTagName)
        if aSubNode is None:
            return None

        aSBSObject = aSBSClass()

        try:
            aSBSObject.parse(aContext, aDirAbsPath, self, aSubNode)
        except AttributeError:
            log.error('[SBSParser.parseSBSNode] Missing method parse on SBSObject: %s ', aSBSClass.__name__)
            return None

        return aSBSObject


    def parseSBSNodeFromXmlNode(self, aContext, aDirAbsPath, aXmlNode, aSBSClass):
        """
        Search for a child node with the given tag in the given XmlNode, and parse the corresponding SBS object

        :return: the SBSObject parsed, or None if not found
        """
        if aXmlNode is None:
            return None

        aSBSObject = aSBSClass()
        try:
            aSBSObject.parse(aContext, aDirAbsPath, self, aXmlNode)
        except AttributeError:
            print('[SBSParser.parseSBSNode] Missing method parse on SBSObject: %s ' % aSBSClass.__name__)
            return None

        return aSBSObject

    def getAllSBSElementsInMulti(self, aContext, aDirAbsPath, aXmlNode, aTagConstructorDict):
        """
        Search for all children with various names under the given xmlNode, and parse them recursively
        using the parse function from the tag constructor dict

        <xmlNode><tagnameA>...</tagnameA><tagnameB>...</tagnameB>...</xmlNode>

        :return: The list of SBS objects corresponding to the given tag, or [] if not found
        """
        aSBSObjectList = []

        if aXmlNode is None or len(aTagConstructorDict) == 0:
            return aSBSObjectList

        xmlElmtObjectList = self.getAllXmlElementsUnder(aXmlNode, None)
        if xmlElmtObjectList is None:
            return aSBSObjectList

        try:
            for xmlElmtChild in aXmlNode:
                if xmlElmtChild.tag in aTagConstructorDict:
                    aSBSObject = aTagConstructorDict[xmlElmtChild.tag]()
                    aSBSObject.parse(aContext, aDirAbsPath, self, xmlElmtChild)
                    aSBSObjectList.append(aSBSObject)
        except AttributeError:
            log.error('[SBSParser.getAllSBSElementsIn] Missing method parse on SBSObject: %s ', aSBSClass.__name__)

        return aSBSObjectList if aSBSObjectList else None


    #==========================================================================
    # Private
    #==========================================================================
    def __isValidSBS(self):
        if self.mXmlRoot is None:
            return False
        if not self.mXmlRoot.tag == "package":
            return False
        formatVersionElmt = self.mXmlRoot.find('formatVersion')
        return formatVersionElmt is not None

    def __isValidSBSAR(self):
        if self.mXmlRoot is None:
            return False
        if not self.mXmlRoot.tag == "sbsdescription":
            return False

        return True

    def __isValidSBSPRS(self):
        if self.mXmlRoot is None:
            return False
        if not self.mXmlRoot.tag == "sbspresets":
            return False
        return True

    def __isValidSBSPRJ(self):
        if self.mXmlRoot is None:
            return False
        if not self.mXmlRoot.tag == "root":
            return False
        return True
