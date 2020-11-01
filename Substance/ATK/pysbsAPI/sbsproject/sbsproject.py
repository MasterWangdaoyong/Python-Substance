# coding: utf-8
"""
Module **sbsproject** aims to define sbsprj files, with helpers for read it correctly
"""

from __future__ import unicode_literals
import os
import platform
import logging
log = logging.getLogger(__name__)

from pysbs.api_decorators import doc_inherit,handle_exceptions, doc_source_code_enum
from pysbs.common_interfaces import SBSObject
from pysbs import sbsparser


ACES_VERSION = 'aces_1.0.3'
CURRENT_SBSPRJ = ''

@doc_source_code_enum
class SBSPRJParams:
    """
    Enumeration for properties in the sbsprj file
    """
    @staticmethod
    def _convert_to_lower(arg):
        if platform.system() == 'Windows':
            return arg.lower()
        return arg
    ACTIONS                             =_convert_to_lower.__func__("actions")
    ALWAYSRECOMPUTETANGENTFRAME         =_convert_to_lower.__func__("alwaysrecomputetangentframe")
    BAKERID                             =_convert_to_lower.__func__("bakerID")
    BAKERS                              =_convert_to_lower.__func__("bakers")
    BAKERSMACROS                        =_convert_to_lower.__func__("bakersMacros")
    BMP                                 =_convert_to_lower.__func__("bmp")
    BMP_COMPRESSION                     =_convert_to_lower.__func__("bmp_compression")
    COLORMANAGEMENT                     =_convert_to_lower.__func__("colormanagement")
    COLORMANAGEMENTENGINE               =_convert_to_lower.__func__("colorManagementEngine")
    DEFAULTENVIRONMENTMAPURL            =_convert_to_lower.__func__("defaultEnvironmentMapUrl")
    DEFAULTRESOURCENAME                 =_convert_to_lower.__func__("defaultResourceName")
    DEFAULTSHADERURL                    =_convert_to_lower.__func__("defaultShaderUrl")
    DEPENDENCIES                        =_convert_to_lower.__func__("dependencies")
    DIRS                                =_convert_to_lower.__func__("dirs")
    EXCLUDEFILTER                       =_convert_to_lower.__func__("excludeFilter")
    EXR                                 =_convert_to_lower.__func__("exr")
    EXR_COMPRESSION                     =_convert_to_lower.__func__("exr_compression")
    EXR_LC                              =_convert_to_lower.__func__("exr_lc")
    EXR_USE_FLOAT                       =_convert_to_lower.__func__("exr_use_float")
    EXT                                 =_convert_to_lower.__func__("ext")
    GENERAL                             =_convert_to_lower.__func__("general")
    ID                                  =_convert_to_lower.__func__("id")
    IMAGE_OPTIONS                       =_convert_to_lower.__func__("image_options")
    INTERPRETERS                        =_convert_to_lower.__func__("interpreters")
    IRAY                                =_convert_to_lower.__func__("iray")
    IS_ENABLED                          =_convert_to_lower.__func__("is_enabled")
    ISAMBIENTLIGHTENABLE                =_convert_to_lower.__func__("isAmbientLightEnable")
    ISENABLED                           =_convert_to_lower.__func__("isEnabled")
    ISPOINTLIGHT1ENABLE                 =_convert_to_lower.__func__("isPointLight1Enable")
    ISPOINTLIGHT2ENABLE                 =_convert_to_lower.__func__("isPointLight2Enable")
    ISRECURSIVE                         =_convert_to_lower.__func__("isRecursive")
    ISVISIBLE                           =_convert_to_lower.__func__("isVisible")
    JPG                                 =_convert_to_lower.__func__("jpg")
    JPG_OPTIMIZE                        =_convert_to_lower.__func__("jpg_optimize")
    JPG_PROGRESSIVE                     =_convert_to_lower.__func__("jpg_progressive")
    JPG_QUALITY                         =_convert_to_lower.__func__("jpg_quality")
    KEY                                 =_convert_to_lower.__func__("key")
    LABEL                               =_convert_to_lower.__func__("label")
    LIBRARY                             =_convert_to_lower.__func__("library")
    MACROS                              =_convert_to_lower.__func__("macros")
    MDL                                 =_convert_to_lower.__func__("mdl")
    MDL_PATHS                           =_convert_to_lower.__func__("mdl_paths")
    MESHID                              =_convert_to_lower.__func__("meshID")
    NAME                                =_convert_to_lower.__func__("name")
    NAMEFILTER                          =_convert_to_lower.__func__("nameFilter")
    NAMEFILTERS                         =_convert_to_lower.__func__("nameFilters")
    NEAR_OR_UNDER                       =_convert_to_lower.__func__("near_or_under")
    NORMAL_FILTER_ALPHA_CHANNEL_CONTENT =_convert_to_lower.__func__("normal_filter_alpha_channel_content")
    NORMAL_MAP_FORMAT                   =_convert_to_lower.__func__("normal_map_format")
    NOT_NEAR_OR_UNDER                   =_convert_to_lower.__func__("not_near_or_under")
    OCIO                                =_convert_to_lower.__func__("ocio")
    OCIOFLOATBITMAPCOLORSPACE           =_convert_to_lower.__func__("ocioFloatBitmapColorSpace")
    OCIODEFAULTVIEW                     =_convert_to_lower.__func__("ocioDefaultView")
    OCIODEFAULTDISPLAY                  =_convert_to_lower.__func__("ocioDefaultDisplay")
    OCIOCUSTOMCONFIGPATH                =_convert_to_lower.__func__("ocioCustomConfigPath")
    OCIOCONFIG                          =_convert_to_lower.__func__("ocioConfig")
    OCIOCOLORMANAGEGRAPHTHUMBNAILS      =_convert_to_lower.__func__("ocioColorManageGraphThumbnails")
    OCIOAUTODETECTCOLORSPACEINFILENAME  =_convert_to_lower.__func__("ocioAutoDetectColorSpaceInFileName")
    OCIO8BITBITMAPCOLORSPACE            =_convert_to_lower.__func__("ocio8BitBitmapColorSpace")
    OCIO16BITBITMAPCOLORSPACE           =_convert_to_lower.__func__("ocio16BitBitmapColorSpace")
    ACE                                 =_convert_to_lower.__func__("ace")
    ACEUSEEMBEDDEDPROFILES              =_convert_to_lower.__func__("aceUseEmbeddedProfiles")
    ACERENDERINGINTENT                  =_convert_to_lower.__func__("aceRenderingIntent")
    ACEFLOATBITMAPCOLORSPACE            =_convert_to_lower.__func__("aceFloatBitmapColorSpace")
    ACEDEFAULTWORKINGSPACE              =_convert_to_lower.__func__("aceDefaultWorkingSpace")
    ACEDEFAULTDISPLAYSPACE              =_convert_to_lower.__func__("aceDefaultDisplaySpace")
    ACECOLORMANAGEGRAPHTHUMBNAILS       =_convert_to_lower.__func__("aceColorManageGraphThumbnails")
    ACE8BITBITMAPCOLORSPACE             =_convert_to_lower.__func__("ace8BitBitmapColorSpace")
    ACE16BITBITMAPCOLORSPACE            =_convert_to_lower.__func__("ace16BitBitmapColorSpace")
    PATH                                =_convert_to_lower.__func__("path")
    PATH_STORAGE_METHODS                =_convert_to_lower.__func__("path_storage_methods")
    PLUGIN_PATHS                        =_convert_to_lower.__func__("plugin_paths")
    PNG                                 =_convert_to_lower.__func__("png")
    PNG_COMPRESSION                     =_convert_to_lower.__func__("png_compression")
    PNG_INTERLACED                      =_convert_to_lower.__func__("png_interlaced")
    PREFERENCES                         =_convert_to_lower.__func__("preferences")
    PROJECTINFO                         =_convert_to_lower.__func__("projectInfo")
    PYTHON                              =_convert_to_lower.__func__("python")
    RESOURCES                           =_convert_to_lower.__func__("resources")
    SBSTEMPLATES                        =_convert_to_lower.__func__("sbstemplates")
    SCENES3D                            =_convert_to_lower.__func__("scenes3d")
    SCRIPT_PATH                         =_convert_to_lower.__func__("script_path")
    SCRIPTING                           =_convert_to_lower.__func__("scripting")
    SETTINGSINFO                        =_convert_to_lower.__func__("settingsInfo")
    SIZE                                =_convert_to_lower.__func__("size")
    SMOOTHINGANGLE                      =_convert_to_lower.__func__("smoothingangle")
    STATESAVEFILEURL                    =_convert_to_lower.__func__("stateSaveFileUrl")
    TANGENTSPACEPLUGIN                  =_convert_to_lower.__func__("tangentspaceplugin")
    TGA                                 =_convert_to_lower.__func__("tga")
    TGA_COMPRESSION                     =_convert_to_lower.__func__("tga_compression")
    TIF                                 =_convert_to_lower.__func__("tif")
    TIF_COMPRESSION                     =_convert_to_lower.__func__("tif_compression")
    URL                                 =_convert_to_lower.__func__("url")
    URLALIASES                          =_convert_to_lower.__func__("urlAliases")
    VALUE                               =_convert_to_lower.__func__("value")
    VERSION                             =_convert_to_lower.__func__("version")
    VERSIONCONTROL                      =_convert_to_lower.__func__("versionControl")
    VIEW3D                              =_convert_to_lower.__func__("view3d")
    WATCHEDPATHS                        =_convert_to_lower.__func__("watchedPaths")
    WEBP                                =_convert_to_lower.__func__("webp")
    WEBP_LOSSLESS                       =_convert_to_lower.__func__("webp_lossless")
    WEBP_QUALITY                        =_convert_to_lower.__func__("webp_quality")
    WORKSPACES                          =_convert_to_lower.__func__("workspaces")
    WORSKSPACE                          =_convert_to_lower.__func__("worskspace")
    WRITE                               =_convert_to_lower.__func__("write")


