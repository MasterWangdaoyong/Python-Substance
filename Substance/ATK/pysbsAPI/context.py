# coding: utf-8
"""
Module **context** provides object relatives to the execution environment (file path, platform, aliases for package).
"""

from __future__ import unicode_literals
import os
import re
import copy
import platform
import tempfile
import logging
log = logging.getLogger( __name__ )

from distutils.version import LooseVersion
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse
from pysbs.api_decorators import handle_exceptions
from pysbs.api_exceptions import SBSLibraryError
from pysbs import sbsproject
from pysbs import api_helpers, python_helpers, common_interfaces, substance, sbsarchive, sbsenum
from pysbs.mdl import MDLManager
from pysbs.api_decorators import doc_inherit,handle_exceptions


# ==============================================================================
@doc_inherit
class ProjectMgr:
    """
    Class that manage the sbsprj (currently, readonly).
    For instance it's usable to get params values i.e: aSbsPrj.getSettingsInfo().getVersion().getValue()
    Or populate the AliasUrlMgr with the alias' sbsprj file.
    It is retrievable by a Context: aContext.getProjectMgr() a aSbsPrjFilePath file path can be pass as arg.
    Or as create an instance aPrjMgr = ProjectMgr() a aSbsPrjFilePath file path can be pass as arg.
    The context is also retrievable directly from aPrjMgr.
    """
    def __init__(self, aContext=None, aSbsPrjFilePath=None, aSBSProject=None):
        self.mContext = aContext if isinstance(aContext, Context) else Context()
        self.mSBSProject = aSBSProject if isinstance(aContext, sbsproject.SBSPRJProject) else sbsproject.SBSPRJProject()
        self.mSbsPrjFilePath = []
        self.mIsParsed = False
        self.mNotNearOrUnderMethod = sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE
        self.mNearOrUnderMethod = sbsproject.SBSPRJDependenciesPathStorageMethods.RELATIVE
        self.mColorManagement = sbsproject.SBSPRJColorManagementMethods.LEGACY
        self.mOcioConfigFilePath = None
        if aSbsPrjFilePath and self.mSBSProject:
            if not isinstance(aSbsPrjFilePath, list):
                aSbsPrjFilePath = [aSbsPrjFilePath]
            for sbsPrj in aSbsPrjFilePath:
                self.parseADoc(sbsPrj)

    def parseADoc(self, aSbsPrjFilePath):
        """
        Parse the sbsprj file in order to populate the ProjectMgr

        :param aSbsPrjFilePath: a sbsprj file
        :return:
        """
        self.mSBSProject.mSbsPrjFilePath.append(aSbsPrjFilePath)
        if not self.mSbsPrjFilePath:
            self.mSbsPrjFilePath = [aSbsPrjFilePath]
        else:
            self.mSbsPrjFilePath.append(aSbsPrjFilePath)
        self.mSBSProject.parseDoc(self.mContext)

    def populateUrlAliasesMgr(self):
        """
        Complete UrlAliasesMgr with the sbsprj's aliases

        :return:
        """
        aAliasMgr = self.mContext.mUrlAliasMgr
        aUrlAliases = self.mSBSProject.mPreferences.mResources.mUrlAliases or []
        for alias in aUrlAliases:
            aAliasMgr.mUrlDict[alias.mName.mElementContent] = aAliasMgr.toAbsPath(
               aAliasMgr.urlToFilePath(alias.mPath.getValue()),
               os.path.dirname(alias.mParentSbsPrj))

    def getDependenciesPathStorageMethod(self, method=sbsproject.SBSPRJDependenciesPathTypes.NOT_NEAR_OR_UNDER):
        """
        Shortcut in order to get the dependencies path storage method

        :param method: not_near_or_under or near_or_under
        :return: SBSPRJDependenciesPathStorageMethods
        """
        if method == sbsproject.SBSPRJDependenciesPathTypes.NOT_NEAR_OR_UNDER:
            if self.mSBSProject.mIsParsed:
                return self.mSBSProject.mPreferences.mGeneral.mDependencies.mPathStorageMethods.mNotNearOrUnder.getValue()
            else:
                return self.mNotNearOrUnderMethod
        elif method == sbsproject.SBSPRJDependenciesPathTypes.NEAR_OR_UNDER:
            if self.mSBSProject.mIsParsed:
                return self.mSBSProject.mPreferences.mGeneral.mDependencies.mPathStorageMethods.mNearOrUnder.getValue()
            else:
                return self.mNearOrUnderMethod

    def getOcioConfigFilePath(self):
        """
        Shortcut in order to get the config.ocio path

        :return: str
        """
        ocioEnv = os.environ.get("OCIO")
        if not ocioEnv:
            if self.mSBSProject.mIsParsed:
                aColorEngine = self.mSBSProject.mPreferences.mColorManagement.mColorManagementEngine.getValue()
                if aColorEngine is sbsproject.SBSPRJColorManagementMethods.LEGACY:
                    return None
                else:
                    aConfig = self.mSBSProject.mPreferences.mOcio.mOcioConfig.getValue()
                    if aConfig == sbsproject.SBSPRJOcioConfigMethods.CUSTOM:
                        return self.mSBSProject.mPreferences.mOcio.mOcioCustomConfigPath.getValue()
                    elif aConfig == sbsproject.SBSPRJOcioConfigMethods.ACES:
                        # TODO: shared config colormanagement file with batchtools
                        return "a path to aces config"
                    elif aConfig == sbsproject.SBSPRJOcioConfigMethods.SUBSTANCE:
                        # TODO: shared config colormanagement file with batchtools
                        return "a path to susbtance config"
            else:
                return self.mOcioConfigFilePath

    def setOcioConfigFilePath(self, value):
        """
        Shortcut to set the config ocio file path and switch pref to custom

        :param value: str file path of config.ocio
        """
        if self.mSBSProject.mIsParsed:
            self.mSBSProject.mPreferences.mOcio.mOcioCustomConfigPath.setValue(value)
            # switch to custom config ocio engine
            self.mSBSProject.mPreferences.mColorManagement.mColorManagementEngine.setValue(sbsproject.SBSPRJColorManagementMethods.OCIO)
            self.mSBSProject.mPreferences.mOcio.mOcioConfig.setValue(sbsproject.SBSPRJOcioConfigMethods.CUSTOM)
        else:
            self.mOcioConfigFilePath = value
            self.mColorManagement = sbsproject.SBSPRJColorManagementMethods.OCIO

    def setDependenciesPathStorageMethod(self, value, method=sbsproject.SBSPRJDependenciesPathTypes.NOT_NEAR_OR_UNDER):
        """
        Shortcut in order to set the dependencies path storage method

        :param method: sbsproject.SBSDependenciesPathTypes enum
        :param value: sbsproject.SBSDependenciesPathMethods enum
        :return: SBSPRJDependenciesPathStorageMethods
        """
        if method == sbsproject.SBSPRJDependenciesPathTypes.NOT_NEAR_OR_UNDER:
            if self.mSBSProject.mIsParsed:
                self.mSBSProject.mPreferences.mGeneral.mDependencies.mPathStorageMethods.mNotNearOrUnder.setValue(value)
            else:
                self.mNotNearOrUnderMethod = value
        elif method == sbsproject.SBSPRJDependenciesPathTypes.NEAR_OR_UNDER:
            if self.mSBSProject.mIsParsed:
                self.mSBSProject.mPreferences.mGeneral.mDependencies.mPathStorageMethods.mNearOrUnder.setValue(value)
            else:
                self.mNearOrUnderMethod = value

    def getSBSProject(self):
        """
        get the SBSProject class which containt the options

        :return:
        """
        return self.mSBSProject

    def getUrlAliasMgr(self):
        """
        get the SBSProject class which containt the options

        :return:
        """
        return self.mContext.mUrlAliasMgr

    def getContext(self):
        """
        get the Context class from ProjectMgr

        :return:
        """
        return self.mContext


