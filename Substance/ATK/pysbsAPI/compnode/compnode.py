# coding: utf-8
"""
Module **compnode** aims to define SBSObjects that are relative to a compositing Node, mostly :class:`.SBSCompNode`,
:class:`.SBSCompImplementation` and :class:`.SBSCompOutput`.
"""

from __future__ import unicode_literals
import copy
import weakref
import re
import logging
log = logging.getLogger(__name__)

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import api_helpers, python_helpers, api_exceptions
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import sbscommon
from pysbs import params
from pysbs import sbsgenerator

from .compimplementation import SBSCompImplementation
from .common import SBSCompOutput, SBSCompImplWithParams, SBSCompInputValue


# =======================================================================
@doc_inherit
class SBSCompNode(sbscommon.SBSNode):
    """
    Class that contains information on a compositing node as defined in a .sbs file

    Members:
        * mGUIName            (str, optional): name of the node.
        * mUID                (str): node unique identifier in the /compNodes/ context.
        * mDisabled           (str, optional): this node is disabled ("1" / None).
        * mGUILayout          (:class:`.SBSGUILayout`): GUI position/options
        * mOptions            (list of :class:`.SBSOption`): options list.
        * mCompOutputs        (list of :class:`.SBSCompOutput`, optional): outputs list.
        * mConnections        (list of :class:`.SBSConnection`, optional): input connections list.
        * mCompImplementation (:class:`.SBSCompImplementation`): implementation of the compositing node.
        * mInputValues        (list of :class:`.SBSCompInputValue`: Input values for the node
    """
    def __init__(self,
                 aGUIName       = None,
                 aUID           = '',
                 aDisabled      = None,
                 aGUILayout     = None,
                 aOptions       = None,
                 aCompOutputs   = None,
                 aConnections    = None,
                 aCompImplementation = None,
                 aInputValues = None):
        super(SBSCompNode, self).__init__(aGUIName, aUID, aDisabled, aConnections, aGUILayout)
        self.mOptions            = aOptions
        self.mCompOutputs        = aCompOutputs
        self.mCompImplementation = aCompImplementation
        self.mInputValues = aInputValues

        self.mMembersForEquality.append('mOptions')
        self.mMembersForEquality.append('mCompOutputs')
        self.mMembersForEquality.append('mCompImplementation')
        self.mMembersForEquality.append('mInputValues')


    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSCompNode, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mOptions            = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'options', 'option', sbscommon.SBSOption)
        self.mCompOutputs        = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'compOutputs', 'compOutput', SBSCompOutput)
        self.mCompImplementation = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'compImplementation', SBSCompImplementation)
        self.mInputValues        = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'inputValues', 'compInputValue', SBSCompInputValue)
        if self.isAValueProcessor():
            # Set up weak reference for dynamic value to comp node to keep type
            # in sync
            aVpf = self.getValProcFunction(createIfEmtpy=False)
            if aVpf:
                aVpf.mValueProcessorRef = weakref.ref(self)
                if self.mCompOutputs[0].mCompType != str(aVpf.getOutputType()):
                    # Type is mismatching, correct and log a warning
                    aVpf.updateValueProcessorType()
                    log.warning('Value processor type is not matching function type, correcting')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        if self.isAValueProcessor():
            # Validate a value processor has a valid output type
            aVpf = self.getValProcFunction(createIfEmtpy=False)
            if aVpf:
                if self.mCompOutputs[0].mCompType != str(aVpf.getOutputType()):
                    raise api_exceptions.SBSTypeError('Mismatching type in Value Processor and its function')

        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mGUIName           , 'GUIName'           )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID               , 'uid'               )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDisabled          , 'disabled'          )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mGUILayout         , 'GUILayout'         )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mOptions           , 'options'           , 'option'     )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mCompOutputs       , 'compOutputs'       , 'compOutput' )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mConnections       , 'connections'       , 'connection'  )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mCompImplementation, 'compImplementation')
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mInputValues       , 'inputValues'       , 'compInputValue')

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther, aParentContainer = None)
        | Use the definition of the two nodes to classify them, and their GUI position if they have the same definition.
        | To classify the different kind of CompImplementation, this order is specify:
        | Filter < Instance < Input < Output.
        | For the Filter, the filter identifier is used to classify them.
        | For the Instance, the lexicographic order is used on the instance path.
        | At a final option, the GUI position is used, and in this case, mostLeft < mostRight and then mostUp < mostDown.

        :param aOther: The node to compare to.
        :param aParentContainer: The graph containing the nodes to classify
        :type aOther: :class:`.SBSCompNode`
        :type aParentContainer: :class:`.SBSGraph`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        # Compare Implementations
        res = self.mCompImplementation.classify(aOther.mCompImplementation, aParentContainer)

        # Last chance: compare GUI position
        if res == 0:
            GUIOffset = map(lambda x,y:x-y, self.getPosition(),aOther.getPosition())
            res = next((offset for offset in GUIOffset if offset != 0), 0)

        return res

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Parse the CompOutputs list to find a :class:`.SBSCompNode` with the given uid

        :param aUID: UID to check
        :type aUID: str
        :return: True if this uid is already used, False otherwise
        """
        return self.getCompOutput(aCompOutputUID = aUID) is not None

    @handle_exceptions()
    def getDisplayName(self):
        """
        getDisplayName()
        Get the display name of this node

        :return: the display name as a string
        """
        impl = self.getCompImplementation()
        return self.mUID if impl is None else impl.getDisplayName()+' ('+self.mUID+')'

    @handle_exceptions()
    def getCompOutput(self, aCompOutputUID = None):
        """
        getCompOutput(aCompOutputUID = None)
        Get the output with the given uid.
        If aCompOutputUID is None, get the type of the first output, if it exists

        :param aCompOutputUID: UID of the output. If None, the first output is returned
        :type aCompOutputUID: str, optional
        :return: a :class:`.SBSCompOutput` object if found, None otherwise
        """
        if not self.mCompOutputs:
            return None

        if aCompOutputUID is None:
            return self.mCompOutputs[0]

        return next((aOutput for aOutput in self.mCompOutputs if aCompOutputUID == aOutput.mUID), None)

    @handle_exceptions()
    def getCompOutputFromIdentifier(self, aOutputIdentifier = None):
        """
        getCompOutputFromIdentifier(aOutputIdentifier = None)
        Get the output with the given identifier.
        If aOutputIdentifier is None, get the first output, if it exists

        :param aOutputIdentifier: identifier of the output. If None, the first output is returned
        :type aOutputIdentifier: str, optional
        :return: A :class:`.SBSCompOutput` object if found, None otherwise
        """
        if aOutputIdentifier is None:
            return self.mCompOutputs[0] if self.mCompOutputs else None

        nodeDef = self.getDefinition()
        nodeDefOutput = nodeDef.getOutput(aOutputIdentifier)
        if nodeDefOutput is None:
            return None

        if self.isAFilter() or self.isAnInputBridge():
            return self.mCompOutputs[0] if self.mCompOutputs else None
        elif self.isAnInstance():
            outputBridge = self.getCompInstance().getCompOutputBridging(aIdentifier=aOutputIdentifier)
            return self.getCompOutput(outputBridge.mUID) if outputBridge else None
        return None

    @handle_exceptions()
    def getCompOutputIdentifier(self, aCompOutputUID = None):
        """
        getCompOutputIdentifier(aCompOutputUID = None)
        Get the identifier of the output with the given uid.
        If aCompOutputUID is None, get the identifier of the first output, if it exists

        :param aCompOutputUID: UID of the output. If None, the identifier of the first output is returned
        :type aCompOutputUID: str, optional
        :return: The identifier of the given output if found, None otherwise
        """
        aCompOutput = self.getCompOutput(aCompOutputUID)
        if aCompOutput is None:
            return None
        if self.isAFilter() or self.isAnInputBridge():
            nodeDef = self.getDefinition()
            return nodeDef.getAllOutputs()[0].getIdentifierStr() if nodeDef.getAllOutputs() else None
        elif self.isAnInstance():
            outputBridge = self.getCompInstance().getCompOutputBridgingFromUID(aCompOutputUID)
            return outputBridge.mIdentifier if outputBridge else None
        return None

    @handle_exceptions()
    def getCompOutputType(self, aCompOutputUID = None):
        """
        getCompOutputType(aCompOutputUID = None)
        Get the type of the output with the given uid.
        If aCompOutputUID is None, get the type of the first output, if it exists

        :param aCompOutputUID: UID of the output. If None, the type of the first output is returned
        :type aCompOutputUID: str, optional
        :return: The type of the given output if found as a :class:`.ParamTypeEnum`, None otherwise
        """
        aCompOutput = self.getCompOutput(aCompOutputUID)
        return int(aCompOutput.mCompType) if aCompOutput is not None else None

    @handle_exceptions()
    def getCompOutputFromBridge(self, aOutputBridge):
        """
        getCompOutputFromBridge(aOutputBridge)
        Get the output corresponding to the given bridge identifier. This can work only on an instance node.

        :param aOutputBridge: identifier of the output bridge.
        :type aOutputBridge: str
        :return: a :class:`.SBSCompOutput` object if found, None otherwise
        """
        if not self.mCompOutputs or not self.isAnInstance():
            return None

        aOutputBridge = self.mCompImplementation.mCompInstance.getCompOutputBridging(aOutputBridge)
        return self.getCompOutput(aOutputBridge.mUID) if aOutputBridge is not None else None


    @handle_exceptions()
    def getFxMapGraph(self):
        """
        getFxMapGraph()
        Get the :class:`.SBSParamsGraph` object which defines the FxMap graph

        :return: For a FxMap filter, returns the graph of this FxMap as a :class:`.SBSParamsGraph`, None otherwise.
        """
        if self.isAFxMap() and self.mCompImplementation.mCompFilter.mParamGraphs:
            return self.mCompImplementation.mCompFilter.mParamGraphs[0]
        return None

    @handle_exceptions()
    def getFxMapGraphNode(self, aUID):
        """
        getFxMapGraphNode(aUID)
        For a FxMap filter, browse the graph of this FxMap and get the :class:`.SBSParamsGraphNode` with the given UID

        :return: A :class:`.SBSParamsGraphNode` object with the given UID if found, None otherwise.
        """
        aFxMapGraph = self.getFxMapGraph()
        if aFxMapGraph is not None:
            return next((aNode for aNode in aFxMapGraph.mParamsGraphNodes if aNode.mUID == aUID), None)
        return None

    @handle_exceptions()
    def getPixProcFunction(self, createIfEmtpy=True):
        """
        getPixProcFunction()
        Get the :class:`.SBSDynamicValue` object which corresponds to the Pixel Processor Function.
        Create the dynamic value if it is None.

        :param createIfEmtpy: If True it creates an empty pixel processor graph if there is none attached already
                              If False and no pixel processor exists it will return None
        :type createIfEmtpy: bool
        :return: For a PixelProcessor filter, returns the function of this PixelProcessor, None otherwise.
        """
        if not self.isAPixelProcessor():
            return None

        aFilter = self.mCompImplementation.mCompFilter
        aDynValue = aFilter.getParameterValue(sbsenum.CompNodeParamEnum.PER_PIXEL)
        if isinstance(aDynValue, params.SBSDynamicValue):
            return aDynValue
        elif createIfEmtpy:
            return aFilter.setDynamicParameter(sbsenum.CompNodeParamEnum.PER_PIXEL)
        else:
            return None

    @handle_exceptions()
    def getValProcFunction(self, createIfEmtpy=True):
        """
        getValProcFunction(createIfEmtpy=True)
        Get the :class:`.SBSDynamicValue` object which corresponds to the Value Processor Function.
        Create the dynamic value if it is None.

        :param createIfEmtpy: If True it creates an empty value processor graph if there is none attached already
                              If False and no value processor exists it will return None
        :type createIfEmtpy: bool
        :return: For a ValueProcessor filter, returns the function of this ValueProcessor, None otherwise.
        """
        if not self.isAValueProcessor():
            return None

        aFilter = self.mCompImplementation.mCompFilter
        aDynValue = aFilter.getParameterValue(sbsenum.CompNodeParamEnum.FUNCTION)
        if isinstance(aDynValue, params.SBSDynamicValue):
            return aDynValue
        elif createIfEmtpy:
            aNewDynValue = params.SBSDynamicValue(aValueProcessorRef=weakref.ref(self))
            paramName = sbslibrary.getCompNodeParam(sbsenum.CompNodeParamEnum.FUNCTION)
            newParam = params.SBSParameter(paramName)
            newParam.setDynamicValue(aNewDynValue)
            aFilter.mParameters.append(newParam)
            return aNewDynValue
        else:
            return None

    @handle_exceptions()
    def initFxMapGraph(self):
        """
        initFxMapGraph()
        Init the :class:`.SBSParamsGraph` of this filter, if it is a FxMap

        :return: The FxMap graph if success, None otherwise
        """
        return self.mCompImplementation.mCompFilter.initFxMapGraph() if self.isAFxMap() else None

    @handle_exceptions()
    def isAFilter(self):
        """
        isAFilter()

        :return: True if the CompNode is a Compositing Node Filter, False otherwise.
        """
        return self.mCompImplementation.isAFilter()

    @handle_exceptions()
    def isAnInstance(self):
        """
        isAnInstance()

        :return: True if the CompNode is a Compositing Node Instance, False otherwise.
        """
        return self.mCompImplementation.isAnInstance()

    @handle_exceptions()
    def isAnInputBridge(self):
        """
        isAnInputBridge()

        :return: True if the CompNode is an Input Bridge, False otherwise.
        """
        return self.mCompImplementation.isAnInputBridge()

    @handle_exceptions()
    def isAnOutputBridge(self):
        """
        isAnOutputBridge()

        :return: True if the CompNode is an Output Bridge, False otherwise.
        """
        return self.mCompImplementation.isAnOutputBridge()

    @handle_exceptions()
    def isAPixelProcessor(self):
        """
        isAPixelProcessor()

        :return: True if the CompNode is a Compositing Node Filter of kind Pixel Processor, False otherwise.
        """
        return self.isAFilter() and self.mCompImplementation.mCompFilter.isAPixelProcessor()

    @handle_exceptions()
    def isAValueProcessor(self):
        """
        isAValueProcessor()

        :return: True if the CompNode is a Compositing Node Filter of kind Value Processor, False otherwise.
        """
        return self.isAFilter() and self.mCompImplementation.mCompFilter.isAValueProcessor()

    @handle_exceptions()
    def isAFxMap(self):
        """
        isAFxMap()

        :return: True if the CompNode is a Compositing Node Filter of kind FxMaps, False otherwise.
        """
        return self.isAFilter() and self.mCompImplementation.mCompFilter.isAFxMap()

    @handle_exceptions()
    def isAResource(self):
        """
        isAResource()

        :return: True if the CompNode uses a resource, meaning is a Compositing Node Filter of kind BITMAP or SVG, False otherwise.
        """
        return self.isAFilter() and self.mCompImplementation.mCompFilter.isAResource()

    @handle_exceptions()
    def getCompFilter(self):
        """
        getCompFilter()

        :return: the :class:`.SBSCompFilter` object if this node is a compositing filter, None otherwise.
        """
        return self.mCompImplementation.mCompFilter if self.isAFilter() else None

    @handle_exceptions()
    def getCompInstance(self):
        """
        getCompInstance()

        :return: the :class:`.SBSCompInstance` object if this node is a compositing graph instance, None otherwise.
        """
        return self.mCompImplementation.mCompInstance if self.isAnInstance() else None

    @handle_exceptions()
    def getCompInputBridge(self):
        """
        getCompInputBridge()

        :return: the :class:`.SBSCompInputBridge` object if this node is an input bridge, None otherwise.
        """
        return self.mCompImplementation.mCompInputBridge if self.isAnInputBridge() else None

    @handle_exceptions()
    def getCompOutputBridge(self):
        """
        getCompOutputBridge()

        :return: the :class:`.SBSCompOutputBridge` object if this node is an output bridge, None otherwise.
        """
        return self.mCompImplementation.mCompOutputBridge if self.isAnOutputBridge() else None

    @handle_exceptions()
    def getCompImplementation(self):
        """
        getCompImplementation(self)
        Return the appropriate comp implementation depending on the compositing node kind

        :return: A :class:`.SBSCompImplWithParams` or a :class:`.SBSCompOutputBridge`
        """
        return self.mCompImplementation.getImplementation() if self.mCompImplementation is not None else None

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the node definition (Inputs, Outputs, Parameters) accordingly to the compnode implementation

        :return: a :class:`.CompNodeDef` object if defined, None otherwise
        """
        impl = self.getCompImplementation()
        if impl is None:
            return None
        nodeDef = copy.deepcopy(impl.getDefinition())
        for aInput in nodeDef.mInputs:
            if aInput.mIsMultiInput:
                identifier = sbslibrary.getCompNodeInput(aInput.mIdentifier)
                maxSuffix = 1 if self.getConnectionOnPin(identifier) else 0

                for conn in self.getConnections():
                    if conn.mIdentifier.startswith(identifier + ':'):
                        suffix = 1 + int(conn.mIdentifier[len(identifier)+1:])
                        maxSuffix = suffix if suffix > maxSuffix else maxSuffix

                for suffix in range(1, maxSuffix+1):
                    nodeDef.mInputs.append(sbslibrary.CompNodeInput(aIdentifier=identifier+':'+str(suffix),
                                                                    aType=aInput.mType,
                                                                    aIsPrimary=False,
                                                                    aIsMultiInput=False))
        return nodeDef

    @handle_exceptions()
    def getDefinedParameters(self):
        """
        getDefinedParameters()
        Get the list of parameters defined on this node.

        :return: the list of :class:`.SBSParameter` specified on this node.
        """
        impl = self.getCompImplementation()
        return impl.mParameters if impl is not None and hasattr(impl, 'mParameters') and impl.mParameters is not None \
            else []

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
        Find a parameter with the given name in the appropriate comp node implementation, and return its value.

        :param aParameter: Parameter identifier
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: The parameter value if found, None otherwise
        """
        impl = self.getCompImplementation()
        return impl.getParameterValue(aParameter) if isinstance(impl, SBSCompImplWithParams) else None

    @handle_exceptions()
    def hasAReferenceOnDependency(self, aDependency):
        aUID = aDependency if python_helpers.isStringOrUnicode(aDependency) else aDependency.mUID

        # CompInstance => Check the dependency
        if self.isAnInstance():
            return self.getCompInstance().getDependencyUID() == aUID

        # Resource node => check the dependency
        elif self.isAResource():
            aPath = self.getCompFilter().getResourcePath()
            return api_helpers.splitPathAndDependencyUID(aPath)[1] == aUID
        return False

    @handle_exceptions()
    def hasAReferenceOnInternalPath(self, aInternalPath):
        if self.isAnInstance():
            return self.getCompInstance().getReferenceInternalPath() == aInternalPath
        elif self.isAResource():
            return self.getCompFilter().getResourcePath() == aInternalPath
        return False

    @handle_exceptions()
    def hasIdenticalParameters(self, other):
        """
        hasIdenticalParameters(self, other)
        Allows to check if two nodes has the same parameters defined with the same values.

        :param other: the node to compare with
        :type other: :class:`.SBSCompImplWithParams`
        :return: True if the two nodes has the same parameters, False otherwise
        """
        selfImpl = self.getCompImplementation()
        otherImpl = other.getCompImplementation()
        return selfImpl.hasIdenticalParameters(otherImpl) if selfImpl is not None and otherImpl is not None else False

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue, aRelativeTo = None):
        """
        setParameterValue(aParameter, aParamValue, aRelativeTo = 0)
        Set the parameter to the appropriate comp node implementation

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :param aRelativeTo: Inheritance of the parameter

        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aParamValue: any parameter type
        :type aRelativeTo: :class:`.ParamInheritanceEnum`

        :return: True if success, False otherwise
        """
        impl = self.getCompImplementation()
        if isinstance(impl, SBSCompImplWithParams):
            result = impl.setParameterValue(aParameter, aParamValue, aRelativeTo)
            if not result:
                return False
            # Update output type if changing color mode of a node
            if aParameter == sbsenum.CompNodeParamEnum.COLOR_MODE:
                definition = self.getDefinition()
                for idx, o in enumerate(definition.getAllOutputs()):
                    if o.mType == sbsenum.ParamTypeEnum.ENTRY_VARIANT:
                        compOutput = self.mCompOutputs[idx]
                        if aParamValue is sbsenum.ColorModeEnum.COLOR:
                            compOutput.mCompType = str(sbsenum.ParamTypeEnum.ENTRY_COLOR)
                        else:
                            compOutput.mCompType = str(sbsenum.ParamTypeEnum.ENTRY_GRAYSCALE)
            return result
        else:
            False

    @handle_exceptions()
    def setDynamicParameter(self, aParameter, aRelativeTo = None):
        """
        setDynamicParameter(aParameter, aRelativeTo = None)
        Set the given parameter as dynamic, to init its params.SBSDynamicValue.
        If aRelative is None, the default Inheritance will be applied

        :param aParameter: identifier of the parameter
        :param aRelativeTo: Inheritance of the parameter
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aRelativeTo: :class:`.ParamInheritanceEnum`
        :return: the :class:`.SBSDynamicValue` object if succeed, None otherwise
        """
        impl = self.getCompImplementation()
        if aParameter == sbsenum.CompNodeParamEnum.COLOR_MODE:
            log.warning('Setting COLOR_MODE to dynamic will not update output types correctly')
        return impl.setDynamicParameter(aParameter, aRelativeTo) if isinstance(impl, SBSCompImplWithParams) else None

    @handle_exceptions()
    def setCurveDefinition(self, aCurveDefinition):
        """
        setCurveDefinition(aCurveDefinition)
        If the node is a Filter Curve, set the given curve definition.

        :param aCurveDefinition: curve key values
        :type aCurveDefinition: :class:`.CurveDefinition`
        :return: True if succeed
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if not self.isAFilter():
            raise SBSImpossibleActionError('Curve keys can only be set on Filter Curve')

        aCompFilter = self.mCompImplementation.mCompFilter
        if aCompFilter.mFilter != sbslibrary.getFilterDefinition(sbsenum.FilterEnum.CURVE).mIdentifier:
            raise SBSImpossibleActionError('Curve keys can only be set on Filter Curve')

        aCurveName = sbslibrary.getCurveName(aCurveDefinition.mIdentifier)

        # If curves are already defined on the node, try to find the one that is set
        aIndex = None
        if aCompFilter.mParamArrays is not None:
            aIndex = next((i for i, aCurve in enumerate(aCompFilter.mParamArrays) if aCurve.mName == aCurveName), None)

        # Generate the new curve
        aCurve = sbsgenerator.createCurveParamsArray(aCompFilter=aCompFilter, aCurveDefinition=aCurveDefinition)

        # Create a new curve if it does not exist
        if aIndex is None:
            api_helpers.addObjectToList(aCompFilter, 'mParamArrays', aCurve)
        else:
            aCompFilter.mParamArrays[aIndex] = aCurve
        return True

    @handle_exceptions()
    def unsetParameter(self, aParameter):
        """
        unsetParameter(aParameter)
        Unset the given parameter so that it is reset to its default value.

        :param aParameter: identifier of the parameter to set
        :type aParameter: :class:`.CompNodeParamEnum` or str
        :return: True if succeed, False otherwise
        """
        impl = self.getCompImplementation()
        return impl.unsetParameter(aParameter) if isinstance(impl, SBSCompImplWithParams) else False

    @handle_exceptions()
    def setGradientMapKeyValues(self, aKeyValues):
        """
        setGradientMapKeyValues(aKeyValues)
        If the node is a Filter Gradient Map, set the given gradient map key values.

        :param aKeyValues: gradient key values
        :type aKeyValues: list of :class:`.GradientKey`
        :return: True if succeed
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if not self.isAFilter():
            raise SBSImpossibleActionError('Gradient keys can only be set on Filter Gradient Map')

        aCompFilter = self.mCompImplementation.mCompFilter
        if aCompFilter.mFilter != sbslibrary.getFilterDefinition(sbsenum.FilterEnum.GRADIENT).mIdentifier:
            raise SBSImpossibleActionError('Gradient keys can only be set on Filter Gradient Map')

        if aCompFilter.mParamArrays is not None:
            del aCompFilter.mParamArrays[:]
            aCompFilter.mParamArrays = None

        aParamsArray = sbsgenerator.createGradientMapParamsArray(aCompFilter = aCompFilter, aKeyValues = aKeyValues)
        aCompFilter.mParamArrays = [aParamsArray]
        return True

    @handle_exceptions()
    def createIterationOnPattern(self, aParameter, aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern = None, aGUIOffset = None):
        """
        createIterationOnPattern(aParameter, aNbIteration, aNodeUIDs, aNodeUIDs_NextPatternInput = None, aGUIOffset = None)
        | Allows to create an iteration in the function defining the value of the given parameter.
        | Duplicate nbIteration times the given node, to create this kind of connection:
        | Pattern -> Pattern_1 -> Pattern_2 -> ... -> Pattern_N

        :param aParameter: Parameter
        :param aNbIteration: number of time the pattern must be duplicated
        :param aNodeUIDs: list of node's UID that constitute the pattern to duplicate
        :param aNodeUIDs_NextPattern: list of node's UID that correspond to the inputs of the next pattern, which must be connected to the given pattern. Default to []
        :param aGUIOffset: pattern position offset. Default to [150, 0]

        :type aParameter: :class:`.CompNodeParamEnum` or str
        :type aNbIteration: positive integer
        :type aNodeUIDs: list of str
        :type aNodeUIDs_NextPattern: list of str, optional
        :type aGUIOffset: list of 2 float, optional

        :return: The list of params.SBSParamNode created
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if aGUIOffset is None: aGUIOffset = [150,0]

        aParamDynValue = self.getParameterValue(aParameter)
        if not isinstance(aParamDynValue, params.SBSDynamicValue):
            raise SBSImpossibleActionError('Parameter '+aParameter+' must be dynamic to be able to create an iteration')

        return aParamDynValue.createIterationOnPattern(aNbIteration, aNodeUIDs, aNodeUIDs_NextPattern, aGUIOffset)

    @handle_exceptions()
    def _computeUniqueIdentifier(self, aIdentifier, aListsToCheck, aSuffixId=0):
        """
        _computeUniqueIdentifier(aIdentifier, aListsToCheck, aSuffixId=0)
        Parse the lists of object to find an object with the given identifier, and compute a unique identifier if it is not unique.

        :param aIdentifier:
        :param aListsToCheck: The list of lists of SBSObject that must be taken in account to ensure identifier uniqueness
        :type aIdentifier: str
        :type aListsToCheck: list of lists of :class:`.SBSObject`
        :return: A unique identifier in the context of the given lists. It can be the given aIdentifier, or aIdentifier_Suffix
        """
        if aSuffixId == 0:
            match = re.search(r'_[0-9]+$', aIdentifier)
            if match:
                aSuffix = aIdentifier[match.start():]
                aSuffixId = int(aSuffix[1:])
                aIdentifier = aIdentifier[0:match.start()]
            else:
                aSuffix = ''
        else:
            aSuffix = '_' + str(aSuffixId)
        aIdentifierToCheck = aIdentifier + aSuffix

        for aList, aObject in [(aList, aObject) for aList in aListsToCheck if aList is not None for aObject in aList]:
            if python_helpers.isStringOrUnicode(aObject):
                if aObject == aIdentifierToCheck:
                    return self._computeUniqueIdentifier(aIdentifier, aListsToCheck, aSuffixId + 1)
            elif aObject.mIdentifier == aIdentifierToCheck:
                return self._computeUniqueIdentifier(aIdentifier, aListsToCheck, aSuffixId + 1)
        return aIdentifierToCheck

    @handle_exceptions()
    def computeUniqueInputValueIdentifier(self, aIdentifier):
        """
        computeUniqueInputValueIdentifier(aIdentifier)
        Check if the given identifier is already used in the node inputs and generate a unique identifier if necessary

        :return: A unique identifier
        """
        return self._computeUniqueIdentifier(aIdentifier, aListsToCheck= [self.mInputValues])

    @handle_exceptions()
    def createInputValue(self, aIdentifier, aType):
        """
        Create a new Input Value attached to the node. :class:`.SBSCompInputValue`

        :param aIdentifier: an unique identifier name, if aIdentifier already exist in the current input values identifiers
        a suffix will be added. The identifier must start by # it will added if it's not present.
        :type aIdentifier: str
        :param aType: the input value type (only boolean and numerical) presents in :class:`.InputValueTypeEnum`
        :type aType: :class:`.InputValueTypeEnum`
        """
        aIdentifier = "#" + aIdentifier if not aIdentifier.startswith("#") else aIdentifier
        uniqueId = self.computeUniqueInputValueIdentifier(api_helpers.formatIdentifier(aIdentifier))
        if aType not in [v for k, v in sbsenum.InputValueTypeEnum.__dict__.items()]:
            raise TypeError("aType must be a sbsenum.InputValueTypeEnum value, given ", type(aType))
        if isinstance(self.mInputValues, list):
            self.mInputValues.append(SBSCompInputValue(aIdentifier=uniqueId, aType=str(aType)))
        else:
            self.mInputValues = [SBSCompInputValue(aIdentifier=uniqueId, aType=str(aType))]

    @handle_exceptions()
    def getInputValue(self, aIdentifier):
        """
        return corresponding InputValue aIdentifier, :class:`.SBSCompInputValue`
        :param aIdentifier: identifier name must start by # it will added if it's not present.
        :type aIdentifier: str
        :return:
        """
        aIdentifier = "#" + aIdentifier if not aIdentifier.startswith("#") else aIdentifier
        return next((aInput for aInput in self.mInputValues if aInput.mIdentifier == aIdentifier), None)

