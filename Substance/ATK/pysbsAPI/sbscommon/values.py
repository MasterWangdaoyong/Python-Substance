# coding: utf-8
"""
Module **values** provides the definition of the classes relative to the value of parameters in the .sbs file:
- :class:`.SBSConstantValue`
- :class:`.SBSOption`
- :class:`.SBSIcon`
- :class:`.SBSAttributes`

"""

from __future__ import unicode_literals
from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject
from pysbs import api_helpers, python_helpers
from pysbs import sbsenum
from collections import OrderedDict
import xml.etree.ElementTree as ET

# ==============================================================================
@doc_inherit
class SBSConstantValue(SBSObject):
    """
    Class that contains information on a constant value as defined in a .sbs file

    Members:
        * mConstantValue (str): simple constant definition of a parameter.
        * mTagName       (str): the tag name in the .sbs file, in the format 'constantvalue<type>'
    """

    def __init__(self,
                 aConstantValue=None,
                 aTagName=''):
        super(SBSConstantValue, self).__init__()
        self.mConstantValue = aConstantValue
        self.mTagName = aTagName

        self.mMembersForEquality = ['mConstantValue',
                                    'mTagName']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        aChildren = list(aXmlNode)
        if aChildren is None:
            return

        aElt = aChildren[0]
        if aElt is None:
            return

        self.mTagName = aElt.tag
        if 'constantValue' in self.mTagName:
            self.mConstantValue = aSBSParser.getXmlElementVAttribValue(aXmlNode, self.mTagName)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        if 'constantValue' in self.mTagName:
            aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mConstantValue, self.mTagName)

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Get the value of this constant value.

        :return: The value as a string if defined, None otherwise
        """
        return self.mConstantValue if 'constantValue' in self.mTagName else None

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Get the type of this constant value

        :return: The type as a :class:`.ParamTypeEnum` if success, None otherwise
        """
        if   self.mTagName.endswith('Bool'):            return sbsenum.ParamTypeEnum.BOOLEAN
        elif self.mTagName.endswith('Int1'):            return sbsenum.ParamTypeEnum.INTEGER1
        elif self.mTagName.endswith('Int32'):           return sbsenum.ParamTypeEnum.INTEGER1
        elif self.mTagName.endswith('Int2'):            return sbsenum.ParamTypeEnum.INTEGER2
        elif self.mTagName.endswith('Int3'):            return sbsenum.ParamTypeEnum.INTEGER3
        elif self.mTagName.endswith('Int4'):            return sbsenum.ParamTypeEnum.INTEGER4
        elif self.mTagName.endswith('Float1'):          return sbsenum.ParamTypeEnum.FLOAT1
        elif self.mTagName.endswith('Float2'):          return sbsenum.ParamTypeEnum.FLOAT2
        elif self.mTagName.endswith('Float3'):          return sbsenum.ParamTypeEnum.FLOAT3
        elif self.mTagName.endswith('Float4'):          return sbsenum.ParamTypeEnum.FLOAT4
        elif self.mTagName.endswith('String'):          return sbsenum.ParamTypeEnum.STRING
        return None

    @handle_exceptions()
    def setConstantValue(self, aType, aValue, aInt1=False):
        """
        setConstantValue(aType, aValue, aInt1 = False)
        Set the constant value to the given value, and set the tagname accordingly to the type of the value.

        :param aType: type of the value
        :param aValue: the value to set
        :param aInt1: True if the tag name must be 'Int1' instead of 'Int32' in the case of a value INTEGER1. Default to False
        :type aType: :class:`.ParamTypeEnum`
        :type aValue: str
        :type aInt1: bool
        """
        self.mTagName = 'constantValue'
        if aType == sbsenum.ParamTypeEnum.BOOLEAN:
            self.mTagName += 'Bool'
        elif aType == sbsenum.ParamTypeEnum.INTEGER1:
            if aInt1:
                self.mTagName += 'Int1'
            else:
                self.mTagName += 'Int32'
        elif aType == sbsenum.ParamTypeEnum.INTEGER2:
            self.mTagName += 'Int2'
        elif aType == sbsenum.ParamTypeEnum.INTEGER3:
            self.mTagName += 'Int3'
        elif aType == sbsenum.ParamTypeEnum.INTEGER4:
            self.mTagName += 'Int4'
        elif aType == sbsenum.ParamTypeEnum.FLOAT1:
            self.mTagName += 'Float1'
        elif aType == sbsenum.ParamTypeEnum.FLOAT2:
            self.mTagName += 'Float2'
        elif aType == sbsenum.ParamTypeEnum.FLOAT3:
            self.mTagName += 'Float3'
        elif aType == sbsenum.ParamTypeEnum.FLOAT4:
            self.mTagName += 'Float4'
        elif aType == sbsenum.ParamTypeEnum.FLOAT_VARIANT:
            if isinstance(aValue, int) or isinstance(aValue, float):
                self.mTagName += 'Float1'
            else:
                self.mTagName += 'Float4'
        elif aType == sbsenum.ParamTypeEnum.STRING:
            self.mTagName += 'String'
        elif aType == sbsenum.ParamTypeEnum.PATH:
            self.mTagName += 'String'
        else:
            return

        self.updateConstantValue(aValue)

    @handle_exceptions()
    def updateConstantValue(self, aValue):
        """
        updateConstantValue(aValue)
        Update the value.

        :param aValue: the value to set
        :type aValue: str
        """
        if isinstance(aValue, list):
            aStrValue = ''
            for v in aValue:
                aStrValue += str(v) + ' '
            if aStrValue != '':
                aStrValue = aStrValue[:-1]
        elif isinstance(aValue, bool):
            aStrValue = '1' if aValue else '0'
        else:
            aStrValue = python_helpers.castStr(aValue)
        self.mConstantValue = aStrValue



