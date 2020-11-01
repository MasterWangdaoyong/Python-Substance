# coding: utf-8
"""
Module **resource** provides the definition of the classes relative to a SBSResource:

- :class:`.SBSSource`
    - :class:`.SBSSourceExternalCopy`
    - :class:`.SBSSourceBinboon`
    - :class:`.SBSSourceBinembedded`
- :class:`.SBSResource`
- :class:`.SBSResourceScene`
    - :class:`.SBSSceneMaterialMapEntry`
    - :class:`.SBSUVSetMaterialMap`
    - :class:`.SBSUVSetMaterialMapEntry`
    - :class:`.SBSUVSetMaterial`
    - :class:`.SBSOptionsByUrlMapEntry`

"""

from __future__ import unicode_literals
import os
import weakref
import glob

from pysbs.api_decorators import doc_inherit,handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject
from pysbs import python_helpers, api_helpers, ocio_helpers
from pysbs import sbsenum
from pysbs import sbscommon
from pysbs import sbsbakers
from pysbs import sbslibrary


# ==============================================================================
@doc_inherit
class SBSSourceExternalCopy(SBSObject):
    """
    Class that contains information on a source external copy as defined in a .sbs file.
    External copy refers to an external file copied in a sub-folder of the application and entirely managed (iTunes style).

    Members:
        * mFilename  (str): name of the managed file.
    """
    def __init__(self,
                 aFilename  = ''):
        super(SBSSourceExternalCopy, self).__init__()
        self.mFilename  = aFilename
        self.mMembersForEquality = ['mFilename']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mFilename  = aSBSParser.getXmlFilePathValue(aXmlNode, 'filename')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlFilePathValue(aXmlNode, self.mFilename   , 'filename')



# ==============================================================================
@doc_inherit
class SBSSourceBinboon(SBSObject):
    """
    Class that contains information on a source binary file bounded to the package as defined in a .sbs file.
    Binboon refers to a file saved in a binary file bounded to this package.

    Members:
        * mOffset           (str): offset in the binary file in bytes.
        * mDatalength       (str): length of the data in the binary file in bytes.
        * mFormat           (str, optional): zlib, raw, etc.
        * mCompressedlength (str, optional): size of the compressed data (if applicable).
    """
    def __init__(self,
                 aOffset           = '',
                 aDatalength       = '',
                 aFormat           = None,
                 aCompressedlength = None):
        super(SBSSourceBinboon, self).__init__()
        self.mOffset            = aOffset
        self.mDatalength        = aDatalength
        self.mFormat            = aFormat
        self.mCompressedlength  = aCompressedlength

        self.mMembersForEquality = ['mOffset',
                                    'mDatalength',
                                    'mFormat',
                                    'mCompressedlength']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mOffset            = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'offset')
        self.mDatalength        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'datalength')
        self.mFormat            = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'format')
        self.mCompressedlength  = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'compressedlength')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mOffset            , 'offset')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDatalength        , 'datalength')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFormat            , 'format')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mCompressedlength  , 'compressedlength')



# ==============================================================================
@doc_inherit
class SBSSourceBinembedded(SBSObject):
    """
    Class that contains information on a source binary file embedded to the package as defined in a .sbs file.
    Binembedded refers to a content embedded in the package file.

    Members:
        * mDatalength (str): size of the binary data in bytes.
        * mFormat     (str, optional): zlibbase64, rawbase64, etc.
        * mStrdata    (str): data in base64 ASCII format.
    """
    def __init__(self,
                 aDatalength= '',
                 aFormat    = None,
                 aStrdata   = ''):
        super(SBSSourceBinembedded, self).__init__()
        self.mDatalength    = aDatalength
        self.mFormat        = aFormat
        self.mStrdata       = aStrdata

        self.mMembersForEquality = ['mDatalength',
                                    'mFormat',
                                    'mStrdata']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mDatalength    = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'datalength')
        self.mFormat        = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'format')
        self.mStrdata       = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'strdata')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mDatalength  , 'datalength')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFormat      , 'format')
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mStrdata     , 'strdata')



#=======================================================================
@doc_inherit
class SBSSource(SBSObject):
    """
    Class that contains information on a source as defined in a .sbs file
    Embedded or managed source. The three children are exclusives.

    Members:
        * mExternalCopy (:class:`.SBSSourceExternalCopy`): external file copied in a sub-folder of the application and entirely managed (iTunes style).
        * mBinBoon      (:class:`.SBSSourceBinboon`): file saved in a binary file bounded to this package.
        * mBinEmbedded  (:class:`.SBSSourceBinembedded`): content embedded in the package file.
    """
    def __init__(self,
                 aExternalCopy  = None,
                 aBinBoon       = None,
                 aBinEmbedded   = None):
        super(SBSSource, self).__init__()
        self.mExternalCopy  = aExternalCopy
        self.mBinBoon       = aBinBoon
        self.mBinEmbedded   = aBinEmbedded

        self.mMembersForEquality = ['mExternalCopy',
                                    'mBinBoon',
                                    'mBinEmbedded']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mExternalCopy = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'externalcopy', SBSSourceExternalCopy)
        self.mBinBoon      = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'binboon'     , SBSSourceBinboon)
        self.mBinEmbedded  = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'binembedded' , SBSSourceBinembedded)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeSBSNode(aXmlNode, self.mExternalCopy, 'externalcopy')
        aSBSWriter.writeSBSNode(aXmlNode, self.mBinBoon     , 'binboon'     )
        aSBSWriter.writeSBSNode(aXmlNode, self.mBinEmbedded , 'binembedded' )

    def getSource(self):
        """
        Get the source, accordingly to the kind of source

        :return: a :class:`.SBSSourceExternalCopy`,  :class:`.SBSSourceBinboon` or :class:`.SBSSourceBinembedded` object
        """
        if   self.mExternalCopy is not None:    return self.mExternalCopy
        elif self.mBinBoon is not None:         return self.mBinBoon
        elif self.mBinEmbedded is not None:     return self.mBinEmbedded
        return None



