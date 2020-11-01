# coding: utf-8
"""
Module **package** aims to define all common interfaces related to the .sbs and .sbsar packages:
    - :class:`.Package`
    - :class:`.ParamInput`
    - :class:`.GraphOutput`
    - :class:`.Preset`
    - :class:`.PresetInput`
"""

from __future__ import unicode_literals
import abc
import os

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs import sbsenum

# ==============================================================================
class Package:
    """
    Class used to provide a common interface between a :class:`.SBSDocument` and a :class:`.SBSArchive`.

    Members:
        * mContext      (:class:`.Context`): Execution context, with alias definition
        * mFileAbsPath  (str): Absolute path of the package
        * mDirAbsPath   (str): Absolute directory of the package
        * mIsAnArchive  (bool): True for a .sbsar, False for a .sbs
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, aContext, aFileAbsPath):
        self.mContext     = aContext
        self.mFileAbsPath = aContext.getUrlAliasMgr().toAbsPath(aFileAbsPath, '')
        self.mDirAbsPath  = self.__getSBSFileDirAbsPath()
        self.mIsAnArchive = Package.isAnArchive(self.mFileAbsPath)

        self._mIsInitialized = False

    @abc.abstractmethod
    def buildAbsPathFromRelToMePath(self, aRelPathFromPackage):
        """
        buildAbsPathFromRelToMePath(aRelPathFromPackage)
        Build a path starting from the current package absolute directory and complete it with the given relative path

        :param aRelPathFromPackage: The relative path from the current package
        :type aRelPathFromPackage: str
        :return: The complete path, as a string
        """
        pass

    @abc.abstractmethod
    def parseDoc(self, aResolveDependencies = True):
        """
        parseDoc(aResolveDependencies = True)
        Parse the file content

        :return: True if succeed
        """
        pass

    @abc.abstractmethod
    def getObjectFromInternalPath(self, aPath):
        """
        getObjectFromInternalPath(aPath)
        Get the object pointed by the given path, which must references the current package.

        :param aPath: the relative path, starting with 'pkg://'
        :type aPath: str
        :return: the pointed :class:`.SBSObject` if found, None otherwise
        """
        pass

    @abc.abstractmethod
    def getSBSGraph(self, aGraphIdentifier):
        """
        getSBSGraph(aGraphIdentifier)
        Get the Graph object with the given identifier

        :param aGraphIdentifier: Identifier of the graph to get
        :type aGraphIdentifier: str
        :return: A :class:`.Graph` object
        """
        pass

    @abc.abstractmethod
    def getSBSGraphPkgUrl(self, aGraph):
        """
        getSBSGraphPkgUrl(aGraph)
        Get the path of the given graph relatively to the current package (pkg:///.../aGraphIdentifier)

        :param aGraph: Identifier of the graph to get
        :type aGraph: A :class:`.SBSGraph` object
        :return: A string containing the relative path from the root content to the given graph, None otherwise
        """
        pass

    @abc.abstractmethod
    def getSBSGraphList(self):
        """
        getSBSGraphList()
        Get the list of all graphs defined in the .sbs file

        :return: A list of :class:`.Graph`
        """
        pass

    @staticmethod
    def isAnArchive(aFilePath):
        """
        isAnArchive(aFilePath)
        Check if the given filename is a .sbsar package or a .sbs package

        :param aFilePath: Path of the package
        :type aFilePath: str
        :return: True if the given path refers to an archive (.sbsar), False otherwise
        """
        return os.path.splitext(aFilePath)[1] == '.sbsar'

    @staticmethod
    def isAPackage(aFilePath):
        """
        isAPackage(aFilePath)
        Check if the given filename is a .sbs file or .sbsar file.

        :param aFilePath: Path of the package
        :type aFilePath: str
        :return: True if the given path ends with .sbs or .sbsar, False otherwise
        """
        aExt = os.path.splitext(aFilePath)[1]
        return aExt == '.sbsar' or aExt == '.sbs'

    def isInitialized(self):
        """
        isInitialized()
        Check if the package is correctly initialized (parsed or well setup for future usage)

        :return: True if the package is initialized, False otherwise
        """
        return self._mIsInitialized

    def setInitialized(self):
        """
        setInitialized()
        Set the package as initialized
        """
        self._mIsInitialized = True

    @staticmethod
    def removePackageExtension(aFilePath):
        """
        removePackageExtension(aFilePath)
        Remove the package extension to the given path (.sbs or .sbsar)

        :param aFilePath: Path of the package
        :type aFilePath: str
        :return: The same path without the package extension
        """
        if aFilePath.endswith('.sbsar'):        return aFilePath[0:-6]
        elif aFilePath.endswith('.sbs'):        return aFilePath[0:-4]
        else:                                   return aFilePath

    #==========================================================================
    # Private
    #==========================================================================
    def __getSBSFileDirAbsPath(self):
        return os.path.abspath(os.path.split(self.mFileAbsPath)[0])




# =======================================================================
class ParamInput:
    """
    Class used to provide a common interface between a :class:`.SBSParamInput` and a :class:`.SBSARInput`.

    Members:
        * mIdentifier: Unique identifier of the input
        * mUID: Unique Id of the input
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 aUID='',
                 aIdentifier=''):
        self.mUID = aUID
        self.mIdentifier = aIdentifier

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        """
        getAttribute(aAttributeIdentifier)
        Get the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :return: the attribute value if defined, None otherwise
        """
        pass

    @handle_exceptions()
    def getDimension(self):
        """
        getDimension()
        Get the dimension of the parameter type (1, 2, 3, or 4 values)

        :return: The dimension as an integer
        """
        aType = self.getType()
        if aType & sbsenum.TypeMasksEnum.SINGLE or aType == sbsenum.ParamTypeEnum.STRING:   return 1
        elif aType & sbsenum.TypeMasksEnum.DIM2:        return 2
        elif aType & sbsenum.TypeMasksEnum.DIM3:        return 3
        elif aType & sbsenum.TypeMasksEnum.DIM4:        return 4
        else:                                           return 1

    @handle_exceptions()
    def formatValueToType(self, aValue):
        """
        formatValueToType(aValue)
        Return the given value formatted in the appropriate type for this parameter (bool, int or float)

        :param aValue: The value to format
        :type aValue: string, bool, int, or float
        :return: The value as a bool, int of float depending on the parameter type
        """
        if aValue:
            aType = self.getType()
            if aType == sbsenum.ParamTypeEnum.BOOLEAN:
                return bool(int(aValue))
            elif aType & sbsenum.TypeMasksEnum.INTEGER:
                return int(aValue)
            elif aType & sbsenum.TypeMasksEnum.FLOAT:
                return float(aValue)
        return aValue

    @abc.abstractmethod
    def getGroup(self):
        """
        getGroup()
        Get the input GUI group containing this input

        :return: the GUI group as a string if defined, None otherwise
        """
        pass

    @abc.abstractmethod
    def getClamp(self):
        """
        getClamp()

        :return: the clamp as a boolean if defined for this parameter, None if not defined
        """
        pass

    @abc.abstractmethod
    def getMinValue(self, asList):
        """
        getMinValue(asList)

        :return: the minimum parameter value in the type of the parameter (int or float), None if not defined
        """
        pass

    @abc.abstractmethod
    def getMaxValue(self, asList):
        """
        getMaxValue(asList)

        :return: the maximum parameter value in the type of the parameter (int or float), None if not defined
        """
        pass

    @abc.abstractmethod
    def getDefaultValue(self):
        """
        getDefaultValue()

        :return: the default value as a value or a list of values, in the type of the parameter (bool, int or float), None if not defined
        """
        pass

    @abc.abstractmethod
    def getDropDownList(self):
        """
        getDropDownList()

        :return: the map{value(int):label(str)} corresponding to the drop down definition if defined for this parameter, None otherwise.
        """
        pass

    @abc.abstractmethod
    def getLabels(self):
        """
        getLabels()

        :return: the list of all labels defined for this parameter, in the right order, as a list of strings. None if not defined
        """
        pass

    @abc.abstractmethod
    def getStep(self):
        """
        getStep()

        :return: the step value (in the type of the parameter) of the widget for this parameter, None if not defined
        """
        pass

    @abc.abstractmethod
    def getUsages(self):
        """
        getUsages()
        Get the usages of this param input

        :return: the list of :class:`.SBSUsage` defined on this param input
        """
        pass

    @abc.abstractmethod
    def getWidget(self):
        """
        getWidget()

        :return: The widget used for this parameter, None if not defined
        """
        pass

    @abc.abstractmethod
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this param input

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this param input, False otherwise
        """
        pass

    @abc.abstractmethod
    def isAnInputImage(self):
        """
        isAnInputImage()
        Check if this input is of kind image.

        :return: True if this is an input image, False otherwise
        """
        pass

    @abc.abstractmethod
    def isAnInputParameter(self):
        """
        isAnInputParameter()
        Check if this input is a parameter.

        :return: True if this is an input parameter, False otherwise
        """
        pass

    @abc.abstractmethod
    def getType(self):
        """
        getType()
        Get the type of the input among the list defined in :class:`.ParamTypeEnum`.

        :return: The type of the parameter as a :class:`.ParamTypeEnum`
        """
        pass

    @abc.abstractmethod
    def getIsConnectable(self):
        """
        getIsConnectable()
        Returns True if this parameter can be connected to

        :return: (bool) If this input is connectable
        """
        return False

# =======================================================================
@doc_inherit
class GraphOutput:
    """
    Class used to provide a common interface between a :class:`.SBSGraphOutput` and a :class:`.SBSAROutput`.

    Members:
        * mUID         (str): identifier of the input.
        * mIdentifier  (str): uid of the input.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 aUID='',
                 aIdentifier=''):
        self.mUID = aUID
        self.mIdentifier = aIdentifier

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        """
        getAttribute(aAttributeIdentifier)
        Get the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :return: the attribute value if defined, None otherwise
        """
        pass

    @abc.abstractmethod
    def getUsages(self):
        """
        getUsages()
        Get the usages of this graph output

        :return: the list of usages defined on this output
        """
        pass

    @abc.abstractmethod
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this graph output

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this param input, False otherwise
        """
        pass

    @abc.abstractmethod
    def getType(self):
        """
        getType()
        Get the output type of this GraphOutput.

        :return: the output type in the format :class:`.ParamTypeEnum` if found, None otherwise
        """
        pass


# =======================================================================
@doc_inherit
class Preset:
    """
    Class used to provide a common interface between a :class:`.SBSPreset` and a :class:`.SBSARPreset`.

    Members:
        * mLabel         (str): label of the preset.
        * mPresetInputs  (list of :class:`.PresetInput`): list of preset inputs.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 aLabel='',
                 aUsertags = '',
                 aPresetInputs=None):
        self.mLabel = aLabel
        self.mUsertags = aUsertags
        self.mPresetInputs = aPresetInputs

    @handle_exceptions()
    def getPresetInputs(self):
        """
        getPresetInputs()
        Get the list of preset inputs defined in this preset

        :return: a list of :class:`.PresetInput`
        """
        return self.mPresetInputs if self.mPresetInputs is not None else []

    @handle_exceptions()
    def getPresetInput(self, aInputParam):
        """
        getPresetInput(aInputParam)
        Get the preset of the given input parameter

        :param aInputParam: the input parameter as ParamInput or identified by its uid
        :type aInputParam: :class:`ParamInput` or str
        :return: a :class:`.PresetInput` if found, None otherwise
        """
        if isinstance(aInputParam, ParamInput):
            aInputParam = aInputParam.mUID
        return next((pInput for pInput in self.getPresetInputs() if pInput.mUID == aInputParam), None)

    @handle_exceptions()
    def getPresetInputFromIdentifier(self, aInputParamIdentifier):
        """
        getPresetInputFromIdentifier(aInputParamIdentifier)
        Get the preset of the given input parameter

        :param aInputParamIdentifier: the input parameter identified by its identifier
        :type aInputParamIdentifier: str
        :return: a :class:`.PresetInput` if found, None otherwise
        """
        return next((pInput for pInput in self.getPresetInputs() if pInput.mIdentifier == aInputParamIdentifier), None)

    @handle_exceptions()
    def getInputValue(self, aInputUID):
        """
        getInputValue(aInputUID)
        Get the value of the given ParamInput in this preset

        :param aInputUID: UID of the input to get
        :type aInputUID: str
        :return: the input value in this preset if defined, None otherwise
        """
        aPresetInput = self.getPresetInput(aInputUID=aInputUID)
        return aPresetInput.getValue() if aPresetInput is not None else None


# =======================================================================
@doc_inherit
class PresetInput:
    """
    Class used to provide a common interface between a :class:`.SBSPresetInput` and a :class:`.SBSARPresetInput`.

    Members:
        * mUID        (str): uid of the input parameter targeted by this preset input
        * mIdentifier (str): identifier of the input parameter targeted by this preset input
        * mValue      (:class:`.SBSConstantValue`): value, depend on the type.
        * mType       (:class:`.SBSParamValue`): type of the input
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 aUID='',
                 aIdentifier='',
                 aValue=None,
                 aType=None):
        self.mUID        = aUID
        self.mIdentifier = aIdentifier
        self.mValue      = aValue
        self.mType       = aType

    def getValue(self):
        """
        getValue()
        Get the value of this preset input as it is saved in the file

        :return: the input value in this preset input
        """
        pass

    def getType(self):
        """
        getType()
        Get the type of the input among the list defined in :class:`.ParamTypeEnum`.

        :return: The type of the parameter as a :class:`.ParamTypeEnum`
        """
        pass

    def getTypedValue(self):
        """
        getTypedValue()
        Get the value of this preset input correctly formatted in the type of this preset (e.g. bool, int, float, list of int, ...)

        :return: The input value in the appropriate type
        """
        pass
