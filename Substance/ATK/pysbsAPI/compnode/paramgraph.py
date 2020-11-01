# coding: utf-8
"""
| Module **paramgraph** provides the definition of all the objects relative to a FxMap graph:
| - :class:`.SBSParamsGraphData`
| - :class:`.SBSParamsGraphNode`
| - :class:`.SBSParamsGraph`
"""
from __future__ import unicode_literals
import copy
import weakref

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import UIDGenerator, SBSObject
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import sbscommon
from pysbs import params

from .common import SBSCompImplWithParams


# ==============================================================================
@doc_inherit
class SBSParamsGraphData(SBSCompImplWithParams):
    """
    Class that contains information on a paramsGraphData as defined in a .sbs file.
    Refers to parameter set of FxMaps.

    Members:
        * mIdentifier  (str): data identifier.
        * mUID         (str): data unique identifier in the /paramsGraphDatas/ context.
        * mType        (str, optional): node type, among the list of available FxMap node identifiers (:mod:`.sbsfxmapnodes`)
        * mInherit     (str, optional): uid of the inherited data if exists (/paramsGraphData/uid).
        * mParameters  (list of :class:`.SBSParameter`): parameters definition.
    """
    def __init__(self,
                 aIdentifier = '',
                 aUID        = '',
                 aType       = '',
                 aInherit    = None,
                 aParameters = None):
        super(SBSParamsGraphData, self).__init__(aParameters)
        self.mParameters = None if self.mParameters == [] else self.mParameters     # Overload mParameters initialization
        self.mIdentifier    = aIdentifier
        self.mUID           = aUID
        self.mType          = aType
        self.mInherit       = aInherit

        self.mMembersForEquality = ['mIdentifier',
                                    'mType',
                                    'mInherit',
                                    'mParameters']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSParamsGraphData, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'identifier')
        self.mUID        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'uid'       )
        self.mType       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'type'      )
        self.mInherit    = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'inherit'   )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIdentifier , 'identifier' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUID        , 'uid'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mType       , 'type'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mInherit    , 'inherit'    )
        aSBSWriter.writeListOfSBSNode(aXmlNode       ,  self.mParameters , 'parameters' , 'parameter'  )

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the FxMap node definition (Inputs, Outputs, Parameters)

        :return: a :class:`.CompNodeDef` object
        """
        return sbslibrary.getFxMapNodeDefinition(self.mType)

    @handle_exceptions()
    def getDisplayName(self):
        return 'FxMap node '+self.mType+' ('+self.mUID+')'

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        """
        setParameterValue(aParameter, aParamValue)
        Set the value of the given parameter to the given value, if compatible with this type of FxMap graph node

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aParamValue: :class:`.SBSDynamicValue` or any parameter type
        :return: True if succeed, False otherwise
        """
        return super(SBSParamsGraphData, self).setParameterValue(aParameter, aParamValue,
                                                                 aRelativeTo = sbsenum.ParamInheritanceEnum.ABSOLUTE)

    @handle_exceptions()
    def unsetParameter(self, aParameter):
        """
        unsetParameter(aParameter)
        Unset the given parameter so that it is reset to its default value.

        :param aParameter: identifier of the parameter to set
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: True if succeed, False otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        return super(SBSParamsGraphData, self).unsetParameter(aParameter)


