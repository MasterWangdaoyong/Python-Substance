# coding: utf-8
"""
Module **sbsarchive** aims to define SBSARObjects that are relative to a sbsar package,
mostly :class:`.SBSArchive` and :class:`.SBSARGlobalVar`.
"""

from __future__ import unicode_literals
import os
import json

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError, SBSUninitializedError
from pysbs.common_interfaces import SBSARObject, Package
from pysbs import python_helpers, api_helpers
from pysbs import sbsparser
from pysbs import lzmabindings
from .sbsargraph import SBSARGraph, SBSARInput


# =======================================================================
@doc_inherit
class SBSARGlobalVar(SBSARObject):
    """
    Class that contains information on a graph input as defined in a .sbsar file

    Members:
        * mInputs   (list of :class:`.SBSARInput`): List of global variables used by the substance.
    """
    def __init__(self,
                 aInputs        = None):
        super(SBSARGlobalVar, self).__init__()
        self.mInputs = aInputs if aInputs is not None else []

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mInputs = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'inputs', 'input', SBSARInput)


# ==============================================================================
@doc_inherit
class SBSArchive(SBSARObject, Package):
    """
    Class used to get information on a .sbsar file.
    It contains the full description of a substance archive, which correspond to the root node <sbsdescription> of the .sbsar file.

    Members:
        * mFormatVersion  (str): version of the format
        * mCookerBuild    (str): build number of the Cooker
        * mAsmUID         (str): unique identifier of the .sbsasm file
        * mContent        (str): content type. Default to 'full'
        * mGlobalVar      (:class:`.SBSARGlobalVar`): global variables used in the substance
        * mGraphs         (list of :class:`.SBSARGraph`): list of graphs
        * mContext        (:class:`.Context`): Execution context, with alias definition
        * mFileAbsPath    (str): Absolute path of the package
        * mDirAbsPath     (str): Absolute directory of the package
    """
    def __init__(self, aContext, aFileAbsPath,
                 aFormatVersion  = '',
                 aCookerBuild    = '',
                 aAsmUID         = '',
                 aContent        = '',
                 aGlobalVar      = None,
                 aGraphs         = None):
        SBSARObject.__init__(self)
        Package.__init__(self, aContext, aFileAbsPath)
        self.mXmlFile       = None

        self.mFormatVersion = aFormatVersion
        self.mCookerBuild   = aCookerBuild
        self.mAsmUID        = aAsmUID
        self.mContent       = aContent
        self.mGlobalVar     = aGlobalVar
        self.mGraphs        = aGraphs if aGraphs is not None else []

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mFormatVersion = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'formatversion'         )
        self.mCookerBuild   = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'cookerbuild'           )
        self.mAsmUID        = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'asmuid'                )
        self.mContent       = aSBSParser.getXmlElementAttribValue(aXmlNode,                 'content'               )
        self.mGlobalVar     = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'global',   SBSARGlobalVar  )
        self.mGraphs        = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'graphs' , 'graph'  , SBSARGraph)

    @handle_exceptions()
    def computeUniqueIdentifier(self, aIdentifier, aSuffixId=0):
        """
        computeUniqueIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used and generate a unique identifier if necessary

        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier_id
        """
        return self._computeUniqueIdentifier(aIdentifier, [self.mGraphs], aSuffixId)

    @handle_exceptions()
    def parseDoc(self, aResolveDependencies = True):
        """
        parseDoc(aResolveDependencies = True)
        Parse the SBS File content

        :return: True if succeed
        """
        aFolderName = os.path.splitext(os.path.basename(self.mFileAbsPath))[0]
        tmpFolder = self.mContext.getUrlAliasMgr().buildTmpFolderPath(aFolderName)
        with python_helpers.createTempFolders(tmpFolder):
            self.mXmlFile = self.__extractSbsarXml(tmpFolder)

            aSBSParser = sbsparser.SBSParser(self.mXmlFile, self.mContext, aFileType = sbsparser.FileTypeEnum.SBSAR)
            if aSBSParser is None or not aSBSParser.mIsValid:
                raise SBSUninitializedError('Failed to parse substance archive '+self.mFileAbsPath)

        aXmlRoot = aSBSParser.getRootNode()
        self.parse(self.mContext, self.mDirAbsPath, aSBSParser, aXmlRoot)

        # Compute unique identifiers for the graphs
        for aGraph in self.getSBSGraphList():
            aGraph.mIdentifier = self.computeUniqueIdentifier(os.path.basename(aGraph.mPkgUrl))

        self.setInitialized()
        return True

    @handle_exceptions()
    def buildAbsPathFromRelToMePath(self, aRelPathFromPackage):
        """
        buildAbsPathFromRelToMePath(aRelPathFromPackage)
        Build a path starting from the current package absolute directory and complete it with the given relative path

        :param aRelPathFromPackage: The relative path from the current package
        :type aRelPathFromPackage: str
        :return: The complete path, as a string
        """
        aRelPathFromPackage = self.mContext.getUrlAliasMgr().normalizePath(aRelPathFromPackage)
        return os.path.join(self.mDirAbsPath, aRelPathFromPackage)

    @handle_exceptions()
    def getObjectFromInternalPath(self, aPath):
        """
        getObjectFromInternalPath(aPath)
        Get the object pointed by the given path, which must reference the current package.

        :param aPath: the relative path, starting with 'pkg:///'
        :type aPath: str
        :return: the pointed :class:`.SBSARObject` if found, None otherwise
        """
        return self.getSBSGraph(api_helpers.removePkgPrefix(aPath))

    @handle_exceptions()
    def getSBSGraphPkgUrl(self, aGraph):
        """
        getSBSGraphPkgUrl(aGraph)
        Get the path of the given graph relatively to the current package (pkg:///.../aGraphIdentifier)

        :param aGraph: Identifier of the graph to get
        :type aGraph: A :class:`.SBSGraph` object
        :return: A string containing the relative path from the root content to the given graph, None otherwise
        """
        return aGraph.mPkgUrl

    @handle_exceptions()
    def getSBSGraph(self, aGraphIdentifier):
        """
        getSBSGraph(aGraphIdentifier)
        Get the SBSARGraph object with the given identifier.

        :param aGraphIdentifier: Identifier of the graph to get
        :type aGraphIdentifier: str
        :return: A :class:`.SBSARGraph` object
        """
        return next((aGraph for aGraph in self.getSBSGraphList() if aGraph.mIdentifier == aGraphIdentifier), None)

    @handle_exceptions()
    def getSBSGraphFromPkgUrl(self, aPkgUrl):
        """
        getSBSGraphFromPkgUrl(aPkgUrl)
        Get the SBSARGraph object with the given package URL.

        :param aPkgUrl: The graph Url relatively to the package, in the format 'pkg:///MyGraph'
        :type aPkgUrl: str
        :return: A :class:`.SBSARGraph` object
        """
        return next((aGraph for aGraph in self.getSBSGraphList()
                     if api_helpers.removePkgPrefix(aGraph.mPkgUrl) == api_helpers.removePkgPrefix(aPkgUrl) ), None)

    @handle_exceptions()
    def getFirstSBSGraph(self):
        """
        getSBSGraph(aGraphIdentifier)
        Get the first Graph object

        :param aGraphIdentifier: Identifier of the graph to get
        :type aGraphIdentifier: str
        :return: A :class:`.Graph` object, a string containing its pkg relative path        """
        aGraphList = self.getSBSGraphList()
        if len(aGraphList) == 0:
            return None, None
        aInternalPath = aGraphList[0].mPkgUrl
        aObject = self.getObjectFromInternalPath(aInternalPath)
        return aObject, aInternalPath

    @handle_exceptions()
    def getSBSGraphList(self):
        """
        getSBSGraphList()
        Get the list of all graphs defined in the .sbsar file

        :return: A list of :class:`.SBSARGraph` object
        """
        return self.mGraphs if self.mGraphs is not None else []

    @handle_exceptions()
    def extractSbsarMetaDataJson(self, aDestFolderPath, aNameToFind='metadata.json'):
        """
        Extract the metadata json file in the destFolderPath

        :param sDestFolderPath: a directory path
        :type aDestFolderPath: str
        :param aNameToFind: json file name present in sbsar, by default it's metadata.json
        :type aNameToFind: str
        :return: a complete file path
        """
        aDestFolderPath = aDestFolderPath if aDestFolderPath.endswith("/") else aDestFolderPath + "/"
        if not lzmabindings.SevenZipExtract(self.mFileAbsPath, aDestFolderPath, '.json'):
            raise SBSImpossibleActionError("Failed to extract the sbsar's file: "+self.mFileAbsPath)
        aJsonFile = next((aFile for aFile in os.listdir(aDestFolderPath) if aFile == aNameToFind), None)
        try:
            outFilename = os.path.join(aDestFolderPath, os.path.normpath(aJsonFile))
            return os.path.join(aDestFolderPath, outFilename)
        except:
            raise SBSImpossibleActionError('Failed to get the .json metadata file contained in the file '+self.mFileAbsPath)

    @handle_exceptions()
    def extractSbsarMetaDataResource(self, aDestFolderPath, aSbsarResourcePath):
        """
        Extract a resource file present in the sbsar.
        The sbsar resource path is the sbsar relative path to the resource file.

        :param aDestFolderPath: a directory path
        :type aDestFolderPath: str
        :param aSbsarResourcePath: sbsar relative path to the resource file, ex: "resources/1/untitled.blend"
        :type aSbsarResourcePath: str
        :return: a complete file path
        """
        aDestFolderPath = aDestFolderPath if aDestFolderPath.endswith("/") else aDestFolderPath + "/"
        if not lzmabindings.SevenZipExtract(self.mFileAbsPath, aDestFolderPath, aSbsarResourcePath):
            raise SBSImpossibleActionError("Failed to extract the sbsar's file: "+self.mFileAbsPath)
        aResourcePath = next((aFile for aFile in os.listdir(aDestFolderPath) if aFile == os.path.basename(aSbsarResourcePath)), None)
        try:
            outFilename = os.path.join(aDestFolderPath, os.path.normpath(aResourcePath))
            return os.path.join(aDestFolderPath, outFilename)
        except:
            raise SBSImpossibleActionError('Failed to get the resource metadata file contained in the file '+self.mFileAbsPath)

    @handle_exceptions()
    def extractSbsarMetaDataPack(self, aDestFolderPath):
        """
        Extract the json file and all metadata resource files present in the sbsar.

        :param aDestFolderPath: a directory path
        :type aDestFolderPath: str
        :return: a complete file path
        """
        aRes = []
        aMetaDataDict = self.getAllMetaData()
        allResourcesPath = [f for f in aMetaDataDict.values() if f.startswith('resources/')]
        for path in allResourcesPath:
            aRes.append(self.extractSbsarMetaDataResource(aDestFolderPath, path))
        aRes.append(self.extractSbsarMetaDataJson(aDestFolderPath))
        return aRes

    @handle_exceptions()
    def getAllMetaData(self):
        """
        Extract the metadata json file and return a dict

        :return: a metadata dict
        """
        aMetaDataDict = {}
        aFolderName = os.path.splitext(os.path.basename(self.mFileAbsPath))[0]
        tmpFolder = self.mContext.getUrlAliasMgr().buildTmpFolderPath(aFolderName)
        with python_helpers.createTempFolders(tmpFolder):
            aJson = self.extractSbsarMetaDataJson(tmpFolder)
            with open(aJson, 'r') as f:
                aMetaDataDict = json.load(f)
        return aMetaDataDict

    #==========================================================================
    # Private
    #==========================================================================
    def __extractSbsarXml(self, destFolderPath):
        # Extract the .sbsar in Substance Designer temp folder
        if not lzmabindings.SevenZipExtract(self.mFileAbsPath, destFolderPath, '.xml'):
            raise SBSImpossibleActionError('Failed to extract the sbsar file: '+self.mFileAbsPath)

        aXmlName = next((aFile for aFile in os.listdir(destFolderPath) if aFile.endswith('.xml')), None)
        try:
            outFilename = os.path.join(destFolderPath, os.path.normpath(aXmlName))
            return os.path.join(destFolderPath, outFilename)
        except:
            raise SBSImpossibleActionError('Failed to get the .xml file contained in the file '+self.mFileAbsPath)
