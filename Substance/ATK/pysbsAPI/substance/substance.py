# coding: utf-8
"""
Module **substance** aims to define SBSObjects that are relative to a package,
mostly :class:`.SBSDocument`, :class:`.SBSContent` and :class:`.SBSResource`.
"""
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import os
import re
import weakref
import xml.etree.ElementTree as ET
import copy

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError, SBSIncompatibleVersionError, SBSUninitializedError, \
    SBSMissingDependencyError, SBSMetaDataTreeNameConflict
from pysbs.common_interfaces import SBSObject, UIDGenerator, Package
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum
from pysbs import graph
from pysbs import mdl
from pysbs import compnode
from pysbs import params
from pysbs import sbsgenerator
from pysbs import sbslibrary
from pysbs import sbsparser
from pysbs import sbswriter

from .content import SBSContent, SBSGroup
from .resource import SBSResource, SBSResourceScene



# ==============================================================================
@doc_inherit
class SBSMetaDataTree(SBSObject):
    """
    """
    def __init__(self, aMetaDataTreeUrlList=None,
                       aMetaDataTreeStrList=None,):
        super(SBSMetaDataTree, self).__init__()
        self.mMetaDataTreeUrlList = aMetaDataTreeUrlList if aMetaDataTreeUrlList is not None else []
        self.mMetaDataTreeStrList = aMetaDataTreeStrList if aMetaDataTreeStrList is not None else []
        self.mMembersForEquality = ['mMetaDataTreeUrlList', 'mMetaDataTreeStrList']

    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mMetaDataTreeUrlList = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'treeurl', SBSMetaDataTreeUrl)
        self.mMetaDataTreeStrList = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'treestr', SBSMetaDataTreeStr)

    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mMetaDataTreeUrlList, 'treeurl')
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mMetaDataTreeStrList, 'treestr')


@doc_inherit
class SBSMetaDataTreeType(SBSObject):
    """
    """
    def __init__(self, aName='',
                       aValue='',):
        super(SBSMetaDataTreeType, self).__init__()
        self.mName = self.mValue = None
        self.mMembersForEquality = ['mName', 'mValue']
        if aName and aValue:
            self.name = aName
            self.value = aValue

    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name')
        self.mValue = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'value')

    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName, 'name')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mValue, 'value')

    @property
    def name(self):
        return self.mName

    @name.setter
    def name(self, aName):
        self.setName(aName)

    def setName(self, aName):
        """
        Setter exist to keep the original design of pysbs
        :param aName:
        :return:
        """
        if not python_helpers.isStringOrUnicode(aName):
            raise TypeError("setName's argument must be a string.")
        self.mName = aName

    @property
    def value(self):
        return self.mValue

    @value.setter
    def value(self, aValue):
        self.setValue(aValue)

    def setValue(self, aValue):
        """
        Setter exist to keep the original design of pysbs
        :param aValue:
        :return:
        """
        if not python_helpers.isStringOrUnicode(aValue):
            raise TypeError("setValue's argument must be a string.")
        self.mValue = aValue


@doc_inherit
class SBSMetaDataTreeUrl(SBSMetaDataTreeType):
    """
    """
    def __init__(self, aName='',
                       aValue='',):
        super(SBSMetaDataTreeUrl, self).__init__(aName=aName, aValue=aValue)

    def setValue(self, aResource):
        # a SBSResource
        if isinstance(aResource, SBSResource):
            self.mValue = aResource.getPkgResourcePath()
        # A dep path, pkg://Resources/corsica_beach?dependency=1358524229
        elif api_helpers.isADependencyPath(aResource):
            self.mValue = aResource
        else:
            raise TypeError("aResource, createMetaDataUrl's argument must be a SBSResource.")


@doc_inherit
class SBSMetaDataTreeStr(SBSMetaDataTreeType):
    """
    """
    def __init__(self, aName='',
                       aValue=''):
        super(SBSMetaDataTreeStr, self).__init__(aName=aName, aValue=aValue)


@doc_inherit
class SBSDependency(SBSObject):
    """
    Class that contains information on a package dependency as defined in a .sbs file

    Members:
        * mFilename    (str): name of the file.
        * mUID         (str): unique identifier of this dependency in the package/ context (used as reference).
        * mType        (str): type of dependency (fixed: package).
        * mFileUID     (str): identifier of the file (*package/header/fileUID*).
        * mVersionUID  (str): identifier of the current version of the file (*package/header/versionUID*). Used for changing repercussion purposes.
        * mFileAbsPath (str): file absolute path
    """
    def __init__(self,
                 aFilename   = '',
                 aUID        = '',
                 aType       = '',
                 aFileUID    = '',
                 aVersionUID = '',
                 aFileAbsPath = None):
        super(SBSDependency, self).__init__()
        self.mFilename      = aFilename.replace('\\', '/') if aFilename else aFilename
        self.mUID           = aUID
        self.mType          = aType
        self.mFileUID       = aFileUID
        self.mVersionUID    = aVersionUID
        self.mFileAbsPath   = aFileAbsPath
        self.mRefPackage = None

        self.mMembersForEquality = ['mFilename',
                                    'mType',
                                    'mVersionUID']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mFilename      = aSBSParser.getXmlFilePathValue(aXmlNode, 'filename'     )
        self.mUID           = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'uid'          )
        self.mType          = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'type'         )
        self.mFileUID       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'fileUID'      )
        self.mVersionUID    = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'versionUID'   )
        self.mFileAbsPath   = aContext.getUrlAliasMgr().toAbsPath(self.mFilename, aDirAbsPath)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlFilePathValue(aXmlNode, self.mFilename    , 'filename'     )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID         , 'uid'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType        , 'type'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFileUID     , 'fileUID'      )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mVersionUID  , 'versionUID'   )

    def isHimself(self):
        """
        :return: True if the dependency references the document itself, False otherwise.
        """
        return self.mFilename == '?himself'

    def getRefPackage(self):
        """
        Get the reference to the :class:`.SBSDocument` pointed by this dependency
        """
        return self.mRefPackage

    @handle_exceptions()
    def setRefPackage(self, aRefPackage):
        """
        setRefPackage(aRefPackage)
        Allows to set the reference to the :class:`.SBSDocument` pointed by this dependency

        :param aRefPackage: The package pointed by this dependency
        :type aRefPackage: :class:`.SBSDocument`
        """
        self.mRefPackage = weakref.ref(aRefPackage)



