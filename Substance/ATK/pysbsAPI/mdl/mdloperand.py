# coding: utf-8
"""
Module **mdloperand** provides the definition of the classes related to the operand structure as in .sbs format:

- :class:`.MDLOperand`
- :class:`.MDLOperandValue`
- :class:`.MDLOperandStruct`
- :class:`.MDLOperandArray`
- :class:`.MDLOperands`
- :class:`.MDLOperandMetaData`
"""

from __future__ import unicode_literals
import abc
import random
import re
import string

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject
from pysbs import api_helpers
from pysbs.sbsenum import ParamTypeEnum

from . import mdl_helpers
from . import mdlenum
from . import mdldictionaries as mdldict

# =======================================================================
@doc_inherit
class MDLOperandMetaData(SBSObject):
    """
    Class MDLOperandMetaData contains additional information associated to operands.

    Members:
        * mAcceptConnection  (string, optional): defines if the connections are allowed on this operand. Default to False
        * mIsDefaultValue    (string, optional): defines if the operand has the default value. Default to False
    """
    def __init__(self,
                 aAcceptConnection = None,
                 aIsDefaultValue = None):
        super(MDLOperandMetaData, self).__init__()
        self.mAcceptConnection = aAcceptConnection
        self.mIsDefaultValue = aIsDefaultValue

        self.mMembersForEquality = ['mAcceptConnection',
                                    'mIsDefaultValue']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mAcceptConnection = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'accept_connection' )
        self.mIsDefaultValue = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'is_default_value' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mAcceptConnection, 'accept_connection' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIsDefaultValue, 'is_default_value' )

    def acceptConnection(self):
        """
        acceptConnection()
        Check if this operand accepts a connection (a pin is visible and active for this parameter)

        :return: True if the operand accepts connection, False otherwise
        """
        return api_helpers.getTypedValueFromStr(self.mAcceptConnection, ParamTypeEnum.BOOLEAN) if self.mAcceptConnection else False

    def isDefaultValue(self):
        """
        isDefaultValue()
        Check if the value of this operand is the default one

        :return: True if the value of the operand is the default one, False otherwise
        """
        return api_helpers.getTypedValueFromStr(self.mIsDefaultValue, ParamTypeEnum.BOOLEAN) if self.mIsDefaultValue else False

    def isEmpty(self):
        """
        isEmpty()
        Check if the content of the metadata is empty

        :return: True if there is no metadata, False otherwise
        """
        return self.mAcceptConnection is None and self.mIsDefaultValue is None

    def setConnectionAccepted(self, aValue):
        """
        setConnectionAccepted(aValue)
        Defines if the connection are accepted or not

        :param aValue: The value to set.
        :type aValue: bool
        """
        if aValue is False:
            self.mAcceptConnection = None
        else:
            self.mAcceptConnection = api_helpers.formatValueForTypeStr(aValue, ParamTypeEnum.BOOLEAN)

    def setIsDefaultValue(self, isDefaultValue):
        """
        setIsDefaultValue(isDefaultValue)
        Defines if the operand is the default value or not

        :param isDefaultValue: The value to set.
        :type isDefaultValue: bool
        """
        if isDefaultValue is False:
            self.mIsDefaultValue = None
        else:
            self.mIsDefaultValue = api_helpers.formatValueForTypeStr(isDefaultValue, ParamTypeEnum.BOOLEAN)


