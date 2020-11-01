# coding: utf-8
"""
Module **graph** aims to define SBSObjects that are relative to a graph or a function,
mostly :class:`.SBSGraph`, :class:`.SBSFunction`, :class:`.SBSParamInput` and :class:`.SBSGraphOutput`.
"""

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import base64
import copy
import zlib

from pysbs.api_decorators import doc_inherit,handle_exceptions,deprecated
from pysbs.api_exceptions import SBSLibraryError,SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject, UIDGenerator, Graph
from pysbs.compnode import compimplementation
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import sbscommon
from pysbs import params
from pysbs import compnode
from pysbs import sbsgenerator
from .inputparameters import SBSParamInput, SBSPreset
from .output import SBSGraphOutput, SBSRoot


#=======================================================================
@doc_inherit
class SBSGraph(SBSObject, Graph):
    """
    Class that contains information on a compositing graph as defined in a .sbs file

    Members:
        * mIdentifier     (str): name of the graph (name of the definition and the instance if applicable).
        * mUID            (str): unique identifier in the package/ context.
        * mAttributes     (:class:`.SBSAttributes`): various attributes
        * mParamInputs    (list of :class:`.SBSParamInput`): list of parameters and compositing inputs of the graph.
        * mPrimaryInput   (str, optional): The uid of the primary (image) input (paramInputs/uid).
        * mGraphOutputs   (list of :class:`.SBSGraphOutput`): list of compositing outputs of the graph.
        * mCompNodes      (list of :class:`.SBSCompNode`): compositing nodes, the graph definition.
        * mBaseParameters (list of :class:`.SBSParameter`): common authoring parameters.
        * mGUIObjects     (list of :class:`.SBSGUIObject`, optional): GUI specific objects.
        * mOptions        (list of :class:`.SBSOption`): list of specific options.
        * mRoot           (:class:`.SBSRoot`, optional): Appears when the graph is a root (root graphs outputs are directly computed at runtime, cooking always needed).
        * mPresets        (:class:`.SBSPreset`, optional): list of user-defined presets
    """
    __sAttributes = [sbsenum.AttributesEnum.Author          ,
                     sbsenum.AttributesEnum.AuthorURL       ,
                     sbsenum.AttributesEnum.Category        ,
                     sbsenum.AttributesEnum.Description     ,
                     sbsenum.AttributesEnum.HideInLibrary   ,
                     sbsenum.AttributesEnum.Icon            ,
                     sbsenum.AttributesEnum.Label           ,
                     sbsenum.AttributesEnum.PhysicalSize    ,
                     sbsenum.AttributesEnum.Tags            ,
                     sbsenum.AttributesEnum.UserTags        ]

    def __init__(self,
                 aIdentifier    = '',
                 aUID           = '',
                 aAttributes    = None,
                 aParamInputs   = None,
                 aPrimaryInput  = None,
                 aGraphOutputs  = None,
                 aCompNodes     = None,
                 aBaseParameters= None,
                 aGUIObjects    = None,
                 aOptions       = None,
                 aRoot          = None,
                 aPresets       = None):
        SBSObject.__init__(self)
        Graph.__init__(self, aIdentifier=aIdentifier,
                             aParamInputs=aParamInputs,
                             aPrimaryInput=aPrimaryInput,
                             aGraphOutputs=aGraphOutputs if aGraphOutputs is not None else [],
                             aPresets = aPresets)
        self.mUID           = aUID
        self.mAttributes    = aAttributes
        self.mCompNodes     = aCompNodes if aCompNodes is not None else []
        self.mBaseParameters= aBaseParameters if aBaseParameters is not None else []
        self.mGUIObjects    = aGUIObjects
        self.mOptions       = aOptions
        self.mRoot          = aRoot

        self.mNodeList = sbscommon.NodeList(self, compnode.SBSCompNode, 'mCompNodes')
        self.mGUIObjectList = sbscommon.GUIObjectList(self, 'mGUIObjects')

        self.mMembersForEquality = ['mIdentifier',
                                    'mAttributes',
                                    'mParamInputs',
                                    'mGraphOutputs',
                                    'mCompNodes',
                                    'mBaseParameters',
                                    'mOptions',
                                    'mRoot',
                                    'mPresets']

    def __deepcopy__(self, memo):
        """
        Overrides deepcopy to ensure that mNodeList and mGUIObjectList are correctly set

        :return: A clone of itself
        """
        clone = SBSGraph()
        memo[id(self)] = clone
        for aMember in ['mIdentifier', 'mUID', 'mAttributes', 'mParamInputs', 'mPrimaryInput', 'mGraphOutputs',
                        'mCompNodes', 'mBaseParameters', 'mGUIObjects', 'mOptions', 'mRoot', 'mPresets']:
            setattr(clone, aMember, copy.deepcopy(getattr(self, aMember), memo))
        return clone

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier    = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'identifier'    )
        self.mUID           = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'           )
        self.mAttributes    = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'attributes'    , sbscommon.SBSAttributes)
        self.mParamInputs   = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paraminputs'   , 'paraminput'  , SBSParamInput)
        self.mPrimaryInput  = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'primaryInput'  )
        self.mGraphOutputs  = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'graphOutputs'  , 'graphoutput' , SBSGraphOutput)
        self.mCompNodes     = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'compNodes'     , 'compNode'    , compnode.SBSCompNode)
        self.mBaseParameters= aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'baseParameters', 'parameter'   , params.SBSParameter)
        self.mGUIObjects    = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'GUIObjects'    , 'GUIObject'   , sbscommon.SBSGUIObject)
        self.mOptions       = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'options'       , 'option'      , sbscommon.SBSOption)
        self.mRoot          = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'root'          , SBSRoot)
        self.mPresets       = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'sbspresets'    , 'sbspreset'   , SBSPreset)
        for aPreset in self.getAllPresets():
            aPreset.setRefGraph(self)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIdentifier    , 'identifier'      )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUID           , 'uid'             )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mAttributes    , 'attributes'      )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mParamInputs   , 'paraminputs'     ,    'paraminput'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mPrimaryInput  , 'primaryInput'    )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mGraphOutputs  , 'graphOutputs'    ,    'graphoutput'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mCompNodes     , 'compNodes'       ,    'compNode'     )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mBaseParameters, 'baseParameters'  ,    'parameter'    )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mGUIObjects    , 'GUIObjects'      ,    'GUIObject'    )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mOptions       , 'options'         ,    'option'       )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mRoot          , 'root'            )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mPresets       , 'sbspresets'      ,    'sbspreset'    )

    @handle_exceptions()
    def createPreset(self, aLabel, aUsertags=None, setCurrentDefaultValues=False):
        """
        createPreset(aLabel, aUsertags=None, setCurrentDefaultValues=False)
        Create a new preset with the given label and usertags and add it to the preset list of this graph.

        :param aLabel: The label of this preset
        :param aUsertags: The usertags of this preset
        :param setCurrentDefaultValues: True to automatically create one SBSPresetInput by input parameter in the graph, initialized with the default value. Default to False.
        :type aLabel: str
        :type aUsertags: str, optional
        :type setCurrentDefaultValues: bool, optional
        :return: the created preset as a :class:`.SBSPreset`
        """
        aPreset = sbsgenerator.createPreset(aParentGraph=self, aLabel=aLabel, aUsertags=aUsertags)
        api_helpers.addObjectToList(aObject=self, aMemberListName='mPresets', aObjectToAdd=aPreset)
        if setCurrentDefaultValues:
            for aInputParam in self.getInputParameters():
                aPreset.setPresetInput(aInputParam=aInputParam, aPresetValue=aInputParam.getDefaultValue())
        return aPreset

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Check if the given uid is already used in the context of the graph

        :param aUID: UID to check
        :type aUID: str
        :return: True if the uid is already used, False otherwise
        """
        listToParse = [self.mCompNodes,self.mParamInputs,self.mGraphOutputs,self.mGUIObjects]
        for aList,aObject in [(aList,aObject) for aList in listToParse if aList is not None for aObject in aList]:
            if aObject.mUID == aUID:
                return True
        return False

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
    def getAllNodes(self):
        """
        getAllNodes()
        Search for all :class:`.SBSCompNode`.

        :return: a list of :class:`.SBSCompNode`.
        """
        return self.getNodeList()

    @handle_exceptions()
    def getAllInputNodes(self):
        """
        getAllInputNodes()
        Search for all :class:`.SBSCompNode` with a CompInputBridge implementation.

        :return: a list of :class:`.SBSCompNode` containing all input nodes of the graph.
        """
        return [node for node in self.getNodeList() if node.isAnInputBridge()]

    @handle_exceptions()
    def getAllOutputNodes(self):
        """
        getAllOutputNodes()
        Search for all :class:`.SBSCompNode` with a CompOutputBridge implementation.

        :return: a list of :class:`.SBSCompNode` containing all output nodes of the graph.
        """
        return [node for node in self.getNodeList() if node.isAnOutputBridge()]

    @handle_exceptions()
    def getAllFiltersOfKind(self, aFilter):
        """
        getAllFiltersOfKind(aFilter)
        Search for all :class:`.SBSCompNode` which represents the given filter kind.

        :param aFilter: kind of filters to look for
        :type aFilter: :class:`.FilterEnum` str
        :return: a list of :class:`.SBSCompNode` containing all filters of the given kind.
        """
        if python_helpers.isStringOrUnicode(aFilter):
            aFilterName = aFilter
            aFilterEnum = sbslibrary.getFilterEnum(aFilterName)
        else:
            aFilterEnum = aFilter
            aFilterName = sbslibrary.getFilterDefinition(aFilterEnum).mIdentifier
        return [node for node in self.getNodeList()
                if (node.isAFilter() and node.mCompImplementation.mCompFilter.mFilter == aFilterName) or
                    (aFilterEnum == sbsenum.FilterEnum.COMPINSTANCE and node.isAnInstance())]

    @handle_exceptions()
    def getAllNodeInstancesOf(self, aSBSDocument, aPath):
        """
        getAllNodeInstancesOf(aSBSDocument, aPath)
        Search for all :class:`.SBSCompNode` with a CompInstance implementation, which reference the given graph path.

        :param aSBSDocument: current SBSDocument
        :param aPath: path of the graph definition (absolute, relative to the current .sbs file, or given with an alias, for instance *sbs://anisotropic_noise.sbs*)

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.
        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :return: a list of :class:`.SBSCompNode` containing all instance nodes of the given graph.
        """
        absPath = aSBSDocument.convertToAbsolutePath(aPath)
        if aSBSDocument.isAPackage(absPath):
            posSep = absPath.rfind('/')
            graphName = aSBSDocument.removePackageExtension(absPath[posSep+1:])
            absPath += '/' + graphName

        return [node for node in self.getNodeList()
                if node.isAnInstance() and node.mCompImplementation.mCompInstance.getReferenceAbsPath() == absPath]

    @handle_exceptions()
    def getAllDependencyUID(self):
        """
        getAllDependencyUID()
        Get the UIDs of the dependencies used by this graph

        :return: a list of UIDs as strings
        """
        dependencySet = set()

        # Parse all compositing nodes of the graph
        for aNode in self.getNodeList():
            # CompInstance => Check the dependency
            if aNode.isAnInstance():
                dependencySet.add(aNode.getCompInstance().getDependencyUID())

            # FxMap => Check in the FxMap graph
            elif aNode.isAFxMap():
                aFxMapGraph = aNode.getFxMapGraph()
                if aFxMapGraph is not None:
                    dependencySet.update(aFxMapGraph.getAllDependencyUID())

            # Resource node => himself dependency
            elif aNode.isAResource():
                aPath = aNode.getCompFilter().getResourcePath()
                aDepUID = api_helpers.splitPathAndDependencyUID(aPath)[1]
                if aDepUID:
                    dependencySet.add(aDepUID)

            # For all nodes, search in the dynamic parameters
            for aParam in aNode.getDynamicParameters():
                dependencySet.update(aParam.getDynamicValue().getAllDependencyUID())

        return sorted(list(dependencySet))

    @handle_exceptions()
    def getAllResourcesUsed(self, aParentDocument):
        """
        getAllResourcesUsed(aParentDocument)
        Get the list of resources used in this graph as a list of paths relative to the package

        :param aParentDocument: Parent SBSDocument containing this graph
        :type aParentDocument: :class:`.SBSDocument`
        :return: the list of resources used in this graph as a list of paths relative to the package (pkg:///...)
        """
        resourcePaths = []
        for aNode in [aNode for aNode in self.getNodeList() if aNode.isAResource()]:
            aPath = aNode.getCompFilter().getResourcePath()
            if aPath is not None and aPath not in resourcePaths:
                resourcePaths.append(aPath)
            aResource = aParentDocument.getSBSResourceFromPath(aPath)
            if aResource is not None and aResource.isABakingOutput():
                meshResourcePath = aResource.getOption('BakingDependencyUrl')
                if meshResourcePath:
                    meshResource = aParentDocument.getSBSResourceFromPath(meshResourcePath)
                    resourcePaths.append(meshResourcePath)

        return resourcePaths

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

        # Parse all compositing nodes of the graph
        for aNode in self.getNodeList():
            # Check the node's direct dependency
            if aNode.hasAReferenceOnDependency(aDependency):
                refNodeList.append(aNode)

            # FxMap => Check in the FxMap graph
            if aNode.isAFxMap():
                aFxMapGraph = aNode.getFxMapGraph()
                if aFxMapGraph is not None:
                    refNodeList.extend(aFxMapGraph.getAllReferencesOnDependency(aDependency))

            # For all nodes, search in the dynamic parameters
            for aParam in aNode.getDynamicParameters():
                refNodeList.extend(aParam.getDynamicValue().getAllReferencesOnDependency(aDependency))

        return refNodeList

    @handle_exceptions()
    def getAllReferencesOnResource(self, aResource):
        """
        getAllReferencesOnResource(aResource)
        Get all the SBSCompNode that are referencing the given resource

        :param aResource: The resource to look for (object or path internal to the package (pkg:///myGroup/myResource)
        :type aResource: str or :class:`.SBSResource`
        :return: A list of :class:`.SBSCompNode`
        """
        aPath = aResource if python_helpers.isStringOrUnicode(aResource) else aResource.getPkgResourcePath()
        return [aNode for aNode in self.getNodeList() \
                       if aNode.isAResource() and aPath == aNode.getCompFilter().getResourcePath()]

    @handle_exceptions()
    def getCommentsAssociatedToNode(self, aNode):
        """
        getCommentsAssociatedToNode(aNode)
        Get the list of comments associated to the given node

        :param aNode: The node to consider, as a SBSCompNode or given its UID
        :type aNode: :class:`.SBSCompNode` or str
        :return: a list of :class:`.SBSGUIObject`
        """
        aUID = aNode.mUID if isinstance(aNode, compnode.SBSCompNode) else aNode
        return [aComment for aComment in self.getAllComments() if aComment.hasDependencyOn(aUID)]

    @handle_exceptions()
    def getGraphInputNode(self, aInputImageIdentifier):
        """
        getGraphInputNode(aInputImageIdentifier)
        Get the input node which corresponds to the input image with the given identifier

        :param aInputImageIdentifier: identifier of the input
        :type aInputImageIdentifier: str
        :return: a :class:`.SBSCompNode` object if found, None otherwise
        """
        inputImage = self.getInputImage(aInputImageIdentifier)
        if inputImage is not None:
            return next((inputNode for inputNode in self.getAllInputNodes()
                         if inputNode.mCompImplementation.mCompInputBridge.mEntry == inputImage.mUID), None)
        return None

    @handle_exceptions()
    @deprecated(__name__, '2018.2.0', 'Renamed for consistency with getGraphOutputNode', 'Please use getGraphInputNode instead')
    def getInputNode(self, aInputImageIdentifier):
        """
        getInputNode(aInputImageIdentifier)
        Get the input node which corresponds to the input image with the given identifier

        :param aInputImageIdentifier: identifier of the input
        :type aInputImageIdentifier: str
        :return: a :class:`.SBSCompNode` object if found, None otherwise
        """
        return self.getGraphInputNode(aInputImageIdentifier)

    @handle_exceptions()
    def getNode(self, aNode):
        """
        getNode(aNode)
        Search for the given compositing node in the node list

        :param aNode: node to get, identified by its uid or as a :class:`.SBSCompNode`
        :type aNode: :class:`.SBSCompNode` or str
        :return: A :class:`.SBSCompNode` object if found, None otherwise
        """
        return self.mNodeList.getNode(aNode)

    @handle_exceptions()
    def getNodeList(self, aNodesList = None):
        """
        getNodeList(aNodesList = None)
        Get all the compositing nodes of this graph, or look for the given nodes if aNodesList is not None

        :param aNodesList: list of node to look for, might be identifiers or .SBSNode
        :type aNodesList: list of str or list of :class:`.SBSCompNode`, optional
        :return: a list of :class:`.SBSCompNode` included in the graph
        """
        return self.mNodeList.getNodeList(aNodesList)

    @handle_exceptions()
    def getConnectionsFromNode(self, aLeftNode, aLeftNodeOutput=None):
        """
        getConnectionsFromNode(self, aLeftNode, aLeftNodeOutput=None)
        Get the connections starting from the given left node, from a particular output or for all its outputs.

        :param aLeftNode: the node to consider, as a SBSCompNode or given its uid
        :param aLeftNodeOutput: the pin output identifier to consider. If let None, all the outputs will be considered
        :type aLeftNode: :class:`.SBSCompNode` or str
        :type aLeftNodeOutput: :class:`.OutputEnum` or str, optional
        :return: a list of :class:`.SBSConnection`
        """
        nodes = self.getNodesConnectedFrom(aLeftNode, aLeftNodeOutput)
        connections = []
        for aNode in nodes:
            for aConn in aNode.getConnectionsFromNode(aLeftNode):
                if aLeftNodeOutput is not None and aConn.getConnectedNodeOutputUID() is not None:
                    if aLeftNode.getCompOutputIdentifier(aConn.getConnectedNodeOutputUID()) == aLeftNodeOutput:
                        connections.append(aConn)
                else:
                    connections.append(aConn)
        return connections

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
            aRightNodeInput = sbslibrary.getCompNodeInput(aRightNodeInput)
        return self.mNodeList.getConnectionsToNode(aRightNode, aRightNodeInput)

    @handle_exceptions()
    def getNodesConnectedFrom(self, aLeftNode, aLeftNodeOutput=None):
        """
        getNodesConnectedFrom(aLeftNode, aOutputIdentifier=None)
        Get all the nodes connected to the given output of the given node.
        If aOutputIdentifier is let None, consider all the outputs of the node.

        :param aLeftNode: the node to consider
        :param aLeftNodeOutput: the output to take in account
        :type aLeftNode: :class:`.SBSCompNode` or str
        :type aLeftNodeOutput: :class:`.OutputEnum` or str, optional
        :return: a list of :class:`.SBSCompNode`
        """
        connectedNodes = self.mNodeList.getNodesConnectedFrom(aLeftNode)

        if aLeftNodeOutput is not None:
            nodeDef = aLeftNode.getDefinition()
            outputDef = nodeDef.getOutput(aLeftNodeOutput)
            if outputDef is not None:
                connectedNodesFromOutput = []
                for n in connectedNodes:
                    for aConn in n.getConnections():
                        outputUID = aConn.getConnectedNodeOutputUID()
                        if aConn.getConnectedNodeUID() == aLeftNode.mUID and aLeftNode.getCompOutputIdentifier(
                                aCompOutputUID=outputUID) == aLeftNodeOutput and n not in connectedNodesFromOutput:
                            connectedNodesFromOutput.append(n)
                connectedNodes = connectedNodesFromOutput
            else:
                log.warning('No output named "%s" in the node %s',
                            python_helpers.castStr(aLeftNodeOutput),
                            aLeftNode.getDisplayName())

        return connectedNodes

    @handle_exceptions()
    def getNodesConnectedTo(self, aRightNode, aRightNodeInput=None):
        """
        getNodesConnectedTo(aRightNode, aRightNodeInput=None)
        Get all the nodes connected to the given input of the given node.
        If aInputIdentifier is let None, consider all the inputs of the node.

        :param aRightNode: the node to consider, as an object or given its uid
        :param aRightNodeInput: the input to take in account
        :type aRightNode: :class:`.SBSCompNode` or str
        :type aRightNodeInput: :class:`.InputEnum` or str, optional
        :return: a list of :class:`.SBSCompNode`
        """
        if isinstance(aRightNodeInput, int):
            aRightNodeInput = sbslibrary.getCompNodeInput(aRightNodeInput)
        return self.mNodeList.getNodesConnectedTo(aRightNode, aRightNodeInput)

    @handle_exceptions()
    def getNodesDockedTo(self, aRightNode):
        """
        getNodesDockedTo(aRightNode)
        Get all the nodes that are docked to the given node.

        :param aRightNode: the node to consider, as an object or given its uid
        :type aRightNode: :class:`.SBSCompNode`
        :return: a list of :class:`.SBSCompNode` corresponding to the nodes that are docked to the given node.
        """
        return self.mNodeList.getNodesDockedTo(aRightNode)

    @handle_exceptions()
    def moveConnectionsOnPinOutput(self, aInitialNode, aTargetNode, aInitialNodeOutput=None, aTargetNodeOutput=None):
        """
        moveConnectionsOnPinOutput(aInitialNode, aTargetNode, aInitialNodeOutput=None, aTargetNodeOutput=None)
        Allows to move all the connections connected to the given pin output of the given node to the target pin output of the target node.

        :param aInitialNode: the node initially connected, as an object or given its uid
        :param aTargetNode: the target node, which should be connected after this function, as an object or given its uid
        :param aInitialNodeOutput: the identifier of the output initially connected in aInitialNode. If None, the first output will be considered
        :param aTargetNodeOutput: the identifier of the output targeted on aTargetNode. If None, the first output will be considered
        :type aInitialNode: :class:`.SBSCompNode` or str
        :type aTargetNode: :class:`.SBSCompNode` or str
        :type aInitialNodeOutput: :class:`.OutputEnum` or str, optional
        :type aTargetNodeOutput: :class:`.OutputEnum` or str, optional
        :return:
        :raise: :class:`.SBSImpossibleActionError`
        """
        initialNode = self.getNode(aInitialNode)
        targetNode = self.getNode(aTargetNode)
        if initialNode is None or targetNode is None:
            raise SBSImpossibleActionError('Cannot modify connections, one of the two nodes is not found in the graph')

        initialOutput = initialNode.getCompOutputFromIdentifier(aInitialNodeOutput)
        targetOutput = targetNode.getCompOutputFromIdentifier(aTargetNodeOutput)
        if initialOutput is None:
            raise SBSImpossibleActionError('Cannot find the initial output on node '+initialNode.getDisplayName())
        if targetOutput is None:
            raise SBSImpossibleActionError('Cannot find the target output on node '+targetNode.getDisplayName())

        targetNodeOutputUID = None
        if aTargetNodeOutput is not None:
            targetNodeOutputUID = targetOutput.mUID if aTargetNode.isAnInstance() or aTargetNode.isAFilter() else None

        initialType = initialNode.getCompOutputType(initialOutput.mUID)
        targetType = targetNode.getCompOutputType(targetOutput.mUID)
        if not initialType & targetType:
            raise SBSImpossibleActionError('Cannot modify connections, the target output type is not compatible with the initial output type')

        connections = self.getConnectionsFromNode(aLeftNode=initialNode, aLeftNodeOutput=aInitialNodeOutput)
        for aConn in connections:
            aConn.setConnection(aTargetNode.mUID, targetNodeOutputUID)

    @handle_exceptions()
    def moveConnectionOnPinInput(self, aInitialNode, aTargetNode, aInitialNodeInput=None, aTargetNodeInput=None):
        """
        moveConnectionOnPinInput(aInitialNode, aTargetNode, aInitialNodeInput=None, aTargetNodeInput=None)
        Allows to move the connection connected to the given pin input of the given node to the target pin input of the target node.

        :param aInitialNode: the node initially connected, as an object or given its uid
        :param aTargetNode: the target node, which should be connected after this function, as an object or given its uid
        :param aInitialNodeInput: the identifier of the input initially connected in aInitialNode. If None, the first input will be considered
        :param aTargetNodeInput: the identifier of the input targeted on aTargetNode. If None, the first input will be considered
        :type aInitialNode: :class:`.SBSCompNode` or str
        :type aTargetNode: :class:`.SBSCompNode` or str
        :type aInitialNodeInput: :class:`.InputEnum` or str, optional
        :type aTargetNodeInput: :class:`.InputEnum` or str, optional
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
        connectedNodes = self.getNodesConnectedTo(aRightNode=initialNode, aRightNodeInput=aInitialNodeInput)
        if conn is None or not connectedNodes:
            raise SBSImpossibleActionError('No connection found on the input '+inputIdentifier+' of the node '+initialNode.getDisplayName())

        # Copy the connection on the target
        leftNode = connectedNodes[0]
        outputIdentifier = None
        if conn.getConnectedNodeOutputUID() is not None:
            outputIdentifier = leftNode.getCompOutputIdentifier(conn.getConnectedNodeOutputUID())
        self.connectNodes(aLeftNode=leftNode, aRightNode=targetNode, aLeftNodeOutput=outputIdentifier, aRightNodeInput=targetInputDef.getIdentifierStr())

        # Remove the previous connection
        initialNode.removeConnectionOnPin(inputIdentifier)

    @handle_exceptions()
    def getNodeAssociatedToComment(self, aComment):
        """
        getNodeAssociatedToComment(aComment)
        Get the node associated to the given comment.

        :param aComment: The comment to consider
        :type aComment: :class:`.SBSGUIObject`
        :return: the :class:`.SBSCompNode` if found, None otherwise
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
        :return: a list of :class:`.SBSCompNode`
        """
        return self.mGUIObjectList.getNodesInFrame(aFrame)

    @handle_exceptions()
    def getRect(self, aNodeList = None):
        """
        getRect(aNodeList = None)
        Get the rectangle occupied by all the nodes of this graph, or use only the given nodes if aNodeList is not None

        :param aNodeList: The list of node to take in account for the GUI rectangle. None to consider the node list pointed by itself.
        :type aNodeList: list of str or list of :class:`.SBSCompNode`, optional
        :return: A :class:`.Rect`
        """
        return self.mNodeList.getRect(aNodeList)

    @handle_exceptions()
    def getAllInputs(self):
        """
        getAllInputs()
        Get the list of all input parameters (images and variables) defined on this graph

        :return: a list of :class:`.SBSParamInput`
        """
        return Graph.getAllInputs(self)

    @handle_exceptions()
    def getAllInputsInGroup(self, aGroup):
        """
        getAllInputsInGroup(aGroup)
        | Get the list of all inputs (images and parameters) contained in the given group.
        | If aGroup is None, returns all the parameters that are not included in a group.

        :param aGroup: The group of parameter to consider
        :type aGroup: str
        :return: a list of :class:`.SBSParamInput`
        """
        return [aInput for aInput in self.getAllInputs() if aInput.getGroup() == aGroup]

    @handle_exceptions()
    def getInput(self, aInputIdentifier):
        """
        getInput(aInputIdentifier)
        Get the SBSParamInput with the given identifier, among the input images and input parameters

        :param aInputIdentifier: input parameter identifier
        :type aInputIdentifier: str
        :return: the corresponding :class:`.SBSParamInput` object if found, None otherwise
        """
        return Graph.getInput(self, aInputIdentifier)

    @handle_exceptions()
    def getInputFromUID(self, aInputUID):
        """
        getInputFromUID(aInputUID)
        Get the SBSParamInput with the given UID, among the input images and parameters

        :param aInputUID: input parameter UID
        :type aInputUID: str
        :return: the corresponding :class:`.SBSParamInput` object if found, None otherwise
        """
        return Graph.getInputFromUID(self, aInputUID)

    @handle_exceptions()
    def getInputImages(self):
        """
        getInputImages()
        Get the list of input images (inputs of kind ENTRY_COLOR | ENTRY_GRAYSCALE | ENTRY_VARIANT)

        :return: a list of :class:`.SBSParamInput`
        """
        return Graph.getInputImages(self)

    @handle_exceptions()
    def getInputImage(self, aInputImageIdentifier):
        """
        getInputImage(aInputImageIdentifier)
        Get the input image with the given identifier

        :param aInputImageIdentifier: input image identifier
        :type aInputImageIdentifier: str
        :return: a :class:`.SBSParamInput` if found, None otherwise
        """
        return Graph.getInputImage(self, aInputImageIdentifier)

    @handle_exceptions()
    def getInputImageFromInputNode(self, aInputNode):
        """
        getInputImageFromInputNode(aInputNode)
        Get the input image associated to the given input node

        :param aInputNode: the input node as a SBSCompNode or a UID
        :type aInputNode: :class:`.SBSCompNode` or str
        :return: The input image as a :class:`.SBSParamInput` if found, None otherwise
        """
        aNode = self.getNode(aInputNode)
        if aNode is None or not aNode.isAnInputBridge():
            return None
        return self.getInputFromUID(aNode.getCompInputBridge().mEntry)

    @handle_exceptions()
    def getInputImageWithUsage(self, aUsage):
        """
        getInputImageWithUsage(aUsage)
        Get the first input image which has the given usage defined

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.SBSParamInput` if found, None otherwise
        """
        return Graph.getInputImageWithUsage(self, aUsage)

    @handle_exceptions()
    def getInputParameter(self, aInputParamIdentifier):
        """
        getInputParameter(aInputIdentifier)
        Get the SBSParamInput with the given identifier, among the input parameters

        :param aInputParamIdentifier: input parameter identifier
        :type aInputParamIdentifier: str
        :return: the corresponding :class:`.SBSParamInput` object if found, None otherwise
        """
        return Graph.getInputParameter(self, aInputParamIdentifier)

    @handle_exceptions()
    def getInputParameterFromUID(self, aInputParamUID):
        """
        getInputParameterFromUID(aInputParamUID)
        Get the SBSParamInput with the given UID

        :param aInputParamUID: input parameter UID
        :type aInputParamUID: str
        :return: the corresponding :class:`.SBSParamInput` object if found, None otherwise
        """
        return Graph.getInputParameterFromUID(self, aInputParamUID)

    @handle_exceptions()
    def getInputParameters(self):
        """
        getInputParameters()
        Get the list of inputs parameters that are not input entries but numerical values

        :return: a list of :class:`.SBSParamInput`
        """
        return Graph.getInputParameters(self)

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
    def getPrimaryInput(self):
        """
        getPrimaryInput()
        Get the UID of the primary input of the graph

        :return: The UID of the primary input as a string if it exists, None otherwise
        """
        return self.mPrimaryInput

    @handle_exceptions()
    def isPrimaryInput(self, aInput):
        """
        isPrimaryInput(aInput)
        Check if the given input is the primary input for this graph or not

        :param aInput: The input to check
        :type aInput: :class:`.SBSParamInput`
        :return: True if this is the primary input, False otherwise
        """
        return self.getPrimaryInput() == aInput.mUID if aInput.mUID is not None else False

    @handle_exceptions()
    def setPrimaryInput(self, aUID):
        """
        setPrimaryInput(aUID)
        Set the UID of the primary input of the graph

        :param aUID: UID of the input to set as primary
        :type aUID: str
        """
        self.mPrimaryInput = aUID

    @handle_exceptions()
    def addInputParameter(self,
                          aIdentifier,
                          aWidget,
                          aDefaultValue = None,
                          aIsConnectable = None,
                          aOptions = None,
                          aDescription = None,
                          aLabel = None,
                          aGroup = None,
                          aUserData = None,
                          aVisibleIf = None):
        """
        addInputParameter(aIdentifier, aWidget, aDefaultValue, aOptions = None, aDescription = None, aLabel = None, aGroup = None, aUserData = None, aVisibleIf = None)
        Create a :class:`.SBSParamInput` with the given parameters and add it to the ParamsInput of the graph.

        :param aIdentifier: identifier of the input parameter
        :param aWidget: widget to use for this parameter
        :param aDefaultValue: default value
        :param aIsConnectable: Whether this parameter can be connected for value computation
        :param aOptions: options
        :param aDescription: textual description
        :param aLabel: GUI label for this input parameter
        :param aGroup: string that contains a group name. Can uses path with '/' separators.
        :param aUserData: user tags
        :param aVisibleIf: string bool expression based on graph inputs values
        :type aIdentifier: str
        :type aWidget: :class:`.WidgetEnum`
        :type aIsConnectable: bool, optional
        :type aDefaultValue: str, optional
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
                                                        aDefaultValue = aDefaultValue,
                                                        aIsConnectable = aIsConnectable,
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
    def getGraphOutputs(self):
        """
        getGraphOutputs()
        Get all the graph outputs

        :return: the list of :class:`.SBSGraphOutput` defined on this graph
        """
        return Graph.getGraphOutputs(self)

    @handle_exceptions()
    def getGraphOutput(self, aOutputIdentifier):
        """
        getGraphOutput(aOutputIdentifier)
        Get the graph output with the given identifier

        :param aOutputIdentifier: identifier of the output
        :type aOutputIdentifier: str
        :return: a :class:`.SBSGraphOutput` object if found, None otherwise
        """
        return Graph.getGraphOutput(self, aOutputIdentifier)

    @handle_exceptions()
    def getGraphOutputNode(self, aOutputIdentifier):
        """
        getGraphOutputNode(aOutputIdentifier)
        Get the output node which corresponds to the graph output with the given identifier

        :param aOutputIdentifier: identifier of the output
        :type aOutputIdentifier: str
        :return: a :class:`.SBSCompNode` object if found, None otherwise
        """
        graphOutput = self.getGraphOutput(aOutputIdentifier)
        if graphOutput is not None:
            return next((outputNode for outputNode in self.getAllOutputNodes()
                         if outputNode.mCompImplementation.mCompOutputBridge.mOutput == graphOutput.mUID), None)
        return None

    @handle_exceptions()
    def getGraphOutputFromOutputNode(self, aOutputNode):
        """
        getGraphOutputFromOutputNode(aOutput)
        Get the graph output corresponding to the given output node

        :param aOutputNode: The output node, as a SBSCompNode or given its UID
        :type aOutputNode: :class:`.SBSCompNode` or str
        :return: the corresponding :class:`.SBSGraphOutput` if found, None otherwise
        """
        aNode = self.getNode(aOutputNode)
        if aNode is None or not aNode.isAnOutputBridge():
            return None
        return self.getGraphOutputFromUID(aOutputNode.getCompOutputBridge().mOutput)

    @handle_exceptions()
    def getGraphOutputFromUID(self, aOutputUID):
        """
        getGraphOutputFromUID(aOutputUID)
        Get the graph output with the given UID

        :param aOutputUID: UID of the output to get
        :type aOutputUID: str
        :return: a :class:`.SBSGraphOutput` object if found, None otherwise
        """
        return next((output for output in self.getGraphOutputs() if output.mUID == aOutputUID), None)

    @handle_exceptions()
    def getGraphOutputWithUsage(self, aUsage):
        """
        getGraphOutputWithUsage(aUsage)
        Get the first GraphOutput which has the given usage defined

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.SBSGraphOutput` if found, None otherwise
        """
        return Graph.getGraphOutputWithUsage(self, aUsage)

    @handle_exceptions()
    def getGraphOutputType(self, aOutputIdentifier):
        """
        getGraphOutputType(aOutputIdentifier)
        Get the output type of the GraphOutput with the given identifier

        :param aOutputIdentifier: identifier of the output
        :type aOutputIdentifier: str
        :return: the output type in the format :class:`.ParamTypeEnum` if found, None otherwise
        """
        aGraphOutput = self.getGraphOutput(aOutputIdentifier)
        return aGraphOutput.getType() if aGraphOutput is not None else None

    @handle_exceptions()
    def getFirstInputOfType(self, aType):
        """
        getFirstInputOfType(aType)
        Get the first ParamInput with the given type. This considers the variant types as compatible types.

        :param aType: The required type
        :type aType: sbsenum.ParamTypeEnum
        :return: a :class:`.SBSParamInput` object if found, None otherwise
        """
        return next((param for param in self.getAllInputs() if param.mType & aType), None)

    @handle_exceptions()
    def getFirstOutputOfType(self, aType):
        """
        getFirstOutputOfType(aType)
        Get the first GraphOutput with the given type. This considers the variant types as compatible types.

        :param aType: The required type
        :type aType: sbsenum.ParamTypeEnum
        :return: a :class:`.SBSGraphOutput` object if found, None otherwise
        """
        return next((output for output in self.getGraphOutputs() if self.getGraphOutputType(output.mIdentifier) & aType), None)

    @handle_exceptions()
    @deprecated(__name__, '2019.1.0', 'Renamed for consistency with SBSGraph.getGraphOutputType()', 'Please use setGraphOutputType instead')
    def setOutputChannel(self, aGraphOutputUID, aType):
        """
        setOutputChannel(aGraphOutputUID, aType)
        Set the output channel type of the :class:`.SBSGraphOutput` with the given uid

        :param aGraphOutputUID: UID of the graph output to consider
        :param aType: Channel type to set
        :type aGraphOutputUID: str
        :type aType: :class:`.ParamTypeEnum`
        """
        self.setGraphOutputType(aGraphOutputUID, aType)

    @handle_exceptions()
    def setGraphOutputType(self, aGraphOutputUID, aType):
        """
        setGraphOutputType(aGraphOutputUID, aType)
        Set the output channel type of the :class:`.SBSGraphOutput` with the given uid

        :param aGraphOutputUID: UID of the graph output to consider
        :param aType: type to set
        :type aGraphOutputUID: str
        :type aType: :class:`.ParamTypeEnum`
        """
        output = next((output for output in self.getGraphOutputs() if output.mUID == aGraphOutputUID), None)
        if output is not None:
            # If equals to the default value, reset to None
            if aType == sbsenum.ParamTypeEnum.ENTRY_COLOR:
                output.mChannels = None
            else:
                output.mChannels = str(aType)

    @handle_exceptions()
    def getBaseParameterValue(self, aParameter):
        """
        getBaseParameterValue(aParameter)
        Find a parameter with the given name/id among the overloaded parameters and the default graph parameters,
        and return its value.

        :param aParameter: Parameter identifier
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: The parameter value if found (string or :class:`.SBSDynamicValue`, None otherwise
        """
        if not python_helpers.isStringOrUnicode(aParameter):
            aParameterName = sbslibrary.getCompNodeParam(aParameter)
        else:
            aParameterName = aParameter

        # Parse the parameters overloaded on the CompFilter node
        if self.mBaseParameters:
            param = next((param for param in self.mBaseParameters if param.mName == aParameterName), None)
            if param is not None:
                return param.mParamValue.getValue()

        # Parse the default parameters of the graph
        aGraphDefaultParams = sbslibrary.getFilterDefinition(sbsenum.FilterEnum.COMPINSTANCE)
        defaultParam = aGraphDefaultParams.getParameter(aParameter)
        if defaultParam is not None:
            return defaultParam.mDefaultValue

        return None

    @handle_exceptions()
    def setBaseParameterValue(self, aParameter, aParamValue, aRelativeTo = sbsenum.ParamInheritanceEnum.ABSOLUTE):
        """
        setBaseParameterValue(aParameter, aParamValue, aRelativeTo = sbsenum.ParamInheritanceEnum.ABSOLUTE)
        Set the value of the given parameter to the given value.

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :param aRelativeTo: Inheritance of the parameter. Default is ABSOLUTE

        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aParamValue: :class:`.SBSDynamicValue` or any parameter type
        :type aRelativeTo: :class:`.ParamInheritanceEnum`

        :return: True if succeed, False otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        # Get Parameter name
        if not python_helpers.isStringOrUnicode(aParameter):
            aParameterName = sbslibrary.getCompNodeParam(aParameter)
        else:
            aParameterName = aParameter
        if aParameterName is None:
            raise SBSLibraryError('Parameter '+str(aParameter)+' cannot be set on a graph')

        # Parse the default input parameter of the input node
        aGraphDefaultParams = sbslibrary.getFilterDefinition(sbsenum.FilterEnum.COMPINSTANCE)
        defaultParam = aGraphDefaultParams.getParameter(aParameter)
        aType = defaultParam.mType if defaultParam is not None else None
        if aType is None:
            raise SBSLibraryError('Parameter '+aParameterName+' cannot be set on a graph')

        isDynamic = isinstance(aParamValue, params.SBSDynamicValue)

        # Ensure having a correctly formatted value
        if not isDynamic:
            aParamValue = api_helpers.formatValueForTypeStr(aParamValue, defaultParam.mType)

        # Parse the parameters already defined on the graph and modify it if found
        if self.mBaseParameters:
            param = next((param for param in self.mBaseParameters if param.mName == aParameterName), None)
            if param is not None:
                if isDynamic:
                    param.mParamValue.setDynamicValue(aParamValue)
                else:
                    param.mParamValue.updateConstantValue(aParamValue)
                return True

        # Create a new parameter
        aSBSParamValue = params.SBSParamValue()
        if isDynamic:   aSBSParamValue.setDynamicValue(aParamValue)
        else:           aSBSParamValue.setConstantValue(aType, aParamValue)
        aNewParam = params.SBSParameter(aName = aParameterName, aRelativeTo = str(aRelativeTo), aParamValue = aSBSParamValue)
        api_helpers.addObjectToList(self, 'mBaseParameters', aNewParam)
        return True

    @handle_exceptions()
    def setDynamicBaseParameter(self, aParameter, aRelativeTo = None):
        """
        setDynamicBaseParameter(aParameter, aRelativeTo = None)
        Set the given parameter as dynamic, to init its params.SBSDynamicValue.
        If Inheritance is None, the default Inheritance is set.

        :param aParameter: identifier of the parameter
        :param aRelativeTo: Inheritance of the parameter
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aRelativeTo: :class:`.ParamInheritanceEnum`
        :return: the :class:`.SBSDynamicValue` object if succeed, None otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        # Get Parameter name
        if not python_helpers.isStringOrUnicode(aParameter):
            aParameterName = sbslibrary.getCompNodeParam(aParameter)
        else:
            aParameterName = aParameter
        if aParameterName is None:
            raise SBSLibraryError('Parameter '+str(aParameter)+' cannot be set on a graph')

        # Parse the parameters already defined on this comp filter and modify it if found
        if self.mBaseParameters:
            param = next((param for param in self.mBaseParameters if param.mName == aParameterName), None)
            if param is not None:
                return param.createEmptyDynamicValue()

        # Parse the default input parameter of an input bridge
        aGraphDefaultParams = sbslibrary.getFilterDefinition(sbsenum.FilterEnum.COMPINSTANCE)
        defaultParam = aGraphDefaultParams.getParameter(aParameter)
        if defaultParam is None:
            raise SBSLibraryError('Parameter '+aParameterName+' cannot be set on a graph')

        # Create a new parameter
        aInheritance = aGraphDefaultParams.mInheritance[0] if aRelativeTo is None else aRelativeTo

        aNewParam = params.SBSParameter(aName = aParameterName, aRelativeTo = str(aInheritance))
        aDynValue = aNewParam.createEmptyDynamicValue()
        api_helpers.addObjectToList(self, 'mBaseParameters', aNewParam)
        return aDynValue

    @handle_exceptions()
    def computeUniqueInputIdentifier(self, aIdentifier, aSuffixId = 0):
        """
        computeUniqueInputIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used in the graph inputs and generate a unique identifier if necessary

        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier_id
        """
        return self._computeUniqueIdentifier(aIdentifier, aListsToCheck= [self.mParamInputs], aSuffixId= aSuffixId)

    @handle_exceptions()
    def computeUniqueOutputIdentifier(self, aIdentifier, aSuffixId = 0):
        """
        computeUniqueOutputIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used in the graph outputs and generate a unique identifier if necessary

        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier_id
        """
        return self._computeUniqueIdentifier(aIdentifier, aListsToCheck= [self.mGraphOutputs], aSuffixId= aSuffixId)

    @handle_exceptions()
    def contains(self, aNode):
        """
        contains(aNode)
        Check if the given node belongs to this graph

        :param aNode: The node to check, as a, object or an UID
        :type aNode: :class:`.SBSCompNode` or str
        :return: True if the given node belongs to the node list, False otherwise
        """
        return self.mNodeList.contains(aNode)

    @handle_exceptions()
    def createBitmapNode(self, aSBSDocument,
                         aResourcePath,
                         aGUIPos = None,
                         aParameters = None,
                         aInheritance = None,
                         aResourceGroup = 'Resources',
                         aCookedFormat = None,
                         aCookedQuality = None,
                         aAttributes=None,
                         aAutodetectImageParameters = True):
        """
        createBitmapNode(aSBSDocument, aResourcePath, aGUIPos = None, aParameters = None, aInheritance = None, aResourceGroup = 'Resources', aCookedFormat = None, aCookedQuality = None)
        Create a new 'bitmap' node and add it to the CompNodes of the graph. Create the referenced resource if necessary, as a Linked resource.
        If you want to import the resource, use first SBSDocument.createImportedResource() and then SBSGraph.createBitmapNode() with the internal path to the imported resource (pkg:///...).

        :param aSBSDocument: current edited document
        :param aResourcePath: internal (*pkg:///MyGroup/MyResourceIdentifier*), relative (to the current package) or absolute path to the bitmap resource to display in the bitmap
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the Bitmap node
        :param aInheritance: Inheritance of the parameters
        :param aResourceGroup: SBSGroup or identifier of the group where the resource will be added (the group is created if necessary).\
        Default to 'Resources'. Put None to create the resource at the root of the package.
        :param aCookedFormat: if a resource is created, it will be used to set the cooked format of the resource. Default value is RAW
        :param aCookedQuality: if a resource is created, it will be used to set the cooked quality of the resource. Default value is 0
        :param aAttributes: if a resource is created, will be set as the attributes of the resource
        :param aAutodetectImageParameters: Autodetect and set resolution and bitdepth for the bitmap.

        :type aSBSDocument: :class:`.SBSDocument`
        :type aResourcePath: str
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(sbsenum.ParamInheritanceEnum)}, optional
        :type aResourceGroup: :class:`.SBSGroup` or str, optional
        :type aCookedFormat: :class:`.BitmapFormatEnum`, optional
        :type aCookedQuality: float, optional
        :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value(str)}, optional
        :type aAutodetectImageParameters: bool
        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        aCompNode = sbsgenerator.createResourceNode(aFilter = sbsenum.FilterEnum.BITMAP,
                                                    aSBSDocument = aSBSDocument,
                                                    aParentGraph = self,
                                                    aParameters = aParameters,
                                                    aInheritance = aInheritance,
                                                    aResourcePath = aResourcePath,
                                                    aResourceGroup = aResourceGroup,
                                                    aCookedFormat = aCookedFormat,
                                                    aCookedQuality = aCookedQuality,
                                                    aAttributes = aAttributes,
                                                    aAutodetectImageParameters = aAutodetectImageParameters)


        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createSvgNode(self, aSBSDocument,
                            aResourcePath,
                            aGUIPos = None,
                            aParameters = None,
                            aInheritance = None,
                            aResourceGroup = 'Resources',
                            aCookedQuality = None):
        """
        createSvgNode(aSBSDocument, aResourcePath, aGUIPos = None, aParameters = None, aInheritance = None, aResourceGroup = 'Resources', aCookedQuality = None)
        Create a new 'svg' node and add it to the CompNodes of the graph. Create the referenced resource if necessary, as a Linked resource.
        If you want to import the resource, use first SBSDocument.createImportedResource() and then SBSGraph.createSvgNode() with the relative path to the imported resource.

        :param aSBSDocument: current edited document
        :param aResourcePath: internal (*pkg:///MyGroup/MyResourceIdentifier*), relative (to the current package) or absolute path to the SVG resource to display in the node
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the Bitmap node
        :param aInheritance: Inheritance of the parameters
        :param aResourceGroup: SBSGroup or identifier of the group where the resource will be added (the group is created if necessary). \
        Default to 'Resources'. Put None to create the resource at the root of the package.
        :param aCookedQuality: default value is 0

        :type aSBSDocument: :class:`.SBSDocument`
        :type aResourcePath: str
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(sbsenum.ParamInheritanceEnum)}, optional
        :type aResourceGroup: :class:`.SBSGroup` or str, optional
        :type aCookedQuality: float, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0, 0, 0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        aCompNode = sbsgenerator.createResourceNode(aFilter = sbsenum.FilterEnum.SVG,
                                                    aSBSDocument = aSBSDocument,
                                                    aParentGraph = self,
                                                    aParameters = aParameters,
                                                    aInheritance = aInheritance,
                                                    aResourcePath = aResourcePath,
                                                    aResourceGroup = aResourceGroup,
                                                    aCookedQuality = aCookedQuality)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createCompFilterNode(self, aFilter, aGUIPos = None, aParameters = None, aInheritance = None):
        """
        createCompFilterNode(aFilter, aGUIPos = None, aParameters = None, aInheritance = None)
        Create a new compositing node filter and add it to the CompNodes of the graph.

        Note:
            - For a Bitmap node, use :func:`createBitmapNode` instead.
            - For a SVG node, use :func:`createSvgNode` instead.
            - For a Gradient Map node, use :func:`createGradientMapNode` instead.
            - For a Curve node, use :func:`createCurveNode` instead.
            - For a Text node, use :func:`createTextNode` instead.

        :param aFilter: filter type among the list defined in sbsenum.FilterEnum
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the filter node
        :param aInheritance: Inheritance of the parameters

        :type aFilter: :class:`.FilterEnum`
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        aCompNode = sbsgenerator.createCompFilterNode(aParentGraph = self,
                                                      aFilter = aFilter,
                                                      aParameters = aParameters,
                                                      aInheritance = aInheritance)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createCurveNode(self, aGUIPos = None, aParameters = None, aInheritance = None, aCurveDefinitions = None):
        """
        createCurveNode(aGUIPos = None, aParameters = None, aInheritance = None, aCurveDefinitions = None)
        Create a new Curve filter and add it to the CompNodes of the graph.

        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the filter node
        :param aInheritance: inheritance of the parameters
        :param aCurveDefinitions: curve definitions

        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
        :type aCurveDefinitions: list of :class:`.CurveDefinition`, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}
        if aCurveDefinitions is None: aCurveDefinitions = []

        aCompNode = sbsgenerator.createCompFilterNode(aParentGraph = self,
                                                      aFilter = sbsenum.FilterEnum.CURVE,
                                                      aParameters = aParameters,
                                                      aInheritance = aInheritance)

        for aCurveDef in aCurveDefinitions:
            aCompNode.setCurveDefinition(aCurveDef)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createGradientMapNode(self, aGUIPos = None, aParameters = None, aInheritance = None, aKeyValues = None):
        """
        createGradientMapNode(aGUIPos = None, aParameters = None, aInheritance = None, aKeyValues = None)
        Create a new Gradient Map filter and add it to the CompNodes of the graph.

        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the filter node
        :param aInheritance: Inheritance of the parameters
        :param aKeyValues: gradient key values

        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
        :type aKeyValues: list of :class:`.GradientKey`, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}
        if aKeyValues is None: aKeyValues = []

        aCompNode = sbsgenerator.createCompFilterNode(aParentGraph = self,
                                                      aFilter = sbsenum.FilterEnum.GRADIENT,
                                                      aParameters = aParameters,
                                                      aInheritance = aInheritance)

        aCompNode.setGradientMapKeyValues(aKeyValues)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createTextNode(self, aFontFamily = 'Arial', aFontSubFamily = None, aGUIPos = None, aParameters = None, aInheritance = None):
        """
        createTextNode(aGUIPos = None, aParameters = None, aInheritance = None, aCurveDefinitions = None)
        Create a new Curve filter and add it to the CompNodes of the graph.

        :param aFontFamily: font family to use for this text. It can be the name of a font, for instance 'Arial', \
        or an internal path to a font resource (*pkg:///myFontResourceIdentifier*). Default to 'Arial'
        :param aFontSubFamily: font subfamily to use for this text. Default to None, which corresponds to the Regular font. \
        For instance: 'Bold','Italic', ... Beware of the compatibility of the font subfamily with the provided font.
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the filter node
        :param aInheritance: inheritance of the parameters

        :type aFontFamily: str, optional
        :type aFontSubFamily: str, optional
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        aFont = aFontFamily + '|' + aFontSubFamily if aFontSubFamily is not None else aFontFamily
        aParameters[sbsenum.CompNodeParamEnum.TEXT_FONT] = aFont
        aCompNode = sbsgenerator.createCompFilterNode(aParentGraph = self,
                                                      aFilter = sbsenum.FilterEnum.TEXT,
                                                      aParameters = aParameters,
                                                      aInheritance = aInheritance)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createInputNode(self, aIdentifier,
                        aColorMode = sbsenum.ColorModeEnum.COLOR,
                        aGUIPos = None,
                        aAttributes = None,
                        aIsConnectable = True,
                        aUsages = None,
                        aSetAsPrimary = False,
                        aParameters = None,
                        aInheritance = None,
                        aGroup = None,
                        aVisibleIf = None):
        """
        createInputNode(aIdentifier, aColorMode = sbsenum.ColorModeEnum.COLOR, aGUIPos = None, aAttributes = None, aUsages = None, aSetAsPrimary = False, aParameters = None, aInheritance = None)
        Create a new compositing node input with the appropriate color and add it to the CompNode list of the graph.
        Declare it as PrimaryInput if this is the first input node.
        Declare the new :class:`.SBSParamInput`

        :param aIdentifier: input identifier. It may change to ensure having a unique identifier.
        :param aColorMode: color or grayscale. Default is COLOR
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aAttributes: output attributes list
        :param aUsages: usage of this output
        :param aSetAsPrimary: True to define this input as the PrimaryInput of the graph. Even if False, the input will be set as the PrimaryInput if this is the first input of the graph
        :param aParameters: parameters of the input node
        :param aInheritance: Inheritance of the parameters
        :param aGroup: GUI group name. Can uses path with '/' separators.
        :param aVisibleIf: Condition of visibility of this input

        :type aIdentifier: str
        :type aColorMode: :class:`.ColorModeEnum`, optional
        :type aGUIPos: list of 3 float, optional
        :type aAttributes: dictionary {:class:`.AttributesEnum` : AttributeName(str)}, optional
        :type aUsages: dictionary {:class:`.UsageEnum` : :class:`.ComponentsEnum`}, optional
        :type aSetAsPrimary: bool, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional
        :type aGroup: str, optional
        :type aVisibleIf: str, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        uniqueIdentifier = self.computeUniqueInputIdentifier(api_helpers.formatIdentifier(aIdentifier))
        aCompNode = sbsgenerator.createInputNode(aParentGraph = self,
                                                 aIdentifier = uniqueIdentifier,
                                                 aColorMode = aColorMode,
                                                 aAttributes = aAttributes,
                                                 aIsConnectable = aIsConnectable,
                                                 aUsages = aUsages,
                                                 aSetAsPrimary = aSetAsPrimary,
                                                 aParameters = aParameters,
                                                 aInheritance = aInheritance,
                                                 aGroup = aGroup,
                                                 aVisibleIf = aVisibleIf)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createOutputNode(self, aIdentifier,
                         aGUIPos = None,
                         aAttributes = None,
                         aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,
                         aMipmaps = None,
                         aUsages = None,
                         aGroup = None,
                         aVisibleIf = None):
        """
        createOutputNode(aIdentifier, aGUIPos = None, aAttributes = None, aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,  aMipmaps = None, aUsages = None, aGroup = None)
        Create a new compositing node output and add it to the CompNodes of the graph.
        Declare the new RootOutput and GraphOutput

        :param aIdentifier: output identifier
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aAttributes: output attributes list
        :param aOutputFormat: output format. Default value is DEFAULT_FORMAT
        :param aMipmaps: mipmaps level. default value is FULL_PYRAMID
        :param aUsages: usage of this output
        :param aGroup: GUI group of this output
        :param aVisibleIf: Condition of visibility of this output

        :type aIdentifier: str
        :type aGUIPos: list of 3 float, optional
        :type aAttributes: dictionary {:class:`.AttributesEnum` : AttributeName(str)}, optional
        :type aOutputFormat: :class:`.TextureFormatEnum`, optional
        :type aMipmaps: sbsenum.MipmapEnum, optional
        :type aUsages: dictionary {:class:`.UsageEnum` : :class:`.ComponentsEnum`}, optional
        :type aGroup: str
        :type aVisibleIf: str, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        uniqueIdentifier = self.computeUniqueOutputIdentifier(api_helpers.formatIdentifier(aIdentifier))
        aCompNode = sbsgenerator.createOutputNode(aParentGraph = self,
                                                  aIdentifier = uniqueIdentifier,
                                                  aOutputFormat = aOutputFormat,
                                                  aMipmaps = aMipmaps,
                                                  aAttributes = aAttributes,
                                                  aUsages = aUsages,
                                                  aGroup = aGroup,
                                                  aVisibleIf = aVisibleIf)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createCompInstanceNode(self, aSBSDocument, aGraph, aGUIPos = None, aParameters = None, aInheritance = None):
        """
        createCompInstanceNode(aSBSDocument, aGraph, aGUIPos = None, aParameters = None, aInheritance = None)
        Create a new compositing node instance which references the given graph, and add it to the CompNodes of the current graph.

        Note:
            - The graph must be defined in the given SBSDocument.
            - Use :func:`createCompInstanceNodeFromPath` to add an instance of a graph included in an external package.

        :param aSBSDocument: current edited document
        :param aGraph: graph that will be referenced by the instance node
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the filter node
        :param aInheritance: Inheritance of the parameters

        :type aSBSDocument: :class:`.SBSDocument`
        :type aGraph: :class:`.SBSGraph`
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional

        :return: The new :class:`.SBSCompNode` object
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        # Check if the graph belongs to the current SBSDocument
        aGraphRelPath = aSBSDocument.getSBSGraphInternalPath(aUID = aGraph.mUID, addDependencyUID=True)
        if aGraphRelPath is None:
            raise SBSImpossibleActionError('The graph to instantiate must be included in the given document')

        aCompNode = sbsgenerator.createCompInstanceNode(aParentGraph = self,
                                                        aGraph = aGraph,
                                                        aPath = aGraphRelPath,
                                                        aDependency = aSBSDocument.getHimselfDependency(),
                                                        aParameters = aParameters,
                                                        aInheritance = aInheritance)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createCompInstanceNodeFromPath(self, aSBSDocument, aPath, aGUIPos = None, aParameters = None, aInheritance = None):
        """
        createCompInstanceNodeFromPath(aSBSDocument, aPath, aGUIPos = None, aParameters = None, aInheritance = None)
        Create a new compositing node instance which references the graph pointed by the given path, and add it to the CompNodes of the graph.

        :param aSBSDocument: current edited document
        :param aPath: path of the graph definition (absolute, relative to the current .sbs file, or given with an alias, for instance *sbs://anisotropic_noise.sbs*)

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.

        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :param aParameters: parameters of the filter node
        :param aInheritance: Inheritance of the parameters

        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :type aGUIPos: list of 3 float, optional
        :type aParameters: dictionary {parameter(:class:`.CompNodeParamEnum`) : parameterValue(str)}, optional
        :type aInheritance: dictionary with the format {parameterName(:class:`.CompNodeParamEnum`) : parameterInheritance(:class:`.ParamInheritanceEnum`)}, optional

        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}
        if aInheritance is None: aInheritance = {}

        # Get/Create the dependency and the reference to the pointed graph
        outValues = aSBSDocument.getOrCreateDependency(aPath, aAllowSBSAR=True)
        if len(outValues) != 3:
            raise SBSImpossibleActionError('Failed to create instance of graph '+python_helpers.castStr(aPath))

        aGraph = outValues[0]
        aGraphRelPath = outValues[1]
        aDependency = outValues[2]

        # Create the comp instance node
        aCompNode = sbsgenerator.createCompInstanceNode(aParentGraph = self,
                                                        aGraph = aGraph,
                                                        aPath = aGraphRelPath,
                                                        aDependency = aDependency,
                                                        aParameters = aParameters,
                                                        aInheritance = aInheritance)

        if aCompNode.mGUILayout is not None:
            aCompNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mCompNodes', aCompNode)

        return aCompNode

    @handle_exceptions()
    def createComment(self, aCommentText='Comment', aGUIPos=None, aLinkToNode=None):
        """
        createComment(aCommentText='Comment', aGUIPos=None, aLinkToNode=None)
        Create a new comment.\
        If aLinkToNode is not None, this comment will be linked to the given node, and the given GUI position must be relative to this node.

        :param aCommentText: The text of the comment. Default to 'Comment'
        :param aGUIPos: The comment position in the graph. Default to [0,0,0]
        :param aLinkToNode: The node to associate to this comment, as a SBSCompNode or given its UID
        :type aCommentText: str, optional
        :type aGUIPos: list of 3 float, optional
        :type aLinkToNode: :class:`.SBSCompNode` or str, optional
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
        :type aNodeList: list of class:`.SBSCompNode`
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
        :type aNodeList: list of class:`.SBSCompNode`
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
    def connectNodes(self, aLeftNode, aRightNode, aLeftNodeOutput = None, aRightNodeInput = None):
        """
        connectNodes(aLeftNode, aRightNode, aLeftNodeOutput = None, aRightNodeInput = None)
        Connect the given nodes together: aLeftNode(on the output aLeftNodeOutput) -> aRightNode(on the input aRightNodeInput).
        If the right node input is None, the connection will be done on the first input of the right node.
        If the left node output is None, the connection will be done on the first compatible output of the left node.

        :param aLeftNode: Node to connect from, as a SBSCompNode or given its UID
        :param aRightNode: Node to connect to, as a SBSCompNode or given its UID
        :param aLeftNodeOutput: Identifier of the output of the left node
        :param aRightNodeInput: Identifier of the input of the right node

        :type aLeftNode: :class:`.SBSCompNode` or str
        :type aRightNode: :class:`.SBSCompNode` or str
        :type aLeftNodeOutput: :class:`.OutputEnum` or str, optional
        :type aRightNodeInput: :class:`.InputEnum` or str, optional

        :return: The connection if success, None otherwise (in case of type incompatibility for instance)
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        def __isEntry(type):
            return (type & sbsenum.TypeMasksEnum.ENTRY) != 0
        def __typeMatches(type1, type2):
            return (type1 & type2) != 0
        # Check that the given nodes belongs to the graph
        leftNode = self.getNode(aLeftNode)
        rightNode = self.getNode(aRightNode)
        if leftNode is None or rightNode is None or not leftNode.mCompOutputs:
            raise SBSImpossibleActionError('Impossible to connect node '+str(aLeftNode)+' to '+str(aRightNode)+', one of them is not found in the graph')

        # Check that the connection will not create a cycle in the DAG
        if self.isAPathBetween(aLeftNode = rightNode, aRightNode = leftNode):
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', it would create a cycle')

        # Get the comp nodes parameters (input entries, parameters, outputs)
        aLeftNodeDefinition = leftNode.getDefinition()
        aRightNodeDefinition = rightNode.getDefinition()
        if aRightNodeDefinition is None or aLeftNodeDefinition is None:
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', failed to get a definition')

        # Find the appropriate CompOutput on the left node
        aLeftOutput = None
        # Only one output => take it (all filters have only one output)
        aLeftType = None
        if len(leftNode.mCompOutputs) == 1:
            aLeftOutput = leftNode.mCompOutputs[0]
        # If left output identifier is given => get the output from the output bridging with this identifier
        elif aLeftNodeOutput is not None and leftNode.isAnInstance():
            aLeftOutput = leftNode.getCompOutputFromBridge(aLeftNodeOutput)
            if not aLeftOutput:
                raise SBSImpossibleActionError('Output %s doesn\'t exist on node %s' % (aLeftNodeOutput, aLeftNode.getDisplayName()))
        if aLeftOutput:
            aLeftType = int(aLeftOutput.mCompType)

        # Find the appropriate CompNodeInput on the right node
        aRightInputDef = None
        if aRightNodeInput is not None:
            aRightInputDef = aRightNodeDefinition.getInput(aRightNodeInput)
            if aRightInputDef is None:
                aRightInputDef = aRightNodeDefinition.getParameter(aRightNodeInput)
                if aRightInputDef and not aRightInputDef.getIsConnectable():
                    raise SBSImpossibleActionError(
                        'Impossible to connect node ' + leftNode.getDisplayName() + ' to ' + rightNode.getDisplayName() +
                        ', right input is not connectable')
            if aRightInputDef is None:
                raise SBSImpossibleActionError(
                    'Impossible to connect node ' + leftNode.getDisplayName() + ' to ' + rightNode.getDisplayName() +
                    ', cannot find on which input to connect them')
        else:
            # Only one input => take it
            if not aLeftType or (__isEntry(aLeftType) and len(aRightNodeDefinition.mInputs) == 1):
                aRightInputDef = aRightNodeDefinition.mInputs[0]
            # If left output is defined => take the first compatible input
            elif aLeftType is not None:
                aRightInputDef = aRightNodeDefinition.getFirstInputOfType(aLeftType)
            # If left node not defined and is an instance => take the first compatibles input and output
            elif leftNode.isAnInstance():
                for o,i in [(o,i) for o in aLeftNodeDefinition.mOutputs for i in aRightNodeDefinition.mInputs
                    if o.mType == i.mType]:
                        aLeftOutput = leftNode.getCompOutputFromBridge(o.mIdentifier)
                        if aLeftOutput is not None:
                            aRightInputDef = i
                            break
                aLeftType = int(aLeftOutput.mCompType)
        # If the left output is still undefined, find the first compatible output
        if aLeftOutput is None and aRightInputDef is not None and leftNode.isAnInstance():
            for o in [o for o in aLeftNodeDefinition.mOutputs if o.mType & aRightInputDef.mType]:
                aLeftOutput = leftNode.getCompOutputFromBridge(o.mIdentifier)
                if aLeftOutput is not None:
                    aLeftType = int(aLeftOutput.mCompType)
                    break

        if aLeftOutput is None or aRightInputDef is None:
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+
                                           ', cannot find on which input/output to connect them')

        aRightType = int(aRightInputDef.mType)

        if not __typeMatches(aLeftType, aRightType):
            raise SBSImpossibleActionError(
                'Impossible to connect node ' + leftNode.getDisplayName() + ' to ' + rightNode.getDisplayName() +
                ', Trying to connect values and images')

        if isinstance(aRightInputDef, sbslibrary.CompNodeInput):
            # This is an ordinary input (as opposed to to a parameter input)
            if not python_helpers.isStringOrUnicode(aRightInputDef.mIdentifier):
                aRightInputIdentifier = sbslibrary.getCompNodeInput(aRightInputDef.mIdentifier)
            else:
                aRightInputIdentifier = aRightInputDef.mIdentifier
        else:
            aRightInputIdentifier = aRightInputDef.mParameter

        # Check the type compatibility
        aLeftNodeType = int(aLeftOutput.mCompType)
        if aLeftNodeType != aRightInputDef.mType and not aRightInputDef.isVariant():
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', types are incompatible')

        # Do the connection: Create a new connection or modify the existing one on the right input
        aConn = rightNode.getConnectionOnPin(aRightInputIdentifier)
        if aConn is None:
            aConn = sbscommon.SBSConnection(aIdentifier   = aRightInputIdentifier,
                                            aConnRef      = leftNode.mUID,
                                            aConnRefOutput= aLeftOutput.mUID)
            api_helpers.addObjectToList(rightNode, 'mConnections', aConn)

        else:
            aConn.setConnection(leftNode.mUID, aLeftOutput.mUID)

        # In case of Variant output on the right node, propagate the type from left node
        if aRightNodeDefinition.isVariant() and aRightInputDef.isVariant():
            if rightNode.mCompOutputs:
                rightNode.mCompOutputs[0].mCompType = str(aLeftNodeType)
            elif rightNode.isAnOutputBridge():
                self.setGraphOutputType(rightNode.mCompImplementation.mCompOutputBridge.mOutput, aLeftNodeType)
        return aConn


    @handle_exceptions()
    def disconnectNodes(self, aLeftNode, aRightNode, aLeftNodeOutput = None, aRightNodeInput = None):
        """
        disconnectNodes(aLeftNode, aRightNode, aLeftNodeOutput = None, aRightNodeInput = None)
        Disconnect the given nodes: aLeftNode(on the output aLeftNodeOutput) -> aRightNode(on the input aRightNodeInput).
        If the left node output and the right node input are None, all the connections will be removed.

        :param aLeftNode: Left node, as a SBSCompNode or given its UID
        :param aRightNode: Right node, as a SBSCompNode or given its UID
        :param aLeftNodeOutput: Identifier of the output of the left node
        :param aRightNodeInput: Identifier of the input of the right node

        :type aLeftNode: :class:`.SBSCompNode` or str
        :type aRightNode: :class:`.SBSCompNode` or str
        :type aLeftNodeOutput: :class:`.OutputEnum` or str, optional
        :type aRightNodeInput: :class:`.InputEnum` or str, optional

        :return: Nothing
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Check that the given nodes belongs to the graph
        leftNode = self.getNode(aLeftNode)
        rightNode = self.getNode(aRightNode)
        if leftNode is None or rightNode is None or not leftNode.mCompOutputs:
            raise SBSImpossibleActionError('Impossible to disconnect node '+str(aLeftNode)+' to '+str(aRightNode))

        # Remove all connections
        if aLeftNodeOutput is None and aRightNodeInput is None:
            rightNode.removeConnectionsFrom(leftNode)
        # Remove only the connection on the given input/output pins
        else:
            connectionsFrom = self.getConnectionsFromNode(aLeftNode=leftNode, aLeftNodeOutput=aLeftNodeOutput)
            connectionsTo = self.getConnectionsToNode(aRightNode=rightNode, aRightNodeInput=aRightNodeInput)
            connectionsToRemove = list(set(connectionsFrom).intersection(set(connectionsTo)))

            for aConn in connectionsToRemove:
                rightNode.removeConnectionOnPin(aConn.mIdentifier)

    @handle_exceptions()
    def copyCompNode(self, aCompNode):
        """
        copyCompNode(aCompNode)
        Create a simple copy of the given CompNode with a new UID.

        :param aCompNode: the node to copy
        :type aCompNode: :class:`.SBSCompNode`
        :return: The new :class:`.SBSCompNode` object
        """
        return self.mNodeList.copyNode(aCompNode)

    @handle_exceptions()
    def duplicateNode(self, aCompNode, aGUIOffset = None):
        """
        duplicateNode(aCompNode, aGUIOffset = None)
        Duplicate the given node, generate a new UID and add the node to the same node list than the source node.

        :param aCompNode: the node to copy (may be identified by its UID)
        :param aGUIOffset: node position offset. Default to [150, 0]
        :type aCompNode: :class:`.SBSCompNode` or str
        :type aGUIOffset: list of 2 float, optional
        :return: The new :class:`.SBSCompNode` object
        """
        if aGUIOffset is None: aGUIOffset = [150, 0]
        return self.mNodeList.duplicateNode(aCompNode, aGUIOffset)

    @handle_exceptions()
    def createIterationOnNode(self, aNbIteration,
                              aNodeUID,
                              aForceRandomSeed = False,
                              aIncrementIteration = False,
                              aGUIOffset = None):
        """
        createIterationOnNode(aNbIteration, aNodeUID, aForceRandomSeed = False, aIncrementIteration = False, aGUIOffset = None)
        Duplicate NbIteration times the given node, and connect each node with the previous one to create this kind of connection:

        Node -> Node_1 -> Node_2 -> ... -> Node_N

        :param aNbIteration: number of time the node must be duplicated
        :param aNodeUID: the UID of the node to duplicate
        :param aForceRandomSeed: specify if a different random seed must be generated for each iteration. Default to False
        :param aIncrementIteration: specify if the parameter 'iteration' must be incremented at each iteration. Default to False
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aNbIteration: positive integer
        :type aNodeUID: str
        :type aForceRandomSeed: bool, optional
        :type aIncrementIteration: bool, optional
        :type aGUIOffset: list of 2 float, optional

        :return: The list of :class:`.SBSCompNode` objects created (including the nodes given in aNodeUIDs_NextPatternInput), None if failed
        """
        if aGUIOffset is None: aGUIOffset = [150, 0]

        # Generate iterations with this single node pattern
        return self.createIterationOnPattern(aNbIteration,
                                             aNodeUIDs = [aNodeUID],
                                             aForceRandomSeed = aForceRandomSeed,
                                             aIncrementIteration = aIncrementIteration,
                                             aGUIOffset = aGUIOffset)

    @handle_exceptions()
    def createIterationOnPattern(self, aNbIteration,
                                 aNodeUIDs,
                                 aNodeUIDs_NextPattern = None,
                                 aForceRandomSeed = False,
                                 aIncrementIteration = False,
                                 aGUIOffset = None):
        """
        createIterationOnPattern(aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern = None, aForceRandomSeed = False, aIncrementIteration = False, aGUIOffset = None)
        | Duplicate NbIteration times the given pattern of compositing nodes, and connect each pattern with the
            previous one to create this kind of connection:
        | Pattern -> Pattern_1 -> Pattern_2 -> ... -> Pattern_N
        | It allows to completely define the way two successive patterns are connected.
        | For instance, provide aNodeUIDs = [A, B, C] and aNodeUIDs_NextPatternInput = [A'],
            if the pattern is A -> B -> C, and if C is connected to A'.
        | If aNodeUIDs_NextPatternInput is let empty, the function will try to connect the successive patterns
            by the most obvious way, respecting the input / output type (color / grayscale)

        :param aNbIteration: number of time the pattern must be duplicated
        :param aNodeUIDs: list of node's UID that constitute the pattern to duplicate
        :param aNodeUIDs_NextPattern: list of node's UID that correspond to the next pattern, which must be connected to the given pattern. Default to []
        :param aForceRandomSeed: specify if a different random seed must be generated for each iteration. Default to False
        :param aIncrementIteration: specify if the parameter 'iteration' must be incremented at each iteration. Default to False
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aNbIteration: positive integer
        :type aNodeUIDs: list of str
        :type aNodeUIDs_NextPattern: list of str, optional
        :type aForceRandomSeed: bool, optional
        :type aIncrementIteration: bool, optional
        :type aGUIOffset: list of 2 float, optional

        :return: The list of :class:`.SBSCompNode` objects created (including the nodes given in aNodeUIDs_NextPatternInput), None if failed
        """
        if aGUIOffset is None: aGUIOffset = [150, 0]

        return sbsgenerator.createIterationOnPattern(aParentObject = self,
                                                     aNbIteration = aNbIteration,
                                                     aNodeUIDs = aNodeUIDs,
                                                     aNodeUIDs_NextPattern = aNodeUIDs_NextPattern,
                                                     aForceRandomSeed = aForceRandomSeed,
                                                     aIncrementIteration = aIncrementIteration,
                                                     aGUIOffset = aGUIOffset)

    @handle_exceptions()
    def deleteInputParameter(self, aInputParameter):
        """
        deleteInputParameter(aInputParameter)
        Allows to delete the given input parameter. If this is an input image, remove the corresponding Input node.

        :param aInputParameter: The input parameter to remove.
        :type aInputParameter: :class:`.SBSParamInput` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if isinstance(aInputParameter, SBSParamInput):
            aInputIdentifier = aInputParameter.mIdentifier
        else:
            aInputIdentifier = aInputParameter
            aInputParameter = self.getInput(aInputIdentifier)

        if not isinstance(aInputParameter, SBSParamInput) or not aInputParameter in self.mParamInputs:
            raise SBSImpossibleActionError('Impossible to remove input parameter '+python_helpers.castStr(aInputIdentifier)+' from this graph, \
cannot find this input in the graph')

        # In case of an input image, remove the associated node in the graph
        if aInputParameter.isAnInputImage():
            aNode = self.getGraphInputNode(aInputImageIdentifier=aInputParameter.mIdentifier)
            if aNode:
                return self.deleteNode(aNode)
        self.mParamInputs.remove(aInputParameter)
        return True

    @handle_exceptions()
    def deleteNode(self, aNode):
        """
        deleteNode(aNode)
        Allows to delete the given node from the graph.
        It removes it from the CompNode list, and delete all the connection from and to that node in the graph.

        :param aNode: The node to remove, as a SBSCompNode or an UID.
        :type aNode: :class:`.SBSCompNode` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aNodeToDelete = self.getNode(aNode)
        if aNodeToDelete is None:
            raise SBSImpossibleActionError('Impossible to delete the node '+python_helpers.castStr(aNode)+', cannot find it in the graph')

        # Input node: remove the input parameter
        if aNodeToDelete.isAnInputBridge():
            aInputImage = self.getInputImageFromInputNode(aNodeToDelete)
            if aInputImage is not None:
                self.mParamInputs.remove(aInputImage)

        # Output node: remove the graph output
        elif aNodeToDelete.isAnOutputBridge():
            aGraphOutput = self.getGraphOutputFromOutputNode(aNodeToDelete)
            if aGraphOutput is not None:
                self.mGraphOutputs.remove(aGraphOutput)
                if self.mRoot:
                    self.mRoot.deleteRootOutput(aGraphOutput.mUID)

        return self.mNodeList.deleteNode(aNode)

    @handle_exceptions()
    def deletePreset(self, aPreset):
        """
        deletePreset(aPreset)
        Allows to delete the given preset.

        :param aPreset: The preset to remove, as a SBSPreset object or identified by its label.
        :type aPreset: :class:`.SBSPreset` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if isinstance(aPreset, SBSPreset):
            aPresetLabel = aPreset.mLabel
        else:
            aPresetLabel = aPreset
            aPreset = self.getPreset(aPresetLabel=aPresetLabel)

        try:
            self.mPresets.remove(aPreset)
            return True
        except:
            raise SBSImpossibleActionError('Impossible to remove the preset '+str(aPresetLabel)+' from this graph')

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
        :type aLeftNode: :class:`.SBSCompNode` or str
        :type aRightNode: :class:`.SBSCompNode` or str
        :return: True if a path is found, False otherwise
        """
        return self.mNodeList.isAPathBetween(aLeftNode, aRightNode)

    @handle_exceptions()
    def getInputImageIndex(self, aInputImageIdentifier):
        """
        getInputImageIndex(aInputImageIdentifier)
        Get the index of the given input image, among the list of ParamInput of kind image.

        :param aInputImageIdentifier: input image identifier
        :type aInputImageIdentifier: str
        :return: the index of the input image as an integer if found, -1 otherwise
        """
        return next((aIndex for aIndex,aInput in enumerate(self.getInputImages())
                        if aInput.mIdentifier == aInputImageIdentifier), -1)

    @handle_exceptions()
    def setInputImageIndex(self, aInputImageIdentifier, aIndex):
        """
        setInputImageIndex(aInputImageIdentifier, aIndex)
        Set the index of the ParamInput of kind image with the given identifier

        :param aInputImageIdentifier: input image identifier
        :param aIndex: index to set, in the range [0 ; nbInputImages[
        :type aInputImageIdentifier: str
        :type aIndex: int
        :raise: :class:`api_exceptions.SBSImpossibleActionError` if failed
        """
        if not 0 <= aIndex < len(self.getInputImages()):
            raise SBSImpossibleActionError('The provided index in not in the range [0; nbInputImages[')
        currentIndex = next((aIndex for aIndex,aInput in enumerate(self.getAllInputs())
                        if aInput.mIdentifier == aInputImageIdentifier), -1)
        if currentIndex == -1:
            raise SBSImpossibleActionError('Cannot find the given input image in the graph')
        aParamInput = self.mParamInputs.pop(currentIndex)

        targetIndex = 0
        inputImageIndex = 0
        for aParam in self.getAllInputs():
            if aIndex == inputImageIndex:
                break
            if aParam.isAnInputImage():
                inputImageIndex += 1
            targetIndex += 1
        self.mParamInputs.insert(targetIndex, aParamInput)

    @handle_exceptions()
    def getInputParameterIndex(self, aInputParamIdentifier):
        """
        getInputParameterIndex(aInputParamIdentifier)
        Get the index of the given input parameter, among the list of ParamInput of kind variable.

        :param aInputParamIdentifier: input parameter identifier
        :type aInputParamIdentifier: str
        :return: the index of the input parameter as an integer if found, -1 otherwise
        """
        return next((aIndex for aIndex,aInput in enumerate(self.getInputParameters())
                        if aInput.mIdentifier == aInputParamIdentifier), -1)

    @handle_exceptions()
    def setInputParameterIndex(self, aInputParamIdentifier, aIndex):
        """
        setInputParameterIndex(aInputParamIdentifier, aIndex)
        Set the index of the given input parameter among the list of ParamInput of kind variable

        :param aInputParamIdentifier: input parameter identifier
        :param aIndex: index to set, in the range [0 ; nbInputParameters[
        :type aInputParamIdentifier: str
        :type aIndex: int
        :raise: :class:`api_exceptions.SBSImpossibleActionError` if failed
        """
        if not 0 <= aIndex < len(self.getInputParameters()):
            raise SBSImpossibleActionError('The provided index in not in the range [0; nbInputParameters[')
        currentIndex = next((aIndex for aIndex,aInput in enumerate(self.getAllInputs())
                        if aInput.mIdentifier == aInputParamIdentifier), -1)
        if currentIndex == -1:
            raise SBSImpossibleActionError('Cannot find the given input parameter in the graph')
        aParamInput = self.mParamInputs.pop(currentIndex)

        targetIndex = 0
        inputParamIndex = 0
        for aParam in self.getAllInputs():
            if aIndex == inputParamIndex:
                break
            if not aParam.isAnInputImage():
                inputParamIndex += 1
            targetIndex += 1
        self.mParamInputs.insert(targetIndex, aParamInput)

    @handle_exceptions()
    def getAllowedAttributes(self):
        """
        getAllowedAttributes()
        Get the attributes allowed on a SBSGraph

        :return: the list of attribute enumeration allowed (:class:`.AttributesEnum`)
        """
        return SBSGraph.__sAttributes

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
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
    def setAttributes(self, aAttributes):
        """
        setAttributes(aAttributes)
        Set the given attributes

        :param aAttributes: The attributes to set
        :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value}
        """
        if self.mAttributes is None:
            self.mAttributes = sbscommon.SBSAttributes()
        self.mAttributes.setAttributes(aAttributes, self)

    def getIcon(self):
        """
        getIcon()
        Get the icon associated to this graph

        :return: The icon as a :class:`.SBSIcon` if it exists, None otherwise
        """
        return self.getAttribute(sbsenum.AttributesEnum.Icon)

    def getIconBytes(self):
        """
        getIconBytes()
        Get the icon stream bytes

        :return: The icon image data as bytes if possible, None otherwise
        """
        aIcon = self.getIcon()
        if aIcon is None:
            return None
        try:
            nob64 = base64.b64decode(aIcon.mStrdata)[4:]
            return zlib.decompress(nob64)
        except BaseException as error:
            log.warning(error)
            return None

    def setIcon(self, aIconAbsPath):
        """
        setIcon(aIconAbsPath)
        Set the given image as the icon of the graph.
        The provided image won't be re-sized to get a thumbnail, so we strongly recommend that you provide the path to a 128x128 image.

        :param aIconAbsPath: The absolute path of the image to set
        :type aIconAbsPath: str
        :return: The :class:`.SBSIcon` object created
        """
        aIcon = sbsgenerator.createIcon(aIconAbsPath)
        self.setAttribute(sbsenum.AttributesEnum.Icon, aIcon)
        return aIcon

    def getDefaultParentSize(self):
        """
        getDefaultParentSize()
        Get the default parent size option of this graph.

        :return: The parent size, as a list of two :class:`.OutputSizeEnum`: [width,height]. If not defined, return the default value [SIZE_256,SIZE_256]
        """
        sizeOpt = self.getOption(aOptionName='defaultParentSize')
        if not sizeOpt:
            return [sbsenum.OutputSizeEnum.SIZE_256,sbsenum.OutputSizeEnum.SIZE_256]
        else:
            return api_helpers.getTypedValueFromStr(sizeOpt.mValue, sbsenum.ParamTypeEnum.INTEGER2, aSep='x')

    def setDefaultParentSize(self, aWidth, aHeight):
        """
        setDefaultParentSize(aWidth, aHeight)
        Set the default parent size option on this graph.

        :param aWidth: The default parent width
        :param aHeight: The default parent height
        :type aWidth: :class:`.OutputSizeEnum`
        :type aHeight: :class:`.OutputSizeEnum`
        """
        strValue = api_helpers.formatValueForTypeStr([aWidth, aHeight], aType=sbsenum.ParamTypeEnum.INTEGER2, aSep='x')
        self.setOption(aOptionName='defaultParentSize', aOptionValue=strValue)

    def getOptions(self):
        """
        getOptions()
        Get the list of options defined in this graph.

        :return: a list of :class:`.SBSOption`
        """
        return self.mOptions if self.mOptions else []

    def getOption(self, aOptionName):
        """
        getOption(aOptionName)
        Get the option with the given name.

        :param aOptionName: the name of the option to get, as saved in the .sbs file
        :type aOptionName: str
        :return: the corresponding :class:`.SBSOption` object if found, None otherwise
        """
        return next((opt for opt in self.getOptions() if opt.mName == aOptionName), None)

    def getPsdExporterOptions(self):
        """
        getPsdExporterOptions()
        Get the list of options related to the PSD exporter defined in this graph.

        :return: a list of :class:`.SBSOption`
        """
        return [aOption for aOption in self.getOptions() if aOption.mName.startswith('psd/')]

    def setOption(self, aOptionName, aOptionValue):
        """
        setOption(aOptionName, aOptionValue)
        Set the given option with the given value.

        :param aOptionName: the name of the option to set, as saved in the .sbs file
        :param aOptionValue: the value of the option to set, as saved in the .sbs file
        :type aOptionName: str
        :type aOptionValue: str
        :return: the created or modified :class:`.SBSOption` object
        """
        aOption = self.getOption(aOptionName)
        if aOption is None:
            aOption = sbscommon.SBSOption(aName = aOptionName, aValue = aOptionValue)
            api_helpers.addObjectToList(self, 'mOptions', aOption)
        else:
            aOption.mValue = aOptionValue
        return aOption

    @handle_exceptions()
    def sortNodesAsDAG(self):
        """
        sortNodesAsDAG()
        Sort the CompNode list of the graph to order them as a DAG. The member mCompNodes is updated.

        :return: the sorted node list.
        """
        return self.mNodeList.sortNodesAsDAG()

    def getUserData(self, aNode):
        """
        Easy way to get userData / userTags associated to an outputCompNode or an inputCompNode.
        :param aNode: the associated node or UID node.
        :type aNode: :class:`.SBSCompNode` or str
        :return:the userTags value as str
        """
        node = self.getNode(aNode)
        if not node:
            return None
        if isinstance(node.getCompImplementation(), compimplementation.SBSCompOutputBridge):
            root = self.mRoot
            rootOutput = root.getRootOutput(node.getCompImplementation().mOutput)
            if not rootOutput:
                return None
            return rootOutput.mUserTag
        elif isinstance(node.getCompImplementation(), compimplementation.SBSCompInputBridge):
            param = next((i for i in self.mParamInputs if i.mUID == node.getCompImplementation().mEntry), None) if self.mParamInputs else None
            return param.mAttributes.mUserTags
        else:
            return None

    def setUserData(self, aNode, data):
        """
        Easy way to set userData / userTags associated to an outputCompNode or an inputCompNode.
        :param aGraph: the graph where live the node.
        :type aGraph: :class:`.SBSGraph`
        :param aData: the data to set as value
        :type aData: str
        :return: bool
        """
        node = self.getNode(aNode)
        if not node:
            return False
        if not isinstance(data, str):
            raise SBSImpossibleActionError('Data argument must be of type string.')
        if isinstance(node.getCompImplementation(), compimplementation.SBSCompOutputBridge):
            root = self.mRoot
            rootOutput = root.getRootOutput(node.getCompImplementation().mOutput)
            if not rootOutput:
                return False
            rootOutput.mUserTag = data
            return True
        elif isinstance(node.getCompImplementation(), compimplementation.SBSCompInputBridge):
            param = next((i for i in self.mParamInputs if i.mUID == node.getCompImplementation().mEntry), None) if self.mParamInputs else None
            if not param.mAttributes:
                param.mAttributes = sbscommon.values.SBSAttributes()
            param.mAttributes.mUserTags = data
            return True
        else:
            return False
