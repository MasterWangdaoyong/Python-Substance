# coding: utf-8
"""
| Module **graph.output** provides the definition of the classes related to the compositing graph output:
| - :class:`.SBSGraphOutput`
| - :class:`.SBSRootOutput`
| - :class:`.SBSRoot`
| - :class:`.SBSUsage`
"""
from __future__ import unicode_literals
from pysbs.api_decorators import doc_inherit,handle_exceptions,deprecated
from pysbs.common_interfaces import SBSObject, GraphOutput
from pysbs import api_helpers
from pysbs import sbsenum
from pysbs import sbscommon
from pysbs import sbslibrary


# ==============================================================================
@doc_inherit
class SBSUsage(SBSObject):
    """
    Class that contains information on a usage as defined in a .sbs file

    Members:
        * mComponents (str): combination of RGBA, among the list defined in :attr:`sbslibrary.__dict_CommonUsageComponents`
        * mName       (str): usage hint, among the list defined in :attr:`sbslibrary.__dict_CommonUsages`.
        * mColorSpace (str): color space, custom  string or a member from the list defined in :attr:`sbslibrary.__dict_CommonColorSpaces`
    """
    def __init__(self,
                 aComponents = '',
                 aName       = '',
                 aColorSpace = None):
        super(SBSUsage, self).__init__()
        self.mComponents = aComponents
        self.mName       = aName
        self.mColorSpace = aColorSpace

        self.mMembersForEquality = ['mComponents',
                                    'mName',
                                    'mColorSpace']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mComponents = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'components')
        self.mName       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name')
        self.mColorSpace = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'colorspace')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mComponents,  'components')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName      ,  'name')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mColorSpace, 'colorspace')



# ==============================================================================
@doc_inherit
class SBSGraphOutput(SBSObject, GraphOutput):
    """
    Class that contains information on a graph output of a graph, as defined in a .sbs file

    Members:
        * mIdentifier (str): identifier of this output.
        * mUID        (str): unique identifier in the /graph/ context.
        * mAttributes (:class:`.SBSAttributes`): various attributes
        * mDisabled   (str, optional): this output is disabled ("1" / None)
        * mVisibleIf  (str, optional): string bool expression based on graph inputs values
        * mUsages     (list of :class:`.SBSUsage`, optional): usages of this output
        * mChannels   (str, optional): channels defined (RGBA, RGB, Grayscale)
        * mGroup      (str, optional): string that contains a group name. Can uses path with '/' separators.
    """
    __sAttributes = [sbsenum.AttributesEnum.Description, sbsenum.AttributesEnum.Label]

    def __init__(self,
                 aIdentifier = '',
                 aUID        = '',
                 aAttributes = None,
                 aUsages     = None,
                 aChannels   = None,
                 aDisabled   = None,
                 aGroup      = None,
                 aVisibleIf  = None):
        SBSObject.__init__(self)
        GraphOutput.__init__(self, aUID, aIdentifier)
        self.mAttributes = aAttributes
        self.mDisabled   = aDisabled
        self.mVisibleIf  = aVisibleIf
        self.mUsages     = aUsages
        self.mChannels   = aChannels
        self.mGroup      = aGroup

        self.mMembersForEquality = ['mIdentifier',
                                    'mAttributes',
                                    'mDisabled',
                                    'mVisibleIf',
                                    'mUsages',
                                    'mChannels',
                                    'mGroup']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'identifier')
        self.mUID        = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'       )
        self.mAttributes = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'attributes', sbscommon.SBSAttributes)
        self.mDisabled   = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'disabled'  )
        self.mUsages     = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'usages'    , 'usage', SBSUsage)
        self.mChannels   = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'channels'  )
        self.mGroup      = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'group'     )
        self.mVisibleIf  = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'visibleIf' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIdentifier    , 'identifier'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUID           , 'uid'         )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mAttributes    , 'attributes'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mDisabled      , 'disabled'    )
        aSBSWriter.writeListOfSBSNode(aXmlNode,         self.mUsages        , 'usages'      , 'usage')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mChannels      , 'channels'    )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mGroup         , 'group'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mVisibleIf     , 'visibleIf'   )

    @handle_exceptions()
    def getAllowedAttributes(self):
        """
        getAllowedAttributes()
        Get the attributes allowed on a SBSGraphOutput

        :return: the list of attribute enumeration allowed (:class:`.AttributesEnum`)
        """
        return SBSGraphOutput.__sAttributes

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

    @deprecated(__name__, '2019.1.0', 'Renamed for consistency with SBSParamInput.getType()', 'Please use getType instead')
    def getOutputChannel(self):
        """
        getOutputChannel()
        Get the output channel

        :return: the output channels of this graph output, as a :class:`.ParamTypeEnum`
        """
        return self.getType()

    def getType(self):
        """
        getType()
        Get the output type of this GraphOutput.

        :return: the output type in the format :class:`.ParamTypeEnum` if found, None otherwise
        """
        if self.mChannels is None:
            return sbsenum.ParamTypeEnum.ENTRY_COLOR
        else:
            return int(self.mChannels)

    def getUsages(self):
        """
        getUsages()
        Get the usages of this output

        :return: the list of :class:`.SBSUsage` defined on this output
        """
        return self.mUsages if self.mUsages is not None else []

    @handle_exceptions()
    def hasUsage(self, aUsage):
        """
        hasUsage(aUsage)
        Check if the given usage is defined on this output

        :param aUsage: The usage to look for
        :type aUsage: str or :class:`.UsageEnum`
        :return: True if the given usage is defined on this output, False otherwise
        """
        if isinstance(aUsage, int):
            aUsage = sbslibrary.getUsage(aUsage)
        return next((True for usage in self.getUsages() if aUsage == usage.mName), False)

    @handle_exceptions()
    def addUsage(self, aUsage, aComponents = sbsenum.ComponentsEnum.RGBA):
        """
        addUsage(aUsage, aComponents = sbsenum.ComponentsEnum.RGBA)
        Add the given usage on this output

        :param aUsage: The usage to set
        :param aComponents: The components associated to this usage. Default to sbsenum.ComponentsEnum.RGBA
        :type aUsage: str or :class:`.UsageEnum`
        :type aComponents: :class:`.ComponentsEnum`, optional
        :return: the create :class:`.SBSUsage` object
        """
        if isinstance(aUsage, int):
            aUsage = sbslibrary.getUsage(aUsage)
        aUsage = SBSUsage(aComponents = aComponents, aName = aUsage)
        api_helpers.addObjectToList(self, 'mUsages', aUsage)