# ==============================================================================
@doc_inherit
class SBSDocument(SBSObject, Package):
    """
    Class used to get information on a .sbs file.
    It contains the full description of a substance, which correspond to the root node <package> of the .sbs file.

    Members:
        * mIdentifier     (str): unique string identifier
        * mDescription    (str, optional): textual description
        * mFormatVersion  (str): version number of the .sbs format of this file
        * mUpdaterVersion (str): version number of the .sbs format updater
        * mFileUID        (str): unique identifier of this file (for buffering coherence). MS GUID-like format
        * mVersionUID     (str): unique identifier of the current version of this file (different at each file save).
        * mDependencies   (list of :class:`.SBSDependency`): list of external dependencies
        * mContent        (:class:`.SBSContent`): content of the package, tree structure
        * mContext        (:class:`.Context`): Execution context, with alias definition
        * mFileAbsPath    (str): Absolute path of the package
        * mDirAbsPath     (str): Absolute directory of the package
    """
    def __init__(self, aContext, aFileAbsPath,
                 aIdentifier     = '',
                 aDescription    = None,
                 aFormatVersion  = '',
                 aUpdaterVersion = '',
                 aFileUID        = '',
                 aVersionUID     = '',
                 aDependencies   = None,
                 aMetaDataTree   = None,
                 aContent        = None):
        SBSObject.__init__(self)
        Package.__init__(self, aContext, aFileAbsPath)

        self.mIdentifier    = aIdentifier
        self.mDescription   = aDescription
        self.mFormatVersion = aFormatVersion
        self.mUpdaterVersion= aUpdaterVersion
        self.mFileUID       = aFileUID
        self.mVersionUID    = aVersionUID
        self.mDependencies  = aDependencies if aDependencies is not None else []
        self.mMetaDataTree  = aMetaDataTree
        self.mContent       = aContent

        self.mMembersForEquality = ['mIdentifier',
                                    'mDescription',
                                    'mFormatVersion',
                                    'mUpdaterVersion',
                                    'mVersionUID',
                                    'mDependencies',
                                    'mContent']

    def setInitialized(self):
        """
        setInitialized()
        Set the package as initialized.

        :raise: :class:`api_exceptions.SBSUninitializedError` in case where the Content or the Format Version are not defined
        """
        if self.mContent and self.mFormatVersion:
            Package.setInitialized(self)
        else:
            raise SBSUninitializedError('Failed to set the SBSDocument in initialized state, please check its Content and Format version')

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mFormatVersion = aSBSParser.getXmlElementVAttribValue(aXmlNode,               'formatVersion' )
        self.mUpdaterVersion= aSBSParser.getXmlElementVAttribValue(aXmlNode,               'updaterVersion')

        if not aContext.canReadSBSPackage(self.mFormatVersion, self.mUpdaterVersion):
            raise SBSIncompatibleVersionError(aPackagePath = self.mFileAbsPath,
                                              aIncompatibleVersion = self.mFormatVersion,
                                              aIncompatibleUpdaterVersion = self.mUpdaterVersion,
                                              aSupportedVersion = aContext.getSBSFormatVersion(),
                                              aSupportedUpdaterVersion = aContext.getSBSUpdaterVersion())

        self.mIdentifier    = aSBSParser.getXmlElementVAttribValue(aXmlNode,               'identifier'    )
        self.mDescription   = aSBSParser.getXmlElementVAttribValue(aXmlNode,               'desc'          )
        self.mFileUID       = aSBSParser.getXmlElementVAttribValue(aXmlNode,               'fileUID'       )
        self.mVersionUID    = aSBSParser.getXmlElementVAttribValue(aXmlNode,               'versionUID'    )
        self.mContent       = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,     'content'       , SBSContent)
        self.mDependencies = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'dependencies'  , 'dependency', SBSDependency)
        self.mMetaDataTree = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'tree', SBSMetaDataTree)
        pass

    @handle_exceptions()
    def parseDoc(self, aResolveDependencies = True):
        """
        parseDoc(aResolveDependencies = True)
        Parse the SBS File content

        :return: True if succeed
        """
        aSBSParser = sbsparser.SBSParser(self.mFileAbsPath, self.mContext, aFileType = sbsparser.FileTypeEnum.SBS)
        if aSBSParser is None or not aSBSParser.mIsValid:
            raise SBSUninitializedError('Failed to parse substance '+self.mFileAbsPath)

        aXmlRoot = aSBSParser.getRootNode()
        self.parse(self.mContext, self.mDirAbsPath, aSBSParser, aXmlRoot)
        self._mIsInitialized = True

        aDep = self.getHimselfDependency()
        if aDep is not None:
            aDep.mFileAbsPath = self.mFileAbsPath
        if aResolveDependencies:
            self.mContext.resolveDependencies(self)

        self.mContext.declarePackage(self)

        return True

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier    , 'identifier'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDescription   , 'desc'             )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFormatVersion , 'formatVersion'    )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUpdaterVersion, 'updaterVersion'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFileUID       , 'fileUID'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mVersionUID    , 'versionUID'       )
        aSBSWriter.writeSBSNode(aXmlNode, self.mMetaDataTree, 'tree')
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mDependencies, 'dependencies', 'dependency')
        aSBSWriter.writeSBSNode(aXmlNode, self.mContent, 'content')

    @handle_exceptions()
    def changeDocumentPath(self, aNewFileAbsPath):
        """
        changeDocumentPath(aNewFileAbsPath)
        Modify the document absolute path and modify the relative paths of the referenced resources and dependencies.
        This function does not modify physically the location of the .sbs file on the disk, it just updates the content of the .sbs file considering a new location.

        :param aNewFileAbsPath: The new location of the document.
        :type aNewFileAbsPath: string
        """
        aCurFolder = os.path.dirname(self.mFileAbsPath)
        aNewFolder = os.path.dirname(aNewFileAbsPath)
        self.mFileAbsPath = aNewFileAbsPath
        self.mDirAbsPath = aNewFolder
        if aCurFolder != aNewFolder:
            aDependencyList = self.getSBSDependencyList()
            for aDependency in aDependencyList:
                if self.mContext.getUrlAliasMgr().getAliasInPath(aDependency.mFilename) is None:
                    aDependency.mFilename = self.mContext.getUrlAliasMgr().toRelPath(aDependency.mFileAbsPath, aNewFolder).replace('\\', '/')

            aResourceList = self.getSBSResourceList()
            for aResource in aResourceList:
                if self.mContext.getUrlAliasMgr().getAliasInPath(aResource.mFilePath) is None:
                    aResource.mFilePath = self.mContext.getUrlAliasMgr().toRelPath(aResource.mFileAbsPath, aNewFolder).replace('\\', '/')

    @handle_exceptions()
    def writeDoc(self, aNewFileAbsPath = None, aUpdateRelativePaths = False):
        """
        writeDoc(aNewFileAbsPath = None, aUpdateRelativePaths = False)
        Write the SBS document in Element Tree structure and write it on the disk.
        If aNewFileAbsPath is provided, the document is saved at this location, otherwise it is save on the current file location.

        :param aNewFileAbsPath: The final location of the document. By default, the document is saved at the same location that the one provided when creating the document.
        :param aUpdateRelativePaths: Set to True to update the relative paths of the resources and dependencies of this document when saving on a new location. Default to False
        :type aNewFileAbsPath: string, optional
        :type aUpdateRelativePaths: boolean, optional
        :return: True if succeed
        """
        aXmlRoot = ET.Element('package')
        aSBSWriter = sbswriter.SBSWriter(aXmlRoot, self.mFileAbsPath, self.mContext)
        if aSBSWriter.mIsValid is False:
            return False

        if aNewFileAbsPath:
            absPath = self.mContext.getUrlAliasMgr().toAbsPath(aNewFileAbsPath, '')
            if aUpdateRelativePaths:
                self.changeDocumentPath(aNewFileAbsPath = absPath)
        else:
            absPath = self.mFileAbsPath

        self.write(aSBSWriter, aXmlRoot)
        aSBSWriter.writeOnDisk(absPath)
        return True


    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Parse the Dependencies and Content to find a :class:`.SBSObject` with the given uid

        :return: True if an object has this uid
        """
        # Parsing of the dependencies
        if next((aDependency for aDependency in self.getSBSDependencyList(True) if aDependency.mUID == aUID), None) is not None:
            return True
        return self.getContent().getUidIsUsed(aUID)


    @handle_exceptions()
    def buildAbsPathFromRelToMePath(self, aRelPathFromPackage):
        """
        buildAbsPathFromRelToMePath(aRelPathFromPackage)
        Build a path starting from the current package absolute directory and complete it with the given relative path

        :param aRelPathFromPackage: The relative path from the current package
        :type aRelPathFromPackage: str
        :return: The complete path, as a string
        """
        return self.convertToAbsolutePath(aRelPathFromPackage)

    @handle_exceptions()
    def convertToAbsolutePath(self, aPath):
        """
        convertToAbsolutePath(aPath)
        Convert the given path into an absolute path.

        :param aPath: The path to convert to an absolute path.

            - If the path is relative to the current document, convert it to an absolute path
            - If the path contains an alias, convert it to an absolute path using the alias absolute path
            - If the path contains a reference to a dependency, use the absolute path of this dependency
            - If the path references an object contained in the current package (pkg:///ObjectIdentifier), use the current document absolute path

        :type aPath: str
        :return: The absolute path corresponding to the given path, with '/' separator
        """
        aAbsPath = ''
        aPath, aDepUID = api_helpers.splitPathAndDependencyUID(aPath)
        if aDepUID is not None:
            aDep = self.getDependency(aUID = aDepUID)
            if aDep:
                aAbsPath = aDep.mFileAbsPath + '/'

            aPath = api_helpers.removePkgPrefix(aPath)
            aAbsPath += aPath
        else:
            if api_helpers.hasPkgPrefix(aPath):
                aPath = api_helpers.removePkgPrefix(aPath)
                aAbsPath = self.mContext.getUrlAliasMgr().toAbsPath(aPath, self.mFileAbsPath)
            else:
                aAbsPath = self.mContext.getUrlAliasMgr().toAbsPath(aPath, self.mDirAbsPath)

        return aAbsPath.replace('\\', '/')

    def getContent(self):
        """
        getContent()
        Get the content of the package

        :return: the package content as a :class:`.SBSContent` object
        :raise: :class:`api_exceptions.SBSUninitializedError` in case where the package is not initialized (not parsed yet or not well created)
        """
        if not self.isInitialized():
            raise SBSUninitializedError()
        return self.mContent

    @handle_exceptions()
    def getSBSDependencyList(self, aIncludeHimself = False):
        """
        getSBSDependencyList(aIncludeHimself = False)
        Get the list of dependencies directly referenced by this SBSDocument.

        :param aIncludeHimself: True to include ?himself dependency to the result. Default to False
        :type aIncludeHimself: bool, optional
        :return: A list of :class:`.SBSDependency` objects
        :raise: :class:`api_exceptions.SBSUninitializedError` in case where the package is not initialized (not parsed yet or not well created)
        """
        if not self.isInitialized():
            raise SBSUninitializedError()

        if self.mDependencies:
            return [dep for dep in self.mDependencies if aIncludeHimself or not dep.isHimself()]
        return []

    @handle_exceptions()
    def getDependencyPathList(self, aRecurseOnPackages = False):
        """
        getDependencyPathList(self, aRecurseOnPackages = False)
        Get the list of the dependencies absolute path of this SBSDocument.
        If aRecurseOnPackages is True, look into the referenced packages to get the list of dependencies recursively.

        :param aRecurseOnPackages: True to build the full list of dependencies recursively. Default to False
        :type aRecurseOnPackages: bool, optional
        :return: The list of absolute paths as strings
        """
        # Start by building the list of dependencies without himself:
        directDependencies = self.getSBSDependencyList(aIncludeHimself=False)
        aDependencyList = [aDep.mFileAbsPath for aDep in directDependencies]

        # Recursive: Resolve recursively the referenced dependencies:
        if aRecurseOnPackages:
            aDependenciesToParse = directDependencies
            aDepToResolve = []
            while aDependenciesToParse:
                aDep = aDependenciesToParse.pop(0)
                try:
                    if aDep.getRefPackage() is not None:
                        aDepPackage = aDep.getRefPackage()()
                    else:
                        aDepPackage = self.mContext.resolveDependency(aParentDocument = self, aSBSDependency = aDep)()

                    if Package.isAnArchive(aDepPackage.mFileAbsPath):
                        continue
                    for aSubDep in aDepPackage.getSBSDependencyList():
                        if aSubDep.mFileAbsPath not in aDependencyList:
                            aDependenciesToParse.append(aSubDep)
                            aDependencyList.append(aSubDep.mFileAbsPath)
                        else:
                            aDepToResolve.append(aSubDep)
                except:
                    log.warning('[substance.SBSDocument.getSBSDependencyList()] Failed to find package at %s', aDep.mFileAbsPath)

            # Finalize all dependency references now that everything is parsed
            for aDep in aDepToResolve:
                self.mContext.resolveDependency(aParentDocument=self, aSBSDependency=aDep)

        return aDependencyList

    @handle_exceptions()
    def getHimselfDependency(self):
        """
        getHimselfDependency()
        Look for the dependency identified by 'himself'

        :return: A :class:`.SBSDependency` object if it exist, None otherwise
        """
        return next((aDep for aDep in self.getSBSDependencyList(aIncludeHimself = True) if aDep.isHimself()), None)

    @handle_exceptions()
    def getDependency(self, aUID):
        """
        getDependency(aUID)
        Get the dependency with the given UID

        :param aUID: Uid of the dependency to get
        :type aUID: str
        :return: A :class:`.SBSDependency` object if it exist, None otherwise
        """
        return next((aDep for aDep in self.getSBSDependencyList(aIncludeHimself = True) if aDep.mUID == aUID), None)

    @handle_exceptions()
    def getDependencyFromPath(self, aPath):
        """
        getDependencyFromPath(aPath)
        Get the dependency that refers to the given path

        :param aPath: The path of the dependency to look for
        :param aPath: str
        :return: A :class:`.SBSDependency` object if it exist, None otherwise
        """
        # Format the path as it is saved in a SBSDependency
        aPath = python_helpers.castStr(aPath)
        aFilename =  self.mContext.getUrlAliasMgr().toRelPath(aUrl = aPath, aDirAbsPath = self.mDirAbsPath).replace('\\', '/')
        aAbsPath = self.mContext.getUrlAliasMgr().toAbsPath(aUrl = aPath, aDirAbsPath = self.mDirAbsPath)

        # Browse dependencies
        return next((aDep for aDep in self.getSBSDependencyList(aIncludeHimself=True) \
                     if aDep.mFilename == aFilename or aDep.mFileAbsPath == aAbsPath ), None)

    @handle_exceptions()
    def getDependencyContainingInternalPath(self, aPath):
        """
        getDependencyContainingInternalPath(self, aPath)
        Try to find a dependency containing an object of the given class with the given identifier.

        :param aPath: The object internal path (pkg:///...) to look for
        :type aPath: str
        :return: The dependency containing the given identifier if found, None otherwise
        """
        for aDep in self.getSBSDependencyList(aIncludeHimself=True):
            if aDep.getRefPackage() is not None:
                if aDep.getRefPackage()().getObjectFromInternalPath(aPath) is not None:
                    return aDep
        return None

    @handle_exceptions()
    def hasADependencyOn(self, aPath):
        """
        hasADependencyOn(aPath)
        Check if this package has a dependency on the given path

        :param aPath: The path of the dependency to look for
        :param aPath: str
        :return: True if the package has this dependency, False otherwise
        """
        return self.getDependencyFromPath(aPath) is not None

    @handle_exceptions()
    def createDependency(self, aPath):
        """
        createDependency(aPath)
        Create a new dependency to the given path.

        :param aPath: the path (absolute, relative or with an alias) to the dependency
        :type aPath: str
        :return: The :class:`.SBSDependency` object
        """
        if not self.isInitialized():
            raise SBSUninitializedError()

        if aPath == self.mFileAbsPath:
            return self.createHimselfDependency()

        aType = ''
        if Package.isAPackage(aPath) or aPath == '?himself':
            aType = 'package'
        if aPath == '?himself':
            aFilename = aPath
            aAbsPath = self.mFileAbsPath
        else:
            aFilename = self.mContext.getUrlAliasMgr().toRelPath(aUrl = aPath, aDirAbsPath = self.mDirAbsPath)
            aAbsPath = self.mContext.getUrlAliasMgr().toAbsPath(aUrl = aPath, aDirAbsPath = self.mDirAbsPath)

        aDependency = SBSDependency(aFilename = aFilename,
                                    aUID = UIDGenerator.generateUID(self),
                                    aType = aType,
                                    aFileUID = '0',
                                    aVersionUID = '0',
                                    aFileAbsPath = aAbsPath)

        api_helpers.addObjectToList(self, 'mDependencies', aDependency)
        return aDependency

    @handle_exceptions()
    def createHimselfDependency(self):
        """
        createHimselfDependency()
        Add the '?himself' dependency to the package, which allows referencing objects  in the package.

        :return: The :class:`.SBSDependency` object
        """
        return self.createDependency('?himself')

    @handle_exceptions()
    def getSBSResource(self, aResourceIdentifier):
        """
        getSBSResource(self, aResourceIdentifier)
        Get the Resource object with the given identifier

        :param aResourceIdentifier: Identifier of the resource to get
        :type aResourceIdentifier: str
        :return: A :class:`.SBSResource` object
        """
        if api_helpers.hasPkgPrefix(aResourceIdentifier):
            return self.getObjectFromInternalPath(aResourceIdentifier)
        return self.getContent().getSBSResource(aResourceIdentifier, True)

    @handle_exceptions()
    def getSBSResourceFromPath(self, aPath, isLinkedResource=None):
        """
        getSBSResourceFromPath(aPath)
        Get the first resource that refers to the given path, with the given link/imported status

        :param aPath: The path of the resource to look for
        :param isLinkedResource: allows to specify if the resource to find is linked or imported, or if it does not matter (e.g. None). Default to None
        :type aPath: str
        :type isLinkedResource: bool
        :return: A :class:`.SBSResource` object if it exist, None otherwise
        """
        resourceList = self.getSBSResourcesFromPath(aPath)
        if resourceList:
            if isLinkedResource is None:
                return resourceList[0]
            else:
                return next((aRes for aRes in resourceList if aRes.isLinked() == isLinkedResource), None)
        return None

    @handle_exceptions()
    def getSBSResourcesFromPath(self, aPath):
        """
        getSBSResourcesFromPath(aPath)
        Get all the resources that refers to the given path

        :param aPath: The path of the resource to look for
        :type aPath: str
        :return: A :class:`.SBSResource` object if it exist, None otherwise
        """
        aAbsPath = self.mContext.getUrlAliasMgr().toAbsPath(aUrl = aPath, aDirAbsPath = self.mDirAbsPath)
        return [aRes for aRes in self.getSBSResourceList() if aRes.mFileAbsPath == aAbsPath]

    @handle_exceptions()
    def getSBSResourceFromUID(self, aUID):
        """
        getSBSResourceFromUID(aUID)
        Get the resource with the given UID

        :param aUID: The UID of the resource to look for
        :param aUID: str
        :return: A :class:`.SBSResource` object if it exist, None otherwise
        """
        return next((aRes for aRes in self.getSBSResourceList() if aRes.mUID == aUID), None)

    @handle_exceptions()
    def getSBSResourceList(self, aIncludeSceneResources=True):
        """
        getSBSResourceList(aIncludeSceneResources=True)
        Get the list of all the resources directly referenced by this SBSDocument.

        :param aIncludeSceneResources: True to include Scene/Mesh resources. Default to True
        :type aIncludeSceneResources: bool, optional
        :return: A list of :class:`.SBSResource` objects
        """
        return self.getContent().getSBSResourceList(aRecursive = True, aIncludeSceneResources=aIncludeSceneResources)

    @handle_exceptions()
    def getResourcePathList(self, aRecurseOnPackages=False, aIncludeSceneResources=True):
        """
        getResourcePathList(aRecurseOnPackages=False, aIncludeSceneResources=True)
        Get the list of all the resources path defined in this SBSDocument.
        If aRecurseOnPackage is True, look into the referenced packages to get the list of resources recursively.

        :param aRecurseOnPackages: True to build the full list of dependencies recursively. Default to False
        :type aRecurseOnPackages: bool, optional
        :param aIncludeSceneResources: True to include Scene/Mesh resources. Default to True
        :type aIncludeSceneResources: bool, optional
        :return: The list of resource paths as strings
        """
        # Get the resources directly included in this package
        aResourceList = []
        for aRes in self.getSBSResourceList(aIncludeSceneResources):
            aResourceList.extend(aRes.getPhysicalResourceList())

        # Recursive: Get all the resources of the referenced dependencies:
        if aRecurseOnPackages:
            for aDepPath in self.getDependencyPathList(aRecurseOnPackages=True):
                aPackage = self.mContext.getPackage(aDepPath)
                if aPackage and not Package.isAnArchive(aPackage.mFileAbsPath):
                    aResourceList.extend(aPackage.getResourcePathList())
        return aResourceList

    @handle_exceptions()
    def getMDLGraph(self, aGraphIdentifier):
        """
        getMDLGraph(aGraphIdentifier)
        Get the MDLGraph object with the given identifier

        :param aGraphIdentifier: Identifier of the graph to get
        :type aGraphIdentifier: str
        :return: A :class:`.MDLGraph` object
        """
        if api_helpers.hasPkgPrefix(aGraphIdentifier):
            return self.getObjectFromInternalPath(aGraphIdentifier)
        return self.getContent().getMDLGraph(aGraphIdentifier, True)

    @handle_exceptions()
    def getMDLGraphList(self):
        """
        getMDLGraphList()
        Get the list of all graphs defined in the .sbs file

        :return: A list of :class:`.MDLGraph` object
        """
        return self.getContent().getMDLGraphList(aRecursive = True)

    @handle_exceptions()
    def getSBSGraph(self, aGraphIdentifier):
        """
        getSBSGraph(aGraphIdentifier)
        Get the Graph object with the given identifier

        :param aGraphIdentifier: Identifier of the graph to get
        :type aGraphIdentifier: str
        :return: A :class:`.SBSGraph` object
        """
        if api_helpers.hasPkgPrefix(aGraphIdentifier):
            return self.getObjectFromInternalPath(aGraphIdentifier)
        return self.getContent().getSBSGraph(aGraphIdentifier, True)

    @handle_exceptions()
    def getSBSGraphList(self):
        """
        getSBSGraphList()
        Get the list of all graphs defined in the .sbs file

        :return: A list of :class:`.SBSGraph` object
        """
        return self.getContent().getSBSGraphList(aRecursive = True)

    @handle_exceptions()
    def getSBSFunction(self, aFunctionIdentifier):
        """
        getSBSFunction(aFunctionIdentifier)
        Get the Function object with the given identifier

        :param aFunctionIdentifier: Identifier of the function to get
        :type aFunctionIdentifier: str
        :return: A :class:`.SBSFunction` object
        """
        if api_helpers.hasPkgPrefix(aFunctionIdentifier):
            return self.getObjectFromInternalPath(aFunctionIdentifier)
        return self.getContent().getSBSFunction(aFunctionIdentifier, True)

    @handle_exceptions()
    def getSBSFunctionList(self):
        """
        getSBSFunctionList()
        Get the list of all functions defined in the .sbs file

        :return: A list of :class:`.SBSFunction` object
        """
        return self.getContent().getSBSFunctionList(aRecursive = True)

    @handle_exceptions()
    def getSBSGroup(self, aGroupIdentifier):
        """
        getSBSGroup(aGroupIdentifier)
        Get the Group object with the given identifier

        :param aGroupIdentifier: Identifier of the group (=folder) to get
        :type aGroupIdentifier: str
        :return: A :class:`.SBSGroup` object
        """
        if api_helpers.hasPkgPrefix(aGroupIdentifier):
            return self.getObjectFromInternalPath(aGroupIdentifier)
        return self.getContent().getSBSGroup(aGroupIdentifier, True)

    @handle_exceptions()
    def getSBSGroupList(self):
        """
        getSBSGroupList()
        Get the list of all groups defined in the .sbs file

        :return: A list of :class:`.SBSGroup` object
        """
        return self.getContent().getSBSGroupList(aRecursive = True)

    @handle_exceptions()
    def getSBSGroupInternalPath(self, aUID, addDependencyUID=False):
        """
        getSBSGroupInternalPath(aUID, addDependencyUID=False)
        Get the path of the given group relatively to the current package (pkg:///.../aGroupIdentifier)

        :param aUID: the UID of the group to search
        :type aUID: str
        :param addDependencyUID: True to add the tag '?dependency=<uid>' at the end of the internal path. Default to False
        :type addDependencyUID: bool, optional
        :return: A string containing the relative path from the root content to the given group, None otherwise
        """
        return self.getObjectInternalPath(aUID= aUID, aObjectClass=SBSGroup, addDependencyUID=addDependencyUID)

    @handle_exceptions()
    def getMDLGraphInternalPath(self, aUID, addDependencyUID=False):
        """
        getMDLGraphInternalPath(aUID, addDependencyUID=False)
        Get the path of the given MDL graph relatively to the current package (pkg:///.../aGraphIdentifier)

        :param aUID: the UID of the MDL graph to search
        :type aUID: str
        :param addDependencyUID: True to add the tag '?dependency=<uid>' at the end of the internal path. Default to False
        :type addDependencyUID: bool, optional
        :return: A string containing the relative path from the root content to the given graph, None otherwise
        """
        return self.getObjectInternalPath(aUID= aUID, aObjectClass=mdl.MDLGraph, addDependencyUID=addDependencyUID)

    @handle_exceptions()
    def getSBSGraphInternalPath(self, aUID, addDependencyUID=False):
        """
        getSBSGraphInternalPath(aUID, addDependencyUID=False)
        Get the path of the given graph relatively to the current package (pkg:///.../aGraphIdentifier)

        :param aUID: the UID of the Substance graph to search
        :type aUID: str
        :param addDependencyUID: True to add the tag '?dependency=<uid>' at the end of the internal path. Default to False
        :type addDependencyUID: bool, optional
        :return: A string containing the relative path from the root content to the given graph, None otherwise
        """
        return self.getObjectInternalPath(aUID= aUID, aObjectClass=graph.SBSGraph, addDependencyUID=addDependencyUID)

    @handle_exceptions()
    def getSBSGraphPkgUrl(self, aGraph):
        """
        getSBSGraphPkgUrl(aGraph)
        Get the path of the given graph relatively to the current package (pkg:///.../aGraphIdentifier)

        :param aGraph: Identifier of the graph to get
        :type aGraph: A :class:`.SBSGraph` object
        :return: A string containing the relative path from the root content to the given graph, None otherwise
        """
        return self.getSBSGraphInternalPath(aGraph.mUID)


    @handle_exceptions()
    def getSBSFunctionInternalPath(self, aUID, addDependencyUID=False):
        """
        getSBSFunctionInternalPath(aUID, addDependencyUID=False)
        Get the path of the given function relatively to the current package (pkg:///.../aFunctionIdentifier)

        :param aUID: the UID of the function graph to search
        :type aUID: str
        :param addDependencyUID: True to add the tag '?dependency=<uid>' at the end of the internal path. Default to False
        :type addDependencyUID: bool, optional
        :return: A string containing the relative path from the root content to the given function, None otherwise
        """
        return self.getObjectInternalPath(aUID= aUID, aObjectClass=graph.SBSFunction, addDependencyUID=addDependencyUID)

    @handle_exceptions()
    def getSBSResourceInternalPath(self, aUID, addDependencyUID=False):
        """
        getSBSResourceInternalPath(aUID, addDependencyUID=False)
        Get the path of the given resource relatively to the current package (pkg:///.../aResourceIdentifier)

        :param aUID: the UID of the resource to search
        :type aUID: str
        :param addDependencyUID: True to add the tag '?dependency=<uid>' at the end of the internal path. Default to False
        :type addDependencyUID: bool, optional
        :return: A string containing the relative path from the root content to the given resource, None otherwise
        """
        return self.getObjectInternalPath(aUID= aUID, aObjectClass=SBSResource, addDependencyUID=addDependencyUID)

    @handle_exceptions()
    def getObjectInternalPath(self, aUID, aObjectClass=None, addDependencyUID=False):
        """
        getObjectInternalPath(aUID, aObjectClass=None, addDependencyUID=False)
        Get the internal path (*pkg:///myGroup/myObject*) of the object with the given UID

        :param aUID: the UID of the object to search
        :type aUID: str
        :param aObjectClass: class of the object to look for.
        :type aObjectClass: class, optional
        :param addDependencyUID: True to add the tag '?dependency=<uid>' at the end of the internal path. Default to False
        :type addDependencyUID: bool, optional
        :return: the internal path of the object if found, None otherwise
        """
        internalPath = self.getContent().getObjectInternalPath(aUID=aUID, aObjectClass=aObjectClass, aPath = api_helpers.getPkgPrefix())
        if addDependencyUID:
            himselfDep = self.getHimselfDependency()
            if himselfDep is None:
                himselfDep = self.createHimselfDependency()
            internalPath += '?dependency='+himselfDep.mUID
        return internalPath

    @handle_exceptions()
    def getObjectFromInternalPath(self, aPath):
        """
        getObjectFromInternalPath(aPath)
        Get the object pointed by the given path, which must reference the current package.

        :param aPath: the relative path, starting with 'pkg:///'
        :type aPath: str
        :return: the pointed :class:`.SBSObject` if found, None otherwise
        """
        aPath = api_helpers.removePkgPrefix(aPath)
        if aPath == '':
            return self

        folders = aPath.split('/')
        aContent = self.getContent()
        while len(folders) > 1:
            aFolder = folders.pop(0)
            aGroup = aContent.getSBSGroup(aFolder, False)
            if aGroup is None or aGroup.getContent() is None:
                return None
            aContent = aGroup.getContent()

        if len(folders) == 1:
            aPath = api_helpers.splitPathAndDependencyUID(folders[0])[0]
            return aContent.getObject(aIdentifier=aPath)
        return None

    def getObject(self, aObject):
        """
        Find the given object (Group, Graph, Function or Resource) if this package.

        :param aObject: The object to search,  as a SBSObject, a UID, or an internal path (*pkg:///myGroup/myObjectIdentifier*)
        :type aObject: :class:`.SBSObject` or str
        :return: The object if found, None otherwise
        """
        if api_helpers.isAUID(aObject):
            return self.getObjectFromUID(aUID=aObject)
        elif python_helpers.isStringOrUnicode(aObject) and api_helpers.hasPkgPrefix(aObject):
            return self.getObjectFromInternalPath(aPath=aObject)
        elif SBSContent.isContentChildType(aObject):
            return self.getObjectFromUID(aUID=aObject.mUID)
        return None

    @handle_exceptions()
    def getObjectFromUID(self, aUID):
        """
        getObjectFromUID(aUID)
        Parse recursively the content of the package to find the Group, Graph, Resource or Function with the given uid.

        :param aUID: The UID of the object (group, graph, resource or function) to look for
        :type aUID: str
        :return: The :class:`SBSObject` if found, None otherwise
        """
        return self.getContent().getObjectFromUID(aUID, aRecursive=True) if self.mContent else None

    @handle_exceptions()
    def getOrCreateGroup(self, aGroup):
        """
        getOrCreateGroup(aGroup)
        Search for the given group, and create it if not found

        :param aGroup: the group to look for, as a group object, an identifier or a path relative to the package (pkg:///myFolder/myGroup)
        :type aGroup: :class:`.SBSGroup` or str
        :return: The group as a :class:`.SBSGroup`
        """
        aGroupIdentifier = aGroup.mIdentifier if isinstance(aGroup, SBSGroup) else aGroup

        # If a path is given, get/create the folder tree
        if api_helpers.hasPkgPrefix(aGroupIdentifier):
            aGroupIdentifier = api_helpers.removePkgPrefix(aGroupIdentifier)
            aContent = self.getContent()
            aParent = None
            for aFolder in aGroupIdentifier.split('/'):
                if aFolder:
                    aGroup = aContent.getSBSGroup(aFolder, aRecursive=False)
                    if aGroup is None and aFolder:
                        aGroup = self.createGroup(aGroupIdentifier = aFolder, aParentFolder=aParent)
                    aParent = aGroup
                    aContent = aGroup.getContent()

        # Otherwise search recursively to get a group with this identified
        else:
            aGroup = self.getSBSGroup(aGroupIdentifier)
            if aGroup is None:
                aGroup = self.createGroup(aGroupIdentifier = aGroupIdentifier)
        return aGroup

    @handle_exceptions()
    def getParentGroupContent(self, aObject):
        """
        getParentGroupContent(aObject)
        Get the parent group content of the given object (Group, Graph, Function, or Resource).

        :param aObject: The object to consider, as a SBSObject, a UID or an internal path (*pkg:///myGroup/myObjectIdentifier*)
        :type aObject: :class:`.SBSObject` or str
        :return: The parent group content, as a :class:`.SBSContent` object
        """
        myObject = self.getObject(aObject)
        if myObject is None:
            return None

        # Get the parent content
        groupPath = api_helpers.getGroupPathFromInternalPath(self.getObjectInternalPath(myObject.mUID))
        aGroup = self.getObjectFromInternalPath(aPath=api_helpers.getPkgPrefix()+groupPath) if groupPath != '' else self
        return aGroup.getContent() if aGroup else None

    @handle_exceptions()
    def copyDependencyFromPackage(self, aPackage, aDependencyUID):
        """
        copyDependencyFromPackage(aPackage, aDependencyUID)
        Copy the dependency with the given UID from the given package, and paste it in this package.
        This method calls :func:`declareDependencyUIDChanged` at the end in case this dependency was already referenced but was missing.

        :param aPackage: The package where to find the dependency to copy
        :param aDependencyUID: The new dependency UID
        :type aPackage: :class:`.SBSDocument`
        :type aDependencyUID: str
        :return: the copied dependency as a :class:`.SBSDependency`
        :raise: :class:`.SBSImpossibleActionError` in case the dependency is not found in the given package
        """
        aDependency = aPackage.getDependency(aDependencyUID)
        if not aDependency:
            raise SBSImpossibleActionError('Failed to copy the dependency '+str(aDependencyUID)+', cannot find it in the given package')

        if aDependency.isHimself():
            newDep = self.getHimselfDependency()
            aPath = aDependency.mFilename
        else:
            newDep = self.getDependencyFromPath(aDependency.mFileAbsPath)
            aPath = aDependency.mFileAbsPath

        if newDep is None:
            newDep = self.createDependency(aPath=aPath)
            if aDependency.getRefPackage():
                newDep.setRefPackage(aDependency.getRefPackage()())

        # In case the copied dependency was already referenced in the graph, replace the references:
        self.declareDependencyUIDChanged(aDependencyUID, newDep.mUID)
        return newDep

    @handle_exceptions()
    def copyResourceFromPackage(self, aPackage, aResourceUID):
        """
        copyResourceFromPackage(aPackage, aResourceUID)
        Copy the resource with the given UID from the given package, and paste it in this package.
        This method calls :func:`declareResourcePathChanged` at the end in case this resource was already referenced but was missing.

        :param aPackage: The package where to find the dependency to copy
        :param aResourceUID: The new resource UID
        :type aPackage: :class:`.SBSDocument`
        :type aResourceUID: str
        :return: the copied dependency as a :class:`.SBSResource`
        :raise: :class:`.SBSImpossibleActionError` in case the resource is not found in the given package
        """
        aResource = aPackage.getSBSResourceFromUID(aResourceUID)
        if not aResource:
            raise SBSImpossibleActionError('Failed to copy the resource '+str(aResourceUID)+', cannot find it in the given package')

        # Create the resource if it does not exist yet
        isLinked = aResource.isLinked()
        newResource = self.getSBSResourceFromPath(aResource.mFileAbsPath, isLinkedResource=isLinked)
        if newResource is None:

            # For a psd layer, copy the root psd resource too if not already included
            pos = aResource.mFileAbsPath.lower().find('.psd'+os.path.sep)
            isPSD = pos >= 0
            if isPSD:
                newPsdRootRes = self.getSBSResourceFromPath(aResource.mFileAbsPath[:pos+4], isLinkedResource=isLinked)
                psdRootRes = aPackage.getSBSResourceFromPath(aResource.mFileAbsPath[:pos+4], isLinkedResource=isLinked)
                if newPsdRootRes is None and psdRootRes is not None:
                    psdResource = self.copyResourceFromPackage(aPackage, psdRootRes.mUID)

                    aGroup = self.getSBSGroup(psdResource.mIdentifier + '_Resources')
                    for newResource in aGroup.getContent().getSBSResourceList():
                        templateResource = aPackage.getSBSResource(newResource.mIdentifier)
                        oldPath = templateResource.getPkgResourcePath()
                        newPath = newResource.getPkgResourcePath()
                        if oldPath != newPath:
                            self.declareResourcePathChanged(oldPath, newPath)

            else:
                aResourcePath = aResource.getPkgResourcePath()
                pos = aResourcePath.rfind(aResource.mIdentifier)
                aGroup = self.getOrCreateGroup(aResourcePath[0:pos])
                createResFct = self.createLinkedResource if isLinked else self.createImportedResource
                newResource = createResFct(aResourceTypeEnum = aResource.getResourceTypeEnum(),
                                           aIdentifier       = aResource.mIdentifier,
                                           aResourcePath     = aResource.mFileAbsPath,
                                           aParentFolder     = aGroup)

                newResource.mAttributes = copy.deepcopy(aResource.mAttributes)
                newResource.mCookedFormat = copy.deepcopy(aResource.mCookedFormat)
                newResource.mCookedQuality = copy.deepcopy(aResource.mCookedQuality)

        # Update the eventual nodes referencing this resource with its new path
        oldPath = aResource.getPkgResourcePath()
        newPath = newResource.getPkgResourcePath()
        if oldPath != newPath:
            self.declareResourcePathChanged(oldPath, newPath)
        return newResource

    @handle_exceptions()
    def declareDependencyUIDChanged(self, oldDependencyUID, newDependencyUID):
        """
        declareDependencyUIDChanged(oldDependencyUID, newDependencyUID)
        Declare a change of UID of a dependency. All the references to the old UID will be replaced by the new UID.
        Warning: no check is done on the name of the referenced object inside the dependency (Graph identifier for instance)

        :param oldDependencyUID: The previous dependency UID
        :param newDependencyUID: The new dependency UID
        :type oldDependencyUID: str
        :type newDependencyUID: str
        """
        nodes = self.getAllReferencesOnDependency(oldDependencyUID)
        for aNode in nodes:
            if isinstance(aNode, compnode.SBSCompNode):
                if aNode.isAResource():
                    aNode.getCompFilter().changeDependencyUID(newDepUID=newDependencyUID)
                elif aNode.isAnInstance():
                    aNode.getCompInstance().changeDependencyUID(aSBSDocument=self, newDepUID=newDependencyUID)
            elif isinstance(aNode, params.SBSParamNode):
                aNode.changeDependencyUID(aSBSDocument=self, newDepUID=newDependencyUID)
            elif isinstance(aNode, mdl.MDLNode):
                aNode.changeDependencyUID(aSBSDocument=self, oldDepUID=oldDependencyUID, newDepUID=newDependencyUID)

    @handle_exceptions()
    def declareInternalPathChanged(self, aObject, oldPath, newPath):
        """
        declareInternalPathChanged(aObject, oldPath, newPath)
        Declare a change in the internal path of the given object, so that all its references are updated in the current package.

        :param aObject: The object (group, graph, function, resource) that has a new internal path (*pkg:///...*)
        :param oldPath: The previous internal path of the object
        :param newPath: The new internal path of the object
        :type aObject: :class:`.SBSObject`
        :type oldPath: str
        :type newPath: str
        """
        if isinstance(aObject, SBSGroup):
            for aResource in aObject.getSBSResourceList(aRecursive=False, aIncludeSceneResources=True):
                self.declareInternalPathChanged(aResource, aResource.getPkgResourcePath(), self.getObjectInternalPath(aResource.mUID, addDependencyUID=True))

            for aSubObject in list(set().union(aObject.getSBSGraphList(aRecursive=False),
                                               aObject.getSBSFunctionList(aRecursive=False),
                                               aObject.getMDLGraphList(aRecursive=False),
                                               aObject.getSBSGroupList(aRecursive=False))):
                self.declareInternalPathChanged(aObject=aSubObject,
                                                oldPath=api_helpers.splitPathAndDependencyUID(oldPath)[0]+'/'+aSubObject.mIdentifier,
                                                newPath=self.getObjectInternalPath(aSubObject.mUID))

        else:
            if isinstance(aObject, SBSResource):
                aObject.resolveDependency(aSBSDocument=self)

            for aNode in self.getAllInternalReferences(oldPath):
                if isinstance(aNode, compnode.SBSCompNode):
                    if aNode.isAResource():
                        aNode.getCompFilter().changeResourcePath(newPath)
                    elif aNode.isAnInstance():
                        aNode.getCompInstance().changeInstancePath(aParentDocument=self, aInstanceDocument=self, aGraphRelPath=newPath)
                elif isinstance(aNode, params.SBSParamNode):
                    aNode.changeInstancePath(aParentDocument=self, aInstanceDocument=self, aFunctionRelPath=newPath)
                elif isinstance(aNode, mdl.MDLNode):
                    if isinstance(aObject, SBSResource):
                        aNode.changeResourcePath(oldPath, newPath)
                    else:
                        aNode.getMDLImplementation().changeInstancePath(aParentDocument=self, aInstanceDocument=self, aGraphRelPath=newPath)

    @handle_exceptions()
    def declareResourcePathChanged(self, oldPath, newPath):
        """
        declareResourcePathChanged(oldPath, newPath)
        Declare a change of resource path. All the references to the resource will be replaced by the new path.

        :param oldPath: The previous path to the resource (path internal to the package pkg:///myGroup/myResource?dependency=1234567890)
        :param newPath: The new path to the resource (path internal to the package pkg:///myGroup/myResource?dependency=1234567890)
        :type oldPath: str
        :type newPath: str
        """
        nodes = self.getAllReferencesOnResource(oldPath)
        for aNode in nodes:
            if isinstance(aNode, compnode.SBSCompNode):
                aNode.getCompFilter().changeResourcePath(newPath=newPath)
            else:
                aNode.changeResourcePath(oldPath=oldPath, newPath=newPath)

    @handle_exceptions()
    def createGraph(self, aGraphIdentifier='New_Graph', aParentFolder=None, aParameters=None, aInheritance=None, aTemplate=None,
                    searchForExistingReferenceByIdentifier=True, copyInternalReferencedObjects=True):
        """
        createGraph(aGraphIdentifier='New_Graph', aParentFolder=None, aParameters=None, aInheritance=None, aTemplate=None,\
                    searchForExistingReferenceByIdentifier=True, copyInternalReferencedObjects=True)
        Create a new graph with the given identifier inside the given ParentFolder.

        :param aGraphIdentifier: identifier of the graph to create. 'New_Graph' by default
        :param aParentFolder: identifier of the folder in which the graph should be created. \
        If None, the new graph will be added to the root content of the :class:`.SBSDocument`
        :param aParameters: parameters of the graph (among the sbslibrary.sbslibclasses.BaseParameters only)
        :param aInheritance: Inheritance of the parameters
        :param aTemplate: the template path to use to initialize this graph. \
        Can be an enumeration value from :class:`.GraphTemplateEnum` or a path to a graph inside a package:

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.

        :param searchForExistingReferenceByIdentifier: if a template is given, for the nodes that are referencing a graph/function inside the template document,\
        allows to define whether this reference will be searched in the destination package by its identifier, to use this reference instead.\
        This parameter has priority against copyInternalReferencedObjects. Default to True

        :param copyInternalReferencedObjects: if a template is given, determine if the objects internal to the original package must be copied in the document or not.\
        If True, the Graph or Functions defined in the original package can be copied also in this package if they are referenced.\
        If False, these references will be updated to point to the original package, thus adding a dependency over the template. Default to True

        :type aGraphIdentifier: str, optional
        :type aParentFolder: :class:`.SBSGroup` or str, optional
        :type aParameters: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
        :type aTemplate: :class:`.GraphTemplateEnum` or str, optional
        :type searchForExistingReferenceByIdentifier: bool, optional
        :type copyInternalReferencedObjects: bool, optional

        :return: the new :class:`.SBSGraph` object
        """
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        # If a template is provided, get the template graph
        templateGraph = None
        templateDoc = None
        if aTemplate is not None:
            if isinstance(aTemplate, int):
                aTemplate = sbslibrary.getSubstanceGraphTemplatePath(aTemplate)

            templateDocPath, graphRelPath = self.splitPackageObjectPath(aTemplate, aAllowSBSAR=False)
            if templateDocPath != self.mFileAbsPath:
                templateDoc = SBSDocument(aContext=self.mContext, aFileAbsPath=templateDocPath)
                templateDoc.parseDoc()
            else:
                templateDoc = self
            templateGraph = templateDoc.getSBSGraph(graphRelPath)
            if templateGraph is None:
                raise SBSImpossibleActionError('Failed to create a graph from the template '+templateDocPath+', cannot find the graph '+graphRelPath+' in it.')

        # Get or create the ParentFolder content
        aContent = self.__getOrCreateGroupContent(aParentFolder)

        # Ensure having a unique identifier
        aGraphIdentifier = aContent.computeUniqueIdentifier(api_helpers.formatIdentifier(aGraphIdentifier))

        # Create the graph
        aGraph = sbsgenerator.createGraph(aGraphIdentifier = aGraphIdentifier,
                                          aParentObject = self,
                                          aParameters = aParameters,
                                          aInheritance = aInheritance)

        # Add the new graph to the graphs list
        api_helpers.addObjectToList(aContent, 'mGraphs', aGraph)

        # Initialize the graph with the given template
        if templateGraph is not None:
            # Copy the template graph
            for aMember in ['mAttributes','mCompNodes','mGraphOutputs','mGUIObjects','mParamInputs','mPresets','mPrimaryInput','mRoot']:
                setattr(aGraph, aMember, copy.deepcopy(getattr(templateGraph, aMember)))

            if templateDoc != self:
                # Copy all the dependencies used by this graph
                self.__copyDependenciesUsedInObject(aGraph, templateDoc, aParentFolder, searchForExistingReferenceByIdentifier,
                                                    copyInternalReferencedObjects)

                # Handle the resources used in the graph
                resourcesUsed = templateGraph.getAllResourcesUsed(aParentDocument=templateDoc)
                for aResourcePath in resourcesUsed:
                    aResource = templateDoc.getObjectFromInternalPath(aResourcePath)
                    if aResource is not None:
                        self.copyResourceFromPackage(aPackage=templateDoc, aResourceUID=aResource.mUID)

        return aGraph

    @handle_exceptions()
    def createMDLGraph(self, aGraphIdentifier = 'MDL_Material', aParentFolder = None, aCreateOutputNode = True, aTemplate=None,
                    searchForExistingReferenceByIdentifier=True, copyInternalReferencedObjects=True):
        """
        createMDLGraph(aGraphIdentifier = 'MDL_Material', aParentFolder = None)
        Create a new graph with the given identifier inside the given ParentFolder.

        :param aGraphIdentifier: identifier of the graph to create. 'New_Graph' by default
        :param aParentFolder: identifier of the folder in which the graph should be created. If None, the new graph will be added to the root content of the :class:`.SBSDocument`
        :param aCreateOutputNode: True to create the output node. Default to True
        :param aTemplate: the template path to use to initialize this graph.\
        Can be an enumeration value from :class:`.MDLGraphTemplateEnum` or a path to a graph inside a package:

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.

        :param searchForExistingReferenceByIdentifier: if a template is given, for the nodes that are referencing a graph inside the template document,\
        allows to define whether this reference will be searched in the destination package by its identifier, to use this reference instead.\
        This parameter has priority against copyInternalReferencedObjects. Default to True

        :param copyInternalReferencedObjects: if a template is given, determine if the objects internal to the original package must be copied in the document or not.\
        If True, the Graph or Functions defined in the original package can be copied also in this package if they are referenced.\
        If False, these references will be updated to point to the original package, thus adding a dependency over the template. Default to True

        :type aGraphIdentifier: str
        :type aParentFolder: str
        :type aCreateOutputNode: bool
        :type aTemplate: :class:`.MDLGraphTemplateEnum` or str, optional
        :type searchForExistingReferenceByIdentifier: bool, optional
        :type copyInternalReferencedObjects: bool, optional
        :return: the new :class:`.MDLGraph` object
        """
        # If a template is provided, get the template graph
        templateGraph = None
        templateDoc = None
        if aTemplate is not None:
            if isinstance(aTemplate, int):
                aTemplate = mdl.mdldictionaries.getMDLGraphTemplatePath(aTemplate)

            templateDocPath, graphRelPath = self.splitPackageObjectPath(aTemplate, aAllowSBSAR=False)
            if templateDocPath != self.mFileAbsPath:
                templateDoc = SBSDocument(aContext=self.mContext, aFileAbsPath=templateDocPath)
                templateDoc.parseDoc()
            else:
                templateDoc = self
            templateGraph = templateDoc.getMDLGraph(graphRelPath)
            if templateGraph is None:
                raise SBSImpossibleActionError('Failed to create a MDL graph from the template '+templateDocPath+', cannot find the graph '+graphRelPath+' in it.')

        # Get or create the ParentFolder content
        aContent = self.__getOrCreateGroupContent(aParentFolder)

        # Ensure having a unique identifier
        aGraphIdentifier = aContent.computeUniqueIdentifier(api_helpers.formatIdentifier(aGraphIdentifier))

        # Create the graph
        aGraph = sbsgenerator.createMDLGraph(aGraphIdentifier = aGraphIdentifier,
                                             aParentObject = self,
                                             aCreateOutputNode = aCreateOutputNode and templateGraph is None)

        # Add the new graph to the graphs list and return it
        api_helpers.addObjectToList(aContent, 'mMDLGraphs', aGraph)

        # Initialize the graph with the given template
        if templateGraph is not None:
            # Copy the template graph
            for aMember in ['mAttributes','mAnnotations','mParamInputs','mNodes','mGUIObjects','mRoot']:
                setattr(aGraph, aMember, copy.deepcopy(getattr(templateGraph, aMember)))

            if templateDoc != self:
                # Copy all the dependencies used by this graph
                self.__copyDependenciesUsedInObject(aGraph, templateDoc, aParentFolder, searchForExistingReferenceByIdentifier,
                                                    copyInternalReferencedObjects)

                # Handle the resources used in the graph
                resourcesUsed = templateGraph.getAllResourcesUsed()
                for aResourcePath in resourcesUsed:
                    aResource = templateDoc.getObjectFromInternalPath(aResourcePath)
                    if aResource is not None:
                        self.copyResourceFromPackage(aPackage=templateDoc, aResourceUID=aResource.mUID)

        return aGraph

    @handle_exceptions()
    def createGroup(self, aGroupIdentifier = 'Untitled_Folder', aParentFolder = None):
        """
        createGroup(aGroupIdentifier = 'Untitled_Folder', aParentFolder = None)
        Create a new group with the given identifier inside the given ParentFolder.

        :param aGroupIdentifier: identifier of the group to create. 'Untitled_Folder' by default
        :param aParentFolder: identifier of the folder in which the graph should be created. \
        If None, the new graph will be added to the root content of the :class:`.SBSDocument`
        :type aGroupIdentifier: :class:`.SBSGroup` or str, optional
        :type aParentFolder: str, optional

        :return: the new :class:`.SBSGroup` object
        """
        # Get or create the ParentFolder content
        aContent = self.__getOrCreateGroupContent(aParentFolder)

        # Ensure having a unique identifier
        aGroupIdentifier = aContent.computeUniqueIdentifier(api_helpers.formatIdentifier(aGroupIdentifier))

        # Create the group
        aGroup = sbsgenerator.createGroup(aParentObject = self, aGroupIdentifier = aGroupIdentifier)

        # Add the new group to the list and return it
        api_helpers.addObjectToList(aContent, 'mGroups', aGroup)
        return aGroup

    @handle_exceptions()
    def createFunction(self, aFunctionIdentifier='Untitled_Function', aParentFolder=None, aTemplate=None,
                       searchForExistingReferenceByIdentifier=True, copyInternalReferencedObjects=True):
        """
        createFunction(aFunctionIdentifier = 'Untitled_Function', aParentFolder = None)
        Create a new Function with the given identifier inside the given ParentFolder.

        :param aFunctionIdentifier: identifier of the function to create. 'Untitled_Function' by default
        :param aParentFolder: identifier of the folder in which the function should be created. \
        If None, the new function will be added to the root content of the :class:`.SBSDocument`
        :param aTemplate: the template to use to initialize this function, as the a path to a function inside a package:

            - If the function is included in the current package, use: *pkg:///MyFunctionIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyFunctionIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyFunctionIdentifier*
            - Note that if the function identifier is equivalent to the filename, the part */MyFunctionIdentifier* may be omit.

        :param searchForExistingReferenceByIdentifier: if a template is given, for the nodes that are referencing a graph/function inside the template document,\
        allows to define whether this reference will be searched in the destination package by its identifier, to use this reference instead.\
        This parameter has priority against copyInternalReferencedObjects.

        :param copyInternalReferencedObjects: if a template is given, determine if the objects internal to the original package must be copied in the document or not.\
        If True, the Functions defined in the original package can be copied also in this package if they are referenced.\
        If False, these references will be updated to point to the original package. It may add a new dependency. Default to True\

        :type aFunctionIdentifier: str, optional
        :type aParentFolder: :class:`.SBSGroup` or str, optional
        :type aTemplate: str, optional
        :type searchForExistingReferenceByIdentifier: bool, optional
        :type copyInternalReferencedObjects: bool, optional

        :return: the new :class:`.SBSFunction` object
        """
        # If a template is provided, get the template function
        templateFct = None
        templateDoc = None
        if aTemplate is not None:
            templateDocPath, fctRelPath = self.splitPackageObjectPath(aTemplate, aAllowSBSAR=False)
            if templateDocPath != self.mFileAbsPath:
                templateDoc = SBSDocument(aContext=self.mContext, aFileAbsPath=templateDocPath)
                templateDoc.parseDoc()
            else:
                templateDoc = self
            templateFct = templateDoc.getSBSFunction(fctRelPath)
            if templateFct is None:
                raise SBSImpossibleActionError('Failed to create a function from the template '+templateDocPath+', cannot find the function '+fctRelPath+' in it.')

        # Get or create the ParentFolder content
        aContent = self.__getOrCreateGroupContent(aParentFolder)

        # Ensure having a unique identifier
        aFunctionIdentifier = aContent.computeUniqueIdentifier(api_helpers.formatIdentifier(aFunctionIdentifier))

        # Create the function
        aFunction = sbsgenerator.createFunction(aFunctionIdentifier = aFunctionIdentifier, aParentObject = self)

        # Add the new function to the list and return it
        api_helpers.addObjectToList(aContent, 'mFunctions', aFunction)

        # Initialize the function with the given template
        if templateFct is not None:
            # Copy the template function
            for aMember in ['mAttributes','mParamInputs','mType','mParamValue']:
                setattr(aFunction, aMember, copy.deepcopy(getattr(templateFct, aMember)))

            if templateDoc != self:
                # Copy all the dependencies used by this function
                self.__copyDependenciesUsedInObject(aFunction, templateDoc, aParentFolder,
                                                searchForExistingReferenceByIdentifier, copyInternalReferencedObjects)

        return aFunction

    @handle_exceptions()
    def createLinkedResource(self, aResourcePath,
                               aResourceTypeEnum,
                               aParentFolder = 'Resources',
                               aIdentifier = None,
                               aAttributes = None,
                               aCookedFormat = None,
                               aCookedQuality = None,
                               aForceNew = False,
                               isRelToPackage = False,
                               isUdim = False):
        """
        createLinkedResource(aResourcePath, aResourceTypeEnum, aParentFolder = 'Resources', aIdentifier = None, aAttributes = None, aCookedFormat = None, aCookedQuality = None, aForceNew = False)
        Add an external Resource from the given path in the given ParentFolder. Equivalent to 'Link resource' in Substance Designer)

        :param aResourcePath: relative or absolute path to the resource
        :param aResourceTypeEnum: type of the resource (BITMAP/SVG/FONT/SCENE)
        :param aParentFolder: folder where the resource will be added (the group is created if necessary). \
        'Resources' by default. Put None to create the resource at the root of the package
        :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
        :param aAttributes: attributes of the resource
        :param aCookedFormat: bitmap format (JPEG/RAW) (only for BITMAP). Default value is RAW
        :param aCookedQuality: bitmap compression quality (only for BITMAP and SVG). Default value is 0
        :param aForceNew: True to force the resource creation even if it is already included in the package. Default to False
        :param isRelToPackage: the given path is relative, if isRelToPackage is True it is relative to the sbs package otherwise it is relative to cwd.

        :type aResourcePath: str
        :type aResourceTypeEnum: :class:`.ResourceTypeEnum`
        :type aParentFolder: :class:`.SBSGroup` or str, optional
        :type aIdentifier: str, optional
        :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
        :type aCookedFormat: :class:`.BitmapFormatEnum`, optional
        :type aCookedQuality: float between 0 and 1, optional
        :type aForceNew: bool, optional
        :type isRelToPackage: bool, optional

        :return: the new :class:`.SBSResource` object
        """
        # Get or create the ParentFolder content
        aGroup = self.getOrCreateGroup(aParentFolder) if aParentFolder is not None else None

        # Create the resource
        aResource = sbsgenerator.createLinkedResource(aSBSDocument      = self,
                                                      aIdentifier       = aIdentifier,
                                                      aResourcePath     = aResourcePath,
                                                      aResourceTypeEnum = aResourceTypeEnum,
                                                      aResourceGroup    = aGroup,
                                                      aAttributes       = aAttributes,
                                                      aCookedQuality    = aCookedQuality,
                                                      aCookedFormat     = aCookedFormat,
                                                      aForceNew         = aForceNew,
                                                      isRelToPackage    = isRelToPackage,
                                                      isUDIM            = isUdim)
        return aResource

    @handle_exceptions()
    def createImportedResource(self, aResourcePath,
                               aResourceTypeEnum,
                               aParentFolder = 'Resources',
                               aIdentifier = None,
                               aAttributes = None,
                               aCookedFormat = None,
                               aCookedQuality = None):
        """
        createImportedResource(aResourcePath, aResourceTypeEnum, aParentFolder = 'Resources', aIdentifier = None, aAttributes = None, aCookedFormat = None, aCookedQuality = None)
        Add an external Resource from the given path in the given ParentFolder. Equivalent to 'Link resource' in Substance Designer)

        :param aResourcePath: relative or absolute path to the resource
        :param aResourceTypeEnum: type of the resource (BITMAP/SVG/FONT/M_BSDF/LIGHT_PROFILE). Resource SCENE cannot be imported.
        :param aParentFolder: folder where the resource will be added (the group is created if necessary). \
        'Resources' by default. Put None to create the resource at the root of the package.
        :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
        :param aAttributes: attributes of the resource
        :param aCookedFormat: bitmap format (JPEG/RAW) (only for BITMAP). Default value is RAW
        :param aCookedQuality: bitmap compression quality (only for BITMAP and SVG). Default value is 0

        :type aResourcePath: str
        :type aResourceTypeEnum: :class:`.ResourceTypeEnum`
        :type aParentFolder: :class:`.SBSGroup` or str, optional
        :type aIdentifier: str, optional
        :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
        :type aCookedFormat: :class:`.BitmapFormatEnum`, optional
        :type aCookedQuality: float between 0 and 1, optional

        :return: the new :class:`.SBSResource` object
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aResourceTypeEnum == sbsenum.ResourceTypeEnum.NONE or aResourceTypeEnum == sbsenum.ResourceTypeEnum.SCENE:
            raise SBSImpossibleActionError('Cannot import a SCENE resource')

        # Get or create the ParentFolder content
        aGroup = self.getOrCreateGroup(aParentFolder) if aParentFolder is not None else None

        # Create the resource
        if aResourceTypeEnum == sbsenum.ResourceTypeEnum.BITMAP:
            return sbsgenerator.createImportedBitmap(aSBSDocument      = self,
                                                     aIdentifier       = aIdentifier,
                                                     aResourcePath     = aResourcePath,
                                                     aResourceGroup    = aGroup,
                                                     aAttributes       = aAttributes,
                                                     aCookedQuality    = aCookedQuality,
                                                     aCookedFormat     = aCookedFormat)
        elif aResourceTypeEnum == sbsenum.ResourceTypeEnum.SVG:
            return sbsgenerator.createEmbeddedSVG(aSBSDocument      = self,
                                                  aIdentifier       = aIdentifier,
                                                  aResourcePath     = aResourcePath,
                                                  aResourceGroup    = aGroup,
                                                  aAttributes       = aAttributes,
                                                  aCookedQuality    = aCookedQuality)
        else:
            return sbsgenerator.createImportedResource(aSBSDocument      = self,
                                                       aResourceTypeEnum = aResourceTypeEnum,
                                                       aIdentifier       = aIdentifier,
                                                       aResourcePath     = aResourcePath,
                                                       aResourceGroup    = aGroup,
                                                       aAttributes       = aAttributes)


    @handle_exceptions()
    def createSceneResource(self, aResourcePath,
                            aParentFolder = 'Resources',
                            aIdentifier = None,
                            aAttributes = None,
                            isUDIM = False,
                            aForceNew = False):
        """
        createSceneResource(aResourcePath, aParentFolder = 'Resources', aIdentifier = None, aAttributes = None, isUDIM = False, aForceNew = False)
        Add a new Scene Resource from the given path in the given ParentFolder.

        :param aResourcePath: relative or absolute path to the resource
        :param aParentFolder: folder where the resource will be added (the group is created if necessary). \
        'Resources' by default. Put None to create the resource at the root of the package
        :param aIdentifier: Identifier of the resource. If None, the identifier is taken from the resource path
        :param aAttributes: attributes of the resource
        :param isUDIM: True to use UDIMs on this scene resource. Default to False
        :param aForceNew: True to force the resource creation even if it is already included in the package. Default to False

        :type aResourcePath: str
        :type aParentFolder: :class:`.SBSGroup` or str, optional
        :type aIdentifier: str, optional
        :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
        :type isUDIM: bool, optional
        :type aForceNew: bool, optional

        :return: the new :class:`.SBSResource` object
        """
        # Get or create the ParentFolder content
        aGroup = self.getOrCreateGroup(aParentFolder) if aParentFolder is not None else None

        # Create the resource
        aResource = sbsgenerator.createLinkedResource(aSBSDocument      = self,
                                                      aIdentifier       = aIdentifier,
                                                      aResourcePath     = aResourcePath,
                                                      aResourceTypeEnum = sbsenum.ResourceTypeEnum.SCENE,
                                                      aResourceGroup    = aGroup,
                                                      aAttributes       = aAttributes,
                                                      isUDIM            = isUDIM,
                                                      aForceNew         = aForceNew)
        return aResource

    @handle_exceptions()
    def getOrCreateDependency(self, aPath, aAllowSBSAR=False):
        """
        getOrCreateDependency(self, aPath, aAllowSBSAR=False)
        Get the

        :param aPath: path of the object (graph, mdlgraph, function) to reference (absolute, relative to the current .sbs file, or given with an alias, for instance *myalias:/myMdlFile.sbs*)

            - If the object is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the object identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.
        :param aAllowSBSAR: True to allow creating a dependency on a .sbsar file. Default to False

        :type aPath: str
        :type aAllowSBSAR: bool, optional
        
        :return: The list of outputs: [Referenced object, object relative path, Dependency object]
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aPath = aPath.replace('\\', '/')
        if api_helpers.hasPkgPrefix(aPath):
            aGraphRelPath = aPath
            aDependencyPath = '?himself'
        else:
            aDependencyPath, aGraphRelPath = api_helpers.getRelativeObjectPathFromFilePath(aPath)
        # Get/Create the dependency and the reference to the pointed object
        return self.addReferenceOnDependency(aDependencyPath=aDependencyPath, aRelPathToObject=aGraphRelPath)


    @handle_exceptions()
    def addReferenceOnDependency(self, aDependencyPath, aRelPathToObject):
        """
        addReferenceOnDependency(aDependencyPath, aRelPathToObject, outValues)
        This function look for the given dependency and create it if it does not exists yet.
        In the case of a new dependency, parses the pointed package to resolve the dependency.
        Finally, look for the given object identified by its relative path inside the package.
        The return values are a tuple: (:class:`.SBSObject` (The pointed object), str (The resolved relative path))

        :param aDependencyPath: The path of the dependency
        :param aRelPathToObject: The path to the referenced object, relatively to its parent package
        :type aDependencyPath: str
        :type aRelPathToObject: str
        :return: Tuple (:class:`.SBSObject` (The pointed object), str (The resolved relative path))
        """
        # Get or create the dependency
        aDependency = self.getDependencyFromPath(aDependencyPath)
        aDepCreated = False
        if aDependency is None:
            aDependency = self.createDependency(aDependencyPath)
            aDepCreated = True

        # Build the relative path from file path
        _, aRelPathFromFile = api_helpers.getRelativeObjectPathFromFilePath(aDependency.mFileAbsPath)
        if aRelPathToObject is None:
            aRelPathToObject = aRelPathFromFile

        # Resolve the dependency and get the referenced package
        aRefPackage = aDependency.getRefPackage()
        if aRefPackage is None:
            aRefPackage = self.mContext.resolveDependency(self, aDependency)
        if aRefPackage is None:
            if aDepCreated:
                self.mDependencies.remove(aDependency)
            raise SBSMissingDependencyError("Dependency package was not found or is incompatible : {}".format(aDependencyPath),
                                            aDependencyPath)

        # Get the pointed object inside this package
        aObject = aRefPackage().getObjectFromInternalPath(aRelPathToObject)
        # if graph 'filename' was not found and there is not an explicit graph name, take the first one if it exist.
        if aObject is None and aRelPathToObject == aRelPathFromFile:
            aObject = aRefPackage().getSBSGraphList()[0] if aRefPackage().getSBSGraphList() else None
            if aObject:
                aRelPathToObject = aRefPackage().getSBSGraphPkgUrl(aObject)

        # if nothing was found raise
        if aObject is None:
            if aDepCreated:
                self.mDependencies.remove(aDependency)
            if aRelPathToObject is None:
                raise SBSMissingDependencyError(
                    "Dependency was not found, package does not have graph : {}".format(aDependencyPath),
                    aDependencyPath)
            raise SBSMissingDependencyError("Dependency was not found from relative path : {}".format(aRelPathToObject),
                                            aRelPathToObject)

        # Complete the relative with the reference to the dependency
        aRelPathToObject += '?dependency=' + aDependency.mUID

        return aObject, aRelPathToObject, aDependency

    @handle_exceptions()
    def getAllInternalReferences(self, aInternalPath=None):
        """
        getAllInternalReferences(aInternalPath=None)
        Get all the SBSNode that are referencing the given internal path (graph, function, resource), or the current package \
        (e.g. pointing to 'himself' dependency) if aInternalPath is let None

        :param aInternalPath: the internal path to look for. Default to None to search all the references of ?himself dependency
        :type aInternalPath: str, optional
        :return: A list of :class:`.SBSNode`
        """
        # Get all the nodes referencing the 'himself' dependency
        himselfDep = self.getHimselfDependency()
        aNodes = self.getAllReferencesOnDependency(himselfDep) if himselfDep else []
        if himselfDep is None or aInternalPath is None:
            return aNodes

        # Add the 'himself' dependency UID if it is missing in the given path
        if not api_helpers.splitPathAndDependencyUID(aInternalPath)[1]:
            aInternalPath += '?dependency='+himselfDep.mUID

        # Keep only the references to the specific given internal path
        return [aNode for aNode in aNodes if aNode.hasAReferenceOnInternalPath(aInternalPath)]

    @handle_exceptions()
    def getAllReferencesOnDependency(self, aDependency):
        """
        getAllReferencesOnDependency(aDependency)
        Get all the SBSNode that are referencing the given dependency

        :param aDependency: The dependency to look for (object or UID)
        :type aDependency: :class:`.SBSDependency` or str
        :return: A list of :class:`.SBSNode`
        """
        refNodeList = []
        for aObj in self.getSBSGraphList() + self.getMDLGraphList() + self.getSBSFunctionList():
            refNodeList.extend(aObj.getAllReferencesOnDependency(aDependency))
        return refNodeList

    @handle_exceptions()
    def getAllReferencesOnResource(self, aResource):
        """
        getAllReferencesOnResource(aResource)
        Get all the SBSNode that are referencing the given resource

        :param aResource: The resource to look for (object or path internal to the package (pkg:///myGroup/myResource)
        :type aResource: :class:`.SBSResource` or str
        :return: A list of :class:`.SBSNode`
        """
        refNodeList = []
        for aGraph in self.getSBSGraphList() + self.getMDLGraphList():
            refNodeList.extend(aGraph.getAllReferencesOnResource(aResource))
        return refNodeList

    @handle_exceptions()
    def getDescription(self):
        """
        getDescription()
        Get the substance description

        :return: The textual description of the substance
        """
        return self.mDescription

    @handle_exceptions()
    def setDescription(self, aDescription):
        """
        setDescription(aDescription)
        Set the given description

        :param aDescription: the textual substance description
        :type aDescription: str
        """
        self.mDescription = python_helpers.castStr(aDescription)

    @handle_exceptions()
    def removeDependency(self, aDependency, aCheckUsage=True):
        """
        removeDependency(aDependency)
        Remove the dependency from the SBSDocument, if there is no more reference on it in the content.

        :param aDependency: The dependency to remove (UID or object)
        :param aCheckUsage: True check if the dependency is used in the package, and raise an exception if it is the case. False to remove without checking. Default to True
        :type aDependency: str or :class:`.SBSDependency`
        :type aCheckUsage: bool, optional
        :return: True if success, False if the dependency was not used by this Substance
        :raise: :class:`api_exceptions.SBSImpossibleActionError` if the dependency is still used by the Substance content
        """
        if python_helpers.isStringOrUnicode(aDependency):
            aDependency = self.getDependency(aDependency)
        if aDependency in self.mDependencies:
            if aCheckUsage:
                refList = self.getAllReferencesOnDependency(aDependency)
                if len(refList) > 0:
                    raise SBSImpossibleActionError('Cannot remove the dependency '+aDependency.mFileAbsPath+', it is still used by '+str(len(refList))+' nodes')
            self.mDependencies.remove(aDependency)
            return True
        return False

    @handle_exceptions()
    def moveObjectUnderGroup(self, aObject, aGroup=None):
        """
        moveObjectUnderGroup(aObject, aGroup=None)
        Moves the given object under the given group. If aGroup is let None, moves the object under the root content.

        :param aObject: The object to move, as a SBSObject, a UID or an internal path
        :param aGroup: The destination group, as a :class:`.SBSGroup`, a UID or an internal path. Can be None to put the object at the root of the package
        :type aObject: :class:`.SBSObject` or str
        :type aGroup: :class:`.SBSGroup` or str, optional
        """
        aInput = aObject
        aObject = self.getObject(aObject)
        if aObject is None:
            raise SBSImpossibleActionError('Cannot find the object '+python_helpers.castStr(aInput)+' in this package')

        # Get the destination group
        if aGroup is None:
            aGroup = self
        else:
            aInput = aGroup
            aGroup = self.getObject(aGroup)
            if not isinstance(aGroup, SBSGroup):
                raise SBSImpossibleActionError('Cannot find the group '+python_helpers.castStr(aInput)+' in this package')
        aContent = aGroup.getContent()
        isAResource = isinstance(aObject, SBSResource)
        oldInternalPath = self.getObjectInternalPath(aObject.mUID, addDependencyUID=isAResource)

        # Remove the object from its current parent
        currentContent = self.getParentGroupContent(aObject)
        currentContent.removeObject(aObject)

        # Add the object under its new parent
        if   isinstance(aObject, SBSGroup):             aMember = 'mGroups'
        elif isinstance(aObject, graph.SBSGraph):       aMember = 'mGraphs'
        elif isinstance(aObject, graph.SBSFunction):    aMember = 'mFunctions'
        elif isinstance(aObject, SBSResourceScene):     aMember = 'mResourcesScene'
        elif isinstance(aObject, SBSResource):          aMember = 'mResources'
        else:                                           aMember = 'mMDLGraphs'
        api_helpers.addObjectToList(aContent, aMember, aObject)

        # Update all references to the moved object inside the package
        self.declareInternalPathChanged(aObject, oldPath=oldInternalPath, newPath=self.getObjectInternalPath(aObject.mUID, addDependencyUID=isAResource))

    @handle_exceptions()
    def relocateResource(self, aResource, aNewPath, checkPathExists = True):
        """
        relocateResource(aResource, aNewPath)
        Relocate the given linked resource to the given path (absolute or relative to this document).

        :param aResource: the resource to relocate, as a SBSResource object or an internal path (pkg:///myGroup/myResource)
        :param aNewPath: the new path to the resource
        :type aResource: :class:`.SBSResource` or str
        :type aNewPath: str
        :param checkPathExists: whether to check the existence of the path. Default to True
        :type checkPathExists: bool, optional
        :return: True if success
        :raise: :class:`.SBSImpossibleActionError`
        """
        aInput = aResource
        aResource = self.getObject(aResource)
        if aResource is None:
            raise SBSImpossibleActionError('Failed to relocate the resource '+python_helpers.castStr(aInput)+', cannot find it in the document')
        if not aResource.isLinked():
            raise SBSImpossibleActionError('Cannot relocate an imported resource ('+aResource.getPkgResourcePath()+')')
        aExtension = api_helpers.splitExtension(aNewPath)[1]
        if not SBSResource.isAllowedExtension(aResource.mType, aExtension):
            raise SBSImpossibleActionError('File extension ('+aExtension+') not supported for this kind of resource ('+aResource.mFormat+')')

        aFileAbsPath = self.mContext.getUrlAliasMgr().toAbsPath(aNewPath, self.mDirAbsPath)
        aRelPath = self.mContext.getUrlAliasMgr().toRelPath(aNewPath, self.mDirAbsPath)
        if checkPathExists and not os.path.exists(aFileAbsPath):
            raise IOError("The resource %s does not exists" % python_helpers.castStr(aFileAbsPath))

        aResource.mFileAbsPath = aFileAbsPath
        aResource.mFilePath = aRelPath.replace('\\', '/')
        aResource.mFormat = aExtension[1:]
        return True

    @handle_exceptions()
    def removeObject(self, aObject):
        """
        removeObject(aObject)
        Remove the given object from this package.\
        Warning, no check is done to ensure that this object is referenced in this package. \
        You can use :func:`getAllInternalReferences()` to get the internal references of this object.

        :param aObject: The object (group, graph, function, resource) to remove from this content, as a SBSObject or given its UID
        :type aObject: :class:`.SBSObject` or UID
        :return: True if success
        """
        myObject = self.getObject(aObject)
        if myObject is None:
            raise SBSImpossibleActionError('Cannot remove the object '+python_helpers.castStr(aObject)+' from this package, cannot find it')

        # Remove the object from its parent content
        parentContent = self.getParentGroupContent(myObject)
        return parentContent.removeObject(myObject)

    @handle_exceptions()
    def deleteSBSGraph(self, aGraph, force=False):
        """
        deleteSBSGraph(aGraph)
        Remove the given object from this package.

        :param aGraph: The sbs graph to delete
        :type aGraph: :class:`.SBSGraph` or UID
        :param force: Whether to remove the object even if there are references to it or not
        :type force: bool
        :return: True if success
        """
        resource_path = self.getSBSGraphInternalPath(aGraph.mUID)
        if aGraph is None:
            raise SBSImpossibleActionError(
                'Cannot delete the object ' + resource_path + ' from this package, cannot find it')
        internal_refs = self.getAllInternalReferences(resource_path)
        if len(internal_refs) == 0:
            return self.removeObject(aGraph)
        elif len(internal_refs) > 0 and force:
            # There are internal references and we are force the delete
            log.warning("Force deleting object: {} when there are internal references to it".format(resource_path))
            return self.removeObject(aGraph)
        else:
            # There are internal references but we are not forcing the delete
            log.warning("Tried to delete object: {} but there are internal references to it, use the force flag to "
                        "delete anyway".format(resource_path))
            return False

    @handle_exceptions()
    def setObjectIdentifier(self, aObject, aIdentifier):
        """
        setObjectIdentifier(aObject, aIdentifier)
        Set the identifier of the given object (Group, Graph, Function or Resource), and update all internal references to this object with the new identifier.

        :param aObject: The object to rename, as a SBSObject, a UID or an internal path (*pkg:///myGroup/myObjectIdentifier*)
        :param aIdentifier: The new identifier to set
        :type aObject: :class:`.SBSObject` or UID
        :type aIdentifier: str
        :return: the identifier set, as it can be modified to ensure uniqueness of identifiers
        """
        myObject = self.getObject(aObject)
        if myObject is None:
            raise SBSImpossibleActionError('Cannot set the identifier of '+python_helpers.castStr(aObject)+', cannot find it in this package')

        aIdentifier = api_helpers.formatIdentifier(aIdentifier)
        if myObject.mIdentifier != aIdentifier:
            currentPath = self.getObjectInternalPath(aUID=myObject.mUID)
            aContent = self.getParentGroupContent(aObject=aObject)
            aIdentifier = aContent.computeUniqueIdentifier(aIdentifier)
            myObject.mIdentifier = aIdentifier
            self.declareInternalPathChanged(aObject=myObject,
                                            oldPath=currentPath,
                                            newPath=self.getObjectInternalPath(myObject.mUID))
        return aIdentifier

    @handle_exceptions()
    def splitPackageObjectPath(self, aPath, aAllowSBSAR=False):
        """
        splitPackageObjectPath(aPath, aAllowSBSAR=False)
        Split the given path to a path to a package (.sbs/.sbsar) and a relative to the object pointed into it.

        :param aPath: path of an object inside a package (absolute, relative to the current .sbs file, or given with an alias, for instance *sbs://anisotropic_noise.sbs*)

            - If the object is included in the current package, use: *pkg:///MyObjectIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyObjectIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyObjectIdentifier*
            - Note that if the object identifier is equivalent to the filename, the part */MyObjectIdentifier* may be omit.

        :param aAllowSBSAR: True to allow considering a sbsar package. Default to False
        :type aPath: str
        :type aAllowSBSAR: bool, optional
        :return: a tuple (packagePath, objectRelativePath), where packagePath is the absolute path to the package,\
        and objectRelativePath is the path of the object as an internal path (pkg:///MyObjectIdentifier)
        """
        # Build the dependency path and graph relative path inside its package
        aObjectRelPath = None
        aPath = aPath.replace('\\', '/')

        if api_helpers.hasPkgPrefix(aPath):
            aObjectRelPath = aPath
            aDependencyPath = self.mFileAbsPath
        else:
            pos = aPath.find('.sbs')
            if pos > 0:
                end = pos + 6 if aAllowSBSAR and len(aPath) > pos + 5 and aPath[pos + 4:pos + 6] == 'ar' else pos + 4
                if len(aPath) > end and aPath[end] == '/':
                    aObjectRelPath = api_helpers.getPkgPrefix() + aPath[end + 1:]
                    aPath = aPath[0:end]
                else:
                    aObjectRelPath = api_helpers.getPkgPrefix() + api_helpers.splitExtension(aPath)[0]

            aDependencyPath = self.mContext.getUrlAliasMgr().toAbsPath(aUrl=aPath, aDirAbsPath=self.mFileAbsPath)

        return aDependencyPath, aObjectRelPath


    @handle_exceptions()
    def getSBSMetaDataTree(self):
        """
        Get the SBSMetaDataTree structure.

        :return: class `.SBSMetaDataTree`
        """
        return self.mMetaDataTree

    @handle_exceptions()
    def getAllMetaData(self):
        """
        Get all MetaData under dictionary form.

        :return: dict
        """
        metadata = {}
        if not self.mMetaDataTree:
            return metadata
        urls = self.mMetaDataTree.mMetaDataTreeUrlList or []
        strings = self.mMetaDataTree.mMetaDataTreeStrList or []
        metadata.update({url.mName: url.mValue for url in urls})
        metadata.update({string.mName: string.mValue for string in strings})
        return metadata

    @handle_exceptions()
    def getMetaData(self, aName):
        """
        Get a MetaData by its name

        :param aName:
        :type aName: str
        :return: :class:`.SBSMetaDataTreeUrl` or :class:`.SBSMetaDataTreeStr`
        """
        if not self.mMetaDataTree:
            return None
        urls = self.mMetaDataTree.mMetaDataTreeUrlList or []
        strings = self.mMetaDataTree.mMetaDataTreeStrList or []
        aMetaData = [x for x in strings+urls if x.mName == aName]
        return aMetaData[0] if aMetaData else None

    @handle_exceptions()
    def createMetaDataStr(self, aName, aValue):
        """
        Create a metadata of type Str.

        :param aName:
        :type aName: str
        :param aResource:
        :type aResource: :class:`.SBSResource` object
        :return: A :class:`.SBSMetaDataUrl` object
        """
        if not self.mMetaDataTree:
            self.mMetaDataTree = SBSMetaDataTree()
        if not self._isAvailableMetaDataName(aName):
            raise SBSMetaDataTreeNameConflict("Name '{0}' is already used by an other metadata.".format(aName))
        self.mMetaDataTree.mMetaDataTreeStrList.append(SBSMetaDataTreeStr(aName, aValue))

    @handle_exceptions()
    def createMetaDataUrl(self, aName, aResource):
        """
        Create a metadata of type Url.

        :param aName:
        :type aName: str
        :param aResource:
        :type aResource: :class:`.SBSResource` object
        :return: A :class:`.SBSMetaDataUrl` object
        """
        if not self.mMetaDataTree:
            self.mMetaDataTree = SBSMetaDataTree()
        if not self._isAvailableMetaDataName(aName):
            raise SBSMetaDataTreeNameConflict("Name '{0}' is already used by an other metadata.".format(aName))
        self.mMetaDataTree.mMetaDataTreeUrlList.append(SBSMetaDataTreeUrl(aName, aResource))

    @handle_exceptions()
    def deleteMetaData(self, aName):
        """
        Delete a metadata, return True if success.

        :param aName:
        :type aName: str
        :return: bool
        """
        metadata = self.getMetaData(aName)
        if metadata:
            try:
                self.mMetaDataTree.mMetaDataTreeUrlList.remove(metadata)
                self.mMetaDataTree.mMetaDataTreeStrList.remove(metadata)
            except ValueError:
                return True
        return False


    @handle_exceptions()
    def _isAvailableMetaDataName(self, aName):
        """
        check if a metadata already exist with this name.

        :return: bool
        """
        metadata_dict = self.getAllMetaData()
        if aName in metadata_dict.keys():
            return False
        return True

    #==========================================================================
    # Private
    #==========================================================================

    def __copyDependenciesUsedInObject(self, aCopiedObject, aTemplatePackage, aParentFolder,
                                       searchForExistingReferenceByIdentifier, copyInternalReferencedObjects):
        # Copy all the dependencies used by this graph
        dependencyUIDList = aCopiedObject.getAllDependencyUID()
        dependencyList = [aTemplatePackage.getDependency(aUID) for aUID in dependencyUIDList]

        for templateDep in dependencyList:
            if templateDep is None:
                continue

            # Copy the dependency and link the eventual already present references to it
            if not templateDep.isHimself():
                self.copyDependencyFromPackage(aPackage=aTemplatePackage, aDependencyUID=templateDep.mUID)

            # Handle all the internal dependencies: create or relink the referenced graph / function
            else:
                referencedGraphs = {}
                referencedFunctions = {}
                referencedMDLGraphs = {}

                # Get all the graphs/functions referenced in the copied object, that are defined in the template package (himself dependency)
                internalRefNodes = aCopiedObject.getAllReferencesOnDependency(templateDep.mUID)
                for aNode in internalRefNodes:
                    aPath = None
                    aReferenceListObj = None
                    if isinstance(aNode, compnode.SBSCompNode) and aNode.isAnInstance():
                        aPath = aNode.getCompInstance().getReferenceInternalPath()
                        aReferenceListObj = referencedGraphs

                    elif isinstance(aNode, params.SBSParamNode):
                        aPath = aNode.getReferenceInternalPath()
                        aReferenceListObj = referencedFunctions

                    elif isinstance(aNode, mdl.MDLNode):
                        if aNode.isSBSInstance():
                            aPath = aNode.getMDLImplSBSInstance().getReferenceInternalPath()
                            aReferenceListObj = referencedGraphs
                        elif aNode.isMDLGraphInstance():
                            aPath = aNode.getMDLImplMDLGraphInstance().getReferenceInternalPath()
                            aReferenceListObj = referencedMDLGraphs

                    if aPath is not None and aReferenceListObj is not None:
                        if aPath in aReferenceListObj:  aReferenceListObj[aPath].append(aNode)
                        else:                           aReferenceListObj[aPath] = [aNode]

                # Parse all lists of references, and recreate the graphs/functions in the destination package
                getObjectFcts = [self.getSBSGraph, self.getSBSFunction, self.getMDLGraph]
                createObjectFcts = [self.createGraph, self.createFunction, self.createMDLGraph]

                for i,aReferences in enumerate([referencedGraphs,referencedFunctions, referencedMDLGraphs]):
                    for aGraphPath, aNodes in list(aReferences.items()):
                        aGroup, aIdentifier = api_helpers.splitGroupAndIdentifierFromInternalPath(aGraphPath)
                        aGroup = aGroup+'/' if aGroup else ''
                        aDocForResolution = self
                        newGraph = None

                        if searchForExistingReferenceByIdentifier:
                            newGraph = self.getObjectFromInternalPath(aPath=aGraphPath) or getObjectFcts[i](aIdentifier)

                        if newGraph is None:
                            if copyInternalReferencedObjects:
                                newGraph = createObjectFcts[i](aIdentifier,
                                                               aParentFolder=aParentFolder,
                                                               aTemplate=aTemplatePackage.mFileAbsPath + '/' + aGroup + aIdentifier,
                                                               searchForExistingReferenceByIdentifier=True,
                                                               copyInternalReferencedObjects=copyInternalReferencedObjects)
                                aGraphPath = self.getObjectInternalPath(aUID=newGraph.mUID)
                            else:
                                aDocForResolution = aTemplatePackage

                        for aNode in aNodes:
                            try:
                                if  isinstance(aNode,compnode.SBSCompNode): aInstance = aNode.getCompInstance()
                                elif isinstance(aNode, mdl.MDLNode):        aInstance = aNode.getMDLImplementation()
                                else:                                       aInstance = aNode
                                aInstance.changeInstancePath(self, aDocForResolution, aGraphPath)

                            except SBSImpossibleActionError as error:
                                log.error(error)


    def __getOrCreateGroupContent(self, aGroup):
        # Get or create the Group
        if aGroup is not None:
            aParentGroup = self.getOrCreateGroup(aGroup)
            aContent = aParentGroup.getContent()
        else:
            aContent = self.getContent()

        if aContent is None:
            aContent = SBSContent()
        return aContent
