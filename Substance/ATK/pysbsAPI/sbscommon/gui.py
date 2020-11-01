# coding: utf-8
"""
Module **gui** provides the definition of the classes relative to the GUI:
- :class:`.SBSGUILayout`
- :class:`.SBSGUIObject`
- :class:`.SBSGUILayoutComp`
"""
from __future__ import unicode_literals
import weakref

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers, api_helpers
from pysbs import sbsenum
from pysbs.common_interfaces import SBSObject
from pysbs import sbsgenerator
from pysbs import sbslibrary
from .values import SBSOption



class Rect(object):
    def __init__(self, aTop=0, aLeft=0, aWidth=0, aHeight=0):
        self.mTop = aTop
        self.mLeft = aLeft
        self.mWidth = aWidth
        self.mHeight = aHeight

    def __eq__(self, other):
        return self.mTop    == other.mTop    and \
               self.mLeft   == other.mLeft   and \
               self.mWidth  == other.mWidth  and \
               self.mHeight == other.mHeight

    @handle_exceptions()
    def containsPoint(self, aPoint):
        """
        containsPoint(aPoint)
        Check if the given point is contained in the Rectangle.

        :param aPoint: The point to test
        :type: list of 2 float [x, y] or tuple
        :return: True if the given point is contained in the Rectangle, False otherwise
        """
        return self.mLeft <= aPoint[0] <= self.mLeft + self.mWidth and \
               self.mTop <= aPoint[1] <= self.mTop + self.mHeight

    @handle_exceptions()
    def getCorners(self):
        """
        getCorners()
        Get the 4 corner points of this rectangle

        :return: The corners of this rectangle, as a list of tuple
        """
        return [(self.mLeft, self.mTop),
                (self.mLeft + self.mWidth, self.mTop),
                (self.mLeft, self.mTop + self.mHeight),
                (self.mLeft + self.mWidth, self.mTop + self.mHeight)]

    @handle_exceptions()
    def overlapsWith(self, aOther):
        """
        overlapsWith(aOther)
        Check if the two rectangles overlap

        :param aOther: The other rectangle
        :type aOther: :class:`.Rect`
        :return: True if the two rectangles overlap
        """
        for aCorner in aOther.getCorners():
            if self.containsPoint(aCorner):
                return True
        for aCorner in self.getCorners():
            if aOther.containsPoint(aCorner):
                return True
        return False

    @handle_exceptions()
    def union(self, aOther):
        """
        union(aOther)
        Create the union of two rectangles

        :param aOther: The other rectangle
        :type aOther: :class:`.Rect`
        :return: The rectangle which is the union of the two rectangles
        """
        aRect = Rect()
        aRight = max(self.mLeft + self.mWidth, aOther.mLeft + aOther.mWidth)
        aBottom = max(self.mTop + self.mHeight, aOther.mTop + aOther.mHeight)

        aRect.mLeft = min(self.mLeft, aOther.mLeft)
        aRect.mTop = min(self.mTop, aOther.mTop)
        aRect.mWidth = aRight - aRect.mLeft
        aRect.mHeight = aBottom - aRect.mTop
        return aRect


