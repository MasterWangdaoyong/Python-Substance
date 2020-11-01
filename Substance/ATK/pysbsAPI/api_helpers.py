# coding: utf-8

from __future__ import unicode_literals
import os
import re
import hashlib
import math
import time
import platform
from random import randint

from pysbs.api_decorators import handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers
from pysbs import sbsenum


__pkgPrefix = 'pkg:///'
__filePrefix = 'file:///'
__identifierPattern = re.compile(u"[ <>().;:|?$£€~&*/\\\\]")
__uvPatternMARI = re.compile(r'^[1-9]\d{3}$')
__uvPatternSBS = re.compile(r'^\d+(x)\d+$')
__uvPatternUV = re.compile(r'^(u)\d+(_v)\d+$')


def getPkgPrefix():
    """
    Get the default package prefix

    :return: the default package prefix as a string ('pkg://')
    """
    return __pkgPrefix

def hasPkgPrefix(aPath):
    """
    hasPkgPrefix(aPath)
    Allows to check if the given path is relative to the package (starts with pkg://)

    :param aPath: the path to check
    :type aPath: string
    :return: True if the given path start with pkg:// or pkg:///, False otherwise
    """
    return True if aPath.startswith('pkg://') else False

def hasFilePrefix(aPath):
    """
    hasFilePrefix(aPath)
    Allows to check if the given path is a uri with file prefix (starts with file://)

    :param aPath: the path to check
    :type aPath: string
    :return: True if the given path start with file:// or file:///, False otherwise
    """
    return True if aPath.startswith('file://') else False

def removePkgPrefix(aPath):
    """
    removePkgPrefix(aPath)
    Remove the prefix pkg:// or pkg:/// if found in the given path

    :param aPath: the path to modify
    :type aPath: string
    :return: The resulting path
    """
    if hasPkgPrefix(aPath):
        aPath = aPath[7:] if len(aPath)>6 and aPath[6] == '/' else aPath[6:]
    return aPath

def removeFilePrefix(aPath):
    """
    removeFilePrefix(aPath)
    Remove the prefix file:// or file:/// if found in the given path

    :param aPath: the path to modify
    :type aPath: string
    :return: The resulting path
    """
    if hasFilePrefix(aPath):
        if platform.system() == "Windows":
            aPath = aPath[8:] if len(aPath)>7 and aPath[7] == '/' else aPath[7:]
        else:
            aPath = aPath[7:] if len(aPath) > 6 and aPath[6] == '/' else aPath[6:]
    return aPath

def isADependencyPath(aPath):
    """
    Check if the given aPath is a
    Check if the given aPath is a dependency path like pkg:///Resources/corsica_beach?dependency=1358524229

    :param aPath: A path
    :type aPath: str
    :return: True if the given is a dependency path
    """
    pattern = r"^(pkg:\/\/\/?)(.+\?)(dependency=[0-9]+$)"
    if re.match(pattern, aPath):
        return True
    return False

def isAUID(aObject):
    """
    isAUID(aObject)
    Check if the given aObject is a UID string

    :param aObject: The object to check
    :type aObject: any type
    :return: True if the given is a string and represents a UID
    """
    return python_helpers.isStringOrUnicode(aObject) and re.match('^[0-9]{10}$', aObject) is not None

def splitPathAndDependencyUID(aPath):
    """
    splitPathAndDependencyUID(aPath)
    If the given path is composed of a path and a dependency part (ex: pkg:///myPath?dependency=1234567890), split the path into the real path part and the dependency uid.
    If not, return (aPath,None)

    :param aPath: the path to split
    :type aPath: str
    :return: a tuple (path, dependencyUID) if possible, or (aPath, None) if the path does not contain a dependency tag
    """
    res = aPath.split('?dependency=')
    return tuple(res) if len(res)==2 else (res[0], None)

def getIdentifierFromInternalPath(aPath):
    """
    getIdentifierFromInternalPath(aPath)
    Given a path internal to a package (pkg:///myGroup/myObjectIdentifier?dependency=1234567890), return the identifier of the object (here: 'myObjectIdentifier').

    :param aPath: the path to consider
    :type aPath: str
    :return: the identifier of the object
    """
    aPath = splitPathAndDependencyUID(aPath=aPath)[0]
    pos = aPath.rfind('/')
    return aPath[pos+1:] if pos >= 0 else aPath