# ==============================================================================
@doc_inherit
class SBSResource(SBSObject):
    """
    Class that contains information on a substance resource as defined in a .sbs file

    Members:
        * mIdentifier       (str): identifier of the file.
        * mUID              (str): unique identifier of this resource in the package/ context.
        * mType             (str): type of the resource ('bitmap','svg',...)
        * mFormat           (str): original format of the resource (e.g. BMP, JPG for bitmap type resources).
        * mColorSpace       (str, optional): colorspace transformation to apply based on ocio config file.
        * mPremultipliedAlpha (bool, optional): alpha is premultiplied or not.
        * mCookedFormat     (str, optional): format of the resource after the cooking stage (among :class:`.BitmapFormatEnum` for bitmap resources)
        * mCookedQuality    (float as a string, optional): quality of resource after the cooking stage (percentage for a bitmap type with a cookedFormat JPEG).
        * mFilePath         (str): path and name of the origin file.
        * mAttributes       (:class:`.SBSAttributes`): various attributes (author, description, ...)
        * mSource           (:class:`.SBSSource`): embedded or managed source.
        * mOptions          (:class:`.SBSOption`): additional options.
    """
    __sAttributes = [sbsenum.AttributesEnum.Category ,   sbsenum.AttributesEnum.Label,   sbsenum.AttributesEnum.Author       ,
                     sbsenum.AttributesEnum.AuthorURL,   sbsenum.AttributesEnum.Tags ,   sbsenum.AttributesEnum.Description  ,
                     sbsenum.AttributesEnum.UserTags ,   sbsenum.AttributesEnum.Icon ,   sbsenum.AttributesEnum.HideInLibrary]

    __sAllowedExtensions = {
        sbsenum.ResourceTypeEnum.SCENE: ['.3ds','.dae','.dxf','.fbx','.obj'],
        sbsenum.ResourceTypeEnum.SVG:   ['.svg'],
        sbsenum.ResourceTypeEnum.FONT:  ['.ttf','.otf'],
        sbsenum.ResourceTypeEnum.BITMAP:['.3fr','.arw','.bay','.bmp','.bmq','.bw','.cap','.cine','.cr2','.crw','.cs1','.cut',
                                         '.dc2','.dcr','.dds','.drf','.dsc','.dng','.erf','.exr','.fff','.gif','.g3',
                                         '.hdp','.hdr','.ia','.ico','.iff','.iiq','.j2c','.j2k','.jbig','.jif','.jng',
                                         '.jpe','.jpeg','.jpeg_xr','.jpeg_2000','.jp2','.jpg','.jxr','.k25','.kc2','.kdc','.koa',
                                         '.lbm','.mdc','.mef','.mng','.mos','.mrw','.nef','.nrw','.orf','.pbm','.pcd',
                                         '.pct','.pcx','.pef','.pic','.pict','.pfm','.pgm','.ppm','.png','.psd','.ptx','.pxn',
                                         '.qtk','.raf','.ras','.raw','.rdc','.rgb','.rgba','.rw2','.rwl','.rwz',
                                         '.sgi','.sr2','.srf','.srw','.surface','.sti','.targa','.tga','.tif','.tiff',
                                         '.wap','.wdp','.wbm','.wbmp','.webp','.x3f','.xbm','.xpm'],
        sbsenum.ResourceTypeEnum.LIGHT_PROFILE: ['.ies'],
        sbsenum.ResourceTypeEnum.M_BSDF:['.mbsdf']
    }

    def __init__(self,
                 aIdentifier         = '',
                 aUID                = '',
                 aType               = '',
                 aFormat             = '',
                 aCookedFormat       = None,
                 aCookedQuality      = None,
                 aFilePath           = '',
                 aAttributes         = None,
                 aSource             = None,
                 aTree               = None,
                 aFileAbsPath        = '',
                 aRefDocument        = None,
                 aColorSpace         = None,
                 aPremultipliedAlpha = None):
        super(SBSResource, self).__init__()
        self.mIdentifier         = aIdentifier
        self.mUID                = aUID
        self.mType               = aType
        self.mFormat             = aFormat
        self.mColorSpace         = aColorSpace
        self.mPremultipliedAlpha = aPremultipliedAlpha
        self.mCookedFormat       = aCookedFormat
        self.mCookedQuality      = aCookedQuality
        self.mFilePath           = aFilePath.replace('\\', '/') if aFilePath else aFilePath
        self.mAttributes         = aAttributes
        self.mSource             = aSource
        self.mTree               = aTree
        self.mFileAbsPath        = aFileAbsPath
        self.mRefDocument        = weakref.ref(aRefDocument) if aRefDocument is not None else None

        self.__mPkgResourcePath = None

        self.mMembersForEquality = ['mIdentifier',
                                    'mType',
                                    'mCookedFormat',
                                    'mCookedQuality',
                                    'mFilePath',
                                    'mAttributes',
                                    'mSource',
                                    'mTree']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier         = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'identifier'   )
        self.mUID                = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'uid'          )
        self.mType               = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'type'         )
        self.mFormat             = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'format'       )
        self.mColorSpace         = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'colorSpace'   )
        self.mPremultipliedAlpha = aSBSParser.getXmlElementVAttribValue(aXmlNode,          'premultipliedAlpha' )
        self.mCookedFormat       = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'cookedFormat' )
        self.mCookedQuality      = aSBSParser.getXmlElementVAttribValue(aXmlNode,                'cookedQuality')
        self.mFilePath           = aSBSParser.getXmlFilePathValue(aXmlNode,                      'filepath'     )
        self.mAttributes         = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'attributes'   , sbscommon.SBSAttributes)
        self.mSource             = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'source'       , SBSSource)
        self.mTree               = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode,      'tree'         , sbscommon.SBSTree)

        self.mFileAbsPath = aContext.getUrlAliasMgr().toAbsPath(self.getResolvedFilePath(), aDirAbsPath)
        aContext.addSBSObjectToResolve(self)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIdentifier         , 'identifier'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUID                , 'uid'          )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mType               , 'type'         )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mFormat             , 'format'       )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mColorSpace         , 'colorSpace'   )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mPremultipliedAlpha , 'premultipliedAlpha' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mCookedFormat  , 'cookedFormat' )
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mCookedQuality , 'cookedQuality')
        aSBSWriter.setXmlFilePathValue(aXmlNode, self.mFilePath      ,       'filepath'     )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mAttributes    , 'attributes'   )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mSource        , 'source'       )
        aSBSWriter.writeSBSNode(aXmlNode             , self.mTree          , 'tree')

    def equals(self, other):
        # Allow different case for the format
        if python_helpers.isStringOrUnicode(self.mFormat) and python_helpers.isStringOrUnicode(other.mFormat):
            if self.mFormat.lower() != other.mFormat.lower():
                return False
        return SBSObject.equals(self, other)

    @handle_exceptions()
    def resolveDependency(self, aSBSDocument):
        """
        resolveDependency(aSBSDocument)
        Allow to resolve the dependency of the resource on the root package that contains it.

        :param aSBSDocument: The root document
        :type aSBSDocument: :class:`.SBSDocument`
        """
        self.mRefDocument = weakref.ref(aSBSDocument) if aSBSDocument is not None else None
        self.__computePkgResourcePath(aAllowDependencyCreation=False)

        return self.mRefDocument is not None

    @handle_exceptions()
    def getAllowedAttributes(self):
        """
        getAllowedAttributes()
        Get the attributes allowed on a SBSResource

        :return: the list of attribute enumeration allowed (:class:`.AttributesEnum`)
        """
        return SBSResource.__sAttributes

    @staticmethod
    @handle_exceptions()
    def isAllowedExtension(aResourceType, aExtension):
        """
        isAllowedExtension(aExtension)
        Check if the given extension is allowed for this type of resource

        :param aResourceType: the kind of resource to consider
        :param aExtension: the extension to check (ex: '.png')
        :type aResourceType: :class:`.ResourceTypeEnum` or str
        :type aExtension: str
        :return: True if this extension is allowed for this kind of resource, False otherwise
        """
        if not isinstance(aResourceType, int):
            aResourceType = sbslibrary.getResourceTypeEnum(aResourceType)
        if aResourceType == sbsenum.ResourceTypeEnum.NONE:
            return aExtension.lower()
        return aExtension.lower() in SBSResource.__sAllowedExtensions[aResourceType]

    @handle_exceptions()
    def getAttribute(self, aAttributeIdentifier):
        """
        getAttribute(aAttributeIdentifier)
        Get the given attribute value

        :param aAttributeIdentifier: the attribute identifier
        :type aAttributeIdentifier: :class:`.AttributesEnum`
        :return: the attribute value if defined, None otherwise
        """
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

    @handle_exceptions()
    def setColorSpace(self, aColorSpace, aContext):
        """
        Set colorspace value to apply to the resource bitmap
        :param aColorSpace: str colorspace value
        :param aContext: str colorspace value
        :type aContext: aContext :class:`.Context`
        :return:
        """
        aConfigFile = aContext.getProjectMgr().getOcioConfigFilePath()
        aColorSpaces = ocio_helpers.getColorSpaces(aConfigFile)
        if not aColorSpace in aColorSpaces:
            raise TypeError("Wrong arg for setColorSpace: allowed {0}".format(aColorSpaces))
        self.mColorSpace = aColorSpace

    @handle_exceptions()
    def setPremultipliedAlpha(self, aIsPremultipliedAlpha):
        if not isinstance(aIsPremultipliedAlpha, bool):
            raise TypeError("Wrong arg type for setPremultipliedAlpha: allowed boolean.")
        self.mPremultipliedAlpha = "1" if aIsPremultipliedAlpha is True else "0"

    @handle_exceptions()
    def setCookedFormat(self, aCookedFormat):
        if aCookedFormat != sbsenum.BitmapFormatEnum.RAW and aCookedFormat != sbsenum.BitmapFormatEnum.JPG:
            raise TypeError("Wrong arg type for setCookedFormat: allowed BitmapFormatEnum.RAW or BitmapFormatEnum.JPG.")
        self.mCookedFormat = str(aCookedFormat)

    @handle_exceptions()
    def getPkgResourcePath(self):
        """
        getPkgResourcePath()
        Get the path of the resource relatively to its parent package (pkg:///).

        :return: The path as a string
        """
        if not self.__mPkgResourcePath:
            return self.__computePkgResourcePath(aAllowDependencyCreation=True)
        return self.__mPkgResourcePath

    @handle_exceptions()
    def getResolvedFilePath(self):
        """
        getResolvedFilePath()
        Get the path of the resource relatively to its parent package (SBSDocument)

        :return: The path as a string
        """
        if self.mSource is not None and hasattr(self.mSource, 'mExternalCopy') and self.mSource.mExternalCopy is not None:
            return self.mSource.mExternalCopy.mFilename
        else:
            return self.mFilePath

    @handle_exceptions()
    def getOption(self, aOptionName):
        """
        getOption(aOptionName)
        Get the option identified by the given name

        :return: the option as a :class:`.SBSOption` if found, None otherwise
        """
        return next((aOption for aOption in self.getOptions() if aOption.mName == aOptionName), None)

    @handle_exceptions()
    def getOptions(self):
        """
        getOptions()
        Get all the options defined on this resource

        :return: a list of :class:`.SBSOption`
        """
        return self.mTree.asOptionList()

    @handle_exceptions()
    def getBakingOptions(self):
        """
        getBakingOptions()
        Get all the options related to the baking parameters on this resource

        :return: a list of :class:`.SBSOption`
        """
        #return [aOption for aOption in self.getOptions() if aOption.mName.startswith('baking/')]
        options = self.mTree.asOptionList()
        return [aOption for aOption in options if aOption.mName.startswith('baking/')]

    @handle_exceptions()
    def getSceneOptions(self):
        """
        getSceneOptions()
        Get all the options related to the 3D Scene on this resource

        :return: a list of :class:`.SBSOption`
        """
        options = self.mTree.asOptionList()
        return [aOption for aOption in options if aOption.mName.startswith('scene/')]

    @handle_exceptions()
    def getSceneInfoOptions(self):
        """
        getSceneInfoOptions()
        Get all the options related to the 3D Scene information on this resource

        :return: a list of :class:`.SBSOption`
        """
        options = self.mTree.asOptionList()
        return [aOption for aOption in options if aOption.mName.startswith('sceneInfo/')]

    @handle_exceptions()
    def setOptions(self, aOptions):
        """

        """
        if self.mTree is None:
            self.mTree = sbscommon.SBSTree()
        for option in aOptions:
            self.mTree.setChildByPath(option.mName, option.mValue)

    @handle_exceptions()
    def getResourceTypeEnum(self):
        """
        getResourceTypeEnum()

        :return: the resource type as a :class:`.ResourceTypeEnum` if defined, None otherwise
        """
        return sbslibrary.getResourceTypeEnum(self.mType) if self.mType else None

    @handle_exceptions()
    def createBakingParameters(self):
        """
        createBakingParameters()
        Create the baking parameters for this Scene resource, and init all required values.
        No converter is added by default.

        :return: The :class:`.BakingParameters` object created
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if self.mType != 'scene':
            raise SBSImpossibleActionError('Cannot set Baking parameters: The resource is not a SCENE')

        aSubMeshColors = [sbsbakers.SubMeshColor()]
        aSubMeshSelections = [sbsbakers.SubMeshSelection()]

        return sbsbakers.BakingParameters(aSubMeshColors=aSubMeshColors,
                                          aSubMeshSelections=aSubMeshSelections)

    @handle_exceptions()
    def getBakingParameters(self):
        """
        getBakingParameters()
        Decode the baking parameters option and convert it into an editable object structure

        :return: The baking parameters as a :class:`.BakingParameters` object if defined, None otherwise
        """
        if not self.mTree:
            return None
        else:
            bakingParams = sbsbakers.BakingParameters()
            bakingParams.fromSBSTree(self.mTree)
        return bakingParams

    @handle_exceptions()
    def setBakingParameters(self, aBakingParameters):
        """
        setBakingParameters(aBakingParameters)
        Set the given baking parameters on this resource.
        The function converts the baking parameters into a list of SBSOptions, as saved in .sbs format.
        All the previous options related to Baking Parameters will be removed before creating the new ones.
        Raise an exception if the resource is not a Scene.

        :param aBakingParameters: The baking parameters to set
        :type aBakingParameters: :class:`.BakingParameters`
        :return: Nothing
        :raise: :class:`api_exceptions.SBSImpossibleActionError`
        """
        if self.mType != 'scene':
            raise SBSImpossibleActionError('Cannot set Baking parameters: The resource is not a SCENE')

        # Keep the scene options as is
        if self.mTree is None:
            self.mTree = sbscommon.SBSTree()

        # Clean out old baking parameters if they exist
        if 'baking' in self.mTree.mTreeElements:
            del self.mTree.mTreeElements['baking']


        # Convert the given baking parameters into a list of SBSOption
        newBakingOptions = aBakingParameters.toSBSOptionList()
        for o in newBakingOptions:
            self.mTree.setChildByPath(o.mName, o.mValue)

    @handle_exceptions()
    def isLinked(self):
        """
        isLinked()

        :return: True if the resource is just linked with its path to the document (by opposition to imported)
        """
        return self.mSource is None

    @handle_exceptions()
    def setResourceIsBakingOutput(self, aBakedSceneResource, aBaker):
        """
        setResourceIsBakingOutput(aBakedSceneResource, aBaker)
        Declare this Bitmap resource as the output of a Baking process

        :param aBakedSceneResource: The scene resource used to bake maps
        :type aBakedSceneResource: :class:`.SBSResourceScene`
        :param aBaker: The baker used (as a BakerEnum or an identifier, for instance 'Curvature Map from Mesh [2]')
        :type aBaker: :class:`.BakerEnum` or str
        :return:
        """
        if self.mType not in [sbslibrary.getResourceTypeName(sbsenum.ResourceTypeEnum.BITMAP),
                              sbslibrary.getResourceTypeName(sbsenum.ResourceTypeEnum.SVG)]:
            raise SBSImpossibleActionError('Only a Bitmap or SVG resource can be set as the output of a baking process')

        if not isinstance(aBakedSceneResource, SBSResourceScene):
            raise SBSImpossibleActionError('Only a SBSResourceScene can be used to define a baking dependency on')

        if self.mTree is None:
           self.mTree = sbscommon.SBSTree()

        optionsData = [('BakingDependencyUrl', aBakedSceneResource.getPkgResourcePath(), True),
                       ('BakingResourceOptions', aBaker if isinstance(aBaker, str) else sbsbakers.getBakerDefaultIdentifier(aBaker=aBaker), False)]

        for optName, optValue, asUrl in optionsData:
            self.mTree.setChildByPath(optName, optValue, asURL=asUrl)

    @handle_exceptions()
    def getPhysicalResourceList(self):
        """
        getPhysicalResourceList()
        Get the list of physical files associated to this resource.
        This allow for the particular case of a resource pointing to the output of a baking with Udims, to get the list of corresponding files.

        :return: a list of string
        """
        resourceName = os.path.basename(self.mFileAbsPath)
        if '$(udim)' in resourceName:
            folderName = os.path.dirname(self.mFileAbsPath)
            splitList = resourceName.split('$(udim)')
            return glob.glob(os.path.join(folderName, '[0-9]*'.join(splitList)))
        else:
            return [self.mFileAbsPath]


    #==========================================================================
    # Private
    #==========================================================================
    @handle_exceptions()
    def __computePkgResourcePath(self, aAllowDependencyCreation=False):
        """
        __computePkgResourcePath(aAllowDependencyCreation)
        Compute the path relatively to the SBSDocument that contains this resource: 'pkg:///pathToTheResource/resourceIdentifier?dependency=DocumentUID'.

        :param aAllowDependencyCreation: True to allow the creation of the 'himself' dependency on the parent document
        :type aAllowDependencyCreation: bool
        :return: the
        """
        docHimSelf = self.mRefDocument().getHimselfDependency()
        if not docHimSelf and aAllowDependencyCreation:
            self.mRefDocument().createHimselfDependency()
            docHimSelf = self.mRefDocument().getHimselfDependency()
        if docHimSelf:
            self.__mPkgResourcePath = self.mRefDocument().getSBSResourceInternalPath(self.mUID)
            if self.__mPkgResourcePath is not None:
                self.__mPkgResourcePath += '?dependency=' + self.mRefDocument().getHimselfDependency().mUID
        return self.__mPkgResourcePath



# ==============================================================================
@doc_inherit
class SBSResourceScene(SBSResource):
    """
    Class that contains information on a substance scene/mesh resource as defined in a .sbs file

    Members:
        * mIdentifier       (str): identifier of the file.
        * mUID              (str): unique identifier of this resource in the package/ context.
        * mType             (str): type of the resource ('bitmap','svg',...)
        * mFormat           (str): original format of the resource (e.g. BMP, JPG for bitmap type resources).
        * mCookedFormat     (str, optional): format of the resource after the cooking stage (among :class:`.BitmapFormatEnum` for bitmap resources)
        * mCookedQuality    (float as a string, optional): quality of resource after the cooking stage (percentage for a bitmap type with a cookedFormat JPEG).
        * mFilePath         (str): path and name of the origin file.
        * mAttributes       (:class:`.SBSAttributes`): various attributes (author, description, ...)
        * mSource           (:class:`.SBSSource`): embedded or managed source.
        * mOptions          (:class:`.SBSOption`): additional options.
        * mIsUdim           (str, optional): flag indicating whether this scene must be managed as a mesh unwrapped on multiple UV-tiles
        * mSceneMaterialMap (list of :class:`.SBSSceneMaterialMapEntry`): An associative list that store material-graph affectation for the scene resource.
    """
    def __init__(self,
                 aIdentifier       = '',
                 aUID              = '',
                 aType             = '',
                 aFormat           = '',
                 aCookedFormat     = None,
                 aCookedQuality    = None,
                 aFilePath         = '',
                 aAttributes       = None,
                 aSource           = None,
                 aOptions          = None,
                 aFileAbsPath      = '',
                 aRefDocument      = None,
                 aIsUdim           = None,
                 aSceneMaterialMap = None):
        super(SBSResourceScene, self).__init__(aIdentifier   ,
                                               aUID          ,
                                               aType         ,
                                               aFormat       ,
                                               aCookedFormat ,
                                               aCookedQuality,
                                               aFilePath     ,
                                               aAttributes   ,
                                               aSource       ,
                                               aOptions      ,
                                               aFileAbsPath  ,
                                               aRefDocument  )
        self.mIsUdim = aIsUdim
        self.mSceneMaterialMap = aSceneMaterialMap
        self.mMembersForEquality.extend(['mIsUdim','mSceneMaterialMap'])

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        super(SBSResourceScene, self).parse(aContext, aDirAbsPath, aSBSParser, aXmlNode)
        self.mIsUdim           = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'isUdim')
        self.mSceneMaterialMap = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'sceneMaterialMap', 'sceneMaterialMapEntry', SBSSceneMaterialMapEntry)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        super(SBSResourceScene, self).write(aSBSWriter, aXmlNode)
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mIsUdim, 'isUdim'   )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mSceneMaterialMap, 'sceneMaterialMap', 'sceneMaterialMapEntry' )

    @handle_exceptions()
    def setMaterialMapEntries(self, aMaterialsList, nbUVSet=1):
        """
        setMaterialMapEntries(aMaterialsList, nbUVSet=1)
        Init the material map entries given the list of materials of the mesh resource.

        :param aMaterialsList: list of material names
        :type aMaterialsList: list of str
        :param nbUVSet: number of UV-sets of the mesh. Default to 1
        :type nbUVSet: int, optional
        """
        self.mSceneMaterialMap = []
        for aMat in aMaterialsList:
            uvSetMaterialMapList = []
            for _ in range(nbUVSet):
                uvSetMaterialMapList.append(SBSUVSetMaterialMapEntry(aUVTiles='all', aMaterial=SBSUVSetMaterial()))

            self.mSceneMaterialMap.append(SBSSceneMaterialMapEntry(aSceneMaterialName=aMat,
                                                                   aUVSetMaterialMapList=[SBSUVSetMaterialMap(aEntries=uvSetMaterialMapList)]))

    @handle_exceptions()
    def getMaterialMapEntry(self, aMaterialName):
        """
        getMaterialMapEntry(aMaterialName)
        Get the material map entry corresponding to the given material name

        :param aMaterialName: The material name to look for
        :type aMaterialName: str
        :return: a :class:`.SBSSceneMaterialMapEntry` if found, None otherwise
        """
        return next((m for m in self.getMaterialMapEntries() if m.mSceneMaterialName == aMaterialName), None)

    @handle_exceptions()
    def getMaterialMapEntries(self):
        """
        getMaterialMapEntries()
        Get the list of material entries of this scene resource

        :return: a list of :class:`.SBSSceneMaterialMapEntry`
        """
        return self.mSceneMaterialMap if self.mSceneMaterialMap is not None else []



# ==============================================================================
@doc_inherit
class SBSSceneMaterialMapEntry(SBSObject):
    """
    Class that contains the description of the affections for a given material of the :class:`.SBSResourceScene`

    Members:
        * mSceneMaterialName    (str): the affected material name.
        * mUVSetMaterialMapList (list of :class:`.SBSUVSetMaterialMap`): a list that describe the affectations by UV-set
    """
    def __init__(self,
                 aSceneMaterialName='',
                 aUVSetMaterialMapList=None):
        super(SBSSceneMaterialMapEntry, self).__init__()
        self.mSceneMaterialName = aSceneMaterialName
        self.mUVSetMaterialMapList = aUVSetMaterialMapList

        self.mMembersForEquality = ['mSceneMaterialName',
                                    'mUVSetMaterialMapList']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mSceneMaterialName = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'sceneMaterialName')
        self.mUVSetMaterialMapList = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'uvSetMaterialMapList', 'uvSetMaterialMap', SBSUVSetMaterialMap)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mSceneMaterialName, 'sceneMaterialName')
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mUVSetMaterialMapList, 'uvSetMaterialMapList', 'uvSetMaterialMap' )

    @handle_exceptions()
    def getAllUVTilesAssociatedToGraph(self, aGraphPath, aUVTileFormat=sbsenum.UVTileFormat.UDIM, aUVSet=0):
        """
        getAllUVTilesAssociatedToGraph(aGraphPath, aUVTileFormat=sbsenum.UVTileFormat.UDIM, aUVSet=0)
        Get the list of UV-tiles associated to the given graph internal path (pkg://...), for the given UV-set.

        :param aGraphPath: The internal path of the graph to consider (pkg://...)
        :type aGraphPath: str
        :param aUVTileFormat: The format desired for the UV-tiles. Default to UDIM
        :type aUVTileFormat: :class:`.UVTileFormat`, optional
        :param aUVSet: The index of the UV-set to consider. Default to 0
        :type aUVSet: int, optional
        :return: the list of UV-tiles in the expected format
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            print("There is no material map associated to this UV-set %s" % aUVSet)
            return []
        return matMap.getAllUVTilesAssociatedToGraph(aGraphPath, aUVTileFormat)

    @handle_exceptions()
    def getUVSetMaterialMap(self, aUVSet=0):
        """
        getUVSetMaterialMap(aUVSet = 0)
        Get the uvSetMaterialMap corresponding to the given UV-set number, for the given UV-set.

        :param aUVSet: The index of the UV-set to consider. Default to 0
        :type aUVSet: int, optional
        :return: a :class:`.SBSUVSetMaterialMap` object if found, None otherwise
        """
        return self.mUVSetMaterialMapList[aUVSet] if self.mUVSetMaterialMapList and 0 <= aUVSet < len(self.mUVSetMaterialMapList) else None

    @handle_exceptions()
    def getUVSetMaterialMapEntry(self, aUVTile, aUVSet = 0):
        """
        getUVSetMaterialMapEntry(aUVTile, aUVSet=0)
        Get the uvSetMaterialMapEntry corresponding to the given UV-tile and UV-set, for the given UV-set.

        :param aUVTile: Id of the UV-tile to get, as saved in the .sbs format ('0x0' for instance), or 'all' to ge the material map entry corresponding to all UV-tiles
        :type aUVTile: str
        :param aUVSet: The index of the UV-set to consider. Default to 0
        :type aUVSet: int, optional
        :return: a :class:`.SBSUVSetMaterialMapEntry` if found, None otherwise
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        return matMap.getUVSetMaterialMapEntry(aUVTile) if matMap else None

    @handle_exceptions()
    def getUVSetMaterialMapEntries(self, aUVSet = 0):
        """
        getUVSetMaterialMapEntries(aUVSet=0)
        Get the list of SBSUVSetMaterialMapEntry in this SBSUVSetMaterialMap, for the given UV-set.

        :param aUVSet: The index of the UV-set to consider. Default to 0
        :type aUVSet: int, optional
        :return: a list of :class:`.SBSUVSetMaterialMapEntry`
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        return matMap.getUVSetMaterialMapEntries() if matMap else None

    @handle_exceptions()
    def assignDefaultSBSGraph(self, aGraphPath, aUVSet = 0):
        """
        assignDefaultSBSGraph(aGraphPath, aUVSet=0)
        Assign the given SBSGraph as the default for all UV-tiles.

        :param aGraphPath: The compositing graph to assign, given its internal path (pkg:///myGraph)
        :type aGraphPath: str
        :param aUVSet: The index of the UV-set to modify. Default to 0
        :type aUVSet: int, optional
        :return: the :class:`.SBSUVSetMaterialMapEntry` corresponding to the assignment
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            raise SBSImpossibleActionError("Cannot affect UV-set %d, cannot find a UVSetMaterialMapEntry corresponding to this UV-set" % aUVSet)
        return matMap.assignDefaultSBSGraph(aGraphPath)

    @handle_exceptions()
    def assignSBSGraphToUVTile(self, aGraphPath, aUVTile, aUVSet = 0):
        """
        assignSBSGraphToUVTile(aGraphPath, aUVTile, aUVSet=0)
        Assign the given UV-tile to the given SBSGraph, for the given UV-set.

        :param aGraphPath: The compositing graph to assign, given its internal path (pkg:///myGraph)
        :type aGraphPath: str
        :param aUVTile: The UV-tile to affect (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) ), or 'all' to assign this graph to all UV-tiles
        :type aUVTile: str, list or tuple
        :param aUVSet: The index of the UV-set to modify. Default to 0
        :type aUVSet: int, optional
        :return: the :class:`.SBSUVSetMaterialMapEntry` corresponding to the assignment
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            raise SBSImpossibleActionError("Cannot affect UV-set %d, cannot find a UVSetMaterialMapEntry corresponding to this UV-set" % aUVSet)
        return matMap.assignSBSGraphToUVTile(aGraphPath, aUVTile)

    @handle_exceptions()
    def assignSBSGraphToUVTiles(self, aGraphPath, aUVTileList, aUVSet = 0):
        """
        assignSBSGraphToUVTiles(aGraphPath, aUVTileList, aUVSet=0)
        Assign the given list of UV-tile to the given SBSGraph, for the given UV-set.

        :param aGraphPath: The compositing graph to assign, given its internal path (pkg:///myGraph)
        :type aGraphPath: str
        :param aUVTileList: The list of UV-tiles to affect (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) )
        :type aUVTileList: list
        :param aUVSet: The index of the UV-set to modify. Default to 0
        :type aUVSet: int, optional
        :return: the list of :class:`.SBSUVSetMaterialMapEntry` corresponding to the assignments
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            raise SBSImpossibleActionError("Cannot affect UV-set %d, cannot find a UVSetMaterialMapEntry corresponding to this UV-set" % aUVSet)
        return matMap.assignSBSGraphToUVTiles(aGraphPath, aUVTileList)

    @handle_exceptions()
    def removeAllAssignationsToGraph(self, aGraphPath, aUVSet = 0):
        """
        removeAllAssignationsToGraph(aGraphPath, aUVSet=0)
        Remove all the entries (:class:`.SBSUVSetMaterialMapEntry`) associated to the given graph, in the given UV-set.

        :param aGraphPath: The internal path of the graph to consider (pkg://...)
        :type aGraphPath: str
        :param aUVSet: The index of the UV-set to modify. Default to 0
        :type aUVSet: int, optional
        :return: the number of entries removed
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            raise SBSImpossibleActionError("Cannot affect UV-set %d, cannot find a UVSetMaterialMapEntry corresponding to this UV-set" % aUVSet)
        return matMap.removeAllAssignationsToGraph(aGraphPath)

    @handle_exceptions()
    def removeDefaultUVTileAssignation(self, aUVSet = 0):
        """
        removeDefaultUVTileAssignation(aUVSet=0)
        Remove the entry (:class:`.SBSUVSetMaterialMapEntry`) associated by default, in the given UV-set.

        :param aUVSet: The index of the UV-set to modify. Default to 0
        :type aUVSet: int, optional
        :return: True if the UV-tile is found and removed, False otherwise
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            raise SBSImpossibleActionError("Cannot affect UV-set %d, cannot find a UVSetMaterialMapEntry corresponding to this UV-set" % aUVSet)
        return matMap.removeDefaultUVTileAssignation()

    @handle_exceptions()
    def removeUVTileAssignation(self, aUVTile, aUVSet = 0):
        """
        removeUVTileAssignation(aUVTile, aUVSet=0)
        Remove the entry (:class:`.SBSUVSetMaterialMapEntry`) associated to the given UV-tile, in the given UV-set.

        :param aUVTile: The UV-tile to look for (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) ), or 'all' to look for the default assignation
        :type aUVTile: string, list or tuple
        :param aUVSet: The index of the UV-set to modify. Default to 0
        :type aUVSet: int, optional
        :return: True if the UV-tile is found and removed, False otherwise
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            raise SBSImpossibleActionError("Cannot affect UV-set %d, cannot find a UVSetMaterialMapEntry corresponding to this UV-set" % aUVSet)
        return matMap.removeUVTileAssignation(aUVTile)

    @handle_exceptions()
    def removeUVTilesAssignation(self, aUVTileList, aUVSet = 0):
        """
        removeUVTilesAssignation(aUVTileList, aUVSet=0)
        Remove the entries (:class:`.SBSUVSetMaterialMapEntry`) associated to the given UV-tile list, in the given UV-set.

        :param aUVTileList: The list of UV-tile to look for (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) )
        :type aUVTileList: list
        :param aUVSet: The index of the UV-set to modify. Default to 0
        :type aUVSet: int, optional
        :return: the number of entries removed
        """
        matMap = self.getUVSetMaterialMap(aUVSet)
        if matMap is None:
            raise SBSImpossibleActionError("Cannot affect UV-set %d, cannot find a UVSetMaterialMapEntry corresponding to this UV-set" % aUVSet)
        return matMap.removeUVTilesAssignation(aUVTileList)



# ==============================================================================
@doc_inherit
class SBSUVSetMaterialMap(SBSObject):
    """
    Class that describe the affectations for a given UV-set

    Members:
        * mEntries        (list of :class:`.SBSUVSetMaterialMapEntry`): a list that associates a graph to one or more UV-tile
        * mOptionsByGraph (list of :class:`.SBSOptionsByUrlMapEntry`, optional): a map that lists options for some graph edited in the context of the current :class:`.SBSUVSetMaterialMap`.
    """
    def __init__(self,
                 aEntries = None,
                 aOptionsByGraph = None):
        super(SBSUVSetMaterialMap, self).__init__()
        self.mEntries        = aEntries
        self.mOptionsByGraph = aOptionsByGraph

        self.mMembersForEquality = ['mEntries',
                                    'mOptionsByGraph']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mEntries        = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'entries',        'uvSetMaterialMapEntry', SBSUVSetMaterialMapEntry)
        self.mOptionsByGraph = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'optionsByGraph', 'optionsByUrlMapEntry',  SBSOptionsByUrlMapEntry)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mEntries,        'entries',        'uvSetMaterialMapEntry' )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mOptionsByGraph, 'optionsByGraph', 'optionsByUrlMapEntry'  )

    @handle_exceptions()
    def assignDefaultSBSGraph(self, aGraphPath):
        """
        assignDefaultSBSGraph(aGraphPath)
        Assign the given SBSGraph as the default for all UV-tiles.

        :param aGraphPath: The compositing graph to assign, given its internal path (pkg:///myGraph)
        :type aGraphPath: str
        :return: the :class:`.SBSUVSetMaterialMapEntry` corresponding to the assignment
        """
        return self.assignSBSGraphToUVTile(aGraphPath=aGraphPath, aUVTile='all')

    @handle_exceptions()
    def assignSBSGraphToUVTile(self, aGraphPath, aUVTile):
        """
        assignSBSGraphToUVTile(aGraphPath, aUVTile)
        Assign the given SBSGraph to the given UV-tile.

        :param aGraphPath: The compositing graph to assign, given its internal path (pkg:///myGraph)
        :type aGraphPath: str
        :param aUVTile: The UV-tile to affect (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) ), or 'all' to assign this graph to all UV-tiles
        :type aUVTile: str, list or tuple
        :return: the :class:`.SBSUVSetMaterialMapEntry` corresponding to the assignment
        """
        aUVTile = api_helpers.formatUVTileToSBSFormat(aUVTile)
        matMapEntry = self.getUVSetMaterialMapEntry(aUVTile)
        if matMapEntry is None:
            matMapEntry = SBSUVSetMaterialMapEntry()
            api_helpers.addObjectToList(self, 'mEntries', matMapEntry)
        matMapEntry.mUVTiles = aUVTile
        matMapEntry.mMaterial = SBSUVSetMaterial(aSBSGraphUrl=aGraphPath)
        return matMapEntry

    @handle_exceptions()
    def assignSBSGraphToUVTiles(self, aGraphPath, aUVTileList):
        """
        assignSBSGraphToUVTiles(aGraphPath, aUVTileList)
        Assign the given SBSGraph to the given list of UV-tile.

        :param aGraphPath: The compositing graph to assign, given its internal path (pkg:///myGraph)
        :type aGraphPath: str
        :param aUVTileList: The list of UV-tiles to affect (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) )
        :type aUVTileList: list
        :return: the list of :class:`.SBSUVSetMaterialMapEntry` corresponding to the assignments
        """
        return [self.assignSBSGraphToUVTile(aGraphPath, aUVTile) for aUVTile in aUVTileList]

    @handle_exceptions()
    def getAllEntriesAssociatedToGraph(self, aGraphPath):
        """
        getAllEntriesAssociatedToGraph(aGraphPath)
        Get the list of entries associated to the given graph internal path (pkg://...)

        :param aGraphPath: The internal path of the graph to consider (pkg://...)
        :type aGraphPath: str
        :return: a list of :class:`.SBSUVSetMaterialMapEntry`
        """
        return [e for e in self.getUVSetMaterialMapEntries() if e.getGraphPath() == aGraphPath]

    @handle_exceptions()
    def getAllUVTilesAssociatedToGraph(self, aGraphPath, aUVTileFormat = sbsenum.UVTileFormat.UDIM):
        """
        getAllUVTilesAssociatedToGraph(aGraphPath, UVTileFormat = sbsenum.UVTileFormat.UDIM)
        Get the list of UV-tiles associated to the given graph internal path (pkg://...)

        :param aGraphPath: The internal path of the graph to consider (pkg://...)
        :type aGraphPath: str
        :param aUVTileFormat: The format desired for the UV-tiles. Default to UDIM
        :type aUVTileFormat: :class:`.UVTileFormat`, optional
        :return: the list of UV-tiles in the expected format
        """
        return [api_helpers.convertUVTileToFormat(e.mUVTiles, aUVTileFormat) for e in self.getAllEntriesAssociatedToGraph(aGraphPath)]

    @handle_exceptions()
    def getUVSetMaterialMapEntries(self):
        """
        getUVSetMaterialMapEntries()
        Get the list of SBSUVSetMaterialMapEntry in this SBSUVSetMaterialMap

        :return: a list of :class:`.SBSUVSetMaterialMapEntry`
        """
        return self.mEntries if self.mEntries is not None else []

    @handle_exceptions()
    def getUVSetMaterialMapEntry(self, aUVTile):
        """
        getUVSetMaterialMapEntry(aUVTile)
        Get the SBSUVSetMaterialMapEntry corresponding to this UVTile

        :param aUVTile: The UV-tile to look for (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) ), or 'all' to look for the default assignation
        :type aUVTile: string, list or tuple
        :return: a :class:`.SBSUVSetMaterialMapEntry` if found, None otherwise
        """
        aUVTile = api_helpers.formatUVTileToSBSFormat(aUVTile)
        return next((e for e in self.getUVSetMaterialMapEntries() if e.mUVTiles == aUVTile), None)

    @handle_exceptions()
    def getGraphAssignedByDefault(self):
        """
        getGraphAssignedByDefault()
        Get the path of the graph assigned by default to all UV-tiles

        :return: the graph internal path as a string if found, None otherwise
        """
        return self.getUVSetMaterialMapEntry(aUVTile='all')

    @handle_exceptions()
    def getGraphAssignedToUVTile(self, aUVTile):
        """
        getGraphAssignedToUVTile(aUVTile)
        Get the path of the graph assigned to this UVTile

        :param aUVTile: The UV-tile to look for (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) )
        :type aUVTile: string, list or tuple
        :return: the graph internal path as a string if found, None otherwise
        """
        entry = self.getUVSetMaterialMapEntry(aUVTile)
        return entry.getGraphPath() if entry else None

    @handle_exceptions()
    def removeAllAssignationsToGraph(self, aGraphPath):
        """
        removeAllAssignationsToGraph(aGraphPath)
        Remove all the entries (:class:`.SBSUVSetMaterialMapEntry`) associated to the given graph

        :param aGraphPath: The internal path of the graph to consider (pkg://...)
        :type aGraphPath: str
        :return: the number of entries removed
        """
        entriesToRemove = self.getAllEntriesAssociatedToGraph(aGraphPath)
        for e in entriesToRemove:
            self.mEntries.remove(e)
        return len(entriesToRemove)

    @handle_exceptions()
    def removeDefaultUVTileAssignation(self):
        """
        removeDefaultUVTileAssignation()
        Remove the entry (:class:`.SBSUVSetMaterialMapEntry`) associated by default

        :return: True if the UV-tile is found and removed, False otherwise
        """
        return self.removeUVTileAssignation(aUVTile='all')

    @handle_exceptions()
    def removeUVTileAssignation(self, aUVTile):
        """
        removeUVTileAssignation(aUVTile)
        Remove the entry (:class:`.SBSUVSetMaterialMapEntry`) associated to the given UV-tile

        :param aUVTile: The UV-tile to look for (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) ), or 'all' to look for the default assignation
        :type aUVTile: string, list or tuple
        :return: True if the UV-tile is found and removed, False otherwise
        """
        entry = self.getUVSetMaterialMapEntry(aUVTile)
        if entry:
            self.mEntries.remove(entry)
        return entry is not None

    @handle_exceptions()
    def removeUVTilesAssignation(self, aUVTileList):
        """
        removeUVTilesAssignation(aUVTileList)
        Remove the entries (:class:`.SBSUVSetMaterialMapEntry`) associated to the given UV-tile list

        :param aUVTileList: The list of UV-tile to look for (different format accepted: 'UDIM', 'u{U}_v{V}', '{U}x{V}', [U,V], (U,V) )
        :type aUVTileList: list
        :return: the number of entries removed
        """
        count = 0
        for aUVTile in aUVTileList:
            count += int(self.removeUVTileAssignation(aUVTile))
        return count