# =======================================================================
@doc_inherit
class MDLOperand(SBSObject):
    """
    Base class for:

    - :class:`.MDLOperandValue`
    - :class:`.MDLOperandStruct`
    - :class:`.MDLOperandArray`

    Members:
        * mName     (string): name of the operand
        * mType     (string): type of the operand (its type's MDL path)
        * mMetaData (:class:`.MDLOperandMetaData`, optional): various meta-data
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 aName     = '',
                 aType     = '',
                 aMetaData = None):
        super(MDLOperand, self).__init__()
        self.mName     = aName
        self.mType     = aType
        self.mMetaData = aMetaData

        self.mMembersForEquality = ['mName',
                                    'mType',
                                    'mMetaData']

    def acceptConnection(self):
        """
        acceptConnection()
        Check if this operand accepts a connection (a pin is visible and active for this parameter)

        :return: True if the operand accepts connection, False otherwise
        """
        return self.mMetaData is not None and self.mMetaData.acceptConnection()

    def getType(self):
        """
        getType()
        Get the type of the operand

        :return: The operand type as a string
        """
        return self.mType

    def isDefaultValue(self):
        """
        isDefaultValue()
        Check if the value of this operand is the default one

        :return: True if the value of the operand is the default one, False otherwise
        """
        return self.mMetaData is not None and self.mMetaData.isDefaultValue()

    @staticmethod
    @abc.abstractmethod
    def getSBSTag():
        pass

    @abc.abstractmethod
    def getValue(self):
        """
        getValue()
        Get the value of the operand

        :return: The operand value, as a string or a :class:`.MDLOperands` object
        """
        pass

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName     = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name' )
        self.mType     = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'type' )
        self.mMetaData = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_operand_meta_data', MDLOperandMetaData)

    def setConnectionAccepted(self, aValue):
        """
        setConnectionAccepted(aValue)
        Defines if the connection are accepted or not

        :param aValue: The value to set.
        :type aValue: bool
        """
        if aValue:
            if self.mMetaData is None:
                self.mMetaData = MDLOperandMetaData()
            self.mMetaData.setConnectionAccepted(True)
        elif self.mMetaData:
            self.mMetaData.setConnectionAccepted(False)
            if self.mMetaData.isEmpty():
                self.mMetaData = None

    def setIsDefaultValue(self, isDefaultValue):
        """
        setIsDefaultValue(isDefaultValue)
        Defines if the operand has the default value or not

        :param isDefaultValue: The value to set.
        :type isDefaultValue: bool
        """
        if isDefaultValue:
            if self.mMetaData is None:
                self.mMetaData = MDLOperandMetaData()
            self.mMetaData.setIsDefaultValue(True)
        elif self.mMetaData:
            self.mMetaData.setIsDefaultValue(False)
            if self.mMetaData.isEmpty():
                self.mMetaData = None


# =======================================================================
@doc_inherit
class MDLOperandValue(MDLOperand):
    """
    Class MDLOperandValue: A simple base-type operand.

    Members:
        * mName     (string): name of the operand
        * mType     (string): type of the operand (its type's MDL path)
        * mValue    (string): value of the operand
        * mMetaData (:class:`.MDLOperandMetaData`, optional): various meta-data
    """
    __sSBSTag = 'mdloperandvalue'

    def __init__(self,
                 aName     = '',
                 aType     = '',
                 aValue    = '',
                 aMetaData = None):

        SBSObject.__init__(self)
        MDLOperand.__init__(self, aName = aName,
                                  aType = aType,
                                  aMetaData = aMetaData)
        self.mValue = aValue

    def equals(self, other):
        # Compare the typed value instead of strings to avoid mismatch with number of decimals
        selfValue = self.getTypedValue()
        otherValue = other.getTypedValue()

        # Remove the unique part of a mdl::call value
        if self.mType == mdldict.getMDLPredefTypePath(mdlenum.MDLPredefTypes.CALL):
            selfValue = selfValue[0:selfValue.rfind('_')] if selfValue else ''
            otherValue = otherValue[0:otherValue.rfind('_')] if otherValue else ''

        # Call function __areEqual on parent SBSObject to properly compare the operand value
        return SBSObject._SBSObject__areEqual(selfValue, otherValue) and SBSObject.equals(self, other)


    @staticmethod
    def getSBSTag():
        return MDLOperandValue.__sSBSTag

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this operand

        :return: The value of the operand, as a string
        """
        return self.mValue

    @handle_exceptions()
    def getTypedValue(self):
        """
        getTypedValue()
        Get the value of this operand, in the type of the operand

        :return: The value of the operand, in the type of the operand
        """
        from . import MDLManager

        aTypeDef = MDLManager.getMDLTypeDefinition(self.mType)
        if aTypeDef:
            return mdl_helpers.getTypedValueFromMdlStr(aValue=self.mValue, aTypeDef=aTypeDef)
        return self.mValue

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        MDLOperand.parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mValue = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'value' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName,  'name'                   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType,  'type'                   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mValue, 'value'                  )
        aSBSWriter.writeSBSNode(aXmlNode, self.mMetaData,          'mdl_operand_meta_data'   )

    @handle_exceptions()
    def setValue(self, aValue):
        """
        setValue(aValue)
        Set the value of this operand

        :param aValue: the value to set
        :type aValue: any type
        """
        from . import MDLManager

        aTypeDef = MDLManager.getMDLTypeDefinition(self.mType)
        if aTypeDef:
            self.mValue = mdl_helpers.formatValueForMdlTypeStr(aValue=aValue, aTypeDef=aTypeDef)



