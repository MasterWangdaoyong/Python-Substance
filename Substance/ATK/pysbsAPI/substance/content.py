# coding: utf-8
"""
Module **content** provides the definition of the classes :class:`.SBSGroup` and :class:`.SBSContent`
"""
from __future__ import unicode_literals
import copy

from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject
from pysbs import graph
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs import python_helpers
from pysbs import mdl

from .resource import SBSResource, SBSResourceScene


# ==============================================================================
@doc_inherit
class SBSGroup(SBSObject):
    """
    Class that contains information on a group node as defined in a .sbs file.
    A group correspond to a folder in Substance Designer, and is a hierarchical group of elements.

    Members:
        * mIdentifier (str): identifier of the group used in the paths that refer to its sub-objects.
        * mUID        (str): unique identifier of this group in the package/ context.
        * mDesc       (str, optional): textual description.
        * mContent    (:class:`.SBSContent`, optional): children of the group.
    """
    def __init__(self,
                 aIdentifier= '',
                 aUID       = '',
                 aDesc      = None,
                 aContent   = None):
        super(SBSGroup, self).__init__()
        self.mUID           = aUID
        self.mIdentifier    = aIdentifier
        self.mDesc          = aDesc
        self.mContent       = aContent

        self.mMembersForEquality = ['mIdentifier',
                                    'mContent',
                                    'mDesc']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUID        = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'uid'        )
        self.mIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'identifier' )
        self.mDesc       = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'desc'       )
        self.mContent    = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'content'    , SBSContent)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID         , 'uid'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier  , 'identifier'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDesc        , 'desc'        )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mContent     , 'content'     )

    @handle_exceptions()
    def getContent(self):
        """
        getContent()
        Get the content included in this group

        :return: The content as a :class:`.SBSContent` object
        """
        return self.mContent

    @handle_exceptions()
    def getMDLGraph(self, aGraphIdentifier):
        """
        getMDLGraph(aGraphIdentifier)
        Get the MDL Graph object with the given identifier

        :param aGraphIdentifier: Identifier of the graph to get
        :type aGraphIdentifier: str
        :return: A :class:`.MDLGraph` object
        """
        return self.getContent().getMDLGraph(aGraphIdentifier, aRecursive = True)

    @handle_exceptions()
    def getMDLGraphList(self, aRecursive = False):
        """
        getMDLGraphList()
        Get the list of all MDL graphs included in this group

        :param aRecursive: True to parse sub folders, False to search only inside the current Group. Default to False
        :type aRecursive: bool, optional
        :return: A list of :class:`.SBSGraph` object
        """
        return self.getContent().getMDLGraphList(aRecursive)

    @handle_exceptions()
    def getSBSResource(self, aResourceIdentifier):
        """
        getSBSResource(self, aResourceIdentifier)
        Get the Resource object with the given identifier

        :param aResourceIdentifier: Identifier of the resource to get
        :type aResourceIdentifier: str
        :return: A :class:`.SBSResource` object
        """
        return self.getContent().getSBSResource(aResourceIdentifier, aRecursive = True)

    @handle_exceptions()
    def getSBSResourceList(self, aRecursive = False, aIncludeSceneResources=True):
        """
        getSBSResourceList(aRecursive = False, aIncludeSceneResources=True)
        Get the list of all the resources included in this group.

        :param aRecursive: True to parse sub folders, False to search only inside the current Group. Default to False
        :type aRecursive: bool, optional
        :param aIncludeSceneResources: True to include the Scene/Mesh resources. Default to True
        :type aIncludeSceneResources: bool, optional
        :return: A list of :class:`.SBSResource` objects
        """
        return self.getContent().getSBSResourceList(aRecursive=aRecursive, aIncludeSceneResources=aIncludeSceneResources)

    @handle_exceptions()
    def getSBSGraph(self, aGraphIdentifier):
        """
        getSBSGraph(aGraphIdentifier)
        Get the Substance graph object with the given identifier

        :param aGraphIdentifier: Identifier of the graph to get
        :type aGraphIdentifier: str
        :return: A :class:`.SBSGraph` object
        """
        return self.getContent().getSBSGraph(aGraphIdentifier, aRecursive = True)

    @handle_exceptions()
    def getSBSGraphList(self, aRecursive = False):
        """
        getSBSGraphList()
        Get the list of all Substance graphs included in this group

        :param aRecursive: True to parse sub folders, False to search only inside the current Group. Default to False
        :type aRecursive: bool, optional
        :return: A list of :class:`.SBSGraph` object
        """
        return self.getContent().getSBSGraphList(aRecursive)

    @handle_exceptions()
    def getSBSFunction(self, aFunctionIdentifier):
        """
        getSBSFunction(aFunctionIdentifier)
        Get the Function object with the given identifier

        :param aFunctionIdentifier: Identifier of the function to get
        :type aFunctionIdentifier: str
        :return: A :class:`.SBSFunction` object
        """
        return self.getContent().getSBSFunction(aFunctionIdentifier, aRecursive = True)

    @handle_exceptions()
    def getSBSFunctionList(self, aRecursive = False):
        """
        getSBSFunctionList()
        Get the list of all functions included in this group

        :param aRecursive: True to parse sub folders, False to search only inside the current Group. Default to False
        :type aRecursive: bool, optional
        :return: A list of :class:`.SBSFunction` object
        """
        return self.getContent().getSBSFunctionList(aRecursive)

    @handle_exceptions()
    def getSBSGroup(self, aGroupIdentifier):
        """
        getSBSGroup(aGroupIdentifier)
        Get the Group object with the given identifier

        :param aGroupIdentifier: Identifier of the group (=folder) to get
        :type aGroupIdentifier: str
        :return: A :class:`.SBSGroup` object
        """
        return self.getContent().getSBSGroup(aGroupIdentifier, aRecursive = True)

    @handle_exceptions()
    def getSBSGroupList(self, aRecursive = False):
        """
        getSBSGroupList()
        Get the list of all groups included in this group

        :param aRecursive: True to parse sub folders, False to search only inside the current Group. Default to False
        :type aRecursive: bool, optional
        :return: A list of :class:`.SBSGroup` object
        """
        return self.getContent().getSBSGroupList(aRecursive)

    @handle_exceptions()
    def getDescription(self):
        """
        getDescription()
        Get the group description

        :return: The textual description of the group
        """
        return self.mDesc

    @handle_exceptions()
    def setDescription(self, aDescription):
        """
        setDescription(aDescription)
        Set the given description

        :param aDescription: the textual group description
        :type aDescription: str
        """
        self.mDesc = python_helpers.castStr(aDescription)