def getGroupPathFromInternalPath(aPath):
    """
    getGroupPathFromInternalPath(aPath)
    Given a path internal to a package (pkg:///myGroup/mySubGroup/myObjectIdentifier?dependency=1234567890), return the parent group tree (here: 'myGroup/mySubGroup').

    :param aPath: the path to consider
    :type aPath: str
    :return: the path of the parent group if it exist, '' otherwise
    """
    aPath = splitPathAndDependencyUID(aPath=aPath)[0]
    pos = aPath.rfind('/')
    return removePkgPrefix(aPath[0:pos]) if pos >= 0 else ''

def splitGroupAndIdentifierFromInternalPath(aPath):
    """
    splitGroupAndIdentifierFromInternalPath(aPath)
    Given a path internal to a package (pkg:///myGroup/myObjectIdentifier?dependency=1234567890), get the group and the identifier of the object (here: ('myGroup','myObjectIdentifier') ).

    :param aPath: the path to split
    :type aPath: str
    :return: a tuple (group, identifier)
    """
    return getGroupPathFromInternalPath(aPath),getIdentifierFromInternalPath(aPath)

def buildUniqueFilePart(aLength):
    """
    buildUniqueFilePart(aLength)
    Allows to build a unique string of the given length, made with alphanumerical characters

    :param aLength: the length of the resulting string
    :type aLength: int
    :return: The random string
    """
    aUniquePart = ''
    for i in range(aLength):
        aChar = randint(0, 0xffff) % (26 + 26)
        if aChar < 26:
            aUniquePart += chr(aChar + ord('A'))
        else:
            aUniquePart += chr(aChar - 26 + ord('a'))
    return aUniquePart


def buildUniqueFilePathWithPrefix(aAbsFolderPath, aFilename):
    """
    buildUniqueFilePathWithPrefix(aAbsFolderPath, aFilename)
    Allows to build a filename unique in the given folder, adding a numbered prefix to it.

    :param aAbsFolderPath: the absolute path of the folder
    :param aFilename: the filename
    :type aAbsFolderPath: str
    :type aFilename: str
    :return: The unique filename as a string
    """
    aPrefix = ''
    aResult = aFilename
    while os.path.exists(os.path.join(aAbsFolderPath, aResult)):
        if aPrefix == '':
            aPrefix = '1'
        else:
            aPrefix = str(int(aPrefix)+1)
        aResult = aPrefix + '-' + aFilename
    return aResult


def getRelativeObjectPathFromFilePath(aFilePath):
    """
    getRelativeObjectPathFromFilePath(aFilePath)
    Deduce a relative object path. If the path ends by a file .sbs or .sbsar its name will be use for the relative
    path object otherwise the path after the file will be used. It will remove any file:// prefix too.

    :param aFilePath: a file path as classic form or with an object extension /foo.sbs/my_graph or /foo.sbs/a_grp/my_graph
    :type aFilePath: str
    :return: Tuple, the absolute file path and the relative object path as a string
    """
    aCleanFilePath = removeFilePrefix(aFilePath)
    aBasename = os.path.basename(aFilePath)
    aName, aExt = os.path.splitext(aBasename)
    if aExt:
        return aCleanFilePath, getPkgPrefix() + aName
    else:
        aMatch = re.search(r"([/\\].[^.]+)$", aFilePath)
        if aMatch:
            aRelPath = aMatch.group(0)
            return aCleanFilePath[:-len(aRelPath)], getPkgPrefix() + aRelPath[1:]  # [1:] for remove first slash
        else:
            return ()


@handle_exceptions()
def addObjectToList(aObject, aMemberListName, aObjectToAdd):
    """
    addObjectToList(aObject, aMemberListName, aObjectToAdd)
    Add the given ObjectToAdd into the list identified by the given MemberListName in the given Object.

    :param aObject: The object that contains the list
    :param aMemberListName: The list name inside aSBSObject
    :param aObjectToAdd: The object to add to the list

    :type aObject: object of any kind
    :type aMemberListName: str
    :type aObjectToAdd: :class:`.SBSObject`

    :return: True if succeed, False otherwise
    """
    if not hasattr(aObject, aMemberListName) or getattr(aObject, aMemberListName) is None:
        setattr(aObject, aMemberListName, [])

    getattr(aObject, aMemberListName).append(aObjectToAdd)
    return True


