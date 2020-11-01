# coding: utf-8
"""
Module **mdlcommon** provides the definition of common interfaces for MDLObjects:

- :class:`.MDLObjectWithAnnotations`
- :class:`.MDLNodeImpl`
- :class:`.MDLImplWithOperands`
"""

from __future__ import unicode_literals
import abc

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSLibraryError, SBSImpossibleActionError
from pysbs import api_helpers
from pysbs import sbsenum
from pysbs.common_interfaces import SBSObject
from pysbs.sbslibrary import getUsage

from . import mdlenum
from . import MDLOperands
from . import mdldictionaries as mdldict


# =======================================================================
class MDLObjectWithAnnotations(object):
    """
    This abstract class allows to provide a common interface for all MDL object with annotations.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, aAllowedAnnotations, aAnnotations):
        self.mAllowedAnnotations = aAllowedAnnotations
        self.mAnnotations = aAnnotations

    @handle_exceptions()
    def getAnnotation(self, aAnnotation):
        """
        getAnnotation(aAnnotation)
        Get the given annotation.

        :param aAnnotation: The annotation to look for, as an enumeration or a mdl path
        :type aAnnotation: :class:`.MDLAnnotationEnum` or str
        :return: The annotation as a :class:`.MDLAnnotation`
        """
        if isinstance(aAnnotation, int):
            aAnnotation = mdldict.getAnnotationPath(aAnnotation)
        return next((annot for annot in self.mAnnotations if annot.mPath == aAnnotation), None)

    @handle_exceptions()
    def getAnnotationValue(self, aAnnotation):
        """
        getAnnotationValue(aAnnotation)
        Get the value of the given annotation.

        :param aAnnotation: The annotation to look for, as an enumeration or a mdl path
        :type aAnnotation: :class:`.MDLAnnotationEnum` or str
        :return: The annotation value as a string or list of string if found, None otherwise
        """
        annot = self.getAnnotation(aAnnotation)
        if annot:
            # Consider an annotation without operand as a boolean, when the annotation is present it means True
            return True if annot.mOperands.getNbOperands() == 0 else annot.getValue()
        return None

    @handle_exceptions()
    def getGroup(self):
        """
        getGroup()
        Get the 'in_group' annotation value

        :return: The group/subgroup/subsubgroup value if found, None otherwise
        """
        groupAnnot = self.getAnnotationValue(mdlenum.MDLAnnotationEnum.IN_GROUP)
        if isinstance(groupAnnot, list):
            return '/'.join(str(grp) for grp in groupAnnot if grp)
        return None

    @handle_exceptions()
    def getUsage(self):
        """
        getUsage()
        Get the 'sampler_usage' annotation value

        :return: The 'sampler_usage' value if found, None otherwise
        """
        usageAnnot = self.getAnnotationValue(mdlenum.MDLAnnotationEnum.SAMPLER_USAGE)
        return usageAnnot

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this constant node

        :param aUsage: The usage to look for (can be an enum value or a custom string)
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this param input, False otherwise
        """
        if isinstance(aUsage, int):
            aUsage = getUsage(aUsage)
        myUsage = self.getUsage()
        return myUsage == aUsage if myUsage else False

    @handle_exceptions()
    def removeAnnotation(self, aAnnotation):
        """
        removeAnnotation(aAnnotation)
        Remove the given annotation from the list of annotations

        :param aAnnotation: The annotation to look for, as an enumeration or a mdl path
        :type aAnnotation: :class:`.MDLAnnotationEnum` or str
        """
        annot = self.getAnnotation(aAnnotation)
        if annot:
            self.mAnnotations.remove(annot)

    @handle_exceptions()
    def setAnnotation(self, aAnnotation, aAnnotationValue):
        """
        setAnnotation(aAnnotation, aAnnotationValue)
        Set the given attribute

        :param aAnnotation: The annotation to set, as an enumeration or a mdl path
        :param aAnnotationValue: The value to set
        :type aAnnotation: :class:`.MDLAnnotationEnum`
        :type aAnnotationValue: str or list of str
        :raise: :class:`.SBSImpossibleActionError`
        """
        from .mdlmanager import MDLManager

        aAnnotationEnum = mdldict.getAnnotationEnum(aAnnotation) if not isinstance(aAnnotation, int) else aAnnotation
        aAnnotationPath = mdldict.getAnnotationPath(aAnnotationEnum)
        if not aAnnotationEnum in self.mAllowedAnnotations:
            raise SBSImpossibleActionError('Cannot set the annotation '+str(aAnnotationPath)+' on this object')

        annotDef = MDLManager.getMDLAnnotationDefinition(aAnnotationEnum)
        if not annotDef:
            raise SBSImpossibleActionError('Cannot find the annotation definition of '+str(aAnnotationPath))

        annot = self.getAnnotation(aAnnotationEnum)
        createAnnot = False

        # Consider an annotation without operand as a boolean, when the annotation is present it means True
        if not annotDef.mParameters:
            boolValue = api_helpers.getTypedValueFromStr(str(aAnnotationValue), sbsenum.ParamTypeEnum.BOOLEAN)
            if annot is not None and not boolValue:
                self.mAnnotations.remove(annot)
            elif annot is None and boolValue:
                createAnnot = True
        elif annot is None:
            createAnnot = True

        if createAnnot:
            annot = annotDef.toMDLAnnotation()
            self.mAnnotations.append(annot)
        annot.setValue(aAnnotationValue)

    @handle_exceptions()
    def setGroup(self, aGroup, aSubGroup=None, aSubSubGroup=None):
        """
        setGroup(aGroup, aSubGroup=None, aSubSubGroup=None)
        Set the 'in_group' annotation value with the given group and subgroups

        :param aGroup: The main group
        :param aSubGroup: The sub-group
        :param aSubSubGroup: The sub-sub-group
        :type aGroup: str
        :type aSubGroup: str, optional
        :type aSubSubGroup: str, optional
        """
        self.setAnnotation(mdlenum.MDLAnnotationEnum.IN_GROUP, [aGroup, aSubGroup, aSubSubGroup])

    @handle_exceptions()
    def setUsage(self, aUsage):
        """
        setUsage(aUsage)
        Set the 'sampler_usage' annotation value with the given usage

        :param aUsage: The usage to set
        :type aUsage: str
        """
        self.setAnnotation(mdlenum.MDLAnnotationEnum.SAMPLER_USAGE, aUsage)