# =======================================================================
@doc_inherit
class SBSGUILayout(SBSObject):
    """
    Class that contains information on a GUILayout (GUI position and options) as defined in a .sbs file

    Members:
        * mGPos         (list of 3 float, optional): position in the graph layout.
        * mDocked       (str, optional): object is in a docked state.
        * mDockDistance (str, optional): original distance between the docked node and its parent (for undock purpose).
        * mSize         (str, optional): size of the object.
    """
    def __init__(self,
                 aGPos          = None,
                 aDocked        = None,
                 aDockDistance  = None,
                 aSize          = None):
        super(SBSGUILayout, self).__init__()
        if aGPos is None:
            self.mGPos = [0, 0, 0]
        else:
            self.mGPos = api_helpers.getTypedValueFromStr(aValue=aGPos, aType=sbsenum.ParamTypeEnum.FLOAT3) if python_helpers.isStringOrUnicode(aGPos) else aGPos

        if aSize is None:
            self.mSize = [-1, -1]
        else:
            self.mSize = api_helpers.getTypedValueFromStr(aValue=aSize, aType=sbsenum.ParamTypeEnum.FLOAT2) if python_helpers.isStringOrUnicode(aSize) else aSize
        self.mDocked       = aDocked
        self.mDockDistance = aDockDistance

        self.mMembersForEquality = ['mGPos',
                                    'mDocked',
                                    'mDockDistance',
                                    'mSize']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        aGPosStr           = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'gpos'          )
        self.mDocked       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'docked'        )
        self.mDockDistance = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'dockDistance'  )
        aSizeStr           = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'size'          )

        if aGPosStr is not None:
            self.mGPos = api_helpers.getTypedValueFromStr(aValue = aGPosStr, aType = sbsenum.ParamTypeEnum.FLOAT3)

        if aSizeStr is not None:
            self.mSize = api_helpers.getTypedValueFromStr(aValue = aSizeStr, aType = sbsenum.ParamTypeEnum.FLOAT2)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        if self.mGPos is not None and self.mGPos != [0,0,0]:
            aGPosStr = api_helpers.formatValueForTypeStr(aValue = self.mGPos, aType = sbsenum.ParamTypeEnum.FLOAT3)
        else:
            aGPosStr = None

        if self.mSize is not None and self.mSize != [-1,-1]:
            aSizeStr = api_helpers.formatValueForTypeStr(aValue = self.mSize, aType = sbsenum.ParamTypeEnum.FLOAT2)
        else:
            aSizeStr = None

        aSBSWriter.setXmlElementVAttribValue(aXmlNode, aGPosStr           , 'gpos'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDocked       , 'docked'        )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDockDistance , 'dockDistance'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, aSizeStr           , 'size'          )



