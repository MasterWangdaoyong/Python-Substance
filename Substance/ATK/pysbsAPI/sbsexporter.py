# coding: utf-8
from __future__ import unicode_literals
import os
import copy
import datetime
import shutil
import logging
log = logging.getLogger(__name__)

from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.api_decorators import handle_exceptions
from pysbs.substance import SBSSourceExternalCopy
from pysbs.common_interfaces import Package
from pysbs import python_helpers

# ==============================================================================
class SBSExporter:
    """
    Class used to provide useful functions when parsing a .sbs (=xml) file
    """
    __dependencyFolder = 'dependencies'

    def __init__(self):
        self.mSBSDocument = None
        self.mExportFolder = ''
        self.mAliasesToExport = []

        self.__exportedResources = {}
        self.__exportedPackages = {}
        self.__missingResources = []
        self.__missingPackages = []

    def reset(self):
        """
        Reset the exporter to its initial state
        """
        self.mSBSDocument = None
        self.mExportFolder = ''
        self.mAliasesToExport = []

        self.__exportedResources = {}
        self.__exportedPackages = {}
        self.__missingResources = []
        self.__missingPackages = []

    @handle_exceptions()
    def export(self, aSBSDocument, aExportFolder, aBuildArchive = False, aAliasesToExport = None, aArchiveFormat = 'zip'):
        """
        export(aSBSDocument, aExportFolder, aBuildArchive = False, aAliasesToExport = None, aArchiveFormat = 'zip')
        Exports the given :class:`.SBSDocument` with its dependencies (resources + packages) to the specified folder, including the packages referenced by the provided aliases.
        This is the equivalent of the function 'Export with dependencies' within Substance Designer.
        If aAliasesToExport is let None, all the packages referenced by an alias will not be included in the self-contained package.

        :param aSBSDocument: The package to export
        :param aExportFolder: The absolute path of the export folder (it must exist). A folder with the name of the document will be created inside this folder.
        :param aBuildArchive: True to create an archive of the exported folder. Default to False
        :param aAliasesToExport: The list of aliases to export in the self-contained package. If left None, the path with aliases will be kept as is.
        :param aArchiveFormat: Archive format, among 'zip', 'tar', 'gztar', 'bztar' as specified in the Python module shutil
        :type aSBSDocument: :class:`.SBSDocument`
        :type aExportFolder: string
        :type aBuildArchive: boolean, optional
        :type aAliasesToExport: list of string, optional
        :type aArchiveFormat: string
        :return: The absolute path of the resulting exported package or archive
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        self.reset()

        self.mSBSDocument = aSBSDocument
        self.mExportFolder = aExportFolder
        self.mAliasesToExport = aAliasesToExport if aAliasesToExport is not None else []

        # Check provided folder and create the subfolder
        if not os.path.isdir(os.path.normpath(self.mExportFolder)):
            raise SBSImpossibleActionError('The folder ' + self.mExportFolder + ' does not exists')

        # Create the destination folder
        aFilename = os.path.splitext(os.path.basename(self.mSBSDocument.mFileAbsPath))[0]
        aNewFolder = os.path.join(self.mExportFolder, aFilename)
        if os.path.isdir(aNewFolder):
            shutil.rmtree(aNewFolder)
        os.makedirs(aNewFolder)

        # Create the dependency folder
        aDependencyFolder = os.path.join(aNewFolder, SBSExporter.__dependencyFolder)
        if self.mSBSDocument.getSBSResourceList() or self.mSBSDocument.getSBSDependencyList():
            os.makedirs(aDependencyFolder)

        # Create a self-contained package with all required dependencies
        aResultPath = self.__exportWithDependencies(self.mSBSDocument, self.mAliasesToExport, aNewFolder, aDependencyFolder)

        # Build an archive with the exported package, and remove the self-contained folder to keep only the archive
        if aBuildArchive:
            aArchivePath = aNewFolder + str('_{:%Y_%m_%d_%H-%M-%S}'.format(datetime.datetime.now()))
            aResultPath = shutil.make_archive(base_name=aArchivePath, format= aArchiveFormat, root_dir=os.path.dirname(aNewFolder), base_dir=os.path.basename(aNewFolder))
            shutil.rmtree(aNewFolder)

        return aResultPath

    @handle_exceptions()
    def getExportedDependencies(self):
        """
        getExportedDependencies()
        Allows to get the exported dependencies (resources + packages) of the last export

        :return: The exported dependencies as a dictionary of {oldAbsPath(string): newAbsPath(string)}
        """
        result = copy.deepcopy(self.__exportedPackages)
        return result.extend(self.__exportedResources)

    def getExportedPackages(self):
        """
        getExportedPackages()
        Allows to get the exported packages of the last export

        :return: The exported packages as a dictionary of {oldAbsPath(string): newAbsPath(string)}
        """
        return self.__exportedPackages

    def getExportedResources(self):
        """
        getExportedResources()
        Allows to get the exported resources of the last export

        :return: The exported resources as a dictionary of {oldAbsPath(string): newAbsPath(string)}
        """
        return self.__exportedResources

    def getMissingPackages(self):
        """
        getMissingPackages()
        Allows to get the missing packages of the last export (file not found)

        :return: The missing packages as a list string
        """
        return self.__missingPackages

    def getMissingResources(self):
        """
        getMissingResources()
        Allows to get the missing resources of the last export (file not found)

        :return: The missing resources as a list string
        """
        return self.__missingResources

    #==========================================================================
    # Private
    #==========================================================================
    @handle_exceptions()
    def __exportWithDependencies(self, aSBSDocument, aAliasesToExport, aNewFolder, aDependencyFolder):

        def createUniqueDependencyPath(aDependencyName, aNewDependencyFolder):
            """
            Checks if the path aNewDependencyFolder/aDependencyName already exists.
            If it exists, generates a unique subfolder based on the name of the dependency and place the dependency inside.
            """
            if os.path.exists(os.path.join(aNewDependencyFolder, aDependencyName)):
                aSubDir = aSubDirSuffix = os.path.splitext(aDependencyName)[0]
                aSuffix = 0
                while os.path.exists(os.path.join(aNewDependencyFolder, aSubDirSuffix)):
                    aSuffix += 1
                    aSubDirSuffix = aSubDir + '_' + str(aSuffix)

                aNewDependencyFolder = os.path.join(aNewDependencyFolder, aSubDirSuffix)
                os.makedirs(aNewDependencyFolder)
            return aNewDependencyFolder

        # Create a copy of this document
        log.info("Export package %s", aSBSDocument.mFileAbsPath)
        aExportedDoc = self.mSBSDocument.mContext.clonePackage(aSBSDocument)

        aDependencyList = aExportedDoc.getSBSDependencyList()
        aResourceList = aExportedDoc.getSBSResourceList()
        aExportedDoc.mDirAbsPath = aNewFolder
        aExportedDoc.mFileAbsPath = os.path.join(aNewFolder, os.path.basename(aExportedDoc.mFileAbsPath))

        # Move each dependencies in the dependencies/ folder
        for aDependency in aDependencyList:
            # Handle the alias
            aAlias = aExportedDoc.mContext.getUrlAliasMgr().getAliasInPath(aDependency.mFilename)
            if aAlias is None or aAlias in aAliasesToExport:

                # If the dependency has already been exported, simply get its path
                if aDependency.mFileAbsPath in self.__exportedPackages:
                    aNewDepPath = self.__exportedPackages[aDependency.mFileAbsPath]
                elif aDependency.mFileAbsPath in self.__missingPackages:
                    aNewDepPath = self.__missingPackages[aDependency.mFileAbsPath]

                # Add the dependency to the self-contained packaged
                else:
                    try:
                        # If the package pointed by the dependency has not been parsed, parse it
                        if aDependency.getRefPackage() is not None:
                            aDepPackage = aDependency.getRefPackage()()
                        else:
                            aDepPackage = self.mSBSDocument.mContext.resolveDependency(aParentDocument=self.mSBSDocument, aSBSDependency=aDependency)()

                        # If the destination path already exists, place the resource to export in a subdirectory
                        aDepName = os.path.basename(aDepPackage.mFileAbsPath)
                        aNewDepFolder = createUniqueDependencyPath(aDependencyName = aDepName, aNewDependencyFolder = aDependencyFolder)

                        # For an archive, just copy the .sbsar file in the destination folder and clone the package for the context
                        if Package.isAnArchive(aDepPackage.mFileAbsPath):
                            aNewDepPackage = self.mSBSDocument.mContext.clonePackage(aDepPackage)
                            aNewDepPackage.mFileAbsPath = aNewDepPath = os.path.join(aNewDepFolder, aDepName)
                            aNewDepPackage.mDirAbsPath = aNewDepFolder
                            shutil.copy(aDepPackage.mFileAbsPath, aNewDepFolder)
                        # For a .sbs package, parse recursively to export its dependencies and resources
                        else:
                            aNewDepPath = self.__exportWithDependencies(aDepPackage, aAliasesToExport, aNewDepFolder, aDependencyFolder)

                        self.__exportedPackages[aDependency.mFileAbsPath] = aNewDepPath

                    except:
                        aNewDepPath = aDependency.mFileAbsPath
                        self.__missingPackages.append(aNewDepPath)
                        log.warning('Failed to find package at %s', aNewDepPath)

                # Set new absolute and relative paths
                aDepRelPath = aExportedDoc.mContext.getUrlAliasMgr().toRelPath(aNewDepPath, aExportedDoc.mDirAbsPath)
                aDependency.mFilename = aDepRelPath.replace('\\', '/')
                aDependency.mFileAbsPath = aNewDepPath

        # Move each resources in the dependencies/ folder
        for aResource in aResourceList:
            aResourceAbsPath = aResource.getResolvedFilePath()
            aAlias = aExportedDoc.mContext.getUrlAliasMgr().getAliasInPath(aResourceAbsPath)

            # Check the alias
            if aAlias is None or aAlias in aAliasesToExport:
                aNewResourcePath = None

                # If the dependency has already been exported, simply get its path
                if aResource.mFileAbsPath in self.__exportedPackages:
                    aNewResourcePath = self.__exportedResources[aResource.mFileAbsPath]
                elif aResource.mFileAbsPath in self.__missingResources:
                    aNewResourcePath = self.__missingResources[aResource.mFileAbsPath]

                # Add the resource to the self-contained packaged
                else:
                    # External copy: copy the .resources folder into the self-contained package
                    if aResource.mSource:
                        aSource = aResource.mSource.getSource()

                        if isinstance(aSource, SBSSourceExternalCopy):
                            aDirPath = os.path.dirname(aResource.mFileAbsPath)
                            aNewPath = os.path.join(aNewFolder, os.path.basename(aDirPath))
                            python_helpers.createFolderIfNotExists(aNewPath)
                            aNewResourcePath = os.path.join(aNewPath, os.path.basename(aResource.mFileAbsPath))

                    # Linked resource: copy the linked resource in the dependencies/ folder
                    else:
                        aResourceName = os.path.basename(aResource.mFileAbsPath)
                        aDepAbsFolder = aExportedDoc.buildAbsPathFromRelToMePath(SBSExporter.__dependencyFolder)

                        # If the destination path already exists, place the resource to export in a subdirectory
                        aDepAbsFolder = createUniqueDependencyPath(aDependencyName = aResourceName, aNewDependencyFolder = aDepAbsFolder)
                        aNewResourcePath = os.path.join(aDepAbsFolder, aResourceName)

                if aNewResourcePath is not None:
                    try:
                        resourceFileList = aResource.getPhysicalResourceList()
                        destFolder = os.path.dirname(aNewResourcePath)
                        for aFile in resourceFileList:
                            shutil.copy(aFile, destFolder)
                        self.__exportedResources[aResource.mFileAbsPath] = aNewResourcePath
                    except IOError:
                        aNewResourcePath = aResource.mFileAbsPath
                        self.__missingResources.append(aNewResourcePath)
                        log.warning('Failed to find resource %s', aNewResourcePath)

                    # Set new absolute and relative paths
                    aResourceRelPath = aExportedDoc.mContext.getUrlAliasMgr().toRelPath(aNewResourcePath, os.path.dirname(aExportedDoc.mFileAbsPath))
                    aResource.mFilePath = aResourceRelPath.replace('\\', '/')
                    aResource.mFileAbsPath = aNewResourcePath

        aExportedDoc.writeDoc()

        return aExportedDoc.mFileAbsPath
