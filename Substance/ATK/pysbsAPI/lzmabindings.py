# coding: utf-8
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import os
import platform
import ctypes
import sys
import pysbs
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers

aPath = None
aLibFilename = None
aLibFolder = 'x86' if python_helpers.isPython32Bit() else 'amd64'

if   platform.system() == 'Windows':  aLibFilename = '7zLib.dll'
elif platform.system() == 'Darwin':   aLibFilename = 'lib7zLib.dylib'
elif platform.system() == 'Linux':    aLibFilename = 'lib7zLib.so'
sevenZipLib = None
seven_zip_extract = None
if aLibFilename is not None:

    aPath = python_helpers.getModulePath(pysbs)
    aPath = os.path.abspath(os.path.join(os.path.split(aPath)[0], 'dll', aLibFolder, aLibFilename))
    if not os.path.exists(aPath):
        log.error('Cannot find the dynamic library for 7z and sbsar extraction at: %s', aPath)
        if aLibFolder == 'x86':
            log.error('The dynamic library for 7z and sbsar extraction is currently not available for 32 bit platforms')
        aPath = None

if aPath:
    try:
        if python_helpers.isPython2():
            aPath = aPath.encode(sys.getfilesystemencoding())

        if platform.system() == 'Windows':
            sevenZipLib = ctypes.WinDLL(aPath)
        else:
            sevenZipLib = ctypes.CDLL(aPath)

        seven_zip_extract = sevenZipLib.SZipExtract
        seven_zip_extract.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int]
        seven_zip_extract.restype = ctypes.c_int
    except:
        log.error('Failed to load the dynamic library for sbsar extraction at: %s\n\
        You won\'t be able to open .sbsar files', aPath )

def SevenZipExtract(aFilePath, aDestFolderPath, aFileToExtract = None, aKeepSubDirectories = False):
    """
    SevenZipExtract(aFilePath, aDestFolderPath, aFileToExtract = None, aKeepSubDirectories = False)
    Extract the 7z archive at the given path to the given destination folder.
    If aFileToExtract is specified, it will only extract the file with the given name.

    :param aFilePath: The absolute path to the 7z archive to extract
    :param aDestFolderPath: The destination folder
    :param aFileToExtract: The particular file to extract. Default to None
    :param aKeepSubDirectories: True to keep the subdirectories in the archive. Default to False
    :type aFilePath: str
    :type aDestFolderPath: str
    :type aFileToExtract: str, optional
    :type aKeepSubDirectories: bool, optional
    :return: True if succeed
    """
    if sevenZipLib and seven_zip_extract:
        fpbuf = python_helpers.ctypesStringBuffer(aFilePath)
        dpbuf = python_helpers.ctypesStringBuffer(aDestFolderPath)
        febuf = None if aFileToExtract is None else python_helpers.ctypesStringBuffer(aFileToExtract)
        res = seven_zip_extract(
                          fpbuf, ctypes.c_size_t(len(fpbuf)),
                          dpbuf, ctypes.c_size_t(len(dpbuf)),
                          febuf, ctypes.c_size_t(0 if febuf is None else len(febuf)),
                          ctypes.c_int(int(aKeepSubDirectories)))
        return res == 0
    else:
        raise SBSImpossibleActionError('Cannot extract 7z file, the dynamic library is not loaded')
