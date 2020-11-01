# coding: utf-8
"""
Module api_exceptions defines the exceptions raised by the API
"""
from __future__ import unicode_literals
from pysbs import python_helpers
from distutils.version import LooseVersion


class APIException(Exception):
    """
    Base class for all API Exceptions
    """
    def __init__(self, aMessage):
        self.message = aMessage

    def __unicode__(self):
        return self.message

    def __str__(self):
        return unicode(self).encode('utf-8') if python_helpers.UNICODE_EXISTS else self.__unicode__()


class SBSLibraryError(APIException):
    """
    Exception SBSLibraryError, an exception raised when a bad parameter is set in an entity defined in the library
    """
    def __init__(self, aMessage):
        super(SBSLibraryError, self).__init__(aMessage)


class SBSImpossibleActionError(APIException):
    """
    Exception SBSImpossibleActionError, an exception raised when an operation is not possible on the given objects
    """
    def __init__(self, aMessage):
        super(SBSImpossibleActionError, self).__init__(aMessage)


class SBSMissingDependencyError(SBSImpossibleActionError):
    def __init__(self, aMessage, dependency):
        """
        Exception SBSMissingDependencyError, an exception raised when a dependency is missing in package, cause by a missing
        graph or a wrong given relative path.
        :param aMessage: message to print by the exception.
        :param dependency: the dependency missing path.
        :type aMessage: str
        :type dependency: str
        """
        super(SBSMissingDependencyError, self).__init__(aMessage)
        self.mMissingDependency = dependency


class SBSUninitializedError(APIException):
    """
    Exception SBSUninitializedError, an exception raised when requesting information on a non-parsed Substance
    """
    _defaultMessage = 'Failed to get the content of this package.\n\
If you are trying to open an existing package, please be sure to use parseDoc() function on the corresponding SBSDocument before requesting its content.\n\
If you are trying to create a new package, please be sure to use sbsgenerator.createSBSDocument() function to properly initialize it'

    def __init__(self, aMessage = None):
        super(SBSUninitializedError, self).__init__(aMessage if aMessage is not None else SBSUninitializedError._defaultMessage)


class SBSProcessInterruptedError(APIException):
    """
    Exception SBSProcessInterruptedError, an exception raised when a batched process is interrupted
    """
    def __init__(self, aMessage):
        super(SBSProcessInterruptedError, self).__init__(aMessage)


class SBSIncompatibleVersionError(APIException):
    """
    Exception SBSIncompatibleVersionError, an exception raised when package with an incompatible version is parsed
    """
    def __init__(self, aPackagePath, aSupportedVersion, aSupportedUpdaterVersion, aIncompatibleVersion, aIncompatibleUpdaterVersion):
        super(SBSIncompatibleVersionError, self).__init__('')
        strIncompatibleVersion = '('+str(aIncompatibleVersion)+' / '+str(aIncompatibleUpdaterVersion)+')'
        strSupportedVersion = '('+str(aSupportedVersion)+' / '+str(aSupportedUpdaterVersion)+')'
        try:
            mustUpdateSBS = False
            if LooseVersion(aSupportedVersion) > LooseVersion(aIncompatibleVersion) or \
                LooseVersion(aSupportedUpdaterVersion) > LooseVersion(aIncompatibleUpdaterVersion):
                    mustUpdateSBS = True

            if mustUpdateSBS:
                self.message = '\nThe package '+aPackagePath+' has been created with an older version of SBS format '+strIncompatibleVersion+\
            ', which is incompatible with the one supported by the API '+strSupportedVersion+'. \n'+\
            'Please use Substance Designer or the Batch Tool sbsmutator or sbsupdater to put this package in the appropriate version.\n'+\
            'This may also be related to upgrading the Automation toolkit without installing the updated pysbs python package'

            else:
                self.message = '\nThe package '+aPackagePath+' has been created with a newer version of SBS format '+strIncompatibleVersion+\
            ', which is incompatible with the one supported by the API '+strSupportedVersion+'. \n'+\
            'Please upgrade the API to have it compatible with the version of Substance Designer you are using.'

        except:
            self.message = '\nThe package '+aPackagePath+' has a format version '+strIncompatibleVersion+\
            ', which is incompatible with the one supported by the API '+strSupportedVersion+'.'


class SBSTypeError(APIException):
    """
    Exception SBSTypeError, an exception raised when an inappropriately typed object is used in the
    autograph system
    """
    def __init__(self, aMessage):
        super(SBSTypeError, self).__init__(aMessage)


class SBSMetaDataTreeNameConflict(APIException):
    """
    Exception SBSMetaDataTreeNameConflict, an exception raised when a metadata name is already used.
    """
    def __init__(self, aMessage):
        super(SBSMetaDataTreeNameConflict, self).__init__(aMessage)
