# coding: utf-8
"""
Module **dynamicvalue** provides the definition of the class :class:`.SBSDynamicValue`: which allows to represent all the
function graph in Substance Designer:
- A function graph
- A function defining the value of a dynamic parameter
- The Pixel processor function
"""
from __future__ import unicode_literals
import copy

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import sbscommon
from pysbs import sbsgenerator

from .paramnode import SBSParamNode


# ==============================================================================
@doc_inherit
class SBSDynamicValue(SBSObject):
    """
    Class that contains information on a dynamic value as defined in a .sbs file.
    A dynamic value allows to define a function, for a dynamic parameter, a pixel processor or a function graph.

    Members:
        * mGUILayoutParam    (:class:`.SBSGUILayoutComp`): GUI flags and options.
        * mRootNode          (str, optional): uid of the output node of the function.
        * mParamNodes        (list of :class:`.SBSParamNode`): function nodes list.
        * mGUIObjects        (list of :class:`.SBSGUIObject`): GUI specific objects.
        * mOptions           (list of :class:`.SBSOption`): list of specific options.
        * mValueProcessorRef (:class:`weakref`): Weak Reference to a value processor to keep output type in sync or None
    """
    def __init__(self,
                 aGUILayoutParam    = None,
                 aRootNode          = None,
                 aParamNodes        = None,
                 aGUIObjects        = None,
                 aOptions           = None,
                 aValueProcessorRef = None):
        super(SBSDynamicValue, self).__init__()
        self.mGUILayoutParam    = aGUILayoutParam
        self.mRootNode          = aRootNode
        self.mParamNodes        = aParamNodes if aParamNodes is not None else []
        self.mGUIObjects        = aGUIObjects
        self.mOptions           = aOptions
        self.mValueProcessorRef = aValueProcessorRef

        self.mNodeList = sbscommon.NodeList(self, SBSParamNode, 'mParamNodes')
        self.mGUIObjectList = sbscommon.GUIObjectList(self, 'mGUIObjects')

        self.mMembersForEquality = ['mParamNodes',
                                    'mOptions']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mGUILayoutParam= aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'GUILayoutParam', sbscommon.SBSGUILayoutComp)
        self.mRootNode      = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'rootnode'        )
        self.mParamNodes    = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paramNodes'    , 'paramNode', SBSParamNode)
        self.mGUIObjects    = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'GUIObjects'    , 'GUIObject', sbscommon.SBSGUIObject)
        self.mOptions       = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'options'       , 'option'   , sbscommon.SBSOption)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeSBSNode(aXmlNode      , self.mGUILayoutParam , 'GUILayoutParam' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mRootNode, 'rootnode'       )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mParamNodes     , 'paramNodes'     , 'paramNode' )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mGUIObjects     , 'GUIObjects'     , 'GUIObject' )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mOptions        , 'options'        , 'option'    )

    def __deepcopy__(self, memo):
        """
        Overrides deepcopy to ensure that mNodeList and mGUIObjectList are correctly set

        :return: A clone of itself
        """
        clone = SBSDynamicValue()
        memo[id(self)] = clone
        for aMember in ['mGUILayoutParam', 'mRootNode', 'mParamNodes', 'mGUIObjects', 'mOptions']:
            setattr(clone, aMember, copy.deepcopy(getattr(self, aMember), memo))
        return clone

    @handle_exceptions()
    def copy(self):
        """
        copy()
        Get deep copy of this SBSDynamicValue

        :return: A :class:`.SBSDynamicValue` object, identical to this object
        """
        return copy.deepcopy(self)

    @handle_exceptions()
    def contains(self, aNode):
        """
        contains(aNode)
        Check if the given node belongs to this function graph

        :param aNode: The node to check, as a, object or an UID
        :type aNode: :class:`.SBSParamNode` or str
        :return: True if the given node belongs to the node list, False otherwise
        """
        return self.mNodeList.contains(aNode)

    @handle_exceptions()
    def copyNode(self, aCompNode):
        """
        copyNode(aCompNode)
        Create a copy of the given node and generate a new uid for it

        :param aCompNode: the node to copy
        :type aCompNode: :class:`.SBSParamNode`
        :return: The new :class:`.SBSParamNode` object
        """
        return self.mNodeList.copyNode(aCompNode)

    @handle_exceptions()
    def duplicateNode(self, aCompNode, aGUIOffset = None):
        """
        duplicateNode(aCompNode, aGUIOffset = None)
        Duplicate the given node, generate a new UID and add the node to the same node list than the source node.

        :param aCompNode: the node to duplicate
        :param aGUIOffset: the offset to apply in the positioning of the new node. Default to [150, 0]
        :type aCompNode: :class:`.SBSParamNode` or str
        :type aGUIOffset: list of 2 float, optional
        :return: The new :class:`.SBSParamNode` object
        """
        if aGUIOffset is None: aGUIOffset = [150,0]
        return self.mNodeList.duplicateNode(aCompNode, aGUIOffset)

    @handle_exceptions()
    def createIterationOnNode(self, aNbIteration, aNodeUID, aGUIOffset = None):
        """
        createIterationOnNode(aNbIteration, aNodeUID, aGUIOffset = None)
        Duplicate NbIteration times the given node, and connect each created node to the previous one

        :param aNbIteration: number of time the pattern must be duplicated
        :param aNodeUID: list of node's UID that constitute the pattern to duplicate
        :param aGUIOffset: pattern position offset. Default to [150, 0]
        :type aNbIteration: positive integer
        :type aNodeUID: str
        :type aGUIOffset: list of 2 float, optional
        :return: The last :class:`.SBSParamNode` object created
        """
        if aGUIOffset is None: aGUIOffset = [150,0]

        # Generate iterations with this single node pattern
        return self.createIterationOnPattern(aNbIteration, aNodeUIDs = [aNodeUID], aGUIOffset = aGUIOffset)


    @handle_exceptions()
    def createIterationOnPattern(self, aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern = None, aGUIOffset = None):
        """
        createIterationOnPattern(aNbIteration, aNodeUIDs, aNodeUIDs_NextPatternInput = None, aGUIOffset = None)
        | Duplicate NbIteration times the given pattern of parameters nodes, and connect each pattern with the previous one.
        | It allows to completely define the way two successive patterns are connected.
        | For instance, provide aNodeUIDs = [A, B, C] and aNodeUIDs_NextPatternInput = [A'],
            if the pattern is A -> B -> C, and if C is connected to A'
        | If aNodeUIDs_NextPatternInput is let empty, the function will try to connect the successive patterns
            by the most obvious way, respecting the input / output type (color / grayscale)

        :param aNbIteration: number of time the pattern must be duplicated
        :param aNodeUIDs: list of node's UID that constitute the pattern to duplicate
        :param aNodeUIDs_NextPattern: list of node's UID that correspond to the next pattern, which must be connected to the given pattern.
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aNbIteration: positive integer
        :type aNodeUIDs: list of str
        :type aNodeUIDs_NextPattern: list of str
        :type aGUIOffset: list of 2 float

        :return: The list of :class:`.SBSParamNode` objects created (including the nodes given in aNodeUIDs_NextPatternInput), None if failed
        """
        if aGUIOffset is None: aGUIOffset = [150,0]

        return sbsgenerator.createIterationOnPattern(aParentObject = self,
                                                     aNbIteration = aNbIteration,
                                                     aNodeUIDs = aNodeUIDs,
                                                     aNodeUIDs_NextPattern = aNodeUIDs_NextPattern,
                                                     aForceRandomSeed = False,
                                                     aIncrementIteration = False,
                                                     aGUIOffset = aGUIOffset)

    @handle_exceptions()
    def createFunctionNode(self, aFunction, aGUIPos = None, aParameters = None):
        """
        createFunctionNode(aFunction, aGUIPos = None, aParameters = None)
        Create a new compositing node filter and add it to the CompNodes of the graph.

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

        aParamNode = sbsgenerator.createFunctionNode(aSBSDynamicValue = self,
                                                     aFunction = aFunction,
                                                     aParameters = aParameters)

        if aParamNode.mGUILayout is not None:
            aParamNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mParamNodes', aParamNode)

        return aParamNode


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
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        # Check if the graph belongs to the current SBSDocument
        aFunctionRelPath = aSBSDocument.getSBSFunctionInternalPath(aUID = aFunction.mUID, addDependencyUID=True)
        if aFunctionRelPath is None:
            raise SBSImpossibleActionError('Failed to create instance of function '+str(aFunction))

        aParamNode = sbsgenerator.createFunctionInstanceNode(aSBSDynamicValue = self,
                                                             aFunction = aFunction,
                                                             aPath = aFunctionRelPath,
                                                             aDependency = aSBSDocument.getHimselfDependency())

        if aParamNode.mGUILayout is not None:
            aParamNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mParamNodes', aParamNode)

        return aParamNode


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
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        # Get/Create the dependency and the reference to the pointed function
        outValues = aSBSDocument.getOrCreateDependency(aPath)
        if len(outValues) != 3:
            raise SBSImpossibleActionError('Failed to create instance of function '+python_helpers.castStr(aPath))

        aFunction = outValues[0]
        aFunctionRelPath = outValues[1]
        aDependency = outValues[2]

        # Create the comp instance node
        aParamNode = sbsgenerator.createFunctionInstanceNode(aSBSDynamicValue = self,
                                                             aFunction = aFunction,
                                                             aPath = aFunctionRelPath,
                                                             aDependency = aDependency)

        if aParamNode.mGUILayout is not None:
            aParamNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mParamNodes', aParamNode)

        return aParamNode

    @handle_exceptions()
    def connectNodes(self, aLeftNode, aRightNode, aRightNodeInput = None):
        """
        connectNodes(aLeftNode, aRightNode, aRightNodeInput = None)
        Connect the given nodes together: aLeftNode -> aRightNode(on the input aRightNodeInput)
        If the right node input is None, the connection will be done on the first compatible input of the right node.

        :param aLeftNode: Node to connect from, as a SBSParamNode or given its UID
        :param aRightNode: Node to connect to, as a SBSParamNode or given its UID
        :param aRightNodeInput: Identifier of the input of the right node

        :type aLeftNode: :class:`.SBSParamNode` or str
        :type aRightNode: :class:`.SBSParamNode` or str
        :type aRightNodeInput: :class:`.FunctionInputEnum` or str, optional

        :return: The connection if success, None otherwise (in case of type incompatibility for instance)
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Check that the given nodes belongs to the function graph
        leftNode = self.getNode(aLeftNode)
        rightNode = self.getNode(aRightNode)
        if not self.contains(aRightNode) or not self.contains(aLeftNode):
            raise SBSImpossibleActionError('Impossible to connect node '+str(aLeftNode)+' to '+str(aRightNode)+', one of them is not found in the graph')

        # Check that the connection will not create a cycle in the DAG
        if self.isAPathBetween(aLeftNode = rightNode, aRightNode = leftNode):
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', it would create a cycle')

        # Get the function nodes parameters (input entries, parameters, outputs)
        aLeftNodeDefinition  = leftNode.getDefinition()
        aRightNodeDefinition = rightNode.getDefinition()
        if aRightNodeDefinition is None or aLeftNodeDefinition is None or not aLeftNodeDefinition.mOutputs:
            raise SBSImpossibleActionError('Impossible to connect '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', failed to get a definition')

        # Find the appropriate paramInput identifier
        if aRightNodeInput is not None:
            aRightInputDef = aRightNodeDefinition.getInput(aRightNodeInput)
        else:
            # Only one input => take it
            if len(aRightNodeDefinition.mInputs) == 1:
                aRightInputDef = aRightNodeDefinition.mInputs[0]
            # Else take the first input compatible with the left output
            else:
                aRightInputDef = aRightNodeDefinition.getFirstInputOfType(aLeftNodeDefinition.mOutputs[0].mType)

        if aRightInputDef is None:
            raise SBSImpossibleActionError('Impossible to connect '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+
                                           ', cannot find on which input to connect them')

        if not python_helpers.isStringOrUnicode(aRightInputDef.mIdentifier):
            aRightInputIdentifier = sbslibrary.getFunctionInput(aRightInputDef.mIdentifier)
        else:
            aRightInputIdentifier = aRightInputDef.mIdentifier

        # Create the connection
        aLeftNodeType = leftNode.getOutputType()
        if aRightInputDef.mType == sbsenum.ParamTypeEnum.TEMPLATE1:
            aRightNodeTypeResolved = aRightNodeDefinition.getInputType(aRightInputDef.mIdentifier, True)
        elif aRightInputDef.mType == sbsenum.ParamTypeEnum.DUMMY_TYPE:
            aRightInputDef.mType = aLeftNodeType
            aRightNodeTypeResolved = aLeftNodeType
            aRightNode.setType(aLeftNodeType)
            aRightNodeDefinition.setInputs([sbslibrary.sbsfunctions.FunctionInput(sbsenum.FunctionInputEnum.INPUT, aRightNodeTypeResolved)])
        else:
            aRightNodeTypeResolved = aRightInputDef.mType

        # Check the type compatibility
        if not aLeftNodeType & aRightNodeTypeResolved:
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', types are incompatible')

        # Do the connection: Create a new connection or modify the existing one on the right input
        aConn = rightNode.getConnectionOnPin(aRightInputIdentifier)
        if aConn is None:
            aConn = sbscommon.SBSConnection(aIdentifier = aRightInputIdentifier,
                                            aConnRef    = leftNode.mUID)
            api_helpers.addObjectToList(rightNode, 'mConnections', aConn)
        else:
            aConn.setConnection(aConnRefValue=leftNode.mUID)

        # Specify the output type of the right node if it is a template
        if aRightNodeDefinition.mOutputs:
            if aRightNodeDefinition.mOutputs[0].mType == sbsenum.ParamTypeEnum.TEMPLATE1 and \
                    aRightInputDef.mType == sbsenum.ParamTypeEnum.TEMPLATE1:
                rightNode.mType = str(aLeftNodeType)
                # Update node type if this dynamic value is in a Value Processor
                self.updateValueProcessorType()

        return aConn

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
        # Check that the given nodes belongs to the function graph
        leftNode = self.getNode(aLeftNode)
        rightNode = self.getNode(aRightNode)
        if not self.contains(aRightNode) or not self.contains(aLeftNode):
            raise SBSImpossibleActionError('Impossible to connect node '+str(aLeftNode)+' to '+str(aRightNode)+', one of them is not found in the graph')

        # Remove all connections
        if aRightNodeInput is None:
            rightNode.removeConnectionsFrom(leftNode)
        # Remove only the connection on the given input pin
        else:
            if not python_helpers.isStringOrUnicode(aRightNodeInput):
                aRightNodeInput = sbslibrary.getFunctionInput(aRightNodeInput)
            conn = rightNode.getConnectionOnPin(aRightNodeInput)
            if conn is not None and conn.getConnectedNodeUID() == leftNode.mUID:
                rightNode.removeConnectionOnPin(aRightNodeInput)

    @handle_exceptions()
    def getConnectionsFromNode(self, aLeftNode):
        """
        getConnectionsFromNode(self, aLeftNode)
        Get the connections starting from the output of the given left node.

        :param aLeftNode: the node to consider, as a SBSCompNode or given its uid
        :type aLeftNode: :class:`.SBSParamNode` or str
        :return: a list of :class:`.SBSConnection`
        """
        return self.mNodeList.getConnectionsFromNode(aLeftNode)

    @handle_exceptions()
    def getConnectionsToNode(self, aRightNode, aRightNodeInput=None):
        """
        getConnectionsToNode(self, aRightNode, aRightNodeInput=None)
        Get the connections incoming to the given right node, to a particular input or for all its inputs.

        :param aRightNode: the node to consider, as a SBSCompNode or given its uid
        :param aRightNodeInput: the pin input identifier to consider. If let None, all the inputs will be considered
        :type aRightNode: :class:`.SBSCompNode` or str
        :type aRightNodeInput: :class:`.InputEnum` or str, optional
        :return: a list of :class:`.SBSConnection`
        """
        if isinstance(aRightNodeInput, int):
            aRightNodeInput = sbslibrary.getFunctionInput(aRightNodeInput)
        return self.mNodeList.getConnectionsToNode(aRightNode, aRightNodeInput)

    @handle_exceptions()
    def moveConnectionsOnPinOutput(self, aInitialNode, aTargetNode):
        """
        moveConnectionsOnPinOutput(self, aInitialNode, aTargetNode)
        Allows to move all the connections connected to the output of the given node to the output of the target node.

        :param aInitialNode: the node initially connected, as an object or given its uid
        :param aTargetNode: the target node, which should be connected after this function, as an object or given its uid
        :type aInitialNode: :class:`.SBSParamNode` or str
        :type aTargetNode: :class:`.SBSParamNode` or str
        :raise: :class:`.SBSImpossibleActionError`
        """
        initialNode = self.getNode(aInitialNode)
        targetNode = self.getNode(aTargetNode)
        if initialNode is None or targetNode is None:
            raise SBSImpossibleActionError('Cannot modify connections, one of the two nodes is not found in the graph')

        initialType = initialNode.getOutputType()
        targetType = targetNode.getOutputType()
        if not initialType & targetType:
            raise SBSImpossibleActionError('Cannot modify connections, the target output type is not compatible with the initial output type')

        connections = self.getConnectionsFromNode(aLeftNode=initialNode)
        if not connections:
            raise SBSImpossibleActionError('No connections on the output of node '+initialNode.getDisplayName())

        for aConn in connections:
            aConn.setConnection(aTargetNode.mUID)

    @handle_exceptions()
    def moveConnectionOnPinInput(self, aInitialNode, aTargetNode, aInitialNodeInput=None, aTargetNodeInput=None):
        """
        moveConnectionOnPinInput(self, aInitialNode, aTargetNode, aInitialNodeInput=None, aTargetNodeInput=None)
        Allows to move the connection connected to the given pin input of the given node to the target pin input of the target node.

        :param aInitialNode: the node initially connected, as an object or given its uid
        :param aTargetNode: the target node, which should be connected after this function, as an object or given its uid
        :param aInitialNodeInput: the identifier of the input initially connected in aInitialNode. If None, the first input will be considered
        :param aTargetNodeInput: the identifier of the input targeted on aTargetNode. If None, the first input will be considered
        :type aInitialNode: :class:`.SBSParamNode` or str
        :type aTargetNode: :class:`.SBSParamNode` or str
        :type aInitialNodeInput: :class:`.FunctionInputEnum` or str, optional
        :type aTargetNodeInput: :class:`.FunctionInputEnum` or str, optional
        :return:
        :raise: :class:`.SBSImpossibleActionError`
        """
        initialNode = self.getNode(aInitialNode)
        targetNode = self.getNode(aTargetNode)
        if initialNode is None or targetNode is None:
            raise SBSImpossibleActionError('Cannot modify connections, one of the two nodes is not found in the graph')

        initialInputDef = initialNode.getInputDefinition(aInputIdentifier=aInitialNodeInput)
        targetInputDef = targetNode.getInputDefinition(aInputIdentifier=aTargetNodeInput)
        if initialInputDef is None:
            raise SBSImpossibleActionError('Cannot find the initial input on node '+initialNode.getDisplayName())
        if targetInputDef is None:
            raise SBSImpossibleActionError('Cannot find the target input on node '+targetNode.getDisplayName())

        inputIdentifier = initialInputDef.getIdentifierStr()
        conn = initialNode.getConnectionOnPin(inputIdentifier)
        leftNode = self.getNodesConnectedTo(aRightNode=initialNode, aRightNodeInput=aInitialNodeInput)
        if conn is None or not leftNode:
            raise SBSImpossibleActionError('No connection found on the input '+inputIdentifier+' of the node '+initialNode.getDisplayName())
        leftNode = leftNode[0]

        # Copy the connection on the target
        self.connectNodes(aLeftNode=leftNode, aRightNode=targetNode, aRightNodeInput=targetInputDef.getIdentifierStr())

        # Remove the previous connection
        initialNode.removeConnectionOnPin(inputIdentifier)

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
        if aLinkToNode is not None:
            aLinkToNode = self.getNode(aLinkToNode)
        aNodeUID = aLinkToNode.mUID if aLinkToNode is not None else None
        return self.mGUIObjectList.createComment(aCommentText, aGUIPos, aLinkToNode=aNodeUID)

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
        return self.mGUIObjectList.createFrame(aSize, aFrameTitle, aCommentText, aGUIPos, aColor, aDisplayTitle)

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
        return self.mGUIObjectList.createFrameAroundNodes(aNodeList, aFrameTitle, aCommentText, aColor, aDisplayTitle)

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
        return self.mGUIObjectList.reframeAroundNodes(aFrame, aNodeList)

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
        return self.mGUIObjectList.createNavigationPin(aPinText, aGUIPos)

    @handle_exceptions()
    def getAllComments(self):
        """
        getAllComments()
        Get all comments defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        return self.mGUIObjectList.getAllComments()

    @handle_exceptions()
    def getAllFrames(self):
        """
        getAllFrames()
        Get all frames defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        return self.mGUIObjectList.getAllFrames()

    @handle_exceptions()
    def getAllNavigationPins(self):
        """
        getAllNavigationPins()
        Get all the navigation pins defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        return self.mGUIObjectList.getAllNavigationPins()

    @handle_exceptions()
    def getAllGUIObjects(self):
        """
        getAllGUIObjects()
        Get all the GUI objects defined in the graph (Comments, Frames, Navigation Pins)

        :return: a list of :class:`.SBSGUIObject`
        """
        return self.mGUIObjectList.getAllGUIObjects()

    @handle_exceptions()
    def getAllFunctionsOfKind(self, aFunction):
        """
        getAllFunctionsOfKind(aFunction)
        Search for all SBSParamNode which represents the given filter kind.

        :param aFunction: kind of filters to look for
        :type aFunction: :class:`.FunctionEnum` str
        :return: a list of :class:`.SBSParamNode` containing all functions of the given kind.
        """
        if not python_helpers.isStringOrUnicode(aFunction):
            aFunction = sbslibrary.getFunctionDefinition(aFunction).mIdentifier
        return [node for node in self.mParamNodes if (node.mFunction == aFunction)]

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
        absPath = aSBSDocument.convertToAbsolutePath(aPath)
        if absPath.endswith('.sbs'):
            posSep = absPath.rfind('/')
            fctName = absPath[posSep+1:-4]
            absPath += '/' + fctName

        return [node for node in self.mParamNodes if node.isAnInstance() and node.getReferenceAbsPath() == absPath]

    @handle_exceptions()
    def getAllDependencyUID(self):
        """
        getAllDependencyUID()
        Get the UIDs of the dependencies used by this dynamic function

        :return: a list of UIDs as strings
        """
        dependencySet = set()
        for aNode in [aNode for aNode in self.getNodeList() if aNode.isAnInstance()]:
            dependencySet.add(aNode.getDependencyUID())
        return sorted(list(dependencySet))

    @handle_exceptions()
    def getAllReferencesOnDependency(self, aDependency):
        """
        getAllReferencesOnDependency(self,(aDependency)
        Get all the SBSParamNode that are referencing the given dependency

        :param aDependency: The dependency to look for (UID or object)
        :type aDependency: str or :class:`.SBSDependency`
        :return: A list of :class:`.SBSParamNode`
        """
        return [node for node in self.mParamNodes if node.hasAReferenceOnDependency(aDependency)]

    @handle_exceptions()
    def getCommentsAssociatedToNode(self, aNode):
        """
        getCommentsAssociatedToNode(aNode)
        Get the list of comments associated to the given node

        :param aNode: The node to consider, as a SBSParamNode or given its UID
        :type aNode: :class:`.SBSParamNode` or str
        :return: a list of :class:`.SBSGUIObject`
        """
        aUID = aNode.mUID if isinstance(aNode, SBSParamNode) else aNode
        return [aComment for aComment in self.getAllComments() if aComment.hasDependencyOn(aUID)]

    @handle_exceptions()
    def getNode(self, aNode):
        """
        getNode(aNode)
        Search for the given function node in the node list

        :param aNode: node to get, identified by its uid or as a :class:`.SBSParamNode`
        :type aNode: :class:`.SBSParamNode` or str
        :return: A :class:`.SBSParamNode` object if found, None otherwise
        """
        return self.mNodeList.getNode(aNode)

    @handle_exceptions()
    def getNodeList(self, aNodesList = None):
        """
        getNodeList(aNodesList = None)
        Get all the function nodes of this function, or look for the given nodes if aNodesList is not None

        :param aNodesList: list of node to look for
        :type aNodesList: list of str or list of :class:`.SBSParamNode`, optional
        :return: a list of :class:`.SBSParamNode` included in the function graph
        """
        return self.mNodeList.getNodeList(aNodesList)

    @handle_exceptions()
    def getNodesConnectedFrom(self, aLeftNode):
        """
        getNodesConnectedFrom(aLeftNode)
        Get all the nodes connected to an output of the given node.

        :param aLeftNode: the node to consider
        :type aLeftNode: :class:`.SBSParamNode` or str
        :return: a list of :class:`.SBSParamNode`
        """
        return self.mNodeList.getNodesConnectedFrom(aLeftNode)

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
        if isinstance(aRightNodeInput, int):
            aRightNodeInput = sbslibrary.getFunctionInput(aRightNodeInput)
        return self.mNodeList.getNodesConnectedTo(aRightNode, aRightNodeInput)

    @handle_exceptions()
    def getNodesDockedTo(self, aNode):
        """
        getNodesDockedTo(aNode)
        Get all the nodes that are docked to the given node.

        :param aNode: the node to consider
        :type aNode: :class:`.SBSParamNode` or str
        :return: a list of :class:`.SBSParamNode` corresponding to the nodes that are docked to the given node.
        """
        return self.mNodeList.getNodesDockedTo(aNode)

    @handle_exceptions()
    def getNodeAssociatedToComment(self, aComment):
        """
        getNodeAssociatedToComment(aComment)
        Get the node associated to the given comment.

        :param aComment: The comment to consider
        :type aComment: :class:`.SBSGUIObject`
        :return: the :class:`.SBSParamNode` if found, None otherwise
        """
        aUID = aComment.getDependencyUID()
        return self.getNode(aUID) if aUID is not None else None

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
        return self.mGUIObjectList.getNodesInFrame(aFrame)

    @handle_exceptions()
    def getRect(self, aNodeList = None):
        """
        getRect(aNodeList = None)
        Get the rectangle occupied by all the nodes of this function, or use only the given nodes if aNodeList is not None

        :param aNodeList: The list of node to take in account for the GUI rectangle. None to consider the node list pointed by itself.
        :type aNodeList: list of str or list of :class:`.SBSParamNode`, optional
        :return: A :class:`.Rect`
        """
        return self.mNodeList.getRect(aNodeList)

    @handle_exceptions()
    def getOutputNode(self):
        """
        getOutputNode()
        Get the output node of the function.

        :return: The :class:`.SBSParamNode` corresponding to the output node, None if there is no output node
        """
        return self.getNode(self.mRootNode) if self.mRootNode is not None else None

    @handle_exceptions()
    def getOutputType(self):
        """
        getOutputType()
        Get the type of output node of the function.

        :return: The type to the output node, in the format :class:`.ParamTypeEnum`. VOID_TYPE if there is no output node
        """
        outputNode = self.getOutputNode()
        return outputNode.getOutputType() if outputNode is not None else sbsenum.ParamTypeEnum.VOID_TYPE

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Parse the node list to find a node with the given uid

        :param aUID: UID to check
        :type aUID: str
        :return: True if a node has this uid
        """
        return self.getNode(aUID) is not None

    @handle_exceptions()
    def getUsedParameters(self, aParameters):
        """
        getUsedParameters(aParameters)
        Get all the input parameters used in the this dynamic value among the given list, meaning the ones that are get by the function.

        :param aParameters: the input parameters to look for
        :type aParameters: list of :class:`.SBSParamInput`
        :return: the list of useless :class:`.SBSParamInput`
        """
        aUsedInputParamList = []
        for aInputParam in aParameters:
            aGetParamFunction = sbslibrary.getFunctionGetType(aInputParam.getType())

            for aParamNode in self.getAllFunctionsOfKind(aGetParamFunction):
                if aParamNode.getParameterValue(aGetParamFunction) == aInputParam.mIdentifier:
                    aUsedInputParamList.append(aInputParam)
                    break
        return aUsedInputParamList

    @handle_exceptions()
    def setOutputNode(self, aNode):
        """
        setOutputNode(aNode)
        Set the output node of the function.

        :param aNode: the node to set as output, or its UID
        :type aNode: :class:`.SBSParamNode` or str
        :return: The :class:`.SBSParamNode` corresponding to the output node, False if not found
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Ensure the given node belongs to this function
        if python_helpers.isStringOrUnicode(aNode):    aNodeUID = aNode
        else:                                          aNodeUID = aNode.mUID
        aParamNode = self.getNode(aNodeUID)
        if aParamNode is None:
            raise SBSImpossibleActionError('Failed to set the output, can\'t find the node '+aNodeUID)

        # Set root node value
        self.mRootNode = aNodeUID

        # Update node type if this dynamic value is in a Value Process
        self.updateValueProcessorType()

        return aParamNode

    @handle_exceptions()
    def setToInputParam(self, aParentGraph, aInputParamIdentifier):
        """
        setToInputParam(aParentGraph, aInputParamIdentifier)
        This function will be set to return the value of the given input parameter defined on the given graph

        :param aParentGraph: graph in which the input parameter is defined.
        :param aInputParamIdentifier: input parameter identifier

        :type aParentGraph: :class:`.SBSGraph`
        :type aInputParamIdentifier: str

        :return: True if succeed
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aParamInput = aParentGraph.getInputParameter(aInputParamIdentifier)
        if aParamInput is None:
            raise SBSImpossibleActionError('Failed to set the parameter, can\'t find the input parameter '+
                                           str(aInputParamIdentifier))
        if self.mParamNodes:
            del self.mParamNodes[:]

        # Create the appropriate function GET_<> depending on the type of the input parameter
        aFunction = sbslibrary.getFunctionGetType(aParamInput.getType())
        aNode = self.createFunctionNode(aFunction, aParameters = {aFunction:aInputParamIdentifier})
        self.setOutputNode(aNode.mUID)

        return True

    @handle_exceptions()
    def deleteNode(self, aNode):
        """
        deleteNode(aNode)
        Allows to delete the given node from the graph.
        It removes it from the ParamNode list, and delete all the connection from and to that node in the function graph.

        :param aNode: The node to remove, as a SBSParamNode or an UID.
        :type aNode: :class:`.SBSParamNode` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        return self.mNodeList.deleteNode(aNode)

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
    def deleteNavigationPin(self, aNavigationPin):
        """
        deleteNavigationPin(aNavigationPin)
        Allows to delete the given navigation pin from the graph.

        :param aNavigationPin: The navigation pin to remove, as a NavigationPin or an UID.
        :type aNavigationPin: :class:`.SBSGUIObject` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        return self.mGUIObjectList.deleteGUIObject(aNavigationPin)

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
        """
        return self.mNodeList.isAPathBetween(aLeftNode, aRightNode)

    @handle_exceptions()
    def sortNodesAsDAG(self):
        """
        sortNodesAsDAG()
        Sort the ParamNode list of the function to order them as a DAG. The member mParamNodes is updated.

        :return: the sorted node list.
        """
        return self.mNodeList.sortNodesAsDAG()

    @handle_exceptions()
    def updateValueProcessorType(self):
        """
        updateValueProcessorType()
        Updates the value processor type so it represents what is in the dynamic value if there is one

        :return: None
        """
        vpRef = self.mValueProcessorRef() if self.mValueProcessorRef else None
        if vpRef:
            vpRef.mCompOutputs[0].mCompType = str(self.getOutputType())
