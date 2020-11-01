# coding: utf-8
"""
Module **sbspreset** aims to define sbsprs files, with helpers for making them interact
with compgraphs

Classes
    :class:`.SBSPRSPresets`
    :class:`.SBSPRSPreset`
    :class:`.SBSPRSPresetInput`
    :class:`.SBSPRSTypes`
"""

from __future__ import unicode_literals
import os
import xml.etree.ElementTree as ET
import logging
log = logging.getLogger(__name__)

from pysbs.api_decorators import doc_inherit,handle_exceptions,doc_source_code_enum
from pysbs.api_exceptions import SBSUninitializedError, SBSImpossibleActionError
from pysbs.common_interfaces import SBSObject, PresetInput, Preset
from pysbs import sbsparser
from pysbs import sbswriter
from pysbs.graph.inputparameters import SBSPreset, SBSPresetInput
from pysbs.sbscommon import SBSConstantValue
from pysbs.sbsenum import ParamTypeEnum
from pysbs import api_helpers


@doc_source_code_enum
class SBSPRSTypes:
    """
    Enumeration for sbsprs preset types
    """
    FLOAT1   = 0
    FLOAT2   = 1
    FLOAT3   = 2
    FLOAT4   = 3
    INTEGER1 = 4
    STRING   = 6
    INTEGER2 = 8
    INTEGER3 = 9
    INTEGER4 = 10

# Dict for converting types in SBS to SBSPRS
# Note how both BOOLEAN and INTEGER1 maps to INTEGER1
__SBS_to_SBSPRS_type_dict = {
    ParamTypeEnum.FLOAT1   : SBSPRSTypes.FLOAT1,
    ParamTypeEnum.FLOAT2   : SBSPRSTypes.FLOAT2,
    ParamTypeEnum.FLOAT3   : SBSPRSTypes.FLOAT3,
    ParamTypeEnum.FLOAT4   : SBSPRSTypes.FLOAT4,
    ParamTypeEnum.BOOLEAN  : SBSPRSTypes.INTEGER1,
    ParamTypeEnum.INTEGER1 : SBSPRSTypes.INTEGER1,
    ParamTypeEnum.INTEGER2 : SBSPRSTypes.INTEGER2,
    ParamTypeEnum.INTEGER3 : SBSPRSTypes.INTEGER3,
    ParamTypeEnum.INTEGER4 : SBSPRSTypes.INTEGER4,
    ParamTypeEnum.STRING   : SBSPRSTypes.STRING,
}

# Dict for converting types in SBSPRS to SBS
# Note how INTEGER1 is explicitly forced to INTEGER1 rather than BOOLEAN
__SBSPRS_to_SBS_type_dict = {
    v : k for k, v in __SBS_to_SBSPRS_type_dict.items()
}
__SBSPRS_to_SBS_type_dict[SBSPRSTypes.INTEGER1] = ParamTypeEnum.INTEGER1

def _convertSBSTypeToSBSPRSType(aType):
    return str(__SBS_to_SBSPRS_type_dict[int(aType)])

def _convertSBSPresetInputToSBSPRSInput(aInput):
    return SBSPRSPresetInput(aIdentifier=aInput.mIdentifier,
                             aType=_convertSBSTypeToSBSPRSType(aInput.getType()),
                             aUID=aInput.mUID,
                             aValue=aInput.mValue.mConstantValue)

def _convertSBSInputToSBSPRSInput(aInput):
    return SBSPRSPresetInput(aIdentifier=aInput.mIdentifier,
                             aType=_convertSBSTypeToSBSPRSType(aInput.getType()),
                             aUID=aInput.mUID,
                             aValue=aInput.mDefaultValue.mConstantValue)


def _convertSBSPRSTypeToSBSType(aType):
    return __SBSPRS_to_SBS_type_dict[aType]

def _convertSBSPRSValueToSBSValue(aValue, aType):
    v = SBSConstantValue()
    v.setConstantValue(aType, aValue)
    return v

