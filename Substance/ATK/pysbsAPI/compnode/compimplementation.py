# coding: utf-8
"""
| Module **compimplementation** provides the definition of the class :class:`.SBSCompImplementation` and all the possible implementation:
| - :class:`.SBSCompFilter`
| - :class:`.SBSCompInstance`
| - :class:`.SBSCompInputBridge`
| - :class:`.SBSCompOutputBridge`
"""

from __future__ import unicode_literals
import copy
import logging
log = logging.getLogger(__name__)
import weakref

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject, UIDGenerator
from pysbs import api_helpers
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import sbscommon
from pysbs import params

from .common import SBSCompImplWithParams, SBSOutputBridging
from .paramgraph import SBSParamsGraph


# =======================================================================
@doc_inherit
class SBSCompFilter(SBSCompImplWithParams):
    """
    Class that contains information on a compositing node filter as defined in a .sbs file

    Members:
        * mFilter      (str): filter type, among the identifiers available for Filter definition (:mod:`.sbsfilters`)
        * mParameters  (list of :class:`.SBSParameter`): filter parameters list (filters parameters, authoring parameters, resources paths, etc.).
        * mParamArrays (list of :class:`.SBSParamsArray`, optional): parameters arrays, e.g. used for gradient data.
        * mParamGraphs (list of :class:`.SBSParamsGraph`, optional): parameters set graphs, e.g. used for FX-Map parametrization.
    """
    def __init__(self,
                 aFilter        = '',
                 aParameters    = None,
                 aParamArrays   = None,
                 aParamGraphs   = None):
        super(SBSCompFilter, self).__init__(aParameters)
        self.mFilter        = aFilter
        self.mParamArrays   = aParamArrays
        self.mParamGraphs   = aParamGraphs

        self.mMembersForEquality = ['mFilter',
                                    'mParamArrays',
                                    'mParamGraphs']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSCompFilter, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mFilter      = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'filter'      )
        self.mParamArrays = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paramsArrays', 'paramsArray', params.SBSParamsArray)
        self.mParamGraphs = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'paramsGraphs', 'paramsGraph' , SBSParamsGraph)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mFilter      , 'filter'       )
        aSBSWriter.writeListOfSBSNode(aXmlNode        , self.mParameters  , 'parameters'   , 'parameter'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode        , self.mParamArrays , 'paramsArrays' , 'paramsArray'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode        , self.mParamGraphs , 'paramsGraphs' , 'paramsGraph'  )

    @handle_exceptions()
    def changeDependencyUID(self, newDepUID):
        """
        changeDependencyUID(newDepUID)
        In case of a filter Bitmap or SVG, change the UID of the dependency referenced by the resource.

        :param newDepUID: The new dependency UID
        :type newDepUID: str
        """
        aPath = self.getResourcePath()
        if aPath:
            oldUID = api_helpers.splitPathAndDependencyUID(aPath)[1]
            if oldUID:
                aPath = aPath.replace(oldUID, newDepUID)
                self.changeResourcePath(aPath)

    @handle_exceptions()
    def changeResourcePath(self, newPath):
        """
        changeResourcePath(newPath)
        In case of a filter Bitmap or SVG, change the referenced resource path.

        :param newPath: The new resource path
        :type newPath: str
        """
        if self.isAResource():
            if self.mFilter == sbslibrary.getFilterDefinition(sbsenum.FilterEnum.BITMAP).mIdentifier:
                param = sbsenum.CompNodeParamEnum.BITMAP_RESOURCE_PATH
            else:
                param = sbsenum.CompNodeParamEnum.SVG_RESOURCE_PATH
            self.setParameterValue(param, newPath)

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther, aParentContainer = None)
        Compare the identifiers of the two filters to classify them.

        :param aOther: The filter to compare to.
        :param aParentContainer: The graph containing the nodes to classify
        :type aOther: :class:`.SBSCompFilter`
        :type aParentContainer: :class:`.SBSGraph`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        selfValue = self.getDefinition().mIdentifier
        otherValue = aOther.getDefinition().mIdentifier
        return (selfValue > otherValue) - (selfValue < otherValue)

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the filter definition (Inputs, Outputs, Parameters)

        :return: a :class:`.CompNodeDef` object
        """
        return sbslibrary.getFilterDefinition(self.mFilter)

    @handle_exceptions()
    def getDisplayName(self):
        return 'Filter '+ self.mFilter

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Check if the given uid is already used in the context of the comp filter

        return: True if the uid is already used, False otherwise
        """
        listToParse = [self.mParamArrays,self.mParamGraphs]
        for aList,aObject in [(aList,aObject) for aList in listToParse if aList is not None for aObject in aList]:
            if aObject.mUID == aUID:
                return True
        return False

    @handle_exceptions()
    def getResourcePath(self):
        """
        getResourcePath()
        If this node is a Bitmap or SVG, get the path to the resource used by this node

        :return: The path relative to the package used by this node if possible, None otherwise
        """
        if self.isAResource():
            if self.mFilter == sbslibrary.getFilterDefinition(sbsenum.FilterEnum.BITMAP).mIdentifier:
                param = sbsenum.CompNodeParamEnum.BITMAP_RESOURCE_PATH
            else:
                param = sbsenum.CompNodeParamEnum.SVG_RESOURCE_PATH
            return self.getParameterValue(param)
        return None

    @handle_exceptions()
    def isAFxMap(self):
        """
        isAFxMap()

        :return: True if this filter is a FxMap, False otherwise
        """
        return self.mFilter == sbslibrary.getFilterDefinition(sbsenum.FilterEnum.FXMAPS).mIdentifier

    @handle_exceptions()
    def isAPixelProcessor(self):
        """
        isAPixelProcessor()

        :return: True if this filter is a Pixel Processor, False otherwise
        """
        return self.mFilter == sbslibrary.getFilterDefinition(sbsenum.FilterEnum.PIXEL_PROCESSOR).mIdentifier

    @handle_exceptions()
    def isAValueProcessor(self):
        """
        isAValueProcessor()

        :return: True if this filter is a Value Processor, False otherwise
        """
        return self.mFilter == sbslibrary.getFilterDefinition(sbsenum.FilterEnum.VALUE_PROCESSOR).mIdentifier

    @handle_exceptions()
    def isAResource(self):
        """
        isAResource()

        :return: True if the filter uses a resource, meaning is a filter of kind BITMAP or SVG, False otherwise.
        """
        return  self.mFilter == sbslibrary.getFilterDefinition(sbsenum.FilterEnum.BITMAP).mIdentifier or \
                self.mFilter == sbslibrary.getFilterDefinition(sbsenum.FilterEnum.SVG).mIdentifier

    @handle_exceptions()
    def initFxMapGraph(self):
        """
        initFxMapGraph()
        Init the :class:`.SBSParamsGraph` of this filter, if it is a FxMap

        :return: The graph of this FxMap as a :class:`.SBSParamsGraph`, None otherwise.
        """
        if self.mParamGraphs is None:
            self.mParamGraphs = []

        if not self.mParamGraphs:
            aUID = UIDGenerator.generateUID(self)
            aParamGraph = SBSParamsGraph(aUID = aUID, aParamsGraphDatas=[], aParamsGraphNodes=[])
            self.mParamGraphs.append(aParamGraph)

        return self.mParamGraphs



