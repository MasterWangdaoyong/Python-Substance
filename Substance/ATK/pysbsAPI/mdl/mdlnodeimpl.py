# coding: utf-8
"""
Module **mdlnodeimpl** provides the definition of the class :class:`.MDLImplementation`: and all the possible implementations of a :class:`.MDLNode`:

- :class:`.MDLImplConstant`
- :class:`.MDLImplSelector`
- :class:`.MDLImplMDLInstance`
- :class:`.MDLImplMDLGraphInstance`
- :class:`.MDLImplSBSInstance`
"""

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import copy
import weakref

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSLibraryError, SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject, UIDGenerator
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum

from . import mdlenum, mdldictionaries, mdl_helpers
from . import MDLOperandValue, MDLAnnotation, MDLParameter, MDLInputBridging, MDLOutputBridging
from .mdlmanager import MDLManager
from . import mdllibclasses, mdlsbsbridge
from .mdlcommon import MDLObjectWithAnnotations, MDLNodeImpl, MDLImplWithOperands



# =======================================================================
@doc_inherit
class MDLImplConstant(MDLImplWithOperands, MDLObjectWithAnnotations):
    """
    Class that contains information on a MDL constant node as defined in a .sbs file

    Members:
        * mOperands     (list of :class:`.MDLOperands`): list of parameters available on this node
        * mIsExposed    (str, optional): boolean indicating if the node is exposed as an input parameter. Default to '0'
        * mTypeModifier (str, optional): enum or bitfield that indicates the type modifier(s) (varying, uniform, const, ...) of the constant. Default to no modifier ('auto')
        * mAnnotations  (list of :class:`.MDLAnnotation`, optional): if this constant is exposed, defines the MDL annotations associated to this input.
    """

    __sAnnotations = [mdlenum.MDLAnnotationEnum.DESCRIPTION,
                      mdlenum.MDLAnnotationEnum.DISPLAY_NAME,
                      mdlenum.MDLAnnotationEnum.GAMMA_TYPE,
                      mdlenum.MDLAnnotationEnum.HARD_RANGE,
                      mdlenum.MDLAnnotationEnum.HIDDEN,
                      mdlenum.MDLAnnotationEnum.IN_GROUP,
                      mdlenum.MDLAnnotationEnum.KEYWORDS,
                      mdlenum.MDLAnnotationEnum.SAMPLER_USAGE,
                      mdlenum.MDLAnnotationEnum.SOFT_RANGE,
                      mdlenum.MDLAnnotationEnum.VISIBLE_BY_DEFAULT]

    def __init__(self,
                 aOperands     = None,
                 aIsExposed    = None,
                 aTypeModifier = None,
                 aAnnotations  = None,
                 aIdentifier   = ''):
        MDLImplWithOperands.__init__(self, aOperands)
        MDLObjectWithAnnotations.__init__(self, aAllowedAnnotations=MDLImplConstant.__sAnnotations, aAnnotations=aAnnotations)

        self.mIsExposed    = aIsExposed
        self.mTypeModifier = aTypeModifier
        self.mIdentifier = aIdentifier

        self.mMembersForEquality = ['mOperands',
                                    'mIsExposed',
                                    'mTypeModifier',
                                    'mIdentifier']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(MDLImplConstant, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mIsExposed    = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'is_exposed'     )
        self.mTypeModifier = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'type_modifier'  )
        self.mAnnotations  = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'mdl_annotations', 'mdl_annotation', MDLAnnotation)
        self.mIdentifier = self.getIdentifier()

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeSBSNode(aXmlNode                 , self.mOperands    , 'mdl_operands'   )
        if self.mIsExposed:
            aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIsExposed   , 'is_exposed'     )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode    , self.mTypeModifier, 'type_modifier'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode           , self.mAnnotations , 'mdl_annotations', 'mdl_annotation'  )

    @handle_exceptions()
    def classify(self, aOther):
        selfValue = self.mIdentifier
        otherValue = aOther.mIdentifier
        return (selfValue > otherValue) - (selfValue < otherValue)

    @handle_exceptions()
    def getDefinition(self):
        if not self.mOperands:
            return mdllibclasses.MDLNodeDef()
        paramDef = mdllibclasses.MDLNodeDefParam()
        paramDef.fromMDLOperand(self.mOperands.getOperandByIndex(0))

        annotationDefs = []
        for annot in self.mAnnotations:
            annotDef = mdllibclasses.MDLAnnotationDef()
            annotDef.fromMDLAnnotation(annot)
            annotationDefs.append(annotDef)

        outputDefs = [mdllibclasses.MDLNodeDefOutput(aType=paramDef.mType)]
        inputDefs = []
        if self.isExposed():
            inputDefs.append(mdllibclasses.MDLNodeDefInput(aIdentifier=paramDef.mName,aType=paramDef.mType))
        nodeDefinition = mdllibclasses.MDLNodeDef(aPath=paramDef.getType(),
                                                  aParameters=[paramDef],
                                                  aAnnotations=annotationDefs,
                                                  aInputs=inputDefs,
                                                  aOutputs=outputDefs)
        return nodeDefinition

    @handle_exceptions()
    def getDisplayName(self):
        annotName = self.getAnnotationValue(mdlenum.MDLAnnotationEnum.DISPLAY_NAME)
        return annotName if annotName else self.getIdentifier()

    @handle_exceptions()
    def getConstantOperand(self):
        """
        getConstantOperand()
        Get the operand corresponding to the constant represented by this node

        :return: The operand as a :class:`.MDLOperand` object if defined, None otherwise
        """
        return self.mOperands.getOperandByIndex(0) if self.mOperands else None

    @handle_exceptions()
    def getIdentifier(self):
        """
        getIdentifier()
        Get the identifier of this constant node

        :return: The identifier as a string
        """
        aOperand = self.getConstantOperand()
        return aOperand.mName if aOperand else ''

    @handle_exceptions()
    def getOutputType(self, aOutputIdentifier=None):
        """
        getOutputType(aOutputIdentifier=None)
        Get the output type of this node.

        :return: The node output type as a string if defined, None otherwise
        """
        aOperand = self.getConstantOperand()
        return aOperand.mType if aOperand else aOperand

    def getParameter(self, aParameter = None):
        return super(MDLImplConstant, self).getParameter(self.getIdentifier() if aParameter is None else aParameter)

    def getParameterValue(self, aParameter = None):
        return super(MDLImplConstant, self).getParameterValue(self.getIdentifier() if aParameter is None else aParameter)

    @handle_exceptions()
    def isAnInput(self):
        """
        isAnInput()
        Check if this node is exposed as an input parameter in its parent graph

        :return: True if this is an input, False otherwise
        """
        return self.isExposed()

    @handle_exceptions()
    def isAnInputImage(self):
        """
        isAnInputImage()
        Check if this node is an exposed input parameter of kind image (e.g. texture_2d)

        :return: True if this is an input image, False otherwise
        """
        aOperand = self.getConstantOperand()
        return aOperand.mType == 'mdl::texture_2d' if aOperand else False

    @handle_exceptions()
    def isAnInputParameter(self):
        """
        isAnInputParameter()
        Check if this node is an exposed input parameter which is not an image (e.g. texture_2d)

        :return: True if this is an input parameter, False otherwise
        """
        return not self.isAnInputImage()

    @handle_exceptions()
    def isExposed(self):
        """
        isExposed()
        Check if this node is exposed as an input parameter in its parent graph

        :return: True if this is an input, False otherwise
        """
        return self.mIsExposed is not None and \
               api_helpers.getTypedValueFromStr(self.mIsExposed, sbsenum.ParamTypeEnum.BOOLEAN)

    @handle_exceptions()
    def isVisibleByDefault(self):
        """
        isVisibleByDefault()
        Get the 'visible_by_default' annotation value.
        If None, consider the default visible state as True

        :return: True if the constant is visible by default, False otherwise
        """
        annotValue = self.getAnnotationValue(mdlenum.MDLAnnotationEnum.VISIBLE_BY_DEFAULT)
        if annotValue:
            return api_helpers.getTypedValueFromStr(annotValue, sbsenum.ParamTypeEnum.BOOLEAN)
        else:
            return True

    @handle_exceptions()
    def setExposed(self, aExposed):
        """
        setExposed(aExposed)
        Set the 'mIsExposed' member of this constant to the given value.

        :param aExposed: True to set this constant as exposed
        :type aExposed: bool
        """
        self.mIsExposed = api_helpers.formatValueForTypeStr(aExposed, sbsenum.ParamTypeEnum.BOOLEAN) if aExposed else None
        aOperand = self.getConstantOperand()
        if aOperand:
            aOperand.setConnectionAccepted(aExposed)

    def resetParameter(self, aParameter = None):
        if aParameter is None:
            aParameter = self.getIdentifier()
        super(MDLImplConstant, self).resetParameter(aParameter)

    @handle_exceptions()
    def setIdentifier(self, aIdentifier):
        """
        setIdentifier(aIdentifier)
        Set the constant identifier

        :param aIdentifier: The identifier to set
        :type aIdentifier: str
        """
        aOperand = self.getConstantOperand()
        if aOperand:
            aOperand.mName = aIdentifier
        self.mIdentifier = aIdentifier