# ==============================================================================
class UrlAliasMgr:
    """
    Class that contains Url Aliases information
    """

    def __init__(self):
        self.mUrlDict = {} # {Name: AbsPath}


    @staticmethod
    def buildTmpFolderPath(aFolderName):
        """
        buildTmpFolderPath(aFolderName)
        Build a temporary folder path in the Substance Automation Toolkit temporary directory, with the given folder name and a unique part (aFolderName_XXXXXX)

        :param aFolderName: The name of the folder to create in the temporary directory
        :type aFolderName: str
        :return: the directory path as a string
        """
        aTmpPath = UrlAliasMgr.getTemporaryDirectoryPath()
        uniquePart = api_helpers.buildUniqueFilePart(6)
        aTmpFolder = os.path.join(aTmpPath, aFolderName + '_')
        while os.path.exists(aTmpFolder + uniquePart):
            uniquePart = api_helpers.buildUniqueFilePart(6)
        return aTmpFolder + uniquePart + os.path.sep

    @staticmethod
    def getTemporaryDirectoryPath():
        """
        Get the temporary folder dedicated to Substance Automation Toolkit

        :return: The temporary folder as a string
        """
        aTmpSSDPath = os.path.normpath(os.path.join(tempfile.gettempdir(), 'Allegorithmic/SubstanceAutomationToolkit/API'))
        python_helpers.createFolderIfNotExists(aTmpSSDPath)
        return aTmpSSDPath

    def getAllAliases(self, includeDefault=False):
        """
        getAllAliases(self, includeDefault=False)
        Get all aliases as a list of strings correctly formatted: alias://path/to/the/alias

        :param includeDefault: True to include the default alias (sbs://). Default to False
        :type includeDefault: bool, optional
        :return: a list of string
        """
        aliasList = []
        for alias, path in self.mUrlDict.items():
            if includeDefault or alias != 'sbs':
                aliasList.append('%s://%s' % (alias, path.replace('\\','/')))
        return aliasList

    def getAliasAbsPath(self, aAliasName):
        """
        Get the absolute path associated to the given alias.

        :param aAliasName: Name of the alias
        :type aAliasName: str
        :return: The absolute path of this alias if found, None otherwise
        """
        return self.mUrlDict.get(aAliasName, None)

    def getAliasInPath(self, aUrl):
        """
        Get the alias part in the given url, if this alias has been declared.
        For instance, if the url is in the format myalias://rest/of/the/path.ext, the function will return 'myalias'
        if this alias has been registered in the aliases dictionary.

        :param aUrl: URL
        :type aUrl: str
        :return: The name of the alias if found, None otherwise
        """
        return next((aliasName for aliasName in self.mUrlDict if aUrl.startswith(aliasName + '://')), None)

    def convertToAliasedPath(self, aUrl):
        """
        Tries to convert the given url with an aliased one.
        If the url starts with the absolute path of a registered alias, this part will be expressed using the alias.
        If no conversion possible, the url is returned as is.

        :param aUrl: The absolute url to convert
        :type aUrl: str
        :return: The same url expressed with an alias if possible, or the url itself otherwise
        """
        for alias, path in list(self.mUrlDict.items()):
            if aUrl.startswith(path):
                resUrl = alias + '://'
                pos = len(path)
                if path[-1] not in ['/','\\']:
                    pos += 1
                resUrl += aUrl[pos:]
                return resUrl.replace('\\', '/')
        return aUrl

    def setAliasAbsPath(self, aAliasName, aAbsPath):
        """
        Save the given alias into the alias dictionary.

        :param aAliasName: Name of the alias, without '://'.
        :param aAbsPath: Absolute directory of this alias
        :type aAliasName: str
        :type aAbsPath: str
        """
        if aAliasName.endswith('://'):
            aAliasName = aAliasName[:-3]
        self.mUrlDict[aAliasName] = os.path.abspath(self.normalizePath(aAbsPath))

    @staticmethod
    def normalizePath(aPath):
        """
        Return a correctly normalized path considering the running OS

        :param aPath: The path to normalize
        :type aPath: str
        :return: The normalized path as a string
        """
        aNorm = os.path.normpath(aPath)

        # normpath does not replace the separator on all os...
        seps = ['/', '\\']
        seps.remove(os.path.sep)
        aNorm = aNorm.replace(seps[0], os.path.sep)
        return aNorm

    def toAbsPath(self, aUrl, aDirAbsPath):
        """
        Convert the given url into an absolute path, considering the given absolute directory path.
        This means that if the url is relative, it will be considered as relative to the given directory path.
        If the url contains a registered alias, the alias part in the url will be replaced by the alias absolute path.
        If the url is already absolute, it will be only formatted correctly for the running platform.

        :param aUrl: The URL to convert to an absolute path
        :param aDirAbsPath: The absolute directory path
        :type aUrl: str
        :type aDirAbsPath: str
        :return: The absolute path corresponding to the given url, correctly formatted for the running platform.
        """
        # If the path starts by an alias, retrieve the absolute path thanks to the alias absolute path
        aliasName = self.getAliasInPath(aUrl)
        if aliasName is not None:
            aliasPath = self.mUrlDict[aliasName]
            absPath = aliasPath
            return self.normalizePath(os.path.join(absPath, aUrl[len(aliasName)+3:]))

        else:
            # Format correctly the path
            aUrl = self.normalizePath(aUrl)

            # File not converted to absPath
            if not os.path.isabs(aUrl):
                # Convert to abs path from the current file
                return os.path.abspath(os.path.join(aDirAbsPath, aUrl))

        return aUrl

    def toRelPath(self, aUrl, aDirAbsPath):
        """
        Convert the given url into a relative path, relatively to the given directory absolute path.
        If the url is expressed using an alias, it will be returned as is.
        If the path of a registered alias is found in the url, it will be expressed with this alias.

        :param aUrl: The URL to convert to a relative path
        :param aDirAbsPath: The absolute directory path
        :type aUrl: str
        :type aDirAbsPath: str
        :return: The relative path corresponding to the given url.
        """
        if self.getAliasInPath(aUrl):
            return aUrl
        aliasedUrl = self.convertToAliasedPath(aUrl)
        try:
            if aliasedUrl != aUrl:
                return aliasedUrl
            elif aUrl and not os.path.isabs(aUrl):
                return aUrl
            else:
                return os.path.relpath(aUrl, aDirAbsPath).replace('\\', '/')
        except ValueError as e:
            # Windows paths on different drives give a ValueError exception but should return an absolute path
            aliasedUrlDrive = os.path.splitdrive(aliasedUrl)
            aliasedDrive = os.path.splitdrive(aDirAbsPath)
            if aliasedUrlDrive[0].lower() != aliasedDrive[0].lower():
                return os.path.abspath(aUrl)
            else:
                # This is not a drive issue on windows,
                # reraise the exception
                raise e

    def isUnderPath(self, aUrl, aDirAbsPath):
        """
        Check if the aUrl path is by or below the aDirAbsPath.
        :param aUrl: The URL to convert to a relative path
        :param aDirAbsPath: The absolute directory path
        :type aUrl: str
        :type aDirAbsPath: str
        :return: True if under aDirAbsPath otherwise False
        """
        aAbsPath = self.toAbsPath(aUrl, aDirAbsPath)
        aNorDirAbsPath = self.normalizePath(aDirAbsPath)
        if aAbsPath == aDirAbsPath:
            return True
        elif aAbsPath.startswith(aNorDirAbsPath + os.path.sep
                                 if not aNorDirAbsPath.endswith(os.path.sep)
                                 else os.path.sep):
            return True
        else:
            return False

    def urlToFilePath(self, aUrl):
        """
        Convert an url type file:///tmp/afile.sbs to a path file /tmp/afile.sbs
        :param aUrl: The URL to convert to a relative path
        :return: a file path
        """
        return urlparse(aUrl).path



    # ==============================================================================