#=======================================================================
@doc_inherit
class SBSRootOutput(SBSObject):
    """
    Class that contains information on the root output of a graph as defined in a .sbs file

    Members:
        * mOutput        (str): uid of the graph output.
        * mFormat        (str, optional): texture format of the output.
        * mMipmaps       (str, optional): Depth of the output, 0: full mipmaps pyramid
        * mUserTag       (str): user information useful for the 3D engine using the substance engine (UNICODE string) (e.g. filepath and texture name).
        * mDisabled      (str, optional): this output is disabled ("1" / None)
        * mStreamingInfo (str, optional): streaming information
    """
    def __init__(self,
                 aOutput        = '',
                 aFormat        = None,
                 aMipmaps       = None,
                 aUserTag       = '',
                 aDisabled      = None,
                 aStreamingInfo = None):
        super(SBSRootOutput, self).__init__()
        self.mOutput        = aOutput
        self.mFormat        = aFormat
        self.mMipmaps       = aMipmaps
        self.mUserTag       = aUserTag
        self.mDisabled      = aDisabled
        self.mStreamingInfo = aStreamingInfo

        self.mMembersForEquality = ['mFormat',
                                    'mMipmaps',
                                    'mUserTag',
                                    'mDisabled',
                                    'mStreamingInfo']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mOutput        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'output'        )
        self.mFormat        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'format'        )
        self.mMipmaps       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'mipmaps'       )
        self.mUserTag       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'usertag'       )
        self.mDisabled      = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'disabled'      )
        self.mStreamingInfo = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'streamingInfo' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mOutput        , 'output'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mFormat        , 'format'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mMipmaps       , 'mipmaps'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUserTag       , 'usertag'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mDisabled      , 'disabled'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mStreamingInfo , 'streamingInfo'   )



#=======================================================================
@doc_inherit
class SBSRoot(SBSObject):
    """
    Class that contains information on the root graph as defined in a .sbs file
    Root graphs outputs are directly computed at runtime, cooking always needed.

    Members:
        * mDisabled      (str, optional): this root is disabled ("1" / None)
        * mRootOutputs   (list of :class:`.SBSRootOutput`): options of the outputs of this root.
    """
    def __init__(self,
                 aDisabled    = None,
                 aRootOutputs = None):
        super(SBSRoot, self).__init__()
        self.mDisabled      = aDisabled
        self.mRootOutputs   = aRootOutputs

        self.mMembersForEquality = ['mDisabled',
                                    'mRootOutputs']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mDisabled    = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'disabled')
        self.mRootOutputs = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'rootOutputs', 'rootOutput', SBSRootOutput)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDisabled, 'disabled'    )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mRootOutputs,     'rootOutputs' , 'rootOutput')

    @handle_exceptions()
    def getRootOutput(self, aOutputUID):
        """
        getRootOutput(aOutputUID)
        Get the SBSRootOutput with the given UID

        :param aOutputUID: the uid of the output to remove in the list of root outputs
        :type aOutputUID: str
        :return: a :class:`.SBSRootOutput` if found, None otherwise
        """
        return next((o for o in self.mRootOutputs if o.mOutput == aOutputUID), None) if self.mRootOutputs else None

    @handle_exceptions()
    def deleteRootOutput(self, aOutputUID):
        """
        deleteRootOutput(aOutputUID)
        Delete the SBSRootOutput with the given UID

        :param aOutputUID: the uid of the output to remove in the list of root outputs
        :type aOutputUID: str
        """
        aRootOutput = self.getRootOutput(aOutputUID)
        if aRootOutput:
            self.mRootOutputs.remove(aRootOutput)