@handle_exceptions()
def formatValueForTypeStr(aValue, aType, aSep = ' ', aDimension = -1, aBooleanAsString = False):
    """
    formatValueForTypeStr(aValue, aType, aSep = ' ', aBooleanAsString = False)
    Format the given value to respect the .sbs format according to the expected data type.

    :param aValue: input value
    :param aType: required type
    :param aSep: separator to use in the formatted string. Default is white space
    :param aDimension: dimension of the type, e.g. number of values that the type should have. Default to -1
    :param aBooleanAsString: True to have the boolean written in strings ('false'/'true'), False for writing them as integers ('0'/'1'). Default to False
    :type aValue: any type
    :type aType: enum value in :class:`.ParamTypeEnum`
    :type aSep: str, optional
    :type aDimension: int, optional
    :type aBooleanAsString: bool, optional
    :return: The value correctly formatted for the required type as a string, as this type is saved in .sbs format, if possible, None otherwise
    """
    splitPattern = re.compile("[ ;,]+")

    if aType & sbsenum.TypeMasksEnum.NUMERIC:
        # Compute the required number of values
        aNbValuesInType = 0
        if aType == sbsenum.ParamTypeEnum.FLOAT_VARIANT:    aNbValuesInType = 4
        elif aType & sbsenum.TypeMasksEnum.SINGLE:          aNbValuesInType = 1
        elif aType & sbsenum.TypeMasksEnum.DIM2:            aNbValuesInType = 2
        elif aType & sbsenum.TypeMasksEnum.DIM3:            aNbValuesInType = 3
        elif aType & sbsenum.TypeMasksEnum.DIM4:            aNbValuesInType = 4
        if aDimension >= 0:
            aNbValuesInType = aDimension

        if aNbValuesInType == 0:
            return str(aValue)

        # Convert the given value to a list
        value = aValue
        if python_helpers.isStringOrUnicode(value):
            value = value.strip('[]')
            aList = re.split(splitPattern, value)
        elif isinstance(value, list):   aList = value
        else:                           aList = [value]

        # Build the result
        result = ''
        prevValue = 0
        for i in range(0,aNbValuesInType):
            # Ensure having the right number of values
            if i < len(aList):
                value = aList[i]
            else:
                if i > 0 and aType == sbsenum.ParamTypeEnum.FLOAT_VARIANT:
                    value = prevValue
                else:
                    value = 0
            if value is None or value == '':
                value = 0

            # Convert to the appropriate type
            if aType & sbsenum.ParamTypeEnum.BOOLEAN:
                if python_helpers.isStringOrUnicode(value):
                    if   value.lower() == 'true':   value = 1
                    elif value.lower() == 'false':  value = 0
                    else:                           value = int(value)
                value = 1 if value > 0 else 0
                if aBooleanAsString:
                    value = 'true' if value == 1 else 'false'

            elif aType & sbsenum.TypeMasksEnum.INTEGER:
                value = int(float(value))

            elif aType & sbsenum.TypeMasksEnum.FLOAT:
                value = round(float(value), 9)

                # Remove useless decimals 0
                value = str(value)
                dotPos = value.find('.')
                if dotPos > 0:
                    match = re.search(r'[0]+$', value[dotPos:])
                    if match:
                        value = value[0:dotPos - 1 + match.start()]

            value = str(value)
            if value == '-0':
                value = '0'

            result += value + aSep
            prevValue = value

        return result[0:-1]

    else:
        return python_helpers.castStr(aValue) if aValue is not None else ''


@handle_exceptions()
def getTypedValueFromStr(aValue, aType, aSep = ' '):
    """
    getTypedValueFromStr(aValue, aType, aSep = ' ')
    Get the typed value from a string formatted as in .sbs format.

    :param aValue: input value
    :param aType: required type
    :param aSep: separator to use in the formatted string. Default is white space
    :type aValue: str
    :type aType: enum value in :class:`.ParamTypeEnum`
    :type aSep: str, optional
    :return: The value correctly typed considering the required type
    """
    if aType & sbsenum.TypeMasksEnum.NUMERIC:
        # Split the given value using the separator
        aList = re.split(aSep, aValue)

        # Build the result
        result = []
        for value in aList:
            # Convert to the appropriate type
            if aType & sbsenum.ParamTypeEnum.BOOLEAN:
                value = True if value =='1' or value.lower() == 'on' or value.lower() == 'true' else False

            elif aType & sbsenum.TypeMasksEnum.INTEGER:
                value = int(float(value))

            elif aType & sbsenum.TypeMasksEnum.FLOAT:
                value = round(float(value), 7)

            result.append(value)

        return result[0] if len(result) == 1 else result
    else:
        return aValue


def tryConversionToFloat(aValue):
    """
    tryConversionToFloat(aValue)
    Try to convert the given value to a float or a list of float.
    If the conversion fails the input value is returned.

    :param aValue: The value to convert
    :type aValue: str
    :return: the value converted to a float or a list of float if success, or the input value itself if the conversion failed
    """
    try:
        aList = re.split(' ', aValue)
        result = []
        for value in aList:
            value = round(float(value), 7)
            result.append(value)

        return result[0] if len(result)==1 else result
    except:
        return aValue