# =======================================================================
@doc_inherit
class MDLImplPassThrough(MDLNodeImpl):

    __DEFINITION = mdllibclasses.MDLNodeDef(
        aInputs=[
            mdllibclasses.MDLNodeDefInput()
        ],
        aOutputs=[
            mdllibclasses.MDLNodeDefOutput()
        ],
        aIsPassthrough=True
    )

    """
    Class that contains information on a MDL passthrough (dot) node as defined in a .sbs file
    """
    def __init__(self):
        super(MDLImplPassThrough, self).__init__()
        self.mMembersForEquality = []

    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        pass

    def write(self, aSBSWriter, aXmlNode):
        pass

    def classify(self, _):
        return True

    def getDisplayName(self):
        return 'Dot'

    def getDefinition(self):
        return MDLImplPassThrough.__DEFINITION

    def getOutputType(self, aOutputIdentifier=None):
        return None

    def getParameter(self, aParameter=None):
        return None

    def getParameterValue(self, aParameter=None):
        return None

    def setParameterValue(self, aParameter, aParamValue):
        return False

    def resetParameter(self, aParameter):
        return False

# =======================================================================
@doc_inherit
class MDLImplSelector(MDLNodeImpl):
    """
    Class that contains information on a MDL selector node as defined in a .sbs file

    Members:
        * mStructType (string): The struct's MDL path from which we want to extract a member. It should match the type of what is connected to the unique input of this node.
        * mName       (string): The selected member name.
        * mType       (string): The selected member type (its MDL path).
    """
    def __init__(self,
                 aStructType = '',
                 aName       = '',
                 aType       = ''):
        super(MDLImplSelector, self).__init__()
        self.mStructType = aStructType
        self.mName       = aName
        self.mType       = aType

        self.mMembersForEquality = ['mStructType',
                                    'mName',
                                    'mType']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mStructType = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'struct_type' )
        self.mName       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name'        )
        self.mType       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'type'        )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mStructType , 'struct_type' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName       , 'name'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType       , 'type'        )

    @handle_exceptions()
    def classify(self, aOther):
        selfValue = self.mStructType+'.'+self.mName
        otherValue = aOther.mStructType+'.'+aOther.mName
        return (selfValue > otherValue) - (selfValue < otherValue)

    @handle_exceptions()
    def getDefinition(self):
        paramDef = mdllibclasses.MDLNodeDefParam()
        paramDef.mName = 'member'
        paramDef.mType = mdllibclasses.MDLNodeDefType(aName='string',
                                                      aPath=mdldictionaries.getMDLPredefTypePath(mdlenum.MDLPredefTypes.STRING))

        inputDefType = mdllibclasses.MDLNodeDefType(aName=mdl_helpers.getModuleName(self.mStructType),
                                                    aPath=self.mStructType,
                                                    aModifier='auto')
        inputDef = mdllibclasses.MDLNodeDefInput(aType=inputDefType)

        outputType = self.getOutputType()
        outputDefType = mdllibclasses.MDLNodeDefType(aName=mdl_helpers.getModuleName(outputType),
                                                     aPath=outputType,
                                                     aModifier='auto')
        outputDef = mdllibclasses.MDLNodeDefOutput(aType=outputDefType)

        nodeDefinition = mdllibclasses.MDLNodeDef(aPath=paramDef.getType(),
                                                  aParameters=[paramDef],
                                                  aInputs=[inputDef],
                                                  aOutputs=[outputDef])
        return nodeDefinition

    @handle_exceptions()
    def getDisplayName(self):
        return 'Selector ' + self.mName

    def getMemberList(self):
        """
        getMemberList()
        Get the list of available members and their types for this Selector

        :return: a list of tuple(member name(str), member type(str))
        """
        if self.mStructType is None:
            return []

        aTypeDef = MDLManager.getMDLTypeDefinition(self.mStructType)
        if not aTypeDef.isStruct() or not aTypeDef.mStructMembers:
            return []

        return [(m.mName,m.mType) for m in aTypeDef.mStructMembers]

    @handle_exceptions()
    def getOutputType(self, aOutputIdentifier=None):
        """
        getOutputType(aOutputIdentifier=None)
        Get the output type of this node.

        :return: The node output type as a string
        """
        return self.mType

    def getParameter(self, aParameter=None):
        return MDLOperandValue(aName='member', aType=self.mType, aValue=self.mName)

    def getParameterValue(self, aParameter=None):
        return self.mName

    def resetParameter(self, aParameter = None):
        self.mName = ''
        self.mType = ''

    def setParameterValue(self, aParameter, aParamValue):
        members = self.getMemberList()
        if not members:
            raise SBSImpossibleActionError('Cannot set the selected a member, there is no members available for selection')

        member = next((m for m in members if m[0] == aParamValue), None)
        if member is None:
            raise SBSImpossibleActionError('No member named '+python_helpers.castStr(aParamValue)+' available for selection in this Selector')

        self.mName, self.mType = member