def _convertSBSPRSPresetInputToSBSInput(aInput):
    sbsType = _convertSBSPRSTypeToSBSType(aInput.getType())
    return SBSPresetInput(aIdentifier=aInput.mIdentifier,
                          aType=str(sbsType),
                          aUID=aInput.mUID,
                          aValue=_convertSBSPRSValueToSBSValue(aInput.mValue, sbsType))


@doc_inherit
class SBSPRSPresetInput(SBSObject, PresetInput):
    """
    Class representing an SBSPRS preset

    Members:
        * mIdentifier   (str): Identifier for the value
        * mUID          (str): Uid for the value
        * mValue        (str): The value to set
        * mType         (str): The type of the value
    """
    def __init__(self,
                 aIdentifier = '',
                 aUID        = '',
                 aValue      = '',
                 aType       = ''):
        SBSObject.__init__(self)
        PresetInput.__init__(self,
                             aUID=aUID,
                             aIdentifier=aIdentifier,
                             aValue=aValue,
                             aType=aType)
        self.mMembersForEquality = ['mIdentifier',
                                    'mUID',
                                    'mValue',
                                    'mType']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mIdentifier = aSBSParser.getXmlElementAttribValue(aXmlNode, 'identifier')
        self.mUID        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'uid')
        self.mValue      = aSBSParser.getXmlElementAttribValue(aXmlNode, 'value')
        self.mType       = aSBSParser.getXmlElementAttribValue(aXmlNode, 'type')

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mIdentifier, 'identifier')
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mUID,        'uid')
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mValue,      'value')
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mType,       'type')

    @handle_exceptions()
    def getIdentifier(self):
        """
        getIdentifier()
        Gets the identifier of the preset input

        :return: identifier as string
        """
        return self.mIdentifier

    @handle_exceptions()
    def setIdentifier(self, aIdentifier):
        """
        setIdentifier(aIdentifier)
        Sets the identifier

        :param aIdentifier: The new identifier
        :type aIdentifier: string
        :return: None
        """
        self.mIdentifier = aIdentifier

    @handle_exceptions()
    def getUID(self):
        """
        getUID()
        Gets the uid of the preset input

        :return: uid as int
        """
        return int(self.mUID)

    @handle_exceptions()
    def setUID(self, aUID):
        """
        setUID(aUID)
        Sets the UID for the input parameter

        :param aUID: The new UID
        :type aUID: int
        :return: None
        """
        self.mUID = str(aUID)

    @handle_exceptions()
    def getValue(self):
        """
        getValue()
        Gets the value of the preset as string

        :return: value as string
        """
        return self.mValue

    @handle_exceptions()
    def getTypedValue(self):
        """
        getTypedValue()
        Gets the value of the preset as a value

        :return: value as float, string, int array of int or float depending on type
        """
        return api_helpers.getTypedValueFromStr(self.mValue, _convertSBSPRSTypeToSBSType(self.getType()))


    @handle_exceptions()
    def setValue(self, aValue):
        """
        setValue(aValue)
        Sets the value for the input parameter

        :param aValue: The new value
        :type aValue: string
        :return: None
        """
        self.mValue = aValue

    @handle_exceptions()
    def getType(self):
        """
        getType()
        Gets the type of the preset input

        :return: type as `:class:`.SBSPRSType`
        """
        return int(self.mType)

    @handle_exceptions()
    def setType(self, aType):
        """
        setType(aType)
        Sets the type for the input parameter

        :param aType: The new type
        :type aType: `:class:`.SBSPRSType`
        :return: None
        """
        self.mType = str(aType)