@handle_exceptions()
def formatIdentifier(aIdentifier):
    """
    formatIdentifier(aIdentifier)
    Format correctly the given identifier for Substance Designer

    :param aIdentifier: The identifier to format
    :type aIdentifier: str
    :return: The correctly formatted identifier
    """
    udimDollsPattern = r"(?P<open>\$\()(udim|u|v)(?P<close>\))"
    aDollsMatch = re.search(udimDollsPattern, aIdentifier)
    if aDollsMatch:
        aIdentifier = aIdentifier.replace(aDollsMatch.groupdict()['open'], "[").replace(aDollsMatch.groupdict()['close'], "]")
    return __identifierPattern.sub('_', aIdentifier) if aIdentifier != '' else 'Untitled'

@handle_exceptions()
def formatUVTileToSBSFormat(aUVTile):
    """
    formatUVtileToSBSFormat(aUVTile)
    Format the given input to the UV tile format used in SBS format, e.g. {u}x{v} (for instance '0x1').
    The given input can be:
    - a tuple (for instance (u,v))
    - a list [u,v]
    - a string, in MARI udim format ('1001') or ('u0_v0') or '0x0', or 'all' to consider all UV tiles

    :param aUVTile: The given UV tile to convert to SBS format
    :type aUVTile: tuple, list or string
    :return: a string
    """
    res = aUVTile
    if isinstance(aUVTile, tuple) or (isinstance(aUVTile, list) and len(aUVTile) >= 2):
        res =  '%sx%s' % (aUVTile[0], aUVTile[1])
    elif python_helpers.isStringOrUnicode(aUVTile):
        if len(aUVTile)==4 and re.match(__uvPatternMARI, aUVTile) is not None:
            udim = int(aUVTile)
            c = udim - 1000 - 1
            u = int(c % 10)
            v = int((c-u) / 10)
            res ='%sx%s' % (u, v)
        elif (re.match(__uvPatternSBS, aUVTile)) is not None:
            res = aUVTile
        elif (re.match(__uvPatternUV, aUVTile)) is not None:
            splitUV = aUVTile.split('_')
            res = '%sx%s' % (splitUV[0][1:], splitUV[1][1:])
    return python_helpers.castStr(res)

@handle_exceptions()
def convertUVTileToFormat(aUVTile, aFormat):
    """
    convertUVTileToFormat(aUVTile, aFormat)

    :param aUVTile: The UV tile, expressed in the .sbs format (UxV)
    :type aUVTile: str
    :param aFormat: The expected format
    :type aFormat: :class:`.UVTileFormat`
    :return: The UV tile converted in the expected format. If 'all' was given in input, 'all' will be returned
    """
    if aUVTile == 'all':
        return aUVTile
    if not python_helpers.isStringOrUnicode(aUVTile) or re.match(__uvPatternSBS, aUVTile) is None:
        raise SBSImpossibleActionError('The provided UV tile %s is not in the SBS format' % python_helpers.castStr(aUVTile))

    u, v = aUVTile.split('x')
    if aFormat == sbsenum.UVTileFormat.UDIM:
        udim = 1001 + int(u) + 10*int(v)
        return python_helpers.castStr(udim)
    elif aFormat == sbsenum.UVTileFormat.uU_vV:
        return 'u%s_v%s' % (u,v)
    elif aFormat == sbsenum.UVTileFormat.UV_LIST:
        return [int(u), int(v)]
    elif aFormat == sbsenum.UVTileFormat.UV_TUPLE:
        return int(u),int(v)
    return aUVTile


@handle_exceptions()
def convertUVTileToUdimPattern(aPath):
    """
    Convert udim or uvTile syntax into a designer pattern

    :param aPath: a resource path
    :return: a complete path
    """
    aRegUdim = r"([^a-zA-Z0-9])(?P<udim>[1-9]\d{3})([^a-zA-Z0-9])"
    replaceUdim = r"$(udim)"
    regUV = r"([^a-zA-Z0-9])(?P<u>[uU]-?(\d{1,3}))([^a-zA-Z0-9]?)(?P<v>[vV]-?(\d{1,3}))([^a-zA-Z0-9])"
    aMatch = re.search(aRegUdim, aPath)
    if aMatch:
        return aPath.replace(aMatch.groupdict()['udim'], replaceUdim)
    aMatch = re.search(regUV, aPath)
    if aMatch:
        return aPath.replace(aMatch.groupdict()['u'], '$(u)').replace(aMatch.groupdict()['v'], '$(v)')
    else:
        return aPath