class Context:
    """
    Class used to purpose information on the application environment
    """
    __sParsedPackage = [] # Static variable referencing all the SBSDocument already parsed
    __sSBSFormatVersion = '1.1.0.202001'
    __sSBSUpdaterVersion = '1.1.0.202001'
    __sSBSARFormatVersion = '2.1'

    __sSATPathsSearched = False
    __sSATInstallPath = None
    __sSDInstallPath = None
    __sDefaultPackagePath = None
    __sMDLRootPaths = []
    __sPSDParseExePath = None
    __sBatchToolsFolderPath = None

    __sBatchToolsExe = {sbsenum.BatchToolsEnum.AXFTOOLS: 'axftools'  ,
                        sbsenum.BatchToolsEnum.BAKER:    'sbsbaker'  ,
                        sbsenum.BatchToolsEnum.COOKER:   'sbscooker' ,
                        sbsenum.BatchToolsEnum.MDLTOOLS: 'mdltools'  ,
                        sbsenum.BatchToolsEnum.MUTATOR:  'sbsmutator',
                        sbsenum.BatchToolsEnum.RENDER:   'sbsrender' ,
                        sbsenum.BatchToolsEnum.UPDATER:  'sbsupdater'}

    def __init__(self, aUrlAliasMgr = None, aMDLManager = None, aProjectMgr=None):
        if aUrlAliasMgr is None:
            self.mUrlAliasMgr = UrlAliasMgr()
            # If found, Add the default alias to the dictionary
            if Context.getDefaultPackagePath() is not None:
                self.mUrlAliasMgr.setAliasAbsPath('sbs', Context.getDefaultPackagePath())
        else:
            self.mUrlAliasMgr = aUrlAliasMgr

        if aProjectMgr is None:
            self.mProjectMgr = ProjectMgr(aContext=self, aSBSProject=sbsproject.SBSPRJProject())
        else:
            self.mProjectMgr = aProjectMgr

        if aMDLManager is None:
            self.mMDLMgr = MDLManager()
            self.mMDLMgr.setRootPaths(Context.getMDLRootPaths())
        else:
            self.mMDLMgr = aMDLManager

        self.mObjectsToResolve = []

    @staticmethod
    def getAutomationToolkitInstallPath():
        """
        getAutomationToolkitInstallPath()
        Get Substance Automation Toolkit installation path

        :return: The installation path as a string
        """
        # If not already done, search for SAT installation path
        if not Context.__sSATPathsSearched:
            Context.__computeSATPaths()
        return Context.__sSATInstallPath

    @staticmethod
    def setAutomationToolkitInstallPath(automationToolkitInstallPath):
        """
        setAutomationToolkitInstallPath(automationToolkitInstallPath)
        Set the installation folder of Substance Automation Toolkit

        :param automationToolkitInstallPath: the absolute path to Substance Automation Toolkit installation folder
        :type automationToolkitInstallPath: str
        """
        if not os.path.isdir(automationToolkitInstallPath):
            raise IOError('The provided installation path is not a directory: '+automationToolkitInstallPath)
        Context.__sSATInstallPath = automationToolkitInstallPath

        # Recompute the default path from this new installation folder
        Context.__sDefaultPackagePath = Context.__get_default_package_path(automationToolkitInstallPath)
        Context.__sMDLRootPaths = Context.__get_mdl_root_paths(automationToolkitInstallPath)
        Context.__sPSDParseExePath = Context.__get_psdparse_path(automationToolkitInstallPath)
        Context.__sSATPathsSearched = True

        log.info('SAT Install path: %s', python_helpers.castStr(Context.__sSATInstallPath))
        log.info('Default package: %s', python_helpers.castStr(Context.__sDefaultPackagePath))
        if not Context.__sMDLRootPaths:
            log.warning('Warning, the mdl default library has not been found, you may have trouble when processing MDL graphs using the API')
        if Context.getBatchToolExePath(sbsenum.BatchToolsEnum.MDLTOOLS) is None:
            log.warning('Warning, mdltools executable has not been found, you won\'t be able to read or create MDL graph with the API')

    @staticmethod
    def getSubstanceDesignerInstallPath():
        """
        getSubstanceDesignerInstallPath()
        Get Substance Designer installation path

        :return: The installation path as a string
        """
        # If not already done, search for SAT installation path
        if not Context.__sSATPathsSearched:
            Context.__computeSATPaths()
        return Context.__sSDInstallPath

    @staticmethod
    def setSubstanceDesignerInstallPath(sdInstallPath):
        """
        setSubstanceDesignerInstallPath(sdInstallPath)
        Set the installation folder of Substance Designer

        :param sdInstallPath: the absolute path to Substance Designer installation folder
        :type sdInstallPath: str
        """
        if not os.path.isdir(sdInstallPath):
            raise IOError('The provided installation path is not a directory: '+sdInstallPath)
        Context.__sSDInstallPath = sdInstallPath
        log.info('SD Install path: ' + python_helpers.castStr(Context.__sSDInstallPath))

        # If SAT install folder is currently None, use SD path instead
        if Context.__sSATInstallPath is None:
            Context.__sSATInstallPath = Context.setAutomationToolkitInstallPath(sdInstallPath)
        # Otherwise fill the eventual missing elements
        else:
            if Context.__sDefaultPackagePath is None:
                Context.__sDefaultPackagePath = Context.__get_default_package_path(sdInstallPath)
                log.info('Default package: ' + python_helpers.castStr(Context.__sDefaultPackagePath))
            if Context.__sPSDParseExePath is None:
                Context.__sPSDParseExePath = Context.__get_psdparse_path(sdInstallPath)
            if Context.__sMDLRootPaths is None:
                Context.__sMDLRootPaths = Context.__get_mdl_root_paths(sdInstallPath)

    @staticmethod
    def getDefaultPackagePath():
        """
        getDefaultPackagePath()
        Get the default resource package path, which corresponds to the alias sbs://

        :return: The resource package path as a string
        """
        # If not already done, search for SAT installation path
        if not Context.__sSATPathsSearched:
            Context.__computeSATPaths()
        return Context.__sDefaultPackagePath

    def setDefaultPackagePath(self, defaultLibraryPath):
        """
        setDefaultPackagePath(defaultLibraryPath)
        Set the default package library path, which corresponds to the alias sbs://
        """
        if not os.path.isdir(defaultLibraryPath):
            raise IOError('The provided path for the default package library is not a directory: '+defaultLibraryPath)
        Context.__sDefaultPackagePath = defaultLibraryPath
        self.mUrlAliasMgr.setAliasAbsPath('sbs', Context.getDefaultPackagePath())

    def addMDLRootPath(self, aPath):
        """
        addMDLRootPath(aPath)
        Add the given path to the existing MDL root path list

        :param aPath: The absolute path to add as a MDL root path
        :type aPath: str
        """
        self.mMDLMgr.addRootPath(aPath)

    @staticmethod
    def getMDLRootPaths():
        """
        getMDLRootPaths()
        Get the list of MDL root paths

        :return: The MDL root paths package path as a list of strings
        """
        # If not already done, search for Substance Automation Toolkit installation path
        if not Context.__sSATPathsSearched:
            Context.__computeSATPaths()
        return Context.__sMDLRootPaths

    def setMDLRootPaths(self, aPathList):
        """
        setMDLRootPath(aPathList)
        Set the list of MDL root path

        :param aPathList: The list of absolute paths to add as MDL root paths
        :type aPathList: list of string
        """
        self.mMDLMgr.setRootPaths(aPathList)

    @staticmethod
    def getPSDParseExePath():
        """
        getPSDParseExePath()
        Get PsdParse executable path, which is provided by Substance Automation Toolkit

        :return: The executable path as a string
        """
        # If not already done, search for Substance Automation Toolkit installation path
        if not Context.__sSATPathsSearched:
            Context.__computeSATPaths()
        return Context.__sPSDParseExePath

    @staticmethod
    def getBatchToolExeName(aBatchTool):
        """
        getBatchToolExeName(aBatchTool)
        Get a batch tool executable name

        :param aBatchTool: The batch tool to get
        :type aBatchTool: :class:`.BatchToolsEnum`
        :return: The executable path as a string
        """
        if aBatchTool in Context.__sBatchToolsExe:
            return Context.__sBatchToolsExe[aBatchTool]
        else:
            raise SBSLibraryError('Bad entry for BatchTool, use a value defined in the enumeration sbsenum.BatchToolsEnum')

    @staticmethod
    def getBatchToolExePath(aBatchTool, aBatchToolsFolder=None):
        """
        getBatchToolExePath(aBatchTool, aBatchToolsFolder=None)
        Get the batch tool executable corresponding

        :param aBatchTool: The batch tool to get
        :param aBatchToolsFolder: The batch tools folder path. If not provided, use the Substance Automation Toolkit installation folder.
        :type aBatchTool: :class:`.BatchToolsEnum`
        :type aBatchToolsFolder: str, optional
        :return: The executable path as a string
        """
        if aBatchToolsFolder is None:
            aBatchToolsFolder = Context.getAutomationToolkitInstallPath()
        if aBatchTool in Context.__sBatchToolsExe:
            aBatchTool = Context.__sBatchToolsExe[aBatchTool]
        else:
            raise SBSLibraryError('Bad entry for BatchTool, use a value defined in the enumeration sbsenum.BatchToolsEnum')

        if platform.system() == 'Windows':
            aBatchTool += '.exe'
        aBatchToolPath =  os.path.join(aBatchToolsFolder, aBatchTool)
        return aBatchToolPath if os.path.exists(aBatchToolPath) else None

    def getUrlAliasMgr(self):
        """
        Get the url alias manager

        :return: a :class:`.UrlAliasMgr`
        """
        return self.mUrlAliasMgr

    def getProjectMgr(self, aSbsPrjFile=None):
        """
        Get the project manager
        if a path is given, it will be parsed by the ProjectMgr
        :param aSbsPrjFile:
        :return: a :class:`.ProjectMgr`
        """
        if aSbsPrjFile:
            if not isinstance(aSbsPrjFile, list):
                aSbsPrjFile = [aSbsPrjFile]
            for sbsPrj in aSbsPrjFile:
                self.mProjectMgr.parseADoc(sbsPrj)
        return self.mProjectMgr

    def getMDLMgr(self):
        """
        Get the mdl manager

        :return: a :class:`.MDLManager`
        """
        return self.mMDLMgr

    @staticmethod
    def canReadSBSPackage(aFormatVersion, aUpdaterVersion):
        """
        canReadSBSPackage(aFormatVersion, aUpdaterVersion)
        Check if a SBS package with the given format version and updater version can be read by the API.

        :param aFormatVersion: the format version of the package
        :param aUpdaterVersion: the updater version of the package
        :type aFormatVersion: string
        :type aUpdaterVersion: string
        :return: True if the package is compatible with this API, False otherwise
        """
        return aFormatVersion == Context.__sSBSFormatVersion and aUpdaterVersion == Context.__sSBSUpdaterVersion

    @staticmethod
    def getSBSARFormatVersion():
        """
        getSBSARFormatVersion()
        Get the SBSAR format version compatible with this version of the API.

        :return: The format version as a string
        """
        return Context.__sSBSARFormatVersion

    @staticmethod
    def getSBSFormatVersion():
        """
        getSBSFormatVersion()
        Get the SBS format version compatible with this version of the API.

        :return: The format version as a string
        """
        return Context.__sSBSFormatVersion

    @staticmethod
    def getSBSUpdaterVersion():
        """
        getSBSUpdaterVersion()
        Get the SBS updater version compatible with this version of the API.

        :return: The updater version as a string
        """
        return Context.__sSBSUpdaterVersion

    @staticmethod
    def getSBSUpdaterVersion():
        """
        getSBSUpdaterVersion()
        Get the SBS updater version compatible with this version of the API.

        :return: The updater version as a string
        """
        return Context.__sSBSUpdaterVersion

    def addSBSObjectToResolve(self, aSBSObject):
        """
        When parsing a .sbs file, some objects need the parsing to be complete to finalize their initialization and resolve their dependencies (the CompInstance for example).
        In order to do so, they must register to the context by calling addSBSObjectToResolve when they are parsed.

        :param aSBSObject: The object to register for later resolution
        :type aSBSObject: :class:`.SBSObject`
        """
        self.mObjectsToResolve.append(aSBSObject)

    @staticmethod
    def clonePackage(aSBSDocument):
        """
        clonePackage(aSBSDocument)
        Create a deep copy of the given document

        :param aSBSDocument: The SBSDocument to clone
        :type aSBSDocument: :class:`.SBSDocument`
        :return: The new document as a :class:`.SBSDocument`
        """
        aCloneDocument = copy.deepcopy(aSBSDocument)
        Context.declarePackage(aCloneDocument)
        return aCloneDocument

    @staticmethod
    def declarePackage(aSBSDocument):
        """
        declarePackage(aSBSDocument)
        Add the given SBSDocument to the list of known packages on the Context

        :param aSBSDocument: The SBSDocument to declare
        :type aSBSDocument: :class:`.SBSDocument`
        """
        if aSBSDocument not in Context.__sParsedPackage:
            Context.__sParsedPackage.append(aSBSDocument)

    @staticmethod
    def getPackage(aAbsPath):
        """
        Look for the given absolute path in the already parsed package and return it if found.

        :param aAbsPath: Absolute path of the package
        :type aAbsPath: str
        :return: a :class:`.SBSDocument` if found, None otherwise
        """
        return next((package for package in Context.__sParsedPackage if package.mFileAbsPath == aAbsPath), None)

    @handle_exceptions()
    def resolveDependency(self, aParentDocument, aSBSDependency):
        """
        resolveDependency(aParentDocument, aSBSDependency)
        This function allows to set and eventually parse the referenced package of the given dependency.

        :param aParentDocument: The SBSDocument which contains the dependency
        :param aSBSDependency: The dependency to handle
        :type aParentDocument: :class:`.SBSDocument`
        :type aSBSDependency: :class:`.SBSDependency`
        :return: the package referenced by the dependency if found, as a :class:`.SBSDocument`, None otherwise
        """
        if aSBSDependency.isHimself():
            aExternalSBSDocument = aParentDocument
        else:
            aExternalSBSDocument = Context.getPackage(aAbsPath = aSBSDependency.mFileAbsPath)
            if aExternalSBSDocument is None:
                aContext = Context(aUrlAliasMgr=aParentDocument.mContext.getUrlAliasMgr(), aMDLManager=aParentDocument.mContext.getMDLMgr())
                # SBSAR package:
                if common_interfaces.Package.isAnArchive(aSBSDependency.mFileAbsPath):
                    aExternalSBSDocument = sbsarchive.SBSArchive(aContext, aSBSDependency.mFileAbsPath)
                # SBS package:
                else:
                    aExternalSBSDocument = substance.SBSDocument(aContext, aSBSDependency.mFileAbsPath)
                try:
                    if aExternalSBSDocument.parseDoc(False):
                        Context.declarePackage(aExternalSBSDocument)
                except BaseException as error:
                    log.error(python_helpers.getErrorMsg(error))

        if aExternalSBSDocument is not None and aExternalSBSDocument.isInitialized():
            aSBSDependency.setRefPackage(aExternalSBSDocument)

        return aSBSDependency.getRefPackage()


    @handle_exceptions()
    def resolveDependencies(self, aSBSDocument):
        """
        resolveDependencies(aSBSDocument)
        This function must be called once the parsing of a .sbs is over, to allow all the registered objects to finalize their initialization.
        This function calls the callback of each registered object.

        :param aSBSDocument: The SBSDocument to finalize
        :type aSBSDocument: :class:`.SBSDocument`
        """
        aDepList = aSBSDocument.getSBSDependencyList(aIncludeHimself = True)
        for dep in aDepList:
            self.resolveDependency(aSBSDocument, dep)

        for aSBSObject in self.mObjectsToResolve:
            try:
                if not aSBSObject.resolveDependency(aSBSDocument):
                    log.warning('-> One missing dependency in the package %s', aSBSDocument.mFileAbsPath)
            except AttributeError:
                log.error('Missing method resolveDependency on SBSObject: %s ', aSBSObject.__class__.__name__)
                raise
            except BaseException as error:
                log.error('Failed to resolveDependency of %s', aSBSObject.__class__.__name__)
                log.error(error)
                continue

        self.mObjectsToResolve = []
        pass

    # ==========================================================================
    # Private
    # ==========================================================================
    @staticmethod
    def __get_default_package_path(sptPath):
        """ Given the Substance Automation Toolkit installation path, returns the path to the default resource package """
        rootPath = UrlAliasMgr.normalizePath(sptPath)
        aPath = os.path.join(rootPath, 'resources', 'packages')
        # Specific Mac OS:
        if not os.path.exists(aPath) and platform.system() == 'Darwin':
            aPath = os.path.join(rootPath, 'Contents', 'Resources', 'packages')
        return aPath if os.path.exists(aPath) else None

    @staticmethod
    def __get_mdl_root_paths(sptPath):
        """ Given the Substance Automation Toolkit installation path, returns the path to the default mdl modules """
        rootPath = UrlAliasMgr.normalizePath(sptPath)
        aPath = os.path.join(rootPath, 'resources', 'view3d', 'iray')
        # Specific Mac OS:
        if not os.path.exists(aPath) and platform.system() == 'Darwin':
            aPath = os.path.join(rootPath, 'Contents', 'Resources', 'view3d', 'iray')
        return [aPath] if os.path.exists(aPath) else None

    @staticmethod
    def __get_psdparse_path(sptPath):
        """ Given the Substance Automation Toolkit installation path, returns the path to the psdparse executable """
        sptPath = UrlAliasMgr.normalizePath(sptPath)
        if platform.system() == 'Darwin':
            aPath = os.path.join(sptPath, 'psdparse')
            if not os.path.exists(aPath):
                aPath = os.path.join(sptPath, 'Contents','MacOS','psdparse') # SD folder structure
        elif platform.system() == 'Linux':
            aPath = os.path.join(sptPath, 'psdparse')
        else:
            aPath = os.path.join(sptPath, 'psdparse.exe')
        return aPath if os.path.exists(aPath) else None

    @staticmethod
    def __computeSATPaths():
        """
        Compute the absolute path of the default resource package library, aliased by sbs:///.
        Depending on the platform, compute the installation folder of Substance Automation Toolkit to retrieve the resources/package/
        folder installed by default.
        The default package path is saved in the static member sDefaultPackagePath.
        """

        def is_exe(fPath):
            """ Returns True if the given path is an executable """
            return os.path.isfile(fPath) and os.access(fPath, os.X_OK)

        def getWinRegKeyVersionAndPath(key):
            try:    import _winreg as winreg    # Python 2.7
            except: import winreg               # Python 3.5
            versionPattern = re.compile('[0-9]+\.[0-9]+\.[0-9]+')
            infoSoft = winreg.QueryInfoKey(key)
            keyVersion = None
            keyInstallPath = None

            # Parse all information available on this software
            for i in range(0, infoSoft[1]):
                value = winreg.EnumValue(key, i)
                if (value[0] == 'UninstallString' or value[0] == 'InstallLocation') and value[1]:
                    keyInstallPath = value[1].strip('"').replace('\\', '/')
                    if os.path.isfile(keyInstallPath):
                        keyInstallPath = os.path.dirname(keyInstallPath)
                    keyInstallPath = os.path.normpath(keyInstallPath)
                elif value[0] == 'DisplayVersion' and value[1]:
                    v = value[1]
                    versionMatch = versionPattern.match(v)
                    if versionMatch:
                        keyVersion = v[versionMatch.start():versionMatch.end()]
                if keyInstallPath is not None and keyVersion is not None:
                    break
            return keyVersion, keyInstallPath

        def searchApplicationOnWindowsRegistry(applicationKey, application, defaultInstallPath, expectedVersion):
            # Search the given application in the Registry
            try:    import _winreg as winreg    # Python 2.7
            except: import winreg               # Python 3.5

            try:    proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
            except: proc_arch = None
            try:    proc_arch64 = os.environ['PROCESSOR_ARCHITEW6432'].lower()
            except: proc_arch64 = None

            if proc_arch == 'x86' and not proc_arch64:
                arch_keys = set([0])
            elif proc_arch == 'x86' or proc_arch == 'amd64':
                arch_keys = set([winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY])
            else:
                arch_keys = set([0])

            latestVersion = None
            installPath = None
            found = False

            for arch_key in arch_keys:
                if found:
                    break
                try:
                    softwares = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                               'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall', 0,
                                               winreg.KEY_READ | arch_key)
                    info = winreg.QueryInfoKey(softwares)

                    appKey = None
                    try:    appKey = winreg.OpenKey(softwares, applicationKey)
                    except: pass
                    if appKey is None:
                        try:    appKey = winreg.OpenKey(softwares, applicationKey+'_is1')
                        except: pass

                    if appKey is not None:
                        displayName = winreg.QueryValueEx(appKey, 'DisplayName')[0]
                        if displayName.find(application) >= 0:
                            version, versionInstallPath = getWinRegKeyVersionAndPath(appKey)
                            if expectedVersion == version:
                                installPath = versionInstallPath
                                found = True
                                key.Close()
                                break

                    # Parse all subkeys in order to find the application
                    for index in range(0, info[0]):
                        try:
                            soft = winreg.EnumKey(softwares, index)
                            key = winreg.OpenKey(softwares, soft)
                            displayName = winreg.QueryValueEx(key, 'DisplayName')[0]
                            if displayName.find(application) >= 0:
                                # Keep the latest version of the application
                                version, versionInstallPath = getWinRegKeyVersionAndPath(key)
                                if versionInstallPath is not None:
                                    if expectedVersion == version:
                                        installPath = versionInstallPath
                                        found = True
                                        break
                                    elif latestVersion is None or version is None or LooseVersion(version) > LooseVersion(latestVersion):
                                        latestVersion = version
                                        installPath = versionInstallPath
                        except:
                            pass
                        finally:
                            key.Close()
                except:
                    pass
                finally:
                    softwares.Close()

            if found:
                return installPath

            # If not found on the registry, try to reach the default installation path:
            if os.path.exists(defaultInstallPath):
                return defaultInstallPath
            elif installPath is not None and os.path.exists(installPath):
                return installPath
            return None


        def getSATPathOnWindows():
            """ Specific Windows: Search for Substance Automation Toolkit installation path """
            _SATInstallPath = searchApplicationOnWindowsRegistry(applicationKey='{A44DE9D4-AAB6-4B59-BA9B-109F55EEA5A8}',
                                    application = 'Substance Automation Toolkit',
                                    defaultInstallPath = 'C:\\Program Files\\Allegorithmic\\Substance Automation Toolkit',
                                    expectedVersion = '2017.2.2')

            # If not found, try to search for Substance Designer path
            _SDInstallPath = searchApplicationOnWindowsRegistry(applicationKey='{e9e3d6d9-3023-41c7-b223-11d8fdd691b9}',
                                    application='Substance Designer',
                                    defaultInstallPath='C:\\Program Files\\Allegorithmic\\Substance Designer',
                                    expectedVersion='2017.2.1')
            return _SATInstallPath, _SDInstallPath


        def getSATPathOnMac():
            """ Specific Mac: Search for Substance Automation Toolkit installation path """
            installPaths = [None,None]
            for i,app in enumerate(['Substance Automation Toolkit', 'Substance Designer']):
                defaultInstallPath = '/Applications/'+app
                if os.path.exists(defaultInstallPath):
                    installPaths[i] = defaultInstallPath
            return installPaths

        def getSATPathOnLinux():
            """ Specific Linux: Search for Substance Automation Toolkit installation path """
            from distutils.spawn import find_executable
            _SATInstallPath = None
            _SDInstallPath = None

            # Try first to retrieve the installation path from the PATH
            pathDirs = os.environ["PATH"].split(os.pathsep)
            pathNames = [os.path.basename(aPath) for aPath in pathDirs]
            if 'Substance_Automation_Toolkit' in pathNames:
                installPath = os.environ["PATH"][pathNames.index('Substance_Automation_Toolkit')]
                _SATInstallPath = os.path.realpath(installPath) if os.path.islink(installPath) else installPath

            # Test with the default installation path
            defaultInstallPath = '/opt/Allegorithmic/Substance_Automation_Toolkit'
            if _SATInstallPath is None and os.path.exists(defaultInstallPath):
                _SATInstallPath = defaultInstallPath

            # Search for Substance Designer if Substance Automation Toolkit is not found
            # Try first to find 'Substance Designer' and then 'Substance Designer 6'
            for exeName in ['substancedesigner', 'Substance_Designer-6']:
                exe = find_executable(exeName)
                if exe:
                    _SDInstallPath = os.path.dirname(os.path.realpath(exe))

            # Test with the default installation path
            if _SDInstallPath is None:
                for v in ['', '-6']:
                    defaultInstallPath = '/opt/Allegorithmic/Substance_Designer'+v
                    if os.path.exists(defaultInstallPath):
                        _SDInstallPath = defaultInstallPath

            return _SATInstallPath, _SDInstallPath

        def getSATPathFromEnvVar():
            """ Look for the environment variable SAT_INSTALL_PATH """
            installPath = os.environ.get('SAT_INSTALL_PATH')
            envDeprecated = os.environ.get('SDAPI_SATPATH') if installPath is None else None
            envName = 'SDAPI_SATPATH' if envDeprecated else 'SAT_INSTALL_PATH'
            if envDeprecated:
                log.warning('The environment variable %s is deprecated instead please use SAT_INSTALL_PATH.', envName)
                installPath = envDeprecated
            if installPath is not None:
                installPath = UrlAliasMgr.normalizePath(installPath)
                if not os.path.exists(installPath):
                    log.error('The directory pointed by the environment variable %s does not exist: %s', envName, installPath)
                    return None
                if is_exe(installPath):
                    installPath = os.path.dirname(installPath)
                if os.path.isdir(installPath):
                    return installPath
                log.error('The environment variable %s should points to the folder that contains Substance Automation Toolkit executables, %s is invalid', envName, installPath)
            return None

        SATInstallPath, SDInstallPath = None, None

        # Search for SD installation path:
        OS = platform.system()
        # Windows platform
        if OS == 'Windows':
            SATInstallPath, SDInstallPath = getSATPathOnWindows()

        # Linux
        elif OS == 'Linux':
            SATInstallPath, SDInstallPath = getSATPathOnLinux()

        # Mac OS: Substance Designer is installed in /Applications/
        elif OS == 'Darwin':
            SATInstallPath, SDInstallPath = getSATPathOnMac()

        # First check if the environment variable SAT_INSTALL_PATH is set
        SATInstallPath = getSATPathFromEnvVar() or SATInstallPath

        if SATInstallPath is not None:
            Context.setAutomationToolkitInstallPath(SATInstallPath)
        else:
            log.error('Failed to find the default installation path of Substance Automation Toolkit, you can use function Context.setAutomationToolkitInstallPath() to set it manually')

        if SDInstallPath is not None:
            Context.setSubstanceDesignerInstallPath(SDInstallPath)
        elif Context.__sPSDParseExePath is None:
            log.warning('Failed to find the default installation path of Substance Designer, you can use function Context.setSubstanceDesignerInstallPath() to set it manually.\n'+
                'It is required only if you need to import a PSD resource.')