@doc_source_code_enum
class SBSPRJDependenciesPathStorageMethods:
    """
    Path settings for sbsprj
    """
    RELATIVE = 'relative'
    ABSOLUTE = 'absolute'


SBSPRJDependenciesPathStorageMethodsValues = {
    'relative': SBSPRJDependenciesPathStorageMethods.RELATIVE,
    'absolute': SBSPRJDependenciesPathStorageMethods.ABSOLUTE
}


@doc_source_code_enum
class SBSPRJDependenciesPathTypes:
    """
    Dependencies resolution types
    """
    NOT_NEAR_OR_UNDER = 'not_near_or_under'
    NEAR_OR_UNDER = 'near_or_under'


@doc_source_code_enum
class SBSPRJColorManagementMethods:
    """
    colormanagement values for sbsprj
    """
    LEGACY = 'legacy'
    OCIO = 'ocio'
    ACE = 'ace'


SBSPRJColorManagementMethodsValues = {
    'legacy': SBSPRJColorManagementMethods.LEGACY,
    'ocio': SBSPRJColorManagementMethods.OCIO,
    'ace': SBSPRJColorManagementMethods.ACE
}


@doc_source_code_enum
class SBSPRJOcioConfigMethods:
    """
    colormanagement values for sbsprj
    """
    SUBSTANCE = 'substance'
    ACES = ACES_VERSION
    CUSTOM = 'custom'


SBSPRJOcioConfigMethodsValues = {
    'susbtance': SBSPRJOcioConfigMethods.SUBSTANCE,
    ACES_VERSION: SBSPRJOcioConfigMethods.ACES,
    'CUSTOM': SBSPRJOcioConfigMethods.CUSTOM
}


def _members_as_getter(__init__):
    def wrapper(self, *args, **kwargs):
        __init__(self, *args, **kwargs)
        for member in self.mMembersForEquality:
            if member.startswith('m'):
                method_name = 'get' + member[1:]
            else:
                continue

            def copy_func(member=''):
                def getter_maker(member=member):
                    return getattr(self, member)
                return getter_maker

            setattr(self, method_name, copy_func(member))
        return None
    return wrapper


class SBSPRJAbsValue(SBSObject):
    """
    Class representing the SBSPrj  datastructure.
    """
    def __init__(self, aElementContent='', aElementTag=''):
        SBSObject.__init__(self)
        self.mElementContent = aElementContent
        self.mElementTag = aElementTag
        self.mType = str
        self.mMembersForEquality = ['mElementContent', 'mElementTag']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mElementContent = aXmlNode.text

    def write(self, aSBSWriter, aXmlNode):
        pass

    def getValue(self):
        return self.mType(self.mElementContent)

    def setValue(self, value):
        self.mElementContent = value

    def __repr__(self):
        return '<%s.%s(%s: %s) object at %s>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.mElementTag,
            self.mElementContent,
            hex(id(self))
        )


class SBSPRJAbsBool(SBSPRJAbsValue):
    """
    Class representing the SBSPrj  datastructure.
    """
    def getValue(self):
        return True if self.mElementContent == "true" else False


class SBSPRJAbsInt(SBSPRJAbsValue):
    """
    Class representing the SBSPrj  datastructure.
    """
    def getValue(self):
        return int(self.mElementContent)


class SBSPRJItemList(SBSObject):
    """
    Class representing a list of SBSPrj data structure.
    """
    def __init__(self):
        SBSObject.__init__(self)

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        raise NotImplementedError

    def write(self, aSBSWriter, aXmlNode):
        pass


