# coding: utf-8
from __future__ import unicode_literals
import copy

from pysbs.api_decorators import handle_exceptions


@handle_exceptions()
def cleanUnusedDependencies(aSBSDocument):
    """
    cleanUnusedDependencies(aSBSDocument)
    Remove all the unused dependencies in the given package.

    :param aSBSDocument: the substance to clean
    :type aSBSDocument: :class:`.SBSDocument`
    """
    depList = aSBSDocument.getSBSDependencyList(aIncludeHimself=True)
    for aDependency in depList:
        if not aSBSDocument.getAllReferencesOnDependency(aDependency=aDependency):
            aSBSDocument.removeDependency(aDependency=aDependency, aCheckUsage=False)

@handle_exceptions()
def cleanUselessNodesInDynamicValue(aDynamicValue):
    """
    cleanUselessNodesInDynamicValue(aDynamicValue)
    Delete all the useless nodes in the given dynamic value, meaning the ones that are not connected to the output node.

    :param aDynamicValue: the graph to clean
    :type aDynamicValue: :class:`.SBSDynamicValue`
    """
    uselessNodes = getUselessNodesInDynamicValue(aDynamicValue)
    for aNode in uselessNodes:
        aDynamicValue.deleteNode(aNode)

@handle_exceptions()
def cleanUselessNodesInFunction(aFunction):
    """
    cleanUselessNodesInFunction(aFunction)
    Delete all the useless nodes in the given function, meaning the ones that are not connected to the output node.

    :param aFunction: the graph to clean
    :type aFunction: :class:`.SBSFunction`
    """
    uselessNodes = getUselessNodesInFunction(aFunction)
    for aNode in uselessNodes:
        aFunction.deleteNode(aNode)

@handle_exceptions()
def cleanUselessNodesInGraph(aGraph):
    """
    cleanUselessNodesInGraph(aGraph)
    Delete all the useless nodes in the given graph, meaning the ones that are not connected to an output.

    :param aGraph: the graph to clean
    :type aGraph: :class:`.SBSGraph`
    """
    uselessNodes = getUselessNodesInGraph(aGraph)
    for aNode in uselessNodes:
        aGraph.deleteNode(aNode)

@handle_exceptions()
def cleanUselessNodesInMDLGraph(aGraph):
    """
    cleanUselessNodesInMDLGraph(aGraph)
    Delete all the useless nodes in the given MDL graph, meaning the ones that are not connected to an output.

    :param aGraph: the graph to clean
    :type aGraph: :class:`.MDLGraph`
    """
    uselessNodes = getUselessNodesInMDLGraph(aGraph)
    for aNode in uselessNodes:
        aGraph.deleteNode(aNode)

@handle_exceptions()
def cleanUselessParametersInFunction(aFunction):
    """
    cleanUselessParametersInFunction(aFunction)
    Delete all the useless input parameters in the given function, meaning the ones that are not used by the dynamic function or a VisibleIf condition.

    :param aFunction: the graph to clean
    :type aFunction: :class:`.SBSFunction`
    """
    uselessParams = getUselessParametersInFunction(aFunction)
    for aParam in uselessParams:
        aFunction.deleteInputParameter(aParam)

@handle_exceptions()
def cleanUselessParametersInGraph(aGraph):
    """
    cleanUselessParametersInGraph(aGraph)
    Delete all the useless input parameters in the given graph, meaning the ones that are not used by a dynamic function or a VisibleIf condition.

    :param aGraph: the graph to clean
    :type aGraph: :class:`.SBSGraph`
    """
    uselessParams = getUselessParametersInGraph(aGraph)
    for aParam in uselessParams:
        aGraph.deleteInputParameter(aParam)

