# coding: utf-8
"""
Module **mdlgraph** aims to define SBSObjects that are relative to a MDL graph,
mostly :class:`.MDLGraph` and :class:`.MDLInput`.
"""

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import base64
import zlib

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import api_helpers
from pysbs.common_interfaces import SBSObject, BaseGraph
from pysbs import python_helpers
from pysbs import sbsenum
from pysbs import sbscommon
from pysbs import sbsgenerator

from . import MDLNode, MDLAnnotation
from . import mdlenum, mdl_helpers
from .mdlcommon import MDLObjectWithAnnotations
from .mdlmanager import MDLManager


@doc_inherit
class MDLInput(SBSObject):
    """
    Class that contains the uid of an MDL input as saved in a .sbs file

    Members:
        * mNodeUID  (str): UID of the MDL Node corresponding to this input
    """
    def __init__(self, aNodeUID = ''):
        super(MDLInput, self).__init__()
        self.mNodeUID = aNodeUID

        self.mMembersForEquality = []

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mNodeUID    = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'nodeuid')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mNodeUID, 'nodeuid' )


#=======================================================================
@doc_inherit
class MDLGraph(SBSObject, BaseGraph, MDLObjectWithAnnotations):
    """
    Class that contains information on a MDL graph as defined in a .sbs file

    Members:
        * mIdentifier     (str): name of the graph (name of the definition and the instance if applicable).
        * mUID            (str): unique identifier in the package/ context.
        * mAttributes     (:class:`.SBSAttributes`): various attributes
        * mAnnotations    (list of :class:`.MDLAnnotation`): list of annotations.
        * mParamInputs    (list of :class:`.MDLInput`): list of exposed parameters of the graph.
        * mNodes          (list of :class:`.MDLNode`): the list of MDL node of the graph.
        * mGUIObjects     (list of :class:`.SBSGUIObject`, optional): list of GUI specific objects (comments, ...).
        * mRoot           (str, optional): UID of the root node of the graph (the output)
    """
    __sAttributes = [sbsenum.AttributesEnum.Category,
                     sbsenum.AttributesEnum.HideInLibrary,
                     sbsenum.AttributesEnum.Icon]
    __sAnnotations = [mdlenum.MDLAnnotationEnum.AUTHOR,
                      mdlenum.MDLAnnotationEnum.CONTRIBUTOR,
                      mdlenum.MDLAnnotationEnum.COPYRIGHT,
                      mdlenum.MDLAnnotationEnum.DESCRIPTION,
                      mdlenum.MDLAnnotationEnum.DISPLAY_NAME,
                      mdlenum.MDLAnnotationEnum.HIDDEN,
                      mdlenum.MDLAnnotationEnum.IN_GROUP,
                      mdlenum.MDLAnnotationEnum.KEYWORDS]

    def __init__(self,
                 aIdentifier    = '',
                 aUID           = '',
                 aAttributes    = None,
                 aAnnotations   = None,
                 aParamInputs   = None,
                 aNodes         = None,
                 aGUIObjects    = None,
                 aRoot          = '0'):
        SBSObject.__init__(self)
        BaseGraph.__init__(self, aIdentifier=aIdentifier,
                                aParamInputs=aParamInputs)
        MDLObjectWithAnnotations.__init__(self, aAllowedAnnotations=MDLGraph.__sAnnotations, aAnnotations=aAnnotations)

        self.mUID           = aUID
        self.mAttributes    = aAttributes
        self.mNodes         = aNodes if aNodes is not None else []
        self.mGUIObjects    = aGUIObjects
        self.mRoot          = aRoot

        self.mNodeList = sbscommon.NodeList(self, MDLNode, 'mNodes')
        self.mGUIObjectList = sbscommon.GUIObjectList(self, 'mGUIObjects')

        self.mMembersForEquality = ['mIdentifier',
                                    'mAttributes',
                                    'mAnnotations',
                                    'mParamInputs',
                                    'mNodes']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier  = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'identifier'     )
        self.mUID         = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'            )
        self.mAttributes  = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'attributes'     , sbscommon.SBSAttributes)
        self.mAnnotations = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'mdl_annotations', 'mdl_annotation', MDLAnnotation)
        self.mParamInputs = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'inputs'         , 'mdl_input'     , MDLInput)
        self.mNodes       = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'nodes'          , 'mdl_node'      , MDLNode)
        self.mGUIObjects  = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'gui_objects'    , 'GUIObject'     , sbscommon.SBSGUIObject)
        self.mRoot        = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'root_node_uid'  )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIdentifier  , 'identifier'      )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUID         , 'uid'             )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mAttributes  , 'attributes'      )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mAnnotations , 'mdl_annotations' ,    'mdl_annotation'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mNodes       , 'nodes'           ,    'mdl_node'        )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mGUIObjects  , 'gui_objects'     ,    'GUIObject'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mRoot        , 'root_node_uid'   )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mParamInputs , 'inputs'          ,    'mdl_input'       )


    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Check if the given uid is already used in the context of the graph

        :param aUID: UID to check
        :type aUID: str
        :return: True if the uid is already used, False otherwise
        """
        listToParse = [self.mNodes,self.mGUIObjects]
        for aList,aObject in [(aList,aObject) for aList in listToParse if aList is not None for aObject in aList]:
            if aObject.mUID == aUID:
                return True
        return False

    @handle_exceptions()
    def getAllowedAttributes(self):
        """
        getAllowedAttributes()
        Get the attributes allowed on a MDLGraph

        :return: the list of attribute enumeration allowed (:class:`.AttributesEnum`)
        """
        return MDLGraph.__sAttributes

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        return self.mAttributes.getAttribute(aAttributeIdentifier) if self.mAttributes is not None else None

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
    def getAllMDLConstants(self):
        """
        getAllMDLConstants()
        Search for all :class:`.MDLNode` which are constants (:class:`.MDLImplConstant` implementation).

        :return: a list of :class:`.MDLNode` that are constants.
        """
        return [node for node in self.getNodeList() if node.isAConstant()]

    @handle_exceptions()
    def getAllMDLConstantsWithName(self, aName):
        """
        getAllMDLConstantsWithName(aName)
        Search for all :class:`.MDLNode` which are constants (:class:`.MDLImplConstant` implementation) with the given name.

        :param aName: the constant name to search
        :type aName: str
        :return: a list of :class:`.MDLNode` that are constants with the given name.
        """
        return [node for node in self.getAllMDLConstants() if node.getMDLImplConstant().getIdentifier() == aName]

    @handle_exceptions()
    def getAllMDLConstantsOfType(self, aType):
        """
        getAllMDLConstantsOfType(aType)
        Search for all :class:`.MDLNode` which are constants (:class:`.MDLImplConstant` implementation) of the given type.

        :param aType: the type of constant to search
        :type aType: str
        :return: a list of :class:`.MDLNode` that are constants of the given type.
        """
        return [node for node in self.getAllMDLConstants() if node.getMDLImplConstant().getOutputType() == aType]

    @handle_exceptions()
    def getAllMDLSelectors(self):
        """
        getAllMDLSelectors()
        Search for all :class:`.MDLNode` which are selectors (:class:`.MDLImplSelector` implementation).

        :return: a list of :class:`.MDLNode` that are selectors.
        """
        return [node for node in self.getNodeList() if node.isASelector()]

    @handle_exceptions()
    def getAllMDLSelectorsWithName(self, aName):
        """
        getAllMDLSelectorsWithName(aName)
        Search for all :class:`.MDLNode` which are selectors (:class:`.MDLImplSelector` implementation) of the given member name.

        :param aName: the selected member name to search
        :type aName: str
        :return: a list of :class:`.MDLNode` that are selectors of the given member name.
        """
        return [node for node in self.getAllMDLSelectors() if node.getMDLImplSelector().mName == aName]

    @handle_exceptions()
    def getAllMDLSelectorsOfType(self, aType):
        """
        getAllMDLSelectorsOfType(aType)
        Search for all :class:`.MDLNode` which are selectors (:class:`.MDLImplSelector` implementation) of the given type.

        :param aType: the selected member type to search
        :type aType: str
        :return: a list of :class:`.MDLNode` that are selectors of the given type.
        """
        return [node for node in self.getAllMDLSelectors() if node.getMDLImplSelector().getOutputType() == aType]

    @handle_exceptions()
    def getAllMDLInstances(self):
        """
        getAllMDLInstances()
        Search for all :class:`.MDLNode` which are instances of a native MDL function/material (:class:`.MDLImplMDLInstance` implementation).

        :return: a list of :class:`.MDLNode` that are native MDL instances.
        """
        return [node for node in self.getNodeList() if node.isMDLInstance()]

    @handle_exceptions()
    def getAllMDLInstancesOf(self, aPath):
        """
        getAllMDLInstancesOf(aPath)
        Search for all :class:`.MDLNode` which are instances of the given MDL function/material (:class:`.MDLImplMDLInstance` implementation), given its path.

        :param aPath: the MDL path to search
        :type aPath: str
        :return: a list of :class:`.MDLNode` that are MDL instances of the given MDL function/material.
        """
        return [node for node in self.getAllMDLInstances() if node.getMDLImplMDLInstance().isAnInstanceOf(aPath)]

    @handle_exceptions()
    def getAllMDLGraphInstances(self):
        """
        getAllMDLGraphInstances()
        Search for all :class:`.MDLNode` which are instances of a MDL graph (:class:`.MDLImplMDLGraphInstance` implementation).

        :return: a list of :class:`.MDLNode` that are instances of a MDL graph.
        """
        return [node for node in self.getNodeList() if node.isMDLGraphInstance()]

    @handle_exceptions()
    def getAllMDLGraphInstancesOf(self, aSBSDocument, aPath):
        """
        getAllMDLGraphInstancesOf(aSBSDocument, aPath)
        Search for all :class:`.MDLNode` with a :class:`.MDLImplMDLGraphInstance` implementation, which reference the given MDL graph path.

        :param aSBSDocument: current SBSDocument
        :param aPath: path of the graph definition (absolute, relative to the current .sbs file, or given with an alias, for instance *sbs://anisotropic_noise.sbs*)

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.
        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :return: a list of :class:`.MDLNode` that are instances of the given MDL graph.
        """
        absPath = aSBSDocument.convertToAbsolutePath(aPath)
        if aSBSDocument.isAPackage(absPath):
            posSep = absPath.rfind('/')
            graphName = aSBSDocument.removePackageExtension(absPath[posSep+1:])
            absPath += '/' + graphName

        return [node for node in self.getAllMDLGraphInstances() if node.getMDLImplMDLGraphInstance().getReferenceAbsPath() == absPath]

    @handle_exceptions()
    def getAllSBSInstances(self):
        """
        getAllSBSInstances()
        Search for all :class:`.MDLNode` which are an instance of a Substance graph (:class:`.MDLImplSBSInstance` implementation).

        :return: a list of :class:`.MDLNode` that are instances of a Substance graph.
        """
        return [node for node in self.getNodeList() if node.isSBSInstance()]

    @handle_exceptions()
    def getAllSBSInstancesOf(self, aSBSDocument, aPath):
        """
        getAllSBSInstancesOf(aSBSDocument, aPath)
        Search for all :class:`.MDLNode` with a :class:`.MDLImplSBSInstance` implementation, which reference the given Substance graph path.

        :param aSBSDocument: current SBSDocument
        :param aPath: path of the graph definition (absolute, relative to the current .sbs file, or given with an alias, for instance *sbs://anisotropic_noise.sbs*)

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.
        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :return: a list of :class:`.MDLNode` that are instances of the given Substance graph.
        """
        absPath = aSBSDocument.convertToAbsolutePath(aPath)
        if aSBSDocument.isAPackage(absPath):
            posSep = absPath.rfind('/')
            graphName = aSBSDocument.removePackageExtension(absPath[posSep+1:])
            absPath += '/' + graphName

        return [node for node in self.getAllSBSInstances() if node.getMDLImplSBSInstance().getReferenceAbsPath() == absPath]

    @handle_exceptions()
    def getAllDependencyUID(self):
        """
        getAllDependencyUID()
        Get the UIDs of the dependencies used by this MDL graph

        :return: a list of UIDs as strings
        """
        dependencySet = set()

        # Parse all nodes of the graph
        for aNode in self.getNodeList():
            # MDL Graph Instance or SBS Instance => Get the dependency
            if aNode.isMDLGraphInstance() or aNode.isSBSInstance():
                dependencySet.add(aNode.getMDLImplementation().getDependencyUID())
            # Resources
            for aPath in aNode.getResourcesPath():
                aDepUID = api_helpers.splitPathAndDependencyUID(aPath)[1]
                if aDepUID:
                    dependencySet.add(aDepUID)

        return sorted(list(dependencySet))

    @handle_exceptions()
    def getAllReferencesOnDependency(self, aDependency):
        """
        getAllReferencesOnDependency(aDependency)
        Get all the MDLNode that are referencing the given dependency

        :param aDependency: The dependency to look for (UID or object)
        :type aDependency: str or :class:`.SBSDependency`
        :return: A list of :class:`.MDLNode`
        """
        return [aNode for aNode in self.getNodeList() if aNode.hasAReferenceOnDependency(aDependency)]

    @handle_exceptions()
    def getAllReferencesOnResource(self, aResource):
        """
        getAllReferencesOnResource(aResource)
        Get all the MDLNode that are referencing the given resource

        :param aResource: The resource to look for (object or path internal to the package (pkg:///myGroup/myResource)
        :type aResource: str or :class:`.SBSResource`
        :return: A list of :class:`.MDLNode`
        """
        aPath = aResource if python_helpers.isStringOrUnicode(aResource) else aResource.getPkgResourcePath()
        return [aNode for aNode in self.getNodeList() if aNode.useResource(aPath)]

    @handle_exceptions()
    def getAllResourcesUsed(self):
        """
        getAllResourcesUsed()
        Get the list of resources used in this graph as a list of paths relative to the package

        :return: the list of resources used in this graph as a list of paths relative to the package (pkg:///...)
        """
        resourcePaths = []
        for aPath in [aPath for aNode in self.getNodeList() for aPath in aNode.getResourcesPath()]:
            if aPath not in resourcePaths:
                resourcePaths.append(aPath)
        return resourcePaths

    @handle_exceptions()
    def getCommentsAssociatedToNode(self, aNode):
        """
        getCommentsAssociatedToNode(aNode)
        Get the list of comments associated to the given node

        :param aNode: The node to consider, as a MDLNode or given its UID
        :type aNode: :class:`.MDLNode` or str
        :return: a list of :class:`.SBSGUIObject`
        """
        aUID = aNode.mUID if isinstance(aNode, MDLNode) else aNode
        return [aComment for aComment in self.getAllComments() if aComment.hasDependencyOn(aUID)]

    @handle_exceptions()
    def getNode(self, aNode):
        """
        getNode(aNode)
        Search for the given compositing node in the node list

        :param aNode: node to get, identified by its uid or as a :class:`.MDLNode`
        :type aNode: :class:`.MDLNode` or str
        :return: A :class:`.MDLNode` object if found, None otherwise
        """
        return self.mNodeList.getNode(aNode)

    @handle_exceptions()
    def getNodeList(self, aNodesList = None):
        """
        getNodeList(aNodesList = None)
        Get all the MDL nodes of this graph, or look for the given nodes if aNodesList is not None

        :param aNodesList: list of node to look for
        :type aNodesList: list of str or list of :class:`.MDLNode`, optional
        :return: a list of :class:`.MDLNode` included in the graph
        """
        return self.mNodeList.getNodeList(aNodesList)

    @handle_exceptions()
    def getConnectionsFromNode(self, aLeftNode, aLeftNodeOutput=None):
        """
        getConnectionsFromNode(self, aLeftNode, aLeftNodeOutput=None)
        Get the connections starting from the given left node, from a particular output or for all its outputs.

        :param aLeftNode: the node to consider, as a MDLNode or given its uid
        :param aLeftNodeOutput: the pin output identifier to consider. If let None, all the outputs will be considered
        :type aLeftNode: :class:`.MDLNode` or str
        :type aLeftNodeOutput: str, optional
        :return: a list of :class:`.SBSConnection`
        """
        nodes = self.getNodesConnectedFrom(aLeftNode, aLeftNodeOutput)
        connections = []
        leftOutputUID = None
        if aLeftNodeOutput and aLeftNode.isSBSInstance():
            leftOutputUID = aLeftNode.getMDLImplSBSInstance().getOutputBridgeUID(aLeftNodeOutput)

        for aNode in nodes:
            for aConn in aNode.getConnectionsFromNode(aLeftNode):
                if leftOutputUID is not None and aConn.getConnectedNodeOutputUID() is not None:
                    if leftOutputUID == aConn.getConnectedNodeOutputUID():
                        connections.append(aConn)
                else:
                    connections.append(aConn)
        return connections

    @handle_exceptions()
    def getConnectionsToNode(self, aRightNode, aRightNodeInput=None):
        """
        getConnectionsToNode(self, aRightNode, aRightNodeInput=None)
        Get the connections incoming to the given right node, to a particular input or for all its inputs.

        :param aRightNode: the node to consider, as a MDLNode or given its uid
        :param aRightNodeInput: the pin input identifier to consider. If let None, all the inputs will be considered
        :type aRightNode: :class:`.MDLNode` or str
        :type aRightNodeInput: str, optional
        :return: a list of :class:`.SBSConnection`
        """
        return self.mNodeList.getConnectionsToNode(aRightNode, aRightNodeInput)

    @handle_exceptions()
    def getNodesConnectedFrom(self, aLeftNode, aLeftNodeOutput=None):
        """
        getNodesConnectedFrom(aLeftNode, aOutputIdentifier=None)
        Get all the nodes connected to the given output of the given node.
        If aOutputIdentifier is let None, consider all the outputs of the node.

        :param aLeftNode: the node to consider
        :param aLeftNodeOutput: the output identifier to take in account
        :type aLeftNode: :class:`.MDLNode` or str
        :type aLeftNodeOutput: str, optional
        :return: a list of :class:`.MDLNode`
        """
        connectedNodes = self.mNodeList.getNodesConnectedFrom(aLeftNode)

        if aLeftNodeOutput is not None:
            nodeDef = aLeftNode.getDefinition()
            outputDef = nodeDef.getOutput(aLeftNodeOutput)
            if outputDef is not None and aLeftNode.isSBSInstance():
                leftOutputUID = aLeftNode.getMDLImplSBSInstance().getOutputBridgeUID(aLeftNodeOutput)

                connectedNodesFromOutput = []
                for n in connectedNodes:
                    for aConn in n.getConnections():
                        outputUID = aConn.getConnectedNodeOutputUID()
                        if aConn.getConnectedNodeUID() == aLeftNode.mUID and leftOutputUID == outputUID and n not in connectedNodesFromOutput:
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
        :type aRightNode: :class:`.MDLNode` or str
        :type aRightNodeInput: str, optional
        :return: a list of :class:`.MDLNode`
        """
        return self.mNodeList.getNodesConnectedTo(aRightNode, aRightNodeInput)

    @handle_exceptions()
    def getNodesDockedTo(self, aNode):
        """
        getNodesDockedTo(aNode)
        Get all the nodes that are docked to the given node.

        :param aNode: the node to consider
        :type aNode: :class:`.MDLNode`
        :return: a list of :class:`.MDLNode` corresponding to the nodes that are docked to the given node.
        """
        return self.mNodeList.getNodesDockedTo(aNode)

    @handle_exceptions()
    def moveConnectionsOnPinOutput(self, aInitialNode, aTargetNode, aInitialNodeOutput=None, aTargetNodeOutput=None):
        """
        moveConnectionsOnPinOutput(aInitialNode, aTargetNode, aInitialNodeOutput=None, aTargetNodeOutput=None)
        Allows to move all the connections connected to the given pin output of the given node to the target pin output of the target node.

        :param aInitialNode: the node initially connected, as an object or given its uid
        :param aTargetNode: the target node, which should be connected after this function, as an object or given its uid
        :param aInitialNodeOutput: the identifier of the output initially connected in aInitialNode. If None, the first output will be considered
        :param aTargetNodeOutput: the identifier of the output targeted on aTargetNode. If None, the first output will be considered
        :type aInitialNode: :class:`.MDLNode` or str
        :type aTargetNode: :class:`.MDLNode` or str
        :type aInitialNodeOutput: str, optional
        :type aTargetNodeOutput: str, optional
        :raise: :class:`.SBSImpossibleActionError`
        """
        initialNode = self.getNode(aInitialNode)
        targetNode = self.getNode(aTargetNode)
        if initialNode is None or targetNode is None:
            raise SBSImpossibleActionError('Cannot modify connections, one of the two nodes is not found in the graph')

        targetNodeOutputUID = None
        if targetNode.isSBSInstance():
            sbsInstance = targetNode.getMDLImplSBSInstance()
            if aTargetNodeOutput is not None:
                targetNodeOutputUID = sbsInstance.getOutputBridgeUID(aTargetNodeOutput)
            elif sbsInstance.mOutputBridgings:
                targetNodeOutputUID = sbsInstance.mOutputBridgings[0]
            if targetNodeOutputUID is None:
                raise SBSImpossibleActionError('Cannot find the target output on node '+targetNode.getDisplayName())

        initialType = initialNode.getOutputType(aInitialNodeOutput)
        targetType = targetNode.getOutputType(aTargetNodeOutput)
        if initialType != targetType:
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
        :type aInitialNode: :class:`.MDLNode` or str
        :type aTargetNode: :class:`.MDLNode` or str
        :type aInitialNodeInput: str, optional
        :type aTargetNodeInput: str, optional
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

        inputIdentifier = initialInputDef.mIdentifier
        conn = initialNode.getConnectionOnPin(inputIdentifier)
        connectedNodes = self.getNodesConnectedTo(aRightNode=initialNode, aRightNodeInput=aInitialNodeInput)
        if conn is None or not connectedNodes:
            raise SBSImpossibleActionError('No connection found on the input '+inputIdentifier+' of the node '+initialNode.getDisplayName())

        # Copy the connection on the target
        leftNode = connectedNodes[0]
        outputIdentifier = None
        if conn.getConnectedNodeOutputUID() is not None and leftNode.isSBSInstance():
            outputIdentifier = leftNode.getMDLImplSBSInstance().getOutputIdentifier(conn.getConnectedNodeOutputUID())
        self.connectNodes(aLeftNode=leftNode, aRightNode=targetNode, aLeftNodeOutput=outputIdentifier, aRightNodeInput=targetInputDef.mIdentifier)

        # Remove the previous connection
        initialNode.removeConnectionOnPin(inputIdentifier)

    @handle_exceptions()
    def getNodesInFrame(self, aFrame):
        """
        getNodesInFrame(aFrame)
        Get all the nodes included or partially included in the given frame.
        The frame must be included in this graph, otherwise SBSImpossibleActionError is raised

        :param aFrame: The frame to consider
        :type aFrame: :class:`.SBSGUIObject`
        :return: a list of :class:`.SBSNode`
        """
        return self.mGUIObjectList.getNodesInFrame(aFrame)

    @handle_exceptions()
    def getRect(self, aNodeList = None):
        """
        getRect(aNodeList = None)
        Get all the GUI rectangle of this graph, or look for the given nodes if aNodeList is not None

        :param aNodeList: The list of node to take in account for the GUI rectangle. None to consider the node list pointed by itself.
        :type aNodeList: list of str or list of :class:`.MDLNode`, optional
        :return: A :class:`.Rect`
        """
        return self.mNodeList.getRect(aNodeList)

    @handle_exceptions()
    def getAllInputs(self):
        """
        getAllInputs()
        Get the list of all nodes that has been exposed as input parameters (images and variables) of this graph

        :return: a list of :class:`.MDLNode`
        """
        inputs = BaseGraph.getAllInputs(self)
        return [self.getNode(aInput.mNodeUID) for aInput in inputs]

    @handle_exceptions()
    def getAllInputIdentifiers(self):
        """
        getAllInputIdentifiers()
        Get the list of all input identifiers

        :return: the list of identifiers as strings
        """
        return [aInput.getMDLImplConstant().getIdentifier() for aInput in self.getAllInputs()]

    @handle_exceptions()
    def getAllInputsInGroup(self, aGroup):
        """
        getAllInputsInGroup(aGroup)
        | Get the list of all input nodes (images and parameters) contained in the given group.
        | If aGroup is None, returns all the parameters that are not included in a group.

        :param aGroup: The group of parameter to consider (can be 'group/subgroup/subsubgroup')
        :type aGroup: str
        :return: a list of :class:`.MDLNode`
        """
        return [aInputNode for aInputNode in self.getAllInputs() if aInputNode.getMDLImplConstant().getGroup() == aGroup]

    @handle_exceptions()
    def getAllInputGroups(self):
        """
        getAllInputGroups()
        Get the list of all groups used for the inputs of the graph.

        :return: a list of groups as strings
        """
        groupList = set([aInput.getMDLImplConstant().getGroup() for aInput in self.getAllInputs() if aInput.getMDLImplConstant().getGroup()])
        return sorted(list(groupList))

    @handle_exceptions()
    def getInput(self, aInputIdentifier):
        """
        getInput(aInputIdentifier)
        Get the input MDLNode with the given identifier, among the input images and input parameters

        :param aInputIdentifier: input node identifier
        :type aInputIdentifier: str
        :return: the corresponding :class:`.MDLNode` object if found, None otherwise
        """
        return next((aInputNode for aInputNode in self.getAllInputs() if aInputNode.getMDLImplConstant().getIdentifier() == aInputIdentifier), None)

    @handle_exceptions()
    def getInputFromUID(self, aInputUID):
        """
        getInputFromUID(aInputUID)
        Get the input MDLNode with the given UID, among the input images and parameters

        :param aInputUID: input node UID
        :type aInputUID: str
        :return: the corresponding :class:`.MDLNode` object if found, None otherwise
        """
        return BaseGraph.getInputFromUID(self, aInputUID)

    @handle_exceptions()
    def getInputImages(self):
        """
        getInputImages()
        Get the list of input MDLNode of kind image (e.g. texture_2D node)

        :return: a list of :class:`.MDLNode`
        """
        return [aInputNode for aInputNode in self.getAllInputs() if aInputNode.getMDLImplConstant().isAnInputImage()]

    @handle_exceptions()
    def getInputImage(self, aInputImageIdentifier):
        """
        getInputImage(aInputImageIdentifier)
        Get the input image with the given identifier

        :param aInputImageIdentifier: input image identifier
        :type aInputImageIdentifier: str
        :return: a :class:`.MDLNode` if found, None otherwise
        """
        return next((aInputNode for aInputNode in self.getInputImages()
                     if aInputNode.getMDLImplConstant().getIdentifier() == aInputImageIdentifier), None)

    @handle_exceptions()
    def getInputImageWithUsage(self, aUsage):
        """
        getInputImageWithUsage(aUsage)
        Get the first input image which has the given usage defined (can be an enum value or a custom string)

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.MDLInput` if found, None otherwise
        """
        return next((aInputNode for aInputNode in self.getInputImages() if aInputNode.getMDLImplConstant().hasUsage(aUsage)), None)

    @handle_exceptions()
    def getInputParameter(self, aInputParamIdentifier):
        """
        getInputParameter(aInputIdentifier)
        Get the MDLInput with the given identifier, among the input parameters

        :param aInputParamIdentifier: input parameter identifier
        :type aInputParamIdentifier: str
        :return: the corresponding :class:`.MDLInput` object if found, None otherwise
        """
        return next((aInputNode for aInputNode in self.getInputParameters()
                     if aInputNode.getMDLImplConstant().getIdentifier() == aInputParamIdentifier), None)

    @handle_exceptions()
    def getInputParameterFromUID(self, aInputParamUID):
        """
        getInputParameterFromUID(aInputParamUID)
        Get the MDLInput with the given UID

        :param aInputParamUID: input parameter UID
        :type aInputParamUID: str
        :return: the corresponding :class:`.MDLInput` object if found, None otherwise
        """
        return BaseGraph.getInputParameterFromUID(self, aInputParamUID)

    @handle_exceptions()
    def getInputParameters(self):
        """
        getInputParameters()
        Get the list of inputs parameters that are not input images

        :return: a list of :class:`.MDLInput`
        """
        return [aInputNode for aInputNode in self.getAllInputs() if aInputNode.getMDLImplConstant().isAnInputParameter()]

    @handle_exceptions()
    def getInputWithUsage(self, aUsage):
        """
        getInputWithUsage(aUsage)
        Get the first input which has the given usage defined (can be an enum value or a custom string)

        :param aUsage: usage to look for
        :type aUsage: :class:`.UsageEnum` or str
        :return: a :class:`.MDLInput` if found, None otherwise
        """
        return next((aInputNode for aInputNode in self.getAllInputs() if aInputNode.getMDLImplConstant().hasUsage(aUsage)), None)

    @handle_exceptions()
    def getInputIndex(self, aInput):
        """
        getInputIndex(aInput)
        Get the index of the given input, among the list of MDLInput in this graph.

        :param aInput: input to search, as a MDLNode or a identifier
        :type aInput: :class:`.MDLNode` or str
        :return: the index of the input as an integer if found, -1 otherwise
        """
        aInputNode = None
        if isinstance(aInput, MDLNode):
            if aInput.isAConstant() and aInput.getMDLImplConstant().isAnInput():
                aInputNode = self.getNode(aInput)
        else:
            aInputNode = self.getInput(aInputIdentifier=aInput)
        if not aInputNode:
            return -1
        return next((i for i,param in enumerate(self.mParamInputs) if param.mNodeUID == aInputNode.mUID), -1)

    def getMDLInput(self, aUID):
        """
        getMDLInput(aUID)
        Get the MDLInput pointing to the given node uid

        :param aUID: The node uid to look for
        :type aUID: str
        :return: a :class:`.MDLInput` object if found, None otherwise
        """
        return next((aInput for aInput in self.mParamInputs if aInput.mNodeUID == aUID), None)

    @handle_exceptions()
    def getFirstInputOfType(self, aType):
        """
        getFirstInputOfType(aType)
        Get the first MDLNode input with the given type. This considers the variant types as compatible types.

        :param aType: The required type
        :type aType: str
        :return: a :class:`.MDLNode` object if found, None otherwise
        """
        return next((aInputNode for aInputNode in self.getAllInputs() if aInputNode.getOutputType() == aType), None)

    @handle_exceptions()
    def getGraphOutput(self):
        """
        getGraphOutput()
        Get the graph output node (root node)

        :return: a :class:`.MDLNode` object if found, None otherwise
        """
        return self.getNode(self.mRoot) if self.mRoot else None

    @handle_exceptions()
    def getGraphOutputNode(self):
        """
        getGraphOutputNode()
        Get the graph output node (root node)

        :return: a :class:`.MDLNode` object if found, None otherwise
        """
        return self.getGraphOutput()

    @handle_exceptions()
    def getGraphOutputType(self):
        """
        getGraphOutputType()
        Get the graph output type

        :return: the output type as a string if defined, None otherwise
        """
        aOutput = self.getGraphOutput()
        return aOutput.getOutputType() if aOutput else None

    @handle_exceptions()
    def computeUniqueInputIdentifier(self, aIdentifier, aSuffixId = 0):
        """
        computeUniqueInputIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used in the graph inputs and generate a unique identifier if necessary

        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier_id
        """
        return self._computeUniqueIdentifier(aIdentifier, aListsToCheck= [self.getAllInputIdentifiers()], aSuffixId= aSuffixId)

    @handle_exceptions()
    def contains(self, aNode):
        """
        contains(aNode)
        Check if the given node belongs to this graph

        :param aNode: The node to check, as a, object or an UID
        :type aNode: :class:`.MDLNode` or str
        :return: True if the given node belongs to the node list, False otherwise
        """
        return self.mNodeList.contains(aNode)

    @handle_exceptions()
    def createComment(self, aCommentText='Comment', aGUIPos=None):
        """
        createComment(aCommentText='Comment', aGUIPos=None)
        Create a new comment.

        :param aCommentText: The text of the comment. Default to 'Comment'
        :param aGUIPos: The comment position in the graph. Default to [0,0,0]
        :type aCommentText: str, optional
        :type aGUIPos: list of 3 float, optional
        :return: The :class:`.SBSGUIObject` created
        """
        return self.mGUIObjectList.createComment(aCommentText, aGUIPos)

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
        :type aNodeList: list of class:`.MDLNode`
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
        :type aNodeList: list of class:`.MDLNode`
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
    def createMDLNodePassThrough(self,
                                 aName = None,
                                 aAnnotations = None,
                                 aTypeModifier = mdlenum.MDLTypeModifierEnum.AUTO,
                                 aGUIPos = None):
        """
        createMDLNodePassThrough(aConstTypePath, aName = None, aTypeModifier = mdlenum.MDLTypeModifierEnum, aGUIPos = None)
        Create a new MDL node passthrough (dot) and add it to the node list of the graph.

        :param aName: name of the constant
        :param aParameters: parameters to set, allowing to set sub members of more complex constant type
        :param aTypeModifier: type modifier associated to the constant output. Default to MDLTypeModifierEnum.AUTO
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aName: str, optional
        :type aAnnotations: dictionary in the format {annotation(:class:`.MDLAnnotationEnum`),annotationValue(str)}, optional
        :type aTypeModifier: :class:`.MDLTypeModifierEnum`, optional
        :type aGUIPos: list of 3 float, optional
        :return: The new :class:`.MDLNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.PASSTHROUGH,
                                             aCstAnnotations = aAnnotations,
                                             aCstName = aName,
                                             aCstTypeModifier = aTypeModifier)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        return mdlNode

    @handle_exceptions()
    def createMDLNodeConst(self, aConstTypePath,
                                 aName = None,
                                 aValue = None,
                                 aParameters = None,
                                 aAnnotations = None,
                                 aExposed = False,
                                 aTypeModifier = mdlenum.MDLTypeModifierEnum.AUTO,
                                 aGUIPos = None):
        """
        createMDLNodeConst(aConstTypePath, aName = None, aValue = None, aParameters = None, aExposed = False, aTypeModifier = mdlenum.MDLTypeModifierEnum, aGUIPos = None)
        Create a new MDL node constant and add it to the node list of the graph.

        :param aConstTypePath: mdl path of the type of constant to create
        :param aName: name of the constant
        :param aValue: value of the constant to set, in case of a simple constant type
        :param aParameters: parameters to set, allowing to set sub members of more complex constant type
        :param aAnnotations: annotations of the mdl constant
        :param aExposed: defines if the constant must be exposed as an input parameter. Default to False
        :param aTypeModifier: type modifier associated to the constant output. Default to MDLTypeModifierEnum.AUTO
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aConstTypePath: str
        :type aName: str, optional
        :type aValue: any type, optional
        :type aParameters: dictionary in the format {paramPath(str),paramValue(any type)}, optional
        :type aAnnotations: dictionary in the format {annotation(:class:`.MDLAnnotationEnum`),annotationValue(str)}, optional
        :type aExposed: bool, optional
        :type aTypeModifier: :class:`.MDLTypeModifierEnum`, optional
        :type aGUIPos: list of 3 float, optional
        :return: The new :class:`.MDLNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        if aExposed:
            if aName is None:
                aName = mdl_helpers.getModuleName(aConstTypePath) + '_1'
            aName = self.computeUniqueInputIdentifier(aIdentifier=aName)

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.CONSTANT,
                                             aPath = aConstTypePath,
                                             aParameters = aParameters,
                                             aCstAnnotations = aAnnotations,
                                             aCstIsExposed = aExposed,
                                             aCstName = aName,
                                             aCstValue = aValue,
                                             aCstTypeModifier = aTypeModifier)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        if aExposed:
            self.setConstantAsInputParameter(mdlNode)
        return mdlNode

    @handle_exceptions()
    def createMDLNodeOutput(self, aParameters = None, aGUIPos = None):
        """
        createMDLNodeOutput(aParameters = None, aGUIPos = None)
        Create a MDL Node instance of mdl::material and set it as the output of the graph

        :param aParameters: parameters of the instance to set
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aParameters: dictionary of parameters to set, in the format {paramPath(str),paramValue(any type)}, optional
        :type aGUIPos: list of 3 float, optional
        :return:
        """
        outputNode = self.createMDLNodeInstance(aPath=MDLManager.MATERIAL_CONSTRUCTOR_FUNCTION,
                                                aParameters=aParameters,
                                                aGUIPos=aGUIPos)
        self.setOutputNode(outputNode)
        return outputNode

    @handle_exceptions()
    def createMDLNodeSelector(self, aConnectToNode = None, aOutput = None, aMember = None, aGUIPos = None):
        """
        createMDLNodeSelector(aConnectToNode = None, aOutput = None, aMember = None, aGUIPos = None)
        Create a new MDL node constant and add it to the node list of the graph.

        :param aConnectToNode: the mdl node to connect to, as a MDLNode or a uid
        :param aOutput: the output identifier of the node to connect to. Can be None if the node to connect to has only one output
        :param aMember: name of the member to select. Will be used only if a node to connect to is provided
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aConnectToNode: :class:`.MDLNode` or str, optional
        :type aOutput: str, optional
        :type aMember: str, optional
        :type aGUIPos: list of 3 float, optional
        :return: The new :class:`.MDLNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.SELECTOR)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        # Connect the selector node and select the appropriate member
        if aConnectToNode:
            self.connectNodes(aLeftNode=aConnectToNode, aRightNode=mdlNode, aLeftNodeOutput=aOutput)
            if aMember:
                mdlNode.setParameterValue('member', aMember)

        return mdlNode

    @handle_exceptions()
    def createMDLNodeInstance(self, aPath,
                                    aParameters = None,
                                    aGUIPos = None):
        """
        createMDLNodeInstance(aPath, aParameters = None, aGUIPos = None)
        Create a new native MDL node instance and add it to the node list of the graph.

        :param aPath: mdl path of the instance to create
        :param aParameters: parameters of the instance to set
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aPath: str
        :type aParameters: dictionary of parameters to set, in the format {paramPath(str),paramValue(any type)}, optional
        :type aGUIPos: list of 3 float, optional
        :return: The new :class:`.MDLNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.MDL_INSTANCE,
                                             aPath = aPath,
                                             aParameters = aParameters)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        return mdlNode

    @handle_exceptions()
    def createMDLNodeMDLGraphInstance(self, aSBSDocument, aGraph, aParameters = None, aGUIPos = None):
        """
        createMDLNodeMDLGraphInstance(aSBSDocument, aGraph, aParameters = None, aGUIPos = None)
        Create a new instance of the given MDL Graph, and add it to the node list of the current graph.

        Note:
            - The graph must be defined in the given SBSDocument.
            - Use :func:`createMDLNodeMDLGraphInstanceFromPath` to add an instance of a graph included in an external package.

        :param aSBSDocument: current edited document
        :param aGraph: graph that will be referenced by the instance node
        :param aParameters: parameters of the filter node
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]

        :type aSBSDocument: :class:`.SBSDocument`
        :type aGraph: :class:`.MDLGraph`
        :type aParameters: dictionary of parameters to set, in the format {paramPath(str),paramValue(any type)}, optional
        :type aGUIPos: list of 3 float, optional

        :return: The new :class:`.MDLNode` object
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}

        # Check if the graph belongs to the current SBSDocument
        aGraphRelPath = aSBSDocument.getMDLGraphInternalPath(aUID = aGraph.mUID, addDependencyUID=True)
        if aGraphRelPath is None:
            raise SBSImpossibleActionError('The graph to instantiate must be included in the given document')

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.MDL_GRAPH_INSTANCE,
                                             aPath = aGraphRelPath,
                                             aInstanceOfGraph = aGraph,
                                             aInstanceDependency = aSBSDocument.getHimselfDependency(),
                                             aParameters = aParameters)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        return mdlNode

    @handle_exceptions()
    def createMDLNodeMDLGraphInstanceFromPath(self, aSBSDocument, aPath, aParameters = None, aGUIPos = None):
        """
        createMDLNodeMDLGraphInstanceFromPath(aSBSDocument, aPath, aParameters = None, aGUIPos = None)
        Create a new instance of the MDL Graph pointed by the given path, and add it to the node list of the graph.

        :param aSBSDocument: current edited document
        :param aPath: path of the MDL graph definition (absolute, relative to the current .sbs file, or given with an alias, for instance *myalias:/myMdlFile.sbs*)

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.
        :param aParameters: parameters of the instance to set
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :type aParameters: dictionary of parameters to set, in the format {paramPath(str),paramValue(any type)}, optional
        :type aGUIPos: list of 3 float, optional
        :return: The new :class:`.MDLNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]

        # Get/Create the dependency and the reference to the pointed graph
        outValues = aSBSDocument.getOrCreateDependency(aPath)
        if len(outValues) != 3:
            raise SBSImpossibleActionError('Failed to create instance of MDL graph '+str(aPath))
        aGraph = outValues[0]
        aGraphRelPath = outValues[1]
        aDependency = outValues[2]

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.MDL_GRAPH_INSTANCE,
                                             aPath = aGraphRelPath,
                                             aInstanceOfGraph = aGraph,
                                             aInstanceDependency = aDependency,
                                             aParameters = aParameters)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        return mdlNode

    @handle_exceptions()
    def createMDLNodeSBSGraphInstance(self, aSBSDocument, aGraph, aParameters = None, aGUIPos = None):
        """
        createMDLNodeSBSGraphInstance(aSBSDocument, aGraph, aParameters = None, aGUIPos = None)
        Create a new instance of the given Substance Graph, and add it to the node list of the current graph.

        Note:
            - The graph must be defined in the given SBSDocument.
            - Use :func:`createMDLNodeSBSGraphInstanceFromPath` to add an instance of a graph included in an external package.

        :param aSBSDocument: current edited document
        :param aGraph: Substance graph that will be referenced by the instance node
        :param aParameters: parameters of the filter node
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]

        :type aSBSDocument: :class:`.SBSDocument`
        :type aGraph: :class:`.SBSGraph`
        :type aParameters: dictionary of parameters to set, in the format {paramPath(str),paramValue(any type)}, optional
        :type aGUIPos: list of 3 float, optional

        :return: The new :class:`.MDLNode` object
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}

        # Check if the graph belongs to the current SBSDocument
        aGraphRelPath = aSBSDocument.getSBSGraphInternalPath(aUID = aGraph.mUID, addDependencyUID=True)
        if aGraphRelPath is None:
            raise SBSImpossibleActionError('The graph to instantiate must be included in the given document')

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.SBS_INSTANCE,
                                             aPath = aGraphRelPath,
                                             aInstanceOfGraph = aGraph,
                                             aInstanceDependency = aSBSDocument.getHimselfDependency(),
                                             aParameters = aParameters)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        return mdlNode

    @handle_exceptions()
    def createMDLNodeSBSGraphInstanceFromPath(self, aSBSDocument, aPath, aParameters = None, aGUIPos = None):
        """
        createMDLNodeSBSGraphInstanceFromPath(aSBSDocument, aPath, aParameters = None, aGUIPos = None)
        Create a new instance of the Substance Graph pointed by the given path, and add it to the node list of the graph.

        :param aSBSDocument: current edited document
        :param aPath: path of the Substance graph definition (absolute, relative to the current .sbs file, or given with an alias, for instance *myalias:/myMdlFile.sbs*)

            - If the graph is included in the current package, use: *pkg:///MyGraphIdentifier*
            - If the path uses an alias, use: *myalias://MyFileName.sbs/MyGraphIdentifier*
            - If the path is relative to the current package or absolute, use *MyAbsoluteOrRelativePath/MyFileName.sbs/MyGraphIdentifier*
            - Note that if the graph identifier is equivalent to the filename, the part */MyGraphIdentifier* may be omit.
        :param aParameters: parameters of the instance to set
        :param aGUIPos: position of the node in the graph: [x,y,z]. default value is [0,0,0]
        :type aSBSDocument: :class:`.SBSDocument`
        :type aPath: str
        :type aParameters: dictionary of parameters to set, in the format {paramPath(str),paramValue(any type)}, optional
        :type aGUIPos: list of 3 float, optional
        :return: The new :class:`.MDLNode` object
        """
        if aGUIPos is None: aGUIPos = [0,0,0]
        if aParameters is None: aParameters = {}

        # Get/Create the dependency and the reference to the pointed graph
        outValues = aSBSDocument.getOrCreateDependency(aPath, aAllowSBSAR=True)
        if len(outValues) != 3:
            raise SBSImpossibleActionError('Failed to create instance of Substance graph '+str(aPath))

        aGraph = outValues[0]
        aGraphRelPath = outValues[1]
        aDependency = outValues[2]

        mdlNode = sbsgenerator.createMDLNode(aParentGraph = self,
                                             aImplementationKind = mdlenum.MDLImplementationKindEnum.SBS_INSTANCE,
                                             aPath = aGraphRelPath,
                                             aInstanceOfGraph = aGraph,
                                             aInstanceDependency = aDependency,
                                             aParameters = aParameters)

        if mdlNode.mGUILayout is not None:
            mdlNode.mGUILayout.mGPos = aGUIPos
        api_helpers.addObjectToList(self, 'mNodes', mdlNode)

        return mdlNode

    @handle_exceptions()
    def connectNodes(self, aLeftNode, aRightNode, aLeftNodeOutput = None, aRightNodeInput = None):
        """
        connectNodes(aLeftNode, aRightNode, aLeftNodeOutput = None, aRightNodeInput = None)
        Connect the given nodes together: aLeftNode(on the output aLeftNodeOutput) -> aRightNode(on the input aRightNodeInput).
        If the right node input is None, the connection will be done on the first input of the right node.
        If the left node output is None, the connection will be done on the first compatible output of the left node.

        :param aLeftNode: Node to connect from, as a MDLNode or as a UID
        :param aRightNode: Node to connect to, as a MDLNode or as a UID
        :param aLeftNodeOutput: Identifier of the output of the left node
        :param aRightNodeInput: Identifier of the input of the right node

        :type aLeftNode: :class:`.MDLNode` or str
        :type aRightNode: :class:`.MDLNode` or str
        :type aLeftNodeOutput: str, optional
        :type aRightNodeInput: str, optional

        :return: The connection as a :class:`.SBSConnection` if success, None otherwise (in case of type incompatibility for instance)
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Check that the given nodes belongs to the graph
        leftNode = self.getNode(aLeftNode)
        rightNode = self.getNode(aRightNode)
        if leftNode is None or rightNode is None:
            raise SBSImpossibleActionError('Impossible to connect node '+str(aLeftNode)+' to '+str(aRightNode)+', one of them is not found in the graph')

        # Check that the connection will not create a cycle in the DAG
        if self.isAPathBetween(aLeftNode = rightNode, aRightNode = leftNode):
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', it would create a cycle')

        # Get the comp nodes parameters (input entries, parameters, outputs)
        leftNodeDef = leftNode.getDefinition()
        rightNodeDef = rightNode.getDefinition()
        if leftNodeDef is None or rightNodeDef is None:
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', failed to get a definition')

        # Find the appropriate output on the left node
        leftOutput = None
        if len(leftNodeDef.getAllOutputs()) == 1:
            leftOutput = leftNodeDef.getOutput()
        elif aLeftNodeOutput is not None:
            leftOutput = leftNodeDef.getOutput(aLeftNodeOutput)

        # Find the appropriate input on the right node
        rightInputDef = None
        if aRightNodeInput is not None:
            rightInputDef = rightNodeDef.getInput(aRightNodeInput)
        else:
            # Only one input => take it
            if len(rightNodeDef.mInputs) == 1:
                rightInputDef = rightNodeDef.mInputs[0]
            # If left output is defined => take the first compatible input
            elif leftOutput is not None:
                rightInputDef = rightNodeDef.getFirstInputOfType(leftOutput.getType())
            # If left node not defined and is a Substance graph instance => take the first compatibles input and output
            elif leftNode.isSBSInstance():
                leftOutput,rightInputDef = next(((o,i) for o in leftNodeDef.mOutputs for i in rightNodeDef.mInputs
                                                 if o.getType()==i.getType()), (None,None))

        # If the left output is still undefined, find the first compatible output
        if leftOutput is None and rightInputDef is not None and leftNode.isSBSInstance():
            leftOutput = next((o for o in leftNodeDef.mOutputs if o.getType() == rightInputDef.getType()), None)

        if leftOutput is None or rightInputDef is None:
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+
                                           ', cannot find on which input/output to connect them')

        # Check the type compatibility
        # TODO: Handle nodes with several signatures to allow changing the mdl path as done in SD for types <*>
        if leftNode.isAPassthrough() or rightNode.isAPassthrough():
            pass # TODO We don't manage dynamic type for passthrough node for now
        elif leftOutput.getType() != rightInputDef.getType() and not rightNode.isASelector():
            raise SBSImpossibleActionError('Impossible to connect node '+leftNode.getDisplayName()+' to '+rightNode.getDisplayName()+', types are incompatible')

        # Do the connection: Create a new connection or modify the existing one on the right input
        connRefOutput = None
        if leftNode.isSBSInstance():
            connRefOutput = leftNode.getMDLImplementation().getOutputBridgeUID(leftOutput.mIdentifier)

        rightInputIdentifier = rightInputDef.mIdentifier
        if rightNode.isSBSInstance():
            rightInputIdentifier = rightNode.getMDLImplementation().getInputBridgeUID(rightInputIdentifier)

        aConn = rightNode.getConnectionOnPin(rightInputIdentifier)
        if aConn is None:
            aConn = sbscommon.SBSConnection(aIdentifier   = rightInputIdentifier,
                                            aConnRef      = leftNode.mUID,
                                            aConnRefOutput= connRefOutput)
            api_helpers.addObjectToList(rightNode, 'mConnections', aConn)

        else:
            aConn.setConnection(leftNode.mUID, connRefOutput)

        if rightNode.isASelector():
            rightNode.getMDLImplementation().mStructType = leftOutput.getType()

        return aConn


    @handle_exceptions()
    def copyNode(self, aNode):
        """
        copyNode(aNode)
        Create a simple copy of the given node with a new UID.

        :param aNode: the node to copy
        :type aNode: :class:`.MDLNode`
        :return: The new :class:`.MDLNode` object
        """
        return self.mNodeList.copyNode(aNode)

    @handle_exceptions()
    def disconnectNodes(self, aLeftNode, aRightNode, aRightNodeInput = None):
        """
        disconnectNodes(aLeftNode, aRightNode, aRightNodeInput = None)
        Disconnect the given nodes: aLeftNode -> aRightNode(on the input aRightNodeInput).
        If the right node input is None, all connections will be removed.

        :param aLeftNode: Left node, as a MDLNode or a UID
        :param aRightNode: Right node, as a MDLNode or a UID
        :param aRightNodeInput: Identifier of the input of the right node

        :type aLeftNode: :class:`.MDLNode` or str
        :type aRightNode: :class:`.MDLNode` or str
        :type aRightNodeInput: str, optional

        :return: Nothing
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        # Check that the given nodes belongs to the graph
        leftNode = self.getNode(aLeftNode)
        rightNode = self.getNode(aRightNode)
        if leftNode is None or rightNode is None:
            raise SBSImpossibleActionError('Impossible to connect node '+str(aLeftNode)+' to '+str(aRightNode))

        # Remove all connections
        if aRightNodeInput is None:
            rightNode.removeConnectionsFrom(leftNode)
        # Remove only the connection on the given input pin
        else:
            conn = rightNode.getConnectionOnPin(aRightNodeInput)
            if conn is not None and conn.getConnectedNodeUID() == leftNode.mUID:
                rightNode.removeConnectionOnPin(aRightNodeInput)


    @handle_exceptions()
    def createIterationOnNode(self, aNbIteration,
                              aNodeUID,
                              aForceRandomSeed = False,
                              aGUIOffset = None):
        """
        createIterationOnNode(aNbIteration, aNodeUID, aForceRandomSeed = False, aGUIOffset = None)
        Duplicate NbIteration times the given node, and connect each node with the previous one to create this kind of connection:

        Node -> Node_1 -> Node_2 -> ... -> Node_N

        :param aNbIteration: number of time the node must be duplicated
        :param aNodeUID: the UID of the node to duplicate
        :param aForceRandomSeed: specify if a different random seed must be generated for each iteration. Default to False
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aNbIteration: positive integer
        :type aNodeUID: str
        :type aForceRandomSeed: bool, optional
        :type aGUIOffset: list of 2 float, optional

        :return: The list of :class:`.MDLNode` objects created (including the nodes given in aNodeUIDs_NextPatternInput), None if failed
        """
        #To check
        if aGUIOffset is None: aGUIOffset = [150, 0]

        # Generate iterations with this single node pattern
        return self.createIterationOnPattern(aNbIteration,
                                             aNodeUIDs = [aNodeUID],
                                             aForceRandomSeed = aForceRandomSeed,
                                             aGUIOffset = aGUIOffset)

    @handle_exceptions()
    def createIterationOnPattern(self, aNbIteration,
                                 aNodeUIDs,
                                 aNodeUIDs_NextPattern = None,
                                 aForceRandomSeed = False,
                                 aGUIOffset = None):
        """
        createIterationOnPattern(aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern = None, aForceRandomSeed = False, aGUIOffset = None)
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
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aNbIteration: positive integer
        :type aNodeUIDs: list of str
        :type aNodeUIDs_NextPattern: list of str, optional
        :type aForceRandomSeed: bool, optional
        :type aGUIOffset: list of 2 float, optional

        :return: The list of :class:`.MDLNode` objects created (including the nodes given in aNodeUIDs_NextPatternInput), None if failed
        """
        # To check
        if aGUIOffset is None: aGUIOffset = [150, 0]

        return sbsgenerator.createIterationOnPattern(aParentObject = self,
                                                     aNbIteration = aNbIteration,
                                                     aNodeUIDs = aNodeUIDs,
                                                     aNodeUIDs_NextPattern = aNodeUIDs_NextPattern,
                                                     aForceRandomSeed = aForceRandomSeed,
                                                     aGUIOffset = aGUIOffset)

    @handle_exceptions()
    def deleteInputParameter(self, aInputParameter, aRemoveConstantNode=False):
        """
        deleteInputParameter(aInputParameter)
        Allows to delete the given input parameter.

        :param aInputParameter: The input parameter to remove, as a MDLNode or as an input identifier
        :param aRemoveConstantNode: True to remove the constant node associated to this input. False to only make this constant not exposed. Default to False
        :type aInputParameter: :class:`.MDLNode` or str
        :type aRemoveConstantNode: bool, optional
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aInputNode = None
        aInputIdentifier = aInputParameter
        if isinstance(aInputParameter, MDLNode):
            if aInputParameter.isAnInput():
                aInputIdentifier = aInputParameter.getMDLImplConstant().getIdentifier()
                aInputNode = self.getNode(aInputParameter)
        else:
            aInputNode = self.getInput(aInputIdentifier=aInputParameter)

        if aInputNode is None:
            raise SBSImpossibleActionError('Impossible to remove input parameter '+python_helpers.castStr(aInputIdentifier)+' from this graph, \
cannot find the constant node in the graph')

        aInputParam = self.getMDLInput(aInputNode.mUID)
        if aInputParam is None:
            raise SBSImpossibleActionError('Impossible to remove input parameter '+python_helpers.castStr(aInputIdentifier)+' from this graph, \
cannot find the associated MDLInput')

        if aRemoveConstantNode:
            self.deleteNode(aInputNode)
        else:
            self.mParamInputs.remove(aInputParam)
            aInputNode.getMDLImplConstant().setExposed(aExposed=False)
            aInputNode.removeConnectionOnPin(aInputNode.getParameter().mName)
        return True

    @handle_exceptions()
    def deleteNode(self, aNode):
        """
        deleteNode(aNode)
        Allows to delete the given node from the graph.
        It removes it from the MDL node list, and delete all the connection from and to that node in the graph.

        :param aNode: The node to remove, as a MDLNode or an UID.
        :type aNode: :class:`.MDLNode` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        aNode = self.getNode(aNode)
        if not aNode:
            raise SBSImpossibleActionError('Failed to delete this node, cannot find it in the MDL graph')
        if self.getGraphOutputNode() == aNode:
            self.mRoot = '0'
        if aNode.isAnInput():
            mdlInput = self.getMDLInput(aNode.mUID)
            if mdlInput is not None:
                self.mParamInputs.remove(mdlInput)
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
    def duplicateNode(self, aNode, aGUIOffset = None):
        """
        duplicateNode(aNode, aGUIOffset = None)
        Duplicate the given node, generate a new UID and add the node to the same node list than the source node.

        :param aNode: the node to copy (may be identified by its UID)
        :param aGUIOffset: node position offset. Default to [150, 0]
        :type aNode: :class:`.MDLNode` or str
        :type aGUIOffset: list of 2 float, optional
        :return: The new :class:`.MDLNode` object
        """
        if aGUIOffset is None: aGUIOffset = [150, 0]
        return self.mNodeList.duplicateNode(aNode, aGUIOffset)

    @handle_exceptions()
    def isAPathBetween(self, aLeftNode, aRightNode):
        """
        isAPathBetween(self, aLeftNode, aRightNode)
        Check if there is a path from the left node to the right node with the current connections.

        :param aLeftNode: The left node
        :param aRightNode: The right node
        :type aLeftNode: :class:`.MDLNode` or str
        :type aRightNode: :class:`.MDLNode` or str
        :return: True if a path is found, False otherwise
        """
        return self.mNodeList.isAPathBetween(aLeftNode, aRightNode)

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

    @handle_exceptions()
    def setConstantAsInputParameter(self, aMDLNode):
        """
        setConstantAsInputParameter(aMDLNode)
        Set the given MDLNode with a MDLImplConstant implementation as an input parameter of the graph

        :param aMDLNode: The constant node to expose, as a MDLNode object or given its uid
        :type aMDLNode: :class:`.MDLNode` or str
        :raise: :class:`.SBSImpossibleActionError`
        """
        aNode = self.getNode(aMDLNode)
        if aNode is None:
            raise SBSImpossibleActionError('Can\'t set this node as an input parameter, it is not included in the graph')
        if not aNode.isAConstant():
            raise SBSImpossibleActionError('Can\'t set this node as an input parameter, it is not a constant')
        if self.mParamInputs is None:
            self.mParamInputs = []

        # Ensure input identifier uniqueness
        cst = aMDLNode.getMDLImplConstant()
        aIdentifier = self.computeUniqueInputIdentifier(cst.getIdentifier())
        cst.setIdentifier(aIdentifier)

        if self.getMDLInput(aNode.mUID) is None:
            self.mParamInputs.append(MDLInput(aNodeUID=aNode.mUID))
        cst.setExposed(True)

    @handle_exceptions()
    def setInputIndex(self, aInput, aIndex):
        """
        setInputIndex(aInput, aIndex)
        Set the index of the given input.

        :param aInput: input to search, as a MDLNode or a identifier
        :param aIndex: index to set, in the range [0 ; nbInputs[
        :type aInput: :class:`.MDLNode` or str
        :type aIndex: int
        :raise: :class:`api_exceptions.SBSImpossibleActionError` if failed
        """
        if not 0 <= aIndex < len(self.mParamInputs):
            raise SBSImpossibleActionError('The provided index in not in the range [0; nbInputs[')
        currentIndex = self.getInputIndex(aInput)
        if currentIndex == -1:
            raise SBSImpossibleActionError('Cannot find the given input in the graph')
        aParamInput = self.mParamInputs.pop(currentIndex)
        self.mParamInputs.insert(aIndex, aParamInput)

    def setOutputNode(self, aMDLNode):
        """
        setOutputNode(aMDLNode)
        Set the given node as the output node of the graph

        :param aMDLNode: the MDLNode, which must be a material
        :type aMDLNode: :class:`.MDLNode` or str
        :raise: :class:`.SBSImpossibleActionError` in case the node is not found in the graph or if it is not a material
        """
        aNode = self.getNode(aMDLNode)
        if aNode is None:
            raise SBSImpossibleActionError('Can\'t set this node as the output, it is not included in the graph')
        if not aNode.isAPotentialOutput():
            raise SBSImpossibleActionError('Can\'t set this node as the output, it is not a material')
        self.mRoot = aNode.mUID

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
            log.error(error)
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

    @handle_exceptions()
    def sortNodesAsDAG(self):
        """
        sortNodesAsDAG()
        Sort the MDL node list of the graph to order them as a DAG. The member mNodes is updated.

        :return: the sorted node list.
        """
        return self.mNodeList.sortNodesAsDAG()