# =======================================================================
@doc_inherit
class MDLOperandStruct(MDLOperand):
    """
    Class MDLOperandStruct: A compound type (struct) operand.

    Members:
        * mName     (string): name of the operand
        * mType     (string): type of the operand (its type's MDL path)
        * mMembers  (:class:`.MDLOperands`): the sub-operands
        * mMetaData (:class:`.MDLOperandMetaData`, optional): various meta-data
    """
    __sSBSTag = 'mdloperandstruct'

    def __init__(self,
                 aName     = '',
                 aType     = '',
                 aMembers  = None,
                 aMetaData = None):

        SBSObject.__init__(self)
        MDLOperand.__init__(self, aName = aName,
                                  aType = aType,
                                  aMetaData = aMetaData)
        self.mMembers = aMembers
        self.mMembersForEquality.append('mMembers')

    @staticmethod
    def getSBSTag():
        return MDLOperandStruct.__sSBSTag

    def getMembers(self):
        """
        getMembers()
        Get the list of members on this operand struct

        :return: The members as a list of :class:`.MDLOperand`
        """
        return self.mMembers.mOperands if self.mMembers else []

    @handle_exceptions()
    def getOperand(self, aOperandName):
        """
        getOperand(aOperandName)
        Get the operand with the given name among the structure members.
        The name can be:
        - Simply the name of the operand to get
        - A set of names separated by '/' to access a sub member of the root member, for instance 'surface/intensity'
        - A name with an operator [] to access a particular item of an operand array, for instance 'color[2]'

        :param aOperandName: The name of the operand to search
        :type aOperandName: str
        :return: The operand as a :class:`.MDLOperand` if found, None otherwise
        """
        return self.mMembers.getOperand(aOperandName)

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this operand

        :return: The value of the operand, as a :class:`.MDLOperands`
        """
        return self.mMembers

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        MDLOperand.parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mMembers = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'members', MDLOperands)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName, 'name'                   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType, 'type'                   )
        aSBSWriter.writeSBSNode(aXmlNode, self.mMembers,           'members'                )
        aSBSWriter.writeSBSNode(aXmlNode, self.mMetaData,          'mdl_operand_meta_data'  )

    @handle_exceptions()
    def setValue(self, aValue):
        """
        setValue(aValue)
        Set the value of this operand

        :param aValue: the value to set
        :type aValue: :class:`.MDLOperandStruct`
        """
        for aOperand in self.mMembers.mOperands:
            aOpToCopy = aValue.getOperand(aOperand.mName)
            if aOpToCopy:
                aOperand.setValue(aOpToCopy.getValue())



# =======================================================================
@doc_inherit
class MDLOperandArray(MDLOperand):
    """
    Class MDLOperandArray: An array operand

    Members:
        * mName     (string): name of the operand
        * mType     (string): type of the operand (its type's MDL path)
        * mItems    (:class:`.MDLOperands`): the list of operands
        * mMetaData (:class:`.MDLOperandMetaData`, optional): various meta-data
    """
    __sSBSTag = 'mdloperandarray'

    def __init__(self,
                 aName   = '',
                 aType   = '',
                 aItems  = None,
                 aMetaData = None):

        SBSObject.__init__(self)
        MDLOperand.__init__(self, aName = aName,
                                  aType = aType,
                                  aMetaData = aMetaData)
        self.mItems = aItems
        self.mMembersForEquality.append('mItems')

    @staticmethod
    def getSBSTag():
        return MDLOperandArray.__sSBSTag

    def addItem(self, aValue, aIndex = -1):
        """
        addItem(aValue, aIndex = -1)
        Add an item with the given value to the array, at the given index if it is provided, or at the end.

        :param aValue: The value to add
        :param aIndex: The index where to add the item. At the end by default
        :type aValue: any type
        :type aIndex: int, optional
        :return: The added item as a :class:`.MDLOperand`
        :raise: :class:`.SBSImpossibleActionError`
        """
        def generateUniqueName(n):
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

        from . import MDLManager

        if self.mItems is None:
            self.mItems = MDLOperands()
        itemLen = self.getSize()
        aIndex = itemLen if aIndex == -1 else aIndex
        if aIndex < 0 or aIndex > self.getSize():
            raise SBSImpossibleActionError('This array contains '+str(itemLen)+' values, cannot add an item at the index '+str(aIndex))

        typeDef = MDLManager.getMDLTypeDefinition(self.mType)
        itemTypeDef = MDLManager.getMDLTypeDefinition(typeDef.mComponentType)
        aOperand = itemTypeDef.toMDLOperand(aName=generateUniqueName(9))
        aOperand.setValue(aValue)
        self.mItems.mOperands.insert(aIndex, aOperand)
        return aOperand

    def getItem(self, aIndex):
        """
        getItem(aIndex)
        Get the item at the given index

        :param aIndex: the index of the item to get
        :type aIndex: positive integer
        :return: The :class:`.MDLOperand` at the given index if it possible, None otherwise
        """
        return self.mItems.getOperandByIndex(aIndex) if self.mItems else None

    def getItems(self):
        """
        getItems()
        Get the array of items on this operand array

        :return: The items as a list of :class:`.MDLOperand`
        """
        return self.mItems.mOperands if self.mItems else []

    def getSize(self):
        """
        getSize()
        Get the size of the array

        :return: The array size as a positive integer
        """
        return len(self.getItems())

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this operand

        :return: The value of the operand, as a :class:`.MDLOperands`
        """
        return self.getItems()

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        MDLOperand.parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mItems = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'items', MDLOperands)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName, 'name'                   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType, 'type'                   )
        aSBSWriter.writeSBSNode(aXmlNode, self.mItems,             'items'                  )
        aSBSWriter.writeSBSNode(aXmlNode, self.mMetaData,          'mdl_operand_meta_data'  )

    @handle_exceptions()
    def setValue(self, aValue):
        """
        setValue(aValue)
        Set the value of this operand

        :param aValue: the value to set
        :type aValue: :class:`.MDLOperandArray`
        """
        self.mItems = MDLOperands()
        if aValue is None:
            return
        aList = aValue.getItems() if isinstance(aValue, MDLOperandArray) else aValue
        if not isinstance(aList, list):
            raise SBSImpossibleActionError('To set the value of a MDLOperandArray, provide a list of MDLOperand or another MDLOperandArray')

        for item in aList:
            self.addItem(item.getValue())