@handle_exceptions()
def cleanSubstance(aSBSDocument, aCleanGraphNodes = True,
                                 aCleanFunctionNodes = True,
                                 aCleanGraphParameters = True,
                                 aCleanFunctionParameters = True,
                                 aCleanUnusedDependencies = True):
    """
    cleanSubstance(aSBSDocument, aCleanGraphNodes = True, aCleanFunctionNodes = True, aCleanGraphParameters = True, aCleanFunctionParameters = True)
    Global clean function, that allows to clean:
     - Clean the useless compositing nodes in the graphs (Substance and MDL)
     - Clean the useless function nodes in the functions and all dynamic values (dynamic nodes parameters, pixel processor function)
     - Clean the useless graph input parameters
     - Clean the useless function input parameters
     - Clean the dependencies unused in the package

    :param aSBSDocument: the substance to clean
    :param aCleanGraphNodes: True to clean the useless compositing nodes in the substance graphs. Default to True
    :param aCleanFunctionNodes: True to clean the useless function nodes in the functions. Default to True
    :param aCleanGraphParameters: True to clean the useless compositing nodes in the substance graphs. Default to True
    :param aCleanFunctionParameters: True to clean the useless compositing nodes in the substance graphs. Default to True
    :param aCleanUnusedDependencies: True to clean the dependencies unused in the package. Default to True
    :type aSBSDocument: :class:`.SBSDocument`
    :type aCleanGraphNodes: bool, optional
    :type aCleanFunctionNodes: bool, optional
    :type aCleanGraphParameters: bool, optional
    :type aCleanFunctionParameters: bool, optional
    :type aCleanUnusedDependencies: bool, optional
    """
    def cleanDynamicValuesOfNode(node):
        for nodeParam in node.getDynamicParameters():
            cleanUselessNodesInDynamicValue(nodeParam.getDynamicValue())

    aGraphs = aSBSDocument.getSBSGraphList()
    aMDLGraphs = aSBSDocument.getMDLGraphList()
    aFunctions = aSBSDocument.getSBSFunctionList()

    # Clean compositing graph nodes
    if aCleanGraphNodes:
        for aGraph in aGraphs:
            cleanUselessNodesInGraph(aGraph)
        for aGraph in aMDLGraphs:
            cleanUselessNodesInMDLGraph(aGraph)


    # Clean function and dynamic values nodes
    if aCleanFunctionNodes:
        for aFunction in aFunctions:
            cleanUselessNodesInFunction(aFunction)

        for aGraph in aGraphs:
            for aNode in aGraph.getNodeList():
                cleanDynamicValuesOfNode(aNode)

                if aNode.isAFxMap():
                    aFxMapGraph = aNode.getFxMapGraph()
                    if aFxMapGraph is not None:
                        for aFxNode in aFxMapGraph.getNodeList():
                            cleanDynamicValuesOfNode(aFxNode)

    # Clean graph parameters
    if aCleanGraphParameters:
        for aGraph in aGraphs:
            cleanUselessParametersInGraph(aGraph)

    # Clean input parameters
    if aCleanFunctionParameters:
        for aFunction in aFunctions:
            cleanUselessParametersInFunction(aFunction)

    # Clean unused dependencies
    if aCleanUnusedDependencies:
        cleanUnusedDependencies(aSBSDocument)


@handle_exceptions()
def getUselessNodesInFunction(aFunction):
    """
    getUselessNodesInFunction(aFunction)
    Get all the useless nodes in the given function, meaning the ones that are not connected to the output node.

    :param aFunction: the graph to clean
    :type aFunction: :class:`.SBSFunction`
    :return: the list of useless :class:`.SBSParamNode`
    """
    aDynValue = aFunction.getDynamicValue()
    return getUselessNodesInDynamicValue(aDynValue) if aDynValue is not None else []

@handle_exceptions()
def getUselessNodesInDynamicValue(aDynamicValue):
    """
    getUselessNodesInDynamicValue(aDynamicValue)
    Get all the useless nodes in the given dynamic value, meaning the ones that are not connected to the output node.

    :param aDynamicValue: the dynamic value to clean
    :type aDynamicValue: :class:`.SBSDynamicValue`
    :return: the list of useless :class:`.SBSParamNode`
    """
    aUselessNodes = set(aDynamicValue.getNodeList())
    aOutput = aDynamicValue.getOutputNode()
    if aOutput:
        __removeConnectedNodesFromList(aDynamicValue, aUselessNodes, aOutput)
        aUselessNodes.remove(aOutput)
    return aUselessNodes

@handle_exceptions()
def getUselessNodesInGraph(aGraph):
    """
    getUselessNodesInGraph(aGraph)
    Get all the useless nodes in the given graph, meaning the ones that are not connected to an output.

    :param aGraph: the graph to clean
    :type aGraph: :class:`.SBSGraph`
    :return: the list of useless :class:`.SBSCompNode`
    """
    aUselessNodes = set(aGraph.getNodeList())
    aOutputNodes = aGraph.getAllOutputNodes()
    for aOutput in aOutputNodes:
        __removeConnectedNodesFromList(aGraph, aUselessNodes, aOutput)
        aUselessNodes.remove(aOutput)
    aInputNodes = aGraph.getAllInputNodes()
    for aInput in aInputNodes:
        if aInput in aUselessNodes:
            aUselessNodes.remove(aInput)
    return aUselessNodes