# =======================================================================
@doc_inherit
class MDLImplMDLInstance(MDLImplWithOperands):
    """
    Class that contains information on a MDL native function or material node implementation as defined in a .sbs file

    Members:
        * mPath     (string): path of the graph definition this instance refers to.
        * mOperands (list of :class:`.MDLOperands`, optional): list of parameters available on this node
    """
    def __init__(self,
                 aPath            = '',
                 aOperands        = None):
        super(MDLImplMDLInstance, self).__init__(aOperands)
        self.mPath = aPath
        self.__resolved = False

        self.mMembersForEquality = ['mPath',
                                    'mOperands']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(MDLImplMDLInstance, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mPath = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'mdl_path')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mPath, 'mdl_path'     )
        aSBSWriter.writeSBSNode(aXmlNode, self.mOperands,          'mdl_operands' )

    def __resolvePath(self):
        if not self.__resolved:
            self.mPath = MDLManager.resolveVersionnedFunctionPath(self.mPath)
            self.__resolved = True

    @handle_exceptions()
    def classify(self, aOther):
        self.__resolvePath()
        selfValue = self.mPath
        otherValue = aOther.mPath
        return (selfValue > otherValue) - (selfValue < otherValue)

    @handle_exceptions()
    def getDefinition(self):
        self.__resolvePath()
        nodeDef = copy.deepcopy(MDLManager.getMDLNodeDefinition(self.mPath))
        for aOperand in self.getOperands():
            aInput = nodeDef.getInput(aOperand.mName)
            if aInput and not aOperand.acceptConnection():
                nodeDef.mInputs.remove(aInput)

        return nodeDef

    @handle_exceptions()
    def getDisplayName(self):
        self.__resolvePath()
        return 'MDL node '+ self.mPath

    @handle_exceptions()
    def getOutputType(self, aOutputIdentifier=None):
        """
        getOutputType(aOutputIdentifier=None)
        Get the output type of this node.

        :return: The node output type as a string
        """
        mdlDef = self.getDefinition()
        if mdlDef and mdlDef.mOutputs:
            return mdlDef.mOutputs[0].getType()
        return None

    @handle_exceptions()
    def isAnInstanceOf(self, aPath):
        """
        isAnInstanceOf(aPath)
        Get the absolute path of the graph referenced by this instance.

        :param aPath: The path to look for, with a complete signature ('mdl::material_surface(bsdf,material_emission)') or a simple path ('mdl::material_surface')
        :type aPath: str
        :return: The absolute path of the graph referenced by this instance, in the format absolutePath/filename.sbs/graphIdentifier, as a string
        """
        self.__resolvePath()
        if mdl_helpers.pathHasSignature(aPath):
            return self.mPath == aPath
        else:
            return mdl_helpers.removePathSignature(self.mPath) == aPath