# =======================================================================
@doc_inherit
class SBSGUIObject(SBSObject):
    """
    Class that contains information on a GUIObject as defined in a .sbs file

    Members:
        * mUID            (str): node unique identifier in the /GUIObjects/ context.
        * mType           (str): type of GUI object (comment, navigation pin, etc.)
        * mGUIDependency  (str): dependency of this GUI Object on an object in the graph ( format : Type?uid(?uid...) )
        * mGUILayout      (:class:`.SBSGUILayout`):
        * mGUIName        (str): name of the GUI object.
        * mOptions        (list of :class:`.SBSOption`): list of specific options of the GUI object type.
        * mTitle          (str, optional): The object Title
        * mFrameColor     (str, optional): frame color (RGBA Float)
        * mIsTitleVisible (str, optional): bool to set title visibility
        * mIsFrameVisible (str, optional): bool to set frame visibility
    """
    sDefaultColor = [0.196078435, 0.196078435, 0.509803951, 0.196078435] #[50/255, 50/255, 130/255, 50/255]

    def __init__(self,
                 aUID               = '',
                 aType              = '',
                 aGUIDependency     = None,
                 aGUILayout         = None,
                 aGUIName           = '',
                 aOptions           = None,
                 aTitle             = None,
                 aFrameColor        = None,
                 aIsTitleVisible    = None,
                 aIsFrameVisible    = None):
        super(SBSGUIObject, self).__init__()
        self.mType           = aType
        self.mGUIDependency  = aGUIDependency
        self.mGUILayout      = aGUILayout
        self.mGUIName        = aGUIName
        self.mUID            = aUID
        self.mOptions        = aOptions
        self.mTitle          = aTitle
        self.mFrameColor     = aFrameColor
        self.mIsTitleVisible = aIsTitleVisible
        self.mIsFrameVisible = aIsFrameVisible

        self.mMembersForEquality = ['mType',
                                    'mGUIDependency',
                                    'mGUIName',
                                    'mOptions',
                                    'mTitle',
                                    'mFrameColor',
                                    'mIsTitleVisible',
                                    'mIsFrameVisible']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mType           = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'type'           )
        self.mGUIDependency  = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'GUIDependency'  )
        self.mGUILayout      = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'GUILayout'      , SBSGUILayout)
        self.mGUIName        = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'GUIName'        )
        self.mUID            = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'            )
        self.mOptions        = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'options'        , 'option' , SBSOption)
        self.mTitle          = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'title'          )
        self.mFrameColor     = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'frameColor'     )
        self.mIsTitleVisible = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'isTitleVisible' )
        self.mIsFrameVisible = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'isFrameVisible' )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mType              , 'type'            )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mGUIDependency     , 'GUIDependency'   )
        aSBSWriter.writeSBSNode(aXmlNode,               self.mGUILayout         , 'GUILayout'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mGUIName           , 'GUIName'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mUID               , 'uid'             )
        aSBSWriter.writeListOfSBSNode(aXmlNode       ,  self.mOptions           , 'options'         , 'option')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mTitle             , 'title'           )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mFrameColor        , 'frameColor'      )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIsTitleVisible    , 'isTitleVisible'  )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode,  self.mIsFrameVisible    , 'isFrameVisible'  )

    def getRect(self):
        """
        getRect()
        Return the rectangle of this GUIObject

        :return: The rectangle as a :class:`.Rect`
        """
        aSize = self.mGUILayout.mSize if self.mGUILayout.mSize != [-1,-1] else [100,50]
        return Rect(aLeft = self.mGUILayout.mGPos[0], aTop = self.mGUILayout.mGPos[1],
                    aWidth= aSize[0], aHeight=aSize[1])

    def getDependencyUID(self):
        """
        getDependencyUID()
        Get the UID of the node associated to this GUIObject.

        :return: the UID as a string if found, None otherwise
        """
        if self.mGUIDependency:
            pos = self.mGUIDependency.find('?')
            if pos > 0:
                return self.mGUIDependency[pos+1:]
        return None

    def hasDependencyOn(self, aUID):
        """
        hasDependencyOn(aUID)
        Checks if this GUI Object has a dependency on the given UID

        :param aUID: The UID to consider
        :type aUID: str
        :return: True if this GUI Object has a dependency on the object with the given UID, False otherwise
        """
        aDepUID = self.getDependencyUID()
        return aDepUID == aUID

    def isANavigationPin(self):
        """
        isANavigationPin()

        :return: True if this GUIObject is a navigation pin
        """
        return self.mType == sbslibrary.getGUIObjectTypeName(sbsenum.GUIObjectTypeEnum.PIN)

    def isAComment(self):
        """
        isAComment()

        :return: True if this GUIObject is a simple comment
        """
        return self.mType == sbslibrary.getGUIObjectTypeName(sbsenum.GUIObjectTypeEnum.COMMENT) and \
            (self.mIsFrameVisible is None or self.mIsFrameVisible == '0')

    def isAFrame(self):
        """
        isAFrame()

        :return: True if this GUIObject is a framed comment
        """
        return self.mType == sbslibrary.getGUIObjectTypeName(sbsenum.GUIObjectTypeEnum.COMMENT) and \
               self.mIsFrameVisible == '1'



# =======================================================================
@doc_inherit
class SBSGUILayoutComp(SBSObject):
    """
    Class that contains information on a GUILayoutComp (Gui flags and options) as defined in a .sbs file

    Members:
        * mDisplay (str): display type (graph, stack, etc.).
        * mGRoi    (str): visualized Region Of Interest of the graph.
        * mGZoom   (str): graph zoom.
    """
    def __init__(self,
                 aDisplay = None,
                 aGRoi    = None,
                 aGZoom   = None):
        super(SBSGUILayoutComp, self).__init__()
        self.mDisplay   = aDisplay
        self.mGRoi      = aGRoi
        self.mGZoom     = aGZoom

        self.mMembersForEquality = ['mDisplay',
                                    'mGRoi',
                                    'mGZoom']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mDisplay   = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'display'  )
        self.mGRoi      = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'groi'     )
        self.mGZoom     = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'gzoom'    )

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDisplay, 'display')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mGRoi   , 'groi'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mGZoom  , 'gzoom'  )