# ==============================================================================
@doc_inherit
class SBSUVSetMaterialMapEntry(SBSObject):
    """
    Class that associate a *graph* to one or more UV-tile

    Members:
        * mUVTiles  (str): a formatted string that list the UV-tiles of this entry. Might be "all" or the UV-tile coordinate formatted as "{U}x{V}"
        * mMaterial (:class:`.SBSUVSetMaterial`): the description of the affected material.
    """
    def __init__(self,
                 aUVTiles  = 'all',
                 aMaterial = None):
        super(SBSUVSetMaterialMapEntry, self).__init__()
        self.mUVTiles  = aUVTiles
        self.mMaterial = aMaterial

        self.mMembersForEquality = ['mUVTiles',
                                    'mMaterial']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUVTiles  = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'uvTiles')
        self.mMaterial = aSBSParser.parseSBSNode(aContext, aDirAbsPath, aXmlNode, 'material', SBSUVSetMaterial)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mUVTiles,  'uvTiles'  )
        aSBSWriter.writeSBSNode(aXmlNode,              self.mMaterial, 'material' )

    @handle_exceptions()
    def getGraphPath(self):
        """
        getGraphPath()
        Get the graph internal path associated to this UV-tile

        :return: the path as a string if defined, None otherwise
        """
        return self.mMaterial.mSBSGraphUrl if self.mMaterial is not None else None