# ==============================================================================
@doc_inherit
class SBSOption(SBSObject):
    """
    Class that contains information on an option that can appear in a substance graph / compNode

    Members:
        * mName  (str): name of the option
        * mValue (str): value of the option
    """
    def __init__(self,
                 aName  = '',
                 aValue = ''):
        super(SBSOption, self).__init__()
        self.mName = aName
        self.mValue = aValue

        self.mMembersForEquality = ['mName',
                                    'mValue']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName    = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name'   )
        self.mValue   = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'value'  )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mName   , 'name'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mValue  , 'value'  )



# ==============================================================================
@doc_inherit
class SBSIcon(SBSObject):
    """
    Class that contains information on an icon as defined in a .sbs file.
    An icon can be added in the attributes section of a graph.

    Members:
        * mDataLength (str): length of the icon image data.
        * mFormat     (str): icon format.
        * mStrdata    (str): icon image data.
    """

    def __init__(self,
                 aDataLength='',
                 aFormat='',
                 aStrdata=''):
        super(SBSIcon, self).__init__()
        self.mDataLength = aDataLength
        self.mFormat = aFormat
        self.mStrdata = aStrdata

        self.mMembersForEquality = ['mDataLength',
                                    'mFormat',
                                    'mStrdata']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mDataLength = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'datalength')
        self.mFormat = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'format')
        self.mStrdata = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'strdata')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDataLength, 'datalength')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFormat, 'format')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mStrdata, 'strdata')



