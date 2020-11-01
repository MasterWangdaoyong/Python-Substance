# coding: utf-8
"""
Module **params** aims to define SBSObjects that are relative to the Function nodes, mostly:
    - :class:`.SBSParamNode`
    - :class:`.SBSParamValue`
    - :class:`.SBSDynamicValue`

This module contains also the definition of the parameters (:class:`.SBSParameter`),
which are useful for the :class:`.SBSParamNode` and the :class:`.SBSCompNode`.
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs import api_helpers
from pysbs.common_interfaces import SBSObject
from pysbs import sbscommon

from .dynamicvalue import SBSDynamicValue


# ==============================================================================
@doc_inherit
class SBSParameter(SBSObject):
    """
    Class that contains information of a parameter as defined in a .sbs file.
    This class is used to define the parameters of a compositing node, a function node or even a graph.

    Members:
        * mName       (str): name of the parameter to define.
        * mRelativeTo (str, optional): parameter inheritance definition, among the list defined in :class:`.ParamInheritanceEnum`.
        * mParamValue (:class:`.SBSParamValue`): definition of the parameter (constant value or dynamic function)
    """
    def __init__(self,
                 aName = '',
                 aRelativeTo = None,
                 aParamValue = None):
        super(SBSParameter, self).__init__()
        self.mName          = aName
        self.mRelativeTo    = aRelativeTo
        self.mParamValue    = aParamValue

        self.mMembersForEquality = ['mName',
                                    'mRelativeTo']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName       = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'name'        )
        self.mRelativeTo = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'relativeTo'  )
        self.mParamValue = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'paramValue', SBSParamValue)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mName      , 'name'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mRelativeTo, 'relativeTo' )
        aSBSWriter.writeSBSNode(aXmlNode             ,  self.mParamValue, 'paramValue' )

    @handle_exceptions()
    def createEmptyDynamicValue(self):
        """
        createEmptyDynamicValue()
        Init a dynamic value for this parameter.
        Remove the previous constant value or dynamic value if defined.

        :return: the new empty :class:`.SBSDynamicValue`
        """
        if self.mParamValue is None:
            self.mParamValue = SBSParamValue()
        aValue = self.mParamValue.getValue()
        if isinstance(aValue, SBSDynamicValue):
            self.mParamValue.mDynamicValue = None
            del aValue

        aNewDynamicValue = SBSDynamicValue()
        self.mParamValue.setDynamicValue(aNewDynamicValue)
        return self.mParamValue.mDynamicValue

    @handle_exceptions()
    def getConstantValue(self):
        """
        getConstantValue()
        Get the constant value of this parameter

        :return: the constant value as a :class:`.SBSConstantValue` if it exists, None otherwise
        """
        return self.mParamValue.getConstantValue() if self.mParamValue is not None else None

    @handle_exceptions()
    def getDynamicValue(self):
        """
        getDynamicValue()
        Get the dynamic value of this parameter

        :return: the dynamic value as a :class:`.SBSDynamicValue` if it exists, None otherwise
        """
        return self.mParamValue.getDynamicValue() if self.mParamValue is not None else None

    @handle_exceptions()
    def setDynamicValue(self, aDynamicValue):
        """
        setDynamicValue(aDynamicValue)
        Set the dynamic value for this parameter.
        Remove the previous constant value or dynamic value if defined.

        :param aDynamicValue: the dynamic value to affect
        :type aDynamicValue: :class:`.SBSDynamicValue`
        """
        if self.mParamValue is None:
            self.mParamValue = SBSParamValue()
        aValue = self.mParamValue.getValue()
        if isinstance(aValue, SBSDynamicValue):
            self.mParamValue.mDynamicValue = None
            del aValue

        self.mParamValue.setDynamicValue(aDynamicValue)



# ==============================================================================
@doc_inherit
class SBSParamValue(sbscommon.SBSConstantValue):
    """
    Class that contains information on a parameter value as defined in a .sbs file.
    A parameter can have a constant value with a specific type, or a value defined dynamically by a function.

    Members:
        * mConstantValue (:class:`.SBSConstantValue`): simple constant definition of the parameter.
        * mDynamicValue  (:class:`.SBSDynamicValue`): dynamic definition of the parameter.
        * mTagName       (str): tag name in the .sbs file, which provides the information of the parameter type.
    """
    def __init__(self,
                 aConstantValue = None,
                 aDynamicValue  = None,
                 aTagName = ''):
        super(SBSParamValue, self).__init__(aConstantValue, aTagName)
        self.mDynamicValue  = aDynamicValue
        if aTagName == '' and self.mConstantValue is None and self.mDynamicValue is not None:
            self.mTagName = 'dynamicValue'

        self.mMembersForEquality.append('mDynamicValue')

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSParamValue, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        if 'dynamicValue' in self.mTagName:
            self.mDynamicValue = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'dynamicValue', SBSDynamicValue)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        super(SBSParamValue, self).write(aSBSWriter, aXmlNode)
        if 'dynamicValue' in self.mTagName:
            aSBSWriter.writeSBSNode(aXmlNode,  self.mDynamicValue  , 'dynamicValue'  )


    @handle_exceptions()
    def getConstantValue(self):
        """
        getConstantValue()
        Get the constant value of this param value

        :return: the constant value as a :class:`.SBSConstantValue` if it exists, None otherwise
        """
        return self.mConstantValue if self.isConstant() else None

    @handle_exceptions()
    def getDynamicValue(self):
        """
        getDynamicValue()
        Get the dynamic value of this param value

        :return: the dynamic value as a :class:`.SBSDynamicValue` if it exists, None otherwise
        """
        return self.mDynamicValue if self.isDynamic() else None

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this parameter

        :return: The parameter value, as a string if it is a constant value, or as a :class:`.SBSDynamicValue` if it is a dynamic value
        """
        if self.isConstant():   return sbscommon.SBSConstantValue.getValue(self)
        if self.isDynamic():    return self.mDynamicValue
        return None

    @handle_exceptions()
    def getTypedConstantValue(self):
        """
        getTypedConstantValue()
        Get the constant value of this parameter, typed according to the type of this parameter

        :return: The constant parameter value appropriately typed according to the parameter type, None otherwise.
        """
        return api_helpers.getTypedValueFromStr(self.getValue(), self.getType()) if self.isConstant() else None

    @handle_exceptions()
    def isConstant(self):
        """
        isConstant(self)

        :return: True if this parameter has a constant definition
        """
        return 'constantValue' in self.mTagName

    @handle_exceptions()
    def isDynamic(self):
        """
        isDynamic(self)

        :return: True if this parameter is handled by a dynamic value
        """
        return 'dynamicValue' in self.mTagName

    @handle_exceptions()
    def setConstantValue(self, aType, aValue, aInt1 = False):
        """
        setConstantValue(aType, aValue, aInt1 = False)
        Set the constant value of this param value to the given value and type.
        Remove the dynamic value if it exists.

        :param aType: type of the parameter
        :param aValue: value to set
        :param aInt1: True if the tag name must be 'Int1' instead of 'Int32' in the case of a value INTEGER1. Default to False
        :type aType: :class:`.ParamTypeEnum`
        :type aValue: str
        :type aInt1: bool
        """
        if self.mDynamicValue is not None:
            self.mDynamicValue = None
        sbscommon.SBSConstantValue.setConstantValue(self, aType, aValue, aInt1)

    @handle_exceptions()
    def setDynamicValue(self, aDynValue):
        """
        setDynamicValue(aDynValue)
        Set the dynamic value of this param value to the given value.
        Remove the constant value if it exists.

        :param aDynValue: value to set
        :type aDynValue: :class:`.SBSDynamicValue`
        """
        if self.mConstantValue is not None:
            self.mConstantValue = None
        self.mDynamicValue = aDynValue
        self.mTagName = 'dynamicValue'



