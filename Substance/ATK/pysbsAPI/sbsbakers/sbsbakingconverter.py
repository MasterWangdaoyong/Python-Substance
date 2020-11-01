# coding: utf-8
"""
Module **sbsbakingconverter** aims to provide the definition of a BakingConverter.
"""

from __future__ import unicode_literals
import copy
import weakref

from pysbs.api_decorators import handle_exceptions
from pysbs.api_exceptions import SBSImpossibleActionError, SBSLibraryError
from pysbs import python_helpers
from pysbs.qtclasses import QtVariant, QtVariantTypeEnum
from pysbs.sbscommon.values import SBSOption

from . import sbsbakersdefaultprops
from . import sbsbakersdictionaries as bakersdict
from .sbsbakersenum import BakingStructureTagEnum, ConverterParamEnum


class BakingConverter(object):
    """
    This class provide the definition of a Baking converter.

    Members
        * mConverterID (str): id of the converter (unique)
        * mBakerType (str): Kind of converter, between 'imagemeshconverter' (default) and 'vectorialmeshconverter'
        * mIdentifier (str): identifier of the converter
        * mIsSelected (bool): True to activate this baker. Default to True
        * mForcedOutputFormat (str): Allow to force a particular output format for this converter. Default to None
    """
    def __init__(self, aIdentifier = '',
                 aConverterID      = '',
                 aBakerType        = 'imagemeshconverter',
                 aIsSelected       = True,
                 aForcedOutputFormat = None,
                 aCommonProperties = None,
                 aProperties       = None,
                 aOverrides        = None,
                 aGlobalParams     = None):
        super(BakingConverter, self).__init__()
        self.mIdentifier = aIdentifier
        self.mConverterID = aConverterID
        self.mBakerType = aBakerType
        self.mIsSelected = aIsSelected
        self.mForcedOutputFormat = aForcedOutputFormat

        self.__mGlobalParamsRef = None
        self.setGlobalParams(aGlobalParams)

        self.__mOutputProperties = copy.deepcopy(sbsbakersdefaultprops.sAllBakersOutputProperties)
        self.__mProperties = copy.deepcopy(sbsbakersdefaultprops.sAllBakersCommonProperties)
        if aCommonProperties:
            self.__mProperties.extend(copy.deepcopy(aCommonProperties))

        if aProperties:
            self.__mProperties.extend(copy.deepcopy(aProperties))

        if aOverrides is None:
            self.__mOverrides = [False for _ in range(len(sbsbakersdefaultprops.sOverridableProperties))]
        else:
            self.__mOverrides = aOverrides

        if self.mForcedOutputFormat:
            self.setParameterValue(ConverterParamEnum.DEFAULT__FORMAT, aForcedOutputFormat)


    def __str__(self):
        return self.mIdentifier

    @handle_exceptions()
    def fromSBSTree(self, aIndexConverter, aSBSTree, removeUsedOptions = False):
        """
        fromSBSTree(self, aIndexConverter, aSBSTree, removeUsedOptions = False)
        Parse the given sbs tree to set the BakingConverter

        :param aIndexConverter: Index of this converter in the Baking Parameters
        :param aSBSTree: The tree of options to parse to build the Baking Converter
        :param removeUsedOptions: True to allow removing the options used to build this baker from the given list. Default to False
        :type aIndexConverter: int
        :type aSBSTree: :class:`.SBSTree`
        :type removeUsedOptions: bool, optional
        :return: True if success
        """
        def getQtVariantValue(aType, aStrValue):
            qVariant = QtVariant(aType)
            qVariant.setValue(aStrValue)
            return qVariant.getValue()

        def setPropertiesFromSBSTree(optionPrefix, properties):
            for prop in properties:
                prop.fromSBSTree(optionPrefix)

        if removeUsedOptions:   aOptions = aSBSTree
        else:                   aOptions = copy.copy(aSBSTree)

        aBakingData = aOptions.getChildByName(str(aIndexConverter))[0]

        # Get overrides values
        guiProperties = aBakingData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.GUI_PROPERTIES))[0]
        aSizeTag = guiProperties.getChildByName('size')
        nbProperties = int(aSizeTag.mValue) if aSizeTag is not None and aSizeTag.mValue != '-1' else 0

        for i in range(1,nbProperties+1):
            aOverride = guiProperties.getChildByName(str(i))
            if aOverride:
                self.__mOverrides[i] = getQtVariantValue(QtVariantTypeEnum.BOOL, aOverride[0].getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.IS_OVERRIDEN)).mValue)
        self.__mOverrides[0] = self.__mOverrides[1]


        # Get properties
        aBakerSpecificData = aBakingData.getChildByName(self.mBakerType)[0]
        properties = aBakerSpecificData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.PROPERTIES))[0]

        aIdentifier = aBakingData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.IDENTIFIER)).mValue
        aSelected   = aBakingData.getChildByName(bakersdict.getBakingStructureTagName(BakingStructureTagEnum.IS_SELECTED)).mValue

        # Get the global properties
        p = aOptions.getChildByName(str(aIndexConverter))[0]
        setPropertiesFromSBSTree(p, self.__mOutputProperties)

        if aIdentifier:  self.mIdentifier = aIdentifier
        if aSelected:    self.mIsSelected = getQtVariantValue(QtVariantTypeEnum.BOOL, aSelected)

        aSizeTag = properties.getChildByName('size')
        nbProperties = int(aSizeTag.mValue) if aSizeTag is not None and aSizeTag.mValue != '-1' else 0
        for i in range(1, nbProperties + 1):
            aChildTag = properties.getChildByName(str(i))
            if aChildTag:
                aPropIdTag = aChildTag[0].getChildByName('id')
                aPropValueTag = aChildTag[0].getChildByName('value')
                if aPropIdTag and aPropValueTag:
                    #aPropId = bakersdict.getConverterParamEnum(aPropIdTag.mValue)
                    self.setParameterValue(aPropIdTag.mValue, aPropValueTag.mValue)

    @handle_exceptions()
    def getAllParameters(self):
        """
        getAllParameters()
        Get all the parameters defined on this Baker

        :return: a list of :class:`.BakingParam`
        """
        parametersList = copy.copy(self.__mOutputProperties)
        parametersList.extend(self.__mProperties)
        return parametersList

    @handle_exceptions()
    def getOverrideState(self, aParameter):
        """
        getOverrideState(aParameter)
        Get the given parameter override state

        :param aParameter: Identifier of the parameter to get
        :type aParameter: :class:`.ConverterParamEnum` or str
        :return: The override state as a boolean if possible, None otherwise
        """
        # Get the parameter from the current list of properties
        aParam = self.getParameter(aParameter)
        if aParam is not None:
            if aParam.mIdentifier in sbsbakersdefaultprops.sOverridableProperties:
                aOverrideIndex = sbsbakersdefaultprops.sOverridableProperties.index(aParameter)
                return self.__mOverrides[aOverrideIndex]
        return None

    @handle_exceptions()
    def getParameter(self, aParameter):
        """
        getParameter(aParameter)
        Get the given parameter

        :param aParameter: Identifier of the parameter to get
        :type aParameter: :class:`.ConverterParamEnum` or str
        :return: The parameter as a :class:`.QtVariant` if found, None otherwise
        :raise: :class:`api_exceptions.SBSLibraryError`
        """
        # Get Parameter name and enum
        paramName, paramEnum = self.__getParamNameAndEnum(aParameter)
        if paramEnum is None:
            raise SBSLibraryError('Parameter '+python_helpers.castStr(paramName)+' is not a valid baking parameter')

        # Start searching in the global properties
        aParam =  next((aParam for aParam in self.__mOutputProperties if aParam.mIdentifier == paramEnum), None)

        # Then search in the specific properties of this baker
        if aParam is None:
            aParam = next((aParam for aParam in self.__mProperties if aParam.mIdentifier == paramEnum), None)
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
    def moveUp(self):
        """
        moveUp()
        Move up this converter in the list of the parent baking parameters
        """
        self.__mGlobalParamsRef().moveUpBaker(self)

    @handle_exceptions()
    def moveDown(self):
        """
        moveDown()
        Move down this converter in the list of the parent baking parameters
        """
        self.__mGlobalParamsRef().moveDownBaker(self)

    @handle_exceptions()
    def resetDefaultProperty(self, aParameter):
        """
        resetDefaultProperty(aParameter)
        Reset the given overriden default property, to match the global default property of the Baking Parameters

        :param aParameter: The property to reset
        :type aParameter: :class:`.ConverterParamEnum` or str
        """
        paramName, paramEnum = self.__getParamNameAndEnum(aParameter)
        if paramEnum == ConverterParamEnum.DEFAULT__FORMAT and self.mForcedOutputFormat:
            return

        if paramEnum in sbsbakersdefaultprops.sOverridableProperties:
            index = sbsbakersdefaultprops.sOverridableProperties.index(paramEnum)
            aProp = self.getParameter(paramEnum)
            if aProp:
                # Set the default value
                aGlobalProp = self.__mGlobalParamsRef().getParameter(paramEnum)
                aProp.setValue(aGlobalProp.getValue())
                # Remove override tag
                if index < 2:
                    self.__mOverrides[0] = self.__mOverrides[1] = False
                else:
                    self.__mOverrides[index] = False


    @handle_exceptions()
    def setGlobalParams(self, aGlobalParams):
        """
        setGlobalParams(aGlobalParams)
        Set the reference to the parent Global Parameters

        :param aGlobalParams: The global parameters that include this converter
        :type aGlobalParams: :class:`.BakingParameters`
        :return: Nothing
        """
        self.__mGlobalParamsRef = weakref.ref(aGlobalParams) if aGlobalParams is not None else None

    @handle_exceptions()
    def setSelected(self, aSelected):
        """
        setSelected(aSelected)
        Select or deselect for the baking

        :param aSelected: True to select the converter, False to deselect it
        :type aSelected: bool
        """
        self.mIsSelected = aSelected

    @handle_exceptions()
    def setParameterValue(self, aParameter, aParamValue):
        """
        setParameterValue(aParameter, aParamValue)
        Set the value of the given parameter on this converter.
        Raise an exception if the parameter is not allowed on this converter.

        :param aParameter: Identifier of the parameter to set
        :param aParamValue: Value to set
        :type aParameter: :class:`.ConverterParamEnum` or str
        :type aParamValue: any type
        :return: Nothing
        :raise: :class:`.SBSImpossibleActionError`
        """
        # Get Parameter name and enum
        paramName, paramEnum = self.__getParamNameAndEnum(aParameter)
        if paramEnum is None:
            raise SBSLibraryError('Parameter '+paramName+' cannot be set on converter '+self.mIdentifier)

        # Get the parameter from the current list of properties
        aParam = self.getParameter(paramEnum)
        if aParam is None:
            raise SBSImpossibleActionError('Parameter '+paramName+' cannot be affected to converter '+self.mIdentifier)

        # Particular case of the output format
        if aParam.mIdentifier == ConverterParamEnum.DEFAULT__FORMAT:
            # Get the string name of the output format
            if isinstance(aParamValue, int):
                aParamValue = bakersdict.getBakerOutputFormatName(aParamValue)
            # In case the output is forced, set only the value if correct, without creating an override
            if self.mForcedOutputFormat is not None:
                if aParamValue == self.mForcedOutputFormat:
                    aParam.setValue(aParamValue)
                return

        # Set the value, and the override state if applicable
        aParam.setValue(aParamValue)
        if aParameter in sbsbakersdefaultprops.sOverridableProperties:
            aOverrideIndex = sbsbakersdefaultprops.sOverridableProperties.index(aParameter)
            if aOverrideIndex < 2:
                self.__mOverrides[0] = self.__mOverrides[1] = True
            else:
                self.__mOverrides[aOverrideIndex] = True

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
        Only parameters 'MESH__CAGE_FILE', 'MESH__SKEW_MAP', 'NORMAL_MAP', 'TEXTURE_FILE', 'DIRECTION_FILE' can be set by this function.
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
    def setFileParameterValueFromPreviousBaker(self, aParameter, aPreviousBaker):
        """
        setFileParameterValueFromPreviousBaker(aParameter, aPreviousBaker)
        Set the file path value of the given parameter as the relative path of the given resource.
        Only parameters 'NORMAL_MAP', 'TEXTURE_FILE', 'DIRECTION_FILE' can be set by this function.
        An exception will be raised if the parameter is not appropriate or if the converter is invalid.

        :param aParameter: Identifier of the parameter to set
        :param aPreviousBaker: The converter to use (provide an BakingConverter object or an identifier)
        :type aParameter: :class:`.ConverterParamEnum` or str
        :type aPreviousBaker: :class:`.BakingConverter` or str
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        okPreviousBaker = self.__mGlobalParamsRef().getBaker(aPreviousBaker)
        if not okPreviousBaker:
            raise SBSImpossibleActionError('Cannot set this converter as the input of the file parameter, cannot found it')

        # Check converter order
        myIndex = self.__mGlobalParamsRef().mBakers.index(self)
        previousIndex = self.__mGlobalParamsRef().mBakers.index(okPreviousBaker)
        if previousIndex >= myIndex:
            raise SBSImpossibleActionError('Cannot set this converter as the input of the file parameter, it is not executed before')

        aBakerPath = 'baker://' + okPreviousBaker.mIdentifier
        self.__setFileParameterValue(aParameter, aBakerPath)

    @handle_exceptions()
    def toSBSOptionList(self, aIndexConverter):
        """
        toSBSOptionList(aIndexConverter)
        Convert the object structure of the BakingConverter into a list of sbs options, as it is saved in the .sbs file

        :param aIndexConverter: Index of this converter in the Baking Parameters
        :type aIndexConverter: int
        :return: A list of :class:`.SBSOptions` object with the content of the BakingConverter
        """

        def getSBSOptions(optionPrefix, properties):
            options = []
            for prop in properties:
                options.extend(prop.toSBSOptionList(optionPrefix))
            return options

        def getQtVariantStrValue(aType, aValue):
            qVariant = QtVariant(aType, aValue)
            return qVariant.getValueStr()

        converterOptionPrefix = bakersdict.getBakingStructureTagName(BakingStructureTagEnum.BAKING) + '/' + \
                                bakersdict.getBakingStructureTagName(BakingStructureTagEnum.RESOURCE_MODEL) + '/' + \
                                bakersdict.getBakingStructureTagName(BakingStructureTagEnum.CONVERTERS) + '/' + \
                                str(aIndexConverter) + '/'
        aOptionList = list()
        aOptionList.append(SBSOption(aName=converterOptionPrefix + bakersdict.getBakingStructureTagName(
            BakingStructureTagEnum.MESH_CONVERTER_ID),
                                  aValue=self.mConverterID))
        aOptionList.append(SBSOption(
            aName=converterOptionPrefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.IDENTIFIER),
            aValue=self.mIdentifier))

        aOptionList.extend(getSBSOptions(converterOptionPrefix, self.__mOutputProperties))

        # Set overrides values
        propertyOptionPrefix = converterOptionPrefix + bakersdict.getBakingStructureTagName(
            BakingStructureTagEnum.GUI_PROPERTIES) + '/'
        for i, aOverride in enumerate(self.__mOverrides[1:]):
            aOptionList.append(SBSOption(
                aName=propertyOptionPrefix + str(i + 1) + '/' + bakersdict.getBakingStructureTagName(
                    BakingStructureTagEnum.IS_OVERRIDEN),
                aValue=getQtVariantStrValue(QtVariantTypeEnum.BOOL, aOverride)))
        aOptionList.append(SBSOption(aName=propertyOptionPrefix + 'size', aValue=str(len(self.__mOverrides) - 1)))

        # Set properties values
        propertyOptionPrefix = converterOptionPrefix + self.mBakerType + '/' + bakersdict.getBakingStructureTagName(
            BakingStructureTagEnum.PROPERTIES) + '/'
        for i, aProp in enumerate(self.__mProperties):
            propPrefix = propertyOptionPrefix + str(i + 1) + '/'
            aOptionList.append(SBSOption(aName=propPrefix + 'id',
                                      aValue=bakersdict.getConverterParamName(aProp.mIdentifier)))
            aOptionList.extend(aProp.toSBSOptionList(propPrefix))
        aOptionList.append(SBSOption(aName=propertyOptionPrefix + 'size', aValue=str(len(self.__mProperties))))

        aOptionList.append(SBSOption(
            aName=converterOptionPrefix + bakersdict.getBakingStructureTagName(BakingStructureTagEnum.IS_SELECTED),
            aValue=getQtVariantStrValue(QtVariantTypeEnum.BOOL, self.mIsSelected)))
        return aOptionList

    @handle_exceptions()
    def updateDefaultProperties(self):
        """
        updateDefaultProperties()
        Update all the default properties that are not overriden, to match the global default properties of the Baking Parameters
        """
        for i, p in enumerate(sbsbakersdefaultprops.sOverridableProperties):
            if not self.__mOverrides[i]:
                aProp = self.getParameter(p)
                if aProp:
                    defaultProp = bakersdict.getDefaultFromCommon(p)
                    aGlobalProp = self.__mGlobalParamsRef().getParameter(defaultProp)
                    if not (aGlobalProp.mIdentifier == ConverterParamEnum.DEFAULT__FORMAT and self.mForcedOutputFormat is not None):
                        aProp.setValue(aGlobalProp.getValue())

    @handle_exceptions()
    def updateDefaultProperty(self, aParameter):
        """
        updateDefaultProperty(aParameter)
        Update the given default property if it is not overriden, to match the global default property of the Baking Parameters

        :param aParameter: The property to update
        :type aParameter: :class:`.ConverterParamEnum` or str
        """
        paramName, paramEnum = self.__getParamNameAndEnum(aParameter)
        if paramEnum == ConverterParamEnum.DEFAULT__FORMAT and self.mForcedOutputFormat is not None:
            return

        if paramEnum in sbsbakersdefaultprops.sOverridableProperties:
            index = sbsbakersdefaultprops.sOverridableProperties.index(paramEnum)
            if not self.__mOverrides[index]:
                aProp = self.getParameter(paramEnum)
                if aProp:
                    aGlobalProp = self.__mGlobalParamsRef().getParameter(paramEnum)
                    aProp.setValue(aGlobalProp.getValue())



    #==========================================================================
    # Private
    #==========================================================================
    @handle_exceptions()
    def __getParamNameAndEnum(self, aParameter):
        """
        Get Parameter name and enum
        """
        if python_helpers.isStringOrUnicode(aParameter):
            aParameterName = aParameter
            aParameterEnum = bakersdict.getConverterParamEnum(aConverterParamName=aParameterName)
        else:
            aParameterName = bakersdict.getConverterParamName(aConverterParam=aParameter)
            aParameterEnum = aParameter
        return aParameterName, aParameterEnum

    @handle_exceptions()
    def __setFileParameterValue(self, aParameter, aValue):
        """
        __setFileParameterValue(aParameter, aValue)
        Set the file path value of the given parameter as the relative path of the given resource.
        Only parameters 'MESH__CAGE_FILE', 'MESH__SKEW_MAP', 'NORMAL_MAP', 'TEXTURE_FILE', 'DIRECTION_FILE' can be set by this function.
        An exception will be raised if the parameter is not appropriate.

        :param aParameter: Identifier of the parameter to set
        :param aValue: The value to set
        :type aParameter: :class:`.ConverterParamEnum` or str
        :type aValue: str
        :return: True if success, False otherwise
        :raise: :class:`.SBSImpossibleActionError`
        """
        paramName, paramEnum = self.__getParamNameAndEnum(aParameter)

        # Get the current BakingConverterParam (from this converter or from the global params)
        aParam = self.getParameter(aParameter)
        if aParam is None:
            raise SBSImpossibleActionError('Parameter '+paramName+' cannot be affected to converter '+self.mIdentifier)

        # Check that the parameter is compatible with a resource
        if not aParam.isAResourceParam():
            raise SBSImpossibleActionError('Parameter '+paramName+' does not correspond to a resource')

        aParam.setValue(aValue)