@handle_exceptions()
def getUselessNodesInMDLGraph(aGraph):
    """
    getUselessNodesInMDLGraph(aGraph)
    Get all the useless nodes in the given MDL graph, meaning the ones that are not connected to the output.

    :param aGraph: the graph to clean
    :type aGraph: :class:`.MDLGraph`
    :return: the list of useless :class:`.MDLNode`
    """
    aUselessNodes = set(aGraph.getNodeList())
    aOutputNode = aGraph.getGraphOutputNode()
    if aOutputNode:
        __removeConnectedNodesFromList(aGraph, aUselessNodes, aOutputNode)
        aUselessNodes.remove(aOutputNode)
    return aUselessNodes

@handle_exceptions()
def getUselessParametersInFunction(aFunction):
    """
    getUselessParametersInFunction(aFunction)
    Get all the useless input parameters in the given function, meaning the ones that are not used by the function graph.

    :param aFunction: the function to clean
    :type aFunction: :class:`.SBSFunction`
    :return: the list of useless :class:`.SBSParamInput`
    """
    aInputParamList = aFunction.getInputParameters()
    if not aFunction.getDynamicValue():
        return aInputParamList

    aUsedParams = aFunction.getDynamicValue().getUsedParameters(aInputParamList)
    aUselessInputParamList = list(set(aInputParamList) - set(aUsedParams))

    return aUselessInputParamList

@handle_exceptions()
def getUselessParametersInGraph(aGraph):
    """
    getUselessParametersInGraph(aGraph)
    Get all the useless input parameters in the given graph, meaning the ones that are not used by a dynamic function or a VisibleIf condition.

    :param aGraph: the graph to clean
    :type aGraph: :class:`.SBSGraph`
    :return: the list of useless :class:`.SBSParamInput`
    """
    def getUsedParametersInNode(node, parameters):
        usedParamsInNode = []
        for nodeParam in node.getDynamicParameters():
            usedParams = nodeParam.getDynamicValue().getUsedParameters(parameters)
            usedParamsInNode = list(set().union(usedParamsInNode, usedParams))
        return usedParamsInNode

    aInputParamList = aGraph.getInputParameters()
    aUselessInputParamList = copy.copy(aInputParamList)

    # Look for parameters used in the dynamic parameters of nodes of the graph
    for aNode in aGraph.getNodeList():
        aUsedParams = getUsedParametersInNode(aNode, aUselessInputParamList)
        aUselessInputParamList = list(set(aUselessInputParamList) - set(aUsedParams))

        if aNode.isAFxMap():
            aFxMapGraph = aNode.getFxMapGraph()
            for aFxNode in aFxMapGraph.getNodeList():
                aUsedParams = getUsedParametersInNode(aFxNode, aUselessInputParamList)
                aUselessInputParamList = list(set(aUselessInputParamList) - set(aUsedParams))

        if not aUselessInputParamList:
            break

    # Look for parameters used in the visible if expression of the input parameters graph
    aParamListForVisibleIfCheck = list((set(aInputParamList) | set(aGraph.getInputImages())) - set(aUselessInputParamList))
    aVisibleIfParams = __getParamsInVisibleIfExpression(aGraph, aParamListForVisibleIfCheck)
    aUselessInputParamList = list(set(aUselessInputParamList) - set(aVisibleIfParams))
    return aUselessInputParamList



@handle_exceptions()
def __removeConnectedNodesFromList(aGraph, aNodeList, aNodeStart):
    """
    __removeConnectedNodesFromList(aGraph, aNodeList, aNodeStart):
    :param aGraph:
    :param aNodeList:
    :param aNodeStart:
    :return:
    """
    for aConn in aNodeStart.getConnections():
        aNode = aGraph.getNode(aConn.getConnectedNodeUID())
        if aNode in aNodeList:
            aNodeList.remove(aNode)
            __removeConnectedNodesFromList(aGraph, aNodeList, aNode)

@handle_exceptions()
def __getParamsInVisibleIfExpression(aGraph, aParameters):
    """
    __getParamsInVisibleIfExpression(aGraph, aParameters)
    Parse the visible if expression of the given parameters to find the input parameters that are referenced.

    :param aGraph: compositing graph or function graph
    :param aParameters: the input parameters to look for
    :type aGraph: :class:`.SBSGraph` or :class:`.SBSFunction`
    :type aParameters: list of :class:`.SBSParamInput`
    :return: the list of :class:`.SBSParamInput` used in the visible if expression and defined in the given graph
    """
    aVisibleIfParams = []
    for aInputParam in aParameters:
        if aInputParam.mVisibleIf is not None:
            aVisibleIfParams.extend(aGraph.getInputParametersInVisibleIfExpression(aInputParam.mVisibleIf))
    return aVisibleIfParams
