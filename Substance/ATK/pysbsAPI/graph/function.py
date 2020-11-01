# coding: utf-8
"""
Module **function** provides the definition of the class :class:`.SBSFunction`: which allows to define a function graph.
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject, UIDGenerator
from pysbs import api_helpers
from pysbs import sbsenum
from pysbs import sbscommon
from pysbs import params
from pysbs import sbsgenerator

from .inputparameters import SBSParamInput


#=======================================================================
@doc_inherit
class SBSFunction(SBSObject):
    """
    Class that contains information on a function as defined in a .sbs file

    Members:
        * mIdentifier  (str): name of the function definition.
        * mUID         (str): unique identifier in the package/ context.
        * mAttributes  (:class:`.SBSAttributes`): various attributes
        * mParamInputs (list of :class:`.SBSParamInput`, optional): list of parameters inputs of the function.
        * mType        (str): type of the function return.
        * mParamValue  (:class:`.SBSParamValue`): definition of the function.
    """
    __sAttributes = [sbsenum.AttributesEnum.Author          ,
                     sbsenum.AttributesEnum.AuthorURL       ,
                     sbsenum.AttributesEnum.Category        ,
                     sbsenum.AttributesEnum.Description     ,
                     sbsenum.AttributesEnum.HideInLibrary   ,
                     sbsenum.AttributesEnum.Icon            ,
                     sbsenum.AttributesEnum.Label           ,
                     sbsenum.AttributesEnum.Tags            ,
                     sbsenum.AttributesEnum.UserTags        ]

    def __init__(self,
                 aIdentifier    = '',
                 aUID           = '',
                 aAttributes    = None,
                 aParamInputs   = None,
                 aType          = '',
                 aParamValue    = None):
        super(SBSFunction, self).__init__()
        self.mIdentifier    = aIdentifier
        self.mUID           = aUID
        self.mAttributes    = aAttributes
        self.mParamInputs   = aParamInputs
        self.mType          = aType
        self.mParamValue    = aParamValue

        self.mMembersForEquality = ['mIdentifier',
                                    'mAttributes',
                                    'mParamInputs',
                                    'mType',
                                    'mParamValue']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier  = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'identifier' )
        self.mUID         = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'        )
        self.mAttributes  = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'attributes' , sbscommon.SBSAttributes)
        self.mParamInputs = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paraminputs', 'paraminput', SBSParamInput)
        self.mType        = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'type'       )
        self.mParamValue  = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'paramValue' , params.SBSParamValue)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIdentifier , 'identifier'     )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUID        , 'uid'            )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mAttributes , 'attributes'     )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mParamInputs, 'paraminputs',   'paraminput'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mType       , 'type',          )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mParamValue , 'paramValue'     )

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Check if the given uid is already used in the context of the function

        :param aUID: UID ti check
        :type aUID: str
        :return: True if the uid is already used, False otherwise
        """
        if self.mParamInputs:
            return next((param for param in self.mParamInputs if param.mUID == aUID), None) is not None
        return False

    def initFunction(self):
        """
        initFunction()
        Init the function with default value
        """
        if self.mParamInputs is None:
            self.mParamInputs = []
        if not self.mType:
            self.mType = str(sbsenum.ParamTypeEnum.VOID_TYPE)
        if self.mParamValue is None:
            self.mParamValue = params.SBSParamValue(aDynamicValue = params.SBSDynamicValue())

    @handle_exceptions()
    def contains(self, aNode):
        """
        contains(aNode)
        Check if the given node belongs to this function graph

        :param aNode: The node to check, as a, object or an UID
        :type aNode: :class:`.SBSParamNode` or str
        :return: True if the given node belongs to the node list, False otherwise
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.contains(aNode) if aDynamicValue is not None else False

    @handle_exceptions()
    def getDynamicValue(self):
        """
        getDynamicValue()
        Get the function definition

        :return: The :class:`.SBSDynamicValue` object that defines this function
        """
        if self.mParamValue is not None and self.mParamValue.mDynamicValue is not None:
            return self.mParamValue.mDynamicValue
        return None

    @handle_exceptions()
    def getNode(self, aNode):
        """
        getNode(aNode)
        Search for the given function node in the node list

        :param aNode: node to get, identified by its uid or as a :class:`.SBSParamNode`
        :type aNode: :class:`.SBSParamNode` or str
        :return: A :class:`.SBSParamNode` object if found, None otherwise
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getNode(aNode) if aDynamicValue is not None else None

    @handle_exceptions()
    def getNodeList(self, aNodesList = None):
        """
        getNodeList(aNodesList = None)
        Get all the function nodes of this function, or look for the given nodes if aNodesList is not None

        :param aNodesList: list of node to look for
        :type aNodesList: list of str or list of :class:`.SBSParamNode`, optional
        :return: a list of :class:`.SBSParamNode` included in the function graph
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getNodeList(aNodesList) if aDynamicValue is not None else []

    @handle_exceptions()
    def getConnectionsFromNode(self, aLeftNode):
        """
        getConnectionsFromNode(self, aLeftNode)
        Get the connections starting from the output of the given left node.

        :param aLeftNode: the node to consider, as a SBSParamNode or given its uid
        :type aLeftNode: :class:`.SBSParamNode` or str
        :return: a list of :class:`.SBSConnection`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getConnectionsFromNode(aLeftNode) if aDynamicValue is not None else []

    @handle_exceptions()
    def getConnectionsToNode(self, aRightNode, aRightNodeInput=None):
        """
        getConnectionsToNode(self, aRightNode, aRightNodeInput=None)
        Get the connections incoming to the given right node, to a particular input or for all its inputs.

        :param aRightNode: the node to consider, as a SBSParamNode or given its uid
        :param aRightNodeInput: the pin input identifier to consider. If let None, all the inputs will be considered
        :type aRightNode: :class:`.SBSParamNode` or str
        :type aRightNodeInput: :class:`.FunctionInputEnum` or str, optional
        :return: a list of :class:`.SBSConnection`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getConnectionsToNode(aRightNode, aRightNodeInput) if aDynamicValue is not None else []

    @handle_exceptions()
    def getNodesConnectedFrom(self, aLeftNode):
        """
        getNodesConnectedFrom(aLeftNode)
        Get all the nodes connected to the output of the given node.

        :param aLeftNode: the node to consider
        :type aLeftNode: :class:`.SBSParamNode` or str
        :return: a list of :class:`.SBSParamNode`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getNodesConnectedFrom(aLeftNode) if aDynamicValue is not None else []

    @handle_exceptions()
    def getNodesConnectedTo(self, aRightNode, aRightNodeInput=None):
        """
        getNodesConnectedTo(aRightNode, aRightNodeInput=None)
        Get all the nodes connected to the given input of the given node.
        If aInputIdentifier is let None, consider all the inputs of the node.

        :param aRightNode: the node to consider, as an object or given its uid
        :param aRightNodeInput: the input to take in account
        :type aRightNode: :class:`.SBSParamNode` or str
        :type aRightNodeInput: :class:`.FunctionInputEnum` or str, optional
        :return: a list of :class:`.SBSParamNode`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getNodesConnectedTo(aRightNode, aRightNodeInput) if aDynamicValue is not None else []

    @handle_exceptions()
    def getNodesDockedTo(self, aNode):
        """
        getNodesDockedTo(aNode)
        Get all the nodes that are docked to the given node.

        :param aNode: the node to consider
        :type aNode: :class:`.SBSParamNode`
        :return: a list of :class:`.SBSParamNode` corresponding to the nodes that are docked to the given node.
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getNodesDockedTo(aNode) if aDynamicValue is not None else []

    @handle_exceptions()
    def getNodeAssociatedToComment(self, aComment):
        """
        getNodeAssociatedToComment(aComment)
        Get the node associated to the given comment.

        :param aComment: The comment to consider
        :type aComment: :class:`.SBSGUIObject`
        :return: the :class:`.SBSParamNode` if found, None otherwise
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getNodeAssociatedToComment(aComment) if aDynamicValue is not None else []

    @handle_exceptions()
    def getNodesInFrame(self, aFrame):
        """
        getNodesInFrame(aFrame)
        Get all the nodes included or partially included in the given frame.
        The frame must be included in this function, otherwise SBSImpossibleActionError is raised

        :param aFrame: The frame to consider
        :type aFrame: :class:`.SBSGUIObject`
        :return: a list of :class:`.SBSParamNode`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getNodesInFrame(aFrame) if aDynamicValue is not None else []

    @handle_exceptions()
    def getRect(self, aNodeList = None):
        """
        getRect(aNodeList = None)
        Get the rectangle occupied by all the nodes of this function graph, or use only the given nodes if aNodeList is not None

        :param aNodeList: The list of node to take in account for the GUI rectangle. None to consider the node list pointed by itself.
        :type aNodeList: list of str or list of :class:`.SBSParamNode`, optional
        :return: A :class:`.Rect`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getRect(aNodeList) if aDynamicValue is not None else None

    @handle_exceptions()
    def getAllComments(self):
        """
        getAllComments()
        Get all comments defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getAllComments() if aDynamicValue is not None else []

    @handle_exceptions()
    def getAllFrames(self):
        """
        getAllFrames()
        Get all frames defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getAllFrames() if aDynamicValue is not None else []

    @handle_exceptions()
    def getAllNavigationPins(self):
        """
        getAllNavigationPins()
        Get all the navigation pins defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getAllNavigationPins() if aDynamicValue is not None else []

    @handle_exceptions()
    def getAllGUIObjects(self):
        """
        getAllGUIObjects()
        Get all the GUI objects defined in the graph (Comments, Frames, Navigation Pins)

        :return: a list of :class:`.SBSGUIObject`
        """
        aDynamicValue = self.getDynamicValue()
        return aDynamicValue.getAllGUIObjects() if aDynamicValue is not None else []

    @handle_exceptions()
    def getAllFunctionsOfKind(self, aFunction):
        """
        getAllFunctionsOfKind(aFunction)
        Search for all SBSParamNode which represents the given filter kind.

        :param aFunction: kind of filters to look for
        :type aFunction: :class:`.FunctionEnum` str
        :return: a list of :class:`.SBSParamNode` containing all functions of the given kind.
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to get nodes, the function is not initialized')

        return aDynamicValue.getAllFunctionsOfKind(aFunction = aFunction)

    @handle_exceptions()
    def getAllNodeInstancesOf(self, aSBSDocument, aPath):
        """
        getAllNodeInstancesOf(aSBSDocument, aPath)
        Search for all SBSParamNode of kind 'instance', which reference the given function path.

        :param aSBSDocument: current SBSDocument
        :param aPath: path of the function definition (absolute, relative to the current .sbs file, or given with an alias, for instance *sbs://functions.sbs/Functions/Math/Pi*)

            - If the function is included in the current package, use: *pkg:///MyFunctionIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyFunctionIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyFunctionIdentifier*
            - Note that if the function identifier is equivalent to the filename, the part */MyFunctionIdentifier* may be omit.
        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :return: a list of :class:`.SBSParamNode` containing all instance nodes of the given function.
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to get nodes, the function is not initialized')

        return aDynamicValue.getAllNodeInstancesOf(aSBSDocument = aSBSDocument, aPath = aPath)

    @handle_exceptions()
    def getAllReferencesOnDependency(self, aDependency):
        """
        getAllReferencesOnDependency(aDependency)
        Get all the SBSParamNode that are referencing the given dependency

        :param aDependency: The dependency to look for (UID or object)
        :type aDependency: str or :class:`.SBSDependency`
        :return: A list of :class:`.SBSParamNode`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to get nodes, the function is not initialized')

        return aDynamicValue.getAllReferencesOnDependency(aDependency = aDependency)

    @handle_exceptions()
    def getAllDependencyUID(self):
        """
        getAllDependencyUID()
        Get the UIDs of the dependencies used by this graph

        :return: a list of UIDs as strings
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to get nodes, the function is not initialized')

        return aDynamicValue.getAllDependencyUID()

    @handle_exceptions()
    def getCommentsAssociatedToNode(self, aNode):
        """
        getCommentsAssociatedToNode(aNode)
        Get the list of comments associated to the given node

        :param aNode: The node to consider, as a SBSParamNode or given its UID
        :type aNode: :class:`.SBSParamNode` or str
        :return: a list of :class:`.SBSGUIObject`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to get nodes, the function is not initialized')

        return aDynamicValue.getCommentsAssociatedToNode(aNode)

    @handle_exceptions()
    def getOutputType(self):
        """
        getOutputType()
        Get the output type of the function.
        The output type can be VOID_TYPE or FUNCTION_ALL if the output node is not set.

        :return: The output type, as a :class:`.ParamTypeEnum`.
        """
        return int(self.mType) if self.mType else sbsenum.ParamTypeEnum.VOID_TYPE

    @handle_exceptions()
    def getOutputNode(self):
        """
        getOutputNode()
        Get the output node of the function.

        :return: The :class:`.SBSParamNode` object corresponding to the output node if defined, None otherwise.
        """
        aDynValue = self.getDynamicValue()
        return aDynValue.getOutputNode() if aDynValue is not None else None

    def getInputParameters(self):
        """
        Get the list of inputs parameters

        :return: a list of :class:`.SBSParamInput`
        """
        return self.mParamInputs if self.mParamInputs is not None else []

    @handle_exceptions()
    def getInputParameter(self, aInputParamIdentifier):
        """
        getInputParameter(aInputParamIdentifier)
        Get the SBSParamInput definition associated to the given identifier

        :param aInputParamIdentifier: input parameter identifier
        :type aInputParamIdentifier: str
        :return: the corresponding :class:`.SBSParamInput` object if found, None otherwise
        """
        return next((param for param in self.getInputParameters() if param.mIdentifier == aInputParamIdentifier), None)

    @handle_exceptions()
    def addInputParameter(self,
                          aIdentifier,
                          aWidget,
                          aOptions = None,
                          aDescription = None,
                          aLabel = None,
                          aGroup = None,
                          aUserData = None,
                          aVisibleIf = None):
        """
        addInputParameter(aIdentifier, aWidget, aOptions = None, aDescription = None, aLabel = None, aGroup = None, aUserData = None, aVisibleIf = None)
        Create a :class:`.SBSParamInput` with the given parameters and add it to the ParamsInput of the function.

        :param aIdentifier: identifier of the input parameter. It may change to ensure having a unique identifier.
        :param aWidget: widget to use for this parameter
        :param aOptions: options
        :param aDescription: textual description
        :param aLabel: GUI label for this input parameter
        :param aGroup: string that contains a group name. Can uses path with '/' separators.
        :param aUserData: user tags
        :param aVisibleIf: string bool expression based on graph inputs values
        :type aIdentifier: str
        :type aWidget: :class:`.WidgetEnum`
        :type aOptions: dictionary in the format {:class:`.WidgetOptionEnum`: value(str)}, optional
        :type aDescription: str, optional
        :type aLabel: str, optional
        :type aGroup: str, optional
        :type aUserData: str, optional
        :type aVisibleIf: str, optional

        :return: The created :class:`.SBSParamInput` object, or None if this input parameter is already defined
        """
        if aOptions is None: aOptions = {}

        aUID = UIDGenerator.generateUID(self)
        uniqueIdentifier = self.computeUniqueInputIdentifier(api_helpers.formatIdentifier(aIdentifier))
        aParamInput = sbsgenerator.createInputParameter(aUID = aUID,
                                                        aIdentifier = uniqueIdentifier,
                                                        aWidget = aWidget,
                                                        aDefaultValue = None,
                                                        aOptions = aOptions,
                                                        aDescription = aDescription,
                                                        aLabel = aLabel,
                                                        aGroup = aGroup,
                                                        aUserData = aUserData,
                                                        aVisibleIf = aVisibleIf)
        if aParamInput is not None:
            api_helpers.addObjectToList(self, 'mParamInputs', aParamInput)
        return aParamInput

    @handle_exceptions()
    def computeUniqueInputIdentifier(self, aIdentifier, aSuffixId = 0):
        """
        computeUniqueInputIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used in the function inputs and generate a unique identifier if necessary

        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier_id
        """
        return self._computeUniqueIdentifier(aIdentifier, aListsToCheck= [self.mParamInputs], aSuffixId= aSuffixId)

    @handle_exceptions()
    def connectNodes(self, aLeftNode, aRightNode, aRightNodeInput = sbsenum.FunctionInputEnum.VALUE):
        """
        connectNodes(aLeftNode, aRightNode, aRightNodeInput = sbsenum.FunctionInputEnum.VALUE)
        Connect the given nodes together: aLeftNode -> aRightNode(on the input aRightNodeInputIdentifier)

        :param aLeftNode: Node to connect from, as a SBSParamNode or given its UID
        :param aRightNode: Node to connect to, as a SBSParamNode or given its UID
        :param aRightNodeInput: Identifier of the input of the right node

        :type aLeftNode: :class:`.SBSParamNode` or str
        :type aRightNode: :class:`.SBSParamNode` or str
        :type aRightNodeInput: :class:`.FunctionInputEnum` or str, optional
        :return: The connection if success, None otherwise (in case of type incompatibility for instance)
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to connect '+str(aLeftNode)+' to '+str(aRightNode)+', the function is not initialized')

        return aDynamicValue.connectNodes(aLeftNode = aLeftNode,
                                          aRightNode = aRightNode,
                                          aRightNodeInput = aRightNodeInput)


    @handle_exceptions()
    def disconnectNodes(self, aLeftNode, aRightNode, aRightNodeInput = None):
        """
        disconnectNodes(self, aLeftNode, aRightNode, aRightNodeInput = None)
        Disconnect the given nodes: aLeftNode -> aRightNode(on the input aRightNodeInputIdentifier).
        If the right node input is None, all connections will be removed.

        :param aLeftNode: Left node, as a SBSParamNode or given its UID
        :param aRightNode: Right node, as a SBSParamNode or given its UID
        :param aRightNodeInput: Identifier of the input of the right node

        :type aLeftNode: :class:`.SBSParamNode` or str
        :type aRightNode: :class:`.SBSParamNode` or str
        :type aRightNodeInput: :class:`.FunctionInputEnum` or str, optional
        :return: Nothing
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to disconnect '+str(aLeftNode)+' to '+str(aRightNode)+', the function is not initialized')

        return aDynamicValue.disconnectNodes(aLeftNode = aLeftNode,
                                          aRightNode = aRightNode,
                                          aRightNodeInput = aRightNodeInput)

    @handle_exceptions()
    def moveConnectionsOnPinOutput(self, aInitialNode, aTargetNode):
        """
        moveConnectionsOnPinOutput(self, aInitialNode, aTargetNode)
        Allows to move all the connections connected to the output of the given node to the output of the target node.

        :param aInitialNode: the node initially connected, as an object or given its uid
        :param aTargetNode: the target node, which should be connected after this function, as an object or given its uid
        :type aInitialNode: :class:`.SBSParamNode` or str
        :type aTargetNode: :class:`.SBSParamNode` or str
        :return:
        :raise: :class:`.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to move the connection, the function is not initialized')
        return aDynamicValue.moveConnectionsOnPinOutput(aInitialNode, aTargetNode)

    @handle_exceptions()
    def moveConnectionOnPinInput(self, aInitialNode, aTargetNode, aInitialNodeInput=None, aTargetNodeInput=None):
        """
        moveConnectionOnPinInput(self, aInitialNode, aTargetNode, aInitialNodeInput=None, aTargetNodeInput=None)
        Allows to move the connection connected to the given pin input of the given node to the target pin input of the target node.

        :param aInitialNode: the node initially connected, as an object or given its uid
        :param aTargetNode: the target node, which should be connected after this function, as an object or given its uid
        :param aInitialNodeInput: the identifier of the input initially connected in aInitialNode
        :param aTargetNodeInput: the identifier of the input targeted on aTargetNode
        :type aInitialNode: :class:`.SBSParamNode` or str
        :type aTargetNode: :class:`.SBSParamNode` or str
        :type aInitialNodeInput: :class:`.FunctionInputEnum` or str, optional
        :type aTargetNodeInput: :class:`.FunctionInputEnum` or str, optional
        :return:
        :raise: :class:`.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to move the connection, the function is not initialized')
        return aDynamicValue.moveConnectionOnPinInput(aInitialNode, aTargetNode, aInitialNodeInput, aTargetNodeInput)

    @handle_exceptions()
    def createFunctionNode(self, aFunction, aGUIPos = None, aParameters = None):
        """
        createFunctionNode(aFunction, aGUIPos = None, aParameters = None)
        Create a new function node and add it to the ParamNodes of the function.

        :param aFunction: kind of function to create, among the list defined in :class:`.FunctionEnum`
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the function node

        :type aFunction: :class:`.FunctionEnum` or str
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {sbsenum.FunctionEnum : parameterValue(str)}, optional

        :return: The new :class:`.SBSParamNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}

        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            self.initFunction()
            aDynamicValue = self.getDynamicValue()

        return aDynamicValue.createFunctionNode(aFunction = aFunction,
                                                aGUIPos = aGUIPos,
                                                aParameters = aParameters)

    @handle_exceptions()
    def createFunctionInstanceNode(self, aSBSDocument, aFunction, aGUIPos = None):
        """
        createFunctionInstanceNode(aSBSDocument, aFunction, aGUIPos = None)
        Create a new function node of kind 'instance' which references the given function.

        Note:
            - The function must be defined in the given SBSDocument.
            - Use :func:`createFunctionInstanceNodeFromPath` to add an instance of a function included in an external package.

        :param aSBSDocument: current edited document
        :param aFunction: Function of which this node will be an instance of
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aSBSDocument: :class:`.SBSDocument`
        :type aFunction: :class:`.SBSFunction`
        :type aGUIPos: list of 3 float, optional

        :return: The new :class:`.SBSParamNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            self.initFunction()
            aDynamicValue = self.getDynamicValue()

        return aDynamicValue.createFunctionInstanceNode(aSBSDocument = aSBSDocument,
                                                        aFunction = aFunction,
                                                        aGUIPos = aGUIPos)

    @handle_exceptions()
    def createFunctionInstanceNodeFromPath(self, aSBSDocument, aPath, aGUIPos = None):
        """
        createFunctionInstanceNodeFromPath(aSBSDocument, aPath, aGUIPos = None)
        Create a new function node of kind 'instance' which references the function pointed by the given path.

        :param aSBSDocument: current edited document
        :param aPath: path of the function definition (absolute, relative to the current .sbs file, or given with an alias, for instance *sbs://functions.sbs/Functions/Math/Pi*)

            - If the function is included in the current package, use: *pkg:///MyFunctionIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyFunctionIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyFunctionIdentifier*
            - Note that if the function identifier is equivalent to the filename, the part */MyFunctionIdentifier* may be omit.

        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]

        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :type aGUIPos: list of 3 float, optional

        :return: The new :class:`.SBSParamNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            self.initFunction()
            aDynamicValue = self.getDynamicValue()

        return aDynamicValue.createFunctionInstanceNodeFromPath(aSBSDocument = aSBSDocument,
                                                                aPath = aPath,
                                                                aGUIPos = aGUIPos)

    @handle_exceptions()
    def createIterationOnPattern(self, aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern = None, aGUIOffset = None):
        """
        createIterationOnPattern(aNbIteration, aNodeUIDs, aNodeUIDs_NextPatternInput = None, aGUIOffset = None)
        | Duplicate NbIteration times the given pattern of function nodes, and connect each pattern with the previous one to create this kind of connection:
        | Pattern -> Pattern_1 -> Pattern_2 -> ... -> Pattern_N
        | It allows to completely define the way two successive patterns are connected.
        | For instance, provide aNodeUIDs = [A, B, C] and aNodeUIDs_NextPatternInput = [A'],
            if the pattern is A -> B -> C, and if C is connected to A'
        | If aNodeUIDs_NextPatternInput is let empty, the function will try to connect the successive patterns
            by the most obvious way, respecting the input / output type (float / integer / ...)

        :param aNbIteration: number of time the pattern must be duplicated
        :param aNodeUIDs: list of node's UID that constitute the pattern to duplicate
        :param aNodeUIDs_NextPattern: list of node's UID that correspond to the next pattern, which must be connected to the given pattern. Default to []
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aNbIteration: positive integer
        :type aNodeUIDs: list of str
        :type aNodeUIDs_NextPattern: list of str, optional
        :type aGUIOffset: list of 2 float, optional

        :return: The list of :class:`.SBSParamNode` created (including the nodes given in aNodeUIDs_NextPatternInput), None if failed
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIOffset is None: aGUIOffset = [150, 0]

        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to create an iteration, the function is not initialized')

        return aDynamicValue.createIterationOnPattern(aNbIteration = aNbIteration,
                                                      aNodeUIDs = aNodeUIDs,
                                                      aNodeUIDs_NextPattern = aNodeUIDs_NextPattern,
                                                      aGUIOffset = aGUIOffset)

    @handle_exceptions()
    def createComment(self, aCommentText='Comment', aGUIPos=None, aLinkToNode=None):
        """
        createComment(aCommentText='Comment', aGUIPos=None, aLinkToNode=None)
        Create a new comment.\
        If aLinkToNode is not None, this comment will be linked to the given node, and the given GUI position must be relative to this node.

        :param aCommentText: The text of the comment. Default to 'Comment'
        :param aGUIPos: The comment position in the graph. Default to [0,0,0]
        :param aLinkToNode: The node to associate to this comment, as a SBSParamNode or given its UID
        :type aCommentText: str, optional
        :type aGUIPos: list of 3 float, optional
        :type aLinkToNode: :class:`.SBSParamNode` or str, optional
        :return: The :class:`.SBSGUIObject` created
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to create a comment, the function is not initialized')

        return aDynamicValue.createComment(aCommentText, aGUIPos, aLinkToNode)

    @handle_exceptions()
    def createFrame(self, aSize, aFrameTitle='Frame', aCommentText='', aGUIPos=None, aColor=None, aDisplayTitle=True):
        """
        createFrame(aSize, aFrameTitle='Frame', aCommentText='', aGUIPos=None, aColor=None, aDisplayTitle=True)
        Create a new framed comment.

        :param aSize: The frame size
        :param aFrameTitle: The title of the frame. Default to 'Frame'
        :param aCommentText: The text of the frame. Empty by default
        :param aGUIPos: The frame position in the graph. Default to [0,0,-100]
        :param aColor: The frame color. Default to [0.196, 0.196, 0.509, 0.196]
        :param aDisplayTitle: True to display the frame title. Default to True
        :type aSize: list of 2 float
        :type aFrameTitle: str, optional
        :type aCommentText: str, optional
        :type aGUIPos: list of 3 float, optional
        :type aColor: list of 4 float between 0 and 1, optional.
        :type aDisplayTitle: boolean, optional
        :return: The :class:`.SBSGUIObject` created
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to create a frame, the function is not initialized')

        return aDynamicValue.createFrame(aSize, aFrameTitle, aCommentText, aGUIPos, aColor, aDisplayTitle)

    @handle_exceptions()
    def createFrameAroundNodes(self, aNodeList, aFrameTitle='Frame', aCommentText='', aColor=None, aDisplayTitle=True):
        """
        createFrameAroundNodes(aNodeList, aFrameTitle='Frame', aCommentText='', aColor=None, aDisplayTitle=True)
        Create a new framed comment around the given nodes.

        :param aNodeList: The nodes to include in the frame
        :param aFrameTitle: The title of the frame. Default to 'Frame'
        :param aCommentText: The text of the frame. Empty by default
        :param aColor: The frame color. Default to [0.196, 0.196, 0.509, 0.196]
        :param aDisplayTitle: True to display the frame title. Default to True
        :type aNodeList: list of class:`.SBSParamNode`
        :type aFrameTitle: str, optional
        :type aCommentText: str, optional
        :type aColor: list of 4 float between 0 and 1, optional.
        :type aDisplayTitle: boolean, optional
        :return: The :class:`.SBSGUIObject` created
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to create a frame, the function is not initialized')

        return aDynamicValue.createFrameAroundNodes(aNodeList, aFrameTitle, aCommentText, aColor, aDisplayTitle)

    @handle_exceptions()
    def reframeAroundNodes(self, aFrame, aNodeList):
        """
        reframeAroundNodes(aFrame, aNodeList)
        Move and resize a frame to be around the given nodes.

        :param aFrame: The frame to edit
        :param aNodeList: The nodes to include in the frame
        :type aFrame: :class:`.SBSGUIObject`
        :type aNodeList: list of class:`.SBSParamNode`
        :raise: SBSImpossibleActionError
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to resize a frame, the function is not initialized')

        return aDynamicValue.reframeAroundNodes(aFrame, aNodeList)

    @handle_exceptions()
    def createNavigationPin(self, aPinText, aGUIPos):
        """
        createNavigationPin(self, aPinText, aGUIPos)
        Create a new navigation pin.

        :param aPinText: The text of the navigation pin
        :param aGUIPos: The navigation pin position in the graph
        :type aPinText: str
        :type aGUIPos: list of 3 float
        :return: The :class:`.SBSGUIObject` created
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to create a navigation pin, the function is not initialized')

        return aDynamicValue.createNavigationPin(aPinText, aGUIPos)


    @handle_exceptions()
    def deleteInputParameter(self, aInputParameter):
        """
        deleteInputParameter(aInputParameter)
        Allows to delete the given input parameter.

        :param aInputParameter: The input parameter to remove.
        :type aInputParameter: :class:`.SBSParamInput` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if isinstance(aInputParameter, SBSParamInput):
            aInputIdentifier = aInputParameter.mIdentifier
        else:
            aInputIdentifier = aInputParameter
            aInputParameter = self.getInputParameter(aInputIdentifier)

        try:
            self.mParamInputs.remove(aInputParameter)
            return True
        except:
            raise SBSImpossibleActionError('Impossible to remove input parameter ' + str(aInputIdentifier) + ' from this function')

    @handle_exceptions()
    def deleteNode(self, aNode):
        """
        deleteNode(aNode)
        Allows to delete the given node from the function graph.
        It removes it from the ParamNode list, and delete all the connection from and to that node in the function graph.

        :param aNode: The node to remove, as a SBSParamNode or an UID.
        :type aNode: :class:`.SBSParamNode` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to create an iteration, the function is not initialized')

        return aDynamicValue.deleteNode(aNode)

    @handle_exceptions()
    def deleteFrame(self, aFrame):
        """
        deleteFrame(aFrame)
        Allows to delete the given frame from the graph.

        :param aFrame: The frame to remove, as a Frame or an UID.
        :type aFrame: :class:`.SBSGUIObject` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        return self.mGUIObjectList.deleteGUIObject(aFrame)

    @handle_exceptions()
    def deleteComment(self, aComment):
        """
        deleteComment(aComment)
        Allows to delete the given comment from the graph.

        :param aComment: The comment to remove, as a Comment or an UID.
        :type aComment: :class:`.SBSGUIObject` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        return self.mGUIObjectList.deleteGUIObject(aComment)

    @handle_exceptions()
    def isAPathBetween(self, aLeftNode, aRightNode):
        """
        isAPathBetween(self, aLeftNode, aRightNode)
        Check if there is a path from the left node to the right node with the current connections.

        :param aLeftNode: The left node
        :param aRightNode: The right node
        :type aLeftNode: :class:`.SBSCompNode` or str
        :type aRightNode: :class:`.SBSCompNode` or str
        :return: True if a path is found, False otherwise
        """
        return self.mNodeList.isAPathBetween(aLeftNode, aRightNode)

    @handle_exceptions()
    def isAPathBetween(self, aLeftNode, aRightNode):
        """
        isAPathBetween(self, aLeftNode, aRightNode)
        Check if there is a path from the left node to the right node with the current connections.

        :param aLeftNode: The left node
        :param aRightNode: The right node
        :type aLeftNode: :class:`.SBSParamNode` or str
        :type aRightNode: :class:`.SBSParamNode` or str
        :return: True if a path is found, False otherwise
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to check the path, the function is not initialized')

        return aDynamicValue.isAPathBetween(aLeftNode, aRightNode)

    @handle_exceptions()
    def getInputParameterIndex(self, aInputParamIdentifier):
        """
        getInputParameterIndex(aInputParamIdentifier)
        Get the index of the given input parameter

        :param aInputParamIdentifier: input parameter identifier
        :type aInputParamIdentifier: str
        :return: the index of the input entry as an integer if found, -1 otherwise
        """
        return next((aIndex for aIndex,aInput in enumerate(self.getInputParameters())
                        if aInput.mIdentifier == aInputParamIdentifier), -1)

    @handle_exceptions()
    def getInputParametersInVisibleIfExpression(self, aVisibleIf):
        """
        getInputParametersInVisibleIfExpression(aVisibleIf)
        Get the list of inputs parameters referenced in the given VisibleIf expression

        :param aVisibleIf: the VisibleIf expression
        :type aVisibleIf: str
        :return: a list of :class:`.SBSParamInput`
        """
        paramsInput = []
        paramsStr = api_helpers.getInputsInVisibleIfExpression(aVisibleIfExpr=aVisibleIf)
        for aParamStr in paramsStr:
            aInput = self.getInputParameter(aParamStr)
            if aInput is not None:
                paramsInput.append(aInput)
        return paramsInput

    @handle_exceptions()
    def setInputParameterIndex(self, aInputParamIdentifier, aIndex):
        """
        setInputParameterIndex(aInputParamIdentifier, aIndex)
        Set the index of the given input parameter

        :param aInputParamIdentifier: input parameter identifier
        :param aIndex: index to set, in the range [0 ; nbInputParameters[
        :type aInputParamIdentifier: str
        :type aIndex: int
        :raise: :class:`api_exceptions.SBSImpossibleActionError` if failed
        """
        inputParameters = self.getInputParameters()
        if not 0 <= aIndex < len(inputParameters):
            raise SBSImpossibleActionError('The provided index in not in the range [0; nbInputParameters[')
        currentIndex = self.getInputParameterIndex(aInputParamIdentifier)
        if currentIndex == -1:
            raise SBSImpossibleActionError('Cannot find the given input parameter in the function')
        if currentIndex != aIndex:
            aParamInput = self.mParamInputs.pop(currentIndex)
            self.mParamInputs.insert(aIndex, aParamInput)

    @handle_exceptions()
    def setOutputNode(self, aNode):
        """
        setOutputNode(aNode)
        Set the output node of the function. This may change the type of the function

        :param aNode: The node to set as output, as an object or identified by its UID
        :type aNode: :class:`.SBSParamNode` or str
        """
        aDynValue = self.getDynamicValue()
        aOutputNode = None
        if aDynValue is not None:
            aOutputNode = aDynValue.setOutputNode(aNode)
        if aOutputNode is not None:
            self.mType = str(aOutputNode.getOutputType())
        return aOutputNode

    @handle_exceptions()
    def getAllowedAttributes(self):
        """
        getAllowedAttributes()
        Get the attributes allowed on a SBSFunction

        :return: the list of attribute enumeration allowed (:class:`.AttributesEnum`)
        """
        return SBSFunction.__sAttributes

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        """
        getAttribute(aAttributeIdentifier)
        Get the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :return: the attribute value if defined, None otherwise
        """
        return self.mAttributes.getAttribute(aAttributeIdentifier) if self.mAttributes is not None else None

    @handle_exceptions()
    def setAttribute(self, aAttributeIdentifier, aAttributeValue):
        """
         setAttribute(aAttributeIdentifier, aAttributeValue)
         Set the given attribute

         :param aAttributeIdentifier: The attribute identifier to set
         :param aAttributeValue: The attribute value to set
         :type aAttributeIdentifier: :class:`.AttributesEnum`
         :type aAttributeValue: str
        """
        if self.mAttributes is None:
            self.mAttributes = sbscommon.SBSAttributes()
        self.mAttributes.setAttribute(aAttributeIdentifier, aAttributeValue, self)

    @handle_exceptions()
    def sortNodesAsDAG(self):
        """
        sortNodesAsDAG()
        Sort the ParamNode list of the function to order them as a DAG. The member mParamNodes of the DynamicValue is updated.

        :return: the sorted node list.
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aDynamicValue = self.getDynamicValue()
        if aDynamicValue is None:
            raise SBSImpossibleActionError('Impossible to create an iteration, the function is not initialized')

        return aDynamicValue.sortNodesAsDAG()