# =======================================================================
@doc_inherit
class MDLNodeImpl(SBSObject):
    """
    This abstract class allows to provide a common interface for all MDL node implementation kind.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        super(MDLNodeImpl, self).__init__()

    @abc.abstractmethod
    def classify(self, aOther):
        """
        classify(aOther)
        Compare the path of the two instances to classify them.

        :param aOther: The filter to compare to.
        :type aOther: :class:`.MDLNodeImpl`
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        pass

    @abc.abstractmethod
    def getDisplayName(self):
        """
        getDisplayName()

        :return: the display name of this node as a string
        """
        return self.mUID

    @abc.abstractmethod
    def getDefinition(self):
        """
        getDefinition()
        Get the definition of the node (Inputs, Outputs, Parameters)

        :return: a :class:`.MDLNodeDef` object
        """
        pass

    @handle_exceptions()
    def getInputDefinition(self, aInputIdentifier=None):
        """
        getInputDefinition(self, aInputIdentifier=None)
        Get the input definition corresponding to the given identifier.

        :param aInputIdentifier: The identifier to get. If let None, the first input will be returned
        :type aInputIdentifier: str, optional
        :return: the input definition as a :class:`.MDLNodeDefInput` if found, None otherwise
        """
        nodeDef = self.getDefinition()
        if not nodeDef:
            return None
        if aInputIdentifier is not None:
            return nodeDef.getInput(aInputIdentifier)
        else:
            return nodeDef.getAllInputs()[0] if nodeDef.getAllInputs() else None

    @abc.abstractmethod
    def getOutputType(self, aOutputIdentifier=None):
        """
        getOutputType(aOutputIdentifier=None)
        Get the output type of this node given the output identifier.

        :param aOutputIdentifier: The output identifier to look for. If None, the first output will be considered
        :type aOutputIdentifier: str, optional
        :return: The node output type as a string (color or float) if found, None otherwise
        """
        pass

    @abc.abstractmethod
    def getParameter(self, aParameter=None):
        """
        getParameter(aParameter=None)
        Get the parameter with the given name among the parameters available on the node.
        aParameter can be None in case of a Constant or Selector node, where there is only one parameter.

        :param aParameter: Parameter identifier
        :type aParameter: str, optional
        :return: The parameter if found (:class:`.MDLParameter` or :class:`.MDLOperand`), None otherwise
        """
        pass

    @abc.abstractmethod
    def getParameterValue(self, aParameter=None):
        """
        getParameterValue(aParameter=None)
        Find a parameter with the given name among the parameters available on the node and return its value.
        aParameter can be None in case of a Constant or Selector node, where there is only one parameter.

        :param aParameter: Parameter identifier
        :type aParameter: str, optional
        :return: The parameter value if found (string or :class:`.MDLOperand`, None otherwise
        """
        pass

    @abc.abstractmethod
    def setParameterValue(self, aParameter, aParamValue):
        """
        setParameterValue(aParameter, aParamValue)
        Set the value of the given parameter to the given value, if compatible with this node.

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :type aParameter: str
        :type aParamValue: any parameter type
        :return: True if succeed, False otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        pass

    @abc.abstractmethod
    def resetParameter(self, aParameter = None):
        """
        resetParameter(aParameter = None)
        Reset the given parameter to its default value.
        aParameter can be None in case of a Constant or Selector node, where there is only one parameter.

        :param aParameter: identifier of the parameter to reset
        :type aParameter: str
        :return: True if succeed, False otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        pass



