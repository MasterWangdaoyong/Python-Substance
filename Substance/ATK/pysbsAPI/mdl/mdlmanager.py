# coding: utf-8
"""
Module **mdlmanager** provides the class :class:`.MDLManager` that allows requesting a native mdl node information.
"""

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import json
import os
import subprocess
import collections

from pysbs.api_decorators import handle_exceptions
from pysbs.api_exceptions import SBSLibraryError
from pysbs import sbsenum
from pysbs import python_helpers
from .mdllibclasses import MDLNodeDefParamValue, MDLAnnotationDef, MDLNodeDef, MDLTypeDef
from .mdlenum import *
from . import mdldictionaries as mdldict



# ==============================================================================
class MDLManager:
    """
    Class used handle the MDL library and to request information on a MDL instance
    """
    __sMDLRootPaths = []                                               # The list of MDL root path
    __sMDLFunctionDictionary = {}                                      # The MDL node dictionary: {mdl_path(str): mdl_node_definition(MDLNodeDef)}
    __sMDLVersionnedFunctionDictionary = collections.defaultdict(list) # The MDL node dictionary: {mdl_path(str): Collection[mdl_path(str)] (sorted by descending version)}
    __sMDLTypeDictionary = {}                                          # The MDL type dictionary: {mdl_path(str): mdl_type_definition(MDLTypeDef)}
    __sInitialized = False
    __sColorTypes = [mdldict.getMDLPredefTypePath(MDLPredefTypes.FLOAT),
                     mdldict.getMDLPredefTypePath(MDLPredefTypes.FLOAT3),
                     mdldict.getMDLPredefTypePath(MDLPredefTypes.COLOR),
                     mdldict.getMDLPredefTypePath(MDLPredefTypes.COLOR_LAYER)]

    MATERIAL_CONSTRUCTOR_FUNCTION = 'mdl::material(bool,material_surface,material_surface,color,material_volume,material_geometry,hair_bsdf)'

    __typeFloat = mdldict.getMDLPredefTypePath(MDLPredefTypes.FLOAT)
    __typeString = mdldict.getMDLPredefTypePath(MDLPredefTypes.STRING)

    __annotationsLibrary = {
        MDLAnnotationEnum.AUTHOR: MDLAnnotationDef(aPath='mdl::anno::author(string)',
                                                   aParameters=[
                                                       MDLNodeDefParamValue(aName='name', aType=__typeString)]),
        MDLAnnotationEnum.CONTRIBUTOR: MDLAnnotationDef(aPath='mdl::anno::contributor(string)',
                                                        aParameters=[
                                                            MDLNodeDefParamValue(aName='name', aType=__typeString)]),
        MDLAnnotationEnum.COPYRIGHT: MDLAnnotationDef(aPath='mdl::anno::copyright_notice(string)',
                                                      aParameters=[
                                                          MDLNodeDefParamValue(aName='copyright', aType=__typeString)]),
        MDLAnnotationEnum.DESCRIPTION: MDLAnnotationDef(aPath='mdl::anno::description(string)',
                                                        aParameters=[MDLNodeDefParamValue(aName='description',
                                                                                          aType=__typeString)]),
        MDLAnnotationEnum.DISPLAY_NAME: MDLAnnotationDef(aPath='mdl::anno::display_name(string)',
                                                         aParameters=[
                                                             MDLNodeDefParamValue(aName='name', aType=__typeString)]),
        MDLAnnotationEnum.GAMMA_TYPE: MDLAnnotationDef(
            aPath='mdl::alg::base::annotations::gamma_type(mdl::tex::gamma_mode)',
            aParameters=[MDLNodeDefParamValue(aName='type', aType='mdl::tex::gamma_mode', aValue='0')]),
        MDLAnnotationEnum.KEYWORDS: MDLAnnotationDef(aPath='mdl::anno::key_words(string[])',
                                                     aParameters=[MDLNodeDefParamValue(aName='words',
                                                                                       aType=__typeString + '[]')]),
        MDLAnnotationEnum.IN_GROUP: MDLAnnotationDef(aPath='mdl::anno::in_group(string,string,string)',
                                                     aParameters=[
                                                         MDLNodeDefParamValue(aName='group', aType=__typeString),
                                                         MDLNodeDefParamValue(aName='subgroup', aType=__typeString),
                                                         MDLNodeDefParamValue(aName='subsubgroup',
                                                                              aType=__typeString)]),
        MDLAnnotationEnum.HIDDEN: MDLAnnotationDef(aPath='mdl::anno::hidden()', aParameters=[]),
        MDLAnnotationEnum.SAMPLER_USAGE: MDLAnnotationDef(aPath='mdl::anno::usage(string)',
                                                          aParameters=[
                                                              MDLNodeDefParamValue(aName='hint', aType=__typeString)]),
        MDLAnnotationEnum.SOFT_RANGE: MDLAnnotationDef(aPath='mdl::anno::soft_range(float,float)',
                                                       aParameters=[MDLNodeDefParamValue(aName='min', aType=__typeFloat,
                                                                                         aValue='0'),
                                                                    MDLNodeDefParamValue(aName='max', aType=__typeFloat,
                                                                                         aValue='0')]),
        MDLAnnotationEnum.HARD_RANGE: MDLAnnotationDef(aPath='mdl::anno::hard_range(float,float)',
                                                       aParameters=[MDLNodeDefParamValue(aName='min', aType=__typeFloat,
                                                                                         aValue='0'),
                                                                    MDLNodeDefParamValue(aName='max', aType=__typeFloat,
                                                                                         aValue='1')]),
        MDLAnnotationEnum.VISIBLE_BY_DEFAULT: MDLAnnotationDef(
            aPath='mdl::alg::base::annotations::visible_by_default(bool)',
            aParameters=[MDLNodeDefParamValue(aName='description', aType='mdl::bool', aValue='true')])
    }


    def __init__(self):
        self.mObjectsToResolve = []

    @staticmethod
    @handle_exceptions()
    def addRootPath(aPath):
        """
        addRootPath()
        Add the given absolute path to the list of mdl root paths

        :param aPath: The absolute path to the directory to add
        :type aPath: str
        :raise: IOError in case the provided path does not exists
        """
        if not os.path.isdir(aPath):
            raise IOError('Cannot add the given path as a root mdl path, it is not a directory: '+aPath)

        MDLManager.__sMDLRootPaths.append(aPath)
        if MDLManager.__sInitialized:
            MDLManager.extractMDLModulesFrom(aRootPaths = [aPath])

    @staticmethod
    @handle_exceptions()
    def extractMDLModulesFrom(aRootPaths):
        """
        extractMDLModulesFrom(aRootPaths)
        Call mdltools executable to extract the JSON data of the mdl module found in the given list of root path.

        :param aRootPaths: The root path list to consider
        :type aRootPaths: list of strings
        :return: the number of extracted items
        """
        from pysbs import context

        log.info('Parsing mdl modules info...')

        # Call mdltools executable to get MDL content as JSON description
        mdlToolsPath = context.Context.getBatchToolExePath(sbsenum.BatchToolsEnum.MDLTOOLS)
        if mdlToolsPath is None or not os.path.exists(mdlToolsPath):
            raise IOError('Can\'t get mdl data, mdltools executable is not found in '+
                          python_helpers.castStr(context.Context.getAutomationToolkitInstallPath()))

        tmpFolder = context.UrlAliasMgr.buildTmpFolderPath('mdlinfo')
        with python_helpers.createTempFolders(tmpFolder):

            aCommand = [mdlToolsPath, 'module-info', '--output-dir', tmpFolder]
            for rootPath in aRootPaths:
                aCommand.extend(['--mdl-root-dir', rootPath])
            try:
                subprocess.check_output(aCommand)
                jsonFiles = [os.path.join(tmpFolder, f) for f in os.listdir(tmpFolder) if os.path.isfile(os.path.join(tmpFolder, f))]

                # Extract MDL node definition from JSON data
                nbItems = 0
                for aJsonFile in jsonFiles:
                    with open(aJsonFile) as dataFile:
                        jsonData = json.load(dataFile)
                        nbItems += MDLManager.parseJsonData(jsonData)

                # sort versionned path from most recent to least recent MDL version, and only keep versionned path
                for path in MDLManager.__sMDLVersionnedFunctionDictionary.keys():
                    versionnedData = MDLManager.__sMDLVersionnedFunctionDictionary[path]
                    MDLManager.__sMDLVersionnedFunctionDictionary[path] = [
                        versionnedPath
                        for version, versionnedPath in sorted(versionnedData, key=lambda _: _[0], reverse=True)
                    ]

                return nbItems

            except BaseException as error:
                log.error('Can\'t get mdl data, failed to execute mdltools (%s)', python_helpers.castStr(mdlToolsPath))
                raise error

    @staticmethod
    def getMDLNodeDefinition(aPath):
        """
        getMDLNodeDefinition(aPath)
        Get the MDLNodeDef object corresponding to the given mdl path

        :param aPath: The mdl path (for instance 'mdl::base::color_layer(color,float,::base::color_layer_mode)')
        :type aPath: string
        :return: The :class:`.MDLNodeDef` object if the path is found, None otherwise
        """
        if not MDLManager.__sInitialized:
            MDLManager.initAllMDLModules()

        return MDLManager.__sMDLFunctionDictionary.get(aPath, None)

    @staticmethod
    def getMDLTypeDefinition(aPath):
        """
        getMDLTypeDefinition(aPath)
        Get the MDLTypeDef object corresponding to the given mdl path

        :param aPath: The mdl path (for instance 'mdl::color')
        :type aPath: string
        :return: The :class:`.MDLTypeDef` object if the path is found, None otherwise
        """
        if not MDLManager.__sInitialized:
            MDLManager.initAllMDLModules()

        aTypeDef = MDLManager.__sMDLTypeDictionary.get(aPath, None)

        # Handle the case of a array of a known type
        if aTypeDef is None and aPath.endswith('[]'):
            aCompTypeDef = MDLManager.getMDLTypeDefinition(aPath[:-2])
            if aCompTypeDef:
                aTypeDef = MDLTypeDef(aPath=aPath,
                                      aKind=MDLTypeDefKindEnum.ARRAY,
                                      aComponentType=aCompTypeDef.mPath,
                                      aArrayDeferredSize=True)
        return aTypeDef

    @staticmethod
    def getMDLAnnotationDefinition(aAnnotation):
        """
        getMDLAnnotationDefinition(aAnnotation)
        Get the annotation definition

        :param aAnnotation: The annotation to get, as an enumeration value, or a complete mdl path
        :type aAnnotation: :class:`.MDLAnnotationEnum` or str
        :return: The annotation definition as a :class:`.MDLAnnotationDef`
        """
        try:
            aAnnotationEnum = mdldict.getAnnotationEnum(aAnnotation) if not isinstance(aAnnotation, int) else aAnnotation
            return MDLManager.__annotationsLibrary[aAnnotationEnum]
        except:
            raise SBSLibraryError('Invalid annotation provided: '+str(aAnnotation))

    @staticmethod
    def getGraphDefaultAnnotations():
        """
        getGraphDefaultAnnotations()
        Get the list of annotation definition for a MDL graph.

        :return: a list of :class:`.MDLAnnotation`
        """
        return [MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.DESCRIPTION),
                MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.IN_GROUP),
                MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.DISPLAY_NAME),
                MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.KEYWORDS),
                MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.COPYRIGHT),
                MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.AUTHOR)]

    @staticmethod
    def getConstantDefaultAnnotations(aTypePath, aExposed):
        """
        getConstantDefaultAnnotations(aTypePath, aExposed)
        Get the list of annotation definition for a MDL constant node.

        :param aTypePath: mdl path of the type of the constant
        :param aExposed: True to consider a constant exposed as an input parameter, False otherwise
        :type aTypePath: str
        :type aExposed: bool
        :return: a list of :class:`.MDLAnnotation`
        """
        annotList = [MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.DESCRIPTION),
                     MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.DISPLAY_NAME),
                     MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.IN_GROUP)]
        if MDLManager.isAColor(aTypePath=aTypePath):
            annotList.append(MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.GAMMA_TYPE))
        if aExposed:
            annotList.append(MDLManager.getMDLAnnotationDefinition(MDLAnnotationEnum.SAMPLER_USAGE))
        return annotList

    @staticmethod
    def getAcceptConnectionByDefaultForType(aTypePath, aParamListContainsRefOrMaterial):
        """
        getAcceptConnectionByDefaultForType(aTypePath, aParamListContainsRefOrMaterial)
        Get the default connectivity status for an input pin, depending on the given type

        :param aTypePath: the mdl path of the type
        :type aTypePath: str
        :type aParamListContainsRefOrMaterial: bool
        :return: True if by default this type accepts connection, False otherwise
        """
        if aTypePath == mdldict.getMDLPredefTypePath(MDLPredefTypes.COLOR):
            return True
        typeDef = MDLManager.getMDLTypeDefinition(aTypePath)
        if not typeDef:
            return False
        if aParamListContainsRefOrMaterial:
            return typeDef.isReference() or (typeDef.isStruct() and typeDef.isMaterial())
        return not typeDef.isString()

    @staticmethod
    def getRootPaths():
        """
        getRootPaths()
        Get the list of MDL root paths

        :return: The MDL root paths package path as a list of strings
        """
        return MDLManager.__sMDLRootPaths

    @staticmethod
    @handle_exceptions()
    def initAllMDLModules():
        """
        initAllMDLModules()
        Initialize the MDL library with all the modules found in the MDL root paths
        """
        MDLManager.extractMDLModulesFrom(aRootPaths=MDLManager.__sMDLRootPaths)
        MDLManager.__sInitialized = True

    @staticmethod
    @handle_exceptions()
    def isAColor(aTypePath):
        """
        isAColor(aTypePath)
        Check whether the given type is related to a color or not.

        :return: True if this type can be interpreted as a color, False otherwise
        """
        return aTypePath in MDLManager.__sColorTypes

    @staticmethod
    @handle_exceptions()
    def isModulePathBlackListed(aPath):
        """
        isModulePathBlackListed(aPath)
        Check if the given mdl path is black listed and cannot be instantiated as a node

        :param aPath: The path to check
        :type aPath: str
        :return: True if the path is black listed, False otherwise
        """
        return aPath is None or \
               aPath.startswith('mdl::std') or \
               aPath.startswith('mdl::limit') or \
			   aPath.startswith('mdl::noise') or \
			   aPath.startswith('mdl::nvidia::axf_importer') or \
               aPath.startswith('mdl::nvidia::df')

    @staticmethod
    @handle_exceptions()
    def parseJsonData(jsonData):
        """
        parseJsonData(jsonData)
        Parse the given JSON data to extract the MDL functions and materials found in it

        :param jsonData: The JSON data, in the format created by 'mdltools' executable
        :return: the number of extracted items
        """
        nbItems = 0
        for aType in jsonData.get("types", []):
            mdlTypeDef = MDLTypeDef()
            mdlTypeDef.fromJSON(aType)
            MDLManager.__sMDLTypeDictionary[mdlTypeDef.mPath] = mdlTypeDef
            nbItems += 1

        for aFunction in jsonData.get("functions", []):
            if not MDLManager.isModulePathBlackListed(aFunction.get('mdl_path')):
                mdlNodeDef = MDLNodeDef(aIsMaterial=False)
                mdlNodeDef.fromJSON(aFunction)
                MDLManager.__sMDLFunctionDictionary[mdlNodeDef.mPath] = mdlNodeDef

                splitDollar = mdlNodeDef.mPath.split('$')
                if len(splitDollar) > 1:
                    assert len(splitDollar) == 2, 'Split dollar length supposed to be 2 instead of {} : {}'.format(len(splitDollar), splitDollar)
                    functionname, remaining = splitDollar
                    version, remaining = remaining.split('(')
                    arguments = '(' + remaining

                    nonVersionnedPath = functionname + arguments

                    versionnedData = ( float(version), mdlNodeDef.mPath )
                    MDLManager.__sMDLVersionnedFunctionDictionary[nonVersionnedPath].append(versionnedData)

                nbItems += 1

        for aMaterial in jsonData.get("materials", []):
            if not MDLManager.isModulePathBlackListed(aMaterial.get('mdl_path')):
                mdlNodeDef = MDLNodeDef(aIsMaterial=True)
                mdlNodeDef.fromJSON(aMaterial)
                MDLManager.__sMDLFunctionDictionary[mdlNodeDef.mPath] = mdlNodeDef
                nbItems += 1
        return nbItems

    @handle_exceptions()
    def setRootPaths(self, aPathList):
        """
        setRootPaths(aPathList)
        If the given root path list is different from the ones already loaded, reinitialize the MDL library with the given root path.
        Do nothing otherwise.

        :param aPathList: the MDL root path list to set, as absolute paths
        :type aPathList: list of string
        """
        if aPathList is None or set(aPathList) == set(MDLManager.__sMDLRootPaths):
            return
        MDLManager.__sMDLRootPaths = aPathList
        MDLManager.__sMDLFunctionDictionary = {}
        MDLManager.__sMDLTypeDictionary = {}
        if self.__sInitialized:
            self.initAllMDLModules()


    @staticmethod
    @handle_exceptions()
    def resolveVersionnedFunctionPath(path):
        """
        Check if the parsed path match mdltools MDL specification, if not change it to a versionned function path

        :param path: mdl path to resolve
        :type path: str
        :return: str, resolved path, same as argument if not resolved required
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        if not MDLManager.__sInitialized:
            MDLManager.initAllMDLModules()

        if path in MDLManager.__sMDLFunctionDictionary:
            return path
        else:
            versionnedPaths = MDLManager.__sMDLVersionnedFunctionDictionary[path]

            if len(versionnedPaths) > 0:
                return versionnedPaths[0]
            else:
                raise SBSLibraryError(
                    'MDL function path {path} cannot be resolved.'.format(path=path) +
                    ' Known versionned functions are : {functions}'.format(functions=versionnedPaths)
                )






