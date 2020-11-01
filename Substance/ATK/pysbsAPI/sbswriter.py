# coding: utf-8
"""
Module sbswriter provides the class SBSWriter which allows the serialization of a SBSDocument into a .sbs file.

All derived :class:`.SBSObject` have a *write* function with the same signature than on the base class :class:`.SBSObject`:
 :func:`common_interface.SBSObject.write`
"""

from __future__ import unicode_literals
import os
import logging
log = logging.getLogger(__name__)
import xml.etree.ElementTree as ET

from pysbs.api_decorators import handle_exceptions
from pysbs.api_exceptions import SBSTypeError
from pysbs.sbsproject import SBSPRJDependenciesPathTypes, SBSPRJDependenciesPathStorageMethods

# ==============================================================================
class SBSWriter:
    """
    Class used to provide useful functions when writing a .sbs (=xml) file from a SBSDocument
    """
    def __init__(self, aXmlRootNode, aPackagePath, aContext):
        self.mXmlRoot = aXmlRootNode
        self.mPackagePath = aPackagePath
        self.mContext = aContext
        if self.mXmlRoot is None:
            self.mIsValid = False
        else:
            self.mIsValid = True

    @handle_exceptions()
    def writeOnDisk(self, aFileAbsPath, aFormatDoc=False, aIncludeXMLHeader=True):
        """
        writeOnDisk(aFileAbsPath, aFormatDoc=False, aIncludeXMLHeader=True)
        Write on disk the XmlRootNode, with the appropriate header, at the given path
        """
        sbsString = ET.tostring(self.mXmlRoot, encoding="utf-8", method="xml")

        if aFormatDoc:
            from xml.dom import minidom
            reparsed = minidom.parseString(sbsString)
            sbsString = reparsed.toprettyxml(indent=' ').encode('utf-8')

        # Format the xml content exactly as Substance Designer does
        sbsString = sbsString.replace(b' />', b'/>')
        sbsString = sbsString.replace(b' ?>', b'?>')

        # - Remove header set by ElementTree (depends on Python version):
        if sbsString.startswith(b'<?xml'):
            posEndHeading = sbsString.find(b'?>')
            endHeading = posEndHeading+2
            if len(sbsString) > endHeading and sbsString[endHeading] == b'\n'[0]:
                endHeading += 1
            sbsString = sbsString[endHeading:]

        # - Add the correct header if requested
        if aIncludeXMLHeader:
            sbsString = b'<?xml version="1.0" encoding="UTF-8"?>' + sbsString
        # - Add line break
        sbsString += b'\n'

        # Write on disk
        aFile = open(aFileAbsPath, 'wb')
        aFile.write(sbsString)
        aFile.close()

    @handle_exceptions()
    def writeSBSNode(self, aXmlNode, aSBSObject, aTagName):
        """
        writeSBSNode(aXmlNode, aSBSObject, aTagName)
        Write the given SBSObject using its proper writing method, and add its XML description to the given XmlNode
        <xmlNode><tagname>...</tagname></xmlnode>
        """
        if aSBSObject is None:
            return

        aNewNode = ET.SubElement(aXmlNode, aTagName)
        try:
            aSBSObject.write(self, aNewNode)
        except AttributeError:
            log.error('[SBSWriter.writeSBSNode] Missing method write on SBSObject: %s', aSBSObject.__class__.__name__)

    @handle_exceptions()
    def writeListOfSBSNode(self, aXmlNode, aSBSObject, aTagName, aChildTagName):
        """
        writeListOfSBSNode(aXmlNode, aSBSObject, aTagName, aChildTagName)
        Write the given list of SBSObject using their proper writing method, and add its hierarchical XML description to the given XmlNode
        <xmlNode><tagname><childtagname>...</childtagname><childtagname>...</childtagname>... </tagname></xmlNode>
        """
        if aSBSObject is None:
            return

        aNewNode = ET.SubElement(aXmlNode, aTagName)
        for child in aSBSObject:
            if child is not None:
                self.writeSBSNode(aNewNode, child, aChildTagName)

    @handle_exceptions()
    def writeAllSBSNodesIn(self, aXmlNode, aObject, aTagName):
        """
        writeAllSBSNodesIn(aXmlNode, aObject, aTagName)
        Write the given list of SBSObject using its proper writing method, and its XML description directly to the given XmlNode
        <xmlNode><tagname>...</tagname><tagname>...</tagname>...</xmlNode>
        """
        if aObject is None:
            return

        for child in aObject:
            if child is not None:
                self.writeSBSNode(aXmlNode, child, aTagName)

    @handle_exceptions()
    def setXmlFilePathValue(self, aXmlElementParent, aFilePath, aChildName):
        """
        setXmlFilePathValue(aXmlElementParent, aAttribute, aChildName)
        Convert attribute path before as a absolute path.
        Write the given attribute as a child of the given XmlParent, using the format <childname v=""/>
        <xmlNode><childname v=""/></xmlNode>
        """
        if self.mPackagePath is None or self.mContext is None:
            raise SBSTypeError("SBSWriter.mPackagePath and SBSWriter.mContext must not be None. Set them in the constructor.")
        aAliasMgr = self.mContext.getUrlAliasMgr()
        aPrjMgr = self.mContext.getProjectMgr()
        aNotNearOrUnder = aPrjMgr.getDependenciesPathStorageMethod()
        aNearOrUnder = aPrjMgr.getDependenciesPathStorageMethod(method=SBSPRJDependenciesPathTypes.NEAR_OR_UNDER)
        if not aAliasMgr.isUnderPath(aFilePath, self.mPackagePath) and not aAliasMgr.getAliasInPath(aFilePath) and aNotNearOrUnder == SBSPRJDependenciesPathStorageMethods.ABSOLUTE:
            aFilePath = aAliasMgr.toAbsPath(aFilePath, os.path.dirname(self.mPackagePath))
        elif aNearOrUnder == SBSPRJDependenciesPathStorageMethods.ABSOLUTE:
            aFilePath = aAliasMgr.toAbsPath(aFilePath, os.path.dirname(self.mPackagePath))
        self.setXmlElementVAttribValue(aXmlElementParent, aFilePath, aChildName)

    @handle_exceptions()
    def setXmlElementVAttribValue(self, aXmlElementParent, aAttribute, aChildName):
        """
        setXmlElementVAttribValue(aXmlElementParent, aAttribute, aChildName)
        Write the given attribute as a child of the given XmlParent, using the format <childname v=""/>
        <xmlNode><childname v=""/></xmlNode>
        """
        if aXmlElementParent is None or aAttribute is None:
            return

        ET.SubElement(aXmlElementParent, aChildName, v=aAttribute)

    @handle_exceptions()
    def setXmlElementAttribValue(self, aXmlElementParent, aAttribute, aAttribName):
        """
        setXmlElementVAttribValue(aXmlElementParent, aAttribute, aChildName)
        Write the given attribute as a child of the given XmlParent, using the format <childname v=""/>
        <xmlNode attribName=attribute></xmlNode>
        """
        if aXmlElementParent is None or aAttribute is None:
            return

        aXmlElementParent.set(aAttribName, aAttribute)
