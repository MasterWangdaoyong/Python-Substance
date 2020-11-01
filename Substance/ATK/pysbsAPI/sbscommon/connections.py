# coding: utf-8
"""
Module **connections** provides the definition of the classes :class:`.SBSConnection` and :class:`.SBSConnectionSplitpoint`,
which define the connection between two nodes (compositing nodes, function nodes or FxMap nodes)
"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.common_interfaces import SBSObject


# =======================================================================
@doc_inherit
class SBSConnection(SBSObject):
    """
    Class that contains information on a connection as defined in a .sbs file

    Members:
        * mIdentifier    (str): input identifier. Among :attr:`sbslibrary.__dict_CompNodeInputs`, :attr:`sbslibrary.__dict_FunctionInputs` or free string.
        * mEntry         (str, deprecated): entry identifier, specific to SBSCompNode type.
        * mConnRef       (str): uid of the node (/compNode/uid) connected to this input.
        * mConnRefOutput (str, optional): uid of the output of the node connected to this input (/compNode/compOutputs/compOutput/uid). Present only if the node has multiple outputs.
        * mSplitpoints   (list of :class:`.SBSConnectionSplitpoint`): splitpoint list.
    """
    def __init__(self,
                 aIdentifier    = '',
                 aEntry         = None,
                 aConnRef       = None,
                 aConnRefOutput = None,
                 aSplitpoints   = None):
        super(SBSConnection, self).__init__()
        self.mIdentifier    = aIdentifier
        self.mEntry         = aEntry
        self.mConnRef       = aConnRef
        self.mConnRefOutput = aConnRefOutput
        self.mSplitpoints   = aSplitpoints

        self.mMembersForEquality = ['mIdentifier',
                                    'mEntry',
                                    'mConnRef',
                                    'mConnRefOutput']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier    = aSBSParser.getXmlElementVAttribValue(aXmlNode               , 'identifier'   )
        self.mEntry         = aSBSParser.getXmlElementVAttribValue(aXmlNode               , 'entry'        )
        self.mConnRef       = aSBSParser.getXmlElementVAttribValue(aXmlNode               , 'connRef'      )
        self.mConnRefOutput = aSBSParser.getXmlElementVAttribValue(aXmlNode               , 'connRefOutput')
        self.mSplitpoints   = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'splitpoints'  , 'splitpoint', SBSConnectionSplitpoint)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIdentifier     , 'identifier'      )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mEntry          , 'entry'           )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mConnRef        , 'connRef'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mConnRefOutput  , 'connRefOutput'   )
        aSBSWriter.writeListOfSBSNode(aXmlNode       ,  self.mSplitpoints    , 'splitpoints'     , 'splitpoint'  )

    @handle_exceptions()
    def getConnectedNodeUID(self):
        """
        getConnectedNodeUID()
        Get the UID of the connected node (member mConnRef).

        :return: The UID as a string if defined, None otherwise.
        """
        return self.mConnRef

    @handle_exceptions()
    def getConnectedNodeOutputUID(self):
        """
        getConnectedNodeOutputUID()
        Get the UID of the connected output (member mConnRefOutput).

        :return: The UID as a string if defined, None otherwise.
        """
        return self.mConnRefOutput

    @handle_exceptions()
    def setConnection(self, aConnRefValue, aConnRefOutputValue = None):
        """
        setConnection(aConnRefValue, aConnRefOutputValue = None)
        Set the connection.

        :param aConnRefValue: The UID of node to connect from
        :param aConnRefOutputValue: The UID of the output of this node to connect. Can be None if the node has only one output.
        :type aConnRefValue: str
        :type aConnRefOutputValue: str, optional
        """
        self.mConnRef = aConnRefValue
        if aConnRefOutputValue is not None:
            self.mConnRefOutput = aConnRefOutputValue



# =======================================================================
@doc_inherit
class SBSConnectionSplitpoint(SBSObject):
    """
    Class that contains information on a splitpoint of a connection as defined in a .sbs file

    Members:
        * mScenePos (str): splitpoint scene position.
    """

    def __init__(self, aScenePos=''):
        super(SBSConnectionSplitpoint, self).__init__()
        self.mScenePos = aScenePos

        self.mMembersForEquality = ['mScenePos']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mScenePos = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'scenepos')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mScenePos, 'scenepos')