@doc_inherit
class SBSPRSPreset(SBSObject, Preset):
    """
    Class representing an SBSPRS preset

    Members:
        * mDescription  (str): Description of thew preset
        * mLabel        (str): Preset label
        * mPkgUrl       (str): Reference to which graph in the package the preset belongs to
        * mPresetInputs (list of :class:`.SBSPRSPresetInput`): Values for parameters in presets
    """
    def __init__(self,
                 aDescription = '',
                 aLabel       = '',
                 aUsertags    = None,
                 aPkgUrl      = '',
                 aPresetInputs = None):
        SBSObject.__init__(self)
        Preset.__init__(self,
                        aLabel=aLabel,
                        aUsertags=aUsertags,
                        aPresetInputs=aPresetInputs if aPresetInputs is not None else [])
        self.mDescription = aDescription
        self.mPkgUrl      = aPkgUrl
        self.mMembersForEquality = ['mDescription',
                                    'mLabel',
                                    'mUsertags',
                                    'mPkgUrl',
                                    'mPresetInputs']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mDescription  = aSBSParser.getXmlElementAttribValue(aXmlNode, 'description')
        self.mLabel        = aSBSParser.getXmlElementAttribValue(aXmlNode, 'label')
        self.mUsertags     = aSBSParser.getXmlElementAttribValue(aXmlNode, 'usertags')
        self.mPkgUrl       = aSBSParser.getXmlElementAttribValue(aXmlNode, 'pkgurl')
        self.mPresetInputs = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'presetinput', SBSPRSPresetInput)

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mDescription, 'description')
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mLabel, 'label')
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mUsertags, 'usertags')
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mPkgUrl, 'pkgurl')
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mPresetInputs, 'presetinput')

    @handle_exceptions()
    def addToGraph(self, aGraph):
        """
        addToGraph(aGraph)
        Adds this preset to an SBSGraph

        :param aGraph: The graph to add it to
        :type aGraph: :class:`.SBSGraph`
        :return: None
        """
        allPresetInputs = [_convertSBSPRSPresetInputToSBSInput(x) for x in self.mPresetInputs]
        cleanedPresetInputs = []
        # Cull presets based on names and types
        for pi in allPresetInputs:
            # First check if we can find a matching uid
            gi = aGraph.getInputFromUID(pi.mUID)
            if not gi:
                # If not matching uid, get by identifier
                gi = aGraph.getInput(pi.mIdentifier)
            if gi:
                # This preset exist on both the graph and material
                if gi.getType() == ParamTypeEnum.BOOLEAN and pi.getType() == ParamTypeEnum.INTEGER1:
                    # This preset came out as an integer but is an bool on the graph
                    # This means it's likely to be related to sbsprs treating BOOLEAN
                    # as INTEGER1
                    pi.setType(gi.getType())
                    pi.mValue.setConstantValue(gi.getType(), pi.getValue())
                    cleanedPresetInputs.append(pi)
                elif gi.getType() != pi.getType():
                    # This preset doesn't match the type in the graph
                    log.warning('Mismatching type for preset input %s in graph %s, skipping' % (gi.mIdentifier, aGraph.mIdentifier))
                else:
                    cleanedPresetInputs.append(pi)
                if gi.getUID() != pi.getUID():
                    log.warning('Mismatching UID for preset input %s in graph %s, correcting' % (gi.mIdentifier, aGraph.mIdentifier))
                    pi.setUID(gi.getUID())
                if gi.mIdentifier != pi.mIdentifier:
                    log.warning('Mismatching Identifier for preset input %s in graph %s, correcting' % (
                    gi.mIdentifier, aGraph.mIdentifier))
                    pi.mIdentifier = gi.mIdentifier
            else:
                log.warning('Preset refer to missing input %s in graph %s' % (gi.mIdentifier, aGraph.mIdentifier))
        api_helpers.addObjectToList(aObject=aGraph,
                                    aMemberListName='mPresets',
                                    aObjectToAdd=SBSPreset(
                                    aLabel=self.mLabel,
                                    aUsertags=self.mUsertags,
                                    aPresetInputs=cleanedPresetInputs))
    @handle_exceptions()
    def createPresetInput(self,
                          aIdentifier,
                          aUID,
                          aValue,
                          aType):
        """
        createPresetInput(aIdentifier, aUID, aValue, aType)
        Creates and adds a preset input

        :param aIdentifier: The identifier for the preset input
        :type aIdentifier: str
        :param aUID: The UID for the preset input
        :type aUID: int
        :param aValue: The value for the preset input
        :type aValue: str
        :param aType: The type for the preset
        :type aType: :class:`.SBSPRSType`
        :return: :class:`.SBSPRSPresetInput representing the new input`
        """
        presetInput = SBSPRSPresetInput(aIdentifier=aIdentifier,
                                        aUID=str(aUID),
                                        aValue=aValue,
                                        aType=str(aType))
        self.addPresetInput(presetInput)
        return presetInput

    @handle_exceptions()
    def createPresetInputFromSBSInput(self, aInput):
        """
        createPresetInputFromSBSInput(aInput)
        Creates and adds a preset input from an SBSParamInput

        :param aInput: The input to create a preset from
        :type aInput: :class:`.SBSParamInput`
        :return: :class:`.SBSPRSPresetInput representing the new input`
        """
        presetInput = _convertSBSInputToSBSPRSInput(aInput)
        self.addPresetInput(presetInput)

    @handle_exceptions()
    def getDescription(self):
        """
        getDescription()
        Gets the description of the preset

        :return: description as str
        """
        return self.mDescription

    @handle_exceptions()
    def setDescription(self, aDescription):
        """
        setDescription(aDescription)
        Sets the description for the preset

        :param aDescription: The new description
        :type aDescription: str
        :return: None
        """
        self.mDescription = aDescription

    @handle_exceptions()
    def getLabel(self):
        """
        getLabel()
        Gets the label for the preset

        :return: type as str
        """
        return self.mLabel

    @handle_exceptions()
    def setLabel(self, aLabel):
        """
        setLabel(aLabel)
        Sets the label for the preset

        :param aLabel: The new label
        :type aLabel: str
        :return: None
        """
        self.mLabel = aLabel

    @handle_exceptions()
    def getUsertags(self):
        """
        getUsertags()
        Gets the usertags for the preset

        :return: usertags as str
        """
        return self.mUsertags

    @handle_exceptions()
    def setUsertags(self, aUsertags):
        """
        setLabel(aUsertags)
        Sets the usertags for the preset

        :param aUsertags: The new label
        :type aUsertags: str
        :return: None
        """
        self.mUsertags = aUsertags


    @handle_exceptions()
    def getPkgUrl(self):
        """
        getPkgUrl()
        Gets the type package url for the preset

        :return: package url as str
        """
        return self.mPkgUrl

    @handle_exceptions()
    def setPkgUrl(self, aPkgUrl):
        """
        setPkgUrl(aPkgUrl)
        Sets the pkgurl the preset

        :param aPkgUrl: The pkgurl. Should contain pkg://
        :type aPkgUrl: str
        :return: None
        """
        self.mPkgUrl = aPkgUrl

    @handle_exceptions()
    def getPresetInputByIndex(self, aIndex):
        """
        getPresetInputByIndex(aIndex)
        Gets the preset at the specified index

        :param aIndex: The index
        :type aIndex: int
        :return: :class:`.SBSPRSPresetInput`
        """
        return self.mPresetInputs[aIndex]

    @handle_exceptions()
    def getPresetInputCount(self):
        """
        getPresetInputCount()
        Gets the number of preset inputs on the preset

        :return: int
        """
        return len(self.mPresetInputs)

    @handle_exceptions()
    def addPresetInput(self, aInput):
        """
        addPresetInput(aInput)
        Adds a preset input to the preset

        :param aInput: The preset to add
        :type aInput: :class:`.SBSPRSPresetInput`
        :return: None
        """
        if not self.getPresetInputFromIdentifier(aInput.mIdentifier):
            self.mPresetInputs.append(aInput)
        else:
            raise SBSImpossibleActionError('Preset Input with identifier %s already exists' % aInput.mIdentifier)

    @handle_exceptions()
    def removePresetInput(self, aPresetInput):
        """
        removePresetInput(aPresetInput)
        Removes an input preset

        :param aPresetInput: The preset to remove
        :type aPresetInput: :class:`.SBSPRSPresetInput`
        :return: None
        """
        return self.mPresetInputs.remove(aPresetInput)

