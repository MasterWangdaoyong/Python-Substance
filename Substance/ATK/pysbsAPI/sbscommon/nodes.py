# coding: utf-8
"""
Module **nodes** provides the definition of the common classes :class:`.SBSNode` and :class:`.NodeList`.
"""
from __future__ import unicode_literals
import abc
import copy
import weakref

from pysbs import python_helpers, api_helpers, sbsenum
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject, UIDGenerator
from pysbs.sbscommon.connections import SBSConnection
from pysbs.sbscommon.gui import SBSGUILayout, Rect


# ==============================================================================
@doc_inherit
class SBSNode(SBSObject):
    """
    Class used to gather common information of a :class:`.SBSCompNode`, :class:`.SBSParamNode`,
    :class:`.SBSParamsGraphNode` and :class:`.MDLNode`

    Members:
        * mGUIName    (str, optional): name of the node.
        * mUID        (str): node unique identifier in the /compNodes/ context.
        * mDisabled   (str, optional): this node is disabled.
        * mGUILayout  (:class:`.SBSGUILayout`): GUI position/options
        * mConnections (list of :class:`.SBSConnection`, optional): input connections list.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,
                 aGUIName   = None,
                 aUID       = '',
                 aDisabled  = None,
                 aConnections= None,
                 aGUILayout = None):
        super(SBSNode, self).__init__()
        self.mGUIName    = aGUIName
        self.mUID        = aUID
        self.mDisabled   = aDisabled
        self.mConnections = aConnections
        self.mGUILayout  = aGUILayout

        self.mMembersForEquality = ['mGUIName',
                                    'mDisabled']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mGUIName   = aSBSParser.getXmlElementVAttribValue(aXmlNode,                 'GUIName'    )
        self.mUID       = aSBSParser.getXmlElementVAttribValue(aXmlNode,                 'uid'        )
        self.mDisabled  = aSBSParser.getXmlElementVAttribValue(aXmlNode,                 'disabled'   )
        self.mConnections= aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'connections', 'connection', SBSConnection)
        self.mGUILayout = aSBSParser.parseSBSNode(aContext, aDirAbsPath,       aXmlNode, 'GUILayout'  , SBSGUILayout)

    @abc.abstractmethod
    def write(self, aSBSWriter, aXmlNode):
        pass

    @abc.abstractmethod
    def getDefinition(self):
        """
        getDefinition()
        Get the node definition (Inputs, Outputs, Parameters) accordingly to the node implementation

        :return: a :class:`.NodeDef` object if defined, None otherwise
        """
        pass

    @abc.abstractmethod
    def getDisplayName(self):
        """
        getDisplayName()
        Get the display name of this node

        :return: the display name as a string
        """
        pass

    @handle_exceptions()
    def getInputDefinition(self, aInputIdentifier=None):
        """
        getInputDefinition(self, aInputIdentifier=None)
        Get the input definition corresponding to the given identifier.

        :param aInputIdentifier: The identifier to get. If let None, the primary input will be returned
        :type aInputIdentifier: :class:`.InputEnum` or str, optional
        :return: the input definition as a :class:`.CompNodeInput` if found, None otherwise
        """
        nodeDef = self.getDefinition()
        if not nodeDef:
            return None
        if aInputIdentifier is not None:
            return nodeDef.getInput(aInputIdentifier)
        else:
            return nodeDef.getAllInputs()[0] if nodeDef.getAllInputs() else None

    @handle_exceptions()
    def getConnections(self):
        """
        getConnections()
        Get the connections defined on this node.

        :return: a list of :class:`.SBSConnection`
        """
        return self.mConnections if self.mConnections is not None else []

    @handle_exceptions()
    def getConnectionsFromNode(self, aLeftNode):
        """
        getConnectionsFromNode(aLeftNode)
        Get all the connections coming from the given left node.

        :param aLeftNode: The node to look for in the incoming connections of this node, as an object or a UID
        :type aLeftNode: :class:`.SBSNode` or str
        :return: a list of :class:`.SBSConnection`
        """
        if isinstance(aLeftNode, SBSNode):
            aLeftNode = aLeftNode.mUID
        return [aConn for aConn in self.getConnections() if aConn.getConnectedNodeUID() == aLeftNode]

    @handle_exceptions()
    def getConnectedNodesUID(self):
        """
        getConnectedNodesUID()
        Get the UIDs of the nodes connected to this node.

        :return: The UIDs as a list of string
        """
        return [aConn.getConnectedNodeUID() for aConn in self.getConnections()]

    @handle_exceptions()
    def getConnectionOnPin(self, aPinIdentifier):
        """
        getConnectionOnPin(aPinIdentifier)
        Get the connection defined on the given input.

        :param aPinIdentifier: identifier of the input pin (for :class:`.SBSCompNode`, :class:`.SBSParamNode` and :class:`.MDLNode`) or of the output pin(for :class:`.SBSParamsGraphNode`)
        :type aPinIdentifier: str
        :return: a :class:`.SBSConnection` object corresponding to the connection defined on the given pin. None otherwise
        """
        return next((conn for conn in self.getConnections() if conn.mIdentifier == aPinIdentifier), None)

    @handle_exceptions()
    def getPosition(self):
        """
        getPosition()
        Get the position of this node in the graph GUI.

        :return: a list of 3 float
        """
        return self.mGUILayout.mGPos if self.mGUILayout is not None else [0,0,0]

    @handle_exceptions()
    def getOffsetPosition(self, aOffset = None):
        """
        getOffsetPosition(aOffset = None)
        Compute the position of this node offset by the given offset

        :param aOffset: the offset to apply to the node's current position. Default to [0,0]
        :type aOffset: list of 2 float, optional
        :return: the offset position
        """
        if aOffset is None: aOffset = [0,0]

        aOffsetPos = copy.copy(self.getPosition())
        aOffsetPos[0] += aOffset[0]
        aOffsetPos[1] += aOffset[1]
        return aOffsetPos

    @handle_exceptions()
    def getRect(self):
        """
        getRect()
        Return the rectangle of this node.

        :return: The rectangle as a :class:`.Rect`
        """
        height = 96.0
        nodeDef = self.getDefinition()
        if nodeDef is not None:
            nbElem = max(len(nodeDef.getAllInputs()), len(nodeDef.getAllOutputs()))
            height += (96.0/4.5)*max(nbElem-3, 0)

        aPos  = self.getPosition()[0:2]
        aSize = self.mGUILayout.mSize if self.mGUILayout is not None and self.mGUILayout.mSize != [-1,-1]  else [96,height]
        return Rect(aLeft   = aPos[0] - aSize[0]/2,
                    aTop    = aPos[1] - aSize[1]/2,
                    aWidth  = aSize[0],
                    aHeight = aSize[1])

    @abc.abstractmethod
    def hasAReferenceOnDependency(self, aDependency):
        """
        hasAReferenceOnDependency(aDependency)
        Check if this node directly references the given dependency. \
        For instance if it instantiates a graph or a resource included in this dependency.

        :param aDependency: The dependency to look for (UID or object)
        :type aDependency: str or :class:`.SBSDependency`
        :return: True if this node references this dependency, False otherwise
        """
        return False

    @abc.abstractmethod
    def hasAReferenceOnInternalPath(self, aInternalPath):
        """
        hasAReferenceOnInternalPath(aInternalPath)
        Check if this node references the given internal path (pkg:///). \
        For instance if it instantiates the graph or the resource pointed at the given path.

        :param aInternalPath: The internal path to look for
        :type aInternalPath: str
        :return: True if this node references the given internal path, False otherwise
        """
        return False

    @handle_exceptions()
    def isConnectedTo(self, aLeftNode):
        """
        isConnectedTo(aLeftNode)
        Check if the node is connected to the given node, in the direction aLeftNode -> self

        :param aLeftNode: The node to look for in the connections of this node.
        :type aLeftNode: :class:`.SBSNode` or str (UID)
        :return: True if the nodes are connected, False otherwise
        """
        if isinstance(aLeftNode, SBSNode):
            aLeftNode = aLeftNode.mUID

        aConn = next((aConn for aConn in self.getConnections() if aConn.getConnectedNodeUID() == aLeftNode), None)
        return aConn is not None

    @handle_exceptions()
    def isDocked(self):
        """
        isDocked()
        Check if this node is docked.

        :return: True if this node is docked, None otherwise
        """
        return self.mGUILayout.mDocked == '1' if self.mGUILayout is not None and self.mGUILayout.mDocked is not None else False

    @handle_exceptions()
    def removeConnectionsFrom(self, aLeftNode):
        """
        removeConnectionsFrom(aLeftNode)
        Remove all the connections from aLeftNode to this node (in the direction aLeftNode -> self)

        :param aLeftNode: The node to look for in the connections of this node.
        :type aLeftNode: :class:`.SBSNode` or str (UID)
        :return: Nothing
        """
        if isinstance(aLeftNode, SBSNode):
            aLeftNode = aLeftNode.mUID

        connections = self.getConnections()
        for i, aConn in reversed(list(enumerate(connections))):
            if aConn.getConnectedNodeUID() == aLeftNode:
                connections.pop(i)

    @handle_exceptions()
    def removeConnectionOnPin(self, aPinIdentifier):
        """
        removeConnectionOnPin(aInput)
        Remove the connection on the given input pin.

        :param aPinIdentifier: identifier of the input pin (for :class:`.SBSCompNode` and :class:`.SBSParamNode`) or of the output pin(for :class:`.SBSParamsGraphNode`) to disconnect
        :type aPinIdentifier: :class:`.InputEnum` or :class:`.FunctionInputEnum` or str
        :return: True if a connection is removed, False otherwise
        """
        for i, conn in enumerate(self.getConnections()):
            if conn.mIdentifier == aPinIdentifier:
                self.getConnections().pop(i)
                return True
        return False

    @handle_exceptions()
    def setPosition(self, aPosition):
        """
        setPosition(aPosition)
        Set the position of this node in the graph GUI.

        :param aPosition: The position to set
        :type aPosition: a list of 3 float
        """
        if python_helpers.isStringOrUnicode(aPosition):
            aPosition = api_helpers.getTypedValueFromStr(aValue=aPosition, aType=sbsenum.ParamTypeEnum.FLOAT3)
        if not self.mGUILayout:
            self.mGUILayout = SBSGUILayout(aGPos = aPosition)
        else:
            self.mGUILayout.mGPos = aPosition



# =======================================================================
class NodeList:
    """
    Class used to provide common methods to SBSObjects that contains a list of nodes:
    :class:`.SBSGraph` and
    :class:`.SBSDynamicValue`

    Members:
        * mParentObject (:class:`.SBSObject`): Parent object that contains the node list.
        * mNodeType     (class): type of node (compnode.SBSCompNode for instance).
        * mNodesAttr    (str): attribute member name in the parent object that corresponds to the node list.
    """
    def __init__(self, aParentObject, aNodeType, aNodesAttribute):
        self.mParentObject = weakref.ref(aParentObject)
        self.mNodeType     = aNodeType
        self.mNodesAttr    = aNodesAttribute

    @handle_exceptions()
    def computeConnectionsInsidePattern(self, aNodeList):
        """
        computeConnectionsInsidePattern(aNodeList)
        Compute the input and output connections of the nodes included in the list.
        It uses the node definition to order the nodes, and the GUI position in case of equality.

        :param aNodeList: The list of node to take in account for the topological sort.
        :type aNodeList: list of tuple(int, :class:`.SBSNode`).
        :return: The input and output connections of each node, as a list of tuple (list of inputs, list of outputs) of
            the same size than aNodeList, where each element of a list describe a connection with three elements:

            - 'index' (index of the connected node)
            - 'identifier' (pin identifier) for input, 'uid' (pin uid) for output
            - 'type' (data type)
        """
        # Init the list of input and output connections inside pattern (tuple: (list of inputs, list of outputs)
        connectionsInsidePattern = [([],[]) for _ in range(len(aNodeList))]

        # Parse all nodes of the pattern
        for i, aNode in enumerate(aNodeList):
            # For each connections of this node, determine if it is connected from a node inside the pattern
            for aConnInput in aNode.getConnections():
                aConnInputRef = aConnInput.getConnectedNodeUID()

                # Parse all the nodes of the pattern, looking for the node connected to aNode on this connection
                for j, aNodeInput in [(j, aNodeInput) for j, aNodeInput in enumerate(aNodeList) if aNodeInput.mUID == aConnInputRef]:
                    # If we found one, this connection comes from the pattern => fill inputConnections
                    if self.mNodeType.__name__ == 'SBSCompNode':
                        aType = aNodeInput.getCompOutputType(aConnInput.getConnectedNodeOutputUID())
                    elif self.mNodeType.__name__ == 'SBSParamNode':
                        aType = aNodeInput.getOutputType()
                    else:
                        aType = aNodeInput.getOutputType(aConnInput.getConnectedNodeOutputUID())

                    # Fill inputConnections of the right node:
                    connectionsInsidePattern[i][0].append((j,{'type':aType,'identifier':aConnInput.mIdentifier}))

                    # Fill outputConnections of the left node:
                    connRefOutput = aConnInput.getConnectedNodeOutputUID()
                    connectionsInsidePattern[j][1].append((i,{'type':aType,'uid':connRefOutput}))
        return connectionsInsidePattern

    @handle_exceptions()
    def computePatternInputsAndOutputs(self, aNodeList, connectionsInsidePattern):
        """
        computePatternInputsAndOutputs(aNodeList, connectionsInsidePattern)
        Compute the input and output pins that corresponds to the input and output of the whole pattern.
            - An input pin is connected to a node that does not belong to the pattern.
            - An output pin is never referenced by the connections inside the pattern.

        :param aNodeList: The list of node to take in account.
        :param connectionsInsidePattern: The connections between the nodes inside the pattern, as a list of tuple
            (list of inputs, list of outputs) of the same size than aNodeList, where each element of a list describe
            a connection with three elements:

            - 'index' (index of the connected node)
            - 'identifier' (pin identifier) for input, 'uid' (pin uid) for output
            - 'type' (data type)
        :type aNodeList: list of :class:`.SBSNode`, optional
        :type connectionsInsidePattern: tuple

        :return: The list of input and output pins as a tuple (list of inputs, list of outputs), where each element
            of a list describe a pin with three elements:

            - 'index' (index of the node)
            - 'identifier' (pin identifier) for input, 'uid' (pin uid) for output
            - 'type' (data type)
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if len(aNodeList) != len(connectionsInsidePattern):
            raise SBSImpossibleActionError('Cannot compute inputs and outputs: length of aNodeList and connectionsInsidePattern are not equal')

        # Init result (tuple: (list of inputs, list of outputs))
        patternInputsOutputs = ([],[])

        # Find all nodes that have no outgoing connections, and save each output pin as an output
        for outputIndex in [i for i in range(0,len(aNodeList)) if len(connectionsInsidePattern[i][1]) == 0]:
            if self.mNodeType.__name__ == 'SBSCompNode':
                for output in aNodeList[outputIndex].mCompOutputs:
                    aType = int(output.mCompType)
                    patternInputsOutputs[1].append({'index':outputIndex, 'type':aType, 'uid':output.mUID})
            elif self.mNodeType.__name__ == "SBSParamNode":
                aType = int(aNodeList[outputIndex].getOutputType())
                patternInputsOutputs[1].append({'index':outputIndex, 'type':aType, 'uid':None})
            else:
                nodeDef = aNodeList[outputIndex].getDefinition()
                for output in nodeDef.getAllOutputIdentifiers():
                    aType = aNodeList[outputIndex].getOutputType(output)
                    patternInputsOutputs[1].append({'index':outputIndex, 'type':aType, 'uid':None})


        # Find all nodes having less incoming connections from the pattern than connected input pins, and save each 'not connected' pin as an input
        for i, (aNode, aConn) in enumerate(zip(aNodeList, connectionsInsidePattern)):
            if len(aNode.getConnections()) > len(aConn[0]):

                # For each connections of this node, determine if it is connected to a node inside or outside the pattern
                for aConnInput in aNode.getConnections():
                    aConnInputRef = aConnInput.getConnectedNodeUID()
                    inputNode = next((j for j in aConn[0] if aNodeList[j[0]].mUID == aConnInputRef), None)

                    # This connection comes from outside the pattern => get the input connection info
                    if inputNode is None:
                        aLeftNode = self.getNode(aConnInputRef)
                        if aLeftNode is not None:
                            if self.mNodeType.__name__ == 'SBSCompNode':
                                aType = aLeftNode.getCompOutputType(aConnInput.getConnectedNodeOutputUID())
                            else:
                                aType = aLeftNode.getOutputType()
                            # Save the attributes of this input connection: index, identifier & type
                            patternInputsOutputs[0].append({'index':i, 'identifier': aConnInput.mIdentifier, 'type': aType})

        return patternInputsOutputs

    @handle_exceptions()
    def computeSortedIndicesOfDAG(self, aNodeList, connectionsInsidePattern):
        """
        computeSortedIndicesOfDAG(aNodeList = None)
        Sort topologically the nodes included in the list.

        :param aNodeList: The list of node to take in account for the topological sort.
        :param connectionsInsidePattern: The input and output connections, as a list of tuple (list of inputs, list of outputs)
            of the same size than aNodeList, where each element of a list describe a connection with three elements:

            - 'index' (index of the connected node)
            - 'identifier' (pin identifier) for input, 'uid' (pin uid) for output
            - 'type' (data type)
        :type aNodeList: list of :class:`.SBSNode`.
        :type connectionsInsidePattern: list of tuple
        :return: The sorted node list
        """
        if len(aNodeList) != len(connectionsInsidePattern):
            raise SBSImpossibleActionError('Cannot create iteration: the two provided patterns are not equivalent')

        # Compute incoming degrees (number of incoming connections for each node)
        inDegrees = [len(conn[0]) for conn in connectionsInsidePattern]

        # Reachable nodes are the node with incoming degree equals to 0
        reachableNodes = [(i,aNodeList[i]) for i,deg in enumerate(inDegrees) if deg == 0]

        # Sort the reachable nodes 'lexicographically' to ensure a determinist sort
        reachableNodes = self.sortListLexicographically(reachableNodes)

        # Sort nodes
        sortedIndices = []
        for i in range(len(aNodeList)):
            # Keep the first reachable node
            sortedIndices.append(reachableNodes[0][0])

            # Reduce degree of each node connected to it, and get new reachable nodes
            newReachableNodes = []
            for conn in connectionsInsidePattern[reachableNodes[0][0]][1]:
                inDegrees[conn[0]] -= 1
                if inDegrees[conn[0]] == 0:
                    newReachableNodes.append((conn[0],aNodeList[conn[0]]))
            reachableNodes.pop(0)
            reachableNodes.extend(self.sortListLexicographically(newReachableNodes))

        return sortedIndices

    @handle_exceptions()
    def contains(self, aNode):
        """
        contains(aNode)
        Check if the given node belongs to this node list

        :param aNode: The node to check, as a, object or an UID
        :type aNode: :class:`.SBSCompNode`, :class:`.SBSParamNode` or str
        :return: True if the given node belongs to the node list, False otherwise
        """
        if python_helpers.isStringOrUnicode(aNode):
            return self.getNode(aNode) is not None
        else:
            return aNode in self.getNodeList()

    @handle_exceptions()
    def copyNode(self, aNode):
        """
        copyNode(aNode)
        Create a copy of the given node and generate a new uid for it

        :param aNode: the node to copy
        :type aNode: :class:`.SBSNode`
        :return: The new :class:`.SBSNode` object
        """
        # Create a deep copy of the node
        aNewNode = copy.deepcopy(aNode)

        # Generate a unique uid
        aUID = UIDGenerator.generateUID(self.mParentObject())
        aNewNode.mUID = aUID

        return aNewNode

    @handle_exceptions()
    def duplicateNode(self, aNode, aGUIOffset = None):
        """
        duplicateNode(aNode, aGUIOffset = None)
        Duplicate the given node, generate a new UID and add the node to the same node list than the source node.

        :param aNode: the node to copy (may be identified by its UID)
        :param aGUIOffset: node position offset. Default to [150, 0]
        :type aNode: :class:`.SBSNode` or str
        :type aGUIOffset: list of 2 float, optional
        :return: The new :class:`.SBSNode` object
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIOffset is None: aGUIOffset = [150,0]

        # Get the SBSNode with the given uid
        aNodeUID = None
        if python_helpers.isStringOrUnicode(aNode):
            aNodeUID = aNode
            aNode = self.getNode(aNode)
        if aNode is None:
            raise SBSImpossibleActionError('Cannot duplicate node: Cannot find node '+str(aNodeUID)+' in this graph')

        # Create a copy of this node
        aNewNode = self.copyNode(aNode)
        if aNewNode is None:
            return None

        # Handle GUILayout: position the new node with a horizontal offset from the source node
        if aNewNode.mGUILayout is not None:
            aNewNode.mGUILayout.mGPos[0] += aGUIOffset[0]
            aNewNode.mGUILayout.mGPos[1] += aGUIOffset[1]

        # Add the new node to the Nodes list
        getattr(self.mParentObject(), self.mNodesAttr).append(aNewNode)

        return aNewNode

    @handle_exceptions()
    def deleteNode(self, aNode):
        """
        deleteNode(aNode)
        Allows to delete the given node from the graph.
        It removes it from the nodes list, and delete all the connections from and to that node in the graph.

        :param aNode: The node to remove, as a SBSNode or an UID.
        :type aNode: :class:`.SBSNode` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if python_helpers.isStringOrUnicode(aNode):    aUID = aNode
        else:                                       aUID = aNode.mUID

        aNodeList = self.getNodeList()
        aNode = self.getNode(aUID)
        if aNode is None:
            raise SBSImpossibleActionError('Impossible to delete the node ' + aUID + ', cannot find this node in the graph')

        for aConnectedNode in [aConnectedNode for aConnectedNode in aNodeList if
                               aConnectedNode.isConnectedTo(aLeftNode = aUID)]:
            aConnectedNode.removeConnectionsFrom(aLeftNode = aUID)

        aNodeList.remove(aNode)
        return True

    @handle_exceptions()
    def getNode(self, aNode):
        """
        getNode(aNode)
        Search for the given node in the node list

        :param aNode: node to get, identified by its uid or as a :class:`.SBSNode`
        :type aNode: :class:`.SBSNode` or str
        :return: A :class:`.SBSNode` object if found, None otherwise
        """
        aNodeList = getattr(self.mParentObject(), self.mNodesAttr)
        if python_helpers.isStringOrUnicode(aNode):
            return next((n for n in aNodeList if n.mUID == aNode), None)
        elif aNode not in aNodeList:
            return None
        return aNode

    @handle_exceptions()
    def getNodeList(self, aNodesList = None):
        """
        getNodeList(aNodesList = None)
        Get all the nodes of this NodeList, or look for the given nodes if aNodesList is not None.

        :param aNodesList: The list of node to retrieve. None to retrieve the entire node list.
        :type aNodesList: list of str or list of :class:`.SBSNode`, optional
        :return: A list of :class:`.SBSNode`.
        """
        aNodeList = []
        if aNodesList is None:
            if hasattr(self.mParentObject(), self.mNodesAttr) and getattr(self.mParentObject(), self.mNodesAttr) is not None:
                aNodeList = getattr(self.mParentObject(), self.mNodesAttr)
        else:
            for aNode in aNodesList:
                aNode = self.getNode(aNode)
                if aNode is not None:
                    aNodeList.append(aNode)
        return aNodeList

    @handle_exceptions()
    def getNodesConnectedFrom(self, aNode):
        """
        getNodesConnectedFrom(aNode)
        Get all the nodes connected to an output of the given node.

        :param aNode: the node to consider
        :type aNode: :class:`.SBSNode` or str
        :return: a list of :class:`.SBSNode`
        """
        aNode = self.getNode(aNode)
        aConnectedNodes = []
        if aNode is None:
            return aConnectedNodes

        for n in self.getNodeList():
            if n.isConnectedTo(aLeftNode=aNode):
                aConnectedNodes.append(n)
        return aConnectedNodes

    @handle_exceptions()
    def getNodesConnectedTo(self, aNode, aPinIdentifier=None):
        """
        getNodesConnectedTo(aNode, aPinIdentifier=None)
        Get all the nodes connected to the given pin of the given node.
        If aPinIdentifier is let None, consider all the pins.

        :param aNode: the node to consider
        :param aPinIdentifier: the identifier of the pin to take in account
        :type aNode: :class:`.SBSNode` or str
        :type aPinIdentifier: str, optional
        :return: a list of :class:`.SBSNode`
        """
        connections = self.getConnectionsToNode(aNode, aPinIdentifier)
        connectedNodes = []

        for aConnection in connections:
            aLeftNode = self.getNode(aConnection.getConnectedNodeUID())
            if aLeftNode and aLeftNode not in connectedNodes:
                connectedNodes.append(aLeftNode)
        return connectedNodes

    @handle_exceptions()
    def getConnectionsFromNode(self, aNode):
        """
        getConnectionsFromNode(aNode)
        Get all the connections coming from the given left node.

        :param aNode: the node to consider, as an object or a UID
        :type aNode: :class:`.SBSNode` or str
        :return: a list of :class:`.SBSConnection`
        """
        aConnectedNodes = self.getNodesConnectedFrom(aNode)
        connections = []
        for n in aConnectedNodes:
            connections.extend(n.getConnectionsFromNode(aNode))
        return connections

    @handle_exceptions()
    def getConnectionsToNode(self, aNode, aPinIdentifier=None):
        """
        getConnectionsToNode(self, aNode, aPinIdentifier=None)
        Get the connections incoming to the given node, to a particular input or for all its inputs.

        :param aNode: the node to consider, as an object or a UID
        :param aPinIdentifier: the identifier of the pin to take in account
        :type aNode: :class:`.SBSNode` or str
        :type aPinIdentifier: str, optional
        :return: a list of :class:`.SBSConnection`
        """
        aNode = self.getNode(aNode)
        connections = []
        if aNode is None:
            return connections

        for aConnection in aNode.getConnections():
            aLeftNode = self.getNode(aConnection.getConnectedNodeUID())
            if aLeftNode:
                if aPinIdentifier is None or aConnection.mIdentifier == aPinIdentifier:
                    connections.append(aConnection)
        return connections

    @handle_exceptions()
    def getNodesDockedTo(self, aNode):
        """
        getNodesDockedTo(aNode)
        Get all the nodes that are docked to the given node.

        :param aNode: the node to consider
        :type aNode: :class:`.SBSNode` or str
        :return: a list of :class:`.SBSNode` corresponding to the nodes that are docked to the given node.
        """
        return [aNode for aNode in self.getNodesConnectedTo(aNode) if aNode.isDocked()]

    @handle_exceptions()
    def getRect(self, aNodeList = None):
        """
        getRect(aNodeList = None)
        Get the rectangle occupied by all the nodes in the list, or use only the given nodes if aNodeList is not None

        :param aNodeList: The list of node to take in account for the GUI rectangle. None to consider the node list pointed by itself.
        :type aNodeList: list of str or list of :class:`.SBSNode`, optional
        :return: The rectangle as a :class:`.Rect`
        """
        aNodeList = self.getNodeList(aNodeList)
        if not aNodeList:
            return Rect()

        aRect = aNodeList[0].getRect()
        for aNode in aNodeList[1:]:
            aRect = aRect.union(aNode.getRect())

        return aRect

    @handle_exceptions()
    def isAPathBetween(self, aLeftNode, aRightNode):
        """
        isAPathBetween(self, aLeftNode, aRightNode)
        Check if there is a path from the left node to the right node with the current connections.

        :param aLeftNode: The left node
        :param aRightNode: The right node
        :type aLeftNode: :class:`.SBSNode` or str
        :type aRightNode: :class:`.SBSNode` or str
        :return: True if a path is found, False otherwise
        """
        aLeftNode = self.getNode(aLeftNode)
        aRightNode = self.getNode(aRightNode)
        if not aLeftNode or not aRightNode:
            return False

        # Avoid connecting a node with itself
        if aLeftNode == aRightNode:
            return True

        # Start from the right node and check the connections
        aCheckedNodes = set([])
        aNodesToCheck = set([aRightNode.mUID])
        found = False

        # Build a dictionary for caching node id's to
        # speed up node lookups
        aNodeList = self.getNodeList()
        aNodeCache = {}
        for n in aNodeList:
            aNodeCache[n.mUID] = n

        while not found and len(aNodesToCheck) > 0:
            aNode = aNodeCache[aNodesToCheck.pop()]
            for conn in aNode.getConnections():
                connRefUID = conn.getConnectedNodeUID()
                if connRefUID == aLeftNode.mUID:
                    found = True
                    break
                elif connRefUID not in aCheckedNodes:
                    aNodesToCheck.add(connRefUID)

            aCheckedNodes.add(aNode.mUID)
        return found

    @handle_exceptions()
    def sortListLexicographically(self, aNodeList):
        """
        sortListLexicographically(aNodeList)
        Sort 'lexicographically' the nodes included in the list.
        It uses the node definition to classify the nodes, and the GUI position in case of equality.

        :param aNodeList: The list of node to take in account for the lexicographical sort.
        :type aNodeList: list of tuple(int, :class:`.SBSNode`).
        :return: The sorted node list
        """
        for i, aNode in enumerate(aNodeList):
            j = i
            while j > 0 and aNodeList[j-1][1].classify(aNodeList[j][1], self.mParentObject()) > 0:
                aNodeList[j], aNodeList[j-1] = aNodeList[j-1], aNodeList[j]
                j -= 1
        return aNodeList

    @handle_exceptions()
    def sortNodesAsDAG(self, aUpdateNodeListMember = True):
        """
        sortNodesAsDAG(aUpdateNodeListMember = True)
        Sort the node list of the graph to order them as a DAG. The node list is updated and returned.

        :param aUpdateNodeListMember: True to update the node list member with the sorted nodes, False to just get the sorted list. Default to True.
        :type aUpdateNodeListMember: bool
        :return: the sorted node list.
        """
        aNodeList = self.getNodeList()

        # Get the list of connections inside the graph
        graphConnections = self.computeConnectionsInsidePattern(aNodeList)

        # Sort the node list as a DAG
        sortedIndices = self.computeSortedIndicesOfDAG(aNodeList, graphConnections)
        assert (len(sortedIndices) == len(aNodeList))

        sortedNodeList = [aNodeList[index] for index in sortedIndices]
        if aUpdateNodeListMember:
            setattr(self.mParentObject(), self.mNodesAttr, sortedNodeList)
        return sortedNodeList