# ==============================================================================
@doc_inherit
class SBSAttributes(SBSObject):
    """
    Class that contains information on attributes as defined in a .sbs file

    Members:
        * mAuthor        (str, optional): author information.
        * mAuthorURL     (str, optional): author url.
        * mCategory      (str, optional): data category. Slash separated strings.
        * mDescription   (str, optional): textual description.
        * mHideInLibrary (str, optional): whether or not the object is hidden in library.
        * mIcon          (:class:`.SBSIcon`, optional): icon.
        * mLabel         (str, optional): user label.
        * mPhysicalSize  (str, optional): the physical size (float3) of a graph.
        * mTags          (str, optional): tags as comma separated strings.
        * mUserTags      (str, optional): user information useful for the 3D engine using the substance engine (UNICODE string).
    """
    __sAttributeMap = {
        sbsenum.AttributesEnum.Author:          'mAuthor',
        sbsenum.AttributesEnum.AuthorURL:       'mAuthorURL',
        sbsenum.AttributesEnum.Category:        'mCategory',
        sbsenum.AttributesEnum.Description:     'mDescription',
        sbsenum.AttributesEnum.HideInLibrary:   'mHideInLibrary',
        sbsenum.AttributesEnum.Icon:            'mIcon',
        sbsenum.AttributesEnum.Label:           'mLabel',
        sbsenum.AttributesEnum.PhysicalSize:    'mPhysicalSize',
        sbsenum.AttributesEnum.Tags:            'mTags',
        sbsenum.AttributesEnum.UserTags:        'mUserTags'
    }
    def __init__(self,
                 aCategory      = None,
                 aLabel         = None,
                 aAuthor        = None,
                 aAuthorURL     = None,
                 aTags          = None,
                 aDescription   = None,
                 aUserTags      = None,
                 aIcon          = None,
                 aHideInLibrary = None,
                 aPhysicalSize  = None):
        super(SBSAttributes, self).__init__()
        self.mCategory      = aCategory
        self.mLabel         = aLabel
        self.mAuthor        = aAuthor
        self.mAuthorURL     = aAuthorURL
        self.mTags          = aTags
        self.mDescription   = aDescription
        self.mUserTags      = aUserTags
        self.mIcon          = aIcon
        self.mHideInLibrary = aHideInLibrary
        self.mPhysicalSize  = aPhysicalSize

        self.mMembersForEquality = ['mCategory',
                                    'mLabel',
                                    'mAuthor',
                                    'mAuthorURL',
                                    'mTags',
                                    'mDescription',
                                    'mUserTags',
                                    'mIcon',
                                    'mHideInLibrary',
                                    'mPhysicalSize']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mCategory      = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'category'     )
        self.mLabel         = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'label'        )
        self.mAuthor        = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'author'       )
        self.mAuthorURL     = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'authorURL'    )
        self.mTags          = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'tags'         )
        self.mDescription   = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'description'  )
        self.mUserTags      = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'usertags'     )
        self.mIcon          = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,  'icon'         , SBSIcon)
        self.mHideInLibrary = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'hideInLibrary')
        self.mPhysicalSize  = aSBSParser.getXmlElementVAttribValue(aXmlNode,            'physicalSize'  )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mCategory      , 'category'     )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mLabel         , 'label'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mAuthor        , 'author'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mAuthorURL     , 'authorURL'    )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mTags          , 'tags'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDescription   , 'description'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUserTags      , 'usertags'     )
        aSBSWriter.writeSBSNode(aXmlNode,              self.mIcon          , 'icon'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mHideInLibrary , 'hideInLibrary')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mPhysicalSize  , 'physicalSize'  )

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        """
        getAttribute(aAttributeIdentifier)
        Get the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :return: the attribute value if defined, None otherwise
        """
        if SBSAttributes.__sAttributeMap.get(aAttributeIdentifier, None) is None or \
            not hasattr(self, SBSAttributes.__sAttributeMap[aAttributeIdentifier]) or \
            getattr(self, SBSAttributes.__sAttributeMap[aAttributeIdentifier]) is None:
            return None

        if aAttributeIdentifier == sbsenum.AttributesEnum.HideInLibrary:
            return api_helpers.getTypedValueFromStr(self.mHideInLibrary, sbsenum.ParamTypeEnum.BOOLEAN)
        elif aAttributeIdentifier == sbsenum.AttributesEnum.PhysicalSize:
            return api_helpers.getTypedValueFromStr(self.mPhysicalSize, sbsenum.ParamTypeEnum.FLOAT3)
        else:
            return getattr(self, SBSAttributes.__sAttributeMap[aAttributeIdentifier])

    @handle_exceptions()
    def setAttribute(self, aAttributeIdentifier, aAttributeValue, aParentObject):
        """
        setAttribute(self, aAttributeIdentifier, aAttributeValue)
        Set the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :param aAttributeValue: the attribute value
        :param aParentObject: the object containing this attribute
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :type aAttributeValue: str or :class:`.SBSIcon`
        :type aParentObject: :class:`.SBSAttribute`
        """
        try:
            if aAttributeIdentifier not in aParentObject.getAllowedAttributes() or \
                SBSAttributes.__sAttributeMap.get(aAttributeIdentifier, None) is None:
                raise SBSImpossibleActionError('Cannot set the attribute '+str(aAttributeIdentifier)+' on a '+str(aParentObject.__class__))
        except AttributeError:
            raise AttributeError('The class '+str(aParentObject.__class__.__name__)+' must implement the function getAllowedAttributes()')

        if aAttributeIdentifier == sbsenum.AttributesEnum.Icon:
            if not isinstance(aAttributeValue, SBSIcon):
                raise SBSImpossibleActionError('The icon must be a SBSIcon object. You may want to use SBSGraph.setIcon() function instead')
            self.mIcon = aAttributeValue

        elif aAttributeIdentifier == sbsenum.AttributesEnum.HideInLibrary:
            self.mHideInLibrary = api_helpers.formatValueForTypeStr(aAttributeValue, aType=sbsenum.ParamTypeEnum.BOOLEAN)
        elif aAttributeIdentifier == sbsenum.AttributesEnum.PhysicalSize:
            self.mPhysicalSize = api_helpers.formatValueForTypeStr(aAttributeValue, aType=sbsenum.ParamTypeEnum.FLOAT3)
        else:
            aAttributeValue = api_helpers.formatValueForTypeStr(aAttributeValue, aType=sbsenum.ParamTypeEnum.STRING)
            setattr(self, SBSAttributes.__sAttributeMap[aAttributeIdentifier], aAttributeValue)

    @handle_exceptions()
    def setAttributes(self, aAttributes, aParentObject):
        """
        setAttributes(aAttributes, aParentObject)
        Set the given attributes

        :param aAttributes: The attributes to set
        :param aParentObject: the object containing this attribute
        :type aAttributes: dictionary in the format {:class:`.AttributesEnum` : value}
        :type aParentObject: :class:`.SBSAttribute`
        """
        for aAttributeKey,aAttributeValue in list(aAttributes.items()):
            self.setAttribute(aAttributeKey, aAttributeValue, aParentObject)

    def hasAttributes(self):
        """
        Check if at least one attribute is defined among:
            'category', 'label', 'author', 'authorURL', 'tags', 'description', 'usertags', 'icon', 'hideInLibrary', 'physicalSize'

        :return: True if at least one attribute is defined, False otherwise
        """
        for aKey, aMember in SBSAttributes.__sAttributeMap.items():
            if hasattr(self, aMember) and getattr(self, aMember) is not None:
                return True
        return False