@handle_exceptions()
def computeChecksumMD5(aAbsFilePath):
    """
    computeChecksumMD5(aAbsFilePath)
    Compute  the MD5 checksum of the given file.

    :param aAbsFilePath: Absolute path of the file
    :type aAbsFilePath: str
    :return: The checksum of the file as a string
    """
    hash_md5 = hashlib.md5()
    with open(aAbsFilePath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


@handle_exceptions()
def getLastModificationTime(aAbsFilePath):
    """
    getLastModificationTime(aAbsFilePath)
    Get the last modification time of the given file

    :param aAbsFilePath: Absolute path of the file
    :type aAbsFilePath: str
    :return: The modification date in the format %Y-%m-%dT%H:%M:%S as a string
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(aAbsFilePath)))

@handle_exceptions()
def getCurrentTime():
    """
    getCurrentTime()
    Get the current time in the appropriate format

    :return: The current date in the format %Y-%m-%dT%H:%M:%S as a string
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())

@handle_exceptions()
def getNearestPowerOf2(aInt):
    """
    getNearestPowerOf2(aInt)

    :param aInt: the input integer to convert to a power of two
    :param aInt: integer
    :return: The nearest greater power of two corresponding to the given integer (1018 will return 10 for instance)
    """
    return int(math.ceil(math.log(float(aInt), 2)))


@handle_exceptions()
def splitExtension(aFilepath):
    """
    splitExtension(aFilepath)
    Split the filename and the extension of the given file and return them as a tuple.

    :param aFilepath: the path of the file
    :type aFilepath: str
    :return: a tuple(str,str)
    """
    aParts = os.path.splitext(os.path.basename(aFilepath))
    aFilename = aParts[0] if aParts[1] != '' else ''
    aExtension = aParts[1] if aParts[1] != '' else aParts[0]
    return tuple((aFilename, aExtension))

@handle_exceptions()
def getInputsInVisibleIfExpression(aVisibleIfExpr):
    """
    getInputsInVisibleIfExpression(aVisibleIfExpr)
    Get the list of inputs parameters referenced in the given VisibleIf expression as strings

    :param aVisibleIfExpr: the VisibleIf expression
    :type aVisibleIfExpr: str
    :return: the list of input parameters as string
    """
    pattern = re.compile('input\["[^\]]+"\]')
    match = re.search(pattern, aVisibleIfExpr)
    aParams = []
    while match is not None:
        aParams.append(aVisibleIfExpr[match.start()+7:match.end()-2])
        aVisibleIfExpr = aVisibleIfExpr[match.end():]
        match = re.search(pattern, aVisibleIfExpr)

    return aParams

@handle_exceptions()
def escapeXMLTag(aString):
    """
    escapeXMLTag(aString)
    Escape < and > chars in the given string

    :param aString: the string to escape
    :type aString: str
    :return: The escaped string
    """
    aString = aString.replace('<', '&lt;')
    aString = aString.replace('>', '&gt;')
    return aString

@handle_exceptions()
def unescapeXMLTag(aString):
    """
    unescapeXMLTag(aString)
    Unescape < and > chars in the given string

    :param aString: the string to unescape
    :type aString: str
    :return: The unescaped string
    """
    aString = aString.replace('&lt;', '<')
    aString = aString.replace('&gt;', '>')
    return aString



def yieldFilesWithExtension(rootPath, extension, excludeFolders):
    """
    yieldFilesWithExtension(rootPath, extension, excludeFolders)
    Generator allowing to get all files of the given extension recursively from the given path.

    :param rootPath: The path of the folder tree to explore
    :param extension: The extension to look for
    :param excludeFolders: A set of folder names to exclude at each level, for instance ['.autosave']
    :type rootPath: str
    :type extension: str
    :type excludeFolders: list of str
    :return: The absolute path of the next file with this extension in the tree as a string
    """
    rootPath = python_helpers.castStr(rootPath)
    for root, dirs, files in os.walk(rootPath):
        for excludeDir in excludeFolders:
            if excludeDir in dirs:
                dirs.remove(excludeDir)
        for f in files:
            if f.endswith(extension):
                yield os.path.join(root, f)


@handle_exceptions()
def popOption(optionName, optionList):
    """
    popOption(optionName, optionList)
    Search for an option with the given name in the given SBSOption list, and remove it from the the list.

    :param optionName: The name of the option to look for in the list
    :type optionName: str
    :param optionList: The list of SBSOption
    :type optionList: list of :class:`.SBSOption`
    :return: The option value if found, None otherwise
    """
    index = next((index for index, option in enumerate(optionList) if option.mName == optionName), None)
    if index is not None:
        option = optionList.pop(index)
        return option.mValue
    return None
