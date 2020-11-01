# coding: utf-8
"""
Module **mdlnode** aims to define the class :class:`.MDLNode` which corresponds to the nodes of a :class:`.MDLGraph`.
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers, api_helpers
from pysbs import sbscommon

from . import MDLImplementation
from . import mdlenum
from . import mdldictionaries as mdldict
from .mdlmanager import MDLManager


# =======================================================================
@doc_inherit
class MDLNode(sbscommon.SBSNode):
    """
    Class that contains information on a MDL node as defined in a .sbs file

    Members:
        * mUID                (str): node unique identifier in the MDLGraph context.
        * mGUILayout          (:class:`.SBSGUILayout`): GUI position/options
        * mConnections        (list of :class:`.SBSConnection`, optional): input connections list.
        * mMDLImplementation  (:class:`.MDLImplementation`): implementation of the MDL node.
    """
    def __init__(self,
                 aUID           = '',
                 aGUILayout     = None,
                 aConnections    = None,
                 aMDLImplementation = None):
        super(MDLNode, self).__init__(aGUIName=None, aUID=aUID, aDisabled=None, aConnections=aConnections, aGUILayout=aGUILayout)
        self.mMDLImplementation  = aMDLImplementation
        self.mMembersForEquality.append('mMDLImplementation')

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(MDLNode, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mMDLImplementation = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'mdl_node_implementation', MDLImplementation)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID              , 'uid'                    )
        aSBSWriter.writeListOfSBSNode(aXmlNode       , self.mConnections      , 'connections'            , 'connection'  )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mMDLImplementation, 'mdl_node_implementation')
        aSBSWriter.writeSBSNode(aXmlNode             , self.mGUILayout        , 'GUILayout'              )

    @handle_exceptions()
    def classify(self, aOther, aParentContainer = None):
        """
        classify(aOther, aParentContainer = None)
        | Use the definition of the two nodes to classify them, and their GUI position if they have the same definition.
        | To classify the different kind of MDLImplementation, this order is specify:
        | Constant < Selector < MDLInstance < MDLGraphInstance < SBSInstance.
        | For two identical implementation kind, the names or the paths of the nodes are used to compare the lexicographic order.
        | At a final option, the GUI position is used, and in this case, mostLeft < mostRight and then mostUp < mostDown.

        :param aOther: The node to compare to.
        :param aParentContainer: The graph containing the nodes to classify
        :type aOther: :class:`.MDLNode`
        :type aParentContainer: :class:`.MDLGraph`, optional
        :return: 1 if itself is considered greater than the other node, -1 for the opposite. 0 in case of equality.
        """
        # Compare Implementations
        res = self.mMDLImplementation.classify(aOther.mMDLImplementation)

        # Last chance: compare GUI position
        if res == 0:
            GUIOffset = map(lambda x,y:x-y, self.getPosition(),aOther.getPosition())
            res = next((offset for offset in GUIOffset if offset != 0), 0)

        return res

    @handle_exceptions()
    def getOutputType(self, aOutputIdentifier=None):
        """
        getOutputType(aOutputIdentifier=None)
        Get the output type of this node given the output identifier.

        :param aOutputIdentifier: The output identifier to look for. If None, the first output will be considered
        :type aOutputIdentifier: str, optional
        :return: The node output type as a string (color or float) if found, None otherwise
        """
        return self.getMDLImplementation().getOutputType(aOutputIdentifier)

    @handle_exceptions()
    def isAConstant(self):
        """
        isAConstant()

        :return: True if the MDLNode is a constant node implementation, False otherwise.
        """
        return self.mMDLImplementation.isAConstant()

    @handle_exceptions()
    def isAPotentialOutput(self):
        """
        isAPotentialOutput()
        Check if this node can be set as an output of the MDLGraph

        :return: True if the MDLNode is a MDL instance of kind 'mdl::material(bool,material_surface,material_surface,color,material_volume,material_geometry)'
        """
        nodeDef = self.getDefinition()
        output = nodeDef.getOutput()
        return self.isMDLGraphInstance() or \
                    (self.isMDLInstance() and
                        (nodeDef.mIsMaterial or
                            (output is not None and output.getType() == mdldict.getMDLPredefTypePath(mdlenum.MDLPredefTypes.MATERIAL))))

    @handle_exceptions()
    def isAnInput(self):
        """
        isAnInput()

        :return: True if the MDLNode is an input of the graph (e.g. exposed constant node), False otherwise.
        """
        return self.isAConstant() and self.getMDLImplConstant().isAnInput()

    @handle_exceptions()
    def isASelector(self):
        """
        isASelector()

        :return: True if the MDLNode is selector (e.g. an implementation of a special node that allows access to struct members), False otherwise.
        """
        return self.mMDLImplementation.isASelector()

    @handle_exceptions()
    def isAPassthrough(self):
        """
        isAPassthrough()

        :return: True if the MDLNode is passthrough (e.g. an implementation of a special node that allows to organize graph connection layout), False otherwise.
        """
        return self.mMDLImplementation.isAPassthrough()

    @handle_exceptions()
    def isMDLInstance(self):
        """
        isMDLInstance()

        :return: True if the MDLNode is a native function or native material node implementation, False otherwise.
        """
        return self.mMDLImplementation.isMDLInstance()

    @handle_exceptions()
    def isMDLGraphInstance(self):
        """
        isMDLGraphInstance()

        :return: True if the MDLNode is a MDL graph instance, False otherwise.
        """
        return self.mMDLImplementation.isMDLGraphInstance()

    @handle_exceptions()
    def isSBSInstance(self):
        """
        isSBSInstance()

        :return: True if the MDLNode is a Substance graph instance, False otherwise.
        """
        return self.mMDLImplementation.isSBSInstance()

    @handle_exceptions()
    def getMDLImplConstant(self):
        """
        getMDLImplConstant()

        :return: the :class:`.MDLImplConstant` object if this node is a MDL constant, None otherwise.
        """
        return self.mMDLImplementation.mImplConstant if self.isAConstant() else None

    @handle_exceptions()
    def getMDLImplSelector(self):
        """
        getMDLImplSelector()

        :return: the :class:`.MDLImplSelector` object if this node is a MDL selector, None otherwise.
        """
        return self.mMDLImplementation.mImplSelector if self.isASelector() else None

    @handle_exceptions()
    def getMDLImplMDLInstance(self):
        """
        getMDLImplMDLInstance()

        :return: the :class:`.MDLImplMDLInstance` object if this node is a native MDL instance, None otherwise.
        """
        return self.mMDLImplementation.mImplMDLInstance if self.isMDLInstance() else None

    @handle_exceptions()
    def getMDLImplMDLGraphInstance(self):
        """
        getMDLImplMDLGraphInstance()

        :return: the :class:`.MDLImplMDLGraphInstance` object if this node is a MDL graph instance, None otherwise.
        """
        return self.mMDLImplementation.mImplMDLGraphInstance if self.isMDLGraphInstance() else None

    @handle_exceptions()
    def getMDLImplSBSInstance(self):
        """
        getMDLImplSBSInstance()

        :return: the :class:`.MDLImplSBSInstance` object if this node is a Substance graph instance, None otherwise.
        """
        return self.mMDLImplementation.mImplSBSInstance if self.isSBSInstance() else None

    @handle_exceptions()
    def getMDLImplementation(self):
        """
        getMDLImplementation(self)
        Get the appropriate implementation depending on the MDL node kind

        :return: A :class:`.MDLNodeImpl` object
        """
        return self.mMDLImplementation.getImplementation() if self.mMDLImplementation is not None else None

    @handle_exceptions()
    def getDefinition(self):
        """
        getDefinition()
        Get the node definition (Inputs, Outputs, Parameters) accordingly to the MDL node implementation

        :return: a :class:`.MDLNodeDef` object if defined, None otherwise
        """
        impl = self.getMDLImplementation()
        return impl.getDefinition() if impl is not None else None

    @handle_exceptions()
    def getDisplayName(self):
        """
        getDisplayName()

        :return: the display name of this node as a string
        """
        impl = self.getMDLImplementation()
        return impl.getDisplayName() if impl is not None else self.mUID

    @handle_exceptions()
    def getParameter(self, aParameter=None):
        """
        getParameter(aParameter=None)
        Get a parameter with the given name in the appropriate MDL node implementation.
        The parameter can be:
        - None in case of a Constant or Selector node, where there is only one parameter.
        - Simply the name of the parameter to get
        - A set of names separated by '/' to access a sub member of the root member, for instance 'surface/intensity'
        - A name with an operator [] to access a particular item of a parameter array, for instance 'color[2]'

        :param aParameter: Parameter identifier (name of the operand). Can be None in case of a MDLImplConstant or a MDLImplSelector
        :type aParameter: str, optional
        :return: The parameter if found (:class:`.MDLParameter` or :class:`.MDLOperand`), None otherwise
        """
        impl = self.getMDLImplementation()
        return impl.getParameter(aParameter) if impl is not None else None

    @handle_exceptions()
    def getParameterValue(self, aParameter=None):
        """
        getParameterValue(aParameter=None)
        Find a parameter with the given name in the appropriate MDL node implementation, and return its value.
        The parameter can be:
        - None in case of a Constant or Selector node, where there is only one parameter.
        - Simply the name of the parameter to get
        - A set of names separated by '/' to access a sub member of the root member, for instance 'surface/intensity'
        - A name with an operator [] to access a particular item of a parameter array, for instance 'color[2]'

        :param aParameter: Parameter identifier (name of the operand). Can be None in case of a MDLImplConstant or a MDLImplSelector
        :type aParameter: str, optional
        :return: The parameter value if found, None otherwise
        """
        impl = self.getMDLImplementation()
        return impl.getParameterValue(aParameter) if impl is not None else None

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        """
        setParameterValue(aParameter, aParamValue)
        Set the parameter to the appropriate MDL node implementation
        The parameter can be:
        - Simply the name of the parameter to set
        - A set of names separated by '/' to access a sub member of the root member, for instance 'surface/intensity'
        - A name with an operator [] to access a particular item of a parameter array, for instance 'color[2]'

        :param aParameter: identifier of the parameter to set
        :param aParamValue: value of the parameter
        :type aParameter: str
        :type aParamValue: any parameter type
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError` if the node has no implementation
        """
        impl = self.getMDLImplementation()
        if not impl:
            raise SBSImpossibleActionError('Cannot set a parameter to the node '+self.mUID+', no implementation found')
        return impl.setParameterValue(aParameter, aParamValue)

    @handle_exceptions()
    def setPinVisibilityForParameter(self, aParameter, aVisible):
        """
        setPinVisibilityForParameter(aParameter, aVisible)
        Set the visibility of the input pin associated to the given parameter.
        Only available for MDL instances and MDL Graph instances

        :param aParameter: The parameter to edit
        :type aParameter: str
        :param aVisible: The visibility to set
        :type aVisible: bool
        :raise: :class:`.SBSImpossibleActionError`
        """
        impl = self.getMDLImplementation()
        if not impl:
            raise SBSImpossibleActionError('Cannot change pin visibility of node '+self.mUID+', no implementation found')
        if not self.isMDLInstance() and not self.isMDLGraphInstance():
            raise SBSImpossibleActionError('Cannot change pin visibility of the node '+self.mUID+', it must be a native mdl instance or a mdl graph instance')

        aParam = impl.getParameter(aParameter)
        if aParam is None:
            raise SBSImpossibleActionError('Cannot change pin visibility of the node '+self.mUID+', the parameter '+
                                           python_helpers.castStr(aParameter)+' is not available')

        aParam.setConnectionAccepted(aVisible)
        if not aVisible:
            self.removeConnectionOnPin(aPinIdentifier=aParam.mName)


    @handle_exceptions()
    def resetParameter(self, aParameter=None):
        """
        resetParameter(aParameter=None)
        Reset the given parameter to its default value.
        The parameter can be:
        - None in case of a Constant or Selector node, where there is only one parameter.
        - Simply the name of the parameter to get
        - A set of names separated by '/' to access a sub member of the root member, for instance 'surface/intensity'
        - A name with an operator [] to access a particular item of a parameter array, for instance 'color[2]'

        :param aParameter: identifier of the parameter to set
        :type aParameter: str, optional
        :return: True if succeed, False otherwise
        :raise: :class:`.SBSImpossibleActionError` if the node has no implementation
        """
        impl = self.getMDLImplementation()
        if not impl:
            raise SBSImpossibleActionError('Cannot unset a parameter to the node '+self.mUID+', no implementation found')
        return impl.resetParameter(aParameter)

    @handle_exceptions()
    def getResourcesPath(self):
        """
        getResourcesPath()
        If this node uses resources in its parameters, returns the list of resources used.

        :return: The list of resources used by this node, as internal paths. Return an empty list otherwise.
        """
        resources = []
        nodeDef = self.getDefinition()
        for aParam in nodeDef.getAllParameters():
            typeDef = MDLManager.getMDLTypeDefinition(aParam.getType())
            if typeDef and (typeDef.isResource() or typeDef.isString()):
                value = self.getParameterValue(aParam.mName)
                if value and python_helpers.isStringOrUnicode(value) and \
                        api_helpers.hasPkgPrefix(value) and value not in resources:
                    resources.append(value)
        return resources

    @handle_exceptions()
    def changeDependencyUID(self, aSBSDocument, oldDepUID, newDepUID):
        """
        changeDependencyUID(aSBSDocument, oldDepUID, newDepUID)
        Change the UID of the dependency referenced by this node.

        :param aSBSDocument: The root document, required to reset all the internal links to the referenced graph
        :type aSBSDocument: :class:`.SBSDocument`
        :param oldDepUID: The new dependency UID
        :param newDepUID: The previous dependency UID
        :type oldDepUID: str
        :type newDepUID: str
        """
        if self.isSBSInstance() or self.isMDLGraphInstance():
            self.getMDLImplementation().changeDependencyUID(aSBSDocument, newDepUID)

        for aPath in self.getResourcesPath():
            if aPath.endswith(oldDepUID):
                newPath = aPath.replace(oldDepUID, newDepUID)
                self.changeResourcePath(aPath, newPath)

    @handle_exceptions()
    def changeResourcePath(self, oldPath, newPath):
        """
        changeResourcePath(oldPath, newPath)
        Change the referenced resource path.

        :param oldPath: The old resource path
        :param newPath: The new resource path
        :type oldPath: str
        :type newPath: str
        """
        nodeDef = self.getDefinition()
        for aParam in nodeDef.getAllParameters():
            typeDef = MDLManager.getMDLTypeDefinition(aParam.getType())
            if typeDef and (typeDef.isResource() or typeDef.isString()):
                if self.getParameterValue(aParam.mName) == oldPath:
                    self.setParameterValue(aParam.mName, newPath)

    @handle_exceptions()
    def hasAReferenceOnDependency(self, aDependency):
        aUID = aDependency if python_helpers.isStringOrUnicode(aDependency) else aDependency.mUID

        # Instance of SBSGraph or MDLGraph => Check the dependency
        if self.isSBSInstance() or self.isMDLGraphInstance():
            if self.getMDLImplementation().getDependencyUID() == aUID:
                return True

        # Resources
        for aPath in self.getResourcesPath():
            if api_helpers.splitPathAndDependencyUID(aPath)[1] == aUID:
                return True
        return False

    @handle_exceptions()
    def hasAReferenceOnInternalPath(self, aInternalPath):
        if self.isSBSInstance() or self.isMDLGraphInstance():
            if self.getMDLImplementation().getReferenceInternalPath()== aInternalPath:
                return True
        return self.useResource(aInternalPath)

    @handle_exceptions()
    def useResource(self, aResourcePath):
        """
        useResource(aResourcePath)

        :return: True if the node uses the given resource (bsdf measurement, ies profile or texture), False otherwise.
        """
        resourceUsed = self.getResourcesPath()
        return aResourcePath in resourceUsed