# =======================================================================
@doc_inherit
class MDLImplMDLGraphInstance(MDLImplWithOperands):
    """
    Class that contains information on a MDL graph instance implementation as defined in a .sbs file

    Members:
        * mPath     (string): path of the graph definition this instance refers to.
        * mOperands (list of :class:`.MDLOperands`, optional): list of parameters available on this node
    """
    def __init__(self,
                 aPath          = '',
                 aOperands      = None,
                 aRefGraph      = None,
                 aRefDependency = None):
        super(MDLImplMDLGraphInstance, self).__init__(aOperands)
        self.mPath          = aPath
        self.mRefGraph      = weakref.ref(aRefGraph) if aRefGraph is not None else None
        self.mRefDependency = weakref.ref(aRefDependency) if aRefDependency is not None else None

        self.mMembersForEquality = ['mPath',
                                    'mOperands']

    def __deepcopy__(self, memo):
        """
        Overrides deepcopy to ensure that mRefGraph and mRefDependency are kept as a reference

        :return: A clone of itself
        """
        clone = MDLImplMDLGraphInstance()
        memo[id(self)] = clone
        clone.mPath      = copy.deepcopy(self.mPath, memo)
        clone.mOperands  = copy.deepcopy(self.mOperands, memo)
        clone.mRefGraph  = self.mRefGraph
        clone.mRefDependency = self.mRefDependency
        return clone

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(MDLImplMDLGraphInstance, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mPath = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'path' )

        aContext.addSBSObjectToResolve(self)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mPath, 'path' )
        aSBSWriter.writeSBSNode(aXmlNode, self.mOperands , 'mdl_operands' )

    @handle_exceptions()
    def classify(self, aOther):
        selfValue = self.mPath
        otherValue = aOther.mPath
        return (selfValue > otherValue) - (selfValue < otherValue)

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

    @handle_exceptions()
    def changeInstancePath(self, aParentDocument, aInstanceDocument, aGraphRelPath):
        """
        changeInstancePath(aParentDocument, aInstanceDocument, aGraphRelPath)
        Change the MDL graph referenced by this instance.
        If aInstanceDocument is not already declared as a dependency, the dependency will be added to aParentDocument.

        :param aParentDocument: The parent document of this node
        :type aParentDocument: :class:`.SBSDocument`
        :param aInstanceDocument: The document containing the MDL graph to reference by this instance (can be equal to parent document)
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
        Allow to resolve the dependency of the MDL graph instance node with the graph it references.

        :param aSBSDocument: The root document
        :type aSBSDocument: :class:`.SBSDocument`
        """
        if not self.mPath or not api_helpers.hasPkgPrefix(self.mPath):
            return False

        aPath = api_helpers.removePkgPrefix(self.mPath)
        aGraphRelPath, aDepUID = api_helpers.splitPathAndDependencyUID(aPath)

        # if the tag ?dependency= is not present, take the first dependency of the document
        if aDepUID is None:
            try:
                aDepUID = aSBSDocument.getDependencyContainingInternalPath(self.mPath).mUID
            except:
                log.error('MDL Graph %s not found' % aPath)
                return False

        try:
            aDep = aSBSDocument.getDependency(aUID = aDepUID)
            self.mRefDependency = weakref.ref(aDep)
            aPackageWR = aDep.getRefPackage()
            try:
                aGraph = aPackageWR().getObjectFromInternalPath(aGraphRelPath)
                self.mRefGraph = weakref.ref(aGraph)
            except:
                log.error('MDL Graph %s/%s not found', aDep.mFilename, aGraphRelPath)
        except:
            log.error('Dependency %s not found, cannot resolve: %s', aDepUID, aPath)

        return self.mRefGraph is not None

    @handle_exceptions()
    def getDefinition(self):
        inputDefs = []
        outputDef = None
        parameterDefs = []
        if not self.mRefGraph():
            for aOperand in self.getOperands():
                inputDef = mdllibclasses.MDLNodeDefInput()
                inputDef.fromMDLOperand(aOperand)
                inputDefs.append(inputDef)

                paramDef = mdllibclasses.MDLNodeDefParam()
                paramDef.fromMDLOperand(aOperand)
                parameterDefs.append(paramDef)

        else:
            for aInputNode in self.mRefGraph().getAllInputs():
                cstImpl = aInputNode.getMDLImplConstant()
                if cstImpl:
                    aOperand = cstImpl.getConstantOperand()
                    nodeOperand = self.getParameter(cstImpl.mIdentifier)
                    if aOperand:
                        # Create an input
                        if cstImpl.isVisibleByDefault() or (nodeOperand and nodeOperand.acceptConnection()):
                            inputDef = mdllibclasses.MDLNodeDefInput()
                            inputDef.fromMDLOperand(aOperand)
                            inputDefs.append(inputDef)

                        # Create a parameter
                        paramDef = mdllibclasses.MDLNodeDefParam()
                        paramDef.fromMDLOperand(aOperand, copyValue = True)
                        parameterDefs.append(paramDef)

            if self.mRefGraph().getGraphOutput():
                outputType = self.mRefGraph().getGraphOutputType()
                outputDefType = mdllibclasses.MDLNodeDefType(aName=mdl_helpers.getModuleName(outputType),
                                                             aPath=outputType,
                                                             aModifier='auto')
                outputDef = mdllibclasses.MDLNodeDefOutput(aType=outputDefType)

        nodeDefinition = mdllibclasses.MDLNodeDef(aPath=self.mPath,
                                                  aInputs=inputDefs,
                                                  aParameters=parameterDefs,
                                                  aOutputs=[outputDef] if outputDef else [])
        return nodeDefinition

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
        return 'Instance of MDL graph: '+ self.mPath

    @handle_exceptions()
    def getOutputType(self, aOutputIdentifier=None):
        """
        getOutputType(aOutputIdentifier=None)
        Get the output type of this node.

        :return: The node output type as a string if it exists, None otherwise
        """
        return self.mRefGraph().getGraphOutputType() if self.mRefGraph() else None

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
        pos = aPath.find('?dependency=')
        aPath = aPath[0:pos].replace('\\', '/')
        aDepAbsPath = self.mRefDependency().mFileAbsPath.replace('\\', '/')
        aPath = aDepAbsPath + '/' + aPath
        return aPath

    @handle_exceptions()
    def getReferenceInternalPath(self):
        """
        getReferenceInternalPath()
        Get the path of the referenced graph relatively to the package (pkg:///).

        :return: The path as a string
        """
        return self.mPath



