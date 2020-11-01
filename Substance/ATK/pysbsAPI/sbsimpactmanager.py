# coding: utf-8

from __future__ import unicode_literals
import os
import logging
log = logging.getLogger(__name__)

from pysbs.api_exceptions import SBSImpossibleActionError, SBSProcessInterruptedError
from pysbs.api_decorators import handle_exceptions
from pysbs import api_helpers, python_helpers
from pysbs import substance


def imRawInput(s):
    """
    Function used to specify the input used by the interactive mode of SBSImpactManager.
    By default it uses the Python standard input, but it can be redefined to mock the standard input.
    """
    return python_helpers.RAW_INPUT(s)

# ==============================================================================
class SBSImpactManager:
    """
    Class used to provide useful functions to propagate changes done a Substance on all the Substances within a particular tree
    """

    def __init__(self):
        self.__updatedPackages = []
        self.__errorPackages = []


    def confirm(self, promptMsg = None, defaultResponse = False):
        """
        Prompts for yes or no response from the user.

        :param promptMsg: The message to prompt to the user. If None, 'Confirm' will be prompted
        :param defaultResponse: The default return value, returned when used simply press ENTER. Default to False
        :type promptMsg: str, optional
        :type defaultResponse: bool, optional
        :return: True for yes and False for no.
        """
        if promptMsg is None:
            promptMsg = 'Confirm'

        if defaultResponse:
            promptMsg = '%s [%s]|%s: ' % (promptMsg, 'y', 'n')
        else:
            promptMsg = '%s [%s]|%s: ' % (promptMsg, 'n', 'y')

        while True:
            ans = imRawInput(promptMsg)
            if not ans:
                return defaultResponse
            if ans not in ['y', 'Y', 'n', 'N']:
                print('please enter y or n.')
                continue
            if ans == 'y' or ans == 'Y':
                return True
            if ans == 'n' or ans == 'N':
                return False

    def reset(self):
        """
        Reset the exporter to its initial state
        """
        self.__updatedPackages = []
        self.__errorPackages = []


    def getAllSubstancesInTree(self, rootPath, excludeAutosave = True, excludeFolders = None):
        """
        Get all the Substance files (.sbs) within a particular tree

        :param rootPath: The root path of the tree to explore on the file system
        :param excludeAutosave: True to exclude the Substances included in a .autosave folder. Default to True
        :param excludeFolders: A list of folder names to exclude in the Substance search
        :type rootPath: str
        :type excludeAutosave: bool, optional
        :type excludeFolders: list of string, optional
        :return: the Substance files as a list of absolute paths
        """
        excludeFolders = excludeFolders or []
        if excludeAutosave:
            excludeFolders.append('.autosave')

        sbsList = [aFile for aFile in api_helpers.yieldFilesWithExtension(os.path.normpath(rootPath), ".sbs", excludeFolders)]
        return sorted(sbsList)


    @handle_exceptions()
    def getAllSubstancesWithDependencyOn(self, aContext, substancePath, withinTree, stopOnException = True):
        """
        getAllSubstancesWithDependencyOn(self, aContext, substancePath, withinTree, stopOnException = True)
        Get all the Substances (.sbs) that have a dependency on the given Substance (.sbs or .sbsar), within the given tree.

        :param aContext: The current execution context (allows to provide aliases)
        :param substancePath: The path of the Substance to look for (can be .sbs or .sbsar file)
        :param withinTree: The tree where to find the referencing Substances
        :param stopOnException: Allows to stop the exploring process when an exception occurs. Default to True
        :type aContext: :class:`.Context`
        :type substancePath: str
        :type withinTree: str
        :type stopOnException: bool, optional
        :return: the list of referencing Substances as :class:`.SBSDocument` objects
        """
        substancePath = os.path.normpath(substancePath)
        withinTree = os.path.normpath(withinTree)

        # Parse the Substances in the tree
        referencingSBSList = []
        substanceList = self.getAllSubstancesInTree(withinTree)
        for sbsPath in substanceList:
            try:
                sbsDoc = substance.SBSDocument(aContext, aFileAbsPath=sbsPath)
                if not sbsDoc.parseDoc():
                    raise SBSProcessInterruptedError("Failed to parse file: " + sbsDoc.mFileAbsPath)

                # Search for dependencies on the given Substance
                aDep = sbsDoc.getDependencyFromPath(substancePath)
                if aDep is not None and not aDep.isHimself():
                    referencingSBSList.append(sbsPath)

            except BaseException as error:
                self.__errorPackages.append(sbsPath)
                if stopOnException:
                    raise error
                else:
                    log.error(error)
        return referencingSBSList


    def getUpdatedPackages(self):
        """
        getUpdatedPackages()
        Allows to get the list of packages updated with the last impact propagation

        :return: The list of packages path as a list string
        """
        return self.__updatedPackages

    def getErrorPackages(self):
        """
        getErrorPackages()
        Allows to get the list of packages that raised error during the last impact propagation

        :return: The list of packages path in error as a list string
        """
        return self.__errorPackages

    def declareSBSMoved(self, aContext, oldPath, newPath, withinTree, interactiveMode = True, stopOnException = True):
        """
        declareSBSMoved(self, aContext, oldPath, newPath, withinTree, interactiveMode = True, stopOnException = True)
        | Allows to declare the fact a substance has been move from the oldPath to the newPath.
        | This will update all the Substance files (.sbs) in the given tree that had a dependency on the Substance that had been moved.

        :param aContext: The current execution context (allows to provide aliases)
        :param oldPath: The old absolute path of the Substance (can be .sbs or .sbsar file)
        :param newPath: The new absolute path of the Substance (can be .sbs or .sbsar file)
        :param withinTree: The tree where to find the Substances to update
        :param interactiveMode: Run the process in an interactive mode, requiring user confirmation at each step. Default to True
        :param stopOnException: Allows to stop the propagation process when an exception occurs. Default to True
        :type aContext: :class:`.Context`
        :type oldPath: str
        :type newPath: str
        :type withinTree: str
        :type interactiveMode: bool, optional
        :type stopOnException: bool, optional
        :return: the list of updated Substance paths
        """
        self.reset()

        oldPath = os.path.normpath(oldPath)
        newPath = os.path.normpath(newPath)
        withinTree = os.path.normpath(withinTree)

        # Check that path exists
        if not os.path.isfile(newPath):
            raise SBSImpossibleActionError('The newPath provided does not exist or is not a file: '+ newPath)
        if not os.path.exists(withinTree):
            raise SBSImpossibleActionError('The tree where to apply the change does not exist: '+ withinTree)

        # Check file extensions
        _, oldExt = api_helpers.splitExtension(oldPath)
        _, newExt = api_helpers.splitExtension(newPath)
        extensions = ['.sbs', '.sbsar']
        if oldExt not in extensions or newExt not in extensions:
            raise SBSImpossibleActionError('Bad extension for oldPath or newPath, they must be .sbs or .sbsar files')

        if interactiveMode:
            msg = 'Confirm replacing references\n\ton: '+ oldPath +'\n\tby: '+ newPath +'\n\tin: '+withinTree
            if not self.confirm(msg):
                return self.__updatedPackages

        # Parse the Substances in the tree
        substanceList = self.getAllSubstancesInTree(withinTree)
        for substancePath in substanceList:
            try:
                sbsDoc = substance.SBSDocument(aContext, aFileAbsPath=substancePath)
                sbsDoc.parseDoc()

                # Search for dependencies on the moved Substance
                needUpdate = False
                aDep = sbsDoc.getDependencyFromPath(oldPath)
                if aDep is not None and not aDep.isHimself():
                    # Check if there is already a dependency on the new path, and use it for the references on oldPath
                    aNewPathDep = sbsDoc.getDependencyFromPath(newPath)
                    if aNewPathDep:
                        if interactiveMode:
                            msg = 'The Substance '+sbsDoc.mFileAbsPath+' uses already both oldPath and newPath.\n\t\
Simply remove the dependency oldPath and update its references to point to newPath?'
                            if not self.confirm(msg):
                                continue

                        sbsDoc.declareDependencyUIDChanged(oldDependencyUID=aDep.mUID, newDependencyUID=aNewPathDep.mUID)
                        sbsDoc.removeDependency(aDep)

                    # Otherwise change the dependency to point to the new path
                    else:
                        if interactiveMode:
                            msg = 'Update the Substance '+sbsDoc.mFileAbsPath+' ?'
                            if not self.confirm(msg):
                                continue

                        aDep.mFilename = aContext.getUrlAliasMgr().toRelPath(aUrl=newPath, aDirAbsPath=sbsDoc.mDirAbsPath).replace('\\', '/')
                        aDep.mFileAbsPath = newPath
                    needUpdate = True

                # Write back the Substance if needed
                if needUpdate:
                    if not sbsDoc.writeDoc():
                        raise SBSProcessInterruptedError("Failed to update file: "+ sbsDoc.mFileAbsPath)
                    self.__updatedPackages.append(substancePath)

            except BaseException as error:
                self.__errorPackages.append(substancePath)
                if stopOnException:
                    raise SBSProcessInterruptedError(python_helpers.getErrorMsg(error))
                elif interactiveMode:
                    msg = 'Error caught when updating Substance '+substancePath+':\n\t'+python_helpers.getErrorMsg(error)+'\n\tContinue anyway ?'
                    if not self.confirm(msg):
                        return self.__updatedPackages
                else:
                    log.warning(python_helpers.getErrorMsg(error))

        return self.__updatedPackages
