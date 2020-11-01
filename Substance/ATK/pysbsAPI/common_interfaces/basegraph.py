"""
Module **basegraph** aims to define base classes related to the graphs in .sbs and .sbsar packages:
    - :class:`.BaseGraph`
    - :class:`.Graph`
"""

from __future__ import unicode_literals
import abc

from pysbs.api_decorators import doc_inherit,handle_exceptions


# ==============================================================================
@doc_inherit
class BaseGraph:
    """
    Class used to provide a common interface between a :class:`.Graph` and a :class:`.MDLGraph`.

    Members:
        * mIdentifier: Unique identifier of the graph
        * mParamInputs: Absolute directory of the package
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aIdentifier, aParamInputs):
        self.mIdentifier   = aIdentifier
        self.mParamInputs  = aParamInputs

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
    def getAllInputs(self):
        """
        getAllInputs()
        Get the list of all inputs (images and parameters) defined on this graph

        :return: a list of inputs as :class:`.ParamInput`
        """
        return self.mParamInputs if self.mParamInputs is not None else []

    @abc.abstractmethod
    def getAllInputsInGroup(self, aGroup):
        """
        getAllInputsInGroup(aGroup)
        | Get the list of all inputs (images and parameters) contained in the given group.
        | If aGroup is None, returns all the parameters that are not included in a group.

        :param aGroup: The group of parameter to consider, given a SBSARGuiGroup object or a Group identifier
        :type aGroup: :class:`.SBSARGuiGroup` or str
        :return: a list of inputs
        """
        pass

    def getAllInputGroups(self):
        """
        getAllInputGroups()
        Get the list of all groups used for the inputs of the graph.

        :return: a list of groups as strings
        """
        groupList = set([aInput.getGroup() for aInput in self.getAllInputs() if aInput.getGroup()])
        return sorted(list(groupList))

    @handle_exceptions()
    def getInput(self, aInputIdentifier):
        """
        getInput(aInputIdentifier)
        Get the ParamInput with the given identifier, among the input images and parameters

        :param aInputIdentifier: input parameter identifier
        :type aInputIdentifier: str
        :return: the corresponding :class:`.ParamInput` object if found, None otherwise
        """
        return next((aInput for aInput in self.getAllInputs() if aInput.mIdentifier == aInputIdentifier), None)

    @handle_exceptions()
    def getInputFromUID(self, aInputUID):
        """
        getInputFromUID(aInputUID)
        Get the ParamInput with the given UID, among the input images and parameters

        :param aInputUID: input parameter UID
        :type aInputUID: str
        :return: the corresponding :class:`.ParamInput` object if found, None otherwise
        """
        return next((aInput for aInput in self.getAllInputs() if aInput.mUID == aInputUID), None)

    @handle_exceptions()
    def getInputImages(self):
        """
        getInputImages()
        Get the list of image inputs

        :return: a list of image inputs as ParamInput
        """
        return [aInput for aInput in self.getAllInputs() if aInput.isAnInputImage()]

    @handle_exceptions()
    def getInputImage(self, aInputImageIdentifier):
        """
        getInputImage(aInputImageIdentifier)
        Get the image input with the given identifier

        :param aInputImageIdentifier: input image identifier
        :type aInputImageIdentifier: str
        :return: a :class:`.ParamInput` if found, None otherwise
        """
        return next((aInput for aInput in self.getInputImages() if aInput.mIdentifier == aInputImageIdentifier), None)

    @handle_exceptions()
    def getInputImageWithUsage(self, aUsage):
        """
        getInputImageWithUsage(aUsage)
        Get the first image input which has the given usage defined

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.ParamInput` if found, None otherwise
        """
        return next((aInput for aInput in self.getInputImages() if aInput.hasUsage(aUsage)), None)

    @handle_exceptions()
    def getInputParameters(self):
        """
        getInputParameters()
        Get the list of input parameters (not image)

        :return: a list of :class:`.ParamInput`
        """
        return [aInput for aInput in self.getAllInputs() if aInput.isAnInputParameter()]

    @handle_exceptions()
    def getInputParameter(self, aInputParamIdentifier):
        """
        getInputParameter(aInputParamIdentifier)
        Get the input parameter with the given identifier

        :param aInputParamIdentifier: input parameter identifier
        :type aInputParamIdentifier: str
        :return: the corresponding :class:`.ParamInput` object if found, None otherwise
        """
        return next((aInput for aInput in self.getInputParameters() if aInput.mIdentifier == aInputParamIdentifier), None)

    @handle_exceptions()
    def getInputParameterFromUID(self, aInputParamUID):
        """
        getInputParameterFromUID(aInputParamUID)
        Get the input parameter with the given UID

        :param aInputParamUID: input parameter UID
        :type aInputParamUID: str
        :return: the corresponding :class:`.ParamInput` object if found, None otherwise
        """
        return next((aInput for aInput in self.getAllInputs() if aInput.mUID == aInputParamUID), None)



# ==============================================================================
@doc_inherit
class Graph(BaseGraph):
    """
    Class used to provide a common interface between a :class:`.SBSGraph` and a :class:`.SBSARGraph`.

    Members:
        * mIdentifier: Unique identifier of the graph
        * mPrimaryInput: Execution context, with alias definition
        * mParamInputs: Absolute directory of the package
        * mGraphOutputs: Absolute path of the package
        * mPresets: List of parameters presets
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aIdentifier, aPrimaryInput, aParamInputs, aGraphOutputs, aPresets):
        super(Graph, self).__init__(aIdentifier, aParamInputs)
        self.mPrimaryInput = aPrimaryInput
        self.mGraphOutputs = aGraphOutputs
        self.mPresets = aPresets

    @handle_exceptions()
    def getAllPresets(self):
        """
        getAllPresets()
        Get all the presets defined on this graph

        :return: a list of :class:`.Preset`
        """
        return self.mPresets if self.mPresets is not None else []

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
    def getGraphOutputs(self):
        """
        getGraphOutputs()
        Get all the graph outputs

        :return: the list of :class:`.GraphOutput` defined on this graph
        """
        return self.mGraphOutputs if self.mGraphOutputs is not None else []

    @handle_exceptions()
    def getGraphOutput(self, aOutputIdentifier):
        """
        getGraphOutput(aOutputIdentifier)
        Get the graph output with the given identifier

        :param aOutputIdentifier: identifier of the output
        :type aOutputIdentifier: str
        :return: a :class:`.GraphOutput` object if found, None otherwise
        """
        return next((output for output in self.getGraphOutputs() if output.mIdentifier == aOutputIdentifier), None)

    @handle_exceptions()
    def getGraphOutputWithUsage(self, aUsage):
        """
        getGraphOutputWithUsage(aUsage)
        Get the first graph output which has the given usage defined

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.GraphOutput` object if found, None otherwise
        """
        return next((output for output in self.getGraphOutputs() if output.hasUsage(aUsage)), None)

    @handle_exceptions()
    def getPreset(self, aPresetLabel):
        """
        getPreset(aPresetLabel)
        Get the preset with the given label

        :return: a :class:`.Preset` object if found, None otherwise
        """
        return next((aPreset for aPreset in self.getAllPresets() if aPreset.mLabel==aPresetLabel), None)

    @abc.abstractmethod
    def getPrimaryInput(self):
        """
        getPrimaryInput()
        Get the primary input of the graph

        :return: The primary input as a string if it exists, None otherwise
        """
        pass

    @abc.abstractmethod
    def isPrimaryInput(self, aInput):
        """
        isPrimaryInput(aInput)
        Check if the given input is the primary input for this graph or not

        :param aInput: The input to check
        :type aInput: str
        :return: True if this is the primary input, False otherwise
        """
        pass