# =======================================================================
@doc_inherit
class MDLImplSBSInstance(MDLNodeImpl):
    """
    Class that contains information on a Substance graph instance implementation as defined in a .sbs file

    Members:
        * mPath              (string): package's url to the referenced graph
        * mParameters        (list of :class:`.MDLParameter`): list of custom parameters used for the integration of Substance Graph in MDL.
        * mSBSParameters     (list of :class:`.MDLParameter`): parameters holding the values of the Graph's input tweaks. See SBSGraph.mParamInputs.
        * mSBSBaseParameters (list of :class:`.MDLParameter`): parameters that are common to all Substance Graphs. See SBSGraph.mBaseParameters.
        * mInputBridgings    (list of :class:`.MDLInputBridging`): list of input bridgings of this SBS graph instance
        * mOutputBridgings   (list of :class:`.MDLOutputBridging`): list of output bridgings of this SBS graph instance
    """
    def __init__(self,
                 aPath              = '',
                 aRefGraph          = None,
                 aRefDependency     = None):
        super(MDLImplSBSInstance, self).__init__()
        self.mPath              = aPath
        self.mSBSParameters = []
        self.mSBSBaseParameters = []
        self.mOutputBridgings = []
        self.mInputBridgings = []

        self.mRefGraph      = weakref.ref(aRefGraph) if aRefGraph is not None else None
        self.mRefDependency = weakref.ref(aRefDependency) if aRefDependency is not None else None

        # Init graph base parameters
        self.mSBSBaseParameters = self.__getDefaultBaseParameters()

        # Init graph common parameters
        self.mParameters = self.__getDefaultCommonParameters()

        # Init data from the referenced graph (inputs, outputs, parameters)
        self.__getInfoFromReferencedGraph()

        self.mMembersForEquality = ['mPath',
                                    'mParameters',
                                    'mSBSParameters',
                                    'mSBSBaseParameters',
                                    'mInputBridgings',
                                    'mOutputBridgings']

    def __deepcopy__(self, memo):
        """
        Overrides deepcopy to ensure that mRefGraph and mRefDependency are kept as a reference

        :return: A clone of itself
        """
        clone = MDLImplSBSInstance()
        memo[id(self)] = clone
        clone.mPath      = copy.deepcopy(self.mPath, memo)
        clone.mParameters        = copy.deepcopy(self.mParameters       , memo)
        clone.mSBSParameters     = copy.deepcopy(self.mSBSParameters    , memo)
        clone.mSBSBaseParameters = copy.deepcopy(self.mSBSBaseParameters, memo)
        clone.mInputBridgings    = copy.deepcopy(self.mInputBridgings   , memo)
        clone.mOutputBridgings   = copy.deepcopy(self.mOutputBridgings  , memo)
        clone.mRefGraph  = self.mRefGraph
        clone.mRefDependency  = self.mRefDependency
        return clone

    @handle_exceptions()
    def getUidIsUsed(self, aUID):
        """
        getUidIsUsed(aUID)
        Check if the given uid is already used in the context of this MDL node

        return: True if the uid is already used, False otherwise
        """
        for aInput in self.mInputBridgings:
            if aInput.mLocalIdentifier == '$'+aUID:
                return True
        for aOutput in self.mOutputBridgings:
            if aOutput.mUID == aUID:
                return True
        return False

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mPath = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'path' )
        self.mParameters        = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'parameters'           , 'parameter',       MDLParameter)
        self.mSBSBaseParameters = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'sbs_common_parameters', 'parameter',       MDLParameter)
        self.mSBSParameters     = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'sbs_parameters'       , 'parameter',       MDLParameter)
        self.mInputBridgings    = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'input_bridgings'      , 'input_bridging' , MDLInputBridging)
        self.mOutputBridgings   = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'output_bridgings'     , 'output_bridging', MDLOutputBridging)

        aContext.addSBSObjectToResolve(self)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mPath, 'path' )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mParameters       , 'parameters'            , 'parameter'        )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mSBSBaseParameters, 'sbs_common_parameters' , 'parameter'        )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mSBSParameters    , 'sbs_parameters'        , 'parameter'        )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mOutputBridgings  , 'output_bridgings'      , 'output_bridging'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mInputBridgings   , 'input_bridgings'       , 'input_bridging'   )

    @handle_exceptions()
    def classify(self, aOther):
        selfValue = self.mPath
        otherValue = aOther.mPath
        return (selfValue > otherValue) - (selfValue < otherValue)

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

    @handle_exceptions()
    def changeInstancePath(self, aParentDocument, aInstanceDocument, aGraphRelPath):
        """
        changeInstancePath(aParentDocument, aInstanceDocument, aGraphRelPath)
        Change the Substance graph referenced by this instance.
        If aInstanceDocument is not already declared as a dependency, the dependency will be added to aParentDocument.

        :param aParentDocument: The parent document of this node
        :type aParentDocument: :class:`.SBSDocument`
        :param aInstanceDocument: The document containing the Substance graph to reference by this instance (can be equal to parent document)
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
    def getDefinition(self):
        parameterDefs = []
        inputDefs = []
        outputDefs = []

        # Get default parameters
        defaultParameters = self.__getDefaultBaseParameters()
        defaultParameters.extend(self.__getDefaultCommonParameters())
        defaultParameters.extend(self.__getDefaultSubstanceParameters())

        for aParam in defaultParameters:
            if aParam.mName == '$uvw':
                inputDefs.append(mdllibclasses.MDLNodeDefInput(
                        aIdentifier=aParam.mName,
                        aType=mdllibclasses.MDLNodeDefType(aPath='mdl::base::texture_coordinate_info',
                                                           aName='texture_coordinate_info')))
            else:
                paramDef = mdllibclasses.MDLNodeDefParam()
                paramDef.fromMDLParameter(aParam, copyValue=True)
                parameterDefs.append(paramDef)

        for aInput in self.mInputBridgings:
            inputDef = mdllibclasses.MDLNodeDefInput()
            inputDef.fromMDLInputBridging(aInput)
            inputDefs.append(inputDef)

        for aOutput in self.mOutputBridgings:
            outputDef = mdllibclasses.MDLNodeDefOutput()
            outputDef.fromMDLOutputBridging(aOutput, self.mRefGraph())
            outputDefs.append(outputDef)

        nodeDefinition = mdllibclasses.MDLNodeDef(aPath = self.mPath,
                                                  aInputs = inputDefs,
                                                  aOutputs = outputDefs,
                                                  aParameters = parameterDefs)
        return nodeDefinition

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
        return 'Instance of Substance graph: '+ self.mPath

    @handle_exceptions()
    def getInputBridgeUID(self, aInputIdentifier):
        """
        getInputBridgeUID(aInputIdentifier)
        Get the input bridge UID (e.g. local identifier) of the input with the given identifier

        :param aInputIdentifier: The input identifier to look for.
        :type aInputIdentifier: str
        :return: The UID of the input bridging corresponding to the given input identifier, as a string
        """
        return next((i.mLocalIdentifier for i in self.mInputBridgings if i.mIdentifier == aInputIdentifier), None)

    @handle_exceptions()
    def getInputIdentifier(self, aInputBridgeUID):
        """
        getInputIdentifier(aInputBridgeUID)
        Get the identifier of the input with the given bridge UID (e.g. local identifier)

        :param aInputBridgeUID: The input bridge UID to look for.
        :type aInputBridgeUID: str
        :return: The identifier of the input bridging corresponding to the given UID, as a string
        """
        return next((i.mIdentifier for i in self.mInputBridgings if i.mLocalIdentifier == aInputBridgeUID), None)

    @handle_exceptions()
    def getOutputBridgeUID(self, aOutputIdentifier):
        """
        getOutputBridgeUID(aOutputIdentifier)
        Get the output bridge UID of the output with the given identifier

        :param aOutputIdentifier: The output identifier to look for.
        :type aOutputIdentifier: str
        :return: The UID of the output bridging corresponding to the given output identifier, as a string
        """
        return next((o.mUID for o in self.mOutputBridgings if o.mIdentifier == aOutputIdentifier), None)

    @handle_exceptions()
    def getOutputIdentifier(self, aOutputBridgeUID):
        """
        getOutputIdentifier(aOutputBridgeUID)
        Get the identifier of the output with the given bridge UID

        :param aOutputBridgeUID: The output bridge UID to look for.
        :type aOutputBridgeUID: str
        :return: The identifier of the output bridging corresponding to the given UID, as a string
        """
        return next((o.mIdentifier for o in self.mOutputBridgings if o.mUID == aOutputBridgeUID), None)

    @handle_exceptions()
    def getOutputType(self, aOutputIdentifier=None):
        """
        getOutputType(aOutputIdentifier=None)
        Get the output type of this node given the output identifier.

        :param aOutputIdentifier: The output identifier to look for. If None, the first output will be considered
        :type aOutputIdentifier: str, optional
        :return: The node output type as a string (color or float) if found, None otherwise
        """
        nodeDef = self.getDefinition()
        outputDef = None
        if aOutputIdentifier is not None:
            outputDef = nodeDef.getOutput(aOutputIdentifier)
            if not outputDef:
                outputBridge = next((ob for ob in self.mOutputBridgings if ob.mUID == aOutputIdentifier), None)
                outputDef = nodeDef.getOutput(outputBridge.mIdentifier) if outputBridge else None

        elif nodeDef.mOutputs:
            outputDef = nodeDef.mOutputs[0]
        return outputDef.getType() if outputDef else None

    def getParameter(self, aParameter):
        return next((p for p in list(set().union(self.mParameters, self.mSBSParameters, self.mSBSBaseParameters)) \
                      if p.mName == aParameter), None)

    def getParameterValue(self, aParameter):
        param = self.getParameter(aParameter)
        return param.getValue() if param is not None else None

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
        aPath = self.mRefDependency().mFileAbsPath + '/' + aPath
        return aPath.replace('\\', '/')

    @handle_exceptions()
    def getReferenceInternalPath(self):
        """
        getReferenceInternalPath()
        Get the path of the referenced graph relatively to the package (pkg:///).

        :return: The path as a string
        """
        return self.mPath

    @handle_exceptions()
    def resetParameter(self, aParameter):
        param = self.getParameter(aParameter)
        if param is None:
            raise SBSLibraryError('Parameter '+python_helpers.castStr(aParameter)+' cannot be reset on '+self.getDisplayName())
        nodeDef = self.getDefinition()
        paramDef = nodeDef.getParameter(aParameter)
        if paramDef is None:
            raise SBSLibraryError('Parameter '+python_helpers.castStr(aParameter)+' cannot be reset on '+self.getDisplayName())

        param.setValue(paramDef.getDefaultValue())
        param.setIsDefaultValue(True)

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        param = self.getParameter(aParameter)
        if param is None:
            raise SBSLibraryError('Parameter '+python_helpers.castStr(aParameter)+' cannot be set on '+self.getDisplayName())

        param.setValue(aParamValue)
        param.setIsDefaultValue(False)

    @handle_exceptions()
    def resolveDependency(self, aSBSDocument):
        """
        resolveDependency(aSBSDocument)
        Allow to resolve the dependency of the SBS graph instance node with the graph it references.

        :param aSBSDocument: The root document
        :type aSBSDocument: :class:`.SBSDocument`
        """
        if not self.mPath or not api_helpers.hasPkgPrefix(self.mPath):
            return False

        aPath = api_helpers.removePkgPrefix(self.mPath)
        aGraphRelPath, aDepUID = api_helpers.splitPathAndDependencyUID(aPath)

        # if the tag ?dependency= is not present, take the first dependency of the document
        if aDepUID is None:
            try:
                aDepUID = aSBSDocument.getDependencyContainingInternalPath(self.mPath).mUID
            except:
                log.error('Graph %s not found', aPath)
                return False

        try:
            aDep = aSBSDocument.getDependency(aUID = aDepUID)
            self.mRefDependency = weakref.ref(aDep)
            aPackageWR = aDep.getRefPackage()
            try:
                aGraph = aPackageWR().getObjectFromInternalPath(aGraphRelPath)
                self.mRefGraph = weakref.ref(aGraph)
            except:
                log.error('Graph %s/%s not found', aDep.mFilename, aGraphRelPath)
        except:
            log.error('Dependency %s not found, cannot resolve: %s', aDepUID, aPath)

        return self.mRefGraph is not None


    @staticmethod
    def __getDefaultCommonParameters():
        return [mdlsbsbridge.MDLParameter(aName='$tiling',
                                          aValue=mdlsbsbridge.MDLParamValue('1', 'float1')),
                mdlsbsbridge.MDLParameter(aName='$directx_normal',
                                          aValue=mdlsbsbridge.MDLParamValue('1', 'bool')),
                mdlsbsbridge.MDLParameter(aName='$use_physical_size',
                                          aValue=mdlsbsbridge.MDLParamValue('0', 'bool')),
                mdlsbsbridge.MDLParameter(aName='$uvw',
                                          aValue=mdlsbsbridge.MDLParamValue('0', 'float1'))]

    @staticmethod
    def __getDefaultBaseParameters():
        return [mdlsbsbridge.MDLParameter(aName='$outputsize',
                                          aValue=mdlsbsbridge.MDLParamValue('9 9', 'int2')),
                mdlsbsbridge.MDLParameter(aName='$pixelsize',
                                          aValue=mdlsbsbridge.MDLParamValue('1 1', 'float2')),
                mdlsbsbridge.MDLParameter(aName='$randomseed',
                                          aValue=mdlsbsbridge.MDLParamValue('0', 'int1'))]

    def __getDefaultSubstanceParameters(self):
        aSBSParameters = []
        if self.mRefGraph is not None:
            for aParam in self.mRefGraph().getInputParameters():
                sbsParam = mdlsbsbridge.MDLParameter(aName=aParam.mIdentifier, aIsDefaultValue='1')
                sbsParam.setValue(aValue=aParam.getDefaultValue(), aType= aParam.getType())
                aSBSParameters.append(sbsParam)
        return aSBSParameters

    def __getInfoFromReferencedGraph(self):
        if self.mRefGraph is None:
            return

        # Create Substance graph specific parameters
        aSBSParameters = []
        if self.__needToUpdateParameters():
            for aParam in self.mRefGraph().getInputParameters():
                aSBSParam = next((p for p in self.mSBSParameters if p.mName == aParam.mIdentifier), None)
                if aSBSParam is not None and not aSBSParam.isDefaultValue():
                    value = aSBSParam.getValue()
                else:
                    value = aParam.getDefaultValue()
                sbsParam = mdlsbsbridge.MDLParameter(aName=aParam.mIdentifier, aIsDefaultValue='1')
                sbsParam.setValue(aValue=value, aType= aParam.getType())
                aSBSParameters.append(sbsParam)
            self.mSBSParameters = aSBSParameters

        # Create input bridgings
        aInputBridges = []
        if self.__needToUpdateInputBridgings():
            for aInput in self.mRefGraph().getInputImages():
                inputBridge = next((b for b in self.mInputBridgings if b.mIdentifier == aInput.mIdentifier), None)
                if inputBridge is None:
                    inputBridge = mdlsbsbridge.MDLInputBridging(aIdentifier=aInput.mIdentifier,
                                                                aLocalIdentifier='$'+UIDGenerator.generateUID(self))
                aInputBridges.append(inputBridge)
            self.mInputBridgings = aInputBridges

        # Create output bridgings
        aOutputBridges = []
        if self.__needToUpdateOutputBridgings():
            for aOutput in self.mRefGraph().getGraphOutputs():
                outputBridge = next((b for b in self.mOutputBridgings if b.mIdentifier == aOutput.mIdentifier), None)
                if outputBridge is None:
                    outputBridge = mdlsbsbridge.MDLOutputBridging(aIdentifier=aOutput.mIdentifier,
                                                                  aUID=UIDGenerator.generateUID(self))
                aOutputBridges.append(outputBridge)
            self.mOutputBridgings = aOutputBridges

    def __needToUpdateParameters(self):
        if not self.mRefGraph():
            return False
        if len(self.mRefGraph().getInputParameters()) != len(self.mSBSParameters):
            return True
        for aParam,aSBSParam in zip(self.mRefGraph().getInputParameters(), self.mSBSParameters):
            if aParam.mIdentifier != aSBSParam.mName:
                return True
            elif aSBSParam.isDefaultValue() and aParam.getDefaultValue() != aSBSParam.getTypedValue():
                return True
        return False

    def __needToUpdateInputBridgings(self):
        if not self.mRefGraph():
            return False
        if len(self.mRefGraph().getInputImages()) != len(self.mInputBridgings):
            return True
        for aInput,aBridge in zip(self.mRefGraph().getInputImages(), self.mInputBridgings):
            if aInput.mIdentifier != aBridge.mIdentifier:
                return True
        return False

    def __needToUpdateOutputBridgings(self):
        if not self.mRefGraph():
            return False
        if len(self.mRefGraph().getGraphOutputs()) != len(self.mOutputBridgings):
            return True
        for aOutput,aBridge in zip(self.mRefGraph().getGraphOutputs(), self.mOutputBridgings):
            if aOutput.mIdentifier != aBridge.mIdentifier:
                return True
        return False



# =======================================================================
@doc_inherit
class MDLImplementation(SBSObject):
    """
    Class that contains information on the implementation of a MDL node as defined in a .sbs file.
    The implementation is exclusive, only one member of the MDLImplementation is defined.

    Members:
        * mImplConstant         (:class:`.MDLImplConstant`): constant node implementation.
        * mImplSelector         (:class:`.MDLImplSelector`): selector node implementation.
        * mImplMDLInstance      (:class:`.MDLImplMDLInstance`): native function or native material node implementation.
        * mImplMDLGraphInstance (:class:`.MDLImplMDLGraphInstance`): MDL graph instance.
        * mImplSBSInstance      (:class:`.MDLImplSBSInstance`): Substance graph instance.
        * mImplPassThrough      (:class:`.MDLImplPassThrough`): Passthrough node implementation.
    """
    def __init__(self,
                 aImplConstant         = None,
                 aImplSelector         = None,
                 aImplMDLInstance      = None,
                 aImplMDLGraphInstance = None,
                 aImplSBSInstance      = None,
                 aImplPassThrough      = None):
        super(MDLImplementation, self).__init__()
        self.mImplConstant         = aImplConstant
        self.mImplSelector         = aImplSelector
        self.mImplMDLInstance      = aImplMDLInstance
        self.mImplMDLGraphInstance = aImplMDLGraphInstance
        self.mImplSBSInstance      = aImplSBSInstance
        self.mImplPassThrough      = aImplPassThrough

        self.mMembersForEquality = ['mImplConstant',
                                    'mImplSelector',
                                    'mImplMDLInstance',
                                    'mImplMDLGraphInstance',
                                    'mImplSBSInstance',
                                    'mImplPassThrough']

        self._mImplKind = None

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mImplConstant         = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_node_implementation_constant'          , MDLImplConstant         )
        self.mImplSelector         = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_node_implementation_selector'          , MDLImplSelector         )
        self.mImplMDLInstance      = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_node_implementation_mdl_instance'      , MDLImplMDLInstance      )
        self.mImplMDLGraphInstance = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_node_implementation_mdl_graph_instance', MDLImplMDLGraphInstance )
        self.mImplSBSInstance      = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_node_implementation_sbs_instance'      , MDLImplSBSInstance      )
        self.mImplPassThrough      = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_node_implementation_passthrough'       , MDLImplPassThrough      )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeSBSNode(aXmlNode, self.mImplConstant        , 'mdl_node_implementation_constant'           )
        aSBSWriter.writeSBSNode(aXmlNode, self.mImplSelector        , 'mdl_node_implementation_selector'           )
        aSBSWriter.writeSBSNode(aXmlNode, self.mImplMDLInstance     , 'mdl_node_implementation_mdl_instance'       )
        aSBSWriter.writeSBSNode(aXmlNode, self.mImplMDLGraphInstance, 'mdl_node_implementation_mdl_graph_instance' )
        aSBSWriter.writeSBSNode(aXmlNode, self.mImplSBSInstance     , 'mdl_node_implementation_sbs_instance'       )
        aSBSWriter.writeSBSNode(aXmlNode, self.mImplPassThrough     , 'mdl_node_implementation_passthrough'        )

    @handle_exceptions()
    def classify(self, aOther):
        """
        classify(aOther, aParentContainer = None)
        | Use the definition of the two MDLImplementation to classify them.
        | To classify the different kind of MDLImplementation, this order is specify:
        | Constant < Selector < MDL instance < MDL graph instance < SBS graph instance.
        | In case of equality, the appropriate classify function is called, depending on the kind of implementation.

        :param aOther: The filter to compare to.
        :type aOther: :class:`.MDLImplementation`
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        # Compare Implementation kind
        selfKind = self.getImplementationKind()
        otherKind = aOther.getImplementationKind()
        if selfKind != otherKind:
            return max(-1, min(1, selfKind - otherKind))

        # Compare the two identical implementation
        return self.getImplementation().classify(aOther.getImplementation())

    @handle_exceptions()
    def getImplementation(self):
        """
        getImplementation()
        Get the implementation kind of this node, among the list defined in :class:`.MDLImplementationKindEnum`

        :return: The :class:`.MDLImplementationKindEnum`
        """
        if   self.isAConstant():        return self.mImplConstant
        elif self.isASelector():        return self.mImplSelector
        elif self.isMDLInstance():      return self.mImplMDLInstance
        elif self.isMDLGraphInstance(): return self.mImplMDLGraphInstance
        elif self.isSBSInstance():      return self.mImplSBSInstance
        elif self.isSBSPassThrough():   return self.mImplPassThrough

    @handle_exceptions()
    def getImplementationKind(self):
        """
        getImplementationKind()
        Get the implementation kind of this node, among the list defined in :class:`.MDLImplementationKindEnum`

        :return: The :class:`.MDLImplementationKindEnum`
        """
        if self._mImplKind is None:
            if   self.isAConstant():        self._mImplKind = mdlenum.MDLImplementationKindEnum.CONSTANT
            elif self.isASelector():        self._mImplKind = mdlenum.MDLImplementationKindEnum.SELECTOR
            elif self.isMDLInstance():      self._mImplKind = mdlenum.MDLImplementationKindEnum.MDL_INSTANCE
            elif self.isMDLGraphInstance(): self._mImplKind = mdlenum.MDLImplementationKindEnum.MDL_GRAPH_INSTANCE
            elif self.isSBSInstance():      self._mImplKind = mdlenum.MDLImplementationKindEnum.SBS_INSTANCE
            elif self.isSBSPassThrough():   self._mImplKind = mdlenum.MDLImplementationKindEnum.PASSTHROUGH

        return self._mImplKind

    @handle_exceptions()
    def isAConstant(self):
        """
        isAConstant()

        :return: True if the MDLNode is a constant node implementation, False otherwise.
        """
        return self.mImplConstant is not None

    @handle_exceptions()
    def isASelector(self):
        """
        isASelector()

        :return: True if the MDLNode is selector (e.g. an implementation of a special node that allows access to struct members), False otherwise.
        """
        return self.mImplSelector is not None

    @handle_exceptions()
    def isAPassthrough(self):
        """
        isAPassthrough()

        :return: True if the MDLNode is passthrough (e.g. an implementation of a special node that allows to organize graph connection layout), False otherwise.
        """
        return self.mImplPassThrough is not None

    @handle_exceptions()
    def isMDLInstance(self):
        """
        isMDLInstance()

        :return: True if the MDLNode is a native function or native material node implementation, False otherwise.
        """
        return self.mImplMDLInstance is not None

    @handle_exceptions()
    def isMDLGraphInstance(self):
        """
        isMDLGraphInstance()

        :return: True if the MDLNode is a MDL graph instance, False otherwise.
        """
        return self.mImplMDLGraphInstance is not None

    @handle_exceptions()
    def isSBSInstance(self):
        """
        isSBSInstance()

        :return: True if the MDLNode is a Substance graph instance, False otherwise.
        """
        return self.mImplSBSInstance is not None

    @handle_exceptions()
    def isSBSPassThrough(self):
        """
        isSBSInstance()

        :return: True if the MDLNode is a passthrough instance, False otherwise.
        """
        return self.mImplPassThrough is not None