# =======================================================================
@doc_inherit
class MDLImplWithOperands(MDLNodeImpl):
    """
    This class allows to gather the parameter management for classes :class:`.MDLImplConstant`, :class:`.MDLImplMDLInstance`
    and :class:`.MDLImplMDLGraphInstance`

    Members:
        * mOperands (:class:`.MDLOperands`): input parameters list.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 aOperands = None):
        super(MDLImplWithOperands, self).__init__()
        self.mOperands = aOperands

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mOperands = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_operands', MDLOperands )

    @handle_exceptions()
    def getOperand(self, aOperandName):
        """
        getOperand(aOperandName)
        Get the operand with the given name

        :return: a :class:`.MDLOperand` object if found, None otherwise
        """
        return self.mOperands.getOperand(aOperandName) if self.mOperands else None

    @handle_exceptions()
    def getOperands(self):
        """
        getOperands()
        Get the list of operands objects

        :return: a list of :class:`.MDLOperand`
        """
        return self.mOperands.getAllOperands()

    @handle_exceptions()
    def getParameter(self, aParameter):
        return self.getOperand(aParameter)

    @handle_exceptions()
    def getParameterValue(self, aParameter):
        # Parse the parameters defined on the MDL node
        aOperand = self.getOperand(aParameter)
        return aOperand.getValue() if aOperand is not None else None

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        # Get the operand named with the given parameter name
        aOperand = self.getOperand(aParameter)
        if not aOperand:
            raise SBSLibraryError('Parameter '+aParameter+' cannot be set on '+self.getDisplayName())

        aOperand.setValue(aParamValue)
        aOperand.setIsDefaultValue(False)
        return True

    @handle_exceptions()
    def resetParameter(self, aParameter):
        # Get the operand named with the given parameter name
        aOperand = self.getOperand(aParameter)
        if not aOperand:
            raise SBSLibraryError('Parameter '+aParameter+' cannot be reset on '+self.getDisplayName())

        # Get the default value looking at the node definition
        nodeDef = self.getDefinition()
        defaultParam = nodeDef.getParameter(aParameter)
        aOperand.setValue(defaultParam.getDefaultValue() if defaultParam is not None else None)
        return True
