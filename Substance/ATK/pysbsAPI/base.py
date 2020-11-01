# coding: utf-8
"""
Module **base** contains all the services related to the communication between the application and the functions.
(Internal use only)
"""

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import sys
import xml.etree.ElementTree as ET

from pysbs import context

# ==============================================================================
class ReturnValue:
    def __init__(self):
        self.mDict = {}

    def getValue(self, aName):
        return self.mDict[aName]

    def setValue(self, aName, aValue):
        # type: (object, object) -> object
        self.mDict[aName] = aValue

    def getKeys(self):
        return self.mDict.keys()

    def getValueDict(self):
        return self.mDict


# ==============================================================================
class CommandLineArgs:
    def __init__(self):
        self.mArgs = {}

    def hasArgument(self, aArgName):
        return aArgName in self.mArgs

    def getArgument(self, aArgName):
        return self.mArgs.get(aArgName)

    def parseArgs(self, aArgs):
        def isArgument(aStr):
            return aStr.startswith('-') and aStr.endswith(':')
        #======================================================================
        def getArgumentName(aStr):
            return aStr[1:-1]
        #======================================================================

        i = 0
        self.mArgs = {}
        argsLen = len(aArgs)
        while i < argsLen:
            arg = aArgs[i]
            i += 1

            if arg is None:
                continue

            if isArgument(arg):
                argName = getArgumentName(arg)
                # Add argument
                self.mArgs[argName] = True

                if i < argsLen:
                    nextArg = aArgs[i]
                    if not isArgument(nextArg):
                        self.mArgs[argName] = nextArg
                        i += 1

# ==============================================================================
class ArgsFile:
    def __init__(self, aFileAbsPath):
        self.mFileAbsPath = aFileAbsPath
        self.mXMLRoot = None
        self.mSBSContext = context.Context()
        self.mFctArgs = {}

    def getSBSContext(self):
        return self.mSBSContext

    def getFunctionArgs(self):
        return self.mFctArgs

    def parse(self):
        # Get fctArgs from file:
        try:
            tree = ET.parse(self.mFileAbsPath)
            self.mXMLRoot = tree.getroot()
            if self.mXMLRoot is None:
                return False
        except:
            log.error('[ArgsFile.parse] Fail to parse file %s', self.mFileAbsPath)
            return False

        # Build SBS Context
        self.mSBSContext = context.Context()
        xmlElmtContext = self.mXMLRoot.find('context')
        aliasMgr = self.mSBSContext.getUrlAliasMgr()
        if xmlElmtContext is not None:
            # URl Aliases
            xmlElmtUrlAliases = xmlElmtContext.find('url_aliases')
            if xmlElmtUrlAliases is not None:
                xmlElmtChildren = xmlElmtUrlAliases.findall('url_alias[@name][@path]')
                for xmlElmtChild in xmlElmtChildren:
                    aliasName = xmlElmtChild.get('name')
                    aliasPath = xmlElmtChild.get('path')
                    if aliasName and aliasPath:
                        aliasMgr.setAliasAbsPath(aliasName, aliasPath)

        # Build function arguments
        self.mFctArgs = {}
        xmlElmtArgs = self.mXMLRoot.find('fct_args')
        if xmlElmtArgs is not None:
            # Args
            xmlElmtChildren = xmlElmtArgs.findall('arg[@name][@value]')
            for xmlElmtChild in xmlElmtChildren:
                argName = xmlElmtChild.get('name')
                argValue = xmlElmtChild.get('value')
                if argName and argValue is not None:
                    self.mFctArgs[argName] = argValue

        return True

# ==============================================================================
class CommandLineArgsProcessor:
    def __init__(self, aCallerModuleName = __name__):
        self.mCallerPyModule = sys.modules[aCallerModuleName]

    def call(self):
        aContext = CommandLineArgs()
        aContext.parseArgs(sys.argv[1:])
        exitCode = self.__execute(aContext)
        sys.exit(exitCode)

    # ==============================================================================
    # Return status are inverted regarding the sys.exit documentation:
    # 0 means 'Successful termination
    # != means 'abnormal termination
    # How does SD interprets this status ?
    def __execute(self, aContext):
        fctName = aContext.getArgument("fct")
        argsFileAbsPath = aContext.getArgument("args")
        retValFile = aContext.getArgument("retval")

        if fctName is None or fctName is True or len(fctName) == 0:
            log.error('Please provide the name of the function to execute with argument "fct"')
            return 0

        if self.mCallerPyModule is None:
            return 0

        if not hasattr(self.mCallerPyModule, fctName):
            log.error('Function "%s" not found', str(fctName))
            return 0
        fct = getattr(self.mCallerPyModule, fctName)

        argsFile = ArgsFile(argsFileAbsPath)
        if not argsFile.parse():
            log.error('Fail to parse argument file :"%s"', argsFileAbsPath)
        fctArgsDict = argsFile.getFunctionArgs()
        fctArgsDict['aContext'] = argsFile.getSBSContext()

        # call fct
        log.info('Calling fct "%s" with args %s', fctName, str(fctArgsDict))
        returnValue = fct(**fctArgsDict)

        # write return value to retValFile
        if returnValue is not None and retValFile is not None:
            xmlRoot = ET.Element('return_value')
            if isinstance(returnValue, ReturnValue):
                for key in returnValue.getKeys():
                    attributes = {'name': key, 'value': returnValue.getValue(key)}
                    ET.SubElement(xmlRoot, 'data', attributes)
            else:
                xmlRoot.text = str(returnValue)

            fileContent = ET.tostring(xmlRoot, encoding="utf-8")

            f = open(retValFile, 'wt')
            if f is not None:
                f.write(fileContent)
                f.close()

        return 1