# ==============================================================================
@doc_inherit
class SBSUVSetMaterial(SBSObject):
    """
    Class that contains the description of the affected material. It only contains a reference to a graph at the moment, but it may be extended in the future.

    Members:
        * mSBSGraphUrl (str): path of the graph definition.
    """
    def __init__(self, aSBSGraphUrl = ''):
        super(SBSUVSetMaterial, self).__init__()
        self.mSBSGraphUrl = aSBSGraphUrl

        self.mMembersForEquality = ['mSBSGraphUrl']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mSBSGraphUrl = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'sbsGraphUrl')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mSBSGraphUrl, 'sbsGraphUrl')



# ==============================================================================
@doc_inherit
class SBSOptionsByUrlMapEntry(SBSObject):
    """
    Class that list options for a graph in the context of the parent :class:`.SBSUVSetMaterialMap`.

    Members:
        * mURL     (str): path of the graph definition to which the options apply.
        * mOptions (list of :class:`.SBSOption`, optional): the options associated with this graph in the current context.
    """
    def __init__(self,
                 aURL  = '',
                 aOptions = None):
        super(SBSOptionsByUrlMapEntry, self).__init__()
        self.mURL     = aURL
        self.mOptions = aOptions

        self.mMembersForEquality = ['mURL',
                                    'mOptions']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mURL     = aSBSParser.getXmlElementVAttribValue(aXmlNode, 'url')
        self.mOptions = aSBSParser.getSBSElementList(aContext, aDirAbsPath, aXmlNode, 'options', 'option', sbscommon.SBSOption)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementVAttribValue(aXmlNode, self.mURL,  'url'  )
        aSBSWriter.writeListOfSBSNode(aXmlNode, self.mOptions, 'options', 'option')