class SBSPRJList(SBSObject, list):
    """
    Class representing a list of SBSPrj data structure.
    """
    itemTemplate = SBSPRJItemList

    def __init__(self, aSize=''):
        SBSObject.__init__(self)
        self.mSize = aSize
        # self.mItems = []
        self.mMembersForEquality = ['mSize']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mSize = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SIZE, SBSPRJSize)
        for i in range(1, int(self.mSize.mElementContent)+1):
            prefix = '_{0}'.format(i)
            it = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, prefix, self.itemTemplate)
            setattr(self, prefix, it)
            self.append(it)
            self.mMembersForEquality.append(prefix)

    def write(self, aSBSWriter, aXmlNode):
        pass

    def append(self, item):
        if not isinstance(item, self.itemTemplate):
            raise(TypeError, 'item is not of type %s' % self.itemTemplate)
        super(SBSPRJList, self).append(item)



class SBSPRJSize(SBSPRJAbsInt):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.SIZE



class SBSPRJVersion(SBSPRJAbsInt):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.VERSION



class SBSPRJLabel(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.LABEL



class SBSPRJStateSaveFileUrl(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.STATESAVEFILEURL



class SBSPRJIsPointLight2Enable(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsBool.__init__(self)
        self.mElementTag = SBSPRJParams.ISPOINTLIGHT2ENABLE



class SBSPRJIsPointLight1Enable(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsBool.__init__(self)
        self.mElementTag = SBSPRJParams.ISPOINTLIGHT1ENABLE



class SBSPRJIsAmbientLightEnable(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsBool.__init__(self)
        self.mElementTag = SBSPRJParams.ISAMBIENTLIGHTENABLE



class SBSPRJDefaultShaderUrl(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.DEFAULTSHADERURL



class SBSPRJDefaultEnvironmentMapUrl(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.DEFAULTENVIRONMENTMAPURL



class SBSPRJPath(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.PATH



class SBSPRJName(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.NAME



class SBSPRJIsEnabled(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsBool.__init__(self)
        self.mElementTag = SBSPRJParams.IS_ENABLED



class SBSPRJExt(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.EXT



class SBSPRJScriptPath(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.SCRIPT_PATH



class SBSPRJId(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ID



class SBSPRJTangentSpacePlugin(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.TANGENTSPACEPLUGIN



class SBSPRJAlwaysRecomputeTangentFrame(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ALWAYSRECOMPUTETANGENTFRAME



class SBSPRJSmoothingAngle(SBSPRJAbsInt):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.SMOOTHINGANGLE



class SBSPRJUrl(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.URL



class SBSPRJIsRecursive(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsBool.__init__(self)
        self.mElementTag = SBSPRJParams.ISRECURSIVE



class SBSPRJExcludeFilter(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.EXCLUDEFILTER



class SBSPRJNormalMapFormat(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.NORMAL_MAP_FORMAT



class SBSPRJNormalFilterAlphaChannelContent(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.NORMAL_FILTER_ALPHA_CHANNEL_CONTENT



class SBSPRJWebpQuality(SBSPRJAbsInt):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.WEBP_QUALITY



class SBSPRJWebpLossLess(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.WEBP_LOSSLESS



class SBSPRJTifCompression(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.TIF_COMPRESSION



class SBSPRJTgaCompression(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.TGA_COMPRESSION



class SBSPRJPngInterlaced(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.PNG_INTERLACED

        

class SBSPRJPngCompression(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.PNG_COMPRESSION



class SBSPRJJpgOptimize(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.JPG_OPTIMIZE



class SBSPRJJpgProgressive(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.JPG_PROGRESSIVE

        

class SBSPRJJpgQuality(SBSPRJAbsInt):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.JPG_QUALITY



class SBSPRJExrCompression(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.EXR_COMPRESSION


class SBSPRJExrLc(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.EXR_LC

        

class SBSPRJExrUseFloat(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.EXR_USE_FLOAT



class SBSPRJBmpCompression(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.BMP_COMPRESSION



class SBSPRJIsVisible(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsBool.__init__(self)
        self.mElementTag = SBSPRJParams.ISVISIBLE



class SBSPRJDefaultResourceName(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.DEFAULTRESOURCENAME



class SBSPRJMeshID(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.MESHID



class SBSPRJValue(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.VALUE



class SBSPRJKey(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.KEY



class SBSPRJNameFilterValue(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.NAMEFILTER



class SBSPRJBakerID(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.BAKERID


class SBSPRJOcioFloatBitmapColorSpace(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIOFLOATBITMAPCOLORSPACE


class SBSPRJOcioDefaultView(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIODEFAULTVIEW


class SBSPRJOcioDefaultDisplay(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIODEFAULTDISPLAY


class SBSPRJOcioCustomConfigPath(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIOCUSTOMCONFIGPATH


class SBSPRJOcioConfig(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIOCONFIG


class SBSPRJOcioColorManageGraphThumbnails(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIOCOLORMANAGEGRAPHTHUMBNAILS


class SBSPRJOcioAutoDetectColorSpaceInFileName(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIOAUTODETECTCOLORSPACEINFILENAME


class SBSPRJOcio8BitBitmapColorSpace(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIO8BITBITMAPCOLORSPACE


class SBSPRJOcio16BitBitmapColorSpace(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.OCIO16BITBITMAPCOLORSPACE


class SBSPRJAceUseEmbeddedProfiles(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACEUSEEMBEDDEDPROFILES


class SBSPRJAceRenderingIntent(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACERENDERINGINTENT


class SBSPRJAceFloatBitmapColorSpace(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACEFLOATBITMAPCOLORSPACE


class SBSPRJAceDefaultWorkingSpace(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACEDEFAULTWORKINGSPACE


class SBSPRJAceDefaultDisplaySpace(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACEDEFAULTDISPLAYSPACE


class SBSPRJAceColorManageGraphThumbnails(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACECOLORMANAGEGRAPHTHUMBNAILS


class SBSPRJAce8BitBitmapColorSpace(SBSPRJAbsBool):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACE8BITBITMAPCOLORSPACE


class SBSPRJAce16BitBitmapColorSpace(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.ACE16BITBITMAPCOLORSPACE


class SBSPRJColorManagementEngine(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.COLORMANAGEMENTENGINE


class SBSPRJNotNearOrUnder(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """

    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.NOT_NEAR_OR_UNDER

    def getValue(self):
        return SBSPRJDependenciesPathStorageMethodsValues.get(self.mElementContent)


class SBSPRJNearOrUnder(SBSPRJAbsValue):
    """
    Class representing the  datastructure.
    """
    def __init__(self):
        SBSPRJAbsValue.__init__(self)
        self.mElementTag = SBSPRJParams.NEAR_OR_UNDER

    def getValue(self):
        return SBSPRJDependenciesPathStorageMethods.ABSOLUTE if self.mElementContent == 'absolute' \
            else SBSPRJDependenciesPathStorageMethods.RELATIVE


@doc_inherit
class SBSPRJView3d(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aStateSaveFileUrl='', aIsPointLight2Enable='', aIsPointLight1Enable='', aIsAmbientLightEnable='',
                 aDefaultShaderUrl='', aDefaultEnvironmentMapUrl=''):
        SBSObject.__init__(self)
        self.mStateSaveFileUrl = aStateSaveFileUrl
        self.mIsPointLight2Enable = aIsPointLight2Enable
        self.mIsPointLight1Enable = aIsPointLight1Enable
        self.mIsAmbientLightEnable = aIsAmbientLightEnable
        self.mDefaultShaderUrl = aDefaultShaderUrl
        self.mDefaultEnvironmentMapUrl = aDefaultEnvironmentMapUrl
        self.mMembersForEquality = ['mStateSaveFileUrl', 'aIsPointLight2Enable', 'aIsPointLight1Enable',
                                    'aIsAmbientLightEnable', 'aDefaultShaderUrl', 'aDefaultEnvironmentMapUrl']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mStateSaveFileUrl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.STATESAVEFILEURL, SBSPRJStateSaveFileUrl)
        self.mIsPointLight2Enable = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ISPOINTLIGHT2ENABLE, SBSPRJIsPointLight2Enable)
        self.mIsPointLight1Enable = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ISPOINTLIGHT1ENABLE, SBSPRJIsPointLight1Enable)
        self.mIsAmbientLightEnable = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ISAMBIENTLIGHTENABLE, SBSPRJIsAmbientLightEnable)
        self.mDefaultShaderUrl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.DEFAULTSHADERURL, SBSPRJDefaultShaderUrl)
        self.mDefaultEnvironmentMapUrl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.DEFAULTENVIRONMENTMAPURL, SBSPRJDefaultEnvironmentMapUrl)

    def write(self, aSBSWriter, aXmlNode):
        pass



@doc_inherit
class SBSPRJVersionControl(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aWorkspaces='', aSettingsInfo=''):
        SBSObject.__init__(self)
        self.mWorkspaces = aWorkspaces
        self.mSettingsInfo = aSettingsInfo
        self.mMembersForEquality = ['mWorkspaces', 'mSettingsInfo']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWorkspaces = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WORKSPACES, SBSPRJWorkspaces)
        self.mSettingsInfo = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SETTINGSINFO, SBSPRJSettingsInfo)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJWorkspacesItem(SBSObject, ):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aWorkspace='', aSettingsInfo='', aIsEnabled='', aInterpreters='', aActions=''):
        SBSObject.__init__(self)
        self.mWorkspace = aWorkspace
        self.mSettingsInfo = aSettingsInfo
        self.mIsEnabled = aIsEnabled
        self.mInterpreters = aInterpreters
        self.mActions = aActions
        self.mMembersForEquality = ['mWorkspace', 'mSettingsInfo', 'mIsEnabled', 'mInterpreters', 'mActions']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWorkspace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WORSKSPACE, SBSPRJWorkspace) # TODO: fix the typo worskspace in sbsprj
        self.mSettingsInfo = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SETTINGSINFO, SBSPRJSettingsInfo)
        self.mIsEnabled = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.IS_ENABLED, SBSPRJIsEnabled)
        self.mInterpreters = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.INTERPRETERS, SBSPRJInterpreters)
        self.mActions = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACTIONS, SBSPRJActions)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJInterpretersItem(SBSObject, ):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aPath='', aExt=''):
        SBSObject.__init__(self)
        self.mPath = aPath
        self.mExt = aExt
        self.mMembersForEquality = ['mPath', 'mExt']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mPath = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PATH, SBSPRJPath)
        self.mExt = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.EXT, SBSPRJExt)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJActionsItem(SBSObject, ):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aScriptPath='', aLabel='', aId='', aEnabled=''):
        SBSObject.__init__(self)
        self.mScriptPath = aScriptPath
        self.mLabel = aLabel
        self.mId = aId
        self.mEnabled = aEnabled
        self.mMembersForEquality = ['mScriptPath', 'mLabel', 'mId', 'mEnabled']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mScriptPath = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SCRIPT_PATH, SBSPRJScriptPath)
        self.mLabel = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.LABEL, SBSPRJLabel)
        self.mId = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ID, SBSPRJId)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJDirsItem(SBSObject, ):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aUrl=''):
        SBSObject.__init__(self)
        self.mUrl = aUrl
        self.mMembersForEquality = ['mUrl']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUrl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.URL, SBSPRJUrl)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJUrlAliasesItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aPath='', aName=''):
        SBSObject.__init__(self)
        self.mPath = aPath
        self.mName = aName
        self.mParentSbsPrj = CURRENT_SBSPRJ
        self.mMembersForEquality = ['mPath', 'mName']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mPath = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PATH, SBSPRJPath)
        self.mName = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NAME, SBSPRJName)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJPluginPathsItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aUrl=''):
        SBSObject.__init__(self)
        self.mUrl = aUrl
        self.mMembersForEquality = ['mUrl']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUrl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.URL, SBSPRJUrl)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJMdlPathsItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aUrl=''):
        SBSObject.__init__(self)
        self.mUrl = aUrl
        self.mMembersForEquality = ['mUrl']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUrl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.URL, SBSPRJUrl)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJWatchedPathsItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aUrl='', aIsRecursive='', aIsEnabled='', aExcludeFilter=''):
        SBSObject.__init__(self)
        self.mUrl = aUrl
        self.mIsRecursive = aIsRecursive
        self.mIsEnabled = aIsEnabled
        self.mExcludeFilter = aExcludeFilter
        self.mMembersForEquality = ['mUrl', 'mIsRecursive', 'mIsEnabled', 'mExcludeFilter']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUrl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.URL, SBSPRJUrl)
        self.mIsRecursive = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ISRECURSIVE, SBSPRJIsRecursive)
        self.mIsEnabled = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ISENABLED, SBSPRJIsEnabled)
        self.mExcludeFilter = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.EXCLUDEFILTER, SBSPRJExcludeFilter)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJNameFiltersItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aNameFilter='', aMeshID=''):
        SBSObject.__init__(self)
        self.mNameFilter = aNameFilter
        self.mMeshID = aMeshID
        self.mMembersForEquality = ['mNameFilter', 'mMeshID']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mNameFilter = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NAMEFILTER, SBSPRJNameFilter)
        self.mMeshID = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.MESHID, SBSPRJMeshID)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJNameFilterItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aValue='', aNameFilter=''):
        SBSObject.__init__(self)
        self.mValue = aValue
        self.mNameFilter = aNameFilter
        self.mMembersForEquality = ['mValue', 'mNameFilter']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mValue = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.VALUE, SBSPRJValue)
        self.mNameFilter = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NAMEFILTER, SBSPRJNameFilterValue)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJBakersMacrosItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aMacros='', aBakerID=''):
        SBSObject.__init__(self)
        self.mMacros = aMacros
        self.mBakerID = aBakerID
        self.mMembersForEquality = ['mMacros', 'mBakerID']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mMacros = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.MACROS, SBSPRJMacros)
        self.mBakerID = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.BAKERID, SBSPRJBakerID)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJMacrosItem(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aValue='', aKey=''):
        SBSObject.__init__(self)
        self.mValue = aValue
        self.mKey = aKey
        self.mMembersForEquality = ['mValue', 'mKey']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mValue = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.VALUE, SBSPRJValue)
        self.mKey = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.KEY, SBSPRJKey)

    def write(self, aSBSWriter, aXmlNode):
        pass



@doc_inherit
class SBSPRJWorkspace(SBSObject):
    """
    """
    @_members_as_getter
    def __init__(self, aPath='', aName=''):
        SBSObject.__init__(self)
        self.mPath = aPath
        self.mName = aName
        self.mMembersForEquality = ['mPath', 'mName']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mPath = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PATH, SBSPRJPath)
        self.mName = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NAME, SBSPRJName)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJSettingsInfo(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aVersion=''):
        SBSObject.__init__(self)
        self.mVersion = aVersion
        self.mMembersForEquality = ['mVersion']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mVersion = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.VERSION, SBSPRJVersion)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJImageOptions(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aWebp='', aTif='', aTga='', aPng='', aJpg='', aExr='', aBmp=''):
        SBSObject.__init__(self)
        self.mWebp = aWebp
        self.mTif = aTif
        self.mTga = aTga
        self.mPng = aPng
        self.mJpg = aJpg
        self.mExr = aExr
        self.mBmp = aBmp
        self.mMembersForEquality = ['mWebp', 'mTif', 'mTga', 'mPng', 'mJpg', 'mExr', 'mBmp']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWebp = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'webp', SBSPRJWebp)
        self.mTif = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'tif', SBSPRJTif)
        self.mTga = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'tga', SBSPRJTga)
        self.mPng = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'png', SBSPRJPng)
        self.mJpg = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'jpg', SBSPRJJpg)
        self.mExr = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'exr', SBSPRJExr)
        self.mBmp = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, 'bmp', SBSPRJBmp)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJWebp(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    class SBSPRJWrite(SBSObject):
        @_members_as_getter
        def __init__(self, aWebpQuality='', aWebpLossless=''):
            SBSObject.__init__(self)
            self.mWebpQuality = aWebpQuality
            self.mWebpLossless = aWebpLossless
            self.mMembersForEquality = ['mWebpQuality', 'mWebpLossless']

        @handle_exceptions()
        def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
            self.mWebpQuality = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WEBP_QUALITY, SBSPRJWebpQuality)
            self.mWebpLossless = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WEBP_LOSSLESS, SBSPRJWebpLossLess)

        def write(self, aSBSWriter, aXmlNode):
            pass

    @_members_as_getter
    def __init__(self, aWrite=''):
        SBSObject.__init__(self)
        self.mWrite = aWrite
        self.mMembersForEquality = ['mWrite']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWrite = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WRITE, SBSPRJWebp.SBSPRJWrite)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJTif(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    class SBSPRJWrite(SBSObject):
        @_members_as_getter
        def __init__(self, aTifCompression=''):
            SBSObject.__init__(self)
            self.mTifCompression = aTifCompression
            self.mMembersForEquality = ['mTifCompression']

        @handle_exceptions()
        def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
            self.mTifCompression = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.TIF_COMPRESSION, SBSPRJTifCompression)

        def write(self, aSBSWriter, aXmlNode):
            pass

    @_members_as_getter
    def __init__(self, aWrite=''):
        SBSObject.__init__(self)
        self.mWrite = aWrite
        self.mMembersForEquality = ['mWrite']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWrite = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WRITE, SBSPRJTif.SBSPRJWrite)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJTga(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    class SBSPRJWrite(SBSObject):
        @_members_as_getter
        def __init__(self, aTgaCompression=''):
            SBSObject.__init__(self)
            self.mTgaCompression = aTgaCompression
            self.mMembersForEquality = ['mTgaCompression']

        @handle_exceptions()
        def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
            self.mTgaCompression = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.TGA_COMPRESSION, SBSPRJTgaCompression)

        def write(self, aSBSWriter, aXmlNode):
            pass

    @_members_as_getter
    def __init__(self, aWrite=''):
        SBSObject.__init__(self)
        self.mWrite = aWrite
        self.mMembersForEquality = ['mWrite']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWrite = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WRITE, SBSPRJTga.SBSPRJWrite)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJBmp(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    class SBSPRJWrite(SBSObject):
        @_members_as_getter
        def __init__(self, aBmpCompression=''):
            SBSObject.__init__(self)
            self.mBmpCompression = aBmpCompression
            self.mMembersForEquality = ['mBmpCompression']

        @handle_exceptions()
        def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
            self.mBmpCompression = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.BMP_COMPRESSION, SBSPRJBmpCompression)

        def write(self, aSBSWriter, aXmlNode):
            pass

    @_members_as_getter
    def __init__(self, aWrite=''):
        SBSObject.__init__(self)
        self.mWrite = aWrite
        self.mMembersForEquality = ['mWrite']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWrite = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WRITE, SBSPRJBmp.SBSPRJWrite)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJPng(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    class SBSPRJWrite(SBSObject):
        @_members_as_getter
        def __init__(self, aPngInterlaced='', aPngCompression=''):
            SBSObject.__init__(self)
            self.mPngInterlaced = aPngInterlaced
            self.mPngCompression = aPngCompression
            self.mMembersForEquality = ['mPngInterlaced', 'mPngCompression']

        @handle_exceptions()
        def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
            self.mPngInterlaced = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PNG_INTERLACED, SBSPRJPngInterlaced)
            self.mPngCompression = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PNG_COMPRESSION, SBSPRJPngCompression)

        def write(self, aSBSWriter, aXmlNode):
            pass

    @_members_as_getter
    def __init__(self, aWrite=''):
        SBSObject.__init__(self)
        self.mWrite = aWrite
        self.mMembersForEquality = ['mWrite']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWrite = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WRITE, SBSPRJPng.SBSPRJWrite)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJJpg(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    class SBSPRJWrite(SBSObject):
        @_members_as_getter
        def __init__(self, aJpgQuality='', aJpgProgressive='', aJpgOptimize=''):
            SBSObject.__init__(self)
            self.mJpgQuality = aJpgQuality
            self.mJpgProgressive = aJpgProgressive
            self.mJpgOptimize = aJpgOptimize
            self.mMembersForEquality = ['mJpgQuality', 'mJpgProgressive', 'mJpgOptimize']

        @handle_exceptions()
        def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
            self.mJpgQuality = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.JPG_QUALITY, SBSPRJJpgQuality)
            self.mJpgProgressive = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.JPG_PROGRESSIVE, SBSPRJJpgProgressive)
            self.mJpgOptimize = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.JPG_OPTIMIZE, SBSPRJJpgOptimize)

        def write(self, aSBSWriter, aXmlNode):
            pass

    @_members_as_getter
    def __init__(self, aWrite=''):
        SBSObject.__init__(self)
        self.mWrite = aWrite
        self.mMembersForEquality = ['mWrite']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWrite = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WRITE, SBSPRJJpg.SBSPRJWrite)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJDependencies(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aPathStorageMethods=''):
        SBSObject.__init__(self)
        self.mPathStorageMethods = aPathStorageMethods
        self.mMembersForEquality = ['mPathStorageMethods']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mPathStorageMethods = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PATH_STORAGE_METHODS, SBSPRJPathStorageMethods)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJPathStorageMethods(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aNotNearOrUnder='', aNearOrUnder=''):
        SBSObject.__init__(self)
        self.mNotNearOrUnder = aNotNearOrUnder
        self.mNearOrUnder = aNearOrUnder
        self.mMembersForEquality = ['mNotNearOrUnder', 'mNearOrUnder']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mNotNearOrUnder = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NOT_NEAR_OR_UNDER, SBSPRJNotNearOrUnder)
        self.mNearOrUnder = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NEAR_OR_UNDER, SBSPRJNearOrUnder)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJExr(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    class SBSPRJWrite(SBSObject):
        @_members_as_getter
        def __init__(self, aExrUseFloat='', aExrLc='', aExrCompression=''):
            SBSObject.__init__(self)
            self.mExrUseFloat = aExrUseFloat
            self.mExrLc = aExrLc
            self.mExrCompression = aExrCompression
            self.mMembersForEquality = ['mExrUseFloat', 'mExrLc', 'mExrCompression']

        @handle_exceptions()
        def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
            self.mExrUseFloat = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.EXR_USE_FLOAT, SBSPRJExrUseFloat)
            self.mExrLc = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.EXR_LC, SBSPRJExrLc)
            self.mExrCompression = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.EXR_COMPRESSION, SBSPRJExrCompression)

        def write(self, aSBSWriter, aXmlNode):
            pass

    @_members_as_getter
    def __init__(self, aWrite=''):
        SBSObject.__init__(self)
        self.mWrite = aWrite
        self.mMembersForEquality = ['mWrite']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWrite = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WRITE, SBSPRJExr.SBSPRJWrite)

    def write(self, aSBSWriter, aXmlNode):
        pass




class SBSPRJWorkspaces(SBSPRJList):
    itemTemplate = SBSPRJWorkspacesItem



class SBSPRJInterpreters(SBSPRJList):
    itemTemplate = SBSPRJInterpretersItem



class SBSPRJActions(SBSPRJList):
    itemTemplate = SBSPRJActionsItem



class SBSPRJDirs(SBSPRJList):
    itemTemplate = SBSPRJDirsItem
    


class SBSPRJUrlAliases(SBSPRJList):
    itemTemplate = SBSPRJUrlAliasesItem



class SBSPRJPluginPaths(SBSPRJList):
    itemTemplate = SBSPRJPluginPathsItem
  


class SBSPRJMdlPaths(SBSPRJList):
    itemTemplate = SBSPRJMdlPathsItem



class SBSPRJWatchedPaths(SBSPRJList):
    itemTemplate = SBSPRJWatchedPathsItem



class SBSPRJNameFilters(SBSPRJList):
    itemTemplate = SBSPRJNameFiltersItem



class SBSPRJNameFilter(SBSPRJList):
    itemTemplate = SBSPRJNameFilterItem



class SBSPRJBakersMacros(SBSPRJList):
    itemTemplate = SBSPRJBakersMacrosItem



class SBSPRJMacros(SBSPRJList):
    itemTemplate = SBSPRJMacrosItem
    
    

@doc_inherit
class SBSPRJScripting(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aInterpreters='', aActions=''):
        SBSObject.__init__(self)
        self.mInterpreters = aInterpreters
        self.mActions = aActions
        self.mMembersForEquality = ['mInterpreters', "mActions"]

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mInterpreters = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.INTERPRETERS, SBSPRJInterpreters)
        self.mActions = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACTIONS, SBSPRJActions)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJScenes3d(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aTangentSpacePlugin='', aSmoothingAngle='', aAlwaysRecomputeTangentFrame=''):
        SBSObject.__init__(self)
        self.mTangentSpacePlugin = aTangentSpacePlugin
        self.mSmoothingAngle = aSmoothingAngle
        self.mAlwaysRecomputeTangentFrame = aAlwaysRecomputeTangentFrame
        self.mMembersForEquality = ['mTangentSpacePlugin', 'mSmoothingAngle', 'mAlwaysRecomputeTangentFrame', 'mAlwaysRecomputeTangentFrame']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mTangentSpacePlugin = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.TANGENTSPACEPLUGIN, SBSPRJTangentSpacePlugin)
        self.mSmoothingAngle = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SMOOTHINGANGLE, SBSPRJSmoothingAngle)
        self.mAlwaysRecomputeTangentFrame = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ALWAYSRECOMPUTETANGENTFRAME, SBSPRJAlwaysRecomputeTangentFrame)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJSbsTemplates(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aDirs=''):
        SBSObject.__init__(self)
        self.mDirs = aDirs
        self.mMembersForEquality = ['mDirs']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mDirs = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.DIRS, SBSPRJDirs)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJResources(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aUrlAliases=''):
        SBSObject.__init__(self)
        self.mUrlAliases = aUrlAliases
        self.mMembersForEquality = ['mUrlAliases']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mUrlAliases = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.URLALIASES, SBSPRJUrlAliases)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJPython(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aPluginPaths=''):
        SBSObject.__init__(self)
        self.mPluginPaths = aPluginPaths
        self.mMembersForEquality = ['mPluginPaths']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mPluginPaths = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PLUGIN_PATHS, SBSPRJPluginPaths)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJOcio(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aOcioFloatBitmapColorSpace='', aOcioDefaultView='', aOcioDefaultDisplay='',
                 aOcioConfig='', aOcioColorManageGraphThumbnails='', aOcioAutoDetectColorSpaceInFileName='',
                 aOcio8BitBitmapColorSpace='', aOcio16BitBitmapColorSpace='', aOcioCustomConfigPath=''):
        SBSObject.__init__(self)
        self.mOcioFloatBitmapColorSpace = aOcioFloatBitmapColorSpace
        self.mOcioDefaultView = aOcioDefaultView
        self.mOcioDefaultDisplay = aOcioDefaultDisplay
        self.mOcioCustomConfigPath = aOcioCustomConfigPath
        self.mOcioConfig = aOcioConfig
        self.mOcioColorManageGraphThumbnails = aOcioColorManageGraphThumbnails
        self.mOcioAutoDetectColorSpaceInFileName = aOcioAutoDetectColorSpaceInFileName
        self.mOcio8BitBitmapColorSpace = aOcio8BitBitmapColorSpace
        self.mOcio16BitBitmapColorSpace = aOcio16BitBitmapColorSpace

        self.mMembersForEquality = ['mOcioFloatBitmapColorSpace', 'mOcioDefaultView', 'mOcioDefaultDisplay',
                                    'mOcioCustomConfigPath', 'mOcioConfig', 'mOcio16BitBitmapColorSpace',
                                    'mOcioColorManageGraphThumbnails', 'mOcioAutoDetectColorSpaceInFileName',
                                    'mOcio8BitBitmapColorSpace']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mOcioFloatBitmapColorSpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIOFLOATBITMAPCOLORSPACE, SBSPRJOcioFloatBitmapColorSpace)
        self.mOcioDefaultView = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIODEFAULTVIEW, SBSPRJOcioDefaultView)
        self.mOcioDefaultDisplay = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIODEFAULTDISPLAY, SBSPRJOcioDefaultDisplay)
        self.mOcioCustomConfigPath = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIOCUSTOMCONFIGPATH, SBSPRJOcioCustomConfigPath)
        self.mOcioConfig = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIOCONFIG, SBSPRJOcioConfig)
        self.mOcioColorManageGraphThumbnails = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIOCOLORMANAGEGRAPHTHUMBNAILS, SBSPRJOcioColorManageGraphThumbnails)
        self.mOcioAutoDetectColorSpaceInFileName = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIOAUTODETECTCOLORSPACEINFILENAME, SBSPRJOcioAutoDetectColorSpaceInFileName)
        self.mOcio8BitBitmapColorSpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIO8BITBITMAPCOLORSPACE, SBSPRJOcio8BitBitmapColorSpace)
        self.mOcio16BitBitmapColorSpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIO16BITBITMAPCOLORSPACE, SBSPRJOcio16BitBitmapColorSpace)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJAce(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aAceUseEmbeddedProfiles='', aAceRenderingIntent='', aAceFloatBitmapColorSpace='',
                 aAceDefaultWorkingSpace='', aAceDefaultDisplaySpace='', aAceColorManageGraphThumbnails='',
                 aAce8BitBitmapColorSpace='', aAce16BitBitmapColorSpace=''):
        SBSObject.__init__(self)
        self.mAceUseEmbeddedProfiles = aAceUseEmbeddedProfiles
        self.mAceRenderingIntent = aAceRenderingIntent
        self.mAceFloatBitmapColorSpace = aAceFloatBitmapColorSpace
        self.mAceDefaultWorkingSpace = aAceDefaultWorkingSpace
        self.mAceDefaultDisplaySpace = aAceDefaultDisplaySpace
        self.mAceColorManageGraphThumbnails = aAceColorManageGraphThumbnails
        self.mAce8BitBitmapColorSpace = aAce8BitBitmapColorSpace
        self.mAce16BitBitmapColorSpace = aAce16BitBitmapColorSpace

        self.mMembersForEquality = ['mAceUseEmbeddedProfiles', 'mAceRenderingIntent', 'mAceFloatBitmapColorSpace',
                                    'mAceDefaultWorkingSpace', 'mAceDefaultDisplaySpace', 'mAceColorManageGraphThumbnails',
                                    'mAce8BitBitmapColorSpace', 'mAce16BitBitmapColorSpace']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mAceUseEmbeddedProfiles = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACEUSEEMBEDDEDPROFILES, SBSPRJAceUseEmbeddedProfiles)
        self.mAceRenderingIntent = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACERENDERINGINTENT, SBSPRJAceRenderingIntent)
        self.mAceFloatBitmapColorSpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACEFLOATBITMAPCOLORSPACE, SBSPRJAceFloatBitmapColorSpace)
        self.mAceDefaultWorkingSpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACEDEFAULTWORKINGSPACE, SBSPRJAceDefaultWorkingSpace)
        self.mAceDefaultDisplaySpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACEDEFAULTDISPLAYSPACE, SBSPRJAceDefaultDisplaySpace)
        self.mAceColorManageGraphThumbnails = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACECOLORMANAGEGRAPHTHUMBNAILS, SBSPRJAceColorManageGraphThumbnails)
        self.mAce8BitBitmapColorSpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACE8BITBITMAPCOLORSPACE, SBSPRJAce8BitBitmapColorSpace)
        self.mAce16BitBitmapColorSpace = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACE16BITBITMAPCOLORSPACE, SBSPRJAce16BitBitmapColorSpace)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJMdl(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aIRay=''):
        SBSObject.__init__(self)
        self.mIRay = aIRay
        self.mMembersForEquality = ['mIRay']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIRay = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.IRAY, SBSPRJIRay)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJIRay(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aMdlPaths=''):
        SBSObject.__init__(self)
        self.mMdlPaths = aMdlPaths
        self.mMembersForEquality = ['mMdlPaths']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mMdlPaths = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.MDL_PATHS, SBSPRJMdlPaths)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJLibrary(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aWatchedPaths='', aSettingsInfo=''):
        SBSObject.__init__(self)
        self.mWatchedPaths = aWatchedPaths
        self.mSettingsInfo = aSettingsInfo
        self.mMembersForEquality = ['mWatchedPaths', 'mSettingsInfo']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mWatchedPaths = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.WATCHEDPATHS, SBSPRJWatchedPaths)
        self.mSettingsInfo = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SETTINGSINFO, SBSPRJSettingsInfo)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJGeneral(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aNormalMapFormat='', aNormalFilterAlphaChannelContent='', aImageOptions='', aDependencies=''):
        SBSObject.__init__(self)
        self.mNormalMapFormat = aNormalMapFormat
        self.mNormalFilterAlphaChannelContent = aNormalFilterAlphaChannelContent
        self.mImageOptions = aImageOptions
        self.mDependencies = aDependencies
        self.mMembersForEquality = ['mNormalMapFormat', 'mNormalFilterAlphaChannelContent', 'mImageOptions', 'mDependencies']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mNormalMapFormat = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NORMAL_MAP_FORMAT, SBSPRJNormalMapFormat)
        self.mNormalFilterAlphaChannelContent = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NORMAL_FILTER_ALPHA_CHANNEL_CONTENT, SBSPRJNormalFilterAlphaChannelContent)
        self.mImageOptions = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.IMAGE_OPTIONS, SBSPRJImageOptions)
        self.mDependencies = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.DEPENDENCIES, SBSPRJDependencies)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJColorManagement(SBSObject):
    """
    Class representing an SBSPRJ Parameter
    """
    @_members_as_getter
    def __init__(self, aColorManagementEngine=''):
        SBSObject.__init__(self)
        self.mColorManagementEngine = aColorManagementEngine
        self.mMembersForEquality = ['mColorManagementEngine']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mColorManagementEngine = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.COLORMANAGEMENTENGINE, SBSPRJColorManagementEngine)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJBakers(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aNameFilters='', aDefaultResourceName='', aBakersMacros=''):
        SBSObject.__init__(self)
        self.mNameFilters = aNameFilters
        self.mDefaultResourceName = aDefaultResourceName
        self.mBakersMacros = aBakersMacros
        self.mMembersForEquality = ['mNameFilters', 'mDefaultResourceName', 'mBakersMacros']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mNameFilters = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.NAMEFILTERS, SBSPRJNameFilters)
        self.mDefaultResourceName = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.DEFAULTRESOURCENAME, SBSPRJDefaultResourceName)
        self.mBakersMacros = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.BAKERSMACROS, SBSPRJBakersMacros)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJProjectInfo(SBSObject, ):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aLabel=''):
        SBSObject.__init__(self)
        self.mLabel = aLabel
        self.mMembersForEquality = ['mLabel']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mLabel = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.LABEL, SBSPRJLabel)

    def write(self, aSBSWriter, aXmlNode):
        pass


@doc_inherit
class SBSPRJPreferences(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aView3d='', aVersionControl='', aScripting='', aScenes3d='', aSbsTemplates='', aResources='',
                 aPython='', aOcio='', aAce='', aMdl='', aLibrary='', aGeneral='', aColorManagement='', aBakers=''):
        SBSObject.__init__(self)
        self.mView3d = aView3d
        self.mVersionControl = aVersionControl
        self.mScripting = aScripting
        self.mScenes3d = aScenes3d
        self.mSbsTemplates = aSbsTemplates
        self.mResources = aResources
        self.mPython = aPython
        self.mOcio = aOcio
        self.mAce = aAce
        self.mMdl = aMdl
        self.mLibrary = aLibrary
        self.mGeneral = aGeneral
        self.mColorManagement = aColorManagement
        self.mBakers = aBakers
        self.mMembersForEquality = ['mView3d', 'mVersionControl', 'mScripting', 'mScenes3d',
                                    'mSbsTemplates', 'mResources', 'mPython', 'mOcio', 'mAce', 'mMdl', 'mLibrary',
                                    'mGeneral', 'mColorManagement', 'mBakers']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mView3d = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.VIEW3D, SBSPRJView3d)
        self.mVersionControl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.VERSIONCONTROL, SBSPRJVersionControl)
        self.mScripting = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SCRIPTING, SBSPRJScripting)
        self.mScenes3d = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SCENES3D, SBSPRJScenes3d)
        self.mSbsTemplates = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SBSTEMPLATES, SBSPRJSbsTemplates)
        self.mResources = overrideSBSObject(self.mResources, aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.RESOURCES, SBSPRJResources))
        self.mPython = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PYTHON, SBSPRJPython)
        self.mOcio = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.OCIO, SBSPRJOcio)
        self.mAce = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ACE, SBSPRJAce)
        self.mMdl = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.MDL, SBSPRJMdl)
        self.mLibrary = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.LIBRARY, SBSPRJLibrary)
        self.mGeneral = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.GENERAL, SBSPRJGeneral)
        self.mColorManagement = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.COLORMANAGEMENT, SBSPRJColorManagement)
        self.mBakers = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.BAKERS, SBSPRJBakers)

    def write(self, aSBSWriter, aXmlNode):
        pass

@doc_inherit
class SBSPRJProject(SBSObject):
    """
    Class representing an SBSPRJ Parameter 
    """
    @_members_as_getter
    def __init__(self, aSettingsInfo='', aProjectInfo='', aPreferences='', aIsVisible=''):
        SBSObject.__init__(self)
        self.mSettingsInfo = aSettingsInfo
        self.mProjectInfo = aProjectInfo
        self.mPreferences = aPreferences
        self.mIsVisible = aIsVisible
        self.mMembersForEquality = ['mSettingsInfo', 'mProjectInfo', 'mPreferences', 'mIsVisible']
        self.mIsParsed = False
        self.mSbsPrjFilePath = []

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mSettingsInfo = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.SETTINGSINFO, SBSPRJSettingsInfo)
        self.mProjectInfo = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PROJECTINFO, SBSPRJProjectInfo)
        self.mPreferences = overrideSBSObject(self.mPreferences, aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.PREFERENCES, SBSPRJPreferences))
        self.mIsVisible = aSBSParser.getSBSElementIn(aContext, aDirAbsPath, aXmlNode, SBSPRJParams.ISVISIBLE, SBSPRJIsVisible)

    @handle_exceptions()
    def parseDoc(self, aContext):
        global CURRENT_SBSPRJ
        if isinstance(self.mSbsPrjFilePath, list):
            CURRENT_SBSPRJ = self.mSbsPrjFilePath[-1]
        else:
            CURRENT_SBSPRJ = self.mSbsPrjFilePath
        aParser = sbsparser.SBSParser(CURRENT_SBSPRJ, aContext, aFileType=sbsparser.FileTypeEnum.SBSPRJ)
        self.parse(aContext, os.path.dirname(CURRENT_SBSPRJ), aParser, aParser.getRootNode())
        self.mIsParsed = True

    def write(self, aSBSWriter, aXmlNode):
        pass


def overrideSBSObject(aObjectA, aObjectB):
    def _recursive_attr(a, b):
        for (kA, vA), (kB, vB) in zip(sorted(vars(a).items()), sorted(vars(b).items())):
            if callable(vA) or callable(vB):
                continue
            if isinstance(vA, list) or isinstance(vB, list):
                vA = vA or []
                vB = vB or []
                vA.extend(vB)
                a.__dict__[kA] = vA
            elif not vA:
                a.__dict__[kA] = vB
            elif not isinstance(vA, SBSObject):
                a.__dict__[kA] = vB
                return
            else:
                _recursive_attr(a.__dict__[kA], b.__dict__[kB])
    if not aObjectA:
        return aObjectB
    if not aObjectB:
        return aObjectA
    _recursive_attr(aObjectA, aObjectB)
    return aObjectA