# =======================================================================
class GUIObjectList:
    """
    Class used to provide common methods to SBSObjects that contains a list of GUIObjects:
    - :class:`.SBSGraph`
    - :class:`.SBSDynamicValue`
    - :class:`.SBSParamsGraph`

    Members:
        * mParentObject    (:class:`.SBSObject`): Parent object that contains the GUI object list.
        * mGUIObjectsAttr  (str): attribute member name in the parent object that corresponds to the GUI object list.
    """
    def __init__(self, aParentObject, aGUIObjectsAttr):
        self.mParentObject = weakref.ref(aParentObject)
        self.mGUIObjectsAttr = aGUIObjectsAttr

    @handle_exceptions()
    def getAllComments(self):
        """
        getAllComments()
        Get all comments defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        return [aGUIObject for aGUIObject in self.getAllGUIObjects() if aGUIObject.isAComment()]

    @handle_exceptions()
    def getAllFrames(self):
        """
        getAllFrames()
        Get all frames defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        return [aGUIObject for aGUIObject in self.getAllGUIObjects() if aGUIObject.isAFrame()]

    @handle_exceptions()
    def getAllNavigationPins(self):
        """
        getAllNavigationPins()
        Get all the navigation pins defined in the graph

        :return: a list of :class:`.SBSGUIObject`
        """
        return [aGUIObject for aGUIObject in self.getAllGUIObjects() if aGUIObject.isANavigationPin()]

    @handle_exceptions()
    def getAllGUIObjects(self):
        """
        getAllGUIObjects()
        Get all the GUI objects defined in the graph (Comments, Frames, Navigation Pins)

        :return: a list of :class:`.SBSGUIObject`
        """
        aGUIObjects = None
        if hasattr(self.mParentObject(), self.mGUIObjectsAttr):
            aGUIObjects = getattr(self.mParentObject(), self.mGUIObjectsAttr)
        return aGUIObjects if aGUIObjects is not None else []

    @handle_exceptions()
    def getGUIObject(self, aGUIObject):
        """
        getGUIObject(aGUIObject):
        Search for the given GUI object in the list

        :param aGUIObject: GUI object to get, identified by its uid or as a :class:`.SBSGUIObject`
        :type  aGUIObject: :class:`.SBSGUIObject` or str
        :return: A :class:`.SBSGUIObject` object if found, None otherwise
        """
        aGUIObjectList = self.getAllGUIObjects()
        if python_helpers.isStringOrUnicode(aGUIObject):
            return next((guiObject for guiObject in aGUIObjectList if guiObject.mUID == aGUIObject), None)
        elif aGUIObject in aGUIObjectList:
            return aGUIObject
        return None

    @handle_exceptions()
    def createComment(self, aCommentText='Comment', aGUIPos=None, aLinkToNode=None):
        """
        createComment(aCommentText='Comment', aGUIPos=None)
        Create a new comment.

        :param aCommentText: The text of the comment. Default to 'Comment'
        :param aGUIPos: The comment position in the graph. Default to [0,0,0]
        :param aLinkToNode: The UID of the node to associate to this comment
        :type aCommentText: str, optional
        :type aGUIPos: list of 3 float, optional
        :type aLinkToNode: str, optional
        :return: The :class:`.SBSGUIObject` created
        """
        if aGUIPos is None: aGUIPos = [0, 0, 0]
        aGUIPos[2] = -100
        aDepUID = 'NODE?'+aLinkToNode if aLinkToNode is not None else None
        aGUIObject = sbsgenerator.createGUIObject(aParentObject  = self.mParentObject(),
                                                  aObjectType    = sbsenum.GUIObjectTypeEnum.COMMENT,
                                                  aGUIName       = aCommentText,
                                                  aGUIPos        = aGUIPos,
                                                  aGUIDependency = aDepUID,
                                                  aColor         = SBSGUIObject.sDefaultColor,
                                                  aSize          = [100, 50])
        api_helpers.addObjectToList(self.mParentObject(), self.mGUIObjectsAttr, aGUIObject)
        return aGUIObject

    @handle_exceptions()
    def createFrame(self, aSize, aFrameTitle='Frame', aCommentText='', aGUIPos=None, aColor=None, aDisplayTitle=True):
        """
        createFrame(aSize, aFrameTitle='Frame', aCommentText='', aGUIPos=None, aColor=None, aDisplayTitle=True)
        Create a new framed comment.

        :param aSize: The frame size
        :param aFrameTitle: The title of the frame. Default to 'Frame'
        :param aCommentText: The text of the frame. Empty by default
        :param aGUIPos: The frame position in the graph. Default to [0,0,-100]
        :param aColor: The frame color. Default to [0.196, 0.196, 0.509, 0.196]
        :param aDisplayTitle: True to display the frame title. Default to True
        :type aSize: list of 2 float
        :type aFrameTitle: str, optional
        :type aCommentText: str, optional
        :type aGUIPos: list of 3 float, optional
        :type aColor: list of 4 float between 0 and 1, optional.
        :type aDisplayTitle: boolean, optional
        :return: The :class:`.SBSGUIObject` created
        """
        if aColor is None: aColor = SBSGUIObject.sDefaultColor
        if aGUIPos is None: aGUIPos = [0, 0, 0]
        aGUIPos[2] = -100

        aGUIObject = sbsgenerator.createGUIObject(aParentObject   = self.mParentObject(),
                                                  aObjectType     = sbsenum.GUIObjectTypeEnum.COMMENT,
                                                  aGUIName        = aCommentText,
                                                  aTitle          = aFrameTitle,
                                                  aGUIPos         = aGUIPos,
                                                  aSize           = aSize,
                                                  aColor          = aColor,
                                                  aIsFrameVisible = True,
                                                  aIsTitleVisible = aDisplayTitle)
        api_helpers.addObjectToList(self.mParentObject(), self.mGUIObjectsAttr, aGUIObject)
        return aGUIObject


    @handle_exceptions()
    def createFrameAroundNodes(self, aNodeList, aFrameTitle='Frame', aCommentText='', aColor=None, aDisplayTitle=True):
        """
        createFrameAroundNodes(aNodeList, aFrameTitle='Frame', aCommentText='', aColor=None, aDisplayTitle=True)
        Create a new framed comment around the given nodes.

        :param aNodeList: The nodes to include in the frame
        :param aFrameTitle: The title of the frame. Default to 'Frame'
        :param aCommentText: The text of the frame. Empty by default
        :param aColor: The frame color. Default to [0.196, 0.196, 0.509, 0.196]
        :param aDisplayTitle: True to display the frame title. Default to True
        :type aNodeList: list of class:`.SBSNode`
        :type aFrameTitle: str, optional
        :type aCommentText: str, optional
        :type aColor: list of 4 float between 0 and 1, optional.
        :type aDisplayTitle: boolean, optional
        :return: The :class:`.SBSGUIObject` created
        :raise: SBSImpossibleActionError
        """
        aRect = self.getFrameRectAroundNodes(aNodeList)

        aGUIPos = [aRect.mLeft, aRect.mTop, 0]
        aSize = [aRect.mWidth, aRect.mHeight]

        if aColor is None: aColor = SBSGUIObject.sDefaultColor
        aGUIObject = sbsgenerator.createGUIObject(aParentObject   = self.mParentObject(),
                                                  aObjectType     = sbsenum.GUIObjectTypeEnum.COMMENT,
                                                  aGUIName        = aCommentText,
                                                  aTitle          = aFrameTitle,
                                                  aGUIPos         = aGUIPos,
                                                  aSize           = aSize,
                                                  aColor          = aColor,
                                                  aIsFrameVisible = True,
                                                  aIsTitleVisible = aDisplayTitle)
        api_helpers.addObjectToList(self.mParentObject(), self.mGUIObjectsAttr, aGUIObject)
        return aGUIObject

    @handle_exceptions()
    def createNavigationPin(self, aPinText, aGUIPos=None):
        """
        createNavigationPin(self, aPinText, aGUIPos)
        Create a new navigation pin.

        :param aPinText: The text of the navigation pin
        :param aGUIPos: The navigation pin position in the graph. Default to [0,0,0]
        :type aPinText: str
        :type aGUIPos: list of 3 float, optional
        :return: The :class:`.SBSGUIObject` created
        """
        if aGUIPos is None: aGUIPos = [0, 0, 0]
        aGUIObject = sbsgenerator.createGUIObject(aParentObject = self.mParentObject(),
                                                  aObjectType   = sbsenum.GUIObjectTypeEnum.PIN,
                                                  aGUIName      = aPinText,
                                                  aGUIPos       = aGUIPos,
                                                  aColor        = [0, 0, 0, 1],
                                                  aSize         = [-1, -1],
                                                  aIsFrameVisible = True,
                                                  aIsTitleVisible = True)
        api_helpers.addObjectToList(self.mParentObject(), self.mGUIObjectsAttr, aGUIObject)
        return aGUIObject

    @handle_exceptions()
    def deleteGUIObject(self, aGUIObject):
        """
        deleteGUIObject(aGUIObject):
        Allows to delete the given GUI object.

        :param aGUIObject: The GUI object to remove, as a SBSGUIObject or an UID.
        :type aGUIObject: :class:`.SBSGUIObject` or str
        :return: True if success
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if python_helpers.isStringOrUnicode(aGUIObject): aUID = aGUIObject
        else:                                            aUID = aGUIObject.mUID

        aGUIObjectLists = self.getAllGUIObjects()
        aGUIObject = self.getGUIObject(aGUIObject)

        if aGUIObject is None:
            raise SBSImpossibleActionError('Impossible to delete the GUI Object ' + aUID + ', cannot find this object in the graph')

        aGUIObjectLists.remove(aGUIObject)
        return True

    def reframeAroundNodes(self, aFrame, aNodeList):
        """
        reframeAroundNodes(aFrame, aNodeList)
        Move and resize a frame to be around the given nodes.

        :param aFrame: The frame to edit
        :param aNodeList: The nodes to include in the frame
        :type aFrame: :class:`.SBSGUIObject`
        :type aNodeList: list of class:`.SBSNode`
        :raise: SBSImpossibleActionError
        """
        aGuiGraph = self.mParentObject()
        if not aFrame in aGuiGraph.getAllFrames():
            raise SBSImpossibleActionError('The given frame is not a part of the parent graph/function')

        aRect = self.getFrameRectAroundNodes(aNodeList)
        aFrame.mGUILayout.mGPos = [aRect.mLeft, aRect.mTop, 0]
        aFrame.mGUILayout.mSize = [aRect.mWidth, aRect.mHeight]


    def getNodesInFrame(self, aFrame):
        """
        getNodesInFrame(aFrame)
        Get all the nodes included or partially included in the given frame.
        The frame must be included in the parent graph, otherwise SBSImpossibleActionError is raised

        :param aFrame: The frame to consider
        :type aFrame: :class:`.SBSGUIObject`
        :return: a list of :class:`.SBSNode`
        :raise: SBSImpossibleActionError
        """
        aGuiGraph = self.mParentObject()
        if not aFrame in aGuiGraph.getAllFrames():
            raise SBSImpossibleActionError('The given frame is not a part of the parent graph/function')

        aRect = aFrame.getRect()
        aIncludedNodes = []
        isDockingAllowed = hasattr(self.mParentObject(), 'getNodesDockedTo')
        for aNode in self.mParentObject().getNodeList():
            if aRect.overlapsWith(aNode.getRect()):
                aIncludedNodes.append(aNode)
                if isDockingAllowed:
                    aIncludedNodes.extend(self.mParentObject().getNodesDockedTo(aNode))
        return aIncludedNodes


    def getFrameRectAroundNodes(self, aNodeList):
        """
        getFrameRectAroundNodes(aNodeList)
        Return the rectangle a frame would fill to be around the given nodes.

        :param aNodeList: The nodes to include in the frame
        :type aNodeList: list of class:`.SBSNode`
        :return: A :class:`.Rect`
        :raise: SBSImpossibleActionError
        """
        # Retrieve the real node list (allows to check that the given nodes belong to the parent graph container)
        realNodeList = self.mParentObject().getNodeList(aNodeList)
        if not realNodeList:
            raise SBSImpossibleActionError('The node list provided is empty, or the nodes are not included in the parent graph')

        # Compute the rectangle as the union of all the nodes rectangle
        aRect = realNodeList[0].getRect()
        for aNode in realNodeList[1:]:
            aRect = aRect.union(aNode.getRect())

        # Add an offset around the nodes, that will align correctly to the grid
        aRight = aRect.mLeft + aRect.mWidth
        if aRight%32 != 0:
            aRight += 32 - aRight%32
        aBottom = aRect.mTop + aRect.mHeight
        if aBottom % 32 != 0:
            aBottom += 32 - aBottom%32

        aRect.mLeft -= 32 + aRect.mLeft%32
        aRect.mTop -= 32 + aRect.mTop%32
        aRect.mWidth = aRight+32 - aRect.mLeft
        aRect.mHeight = aBottom+32 - aRect.mTop

        return aRect
