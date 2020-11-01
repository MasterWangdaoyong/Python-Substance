# coding: utf-8
"""
| Module **sbsbakingparameters** aims to provide useful functions to read and modify the baking parameters of a Scene resource.
| The baking parameters are saved as an encoded string in the .sbs file, this is why a specific module is required for them.
"""
from __future__ import unicode_literals
import copy
import re

from pysbs.api_decorators import handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs import python_helpers
from pysbs.sbscommon.values import SBSOption
from pysbs import qtclasses

from . import sbsbakerslibrary
from . import sbsbakersdictionaries as bakersdict
from . import sbsbakersdefaultprops
from . import sbsbakingconverter
from . import sbsscenedata
from .sbsbakersenum import BakingStructureTagEnum, ConverterParamEnum


class BakingParameters:
    """
    Class that contains information on the Baking Parameters of a Scene resource

    Members:
        * mBakers            (list of :class:`.BakingConverter`): list of BakingConverters
        * mSubMeshColors     (list of :class:`.SubMeshColor`): list of SubMeshColor
        * mSubMeshSelections (list of :class:`.SubMeshSelection`): list of SubMeshSelection
        * mOutputProperties  (list of :class:`.BakingGlobalParam`): list of global output properties
        * mDefaultProperties (list of :class:`.BakingGlobalParam`): list of global default properties
        * mMeshProperties    (list of :class:`.BakingGlobalParam`): list of global mesh properties
    """
    def __init__(self, aBakers=None, aSubMeshColors=None, aSubMeshSelections=None):
        self.mBakers = aBakers if aBakers is not None else []
        self.mSubMeshColors = aSubMeshColors if aSubMeshColors is not None else []
        self.mSubMeshSelections= aSubMeshSelections if aSubMeshSelections is not None else []

        self.mOutputProperties  = copy.deepcopy(sbsbakersdefaultprops.sGlobalOutputProperties)
        self.mDefaultProperties = copy.deepcopy(sbsbakersdefaultprops.sGlobalBakersDefaultProperties)
        self.mMeshProperties    = copy.deepcopy(sbsbakersdefaultprops.sGlobalMeshesProperties)

        aFormat = self.getParameter(ConverterParamEnum.DEFAULT__FORMAT)
        if isinstance(aFormat.getValue(), int):
            aFormat.setValue(bakersdict.getBakerOutputFormatName(aFormat.getValue()))

    @handle_exceptions()
    def addHighDefinitionMeshFromFile(self, aAbsFilePath):
        """
        addHighDefinitionMeshFromFile(aAbsFilePath)
        Add the given absolute path to the list of High Definition Meshes for a 'From Mesh' converter.
        This modifies the parameter MESH__HIGH_DEF_MESHES of this converter.

        :param aAbsFilePath: The absolute path to the resource
        :type aAbsFilePath: str
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        aHighDefMeshesParam = self.getParameter(ConverterParamEnum.MESH__HIGH_DEF_MESHES)
        if not aHighDefMeshesParam:
            raise SBSImpossibleActionError('Cannot add a HighDefinitionMesh on this converter, the parameter is not available')

        aCurrentList = aHighDefMeshesParam.getValue()
        aFormattedPath = aAbsFilePath.replace('\\', '/')
        aFormattedPath = 'file:///'+aFormattedPath
        if not aFormattedPath in aCurrentList:
            aCurrentList.append(aFormattedPath)
            return True
        return False

    @handle_exceptions()
    def addHighDefinitionMeshFromResource(self, aResource):
        """
        addHighDefinitionMeshFromResource(aResource)
        Add the given resource in the list of High Definition Meshes for a 'From Mesh' converter.
        The resource must be already included in the package.
        This modifies the parameter MESH__HIGH_DEF_MESHES of this converter.

        :param aResource: The resource to reference
        :type aResource: :class:`.SBSResource`
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        aHighDefMeshesParam = self.getParameter(ConverterParamEnum.MESH__HIGH_DEF_MESHES)
        if not aHighDefMeshesParam:
            raise SBSImpossibleActionError('Cannot add a HighDefinitionMesh on this converter, the parameter is not available')

        aResourcePath = aResource.getPkgResourcePath()
        if not aResourcePath:
            raise SBSImpossibleActionError('Cannot add this resource to the HighDefinitionMeshes, failed to get its relative path')

        aCurrentList = aHighDefMeshesParam.getValue()
        if not aResourcePath in aCurrentList:
            aCurrentList.append(aResourcePath)
            return True
        return False

    @handle_exceptions()
    def addBaker(self, aIdentifier):
        """
        addBaker(aIdentifier)
        Add a BakingConverter of the given kind

        :param aIdentifier: Identifier of the converter to create
        :type aIdentifier: :class:`.BakerEnum`
        :return: The created :class:`.BakingConverter` object
        :raise: :class:`.SBSImpossibleActionError`
        """
        # Get and copy the baker definition
        aBakerDef = sbsbakerslibrary.getBakerDefinition(aIdentifier)
        if aBakerDef is None:
            raise SBSImpossibleActionError('Cannot add this converter, bad identifier')
        aBaker = copy.deepcopy(aBakerDef)

        # Compute a unique identifier
        aUniqueIdentifier = self.computeUniqueIdentifier(aBaker.mIdentifier)
        aBaker.mIdentifier = aUniqueIdentifier

        # Set the reference to the Baking Parameter, and the default properties
        aBaker.setGlobalParams(self)
        aBaker.updateDefaultProperties()

        self.mBakers.append(aBaker)
        return aBaker

    @handle_exceptions()
    def computeUniqueIdentifier(self, aIdentifier, aSuffixId = 0):
        """
        computeUniqueIdentifier(aIdentifier, aSuffixId = 0)
        Check if the given identifier is already used and generate a unique identifier if necessary

        :param aIdentifier: Identifier to check
        :type aIdentifier: str
        :param aSuffixId: Suffix ID
        :type aSuffixId: int
        :return: A unique identifier, which is either the given one or a new one with a suffix: identifier [id]
        """
        if aSuffixId == 0:
            match = re.search(r' \[[0-9]\]+$', aIdentifier)
            if match:
                aSuffix = aIdentifier[match.start():]
                aSuffixId = int(aSuffix[2:-1])
                aIdentifier = aIdentifier[0:match.start()]
            else:
                aSuffix = ''
                aSuffixId+=1
        else:
            aSuffix = ' [' + str(aSuffixId) + ']'
        aIdentifierToCheck = aIdentifier + aSuffix

        if self.getBaker(aBaker = aIdentifierToCheck) is not None:
            return self.computeUniqueIdentifier(aIdentifier, aSuffixId + 1)

        return aIdentifierToCheck

    @handle_exceptions()
    def fromSBSTree(self, aSBSTree):
        """
        fromSBSTree(aSBSTree)
        Get the content of the given SBSTree to set the Baking Parameters

        :param aSBSTree: The tree of options ot baking parameters from
        :type aSBSTree: :class:`.SBSTree`
        :return: True if success
        """
        def setPropertiesFromSBSTree(optionPrefix, tree, properties):
            for prop in properties:
                propName = bakersdict.getConverterParamName(prop.mIdentifier)
                value = tree.getChildByPath(optionPrefix + propName)
                if value:
                    if prop.getType() == qtclasses.QtVariantTypeEnum.STRING_LIST:
                        l = value[0].asStringList()
                        if l:
                            prop.setValue(l)
                    else:
                        prop.setValue(value.mValue)

        aTree = copy.copy(aSBSTree)

        # Get the global properties
        rootTag = bakersdict.getBakingStructureTagName(BakingStructureTagEnum.BAKING) + '/'
        prefix = rootTag + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_DEFAULT_VALUES_MODEL)+'/'
        setPropertiesFromSBSTree(prefix, aTree, self.mDefaultProperties)
        prefix = rootTag + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MESHES_MODEL)+'/'
        setPropertiesFromSBSTree(prefix, aTree, self.mMeshProperties)
        prefix = rootTag + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_OUTPUT_MODEL)+'/'
        setPropertiesFromSBSTree(prefix, aTree, self.mOutputProperties)

        # Get the submesh colors
        prefix = rootTag + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MODEL) + '/'
        colorDataTag = aTree.getChildByPath(prefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SUBMESH_COLORS))
        if colorDataTag:
            nbColors = colorDataTag[0].getChildByName('size')
            if nbColors is not None:
                for i in range(1,int(nbColors.mValue) + 1):
                   aSubMeshColor = sbsscenedata.SubMeshColor()
                   aSubMeshColor.fromSBSTree(aSBSTree=colorDataTag[0], aIndexColor=i, removeUsedOptions=True)
                   self.mSubMeshColors.append(aSubMeshColor)

        # Get the submesh selections
        selectionTag = aTree.getChildByPath(prefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SELECTIONS))
        if selectionTag:
            nbSelections = selectionTag[0].getChildByName('size')
            nbSelections = int(nbSelections.mValue) if nbSelections is not None and nbSelections != '-1' else 0
            for i in range(1,nbSelections+1):
                aSubMeshSelection = sbsscenedata.SubMeshSelection()
                aSubMeshSelection.fromSBSTree(aSBSTree=selectionTag[0], aIndexSelection=i, removeUsedOptions=True)
                self.mSubMeshSelections.append(aSubMeshSelection)

        # Get the bakers
        self.mBakers = []
        prefix = rootTag + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MODEL) + '/' + \
                 bakersdict.getBakingStructureTagName(BakingStructureTagEnum.CONVERTERS) + '/'

        converterTag = aTree.getChildByPath(prefix)
        if converterTag:
            nbConverters = converterTag[0].getChildByName('size')
            nbConverters = int(nbConverters.mValue) if nbConverters is not None else 0

            for i in range(1, nbConverters+1):
                prefixConverter = prefix + str(i) + '/'
                convIDTag = aTree.getChildByPath(prefixConverter + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.MESH_CONVERTER_ID))
                if convIDTag:
                    convID = convIDTag.mValue
                    aBakerDef = sbsbakerslibrary.getBakerDefinition(convID)
                    aBaker = copy.deepcopy(aBakerDef)
                    aBaker.setGlobalParams(self)
                    aBaker.fromSBSTree(aIndexConverter=i, aSBSTree=converterTag[0], removeUsedOptions=True)
                    self.mBakers.append(aBaker)
        return True

    @handle_exceptions()
    def getBaker(self, aBaker):
        """
        getBaker(aBaker)
        Get the BakingConverter object with the given identifier (ex: 'Ambient Occlusion')

        :param aBaker: Identifier of the baker
        :type aBaker: :class:`.BakerEnum` or str
        :return: The :class:`.BakingConverter` with this identifier if found, None otherwise
        """
        if isinstance(aBaker, sbsbakingconverter.BakingConverter):
            return aBaker if aBaker in self.mBakers else None

        if not python_helpers.isStringOrUnicode(aBaker):
            aBaker = sbsbakerslibrary.getBakerDefinition(aBaker).mIdentifier
        if self.mBakers:
            return next((b for b in self.mBakers if b.mIdentifier == aBaker), None)

    @handle_exceptions()
    def getNbBakers(self):
        """
        getNbBakers()
        Get the number of BakingConverter defined

        :return: The number of BakingConverter as an integer
        """
        return len(self.mBakers)

    @handle_exceptions()
    def getParameter(self, aParameter):
        """
        getParameter(aParameter)
        Get the global parameter with the given identifier

        :param aParameter: Identifier of the parameter to get
        :type aParameter: :class:`.ConverterParamEnum` or str
        :return: The parameter as a :class:`.QtVariant` if found, None otherwise
        """
        aParam = self.__getCommonParameterFromList(aParameter, self.mDefaultProperties)
        if aParam is None:
            aParam = self.__getCommonParameterFromList(aParameter, self.mMeshProperties)
        if aParam is None:
            aParam = self.__getCommonParameterFromList(aParameter, self.mOutputProperties)
        return aParam

    @handle_exceptions()
    def getParameterValue(self, aParameter):
        """
        getParameterValue(aParameter)
        Get the value of the parameter with the given identifier

        :param aParameter: Identifier of the parameter to get
        :type aParameter: :class:`.ConverterParamEnum` or str
        :return: The parameter value in the type of the parameter if found, None otherwise
        """
        aParam = self.getParameter(aParameter)
        return aParam.getValue() if aParam is not None else None

    @handle_exceptions()
    def getSubMeshColor(self, aEntityId, aSubMeshId):
        """
        getSubMeshColor(aEntityId, aSubMeshId)
        Get the SubMeshColor corresponding to the given (entityId, subMeshId)

        :return: The :class:`.SubMeshColor` object if found, None otherwise
        """
        return next((c for c in self.mSubMeshColors if c.mEntityId==aEntityId and c.mSubMeshId==aSubMeshId), None)

    @handle_exceptions()
    def getSubMeshColorHexa(self, aEntityId, aSubMeshId):
        """
        getSubMeshColorHexa(aEntityId, aSubMeshId)
        Get the hexadecimal color of the SubMeshColor corresponding to the given (entityId, subMeshId)

        :param aEntityId: Index of the entity that contains the submesh (start to 1)
        :param aSubMeshId: Index of the submesh part (start to 0)
        :type aEntityId: int
        :type aSubMeshId: int
        :return: The hexadecimal color as a string if it exists, None otherwise
        """
        color = self.getSubMeshColor(aEntityId, aSubMeshId)
        return color.mColor if color is not None else None

    @handle_exceptions()
    def getSubMeshSelection(self, aEntityId, aSubMeshId):
        """
        getSubMeshSelection(aEntityId, aSubMeshId)
        Get the SubMeshSelection corresponding to the given (entityId, subMeshId)

        :return: The :class:`.SubMeshSelection` object if found, None otherwise
        """
        return next((s for s in self.mSubMeshSelections if s.mEntityId==aEntityId and s.mSubMeshId==aSubMeshId), None)

    @handle_exceptions()
    def isSubMeshSelected(self, aEntityId, aSubMeshId):
        """
        isSubMeshSelected(aEntityId, aSubMeshId)
        Check if the given (entityId, subMeshId) is selected

        :param aEntityId: Index of the entity that contains the submesh (start to 1)
        :param aSubMeshId: Index of the submesh part (start to 0)
        :type aEntityId: int
        :type aSubMeshId: int
        :return: True if the given submesh index is selected, False otherwise
        """
        return self.getSubMeshSelection(aEntityId, aSubMeshId) is not None

    @handle_exceptions()
    def moveDownBaker(self, aBaker):
        """
        moveDownBaker(aBaker)
        Move down the given baker in the bakers list

        :param aBaker: Baker to move down in the bakers list
        :type aBaker: :class:`.BakingConverter` or :class:`.BakerEnum` or str
        :raise: :class:`.SBSImpossibleActionError`
        """
        okBaker = self.getBaker(aBaker)
        try:
            aIndex = self.mBakers.index(okBaker)
        except:
            if isinstance(aBaker, int):
                aBaker = sbsbakerslibrary.getBakerDefaultIdentifier(aBaker)
            raise SBSImpossibleActionError('Cannot move up the baker '+str(aBaker)+', could not find it in the BakingParameters')

        if aIndex < len(self.mBakers)-1:
            self.mBakers.insert(aIndex+1, self.mBakers.pop(aIndex))
        else:
            raise SBSImpossibleActionError('Cannot move down the baker ' + str(okBaker) + ', it is already the last converter')

    @handle_exceptions()
    def moveUpBaker(self, aBaker):
        """
        moveUpBaker(aBaker)
        Move up the given baker in the bakers list

        :param aBaker: Baker to move up in the bakers list
        :type aBaker: :class:`.BakingConverter` or :class:`.BakerEnum` or str
        :raise: :class:`.SBSImpossibleActionError`
        """
        okBaker = self.getBaker(aBaker)
        try:
            aIndex = self.mBakers.index(okBaker)
        except:
            if isinstance(aBaker, int):
                aBaker = sbsbakerslibrary.getBakerDefaultIdentifier(aBaker)
            raise SBSImpossibleActionError('Cannot move up the baker '+str(aBaker)+', could not find it in the BakingParameters')

        if aIndex > 0:
            self.mBakers.insert(aIndex-1, self.mBakers.pop(aIndex))
        else:
            raise SBSImpossibleActionError('Cannot move up the baker ' + str(aBaker) + ', it is already at position 0')

    @handle_exceptions()
    def removeBaker(self, aBaker):
        """
        removeBaker(aBaker)
        Remove the given baker

        :param aBaker: Baker to remove, as an object or an identifier
        :type aBaker: :class:`.BakingConverter` or :class:`.BakerEnum` or str
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        okBaker = self.getBaker(aBaker)
        try:
            self.mBakers.remove(okBaker)
        except:
            if isinstance(aBaker, int):
                aBaker = sbsbakerslibrary.getBakerDefaultIdentifier(aBaker)
            raise SBSImpossibleActionError('Cannot remove the converter '+str(aBaker)+', could not find it in the BakingParameters')

    @handle_exceptions()
    def selectBaker(self, aBaker, aSelected=True):
        """
        selectBaker(aBaker, aSelected=True)
        Select the given baker

        :param aBaker: Baker to select, as an object or an identifier
        :param aSelected: True to select the baker, False to deselect it
        :type aBaker: :class:`.BakingConverter` or :class:`.BakerEnum` or str
        :type aSelected: bool
        :raise: :class:`.SBSImpossibleActionError`
        """
        okBaker = self.getBaker(aBaker)
        try:
            okBaker.setSelected(aSelected)
        except:
            if isinstance(aBaker, int):
                aBaker = sbsbakerslibrary.getBakerDefaultIdentifier(aBaker)
            raise SBSImpossibleActionError('Cannot select the converter '+str(aBaker)+', could not find it in the BakingParameters')

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        """
        setParameterValue(aParameter, aParamValue)
        Set the value of the given global parameter

        :param aParameter: The parameter to set
        :param aParamValue: The value to set
        :type aParameter: :class:`.BakingGlobalParam`
        :type aParamValue: any type
        :raise: :class:`.SBSImpossibleActionError`
        """
        aParam = self.getParameter(aParameter)
        if aParam is None:
            raise SBSImpossibleActionError('Cannot set '+python_helpers.castStr(aParameter)+' as a global baking parameter')

        if aParam.mIdentifier == ConverterParamEnum.DEFAULT__FORMAT and isinstance(aParamValue, int):
            aParamValue = bakersdict.getBakerOutputFormatName(aParamValue)
        aParam.setValue(aParamValue)

        for aBaker in self.mBakers:
            aBaker.updateDefaultProperty(aParameter)

    @handle_exceptions()
    def setFileParameterValueFromPath(self, aParameter, aAbsPath):
        """
        setFileParameterValueFromPath( aParameter, aAbsPath)
        Set the file path value of the given parameter as the relative path of the given resource.
        Only parameters 'MESH__CAGE_FILE', 'MESH__SKEW_MAP', 'NORMAL_MAP', 'TEXTURE_FILE', 'DIRECTION_FILE' can be set by this function.
        An exception will be raised if the parameter is not appropriate.

        :param aParameter: Identifier of the parameter to set
        :param aAbsPath: The absolute path to the file resource
        :type aParameter: :class:`.ConverterParamEnum` or str
        :type aAbsPath: str
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        aFormattedPath = aAbsPath.replace('\\', '/')
        aFormattedPath = 'file:///' + aFormattedPath

        self.__setFileParameterValue(aParameter, aFormattedPath)

    @handle_exceptions()
    def setFileParameterValueFromResource(self, aParameter, aResource):
        """
        setFileParameterValueFromResource(aParameter, aResource)
        Set the file path value of the given parameter as the relative path of the given resource.
        Only parameters 'MESH__CAGE_FILE', 'NORMAL_MAP', 'TEXTURE_FILE', 'DIRECTION_FILE' can be set by this function.
        An exception will be raised if the resource is invalid or if the parameter is not appropriate.

        :param aParameter: Identifier of the parameter to set
        :param aResource: The resource to reference
        :type aParameter: :class:`.ConverterParamEnum` or str
        :type aResource: :class:`.SBSResource`
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        aResourcePath = aResource.getPkgResourcePath()
        if not aResourcePath:
            raise SBSImpossibleActionError('Cannot set this resource as the parameter value, failed to get its relative path')

        self.__setFileParameterValue(aParameter, aResourcePath)

    @handle_exceptions()
    def setSubMeshColorHexa(self, aEntityId, aSubMeshId, aColor):
        """
        setSubMeshColorHexa(aEntityId, aSubMeshId, aColor)
        Set the given color to the SubMesh part of the given Id

        :param aEntityId: Index of the entity that contains the submesh (start to 1)
        :param aSubMeshId: Index of the submesh part (start to 0)
        :param aColor: The hexadecimal color
        :type aEntityId: int
        :type aSubMeshId: int
        :type aColor: str
        :return: Nothing
        :raise: :class:`.SBSImpossibleActionError`
        """
        # Try to modify an existing setting
        for c in self.mSubMeshColors:
            if (c.mEntityId,c.mSubMeshId) == (aEntityId,aSubMeshId):
                c.setColorHexa(aColor)
                return

        # Add a new submesh color
        self.mSubMeshColors.append(sbsscenedata.SubMeshColor(aEntityId,aSubMeshId,aColor))

    @handle_exceptions()
    def setSubMeshSelection(self, aEntityId, aSubMeshId, aSelected):
        """
        setSubMeshSelection(aEntityId, aSubMeshId, aSelected)
        Set the given color to the SubMesh part of the given Id

        :param aEntityId: Index of the entity that contains the submesh (start to 1)
        :param aSubMeshId: Index of the submesh part (start to 0)
        :param aSelected: True to select the SubMesh part, False to deselect it
        :type aEntityId: int
        :type aSubMeshId: int
        :type aSelected: bool
        """
        # Try to find this SubMesh part in the current selection
        aCurrentSelection = self.isSubMeshSelected(aEntityId, aSubMeshId)

        if aSelected != aCurrentSelection:
            # Add the submesh part to the selection
            if aSelected:
                self.mSubMeshSelections.append(sbsscenedata.SubMeshSelection(aEntityId,aSubMeshId))
            # Remove the submesh from the selection
            else:
                self.mSubMeshSelections.remove((aEntityId,aSubMeshId))

    @handle_exceptions()
    def toSBSOptionList(self):
        """
        toSBSOptionList()
        Convert the object structure of the BakingParameters into a tree of SBSOptions, as it is saved in the .sbs file

        :return: A list of :class:`.SBSOptions` object with the content of the BakingParameters
        """
        def getSBSOptions(optionPrefix, properties):
            options = []
            for prop in properties:
                options.extend(prop.toSBSOptionList(optionPrefix))
            return options

        def getListSBSOptions(aList, aTag):
            options = []
            # Set the submesh selections
            for i, aItem in enumerate(aList):
                options.extend(aItem.toSBSOptionList(i + 1))
            aSize = len(aList) if aList else -1
            options.append(SBSOption(aName=aTag+'/size', aValue=str(aSize)))
            return options

        aSBSOptionList = list()

        # Set the global properties
        rootTag = bakersdict.getBakingStructureTagName(BakingStructureTagEnum.BAKING) + '/'
        prefix = rootTag+bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_DEFAULT_VALUES_MODEL)+'/'
        aSBSOptionList.extend(getSBSOptions(prefix, self.mDefaultProperties))
        prefix = rootTag+bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MESHES_MODEL)+'/'
        aSBSOptionList.extend(getSBSOptions(prefix, self.mMeshProperties))

        # Set the submesh colors
        prefix = rootTag+bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MODEL)+'/'
        aSBSOptionList.extend(getListSBSOptions(aList = self.mSubMeshColors,
                                             aTag  = prefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SUBMESH_COLORS)))
        # Set the bakers
        aSBSOptionList.extend(getListSBSOptions(aList = self.mBakers,
                                             aTag  = prefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.CONVERTERS)))
        # Set the submesh selections
        aSBSOptionList.extend(getListSBSOptions(aList = self.mSubMeshSelections,
                                             aTag = prefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.SELECTIONS)))
        # Set the output properties
        aSBSOptionList.extend(getSBSOptions(rootTag+bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_OUTPUT_MODEL)+'/',
                                         self.mOutputProperties))

        return aSBSOptionList


    #==========================================================================
    # Private
    #==========================================================================
    @handle_exceptions()
    def __getCommonParameterFromList(self, aParameter, aParameterList):
        """
        __getCommonParameterFromList(aParameter, aParameterList)
        Get the given parameter from the given list

        :param aParameter: Identifier of the parameter to get
        :type aParameter: :class:`.ConverterParamEnum` or str
        :param aParameterList: The list of parameters to consider
        :type aParameterList: list of :class:`.BakingGlobalParam`
        :return: The output parameter as a :class:`.QtVariant` if found, None otherwise
        """
        # Check library
        if python_helpers.isStringOrUnicode(aParameter):
            aParameter = bakersdict.getGlobalParamEnum(aParameter)
        else:
            bakersdict.getConverterParamName(aParameter)
        return next((aParam for aParam in aParameterList if aParam.mIdentifier == aParameter), None)


    @handle_exceptions()
    def __setFileParameterValue(self, aParameter, aValue):
        """
        __setFileParameterValue(aParameter, aValue)
        Set the file path value of the given parameter as the relative path of the given resource.
        Only parameters 'MESH__CAGE_FILE', 'NORMAL_MAP', 'TEXTURE_FILE', 'DIRECTION_FILE' can be set by this function.
        An exception will be raised if the parameter is not appropriate.

        :param aParameter: Identifier of the parameter to set
        :param aValue: The value to set
        :type aParameter: :class:`.ConverterParamEnum` or str
        :type aValue: str
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        # Check library (raise error if failed)
        if python_helpers.isStringOrUnicode(aParameter):
            aParameterName = aParameter
            aParameter = bakersdict.getGlobalParamEnum(aGlobalParamName=aParameterName)
        else:
            aParameterName = bakersdict.getConverterParamName(aParameter)

        # Get the current BakingConverterParam (from this converter or from the global params)
        aParam = self.getParameter(aParameter)
        if aParam is None:
            raise SBSImpossibleActionError('Parameter '+aParameterName+' cannot be affected globally on the BakingParameter')

        # Check that the parameter is compatible with a resource
        if not aParam.isAResourceParam():
            raise SBSImpossibleActionError('Parameter '+aParameterName+' does not correspond to a resource')

        aParam.setValue(aValue)