# =======================================================================
@doc_inherit
class MDLOperands(SBSObject):
    """
    Class that contains information on the MDL operands as defined in a .sbs file.
    A MDLOperands provides the list of parameters of a MDLNode or of a MDLAnnotation, and is constituted of a list of:
    - :class:`.MDLOperandValue`
    - :class:`.MDLOperandStruct`
    - :class:`.MDLOperandArray`

    Members:
        * mOperands (list of :class:`.MDLOperand`, optional): list of parameters available on this node
    """
    def __init__(self,
                 aOperands = None):
        super(MDLOperands, self).__init__()
        self.mOperands = aOperands or []

        self.mMembersForEquality = ['mOperands']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mOperands = []
        aChildren = list(aXmlNode)
        if not aChildren:
            return

        for aElt in aChildren:
            aClass = None
            if   aElt.tag == MDLOperandValue.getSBSTag():       aClass = MDLOperandValue
            elif aElt.tag == MDLOperandStruct.getSBSTag():      aClass = MDLOperandStruct
            elif aElt.tag == MDLOperandArray.getSBSTag():       aClass = MDLOperandArray
            if aClass:
                self.mOperands.append(aSBSParser.parseSBSNodeFromXmlNode(aContext, aDirAbsPath, aElt, aClass))

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        for aOperand in self.mOperands:
            aSBSWriter.writeSBSNode(aXmlNode, aOperand, aOperand.getSBSTag())

    @handle_exceptions()
    def getOperand(self, aOperandName):
        """
        getOperand(aOperandName)
        Get the operand with the given name.
        The name can be:
        - Simply the name of the operand to get
        - A set of names separated by '/' to access a sub member of the root member, for instance 'surface/intensity'
        - A name with an operator [] to access a particular item of an operand array, for instance 'color[2]'

        :param aOperandName: The name of the operand to search
        :type aOperandName: str
        :return: The operand as a :class:`.MDLOperand` if found, None otherwise
        """
        # Split the name to handle the case of a submember of a struct
        names = aOperandName.split('/')
        if not names:
            return None
        aName = names.pop(0)

        # Search for an operator [] in the first member to get
        match = re.search('\[[0-9]+\]$', aName)
        eltId = -1
        checkWithHooks = False
        if match:
            eltId = int(aName[match.start()+1:match.end()-1])
            aName = aName[:match.start()]
            checkWithHooks = True

        # Look for the first member to get
        aOperand = None
        if checkWithHooks:
            aOperand = next((aOperand for aOperand in self.mOperands if aOperand.mName == aName+'[]'), None)
        if aOperand is None:
            aOperand = next((aOperand for aOperand in self.mOperands if aOperand.mName == aName), None)

        if eltId != -1 and isinstance(aOperand, MDLOperandArray):
            aOperand = aOperand.getItem(eltId)
        if aOperand is None or not names or not isinstance(aOperand, MDLOperandStruct):
            return aOperand
        return aOperand.mMembers.getOperand('/'.join(names))

    @handle_exceptions()
    def getOperandByIndex(self, aIndex):
        """
        getOperandByIndex(aIndex)
        Get the operand at the given index

        :param aIndex: The index of the operand to get
        :param aIndex: positive integer
        :return: The operand as a :class:`.MDLOperand` if possible, None otherwise
        """
        return self.mOperands[aIndex] if aIndex < len(self.mOperands) else None

    @handle_exceptions()
    def getOperandValue(self, aOperandName):
        """
        getOperandValue(aOperandName)
        Get the value of the operand with the given name.

        :param aOperandName: The name of the operand to search
        :param aOperandName: str
        :return: The operand value as a string (for a MDLOperandValue) or a list of :class:`.MDLOperand` (for a MDLOperandStruct or a MDLOperandArray) if found, None otherwise
        """
        aOperand = self.getOperand(aOperandName)
        return aOperand.getValue() if aOperand else None

    @handle_exceptions()
    def getOperandValueByIndex(self, aIndex):
        """
        getOperandValueByIndex(aIndex)
        Get the value of the operand at the given index

        :param aIndex: The index of the operand to get
        :param aIndex: positive integer
        :return: The operand value as a string (for a MDLOperandValue) or a list of :class:`.MDLOperand` (for a MDLOperandStruct or a MDLOperandArray) if possible, None otherwise
        """
        aOperand = self.getOperandByIndex(aIndex)
        return aOperand.getValue() if aOperand else None

    @handle_exceptions()
    def getAllOperands(self):
        """
        getAllOperands()
        Get the all the operands.

        :return: A list of :class:`.MDLOperand`
        """
        return self.mOperands if self.mOperands is not None else []

    @handle_exceptions()
    def getAllOperandsValue(self):
        """
        getAllOperandsValue()
        Get all the operand values

        :return: A list of string and MDLOperand objects
        """
        if not self.mOperands:
            return []
        return [aOperand.getValue() for aOperand in self.mOperands]

    @handle_exceptions()
    def getNbOperands(self):
        """
        getNbOperands()

        :return: The number of operands
        """
        return len(self.mOperands) if self.mOperands else 0

    @handle_exceptions()
    def equalsTo(self, other):
        """
        equalsTo(other)
        Allows to check if two MDLOperands are identical.

        :param other: the MDLOperands to compare with
        :type other: :class:`.MDLOperands`
        :return: True if the two MDLOperands has the same parameters, False otherwise
        """
        if len(self.mOperands) != len(other.mOperands):
            return False
        for aOperand in self.mOperands:
            aOperandOther = next((oper for oper in other.mOperands if oper.mName == aOperand.mName), None)
            if aOperandOther is None:
                return False
            if aOperand.getType() != aOperandOther.getType():
                return False
            if aOperand.getValue() != aOperandOther.getValue():
                return False
        return True