# ==============================================================================
@doc_inherit
class SBSTreeStr(SBSObject):
    """
    A string option. Currently used in resource scenes

    Members:
        * mName  (str): name of the option
        * mValue (str): value of the option
    """
    def __init__(self,
                 aName  = '',
                 aValue = ''):
        super(SBSTreeStr, self).__init__()
        self.mName = aName
        self.mValue = aValue
        self.mMembersForEquality = ['mName',
                                    'mValue']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName  = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name'   )
        self.mValue = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'value'  )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mName   , 'name'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mValue  , 'value'  )

# ==============================================================================
@doc_inherit
class SBSTreeUrl(SBSObject):
    """
    A url option. Currently used in resource scenes

    Members:
        * mName  (str): name of the option
        * mValue (str): value of the option
    """
    def __init__(self,
                 aName  = '',
                 aValue = ''):
        super(SBSTreeUrl, self).__init__()
        self.mName = aName
        self.mValue = aValue

        self.mMembersForEquality = ['mName',
                                    'mValue']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName  = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name'   )
        self.mValue = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'value'  )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mName   , 'name'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode , self.mValue  , 'value'  )


# ==============================================================================
@doc_inherit
class SBSTreeList(SBSObject):
    """
    List of options in the resource scene tree. Currently used in resource scenes

    Members:
        * mName  (str): name of the option
        * aElements (list): a list of options to populate the list with
    """
    def __init__(self,
                 aName  = '',
                 aElements = None):
        super(SBSTreeList, self).__init__()
        self.mName = aName
        self.mElements = [] if aElements is None else aElements

        self.mMembersForEquality = ['mName',
                                    'mElements']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mName     = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'name'   )
        self.mElements = aSBSParser.getAllSBSElementsInMulti(aContext,
                                                         aDirAbsPath,
                                                         aXmlNode,
                                                         {
                                                             'tree': SBSTree,
                                                             'treestr': SBSTreeStr,
                                                             'treeurl': SBSTreeUrl
                                                         })

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        # TODO: Implement
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mName, 'name')
        for element in self.mElements:
            if isinstance(element, SBSTreeStr):
                aSBSWriter.writeSBSNode(aXmlNode, element, 'treestr')
            elif isinstance(element, SBSTreeUrl):
                aSBSWriter.writeSBSNode(aXmlNode, element, 'treeurl')
            elif isinstance(element, SBSTree):
                aSBSWriter.writeSBSNode(aXmlNode, element, 'tree')
            else:
                raise SBSImpossibleActionError('Invalid child type for treelist node')

    @handle_exceptions()
    def __getitem__(self, item):
        return self.mElements[item]



