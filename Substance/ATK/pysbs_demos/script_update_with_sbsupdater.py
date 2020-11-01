# coding: utf-8

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import os
import subprocess
import sys

try:
    import pysbs
except ImportError:
    try:
        pysbsPath = bytes(__file__).decode(sys.getfilesystemencoding())
    except:
        pysbsPath = bytes(__file__, sys.getfilesystemencoding()).decode(sys.getfilesystemencoding())
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(pysbsPath)[0], '..')))

from pysbs.api_decorators import doc_source_code
from pysbs.api_exceptions import SBSIncompatibleVersionError
from pysbs import sbsenum
from pysbs import context
from pysbs import substance


@doc_source_code
def scriptUpdatePackagesVersion(aContext, aPreviousVersion, aPreviousUpdaterVersion, aPackagesFolderRootDir, aBatchToolsFolder = None):
    """
    Allows to update to the current version of Substance Designer all .sbs recursively included in the given folder path using the Mutator Batch Tool.

    :param aContext: Execution context
    :param aPreviousVersion: Previous version number. Only .sbs with this version will be updated
    :param aPreviousUpdaterVersion: Previous updater version number. Only .sbs with this updater version will be updated
    :param aPackagesFolderRootDir: The root folder containing the packages to update
    :param aBatchToolsFolder: The folder containing the batch tools executables. If not provided, the path of Substance Designer identified by the given context will be used
    :type aContext: context.Context
    :type aPreviousVersion: str
    :type aPreviousUpdaterVersion: str
    :type aBatchToolsFolder: str, optional
    :return: True if success
    """
    aUpdaterPath = aContext.getBatchToolExePath(aBatchTool=sbsenum.BatchToolsEnum.UPDATER, aBatchToolsFolder=aBatchToolsFolder)
    aPresetPackagePath = aContext.getDefaultPackagePath()
    try:
        aCommand = [aUpdaterPath, '--no-dependency', '--output-path', '{inputPath}', '--output-name', '{inputName}', '--presets-path', aPresetPackagePath]
        log.info(aCommand)

        aRootDir = os.path.normpath(aPackagesFolderRootDir)

        for root, subFolders, files in os.walk(aRootDir):
            for aFile in files:
                if aFile.endswith('.sbs'):
                    aPackagePath = os.path.join(root, aFile)
                    aDoc = substance.SBSDocument(aContext=aContext, aFileAbsPath=aPackagePath)
                    log.info('Parse substance '+aPackagePath)
                    try:
                        aDoc.parseDoc()
                    except SBSIncompatibleVersionError:
                        pass

                    if aDoc.mFormatVersion == aPreviousVersion and aDoc.mUpdaterVersion == aPreviousUpdaterVersion:
                        aMutatorCmd = aCommand + ['--input', aPackagePath]
                        log.info('Update substance '+aPackagePath)
                        subprocess.check_call(aMutatorCmd)

        log.info('=> All packages have been updated using the Mutator Batch Tool')
        return True

    except BaseException as error:
        log.error("!!! [demoUpdatePackagesVersion] Failed to update a package")
        raise error


if __name__ == "__main__":
    apiAliasPath = os.path.abspath(os.path.join(os.path.split(__file__)[0], '../pysbs_demos/sample'))
    apiContext = context.Context()
    apiContext.getUrlAliasMgr().setAliasAbsPath('api', apiAliasPath)

    here = os.path.split(__file__)[0]
    folders = [os.path.abspath(os.path.join(here, '../pysbs')),
               os.path.abspath(os.path.join(here, '../pysbs_demos'))]
    for f in folders:
        scriptUpdatePackagesVersion(aContext=apiContext,
                                    aPreviousVersion="1.1.0.201806",
                                    aPreviousUpdaterVersion="1.1.0.201806",
                                    aPackagesFolderRootDir = f)