@doc_inherit
class SBSPRSPresets(SBSObject):
    """
    Class representing the preset datastructure.

    Members:
        * mContext        (:class:`.Context`): Execution context, with alias definition
        * mFileAbsPath    (str): Absolute path of the package
        * mFormatVersion  (str): version of the format
        * mPresets        (list of :class:`.SBSPRSPreset`): Presets to add
    """
    def __init__(self, aContext, aFileAbsPath,
                 aFormatVersion = '',
                 aPresets       = None):
        SBSObject.__init__(self)
        self.mContext       = aContext
        self.mFileAbsPath   = os.path.abspath(aFileAbsPath)
        self.mFormatVersion = aFormatVersion
        self.mPresets       = aPresets if aPresets is not None else []
        self.mMembersForEquality = ['mFormatVersion',
                                    'mPresets']

    @handle_exceptions()
    def parse(self, aContext, aDirAbsPath, aSBSParser, aXmlNode):
        self.mFormatVersion = aSBSParser.getXmlElementAttribValue(aXmlNode, 'formatversion')
        count               = aSBSParser.getXmlElementAttribValue(aXmlNode,  'count')
        self.mPresets       = aSBSParser.getAllSBSElementsIn(aContext, aDirAbsPath, aXmlNode, 'sbspreset', SBSPRSPreset)
        if int(count) != len(self.mPresets):
            log.warning('Preset count in preset file set to %d but it contains %d presets' % (self.mCount, len(self.mPresets)))

    @handle_exceptions()
    def write(self, aSBSWriter, aXmlNode):
        aSBSWriter.setXmlElementAttribValue(aXmlNode, self.mFormatVersion, 'formatversion')
        aSBSWriter.setXmlElementAttribValue(aXmlNode, str(len(self.mPresets)), 'count')
        aSBSWriter.writeAllSBSNodesIn(aXmlNode, self.mPresets, 'sbspreset')

    @handle_exceptions()
    def parseDoc(self):
        """
        parseDoc()
        Parse the SBSPRS File content

        :return: True if succeed
        """
        aSBSParser = sbsparser.SBSParser(self.mFileAbsPath, self.mContext, aFileType = sbsparser.FileTypeEnum.SBSPRS)
        if aSBSParser is None or not aSBSParser.mIsValid:
            raise SBSUninitializedError('Failed to parse substance '+self.mFileAbsPath)

        aXmlRoot = aSBSParser.getRootNode()
        self.parse(self.mContext, os.path.dirname(self.mFileAbsPath), aSBSParser, aXmlRoot)
        self._mIsInitialized = True

        return True

    @handle_exceptions()
    def writeDoc(self, aNewFileAbsPath = None):
        """
        writeDoc(aNewFileAbsPath = None)
        Write the SBSPRS document in Element Tree structure and write it on the disk.
        If aNewFileAbsPath is provided, the document is saved at this location, otherwise it is save on the current file location.

        :param aNewFileAbsPath: The final location of the document. By default, the document is saved at the same location that the one provided when creating the document.
        :return: True if succeed
        """
        aXmlRoot = ET.Element('sbspresets')
        aSBSWriter = sbswriter.SBSWriter(aXmlRoot, self.mFileAbsPath, self.mContext)
        if aSBSWriter.mIsValid is False:
            return False

        if aNewFileAbsPath:
            self.mFileAbsPath = os.path.abspath(aNewFileAbsPath)

        self.write(aSBSWriter, aXmlRoot)
        aSBSWriter.writeOnDisk(self.mFileAbsPath, aFormatDoc=True, aIncludeXMLHeader=False)
        return True


    @handle_exceptions()
    def addSBSPresetFromGraph(self, aPreset, aGraph):
        """
        addSBSPresetFromGraph(aPreset, aGraph)
        Adds a preset from a graph

        :param aPreset: The preset to add
        :type aPreset: :class:`.SBSPreset`
        :param aGraph: The graph to add from
        :type aGraph: :class:`.SBSGraph`
        :return: :class:`.SBSPRSPreset`
        """
        newPreset = SBSPRSPreset(aLabel=aPreset.mLabel,
                                 aUsertags=aPreset.mUsertags,
                                 aPkgUrl='pkg://' + aGraph.mIdentifier,
                                 aPresetInputs=[_convertSBSPresetInputToSBSPRSInput(i) for i in aPreset.mPresetInputs])
        self.mPresets.append(newPreset)

    @handle_exceptions()
    def importAllPresetsFromGraph(self, aGraph):
        """
        importAllPresetsFromGraph(aGraph)
        Adds a all presets from a graph

        :param aGraph: The graph to add from
        :type aGraph: :class:`.SBSGraph`
        :return: list of :class:`.SBSPRSPreset`
        """
        return [self.addSBSPresetFromGraph(p, aGraph) for p in aGraph.mPresets]


    @handle_exceptions()
    def insertAllPresetsInSBS(self, aDoc):
        """
        insertAllPresetsInSBS(aDoc)
        Inserts all presets from the preset to an SBS document
        Ignores presets on graphs not present in the sbsdocument

        :param aDoc: the document to add presets to
        :type aDoc: :class:`.SBSDocument`
        :return: None
        """
        for p in self.mPresets:
            graphName = p.getPkgUrl().replace('pkg://', '')
            graph = aDoc.getSBSGraph(graphName)
            if graph:
                p.addToGraph(graph)
            else:
                log.warning('Target graph %s not present in sbs file: %s, ignoring' % (graphName, aDoc.mFileAbsPath))

    @handle_exceptions()
    def getPresetByIndex(self, aIndex):
        """
        getPresetByIndex(aIndex)
        Gets a preset at the specified index

        :param aIndex: The index to look for
        :type aIndex: int
        :return: :class:`.SBSPreset`
        """
        return self.mPresets[aIndex]

    @handle_exceptions()
    def getPresetByLabel(self, aLabel):
        """
        getPresetByLabel(aLabel)
        Gets a preset with the specified label

        :param aLabel: The label to look for
        :type aLabel: str
        :return: :class:`.SBSPreset` or None if not found
        """
        return next((x for x in self.mPresets if x.mLabel == aLabel), None)

    @handle_exceptions()
    def addPreset(self, aPreset):
        """
        addPreset(preset)
        Add preset

        :param aPreset: The label to look for
        :type aPreset: :class:`.SBSPreset`
        :return: None
        """
        if not self.getPresetByLabel(aPreset.mLabel):
            self.mPresets.append(aPreset)
        else:
            raise SBSImpossibleActionError('Preset with label %s already exists' % aPreset.mLabel)

    @handle_exceptions()
    def createPreset(self, aLabel, aDescription='', aUsertags=None, aGraph=None, aPkgUrl=None):
        """
        createPreset(aLabel, aDescription='', aGraph=None, aPkgUrl=None)
        Creates a new preset and returns it

        :param aLabel: The label for new preset
        :type aLabel: str
        :param aDescription: The description for the new preset
        :type aDescription: str
        :param aUsertags: Semi-colon separated tags for the preset
        :type aUsertags: str
        :param aGraph: The graph to make the preset apply to. Can't be used if specifying aPkgUrl
        :type aGraph: :class:`.SBSGraph`
        :param aPkgUrl: The pkgurl to apply the the preset to. Can't be used if specifying aGraph
        :type aPkgUrl: str
        :return: :class:`.SBSPRSPreset`
        """
        if aGraph is None and aPkgUrl is None:
            raise SBSImpossibleActionError('A preset needs either aGraph or aPkgUrl to be set')
        elif aGraph and aPkgUrl:
            raise SBSImpossibleActionError('A preset can not have both aGraph and aPkgUrl')
        elif aGraph:
            aPkgUrl = 'pkg://' + aGraph.mIdentifier
        preset = SBSPRSPreset(aDescription=aDescription,
                              aLabel=aLabel,
                              aUsertags=aUsertags,
                              aPkgUrl=aPkgUrl)
        self.addPreset(preset)
        return preset

    @handle_exceptions()
    def removePreset(self, aPreset):
        """
        removePreset(aPreset)
        Removes a preset

        :param aPreset: The preset to remove
        :type aPreset: :class:`.SBSPRSPreset`
        :return: None
        """
        self.mPresets.remove(aPreset)

    @handle_exceptions()
    def getPresetCount(self):
        """
        getPresetCount()
        Gets the total number of presets

        :return: int
        """
        return len(self.mPresets)