# =======================================================================
@doc_inherit
class SBSParamsArrayCell(SBSObject):
    """
    Class that contains information on a paramsArrayCell as defined in a .sbs file.
    It allows to define a gradient key in a Gradient map filter.

    Members:
        * mUID        (str): unique identifier of the cell in the /paramsArrayCells/ context.
        * mParameters (list of :class:`.SBSParameter`): parameter list of the cell.
    """
    def __init__(self,
                 aUID = '',
                 aParameters = None):
        super(SBSParamsArrayCell, self).__init__()
        self.mUID           = aUID
        self.mParameters    = aParameters if aParameters is not None else []

        self.mMembersForEquality = ['mParameters']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'uid'      )
        self.mParameters = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'parameters', 'parameter', SBSParameter)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID       , 'uid'        )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mParameters, 'parameters' , 'parameter'  )



# =======================================================================
@doc_inherit
class SBSParamsArray(SBSObject):
    """
    Class that contains information on a paramsArray as defined in a .sbs file.
    It allows to define the gradient keys in a Gradient map filter.

    Members:
        * mName             (str): name (type) of the array.
        * mUID              (str): unique identifier of the array in the /paramsArray/ context.
        * mParamsArrayCells (list of :class:`.SBSParamsArrayCell`): list of cells, representing gradient keys.
    """
    def __init__(self,
                 aName  = '',
                 aUID   = '',
                 aParamsArrayCells = None):
        super(SBSParamsArray, self).__init__()
        self.mName              = aName
        self.mUID               = aUID
        self.mParamsArrayCells  = aParamsArrayCells if aParamsArrayCells is not None else []

        self.mMembersForEquality = ['mName',
                                    'mParamsArrayCells']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName             = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'name'             )
        self.mUID              = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'              )
        self.mParamsArrayCells = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paramsArrayCells' , 'paramsArrayCell', SBSParamsArrayCell)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName            , 'name'             )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID             , 'uid'              )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mParamsArrayCells, 'paramsArrayCells' , 'paramsArrayCell')

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Parse the ParamsArrayCell list to find a :class:`.SBSParamsArrayCell` with the given uid

        :param aUID: UID to check
        :type aUID: str
        :return: True if this uid is already used, False otherwise
        """
        if self.mParamsArrayCells:
            return next((aCell for aCell in self.mParamsArrayCells if aCell.mUID == aUID), None) is not None
        return False
