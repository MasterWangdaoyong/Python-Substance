"""
Module **ag_layout** provides the definition of the functions :func:`.layoutGraph`,
and :func:`.layoutDoc` for automatically organizing the nodes in a graph or all graphs
in a document respectively.
"""
import abc
from pysbs import sbsenum
from pysbs.graph import SBSGraph, SBSFunction
from pysbs.params import SBSDynamicValue
from pysbs.compnode import SBSParamsGraph
from pysbs.mdl import MDLGraph
from pysbs.api_decorators import doc_source_code_enum
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.api_decorators import doc_inherit
from pysbs.sbslibrary import getCompNodeInput, getCompNodeOutput


@doc_source_code_enum
class NodesToKeepEnum:
    """
    Enumeration of what nodes to keep when laying out a graph
    """
    KEEP_ALL_NODES, \
    KEEP_COMPUTED_NODES, \
    KEEP_COMPUTED_AND_INPUT_NODES, \
        = range(3)


@doc_source_code_enum
class GUIElementsToKeepEnum:
    """
    Enumeration treatments of gui elements when laying out a graph
    """
    KEEP_ALL, \
    KEEP_NONE, \
    KEEP_NON_EMPTY, \
        = range(3)


@doc_source_code_enum
class GraphFlowDirectionEnum:
    """
    Enumeration layout directions for graphs
    """
    RIGHTWARD, \
    UPWARD, \
        = range(2)


@doc_source_code_enum
class GraphLayoutAlignment:
    """
    Enumeration what side of a graph to align when laying out a graph
    """
    OUTPUTS, \
    INPUTS, \
        = range(2)


