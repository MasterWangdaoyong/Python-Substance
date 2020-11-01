# coding: utf-8
"""
Module **functions** contains functions that can be called by Substance Designer application, if it is configured
in the preferences.
"""

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)

try:
    import pysbs
except ImportError:
    raise ImportError('The current Python interpreter does not have pysbs, check your Python installation, and your Substance Designer settings')

from pysbs import base
from pysbs import substance



def onBeforeFileSaved(aContext, aFileAbsPath = '', aPackageFileAbsPath = ''):
    """
    This function can be called by Substance Designer if configured to.
    It is called when a file is about to be saved on disk.
    The parameter names of this function must not be changed otherwise the call from SD will fail.

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aPackageFileAbsPath: The path of the package that contains the exported data (if any)
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aPackageFileAbsPath: str
    :return: a :class:`.ReturnValue` object that contains the following keys:

        - userData: User data as string
    """
    # Build return value
    returnValue = base.ReturnValue()
    returnValue.setValue('userData', '')
    return returnValue


def onAfterFileSaved(aContext, aFileAbsPath = '', aSucceed = True, aUserData = ''):
    """
    This function can be called by Substance Designer if configured to.
    It is called after a save process has been triggered.
    The parameter names of this function must not be changed otherwise the call from SD will fail.

    :param aContext: Execution context
    :param aFileAbsPath: The absolute path of the file
    :param aSucceed: The result of the save process
    :param aUserData: The userData value set in field "userData' of the returnValue object returned by the function :func:`onBeforeFileSaved()`
    :type aContext: context.Context
    :type aFileAbsPath: str
    :type aSucceed: bool
    :type aUserData: str
    :return: Nothing
    """
    sbsDoc = substance.SBSDocument(aContext, aFileAbsPath)
    sbsDoc.parseDoc()
    for s in sbsDoc.getSBSDependencyList():
        log.info(s.mFileAbsPath)
    for s in sbsDoc.getSBSResourceList():
        log.info(s.getResolvedFilePath())
        log.info(s.mFileAbsPath)

    pass


def getGraphExportOptions(aContext, aPackageFileAbsPath = '', aGraphIdentifier = ''):
    """
    Get the options used to fill the widget used to export a graph outputs

    :param aContext: Execution context
    :param aPackageFileAbsPath: The absolute path of the package (i.e. the .sbs file)
    :param aGraphIdentifier: The identifier of the graph
    :type aContext: context.Context
    :type aPackageFileAbsPath: str
    :type aGraphIdentifier: str
    :return: a :class:`.ReturnValue` object that contains the following keys:

        - outputDirAbsPath: absolute path of the directory used to export
        - fileExtension: the image file extension (png, tga, ...)
    """
    # Build return value
    returnValue = base.ReturnValue()
    returnValue.setValue('outputDirAbsPath', '')
    returnValue.setValue('fileExtension', '')
    returnValue.setValue('pattern', '')
    return returnValue


# ==============================================================================
if __name__ == "__main__":
    base.CommandLineArgsProcessor(__name__).call()