# ==============================================================================
@doc_inherit
class SBSContent(SBSObject):
    """
    Class that contains information on the content node as defined in a .sbs file.
    The content is a tree structure of these elements:

    Members:
        * mGraphs (list of :class:`.SBSGraph`): Graphs in this content
        * mGroups (list of :class:`.SBSGroup`): Folders in this content
        * mResources (list of :class:`.SBSResource`): Resources in this content
        * mResourcesScene (list of :class:`.SBSResourceScene`): Scene resources in this content
        * mFunctions (list of :class:`.SBSFunction`): Functions in this content
    """
    def __init__(self,
                 aGroups         = None,
                 aGraphs         = None,
                 aResources      = None,
                 aResourcesScene = None,
                 aFunctions      = None,
                 aMDLGraphs      = None):
        super(SBSContent, self).__init__()
        self.mGroups         = aGroups
        self.mGraphs         = aGraphs
        self.mResources      = aResources
        self.mResourcesScene = aResourcesScene
        self.mFunctions      = aFunctions
        self.mMDLGraphs      = aMDLGraphs

        self.mMembersForEquality = ['mGroups',
                                    'mGraphs',
                                    'mResources',
                                    'mResourcesScene',
                                    'mFunctions',
                                    'mMDLGraphs']

    @staticmethod
    def isContentChildType(aObject):
        """
        Check if the type of given object is one of the types accepted under a SBSContent object

        :param aObject: The object to check
        :return: True if the type of the given object can be included in a SBSContent
        """
        return type(aObject) in [SBSGroup, SBSResource, SBSResourceScene, graph.SBSGraph, graph.SBSFunction, mdl.MDLGraph]

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath,  aSBSParser, aXmlNode):
        self.mGraphs         = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'graph'   ,      graph.SBSGraph)
        self.mGroups         = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'group'   ,      SBSGroup)
        self.mResources      = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'resource',      SBSResource)
        self.mResourcesScene = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'resourceScene', SBSResourceScene)
        self.mFunctions      = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'function',      graph.SBSFunction)
        self.mMDLGraphs      = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'mdl_graph',     mdl.MDLGraph)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mGraphs   ,      'graph'        )
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mGroups   ,      'group'        )
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mResources,      'resource'     )
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mResourcesScene, 'resourceScene')
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mFunctions,      'function'     )
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mMDLGraphs,      'mdl_graph'    )

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Parse the Groups, Graphs, Resources and Functions to find a SBSObject with the given uid

        :return: True if a compnode has this uid
        """
        return self.getObjectFromUID(aUID, aRecursive=True) is not None

    @handle_exceptions()
    def computeUniqueIdentifier(self, aIdentifier, aSuffixId = 0):
        """
        computeUniqueIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used and generate a unique identifier if necessary

        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier_id
        """
        listsToCheck = [self.mResources,self.mResourcesScene,self.mFunctions,self.mGraphs,self.mGroups,self.mMDLGraphs]
        return self._computeUniqueIdentifier(aIdentifier, listsToCheck, aSuffixId)

    @handle_exceptions()
    def getMDLGraphList(self, aRecursive = True):
        """
        getMDLGraphList(aRecursive = True)
        Get the list of MDL graphs defined in this content, including sub-folders or not.

        :return: A list of :class:`.MDLGraph` objects
        """
        graphList = copy.copy(self.mMDLGraphs) if self.mMDLGraphs is not None else []

        # Recurse on groups
        if aRecursive and self.mGroups:
            for aContent in [aGroup.getContent() for aGroup in self.mGroups if aGroup.getContent() is not None]:
                graphList.extend(aContent.getMDLGraphList(aRecursive))

        return graphList

    @handle_exceptions()
    def getMDLGraph(self, aGraphIdentifier, aRecursive = True):
        """
        getMDLGraph(aGraphIdentifier, aRecursive = True)
        Get the MDL Graph object with the given identifier

        :param aGraphIdentifier: the identifier (not uid) of the graph to find
        :param aRecursive: True to parse sub folders, False to search only inside the current Content
        :type aGraphIdentifier: str
        :type aRecursive: bool
        :return: A :class:`.MDLGraph` object
        """
        if self.mMDLGraphs:
            aGraph =  next((aGraph for aGraph in self.mMDLGraphs if aGraph.mIdentifier == aGraphIdentifier), None)
            if aGraph is not None:
                return aGraph
        if aRecursive and self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aResult = aGroup.getContent().getMDLGraph(aGraphIdentifier, aRecursive)
                    if aResult is not None:
                        return aResult
        return None

    @handle_exceptions()
    def getSBSGraphList(self, aRecursive = True):
        """
        getSBSGraphList(aRecursive = True)
        Get the list of graphs defined in this content, including sub-folders or not.

        :return: A list of :class:`.SBSGraph` objects
        """
        graphList = copy.copy(self.mGraphs) if self.mGraphs is not None else []

        # Recurse on groups
        if aRecursive and self.mGroups:
            for aContent in [aGroup.getContent() for aGroup in self.mGroups if aGroup.getContent() is not None]:
                graphList.extend(aContent.getSBSGraphList(aRecursive))

        return graphList

    @handle_exceptions()
    def getSBSGraph(self, aGraphIdentifier, aRecursive = True):
        """
        getSBSGraph(aGraphIdentifier, aRecursive = True)
        Get the Graph object with the given identifier

        :param aGraphIdentifier: the identifier (not uid) of the graph to find
        :param aRecursive: True to parse sub folders, False to search only inside the current Content
        :type aGraphIdentifier: str
        :type aRecursive: bool
        :return: A :class:`.SBSGraph` object
        """
        if self.mGraphs:
            aGraph =  next((aGraph for aGraph in self.mGraphs if aGraph.mIdentifier == aGraphIdentifier), None)
            if aGraph is not None:
                return aGraph
        if aRecursive and self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aResult = aGroup.getContent().getSBSGraph(aGraphIdentifier, aRecursive)
                    if aResult is not None:
                        return aResult
        return None

    @handle_exceptions()
    def getSBSFunctionList(self, aRecursive = True):
        """
        getSBSFunctionList(aRecursive = True)
        Get the list of functions defined in this content, including sub-folders or not.

        :param aRecursive: True to parse sub folders, False to search only inside the current Content
        :type aRecursive: bool
        :return: A list of :class:`.SBSFunction` objects
        """
        functionList = copy.copy(self.mFunctions) if self.mFunctions is not None else []

        # Recurse on groups
        if aRecursive and self.mGroups:
            for aContent in [aGroup.getContent() for aGroup in self.mGroups if aGroup.getContent() is not None]:
                functionList.extend(aContent.getSBSFunctionList(aRecursive))

        return functionList

    @handle_exceptions()
    def getSBSFunction(self, aFunctionIdentifier, aRecursive = True):
        """
        getSBSFunction(aFunctionIdentifier, aRecursive = True)
        Get the Function object with the given identifier

        :param aFunctionIdentifier: the identifier (not uid) of the function to find
        :param aRecursive: True to parse sub folders, False to search only inside the current Content
        :type aFunctionIdentifier: str
        :type aRecursive: bool
        :return: A :class:`.SBSFunction` object
        """
        if self.mFunctions:
            aFunction =  next((aFunction for aFunction in self.mFunctions if aFunction.mIdentifier == aFunctionIdentifier), None)
            if aFunction is not None:
                return aFunction
        if aRecursive and self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aResult = aGroup.getContent().getSBSFunction(aFunctionIdentifier, aRecursive)
                    if aResult is not None:
                        return aResult
        return None

    @handle_exceptions()
    def getSBSGroupList(self, aRecursive = True):
        """
        getSBSGroupList(aRecursive = True)
        Get the list of groups defined in this content, including sub-folders or not.

        :return: A list of :class:`.SBSGroup` objects
        """
        groupList = copy.copy(self.mGroups) if self.mGroups is not None else []

        # Recurse on groups
        if aRecursive and self.mGroups:
            for aContent in [aGroup.getContent() for aGroup in self.mGroups if aGroup.getContent() is not None]:
                groupList.extend(aContent.getSBSGroupList(aRecursive))

        return groupList

    @handle_exceptions()
    def getSBSGroup(self, aGroupIdentifier, aRecursive = True):
        """
        getSBSGroup(aGroupIdentifier, aRecursive = True)
        Get the Group object with the given identifier

        :param aGroupIdentifier: the identifier (not uid) of the group to find
        :param aRecursive: True to parse sub folders, False to search only inside the current Content
        :type aGroupIdentifier: str
        :type aRecursive: bool
        :return: A :class:`.SBSGroup` object
        """
        if self.mGroups:
            aGroup =  next((aGroup for aGroup in self.mGroups if aGroup.mIdentifier == aGroupIdentifier), None)
            if aGroup is not None:
                return aGroup
        if aRecursive and self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aResult = aGroup.getContent().getSBSGroup(aGroupIdentifier, aRecursive)
                    if aResult is not None:
                        return aResult
        return None

    @handle_exceptions()
    def getSBSResourceList(self, aRecursive = True, aIncludeSceneResources = True):
        """
        getSBSResourceList(aRecursive = True, aIncludeSceneResources = True)
        Get the list of the resources defined in this content, including sub-folders or not.

        :param aRecursive: True to parse sub folders, False to search only inside the current Group. Default to True
        :type aRecursive: bool, optional
        :param aIncludeSceneResources: True to include the Scene/Mesh resources. Default to True
        :type aIncludeSceneResources: bool, optional
        :return: A list of :class:`.SBSResource` objects
        """
        resourceList = copy.copy(self.mResources) if self.mResources is not None else []
        if aIncludeSceneResources and self.mResourcesScene:
            resourceList.extend(self.mResourcesScene)

        # Recurse on groups
        if aRecursive and self.mGroups:
            for aContent in [aGroup.getContent() for aGroup in self.mGroups if aGroup.getContent() is not None]:
                resourceList.extend(aContent.getSBSResourceList(aRecursive, aIncludeSceneResources))

        return resourceList

    @handle_exceptions()
    def getSBSResource(self, aResourceIdentifier, aRecursive = True):
        """
        getSBSResource(self, aResourceIdentifier, aRecursive = True)
        Get the Resource object with the given identifier

        :param aResourceIdentifier: the identifier (not uid) of the resource to find
        :param aRecursive: True to parse sub folders, False to search only inside the current Content
        :type aResourceIdentifier: str
        :type aRecursive: bool
        :return: A :class:`.SBSResource` object
        """
        resourceLists = [self.mResources, self.mResourcesScene]
        for aList in resourceLists:
            if aList:
                aResource = next((aResource for aResource in aList if aResource.mIdentifier == aResourceIdentifier), None)
                if aResource is not None:
                    return aResource
        if aRecursive and self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aResult = aGroup.getContent().getSBSResource(aResourceIdentifier, aRecursive)
                    if aResult is not None:
                        return aResult
        return None

    @handle_exceptions()
    def getObjectFromUID(self, aUID, aRecursive=True):
        """
        getObjectFromUID(aUID, aRecursive=True)
        Parse the Groups, Graphs, Resources and Functions to find the object with the given uid

        :param aUID: The UID of the object (group, graph, resource or function) to look for
        :param aRecursive: True to search recursively in all groups, False to search only in the direct content. Default to True
        :type aUID: str
        :type aRecursive: boolean, optional
        :return: The :class:`SBSObject` if found, None otherwise
        """
        listToParse = [self.mResources,self.mResourcesScene,self.mFunctions,self.mGraphs,self.mGroups,self.mMDLGraphs]
        for aList,aObject in [(aList,aObject) for aList in listToParse if aList is not None for aObject in aList]:
            if aObject.mUID == aUID:
                return aObject

        # Recurse on groups:
        if aRecursive and self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aObject = aGroup.getContent().getObjectFromUID(aUID, aRecursive)
                    if aObject is not None:
                        return aObject
        return None

    @handle_exceptions()
    def getObject(self, aIdentifier):
        """
        getObject(aIdentifier)
        Get the object with the given identifier in the content directly under this content.

        :param aIdentifier: the identifier (not uid) of the object to find
        :type aIdentifier: str
        :return: A :class:`.SBSObject` if found, None otherwise
        """
        for aFunction in [self.getSBSGraph, self.getSBSFunction, self.getSBSGroup, self.getSBSResource, self.getMDLGraph]:
            aObject = aFunction(aIdentifier, aRecursive=False)
            if aObject is not None:
                return aObject
        return None


    @handle_exceptions()
    def getSBSGroupInternalPath(self, aGroupIdentifier, aPath = ''):
        """
        getSBSGroupInternalPath(aGroupIdentifier, aPath = '')
        Get the path of the given group relatively to the current content

        :return: A string containing the relative path from the current content to the given group, None otherwise
        """
        if self.mGroups is None:
            return None

        aGroup =  next((aGroup for aGroup in self.mGroups if aGroup.mIdentifier == aGroupIdentifier), None)
        if aGroup is not None:
            return aPath + aGroup.mIdentifier

        if self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aResult = aGroup.getContent().getSBSGroupInternalPath(aGroupIdentifier, aPath + aGroup.mIdentifier + '/')
                    if aResult is not None:
                        return aResult
        return None


    @handle_exceptions()
    def getObjectInternalPath(self, aUID, aObjectClass=None, aPath = ''):
        """
        getObjectInternalPath(aUID, aObjectClass=None, aPath = '')
        Get the path of the given object relatively to the current content.
        Only objects that are directly under a Content node can be found:
        :class:`.SBSGroup`
        :class:`.SBSGraph`
        :class:`.MDLGraph`
        :class:`.SBSResource`
        :class:`.SBSFunction`

        :param aUID: the UID of the object to search
        :param aObjectClass: the class of the object to search. If None, the function will look into all the kind of content
        :type aUID: str
        :type aObjectClass: class, optional
        :return: A string containing the relative path from the current content to the given object if found, None otherwise
        """
        if   aObjectClass is SBSGroup:            aListMember = ['mGroups']
        elif aObjectClass is SBSResource:         aListMember = ['mResources','mResourcesScene']
        elif aObjectClass is graph.SBSGraph:      aListMember = ['mGraphs']
        elif aObjectClass is mdl.MDLGraph:        aListMember = ['mMDLGraphs']
        elif aObjectClass is graph.SBSFunction:   aListMember = ['mFunctions']
        else:
             aListMember = ['mGroups', 'mResources', 'mResourcesScene',  'mGraphs', 'mFunctions', 'mMDLGraphs']

        # Try to find the object in the appropriate list
        for aMember in aListMember:
            if getattr(self, aMember):
                aObject = next((aObject for aObject in getattr(self, aMember) if aObject.mUID == aUID), None)
                if aObject is not None:
                    return aPath + aObject.mIdentifier if hasattr(aObject, 'mIdentifier') else aPath

        # Try to find the object in a sub group
        if self.mGroups:
            for aGroup in self.mGroups:
                if aGroup.getContent() is not None:
                    aResult = aGroup.getContent().getObjectInternalPath(aUID, aObjectClass, aPath + aGroup.mIdentifier + '/')
                    if aResult is not None:
                        return aResult

        return None

    @handle_exceptions()
    def removeObject(self, aObject):
        """
        removeObject(aObject)
        Remove the given object from this content

        :param aObject: The object (group, graph, function, resource) to remove from this content, as a SBSObject or given its UID
        :type aObject: :class:`.SBSObject` or UID
        :return: True if success
        """
        aUID = aObject.mUID if SBSContent.isContentChildType(aObject) else aObject
        aObject = self.getObjectFromUID(aUID=aUID, aRecursive=False)
        if aObject is None:
            raise SBSImpossibleActionError('Cannot remove the object '+python_helpers.castStr(aUID)+' from this content, cannot find it')

        if   isinstance(aObject, SBSGroup):             aMember = 'mGroups'
        elif isinstance(aObject, graph.SBSGraph):       aMember = 'mGraphs'
        elif isinstance(aObject, graph.SBSFunction):    aMember = 'mFunctions'
        elif isinstance(aObject, mdl.MDLGraph):         aMember = 'mMDLGraphs'
        elif isinstance(aObject, SBSResourceScene):     aMember = 'mResourcesScene'
        else:                                           aMember = 'mResources'

        getattr(self, aMember).remove(aObject)
        if not getattr(self, aMember):
            setattr(self, aMember, None)
        return True