@doc_inherit
class _NodeFinder(object):
    """
    Helps looking up nodes in graphs of many types based on various criteria
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, graph, flowDirection=GraphFlowDirectionEnum.RIGHTWARD):
        self.graph = graph
        self.flowDirection = flowDirection
        self.uidToNodeCache = {node.mUID: node for node in self.graph.getNodeList()}
        self.childUIDCache = {}
        self.parentUIDCache = {}
        self.definitionCache = {node.mUID: node.getDefinition() for node in self.graph.getNodeList()}
        self.isFXMap = isinstance(graph, SBSParamsGraph)
        nodeToInputMap = {}
        nodeToOutputMap = {}

        # Create fast ways of figuring what input and output pins are connected to what node
        for node in self.graph.getNodeList():
            # Make sure we have an entry for each node in both the child and parent caches
            nodeToInputMap.setdefault(node.mUID, {})
            nodeToOutputMap.setdefault(node.mUID, {})

            # Loop over all input connections
            for c in node.getConnections():
                parentUID = c.mConnRef
                parentNode = self.uidToNodeCache[parentUID]
                parentOutputName = self._getOutputName(parentNode, c.mConnRefOutput)
                if self.isFXMap:
                    nodeToOutputMap.setdefault(node.mUID, {}).setdefault(c.mIdentifier, []).append(parentUID)
                    nodeToInputMap.setdefault(parentUID, {}).setdefault(parentOutputName, []).append(node.mUID)
                else:
                    nodeToInputMap.setdefault(node.mUID, {}).setdefault(c.mIdentifier, []).append(parentUID)
                    nodeToOutputMap.setdefault(parentUID, {}).setdefault(parentOutputName, []).append(node.mUID)

        # Now build a cache of sorted connections for each node uid
        for node in self.graph.getNodeList():
            # Input/parents
            self.parentUIDCache[node.mUID] = []
            nodeDef = self.definitionCache[node.mUID]
            inputToNodeUIDMap = nodeToInputMap[node.mUID]
            knownInputs = set()
            for input in nodeDef.getAllInputs():
                idStr = input.getIdentifierStr()
                if idStr in inputToNodeUIDMap:
                    connectedNodeUIDs = inputToNodeUIDMap[idStr]
                    for connectedNodeUID in connectedNodeUIDs:
                        if connectedNodeUID not in knownInputs:
                            self.parentUIDCache[node.mUID].append(connectedNodeUID)
                            knownInputs.add(connectedNodeUID)

            # Output/children
            self.childUIDCache[node.mUID] = []
            outputToNodeUIDMap = nodeToOutputMap[node.mUID]
            knownOutputs = set()
            for output in nodeDef.getAllOutputs():
                idStr = output.getIdentifierStr()
                if idStr in outputToNodeUIDMap:
                    connectedNodeUIDs = outputToNodeUIDMap[idStr]
                    for connectedNodeUID in connectedNodeUIDs:
                        if connectedNodeUID not in knownOutputs:
                            self.childUIDCache[node.mUID].append(connectedNodeUID)
                            knownOutputs.add(connectedNodeUID)
        # swap children an parent caches for FX maps
        if self.isFXMap:
            self.parentUIDCache, self.childUIDCache = self.childUIDCache, self.parentUIDCache

    def _getOutputName(self, parentNode, connectionRef):
        if connectionRef is None:
            # This suggest we have a node type where there is only one
            # output/input. With the current graphs it means it's called
            # input in case we are dealing with an FXMap, otherwise it's called
            # output
            return getCompNodeInput(sbsenum.InputEnum.INPUT) if self.isFXMap else getCompNodeOutput(sbsenum.OutputEnum.OUTPUT)
        else:
            return parentNode.getCompOutputIdentifier(aCompOutputUID=connectionRef)


    @abc.abstractmethod
    def findInputNodeUids(self):
        """
        Returns all input node uid's
        :return: list of int
        """
        pass

    @abc.abstractmethod
    def findOutputNodeUids(self):
        """
        Returns all output node uid's
        :return: list of int
        """
        pass

    def getParentUidsOfNode(self, node):
        """
        Returns node uid's of nodes upstream from compNode
        :param node: The node to start the search from
        :type node: :class:`.SBSCompNode` or :class:`.SBSParamNode` or :class:`.SBSParamsGraphNode`
        :return: list of int
        """
        return self.parentUIDCache[node.mUID]

    def getChildrenUidsOfNode(self, node):
        """
        Returns node uid's of nodes downstream from compNode
        :param node: The node to start the search from
        :type node: :class:`.SBSCompNode` or :class:`.SBSParamNode` or :class:`.SBSParamsGraphNode`
        :return: list of int
        """
        return self.childUIDCache[node.mUID]

    def findNodeUids(self):
        """
        Gets uid's for all nodes in the graph
        :return: list of string
        """
        return list(self.uidToNodeCache.keys())

    def findRootUids(self):
        """
        Gets uid's for all nodes with no parents
        :return: list of string
        """
        return [node.mUID for node in self.graph.getNodeList() if len(self.parentUIDCache[node.mUID]) == 0]

    def findLeafUids(self):
        """
        Gets uid's for all nodes with no children
        :return: list of string
        """
        return [node.mUID for node in self.graph.getNodeList() if len(self.childUIDCache[node.mUID]) == 0]

    def findStartNodeUids(self, fromIO, layoutAlignment):
        """
        Finds nodes to start from based on the traversal direction and whether to use only inputs/outputs or
        all nodes as starting points
        :param fromIO: Whether all nodes or just input/output nodes are considered starting nodes
        :type fromIO: bool
        :param layoutAlignment: Enum selecting whether to traverse from inputs or outputs
        :type layoutAlignment: :class:`.GraphLayoutAlignment`
        :return: list of string representing uid's for the starting nodes
        """
        if layoutAlignment == GraphLayoutAlignment.OUTPUTS:
            if fromIO:
                outputNodes = self.findOutputNodeUids()
                if len(outputNodes) == 0:
                    raise SBSImpossibleActionError('No output node found on graph')
                return outputNodes
            else:
                return self.findLeafUids()
        else:
            return self.findInputNodeUids() if fromIO else self.findRootUids()

    def findEndNodeUids(self, fromIO, layoutAlignment):
        """
        Finds nodes where the graph ends from based on the traversal direction and whether to use only inputs/outputs or
        all nodes as starting points
        :param fromIO: Whether all nodes or just input/output nodes are considered starting nodes
        :type fromIO: bool
        :param layoutAlignment: Enum selecting whether to traverse from inputs or outputs
        :type layoutAlignment: :class:`.GraphLayoutAlignment`
        :return: list of string representing uid's for the ending nodes
        """
        return self.findStartNodeUids(fromIO,
                                      GraphLayoutAlignment.OUTPUTS if layoutAlignment == GraphLayoutAlignment.INPUTS else GraphLayoutAlignment.INPUTS)

    def findNextNodeUids(self, node, layoutAlignment):
        """
        Find nodes upstream given the current search direction
        :param node: The node to search from
        :type node: :class:`.SBSCompNode` or :class:`.SBSParamNode` or :class:`.SBSParamsGraphNode`
        :param layoutAlignment: Enum selecting whether to traverse from inputs or outputs
        :type layoutAlignment: :class:`.GraphLayoutAlignment`
        :return: list of str representing node uid's
        """
        return self.getParentUidsOfNode(
            node) if layoutAlignment == GraphLayoutAlignment.OUTPUTS else self.getChildrenUidsOfNode(node)

    def getNodeBreadth(self, node, nodeSpacing):
        """
        Get the width of of a node including its node spacing
        :param node: The node to operatoe on
        :type node: :class:`.SBSCompNode` or :class:`.SBSParamNode` or :class:`.SBSParamsGraphNode`
        :param nodeSpacing: the requested spacing for the node
        :type nodeSpacing: int
        :return: int
        """
        rect = node.getRect()
        return int(rect.mHeight - rect.mWidth + nodeSpacing)

    def findAncestorsOfOutputs(self):
        """
        Return the pair of two sets, the first containing uid nodes that are ancestor of one output and children of the roots,
        i.e. have a chain of parents from some output to them, the second containing uid of other nodes.
        """
        rootUids = self.findRootUids()
        outputUids = self.findOutputNodeUids()
        if len(outputUids) == 0:
            raise SBSImpossibleActionError('No output node found on graph')

        nodeUids = [node.mUID for node in self.graph.getNodeList()]

        def descend(nodeUid, _visited):
            if nodeUid in outputUids:
                ioRelated = True
            else:
                ioRelated = False
                node = self.graph.getNode(nodeUid)
                for subNodeUid in self.getChildrenUidsOfNode(node):
                    if subNodeUid in _visited:
                        ioRelated = _visited[subNodeUid] or ioRelated  # order is important !
                    else:
                        ioRelated = descend(subNodeUid, _visited) or ioRelated

            _visited[nodeUid] = ioRelated
            return ioRelated

        visited = {}
        for iNodeUid in rootUids:
            descend(iNodeUid, visited)

        selected = [uid for uid in nodeUids if visited[uid]]
        discarded = [uid for uid in nodeUids if not visited[uid]]
        return selected, discarded

    def findNodeFromUID(self, uid):
        return self.uidToNodeCache[uid]


@doc_inherit
class _CompNodeFinder(_NodeFinder):
    """
    Implementation of :class:`_NodeFinder` for comp nodes
    """

    def __init__(self, graph):
        _NodeFinder.__init__(self, graph)

    def findInputNodeUids(self):
        return [node.mUID for node in self.graph.getAllInputNodes()]

    def findOutputNodeUids(self):
        return [node.mUID for node in self.graph.getAllOutputNodes()]


@doc_inherit
class _FuncNodeFinder(_NodeFinder):
    """
    Implementation of :class:`_NodeFinder` for function graph nodes
    """

    def __init__(self, graph):
        _NodeFinder.__init__(self, graph)

    def findInputNodeUids(self):
        uids = []
        functionInputTypes = {
            sbsenum.FunctionEnum.GET_BOOL,
            sbsenum.FunctionEnum.GET_INTEGER1,
            sbsenum.FunctionEnum.GET_INTEGER2,
            sbsenum.FunctionEnum.GET_INTEGER3,
            sbsenum.FunctionEnum.GET_INTEGER4,
            sbsenum.FunctionEnum.GET_FLOAT1,
            sbsenum.FunctionEnum.GET_FLOAT2,
            sbsenum.FunctionEnum.GET_FLOAT3,
            sbsenum.FunctionEnum.GET_FLOAT4,
            sbsenum.FunctionEnum.GET_STRING,
        }
        for node in self.graph.getNodeList():
            functionType = self.definitionCache[node.mUID].getIdentifier()
            if functionType in functionInputTypes:
                uids.append(node.mUID)
        return uids

    def findOutputNodeUids(self):
        output_node = self.graph.getOutputNode()
        if output_node is None:
            return []
        return [output_node.mUID]


@doc_inherit
class _ParamNodeFind(_NodeFinder):
    """
    Implementation of :class:`_NodeFinder` for param graphs
    """

    # Note: the layout algorithm is designed to preserve the outputs.
    # In the case of fx-maps, though, we want to preserve the "Root" and define it as the "output" of the graph.
    # That has the unfortunate side effect of reversing the meaning of parents,
    # where the fx node children are the parents for the layout algorithm and conversely.
    def __init__(self, graph):
        _NodeFinder.__init__(self, graph, GraphFlowDirectionEnum.UPWARD)

    def findInputNodeUids(self):
        # There are No input nodes in the graph
        # However, FX map inputs may be sampled in their dynamic values
        # So for now, we'll assume all executed nodes are inputs.
        return self.findAncestorsOfOutputs()[0]

    def findOutputNodeUids(self):
        if self.graph.mRootNode is None:
            return []
        return [self.graph.mRootNode]


@doc_inherit
class _MDLNodeFinder(_NodeFinder):
    """
    Implementation of :class:`_NodeFinder` for comp nodes
    """

    def __init__(self, graph):
        _NodeFinder.__init__(self, graph)

    def findInputNodeUids(self):
        inputNodes = self.graph.getAllInputs()
        return [node.mUID for node in inputNodes]

    def findOutputNodeUids(self):
        output_node = self.graph.getGraphOutput()
        if output_node is None:
            return []
        return [output_node.mUID]


def _createNodeFinder(graph):
    """
    Creates the appropriate node finder based on the graph type
    :param graph: The graph to create a node finder
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:`.MDLGraph`
    :return: :class:`_NodeFinder` The nodefinder for the graph
    """
    if isinstance(graph, SBSGraph):
        return _CompNodeFinder(graph)

    elif isinstance(graph, SBSFunction):
        return _FuncNodeFinder(graph)

    elif isinstance(graph, SBSDynamicValue):
        return _FuncNodeFinder(graph)

    elif isinstance(graph, SBSParamsGraph):
        return _ParamNodeFind(graph)

    elif isinstance(graph, MDLGraph):
        return _MDLNodeFinder(graph)

    raise SBSImpossibleActionError("Cannot create a _NodeFinder for invalid graph of type %s" % (type(graph)))


def _clearNodes(
        graph,
        nodesToKeep):
    """
    Clears nodes in a graph according to the supplied rule

    :param graph: The graph to clear nodes in
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :param nodesToKeep: Rule for what nodes to keep
    :type nodesToKeep: :class:`NodeToKeepEnum`
    :return: list of int, the uid's of the nodes kept
    """
    nf = _createNodeFinder(graph)
    if nodesToKeep == NodesToKeepEnum.KEEP_ALL_NODES:
        nodesToKeepList, nodesToRemove = nf.findNodeUids(), []

    elif nodesToKeep == NodesToKeepEnum.KEEP_COMPUTED_NODES:
        nodesToKeepList, nodesToRemove = nf.findAncestorsOfOutputs()

    elif nodesToKeep == NodesToKeepEnum.KEEP_COMPUTED_AND_INPUT_NODES:
        nodesToKeepList, nodesToRemove = nf.findAncestorsOfOutputs()
        # Make all inputs are kept
        # Use a set for lookup in case the nodes to keep list is long
        nodesToKeepSet = set(nodesToKeepList)
        for inputNode in nf.findInputNodeUids():
            if inputNode not in nodesToKeepSet:
                nodesToKeepList.append(inputNode)
                nodesToRemove.remove(inputNode)

    else:
        raise SBSImpossibleActionError("Invalid enum value for nodesToKeep: %s" % nodesToKeep)

    for uid in nodesToRemove:
        graph.deleteNode(uid)

    return nodesToKeepList


def _computeMaxDepths(
        nodeUidToMaxDepth,
        nodeUID,
        nodeFinder,
        layoutAlignment=GraphLayoutAlignment.OUTPUTS):
    """
    Compute maximum depth of the node with the uid nodeUID and all its descendants
    :param nodeUidToMaxDepth: Current max depths
    :type nodeUidToMaxDepth: dict from string to max depths
    :param nodeUID: The node id to compute max depth from
    :type nodeUID: string
    :param nodeFinder: Nodefinder initialized for the graph
    :type nodeFinder: :class:`_NodeFinder`
    :param layoutAlignment: Enum selecting whether to traverse from inputs or outputs. I.E compute depths from inputs/roots or from outputs/roots
    :type layoutAlignment: :class:`.GraphLayoutAlignment`
    :return: None
    """

    def _computeMaxDepths_impl(previous_level, depth):
        next_level = set([])
        for uid in previous_level:
            if uid not in nodeUidToMaxDepth or depth > nodeUidToMaxDepth[uid]:
                nodeUidToMaxDepth[uid] = depth
            for childUid in nodeFinder.findNextNodeUids(nodeFinder.findNodeFromUID(uid), layoutAlignment):
                next_level.add(childUid)
        if len(next_level) != 0:
            _computeMaxDepths_impl(next_level, depth + 1)

    _computeMaxDepths_impl({nodeUID}, 0)


def _computePositions(
        nodeUidToPosition,
        graph,
        nodeUID,
        nodeUidToMaxDepth,
        nodeFinder,
        aNodeSpacing=160,
        aNodeShift=(80, 0),
        layoutAlignment=GraphLayoutAlignment.OUTPUTS):
    """
    Compute new node positions for the nodes in a graph
    :param nodeUidToPosition: Mapping of nodes to current positions
    :type nodeUidToPosition: dict of string to tuple of int
    :param graph: The graph to compute node positions in
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :param nodeUID: The node uid to compute position for
    :type nodeUID: string
    :param nodeUidToMaxDepth: Mapping from node uid to its max depths
    :type nodeUidToMaxDepth: dict from string to int
    :param nodeFinder: Nodefinder initialized for the graph
    :type nodeFinder: :class:`_NodeFinder`
    :param aNodeSpacing: Spacing between nodes
    :type aNodeSpacing: int
    :param aNodeShift: The distance to keep between nodes
    :type aNodeShift: tuple of int
    :param layoutAlignment: Enum selecting whether to traverse from inputs or outputs
    :type layoutAlignment: :class:`.GraphLayoutAlignment`
    :return: float the x location of the node.
    """
    depth_direction_sign = -1 if layoutAlignment == GraphLayoutAlignment.OUTPUTS else 1

    def _computePositions_impl(uid, shift, depth):
        # Note: breadth is computed in pixels, while depth is computed in number of nodes
        # already set the node currently being treated to Avoid cycles when doing the recursive call
        nodeUidToPosition[uid] = (-1, -1)
        children_breadth = 0
        for childUid in nodeFinder.findNextNodeUids(graph.getNode(uid), layoutAlignment):
            if childUid in nodeUidToPosition or nodeUidToMaxDepth[childUid] != depth + 1:
                continue
            children_breadth += _computePositions_impl(childUid, shift + children_breadth, depth + 1)
        thisNodeBreadth = nodeFinder.getNodeBreadth(graph.getNode(uid), aNodeSpacing)
        breadth = max(children_breadth, thisNodeBreadth)
        nodeUidToPosition[uid] = (depth_direction_sign * depth * aNodeSpacing + aNodeShift[0],
                                  shift + breadth // 2 + aNodeShift[1])
        return breadth

    return _computePositions_impl(nodeUID, shift=0, depth=0)


def _getNodesUnderFrames(graph):
    """
    Get all frames associated with a list of the nodes under the frame
    :param graph: The graph to get the frames for
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :return: a dict of string to list of strings representing the uid of frames and what nodes they are associated with
    """
    frameUidToNodeUidList = {}
    for frame in graph.getAllFrames():
        frameUid = frame.mUID
        nodesUIDs = [node.mUID for node in graph.getNodesInFrame(frame)]
        frameUidToNodeUidList[frameUid] = nodesUIDs
    return frameUidToNodeUidList


def _reframeAllFramesAroundNodes(
        frameUidtoNodeUidList,
        graph):
    """
    Reframes all frames to contain the nodes they used to contain after a layout

    :param frameUidtoNodeUidList: Dict of frame uuids with a list of node uuids in
    :type frameUidtoNodeUidList: dict of string to list of strings
    :param graph: The graph to reframe nodes in
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :return: tuple of list of frames that were resized and a list of frames that were left untouched
    """
    resizedFrames = []
    unresizedFrames = []
    for frame in graph.getAllFrames():
        nodeUIDs = frameUidtoNodeUidList[frame.mUID]
        if nodeUIDs:
            graph.reframeAroundNodes(frame, [graph.getNode(nodeUID) for nodeUID in nodeUIDs])
            resizedFrames.append(frame)
        else:
            unresizedFrames.append(frame)
    return resizedFrames, unresizedFrames


def _stackGUIObjects(
        guiObjectList,
        nodeFinder,
        position=(0, 0, 0),
        minimalShift=8):
    """
    Stack each gui object in the input list on top of each other and return the position the next possible ui
    object can be stacked to avoid overlaps
    :param guiObjectList:
    :type guiObjectList: list of :class:`.guiObject`
    :param nodeFinder: Nodefinder initialized for the graph
    :type nodeFinder: :class:`_NodeFinder`
    :param position: Position (x, y, depth) of the gui objects to be stacked
    :type position: tuple of int
    :param minimalShift: Minimal distance between nodes
    :type minimalShift: int
    :return: tuple of int the position for the stacked objects?
    """
    if nodeFinder.flowDirection == GraphFlowDirectionEnum.RIGHTWARD:
        increment_index = 1
        increment_sign = 1
    elif nodeFinder.flowDirection == GraphFlowDirectionEnum.UPWARD:
        increment_index = 0
        increment_sign = -1

    position = list(position)  # make a (shallow) copy
    for guiObject in guiObjectList:
        rect = guiObject.getRect()
        position[increment_index] += increment_sign * max(rect.mHeight, minimalShift)
        guiObject.mGUILayout.mGPos = list(position)
    return position


def _deleteFrames(guiObjectList, graph):
    """
    Deletes all frames in a graph

    :param guiObjectList: List of all gui objects in a graph
    :type guiObjectList: list of :class:`.guiObject`
    :param graph: The graph to delete the the frames from
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :return: None
    """
    for guiObject in guiObjectList:
        graph.deleteFrame(guiObject)


def _deleteComments(guiObjectList, graph):
    """
    Deletes all comments in a graph

    :param guiObjectList: List of all gui objects in a graph
    :type guiObjectList: list of :class:`.guiObject`
    :param graph: The graph to delete the the comments from
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :return: None
    """
    for guiObject in guiObjectList:
        graph.deleteComment(guiObject)


def _deleteNavigationPins(guiObjectList, graph):
    """
    Deletes all navigation pins in a graph

    :param guiObjectList: List of all gui objects in a graph
    :type guiObjectList: list of :class:`.guiObject`
    :param graph: The graph to delete the the navigation pins from
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :return: None
    """
    for guiObject in guiObjectList:
        graph.deleteNavigationPin(guiObject)


def layoutGraph(
        graph,
        aNodeSpacing=160,
        aNodeShift=(80, 0),
        nodesToKeep=NodesToKeepEnum.KEEP_ALL_NODES,
        layoutAlignment=GraphLayoutAlignment.OUTPUTS,
        commentsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
        framesToKeep=GUIElementsToKeepEnum.KEEP_ALL,
        navigationPinsToKeep=GUIElementsToKeepEnum.KEEP_ALL):
    """
    Lays out a graph

    :param graph: graph to layout
    :type graph: :class:`.SBSDynamicValue` or :class:`.SBSGraph` or :class:`.SBSFunction` or :class:`.SBSParamsGraph` or :class:.`MDLGraph`
    :param aNodeSpacing: distance to keep between nodes when laying them out
    :type aNodeSpacing: int
    :param aNodeShift: Start position for the laid out graph
    :type aNodeShift: tuple of int
    :param nodesToKeep: What nodes to keep in the graph
    :type nodesToKeep: :class:`.NodesToKeepEnum`
    :param layoutAlignment: Enum selecting whether to traverse from inputs or outputs
    :type layoutAlignment: :class:`.GraphLayoutAlignment`
    :param commentsToKeep: Whether to delete or keep comments
    :type commentsToKeep: :class:`.GUIElementsToKeepEnum`
    :param framesToKeep: Whether to delete or keep frames
    :type framesToKeep: :class:`.GUIElementsToKeepEnum`
    :param navigationPinsToKeep: Whether to delete or keep navigation pins
    :type navigationPinsToKeep: :class:`.GUIElementsToKeepEnum`
    :return: None
    """

    nodesToKeep = _clearNodes(graph, nodesToKeep)

    nf = _createNodeFinder(graph)
    startNodes = nf.findStartNodeUids(fromIO=False, layoutAlignment=layoutAlignment)

    frameUidToNodeUidList = _getNodesUnderFrames(graph)

    nodeUidToMaxDepth = {}
    nodeUidToPosition = {}

    for startUID in startNodes:
        if startUID not in nodeUidToMaxDepth:
            _computeMaxDepths(
                nodeUidToMaxDepth,
                startUID,
                nf,
                layoutAlignment=layoutAlignment)

    breadthShift = 0
    for startUID in startNodes:
        if startUID not in nodeUidToPosition:
            breadthShift += _computePositions(
                nodeUidToPosition,
                graph,
                startUID,
                nodeUidToMaxDepth,
                nf,
                aNodeSpacing=aNodeSpacing,
                aNodeShift=(aNodeShift[0], aNodeShift[1] + breadthShift),
                layoutAlignment=layoutAlignment)

    for uid in nodesToKeep:
        x, y = nodeUidToPosition[uid]
        if nf.flowDirection == GraphFlowDirectionEnum.UPWARD:
            x, y = y, -x
        node = graph.getNode(uid)
        node.setPosition([x, y, 0])

    stackPosition = (0, breadthShift, 0)
    if commentsToKeep is GUIElementsToKeepEnum.KEEP_NONE:
        _deleteComments(graph.getAllComments(), graph)
    else:
        stackPosition = _stackGUIObjects(graph.getAllComments(), nf, stackPosition)

    if not (isinstance(graph, SBSFunction) or isinstance(graph, SBSParamsGraph) or isinstance(graph, SBSDynamicValue)):
        if navigationPinsToKeep is GUIElementsToKeepEnum.KEEP_NONE:
            _deleteNavigationPins(graph.getAllNavigationPins(), graph)
        else:
            stackPosition = _stackGUIObjects(graph.getAllNavigationPins(), nf, stackPosition)

    if framesToKeep is GUIElementsToKeepEnum.KEEP_NON_EMPTY:
        resizedFrames, unresizedFrames = _reframeAllFramesAroundNodes(frameUidToNodeUidList, graph)
        _deleteFrames(unresizedFrames, graph)

    elif framesToKeep is GUIElementsToKeepEnum.KEEP_NONE:
        _deleteFrames(frameUidToNodeUidList.keys(), graph)

    else:
        resizedFrames, unresizedFrames = _reframeAllFramesAroundNodes(frameUidToNodeUidList, graph)
        stackPosition = _stackGUIObjects(unresizedFrames, nf, stackPosition)


def layoutDoc(
        sbsDoc,
        aNodeSpacing=160,
        aNodeShift=(80, 0),
        nodesToKeep=NodesToKeepEnum.KEEP_ALL_NODES,
        layoutAlignment=GraphLayoutAlignment.OUTPUTS,
        commentsToKeep=GUIElementsToKeepEnum.KEEP_ALL,
        framesToKeep=GUIElementsToKeepEnum.KEEP_ALL,
        navigationPinsToKeep=GUIElementsToKeepEnum.KEEP_ALL):
    """
    Layout all graphs in an sbs document

    :param sbsDoc: Document to layout
    :type sbsDoc:
    :param aNodeSpacing: distance to keep between nodes when laying them out
    :type aNodeSpacing: int
    :param aNodeShift: Start position for the laid out graphs
    :type aNodeShift: tuple of int
    :param nodesToKeep: What nodes to keep in the graph
    :type nodesToKeep: :class:`.NodesToKeepEnum`
    :param layoutAlignment: Enum selecting whether to traverse from inputs or outputs
    :type layoutAlignment: :class:`.GraphLayoutAlignment`
    :param commentsToKeep: Whether to delete or keep comments
    :type commentsToKeep: :class:`.GUIElementsToKeepEnum`
    :param framesToKeep: Whether to delete or keep frames
    :type framesToKeep: :class:`.GUIElementsToKeepEnum`
    :param navigationPinsToKeep: Whether to delete or keep navigation pins
    :type navigationPinsToKeep: :class:`.GUIElementsToKeepEnum`
    :return: None
    """
    all_graphs = sbsDoc.getSBSGraphList()
    all_graphs += sbsDoc.getMDLGraphList()
    all_graphs += sbsDoc.getSBSFunctionList()
    graphs_with_dyn_params = sbsDoc.getSBSGraphList()

    for comp_graph in sbsDoc.getSBSGraphList():
        for node in comp_graph.getNodeList():
            if node.isAFxMap() and node.getFxMapGraph() is not None:
                fx_graph = node.getFxMapGraph()
                all_graphs.append(fx_graph)
                graphs_with_dyn_params.append(fx_graph)
            elif node.isAPixelProcessor():
                pp_fun = node.getPixProcFunction(createIfEmtpy=False)
                if pp_fun:
                    all_graphs.append(pp_fun)
    for graph in graphs_with_dyn_params:
        for node in graph.getNodeList():
            for dyn_param in node.getDynamicParameters():
                all_graphs.append(dyn_param.getDynamicValue())

    caughtFailures = []
    for graph in all_graphs:
        try:
            layoutGraph(
                graph,
                aNodeSpacing,
                aNodeShift,
                nodesToKeep,
                layoutAlignment,
                commentsToKeep,
                framesToKeep,
                navigationPinsToKeep,
            )
        except SBSImpossibleActionError:
            caughtFailures.append(graph)
    if len(caughtFailures) > 0:
        names = [graph.mIdentifier if hasattr(graph, 'mIdentifier') else str(graph.__class__) for graph in caughtFailures]
        raise SBSImpossibleActionError('Layout failures in graphs: ' +
                                       ' '.join(names))
