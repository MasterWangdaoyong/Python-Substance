# coding: utf-8
"""
Module **paramnode** provides the definition of the class :class:`.SBSFuncData` and :class:`.SBSParamNode` which compose a function graph.
"""
from __future__ import unicode_literals
import copy
import logging
log = logging.getLogger(__name__)
import weakref

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSLibraryError, SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum
from pysbs import sbslibrary
from pysbs import sbscommon


# ==============================================================================
@doc_inherit
class SBSFuncData(SBSObject):
    """
    Class that contains information on a function data as defined in a .sbs file

    Members:
        * mName          (str): identifier of the data.
        * mConstantValue (:class:`.SBSConstantValue`): value.
    """
    def __init__(self,
                 aName = '',
                 aConstantValue = None):
        super(SBSFuncData, self).__init__()
        self.mName          = aName
        self.mConstantValue = aConstantValue

        self.mMembersForEquality = ['mName',
                                    'mConstantValue']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName          = aSBSParser.getXmlElementVAttribValue(aXmlNode,           'name'           )
        self.mConstantValue = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'constantValue', sbscommon.SBSConstantValue)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName, 'name'           )
        aSBSWriter.writeSBSNode(aXmlNode,  self.mConstantValue,    'constantValue'  )

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this function data

        :return: The value as a string
        """
        return self.mConstantValue.getValue() if self.mConstantValue is not None else None



# ==============================================================================
@doc_inherit
class SBSParamNode(sbscommon.SBSNode):
    """
    Class that contains information on a parameter node as defined in a .sbs file.
    A SBSParamNode represents a function node. It is included in the definition of a :class:`.SBSDynamicValue`,
    and it can be connected to other SBSParamNode.

    Members:
        * mGUIName     (str, optional): name of the node.
        * mUID         (str): unique identifier in the dynamicValue/paramNodes/ context.
        * mFunction    (str): identifier of the function, among the available identifiers as defined in :mod:`.sbsfunctions`.
        * mDisabled    (str, optional): this node is disabled ("1" / None).
        * mType        (str, optional): return type of the node, if the node can handle multiple types.
        * mConnections (list of :class:`.SBSConnection`, optional): input connections list.
        * mFuncDatas   (list of :class:`.SBSFuncData`): additional data list.
        * mGUILayout   (:class:`.SBSGUILayout`): GUI position of the node in the function graph.
        * mRefFunction (:class:`.SBSFunction`, optional): in the case of an *instance* function node, reference to the function it represents.
   """
    def __init__(self,
                 aGUIName       = None,
                 aUID           = '',
                 aFunction      = '',
                 aDisabled      = None,
                 aType          = None,
                 aConnections   = None,
                 aFuncDatas     = None,
                 aGUILayout     = None,
                 aRefFunction   = None,
                 aRefDependency = None):
        super(SBSParamNode, self).__init__(aGUIName, aUID, aDisabled, aConnections, aGUILayout)
        self.mFunction   = aFunction
        self.mType       = aType
        self.mFuncDatas  = aFuncDatas
        self.mRefFunction  = weakref.ref(aRefFunction) if aRefFunction is not None else None
        self.mRefDependency= weakref.ref(aRefDependency) if aRefDependency is not None else None

        self.mMembersForEquality.append('mFunction')
        self.mMembersForEquality.append('mType')
        self.mMembersForEquality.append('mFuncDatas')

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSParamNode, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mFunction  = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'function' )
        self.mType      = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'type'     )
        self.mFuncDatas = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'funcDatas', 'funcData', SBSFuncData)

        if self.isAnInstance():
            aContext.addSBSObjectToResolve(self)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mGUIName    , 'GUIName'    )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID        , 'uid'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFunction   , 'function'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDisabled   , 'disabled'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType       , 'type'       )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mConnections, 'connections', 'connection'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mFuncDatas  , 'funcDatas'  , 'funcData'   )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mGUILayout  , 'GUILayout'  )

    @handle_exceptions()
    def getDisplayName(self):
        return self.mFunction+' ('+self.mUID+')'

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther)
        Use the definition of the two nodes to classify them, and their GUI position if they have the same definition.
        The function identifier is used to classify them.
        At a final option, the GUI position is used, and in this case, mostLeft < mostRight and then mostUp < mostDown.

        :param aOther: The node to compare to.
        :param aParentContainer: The dynamic value containing the nodes to classify
        :type aOther: :class:`.SBSParamNode`
        :type aParentContainer: :class:`.SBSDynamicValue`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        selfValue = self.mFunction
        otherValue = aOther.mFunction
        res = (selfValue > otherValue) - (selfValue < otherValue)

        if res == 0 and self.isAnInstance():
            if self.mRefFunction and aOther.mRefFunction:
                selfValue = self.mRefFunction().mIdentifier
                otherValue = aOther.mRefFunction().mIdentifier
            elif self.mFuncDatas and aOther.mFuncDatas:
                selfValue = self.mFuncDatas[0].getValue()
                otherValue = aOther.mFuncDatas[0].getValue()
            res = (selfValue > otherValue) - (selfValue < otherValue)

        if res == 0:
            GUIOffset = map(lambda x,y:x-y, self.getPosition(), aOther.getPosition())
            res = next((1 if offset > 0 else -1 for offset in GUIOffset if offset != 0), 0)

        return res

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
        if not self.isAnInstance():
            raise SBSImpossibleActionError('The node '+self.getDisplayName()+' is not an instance, cannot change the dependency UID it references')

        oldUID = self.getDependencyUID()
        aPath = self.getParameterValue(self.mFunction)
        if oldUID is not None and aPath is not None:
            self.setParameterValue(self.mFunction, aPath.replace(oldUID, newDepUID))
        self.resolveDependency(aSBSDocument)

    def changeInstancePath(self, aParentDocument, aInstanceDocument, aFunctionRelPath):
        """
        changeInstancePath(aParentDocument, aInstanceDocument, aFunctionRelPath)
        Change the function referenced by this instance.
        If aInstanceDocument is not already declared as a dependency, the dependency will be added to aParentDocument.

        :param aParentDocument: The parent document of this node
        :type aParentDocument: :class:`.SBSDocument`
        :param aInstanceDocument: The document containing the function to reference by this instance (can be equal to parent document)
        :type aInstanceDocument: :class:`.SBSDocument`
        :param aFunctionRelPath: The function path, relatively to its parent package aInstanceDocument (pkg:///myFunction?dependency=1234567890)
        :type aFunctionRelPath: str
        """
        if not self.isAnInstance():
            raise SBSImpossibleActionError('The node '+self.getDisplayName()+' is not an instance, cannot change the path of the referenced function')

        outValues = aParentDocument.addReferenceOnDependency(aDependencyPath = aInstanceDocument.mFileAbsPath,
                                                            aRelPathToObject = api_helpers.splitPathAndDependencyUID(aFunctionRelPath)[0])
        aFunctionRelPath = outValues[1]
        self.setParameterValue(self.mFunction, aFunctionRelPath)
        self.resolveDependency(aParentDocument)

    @handle_exceptions()
    def hasAReferenceOnDependency(self, aDependency):
        aUID = aDependency if python_helpers.isStringOrUnicode(aDependency) else aDependency.mUID
        return self.isAnInstance() and self.getDependencyUID() == aUID

    @handle_exceptions()
    def hasAReferenceOnInternalPath(self, aInternalPath):
        return self.getReferenceInternalPath() == aInternalPath

    @handle_exceptions()
    def resolveDependency(self, aSBSDocument):
        """
        resolveDependency(aSBSDocument)
        Allow to resolve the dependency of the function instance node with the function it references.

        :param aSBSDocument: The root document
        :type aSBSDocument: :class:`.SBSDocument`
        """
        if self.mFuncDatas is None:
            return False

        aInternalPath = self.getParameterValue(self.mFunction)
        if not api_helpers.hasPkgPrefix(aInternalPath):
            return False

        aPath = api_helpers.removePkgPrefix(aInternalPath)
        aFunctionRelPath, aDepUID = api_helpers.splitPathAndDependencyUID(aPath)

        # if the tag ?dependency= is not present, take the first dependency of the document
        if aDepUID is None:
            try:
                aDepUID = aSBSDocument.getDependencyContainingInternalPath(aInternalPath).mUID
            except:
                log.warning('Function %s not found', aInternalPath)
                return False

        try:
            aDep = aSBSDocument.getDependency(aUID = aDepUID)
            self.mRefDependency = weakref.ref(aDep)
            aPackageWR = aDep.getRefPackage()
            try:
                aFunction = aPackageWR().getObjectFromInternalPath(aFunctionRelPath)
                self.mRefFunction = weakref.ref(aFunction)
            except:
                log.warning('Function %s/%s not found', aDep.mFilename, aFunctionRelPath)
        except:
            log.warning('Dependency %s not found, cannot resolve: %s', aDepUID, aPath)

        return self.mRefFunction is not None

    def isAnInstance(self):
        """
        isAnInstance()
        Check if this SBSParamNode is of kind 'instance'

        :return: True if this node is a function node 'instance', False otherwise
        """
        return self.mFunction == sbslibrary.getFunctionDefinition(sbsenum.FunctionEnum.INSTANCE).mIdentifier

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the function node definition (Inputs, Outputs, Parameters)

        :return: a :class:`.FunctionDef` object
        """
        aFunction = sbslibrary.getFunctionEnum(self.mFunction)

        # Particular case of an instance of function: complete the definition to add the input parameters
        if aFunction == sbsenum.FunctionEnum.INSTANCE and self.mRefFunction is not None:
            functionDef = copy.deepcopy(sbslibrary.getFunctionDefinition(aFunction))

            # Look for the input parameters of the function
            for aParamInput in self.mRefFunction().getInputParameters():
                newInput = sbslibrary.FunctionInput(aIdentifier = aParamInput.mIdentifier,
                                                    aType = int(aParamInput.mType))
                functionDef.mInputs.append(newInput)

            # Set the output type
            if functionDef.mOutputs:
                functionDef.mOutputs[0].mType = self.mRefFunction().getOutputType()
        else:
            functionDef = sbslibrary.getFunctionDefinition(aFunction)

        return functionDef

    @handle_exceptions()
    def getParameterValue(self, aParameter = None):
        """
        getParameterValue(aParameter = None)
        Find a parameter with the given name/id among the function datas of this ParamNode.
        If aParameter is None, return the parameter with the name of the function.

        :param aParameter: Parameter identifier
        :type aParameter: sbsenum.Function or str, optional
        :return: The parameter value if found, None otherwise
        """
        if aParameter is None:
            aParameter = self.mFunction

        aFunction = None
        aParameterName = None
        if python_helpers.isStringOrUnicode(aParameter):
            aParameterName = aParameter
        else:
            aFunction = sbslibrary.getFunctionDefinition(aParameter)
            if aFunction is not None:
                aParameterName = aFunction.mIdentifier

        if aParameterName is None:
            return None

        # Parse the parameters overloaded on the ParamNode
        if self.mFuncDatas is not None:
            param = next((param for param in self.mFuncDatas if param.mName == aParameterName), None)
            if param is not None:
                return param.mConstantValue.getValue()

        # Parse the default parameters of this ParamNode
        if aFunction is None:
            aFunction = sbslibrary.getFunctionDefinition(aParameter)
        if aFunction is not None:
            defaultParam = aFunction.getParameter(aParameter)
            if defaultParam is not None:
                return defaultParam.mDefaultValue

        return None

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        """
        setParameterValue(aParameter, aParamValue)
        Set the value of the given parameter to the given value, if compatible with this type of Function

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :type aParameter: sbsenum.FilterParameterEnum or str
        :type aParamValue: any parameter type
        :return: True if succeed
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        if aParameter is None:
            aParameter = self.mFunction

        aParameterName = None
        aFunctionDef = None
        aType = None
        if python_helpers.isStringOrUnicode(aParameter):
            aParameterName = aParameter
        else:
            aFunctionDef = sbslibrary.getFunctionDefinition(aParameter)
            if aFunctionDef is not None:
                aParameterName = aFunctionDef.mIdentifier

        # For now only the parameter that has the same name as the function is supported
        # As the model allows it, maybe one day there will be several parameters on a function, and this test should be removed
        if aParameterName != self.mFunction:
            paramStr = aParameterName if aParameterName is not None else str(aParameter)
            raise SBSLibraryError('Parameter '+paramStr+' cannot be set on function '+self.mFunction)

        # Parse the default input parameter of this Function node
        if aFunctionDef is None:
            aFunctionDef = sbslibrary.getFunctionDefinition(self.mFunction)
        defaultParam = aFunctionDef.getParameter(aParameter)
        if defaultParam is not None:
            aType = defaultParam.mType
        if aType is None:
            raise SBSLibraryError('Parameter '+aParameterName+' cannot be set on function '+self.mFunction)

        # Ensure having a correctly formatted value
        aFormattedParamValue = api_helpers.formatValueForTypeStr(aParamValue, aType)

        # Parse the parameters already defined on this Function node and modify it if found
        if self.mFuncDatas:
            param = next((param for param in self.mFuncDatas if param.mName == aParameterName), None)
            if param is not None:
                param.mConstantValue.updateConstantValue(aFormattedParamValue)
                return True

        # Create a new parameter
        aSBSConstantValue = sbscommon.SBSConstantValue()
        aSBSConstantValue.setConstantValue(aType, aFormattedParamValue)
        aSBSFuncData = SBSFuncData(aName = aParameterName, aConstantValue = aSBSConstantValue)
        api_helpers.addObjectToList(self, 'mFuncDatas', aSBSFuncData)
        return True


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
        if aParameter is None:
            aParameter = self.mFunction

        aParameterName = None
        aFunctionDef = None
        if python_helpers.isStringOrUnicode(aParameter):
            aParameterName = aParameter
        else:
            aFunctionDef = sbslibrary.getFunctionDefinition(aParameter)
            if aFunctionDef is not None:
                aParameterName = aFunctionDef.mIdentifier

        # For now only the parameter that has the same name as the function is supported
        # As the model allows it, maybe one day there will be several parameters on a function, and this test should be removed
        if aParameterName != self.mFunction:
            paramStr = aParameterName if aParameterName is not None else str(aParameter)
            raise SBSLibraryError('Parameter '+paramStr+' cannot be unset on function '+self.mFunction)

        # Parse the default input parameter of this Function node
        if aFunctionDef is None:
            aFunctionDef = sbslibrary.getFunctionDefinition(self.mFunction)
        defaultParam = aFunctionDef.getParameter(aParameter)
        if defaultParam is None:
            raise SBSLibraryError('Parameter '+aParameterName+' cannot be unset on function '+self.mFunction)

        # Parse the parameters already defined on this Function node and modify it if found
        if self.mFuncDatas:
            param = next((param for param in self.mFuncDatas if param.mName == aParameterName), None)
            if param is not None:
                self.mFuncDatas.remove(param)
                return True

        return False


    @handle_exceptions()
    def getOutputType(self):
        """
        getOutputType()

        :return: The output type of the function node. In case of a template, return the value of the template
        """
        if self.mType is None:
            return None

        aType = int(self.mType)
        if self.isAnInstance() and self.mRefFunction is not None:
            aType = self.mRefFunction().getOutputType()
        elif aType == sbsenum.ParamTypeEnum.TEMPLATE1:
            aFunction = sbslibrary.getFunctionDefinition(self.mFunction)
            aType = aFunction.mTemplate1

        return aType

    @handle_exceptions()
    def getDependencyUID(self):
        """
        getDependencyUID()
        If this node is an instance of a Function, get the UID of the dependency referenced by this instance.

        :return: The dependency UID as a string if found, None otherwise
        """
        if not self.isAnInstance():
            return None
        if self.mRefDependency() is not None:
            return self.mRefDependency().mUID

        aPath = self.getParameterValue()
        return api_helpers.splitPathAndDependencyUID(aPath)[1] if aPath else None

    @handle_exceptions()
    def getReferenceAbsPath(self):
        """
        getReferenceAbsPath()
        If this function node is an instance, get the absolute path of the function referenced by this instance.

        :return: The absolute path of the function referenced by this instance, in the format absolutePath/filename.sbs/functionIdentifier, as a string
        """
        if not self.isAnInstance() or not self.mFuncDatas:
            return None

        aPath = self.mFuncDatas[0].getValue()
        aPath = api_helpers.removePkgPrefix(aPath)
        aPath = api_helpers.splitPathAndDependencyUID(aPath)[0]
        aPath = aPath.replace('\\', '/')
        aDepAbsPath = self.mRefDependency().mFileAbsPath.replace('\\', '/')
        aPath = aDepAbsPath + '/' + aPath
        return aPath


    @handle_exceptions()
    def getReferenceInternalPath(self):
        """
        getReferenceInternalPath()
        If this function node is an instance, get the path of the function relatively to the package (pkg:///).

        :return: The path as a string
        """
        return self.mFuncDatas[0].getValue() if self.isAnInstance() and self.mFuncDatas else None


    @handle_exceptions()
    def setType(self, aParamTypeEnum):
        """
        setType()
        Set a new param type

        :return: aParamTypeEnum
        """
        if not python_helpers.isIntOrLong(aParamTypeEnum):
            raise SBSLibraryError('Parameter '+str(aParamTypeEnum)+' is not a valid param type')
        self.mType = str(aParamTypeEnum)
        return aParamTypeEnum