# ==============================================================================
@doc_inherit
class SBSTree(SBSObject):
    """
    Tree of options in the resource scene

    Members:
        * mTreeElements (collections.OrderedDict): Ordered dict of options with their name as ey
    """
    def __init__(self,
                 aTreeElements = None):
        super(SBSTree, self).__init__()
        self.mTreeElements = OrderedDict() if aTreeElements is None else aTreeElements

        self.mMembersForEquality = ['mTreeElements']

    @handle_exceptions()
    def __len__(self):
        return len(self.mTreeElements)

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        allElements = aSBSParser.getAllSBSElementsInMulti(aContext,
                                                              aDirAbsPath,
                                                              aXmlNode,
                                                              {
                                                                  'treelist': SBSTreeList,
                                                                  'treestr': SBSTreeStr,
                                                                  'treeurl': SBSTreeUrl
                                                              })
        self.mTreeElements = OrderedDict([(e.mName, e) for e in allElements])

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        for element in self.mTreeElements.values():
            if isinstance(element, SBSTreeStr):
                aSBSWriter.writeSBSNode(aXmlNode, element, 'treestr')
            elif isinstance(element, SBSTreeUrl):
                aSBSWriter.writeSBSNode(aXmlNode, element, 'treeurl')
            elif isinstance(element, SBSTreeList):
                aSBSWriter.writeSBSNode(aXmlNode, element, 'treelist')
            else:
                raise SBSImpossibleActionError('Invalid child type for tree node')

    @handle_exceptions()
    def getChildByName(self, aName):
        """
        Returns a child node based on its name. Returns None if the child doesn't exist
        :param aName: The name of the child to ask for
        :type aName: str
        :return: SBSTree SBSTreeList, SBSTreeStr, SBSTreeUrl or None if not found
        """
        return self.mTreeElements.get(aName, None)

    @handle_exceptions()
    def getChildByPath(self, aPath):
        """
        Queries a child by a path in a hierarchy of SBSTree and nodes
        :param aPath: The path to the child queried in the format a/b/c where a and b are SBStrees and c is the name
        of the element asked for
        :type aPath: str
        :return: SBSTree SBSTreeList, SBSTreeStr, SBSTreeUrl or None if not found
        """
        pList = list(filter(None, aPath.split('/')))
        o = [self]
        for i, p in list(enumerate(pList)):
            currentNode = o[0].getChildByName(p)
            if currentNode is None:
                if i is (len(pList) - 1):
                    return None
            else:
                o = currentNode
        return o

    @handle_exceptions()
    def setChildByPath(self, aPath, aValue, asURL=False):
        """
        Sets a child by a path in a hierarchy of SBSTree and nodes
        :param aPath: The path to the child queried in the format a/b/c where a and b are SBStrees and c is the name
        of the element to set
        If the element set already exists it will be overwritten by the new value
        :type aPath: str
        :param aValue: a string representing the value to set
        :type aValue: str
        :param asURL: Optional parameter to say whether the value should be created as an SBSTreeStr or SBSTreeUrl
        :type asURL: bool
        """
        pList = aPath.split('/')
        o = [self]
        for i, p in list(enumerate(pList)):
            currentNode = o[0].getChildByName(p)
            if currentNode is None:
                # This is a node that didn't exist in the initial setup
                if i is (len(pList) - 1):
                    # We are at the value
                    value = (SBSTreeUrl if asURL else SBSTreeStr)(aName=p, aValue=aValue)
                    o[0].mTreeElements[p] = value
                    return
                else:
                    # We are at a branch
                    newBranch = SBSTreeList(aName=p, aElements=[SBSTree()])
                    o[0].mTreeElements[p] = newBranch
                    o = newBranch
            else:
                o = currentNode

        o.mValue = aValue

    @handle_exceptions()
    def asStringList(self):
        """
        Returns the content of a tree representing a vector (meaning it has a size element and the indices as keys)
        :return: [str]
        """
        nbItems = self.getChildByName('size')
        if not nbItems:
            raise SBSImpossibleActionError('SBSTree doesn\'t have a size parameter and can not be interpreted as a list')
        if  int(nbItems.mValue) > 0:
            aStringList = []
            for i in range(1, int(nbItems.mValue) + 1):
                opt = self.getChildByName(str(i))
                if isinstance(opt, SBSTreeStr):
                    aStringList.append(opt.mValue)
                elif isinstance(opt, SBSTreeList):
                    # This code is very much special case for our current tree
                    # Might break if we introduce other stringlists
                    aStringList.append(opt[0].getChildByName('mesh').mValue)
            return aStringList
        return []

    @handle_exceptions()
    def asOptionList(self):
        """
        Recursively turns a tree into a list of options with paths.
        The options will have a name on the form a/b/c and a value representing the string at the leaf
        :return: [SBSOption]
        """
        def genOptionList(tree, currentPath, result):
            for name, item in tree.mTreeElements.items():
                if isinstance(item, SBSTreeList):
                    if len(item.mElements) == 1 and isinstance(item.mElements[0], SBSTree):
                         genOptionList(item.mElements[0], currentPath + name + '/', result)
                elif isinstance(item, SBSTreeStr):
                    result.append(SBSOption(aName=currentPath + name, aValue=item.mValue))
                elif isinstance(item, SBSTreeUrl):
                    result.append(SBSOption(aName=currentPath + name, aValue=item.mValue))
        results = []
        genOptionList(self, '', results)
        return results