# ==============================================================================
@doc_inherit
class SBSParamsGraphNode(sbscommon.SBSNode):
    """
    Class that contains information on a paramsGraphNode as defined in a .sbs file
    Refers to a FxMap graph node.

    Members:
        * mGUIName     (str): name of the node.
        * mUID         (str): node unique identifier in the /paramsGraphNodes/ context.
        * mType        (str): node type, among the identifiers available for the FxMap node definition (:mod:`.sbsfxmapnodes`)
        * mDisabled    (str, optional): this node is disabled ("1" / None).
        * mConnections (list of :class:`.SBSConnection`): input (parameter of type ENTRY_PARAMETER) connections list. connRef are nodes unique identifier references (/paramsGraphNode/uid).
        * mData        (str): uid of the data associated to this node (/paramsGraph/paramsGraphDatas/), where the parameters are defined.
        * mGUILayout   (:class:`.SBSGUILayout`): GUI position/options.
    """
    def __init__(self,
                 aGUIName     = None,
                 aUID         = '',
                 aType        = '',
                 aDisabled    = None,
                 aConnections = None,
                 aData        = '',
                 aGUILayout   = None,
                 aParentGraph = None):
        super(SBSParamsGraphNode, self).__init__(aGUIName, aUID, aDisabled, aConnections, aGUILayout)
        self.mType          = aType
        self.mData          = aData
        self.mParentGraph = weakref.ref(aParentGraph) if aParentGraph is not None else None

        self.mMembersForEquality.append('mType')

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSParamsGraphNode, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mType          = aSBSParser.getXmlElementVAttribValue(aXmlNode , 'type' )
        self.mData          = aSBSParser.getXmlElementVAttribValue(aXmlNode , 'data' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mGUIName    , 'GUIName'    )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mUID        , 'uid'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mType       , 'type'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mDisabled   , 'disabled'   )
        aSBSWriter.writeListOfSBSNode(aXmlNode        , self.mConnections, 'connections' , 'connection' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mData       , 'data'       )
        aSBSWriter.writeSBSNode(aXmlNode              , self.mGUILayout  , 'GUILayout'  )

    def hasAReferenceOnDependency(self, aDependency):
        return False

    def hasAReferenceOnInternalPath(self, aInternalPath):
        return False

    @handle_exceptions()
    def getData(self):
        """
        getData()
        Get the data associated to this node

        :return: a :class:`.SBSParamsGraphData` object if found, None otherwise
        """
        return self.mParentGraph().getNodeData(self.mData) if self.mData is not None and  self.mParentGraph is not None else None

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the FxMap node definition (Inputs, Outputs, Parameters)

        :return: a :class:`.CompNodeDef` object
        """
        return sbslibrary.getFxMapNodeDefinition(self.mType)

    @handle_exceptions()
    def getDefinedParameters(self):
        """
        getDefinedParameters()
        Get the list of parameters defined on this node.

        :return: the list of :class:`.SBSParameter` specified on this node.
        """
        aData = self.getData()
        return aData.mParameters if aData is not None and aData.mParameters is not None else []

    @handle_exceptions()
    def getDisplayName(self):
        return self.mType+' ('+self.mUID+')'

    @handle_exceptions()
    def getDynamicParameters(self):
        """
        getDynamicParameters()
        Get the list of dynamic parameters defined on this node.

        :return: the list of :class:`.SBSParameter` specified on this node that have a dynamic function.
        """
        dynParams = []
        for aParam in self.getDefinedParameters():
            dynValue = aParam.getDynamicValue()
            if dynValue is not None:
                dynParams.append(aParam)
        return dynParams

    @handle_exceptions()
    def getParameterValue(self, aParameter):
        """
        getParameterValue(aParameter)
        Find a parameter among the data (SBSParamsGraphData) with the given name/id, and return its value.

        :param aParameter: Parameter identifier
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: The parameter value if found, None otherwise
        """
        aData = self.getData()
        return aData.getParameterValue(aParameter) if aData is not None else None

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        """
        setParameterValue(aParameter, aParamValue)
        Find a parameter among the data (SBSParamsGraphData) with the given name/id, and set it to the given value.

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aParamValue: :class:`.SBSDynamicValue` or any parameter type
        :return: True if succeed, False otherwise
        """
        aData = self.getData()
        return aData.setParameterValue(aParameter, aParamValue) if aData is not None else False

    @handle_exceptions()
    def setDynamicParameter(self, aParameter):
        """
        setDynamicParameter(aParameter)
        Set the given parameter as dynamic, to init its params.SBSDynamicValue.

        :param aParameter: identifier of the parameter
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: the :class:`.SBSDynamicValue` object if succeed, None otherwise
        """
        aData = self.getData()
        return aData.setDynamicParameter(aParameter) if aData is not None else False

    @handle_exceptions()
    def unsetParameter(self, aParameter):
        """
        unsetParameter(aParameter)
        Unset the given parameter so that it is reset to its default value.

        :param aParameter: identifier of the parameter to set
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: True if succeed, False otherwise
        """
        aData = self.getData()
        return aData.unsetParameter(aParameter) if aData is not None else False

    @handle_exceptions()
    def setParentGraph(self, aParentGraph):
        """
        setParentGraph(aParentGraph)
        Allows to set the reference to the parent graph.

        :param aParentGraph: The parent Graph of this node
        :type aParentGraph: :class:`.SBSGraph`
        """
        self.mParentGraph = weakref.ref(aParentGraph)

    @handle_exceptions()
    def isConnectedTo(self, aBottomNode):
        """
        isConnectedTo(aBottomNode)
        Check if the node is connected to the given node, in the direction aLeftNode -> self

        :param aBottomNode: The node to look for in the connections of this node.
        :type aBottomNode: :class:`.SBSParamsGraphNode` or str (UID)
        :return: True if the nodes are connected, False otherwise
        """
        return super(SBSParamsGraphNode, self).isConnectedTo(aLeftNode = aBottomNode)

    @handle_exceptions()
    def removeConnectionsFrom(self, aBottomNode):
        """
        removeConnectionsFrom(aBottomNode)
        Remove the connection between this node and aBottomNode (in the direction self -> aBottomNode)

        :param aBottomNode: The node to look for in the connections of this node.
        :type aBottomNode: :class:`.SBSParamsGraphNode` or str (UID)
        :return: Nothing
        """
        return super(SBSParamsGraphNode, self).removeConnectionsFrom(aLeftNode = aBottomNode)



# ==============================================================================
@doc_inherit
class SBSParamsGraph(SBSObject):
    """
    Class that contains information on a FxMap graph (e.g. parameters set graph) as defined in a .sbs file.
    Data (parameters) are separated from node instances to allow data reuse and Inheritance.

    Members:
        * mName             (str): name (type) of the graph.
        * mUID              (str): unique identifier of the graph in the /paramsGraphs/ context.
        * mGUILayoutPGraph  (:class:`.SBSGUILayoutComp`, optional): GUI flags and options.
        * mRootNode         (str, optional): uid of the root node.
        * mParamsGraphDatas (list of :class:`.SBSParamsGraphData`): data set of nodes, with Inheritance system.
        * mParamsGraphNodes (list of :class:`.SBSParamsGraphNode`): nodes list of the parameters graph.
        * mGUIObjects       (:class:`.SBSGUIObject`): GUI specific objects.
    """
    def __init__(self,
                 aName              = '',
                 aUID               = '',
                 aGUILayoutPGraph   = None,
                 aRootNode          = None,
                 aParamsGraphDatas  = None,
                 aParamsGraphNodes  = None,
                 aGUIObjects        = None):
        super(SBSParamsGraph, self).__init__()
        self.mName              = aName
        self.mUID               = aUID
        self.mGUILayoutPGraph   = aGUILayoutPGraph
        self.mRootNode          = aRootNode
        self.mParamsGraphDatas  = aParamsGraphDatas if aParamsGraphDatas is not None else []
        self.mParamsGraphNodes  = aParamsGraphNodes if aParamsGraphNodes is not None else []
        self.mGUIObjects        = aGUIObjects

        self.mGUIObjectList = sbscommon.GUIObjectList(self, 'mGUIObjects')

        self.mMembersForEquality = ['mName',
                                    'mParamsGraphDatas',
                                    'mParamsGraphNodes']

    def __deepcopy__(self, memo):
        """
        Overrides deepcopy to ensure that mGUIObjectList is correctly set

        :return: A clone of itself
        """
        clone = SBSParamsGraph()
        memo[id(self)] = clone
        for aMember in ['mName', 'mUID', 'mGUILayoutPGraph', 'mRootNode', 'mParamsGraphDatas', 'mParamsGraphNodes', 'mGUIObjects']:
            setattr(clone, aMember, copy.deepcopy(getattr(self, aMember), memo))
        for aNode in clone.getNodeList():
            aNode.setParentGraph(clone)
        return clone

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName             = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'name'            )
        self.mUID              = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'             )
        self.mGUILayoutPGraph  = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'GUIlayoutPGraph' , sbscommon.SBSGUILayoutComp)
        self.mRootNode         = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'rootnode'        )
        self.mParamsGraphDatas = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paramsGraphDatas', 'paramsGraphData', SBSParamsGraphData)
        self.mParamsGraphNodes = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paramsGraphNodes', 'paramsGraphNode', SBSParamsGraphNode)
        self.mGUIObjects       = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'GUIObjects'      , 'GUIObject', sbscommon.SBSGUIObject)

        if self.mParamsGraphNodes:
           for aGraphNode in self.mParamsGraphNodes:
               aGraphNode.setParentGraph(self)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName            , 'name'            )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID             , 'uid'             )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mGUILayoutPGraph , 'GUIlayoutPGraph' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mRootNode        , 'rootnode'        )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mParamsGraphDatas, 'paramsGraphDatas', 'paramsGraphData' )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mParamsGraphNodes, 'paramsGraphNodes', 'paramsGraphNode' )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mGUIObjects      , 'GUIObjects'      , 'GUIObject'  )

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Check if the given uid is already used in the context of this paramsGraphData

        return: True if the uid is already used, False otherwise
        """
        listToParse = [self.mParamsGraphDatas,self.mParamsGraphNodes]
        for aList,aObject in [(aList,aObject) for aList in listToParse if aList is not None for aObject in aList]:
            if aObject.mUID == aUID:
                return True
        return False

    @handle_exceptions()
    def getParamsGraphDataList(self):
        """
        getParamsGraphDataList()
        Get the list of :class:`.SBSParamsGraphData` of this graph

        :return: A list of :class:`.SBSParamsGraphData`
        """
        return self.mParamsGraphDatas if self.mParamsGraphDatas is not None else []

    @handle_exceptions()
    def getNodeList(self, aNodesList = None):
        """
        getNodeList(aNodesList = None)
        Get all the nodes of this FxMap graph, or look for the given nodes if aNodesList is not None

        :param aNodesList: list of node to look for
        :type aNodesList: list of str or list of :class:`.SBSParamsGraphNode`, optional
        :return: A list of :class:`.SBSParamsGraphNode` included in the FxMap graph
        """
        if aNodesList is None:
            resNodeList = self.mParamsGraphNodes if self.mParamsGraphNodes is not None else []
        else:
            resNodeList = []
            for aNode in aNodesList:
                if python_helpers.isStringOrUnicode(aNode):
                    aNode = self.getNode(aNode)
                else:
                    aNode = aNode if aNode in self.mParamsGraphNodes else None
                if aNode is not None:
                    resNodeList.append(aNode)

        return resNodeList

    @handle_exceptions()
    def getNodeData(self, aDataUID):
        """
        getNodeData(aDataUID)
        Get the :class:`.SBSParamsGraphData` object with the given UID

        :param aDataUID: uid of the data to get
        :type aDataUID: str
        :return: The :class:`.SBSParamsGraphData` object if found, None otherwise
        """
        return next((aData for aData in self.getParamsGraphDataList() if aData.mUID == aDataUID), None)

    @handle_exceptions()
    def getNode(self, aNodeUID):
        """
        getNode(aNodeUID)
        Get the :class:`.SBSParamsGraphNode` object with the given UID

        :param aNodeUID: uid of the node to get
        :type aNodeUID: str
        :return: The :class:`.SBSParamsGraphNode` object if found, None otherwise
        """
        return next((aNode for aNode in self.getNodeList() if aNode.mUID == aNodeUID), None)

    @handle_exceptions()
    def getNodeAssociatedToComment(self, aComment):
        """
        getNodeAssociatedToComment(aComment)
        Get the node associated to the given comment.

        :param aComment: The comment to consider
        :type aComment: :class:`.SBSGUIObject`
        :return: the :class:`.SBSParamsGraphNode` if found, None otherwise
        """
        aUID = aComment.getDependencyUID()
        return self.getNode(aUID) if aUID is not None else None

    @handle_exceptions()
    def getNodesInFrame(self, aFrame):
        """
        getNodesInFrame(aFrame)
        Get all the nodes included or partially included in the given frame.
        The frame must be included in this graph, otherwise SBSImpossibleActionError is raised

        :param aFrame: The frame to consider
        :type aFrame: :class:`.SBSGUIObject`
        :return: a list of :class:`.SBSParamsGraphNode`
        """
        return self.mGUIObjectList.getNodesInFrame(aFrame)

    @handle_exceptions()
    def getAllDependencyUID(self):
        """
        getAllDependencyUID()
        Get the UIDs of the dependencies used by this graph

        :return: a list of UIDs as strings
        """
        dependencySet = set()
        for aFxNode in self.getNodeList():
            for aParam in aFxNode.getDynamicParameters():
                dependencySet.update(aParam.getDynamicValue().getAllDependencyUID())
        return sorted(list(dependencySet))

    @handle_exceptions()
    def getAllReferencesOnDependency(self, aDependency):
        """
        getAllReferencesOnDependency(aDependency)
        Get all the SBSCompNode that are referencing the given dependency

        :param aDependency: The dependency to look for (UID or object)
        :type aDependency: str or :class:`.SBSDependency`
        :return: A list of :class:`.SBSCompNode`
        """
        refNodeList = []

        # Parse all FxMap nodes of the graph
        for aFxNode in self.getNodeList():
            for aParam in aFxNode.getDynamicParameters():
                refNodeList.extend(aParam.getDynamicValue().getAllReferencesOnDependency(aDependency))

        return refNodeList

    @handle_exceptions()
    def computeUniqueIdentifier(self, aIdentifier, aSuffixId = 0):
        """
        computeUniqueIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used and generate a unique identifier if necessary

        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier_id
        """
        return self._computeUniqueIdentifier(aIdentifier, aListsToCheck= [self.mParamsGraphDatas], aSuffixId= aSuffixId)

    @handle_exceptions()
    def contains(self, aNode):
        """
        contains(aNode)
        Check if the given node belongs to this graph

        :param aNode: The node to check, as a, object or an UID
        :type aNode: :class:`.SBSParamsGraphNode` or str
        :return: True if the given node belongs to the graph, False otherwise
        """
        if python_helpers.isStringOrUnicode(aNode):
            return self.getNode(aNode) is not None
        else:
            return aNode in self.getNodeList()


    @handle_exceptions()
    def connectNodes(self, aTopNode, aBottomNode, aTopNodeOutput = None):
        """
        connectNodes(aBottomNode, aTopNode, aTopNodeOutput = None)
        Connect the given nodes together: aTopNode(on the output aTopNodeOutput) -> aBottomNode.
        If the top node output is None, the connection will be done for ALL the outputs of the top node.

        :param aBottomNode: Node to connect to
        :param aTopNode: Node to connect from
        :param aTopNodeOutput: Identifier of the output of the top node

        :type aBottomNode: :class:`.SBSParamsGraphNode` or str
        :type aTopNode: :class:`.SBSParamsGraphNode` or str
        :type aTopNodeOutput: :class:`.OutputEnum` or str, optional

        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Check that the given nodes belongs to the function graph
        if python_helpers.isStringOrUnicode(aBottomNode):
            aBottomNodeUID = aBottomNode
            aBottomNode = self.getNode(aBottomNodeUID)
        else:
            aBottomNodeUID = aBottomNode.mUID
        if python_helpers.isStringOrUnicode(aTopNode):
            aTopNodeUID = aTopNode
            aTopNode = self.getNode(aTopNode)
        else:
            aTopNodeUID = aTopNode.mUID

        if not self.contains(aBottomNode) or not self.contains(aTopNode):
            raise SBSImpossibleActionError('Impossible to connect node '+str(aTopNodeUID)+' to '+str(aBottomNodeUID))

        # Get the comp nodes parameters (input entries, parameters, outputs)
        aBottomNodeDefinition = aBottomNode.getDefinition()
        aTopNodeDefinition = aTopNode.getDefinition()
        if aBottomNodeDefinition is None or aTopNodeDefinition is None:
            raise SBSImpossibleActionError('Impossible to connect node '+str(aTopNode)+' to '+str(aBottomNode))

        # Check the given top node output
        aTopOutputs = []
        if aTopNodeOutput is not None:
            aOutput = aTopNodeDefinition.getOutput(aTopNodeOutput)
            if aOutput is None:
                aOutput = aTopNodeOutput if python_helpers.isStringOrUnicode(aTopNodeOutput) else sbslibrary.getCompNodeOutput(aTopNodeOutput)
                raise SBSImpossibleActionError('Impossible to connect node '+str(aTopNode)+' to '+str(aBottomNode) +\
                                               ', output '+aOutput+' not found on node '+str(aTopNode))

            aTopOutputs.append(aOutput.mIdentifier)

        # Retrieve all the output identifier
        else:
            for aOutput in aTopNodeDefinition.mOutputs:
                aTopOutputs.append(aOutput.mIdentifier)
        if not aTopOutputs:
            raise SBSImpossibleActionError('Impossible to connect node '+str(aTopNode)+' to '+str(aBottomNode))

        # Check that the connection will not create a cycle in the DAG
        if self.isAPathBetween(aTopNode = aBottomNode, aBottomNode = aTopNode):
            raise SBSImpossibleActionError('Impossible to connect node '+str(aTopNode)+' to '+str(aBottomNode)+', it would create a cycle')

        # Create the connection:
        # All FxMap nodes have one single input, and all FxMap node outputs are compatible with this input
        for aOutput in aTopOutputs:
            aOutputIdentifier = sbslibrary.getCompNodeOutput(aOutput)
            aConn = aTopNode.getConnectionOnPin(aOutputIdentifier)
            if aConn is None:
                aConn = sbscommon.SBSConnection(aIdentifier = aOutputIdentifier,
                                                aConnRef    = aBottomNode.mUID)
                api_helpers.addObjectToList(aTopNode, 'mConnections', aConn)

            else:
                aConn.setConnection(aConnRefValue = aBottomNode.mUID)

        return True

    @handle_exceptions()
    def disconnectNodes(self, aTopNode, aBottomNode, aTopNodeOutput = None):
        """
        disconnectNodes(aTopNode, aBottomNode, aTopNodeOutput = None)
        Disconnect the given nodes: aTopNode(on the output aTopNodeOutput) -> aBottomNode.
        If the top node output is None, all connections will be removed.

        :param aTopNode: Top node
        :param aBottomNode: Bottom node
        :param aTopNodeOutput: Identifier of the output of the top node

        :type aTopNode: :class:`.SBSCompNode`
        :type aBottomNode: :class:`.SBSCompNode`
        :type aTopNodeOutput: :class:`.OutputEnum` or str, optional

        :return: Nothing
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Check that the given nodes belongs to the function graph
        if python_helpers.isStringOrUnicode(aBottomNode):
            aBottomNodeUID = aBottomNode
            aBottomNode = self.getNode(aBottomNodeUID)
        else:
            aBottomNodeUID = aBottomNode.mUID
        if python_helpers.isStringOrUnicode(aTopNode):
            aTopNodeUID = aTopNode
            aTopNode = self.getNode(aTopNode)
        else:
            aTopNodeUID = aTopNode.mUID

        if not self.contains(aBottomNode) or not self.contains(aTopNode):
            raise SBSImpossibleActionError('Impossible to disconnect node '+str(aTopNodeUID)+' to '+str(aBottomNodeUID))

        if aTopNodeOutput is None:
            aTopNode.removeConnectionsFrom(aBottomNode)
        else:
            if not python_helpers.isStringOrUnicode(aTopNodeOutput):
                aTopNodeOutput = sbslibrary.getCompNodeOutput(aTopNodeOutput)
            conn = aTopNode.getConnectionOnPin(aTopNodeOutput)
            if conn is not None and conn.getConnectedNodeUID() == aBottomNode.mUID:
                aTopNode.removeConnectionOnPin(aTopNodeOutput)

    @handle_exceptions()
    def createFxMapNode(self, aFxMapNode, aGUIPos = None, aParameters = None):
        """
        createFxMapNode(aFxMapNode, aGUIPos = None, aParameters = None)
        Create a new FxMap node (:class:`.SBSParamsGraphNode`) and its associated data (:class:`.SBSParamsGraphData`)
        and add them to the FxMap graph.

        :param aFxMapNode: the kind of FxMap node to create among the list defined in :class:`.FxMapNodeEnum`
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the FxMap node

        :type aFxMapNode: :class:`.FxMapNodeEnum` or str
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {:class:`.CompNodeParamEnum` : parameterValue(str)}, optional

        :return: The new :class:`.SBSParamsGraphNode` object
        """
        if aGUIPos is None: aGUIPos = [0, 0, 0]
        if aParameters is None: aParameters = {}

        # Get the appropriate fxmap parameters
        aFxMapDef = sbslibrary.getFxMapNodeDefinition(aFxMapNode)

        # Create the data associated to the new node
        aDataUID = UIDGenerator.generateUID(self)
        aIdentifier = self.computeUniqueIdentifier('Parameter_node')
        aFxMapData = SBSParamsGraphData(aUID = aDataUID,
                                        aIdentifier = aIdentifier,
                                        aType = aFxMapDef.mIdentifier)
        api_helpers.addObjectToList(self, 'mParamsGraphDatas', aFxMapData)

        # Create the new node
        aNodeUID = UIDGenerator.generateUID(self)
        aFxMapNode = SBSParamsGraphNode(aUID = aNodeUID,
                                        aData = aDataUID,
                                        aType = aFxMapDef.mIdentifier,
                                        aGUILayout = sbscommon.SBSGUILayout(aGPos = aGUIPos),
                                        aParentGraph = self)

        # Set the parameters
        for aParam in aParameters.items():
            aFxMapNode.setParameterValue(aParameter=aParam[0], aParamValue=aParam[1])

        api_helpers.addObjectToList(self, 'mParamsGraphNodes', aFxMapNode)

        return aFxMapNode

    @handle_exceptions()
    def createIterationOnPattern(self, aGraphNode, aParameter, aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern = None, aGUIOffset = None):
        """
        createIterationOnPattern(aGraphNode, aParameter, aNbIteration, aNodeUIDs, aNodeUIDs_NextPatternInput = None, aGUIOffset = None)
        | Allows to create an iteration in the function defining the value of the given parameter.
        | Duplicate nbIteration times the given pattern of nodes, to create this kind of connection:
        | Pattern -> Pattern_1 -> Pattern_2 -> ... -> Pattern_N

        :param aGraphNode: the FxMap node which contains the parameter definition dynamically driven
        :param aParameter: the parameter driven by a dynamic function, on which the iteration will be created
        :param aNbIteration: number of time the pattern must be duplicated
        :param aNodeUIDs: list of node's UID that constitute the pattern to duplicate
        :param aNodeUIDs_NextPattern: list of node's UID that correspond to the next pattern, which must be connected to the given pattern.
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aGraphNode: :class:`.SBSParamsGraphNode` or str
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aNbIteration: positive integer
        :type aNodeUIDs: list of str
        :type aNodeUIDs_NextPattern: list of str, optional
        :type aGUIOffset: list of 2 float, optional

        :return: The list of params.SBSParamNode created if succeed
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIOffset is None: aGUIOffset = [150,0]
        if aNodeUIDs_NextPattern is None: aNodeUIDs_NextPattern = []

        if python_helpers.isStringOrUnicode(aGraphNode):   aGraphNodeUID = aGraphNode
        else:                                           aGraphNodeUID = aGraphNode.mUID

        aGraphNode = self.getNode(aGraphNodeUID)
        if aGraphNode is None or aGraphNode.mData is None:
            raise SBSImpossibleActionError('Cannot create iteration: Failed to find '+aGraphNodeUID+' on this graph')

        aData = self.getNodeData(aGraphNode.mData)
        if aData is None:
            raise SBSImpossibleActionError('Cannot create iteration: No data found for node '+aGraphNodeUID)

        if not python_helpers.isStringOrUnicode(aParameter):
            aParameter = sbslibrary.getCompNodeParam(aParameter)
        if aParameter is None:
            raise SBSImpossibleActionError('Cannot create iteration: Invalid parameter '+aParameter)

        aParamDynValue = aData.getParameterValue(aParameter)
        if not isinstance(aParamDynValue, params.SBSDynamicValue):
            raise SBSImpossibleActionError('Cannot create iteration: Parameter '+aParameter+' is not dynamic')

        return aParamDynValue.createIterationOnPattern(aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern, aGUIOffset)


    @handle_exceptions()
    def createComment(self, aCommentText='Comment', aGUIPos=None, aLinkToNode=None):
        """
        createComment(aCommentText='Comment', aGUIPos=None, aLinkToNode=None)
        Create a new comment.\
        If aLinkToNode is not None, this comment will be linked to the given node, and the given GUI position must be relative to this node.

        :param aCommentText: The text of the comment. Default to 'Comment'
        :param aGUIPos: The comment position in the graph. Default to [0,0,0]
        :param aLinkToNode: UID of the node to associate to this comment
        :type aCommentText: str, optional
        :type aGUIPos: list of 3 float, optional
        :type aLinkToNode: str, optional
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
        :type aNodeList: list of class:`.SBSParamsGraphNode`
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
        :type aNodeList: list of class:`.SBSParamsGraphNode`
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
    def deleteNode(self, aNode):
        """
        deleteNode(aNode)
        Allows to delete the given node from the graph.
        It removes it from the mParamsGraphNodes and mParamsGraphDatas list, and delete all the connection from and to that node in the graph.

        :param aNode: The node to remove, as a SBSParamsGraphNode or an UID.
        :type aNode: :class:`.SBSParamsGraphNode` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if python_helpers.isStringOrUnicode(aNode): aUID = aNode
        else:                                       aUID = aNode.mUID

        aNodeList = self.getNodeList()
        aNode = self.getNode(aUID)
        if aNode is None:
            raise SBSImpossibleActionError('Impossible to delete the node ' + aUID + ', cannot find this node in the graph')

        for aConnectedNode in [aConnectedNode for aConnectedNode in aNodeList if
                               aConnectedNode.isConnectedTo(aBottomNode = aUID)]:
            aConnectedNode.removeConnectionsFrom(aBottomNode = aUID)

        aNodeList.remove(aNode)
        return True

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
    def getAllNodesOfKind(self, aFxMapNode):
        """
        getAllNodesOfKind(aFxMapNode)
        Search for all :class:`.SBSParamsGraphNode` of the given kind (Quadrant, Switch or Iterate).

        :param aFxMapNode: kind of FxMap node to look for
        :type aFxMapNode: :class:`.FxMapNodeEnum` str
        :return: a list of :class:`.SBSParamsGraphNode` containing all filters of the given kind.
        """
        if python_helpers.isStringOrUnicode(aFxMapNode):
            aNodeName = aFxMapNode
        else:
            aNodeName = sbslibrary.getFxMapNodeDefinition(aFxMapNode).mIdentifier
        return [node for node in self.mParamsGraphNodes if node.mType == aNodeName]

    @handle_exceptions()
    def getCommentsAssociatedToNode(self, aNode):
        """
        getCommentsAssociatedToNode(aNode)
        Get the list of comments associated to the given node

        :param aNode: The node to consider, as a SBSParamsGraphNode or given its UID
        :type aNode: :class:`.SBSParamsGraphNode` or str
        :return: a list of :class:`.SBSGUIObject`
        """
        aUID = aNode.mUID if isinstance(aNode, SBSParamsGraphNode) else aNode
        return [aComment for aComment in self.getAllComments() if aComment.hasDependencyOn(aUID)]

    @handle_exceptions()
    def duplicateNode(self, aNode, aGUIOffset = None):
        """
        duplicateNode(aNode, aGUIOffset = None)
        Duplicate the given node, generate a new UID and add the node to the graph.
        Duplicate also the SPSParamsGraphData associated to this node

        :param aNode: the node to copy (may be identified by its UID)
        :param aGUIOffset: node position offset. Default to [150, 0]
        :type aNode: :class:`.SPSParamsGraphNode` or str
        :type aGUIOffset: list of 2 float, optional
        :return: The new :class:`.SPSParamsGraphNode` object
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIOffset is None: aGUIOffset = [0,150]

        # Get the SBSNode with the given uid
        aNodeUID = None
        if python_helpers.isStringOrUnicode(aNode):
            aNodeUID = aNode
            aNode = self.getNode(aNodeUID)
        if aNode is None:
            raise SBSImpossibleActionError('Cannot duplicate node: Cannot find node '+str(aNodeUID)+' in this graph')

        # Create a copy of this node
        aNewNode = copy.deepcopy(aNode)

        # Generate a new UID
        aNewNode.mUID = UIDGenerator.generateUID(self)

        # Handle GUILayout: position the new node with a horizontal offset from the source node
        if aNewNode.mGUILayout is not None:
            aNewNode.mGUILayout.mGPos[0] += aGUIOffset[0]
            aNewNode.mGUILayout.mGPos[1] += aGUIOffset[1]

        # Add the new node to the Nodes list
        self.mParamsGraphNodes.append(aNewNode)

        aData = self.getNodeData(aNode.mData)
        if aData is not None:
            aNewData = copy.deepcopy(aData)
            aNewData.mUID = UIDGenerator.generateUID(self)
            aNewNode.mData = aNewData.mUID
            self.mParamsGraphDatas.append(aNewData)

        return aNewNode

    @handle_exceptions()
    def isAPathBetween(self, aTopNode, aBottomNode):
        """
        isAPathBetween(self, aTopNode, aBottomNode)
        Check if there is a path from the top node to the bottom node with the current connections.

        :param aTopNode: The left node
        :param aBottomNode: The right node
        :type aTopNode: :class:`.SBSNode`
        :type aBottomNode: :class:`.SBSNode`
        :return: True if a path is found, False otherwise
        """
        if not self.contains(aTopNode) or not self.contains(aBottomNode):
            return False

        # Start from the top node and check the connections
        aCheckedNodes = []
        aNodesToCheck = [aTopNode.mUID]
        found = False
        while not found and len(aNodesToCheck) > 0:
            aNode = self.getNode(aNodesToCheck[0])
            aNodesToCheck = aNodesToCheck[1:]
            for conn in aNode.getConnections():
                connRefUID = conn.getConnectedNodeUID()
                if connRefUID == aBottomNode.mUID:
                    found = True
                    break
                elif connRefUID not in aCheckedNodes and connRefUID not in aNodesToCheck:
                    aNodesToCheck.append(connRefUID)

            aCheckedNodes.append(aNode.mUID)
        return found

    @handle_exceptions()
    def setRootNode(self, aNode):
        """
        setRootNode(aNode)
        Set the root node of the FxMap graph

        :param aNode: the node to set as root, or its UID
        :type aNode: :class:`.SBSParamsGraphNode` or str
        :return: The :class:`.SBSParamsGraphNode` corresponding to the root node, False if not found
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Get the SBSNode with the given uid
        if python_helpers.isStringOrUnicode(aNode): aNodeUID = aNode
        else:                                       aNodeUID = aNode.mUID
        aNode = self.getNode(aNodeUID)
        if aNode is None:
            raise SBSImpossibleActionError('Cannot duplicate node: Cannot find node '+aNodeUID+' in this graph')

        self.mRootNode = aNodeUID
        return aNode