# =======================================================================
@doc_inherit
class SBSCompInstance(SBSCompImplWithParams):
    """
    Class that contains information on a compositing node instance as defined in a .sbs file

    Members:
        * mPath            (str): path of the graph definition this instance refers to.
        * mParameters      (list of :class:`.SBSParameter`): instance parameters list.
        * mOutputBridgings (list of :class:`.SBSOutputBridging`, optional): List of bridging between outputs of this instance node and the graph definition.
        * mGUILayoutComp   (:class:`.SBSGUILayoutComp`, optional): GUI flags and options instance overload.
        * mRefGraph        (:class:`.SBSGraph`, optional): reference to the graph that this node instantiates.
    """
    def __init__(self,
                 aPath              = None,
                 aParameters        = None,
                 aOutputBridgings   = None,
                 aGUILayoutComp     = None,
                 aRefGraph          = None,
                 aRefDependency     = None):
        super(SBSCompInstance, self).__init__(aParameters)
        self.mPath              = aPath
        self.mOutputBridgings   = aOutputBridgings if aOutputBridgings is not None else []
        self.mGUILayoutComp     = aGUILayoutComp
        self.mRefGraph          = weakref.ref(aRefGraph) if aRefGraph is not None else None
        self.mRefDependency     = weakref.ref(aRefDependency) if aRefDependency is not None else None

        self.mMembersForEquality = ['mPath',
                                    'mOutputBridgings']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSCompInstance, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mPath            = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'path'           )
        self.mGUILayoutComp   = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'GUIlayoutComp'  , sbscommon.SBSGUILayoutComp)
        self.mParameters      = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'parameters'     , 'parameter', params.SBSParameter)
        self.mOutputBridgings = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'outputBridgings', 'outputBridging', SBSOutputBridging)

        aContext.addSBSObjectToResolve(self)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mPath      , 'path'              )
        aSBSWriter.writeSBSNode(aXmlNode      , self.mGUILayoutComp    , 'GUIlayoutComp'     )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mParameters       , 'parameters'        , 'parameter'      )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mOutputBridgings  , 'outputBridgings'   , 'outputBridging' )

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther, aParentContainer = None)
        Compare the path of the two instances to classify them.

        :param aOther: The filter to compare to.
        :param aParentContainer: The graph containing the nodes to classify
        :type aOther: :class:`.SBSCompInstance`
        :type aParentContainer: :class:`.SBSGraph`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        return (self.mPath > aOther.mPath) - (self.mPath < aOther.mPath)

    @handle_exceptions()
    def changeDependencyUID(self, aSBSDocument, newDepUID):
        """
        changeDependencyUID(aSBSDocument, newDepUID)
        Change the UID of the dependency referenced by this instance.

        :param aSBSDocument: The root document, required to reset all the internal links to the referenced graph
        :type aSBSDocument: :class:`.SBSDocument`
        :param newDepUID: The new dependency UID
        :type newDepUID: str
        """
        oldUID = self.getDependencyUID()
        self.mPath = self.mPath.replace(oldUID, newDepUID)
        self.resolveDependency(aSBSDocument)

    def changeInstancePath(self, aParentDocument, aInstanceDocument, aGraphRelPath):
        """
        changeInstancePath(aParentDocument, aInstanceDocument, aGraphRelPath)
        Change the function referenced by this instance.
        If aInstanceDocument is not already declared as a dependency, the dependency will be added to aParentDocument.

        :param aParentDocument: The parent document of this node
        :type aParentDocument: :class:`.SBSDocument`
        :param aInstanceDocument: The document containing the function to reference by this instance (can be equal to parent document)
        :type aInstanceDocument: :class:`.SBSDocument`
        :param aGraphRelPath: The graph path, relatively to its parent package aInstanceDocument (pkg:///myGroup/myGraph)
        :type aGraphRelPath: str
        """
        outValues = aParentDocument.addReferenceOnDependency(aDependencyPath = aInstanceDocument.mFileAbsPath,
                                                            aRelPathToObject = api_helpers.splitPathAndDependencyUID(aGraphRelPath)[0])
        aGraphRelPath = outValues[1]
        self.mPath = aGraphRelPath
        self.resolveDependency(aParentDocument)

    @handle_exceptions()
    def resolveDependency(self, aSBSDocument):
        """
        resolveDependency(aSBSDocument)
        Allow to resolve the dependency of the compositing instance node with the graph it references.

        :param aSBSDocument: The root document
        :type aSBSDocument: :class:`.SBSDocument`
        """
        if self.mPath is None or not api_helpers.hasPkgPrefix(self.mPath):
            return False

        aPath = api_helpers.removePkgPrefix(self.mPath)
        aGraphRelPath, aDepUID = api_helpers.splitPathAndDependencyUID(aPath)

        # if the tag ?dependency= is not present, take the first dependency of the document
        if aDepUID is None:
            try:
                aDepUID = aSBSDocument.getDependencyContainingInternalPath(self.mPath).mUID
            except:
                log.warning('Graph %s not found', aPath)
                return False
        try:
            aDep = aSBSDocument.getDependency(aUID = aDepUID)
            self.mRefDependency = weakref.ref(aDep)
            aPackageWR = aDep.getRefPackage()
            try:
                aGraph = aPackageWR().getObjectFromInternalPath(aGraphRelPath)
                self.mRefGraph = weakref.ref(aGraph)
            except:
                log.warning('Graph %s/%s not found', aDep.mFilename, aGraphRelPath)
        except:
            log.warning('Dependency %s not found, cannot resolve: %s', aDepUID, aPath)

        return self.mRefGraph is not None


    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Build a :class:`.CompNodeParam` object to describe the inputs, outputs and parameters of this graph instance

        :return: A :class:`.CompNodeParam` object
        """
        # Copy the default instance parameter from the library
        compInstanceDefinition = sbslibrary.getFilterDefinition(sbsenum.FilterEnum.COMPINSTANCE)
        if compInstanceDefinition is None:
            return None
        thisInstanceDef = copy.deepcopy(compInstanceDefinition)

        if self.mRefGraph is None or self.mRefGraph() is None:
            return thisInstanceDef

        # Add the input entries of the reference graph
        for aInputImage in self.mRefGraph().getInputImages():
            aInput = sbslibrary.CompNodeInput(aIdentifier = aInputImage.mIdentifier,
                                              aType       = aInputImage.getType(),
                                              aIsPrimary  = self.mRefGraph().isPrimaryInput(aInputImage))
            thisInstanceDef.mInputs.append(aInput)

        # Add the Input Inheritance
        thisInstanceDef.mInheritance.insert(0, sbsenum.ParamInheritanceEnum.INPUT)

        # Add the outputs of the reference graph
        for output in self.mRefGraph().getGraphOutputs():
            aType = self.mRefGraph().getGraphOutputType(output.mIdentifier)
            aOutput = sbslibrary.CompNodeOutput(aIdentifier = output.mIdentifier,
                                                aType       = int(aType))
            thisInstanceDef.mOutputs.append(aOutput)

        # Add the input parameters of the reference graph
        for aParamInput in self.mRefGraph().getInputParameters():
            aType = aParamInput.getType()
            aDefaultValue = aParamInput.getDefaultValue()
            aDefaultValue = api_helpers.formatValueForTypeStr(aDefaultValue, aType)
            aIsConnectable = aParamInput.getIsConnectable()
            aParameter = sbslibrary.CompNodeParam(aParameter     = aParamInput.mIdentifier,
                                                  aType          = aType,
                                                  aDefaultValue  = aDefaultValue,
                                                  aIsConnectable = aIsConnectable)

            thisInstanceDef.mParameters.append(aParameter)

        return thisInstanceDef

    @handle_exceptions()
    def getDependencyUID(self):
        """
        getDependencyUID()
        Get the UID of the dependency referenced by this instance

        :return: The dependency UID as a string if found, None otherwise
        """
        if self.mRefDependency() is not None:
            return self.mRefDependency().mUID
        return api_helpers.splitPathAndDependencyUID(self.mPath)[1]

    @handle_exceptions()
    def getDisplayName(self):
        return 'Instance of '+ self.mPath

    @handle_exceptions()
    def getCompOutputBridging(self, aIdentifier):
        """
        getCompOutputBridging(aIdentifier)
        Get the SBSOutputBridging corresponding to the given identifier

        :param aIdentifier: required identifier
        :type aIdentifier: str
        :return: a :class:`.SBSOutputBridging` object if found, None otherwise
        """
        if self.mOutputBridgings:
            return next((outputBridge for outputBridge in self.mOutputBridgings if outputBridge.mIdentifier == aIdentifier), None)
        return None

    @handle_exceptions()
    def getCompOutputBridgingFromUID(self, aUID):
        """
        getCompOutputBridgingFromUID(aUID)
        Get the SBSOutputBridging corresponding to the given output uid

        :param aUID: the unique identifier to look for
        :type aUID: str
        :return: a :class:`.SBSOutputBridging` object if found, None otherwise
        """
        if self.mOutputBridgings:
            return next((outputBridge for outputBridge in self.mOutputBridgings if outputBridge.mUID == aUID), None)
        return None

    @handle_exceptions()
    def getReferenceAbsPath(self):
        """
        getReferenceAbsPath()
        Get the absolute path of the graph referenced by this instance.

        :return: The absolute path of the graph referenced by this instance, in the format absolutePath/filename.sbs/graphIdentifier, as a string
        """
        if not self.mRefDependency:
            return self.mPath

        aPath = api_helpers.removePkgPrefix(self.mPath)
        aPath = api_helpers.splitPathAndDependencyUID(aPath)[0]
        aPath = aPath.replace('\\', '/')
        aDepAbsPath = self.mRefDependency().mFileAbsPath.replace('\\', '/')
        aPath = aDepAbsPath + '/' + aPath
        return aPath

    @handle_exceptions()
    def getReferenceInternalPath(self):
        """
        getReferenceInternalPath()
        If this node is an instance, get the path of the referenced graph relatively to the package (pkg:///).

        :return: The path as a string
        """
        return self.mPath



# =======================================================================
@doc_inherit
class SBSCompInputBridge(SBSCompImplWithParams):
    """
    Class that contains information on an input node as defined in a .sbs file

    Members:
        * mEntry      (str): uid of this input (/graph/paramInputs/paramInput/uid).
        * mParameters (list of :class:`.SBSParameter`): input parameters list.
    """
    def __init__(self,
                 aEntry = '',
                 aParameters = None):
        super(SBSCompInputBridge, self).__init__(aParameters)
        self.mEntry         = aEntry

        self.mMembersForEquality = ['mParameters']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSCompInputBridge, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mEntry      = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'entry'     )
        self.mParameters = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'parameters', 'parameter', params.SBSParameter)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mEntry      , 'entry'       )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mParameters , 'parameters'  , 'parameter'  )

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther, aParentContainer = None)
        If aParentContainer is provided, compare the identifiers of the two input nodes to classify them, else use the Entry UID.

        :param aOther: The filter to compare to.
        :param aParentContainer: The graph containing the nodes to classify
        :type aOther: :class:`.SBSCompInputBridge`
        :type aParentContainer: :class:`.SBSGraph`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        if aParentContainer:
            selfValue = aParentContainer.getInputParameterFromUID(self.mEntry).mIdentifier
            otherValue = aParentContainer.getInputParameterFromUID(aOther.mEntry).mIdentifier
        else:
            selfValue = self.mEntry
            otherValue = aOther.mEntry
        return (selfValue > otherValue) - (selfValue < otherValue)

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the comp input bridge definition (Inputs, Outputs, Parameters)

        :return: a :class:`.CompNodeDef` object
        """
        return sbslibrary.getInputBridgeDefinition()

    @handle_exceptions()
    def getDisplayName(self):
        return 'Input node'



# =======================================================================
@doc_inherit
class SBSCompOutputBridge(SBSObject):
    """
    Class that contains information on an output node as defined in a .sbs file

    Members:
        * mOutput              (str): uid of this output.  (/graph/graphOutputs/graphOutput/uid).
        * mConnectionColorType (str, optional): connection color type. Type format defined at :class:`.ParamTypeEnum`
    """
    def __init__(self,
                 aOutput = '',
                 aConnectionColorType = None):
        super(SBSCompOutputBridge, self).__init__()
        self.mOutput                = aOutput
        self.mConnectionColorType   = aConnectionColorType

        self.mMembersForEquality = ['mConnectionColorType']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mOutput                = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'output'               )
        self.mConnectionColorType   = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'connectionColorType'  )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mOutput              , 'output'              )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mConnectionColorType , 'connectionColorType' )

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther, aParentContainer = None)
        If aParentContainer is provided, compare the identifiers of the two output nodes to classify them, else use the Output UID.

        :param aOther: The filter to compare to.
        :param aParentContainer: The graph containing the nodes to classify
        :type aOther: :class:`.SBSCompOutputBridge`
        :type aParentContainer: :class:`.SBSGraph`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        if aParentContainer:
            selfValue  = aParentContainer.getGraphOutputFromUID(self.mOutput).mIdentifier
            otherValue = aParentContainer.getGraphOutputFromUID(aOther.mOutput).mIdentifier
        else:
            selfValue  = self.mOutput
            otherValue = aOther.mOutput
        return (selfValue > otherValue) - (selfValue < otherValue)

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the output bridge definition (Inputs, Outputs, Parameters)

        :return: a :class:`.CompNodeDef` object
        """
        return sbslibrary.getOutputBridgeDefinition()

    @handle_exceptions()
    def getDisplayName(self):
        """
        getDisplayName()
        Get the display name of this node

        :return: the display name as a string
        """
        return 'Output node'



# =======================================================================
@doc_inherit
class SBSCompImplementation(SBSObject):
    """
    Class that contains information on the implementation of a compositing node as defined in a .sbs file.
    The implementation is exclusive, only one member of the SBSCompImplementation is defined.

    Members:
        * mCompFilter       (:class:`.SBSCompFilter`): filter type compositing node definition.
        * mCompInstance     (:class:`.SBSCompInstance`): graph instance node.
        * mCompInputBridge  (:class:`.SBSCompInputBridge`): graph input bridge node.
        * mCompOutputBridge (:class:`.SBSCompOutputBridge`): graph output bridge node.
    """
    def __init__(self,
                 aCompFilter        = None,
                 aCompInstance      = None,
                 aCompInputBridge   = None,
                 aCompOutputBridge  = None):
        super(SBSCompImplementation, self).__init__()
        self.mCompFilter        = aCompFilter
        self.mCompInstance      = aCompInstance
        self.mCompInputBridge   = aCompInputBridge
        self.mCompOutputBridge  = aCompOutputBridge

        self.mMembersForEquality = ['mCompFilter',
                                    'mCompInstance',
                                    'mCompInputBridge',
                                    'mCompOutputBridge']

        self._mImplKind = None

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mCompFilter       = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'compFilter'      , SBSCompFilter)
        self.mCompInstance     = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'compInstance'    , SBSCompInstance)
        self.mCompInputBridge  = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'compInputBridge' , SBSCompInputBridge)
        self.mCompOutputBridge = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'compOutputBridge', SBSCompOutputBridge)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeSBSNode(aXmlNode ,  self.mCompFilter       , 'compFilter'        )
        aSBSWriter.writeSBSNode(aXmlNode ,  self.mCompInstance     , 'compInstance'      )
        aSBSWriter.writeSBSNode(aXmlNode ,  self.mCompInputBridge  , 'compInputBridge'   )
        aSBSWriter.writeSBSNode(aXmlNode ,  self.mCompOutputBridge , 'compOutputBridge'  )

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther, aParentContainer = None)
        | Use the definition of the two CompImplementation to classify them.
        | To classify the different kind of CompImplementation, this order is specify:
        | Filter < Instance < Input < Output.
        | In case of equality, the appropriate classify function is called, depending on the kind of implementation.

        :param aOther: The filter to compare to.
        :param aParentContainer: The graph containing the nodes to classify
        :type aOther: :class:`.SBSCompImplementation`
        :type aParentContainer: :class:`.SBSGraph`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        # Compare Implementation kind
        selfKind = self.getImplementationKind()
        otherKind = aOther.getImplementationKind()
        if selfKind != otherKind:
            return max(-1, min(1, selfKind - otherKind))

        # Compare the two identical implementation
        return self.getImplementation().classify(aOther.getImplementation(), aParentContainer)

    @handle_exceptions()
    def getImplementation(self):
        """
        getImplementation(self)
        Return the appropriate node implementation depending on the compositing node kind

        :return: A :class:`.SBSCompImplWithParams` or a :class:`.SBSCompOutputBridge`
        """
        if self.isAFilter():            return self.mCompFilter
        elif self.isAnInstance():       return self.mCompInstance
        elif self.isAnInputBridge():    return self.mCompInputBridge
        elif self.isAnOutputBridge():   return self.mCompOutputBridge

    @handle_exceptions()
    def getImplementationKind(self):
        """
        getImplementationKind()
        Get the implementation kind of this node, among the list defined in :class:`.CompImplementationKindEnum`

        :return: The :class:`.CompImplementationKindEnum`
        """
        if self._mImplKind is None:
            if self.isAFilter():            self._mImplKind = sbsenum.CompImplementationKindEnum.FILTER
            elif self.isAnInstance():       self._mImplKind = sbsenum.CompImplementationKindEnum.INSTANCE
            elif self.isAnInputBridge():    self._mImplKind = sbsenum.CompImplementationKindEnum.INPUT
            elif self.isAnOutputBridge():   self._mImplKind = sbsenum.CompImplementationKindEnum.OUTPUT

        return self._mImplKind

    @handle_exceptions()
    def isAFilter(self):
        """
        isAFilter()

        :return: True if this is a Compositing Node Filter, False otherwise.
        """
        return self.mCompFilter is not None

    @handle_exceptions()
    def isAnInstance(self):
        """
        isAnInstance()

        :return: True if this is a Compositing Node Instance, False otherwise.
        """
        return self.mCompInstance is not None

    @handle_exceptions()
    def isAnInputBridge(self):
        """
        isAnInputBridge()

        :return: True if this is an Input Bridge, False otherwise.
        """
        return self.mCompInputBridge is not None

    @handle_exceptions()
    def isAnOutputBridge(self):
        """
        isAnOutputBridge()

        :return: True if this is an Output Bridge, False otherwise.
        """
        return self.mCompOutputBridge is not None

