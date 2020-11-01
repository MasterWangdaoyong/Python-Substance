# coding: utf-8
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import os
import sys
import subprocess
import xml.etree.ElementTree as ET

from pysbs.api_exceptions import SBSImpossibleActionError
from pysbs.api_decorators import handle_exceptions
from pysbs import api_helpers, python_helpers
from pysbs import sbsenum


__errorPSDParseMissing = 'Failed to parse the PSD file, psdparse executable is not found.\n' + \
    'Please provide Substance Designer installation folder using Context.setSubstanceDesignerInstallPath().'


class PSDLayer:
    """
    Class PSDLayer is used to gather information on a layer of a PSD file

    Members:
        * mName      (str): name of the function definition.
        * mLayerNo   (str): unique identifier in the package/ context.
        * mFormat    (str): various attributes
        * mWidth     (int): width in pixel
        * mHeight    (int): height in pixel
        * mDepth     (:class:`.sbsenum.OutputFormatEnum`): bit depth
        * mColorMode (:class:`.sbsenum.ColorModeEnum`): color mode
    """
    def __init__(self, aName, aLayerNo, aFormat, aWidth, aHeight, aDepth, aColorMode):
        self.mName      = aName
        self.mLayerNo   = aLayerNo
        self.mFormat    = aFormat
        self.mWidth     = aWidth
        self.mHeight    = aHeight
        self.mDepth     = aDepth
        self.mColorMode = aColorMode

    def getFilterParamSize(self):
        return [api_helpers.getNearestPowerOf2(self.mWidth), api_helpers.getNearestPowerOf2(self.mHeight)]

    def getFilterParamColor(self):
        return self.mColorMode

    @staticmethod
    def convertDepthToSbsEnum(aDepth):
        if int(aDepth) == 16:
            return sbsenum.OutputFormatEnum.FORMAT_16BITS
        return sbsenum.OutputFormatEnum.FORMAT_8BITS

    @staticmethod
    def convertColorToSbsEnum(aColor):
        return sbsenum.ColorModeEnum.COLOR if aColor.startswith('RGB') else sbsenum.ColorModeEnum.GRAYSCALE


@handle_exceptions()
def getLayers(aContext, aPsdFileAbsPath):
    """
    getLayers(aContext, aPsdFileAbsPath)
    Get the list of layers included in the given .psd file.

    :param aContext: current execution context
    :param aPsdFileAbsPath: path of the .psd file
    :type aContext: :class:`.Context`
    :type aPsdFileAbsPath: str
    :return: a list of :class:`.PSDLayer`
    """
    def createPngLayer(aLayerName, aLayerNo, aPngElt):
        return PSDLayer(aName      = aLayerName,
                        aLayerNo   = aLayerNo,
                        aWidth     = int(aPngElt.get('WIDTH')),
                        aHeight    = int(aPngElt.get('HEIGHT')),
                        aFormat    = 'png',
                        aColorMode = PSDLayer.convertColorToSbsEnum(aPngElt.get('COLORTYPENAME')),
                        aDepth     = PSDLayer.convertDepthToSbsEnum(aPngElt.get('DEPTH')))

    def createRawLayer(aLayerName, aLayerNo, aRawElt):
        return PSDLayer(aName      = aLayerName,
                        aLayerNo   = aLayerNo,
                        aWidth     = int(aRawElt.get('COLS')),
                        aHeight    = int(aRawElt.get('ROWS')),
                        aFormat    = 'raw',
                        aColorMode = sbsenum.ColorModeEnum.COLOR if int(aRawElt.get('CHANNELS'))>1 else sbsenum.ColorModeEnum.GRAYSCALE,
                        aDepth     = sbsenum.OutputFormatEnum.FORMAT_32BITS_FLOAT)

    psdExePath = aContext.getPSDParseExePath()
    if not psdExePath:
        raise SBSImpossibleActionError(__errorPSDParseMissing)

    aLayersXml = None
    tmpFolder = aContext.getUrlAliasMgr().buildTmpFolderPath('psd')
    with python_helpers.createTempFolders(tmpFolder):
        try:
            cmd = python_helpers.encodeCommandForSubProcess(
                [psdExePath, '--xmlout', aPsdFileAbsPath, '-d', tmpFolder])

            aLayersXml = subprocess.check_output(cmd)

        except BaseException as error:
            log.error('Failed to use psdparse on the given file: %s', aPsdFileAbsPath)
            raise error

    try:
        aString = bytes(aLayersXml).decode(sys.getfilesystemencoding()) # Get content from output
        rootElt = ET.fromstring(aString.encode('utf-8'))                # Force utf-8 encoding for ET.fromstring()
        psdLayers = []
        layerElmts = rootElt.findall('LAYER[@NAME]')

        for i,aLayerElt in enumerate(layerElmts):
            aPNGElt = aLayerElt.find('PNG[@WIDTH][@HEIGHT]')
            if aPNGElt is not None:
                aLayer = createPngLayer(aLayerElt.get('NAME'),'layer'+str(i+1), aPNGElt)
                psdLayers.append(aLayer)

            aRAWElt = aLayerElt.find('RAW[@WIDTH][@HEIGHT]')
            if aRAWElt is not None:
                aLayer = createRawLayer(aLayerElt.get('NAME'),'layer'+str(i+1), aRAWElt)
                psdLayers.append(aLayer)

            layerMaskElmts = aLayerElt.findall('LAYERMASK')
            for aLayerMask in layerMaskElmts:
                aPNGElt = aLayerMask.find('PNG[@WIDTH][@HEIGHT]')
                if aPNGElt is not None:
                    aMask = createPngLayer(aLayerElt.get('NAME') + '.mask','layer'+str(i+1)+'.lmask', aPNGElt)
                    psdLayers.append(aMask)

                aRAWElt = aLayerMask.find('RAW[@WIDTH][@HEIGHT]')
                if aRAWElt is not None:
                    aMask = createRawLayer(aLayerElt.get('NAME') + '.mask','layer'+str(i+1)+'.lmask', aRAWElt)
                    psdLayers.append(aMask)

        return psdLayers

    except BaseException as error:
        log.error('Failed to get the layers from the given file: %s', aPsdFileAbsPath)
        raise error

@handle_exceptions()
def extractCompositeTo(aContext, aPsdFileAbsPath, aDestinationFolder):
    """
    extractCompositeTo(aContext, aPsdFileAbsPath, aDestinationFolder)
    Extract the composite image of the given .psd file into a .png file, and save it in the destination folder.

    :param aContext: current execution context
    :param aPsdFileAbsPath: path of the .psd file
    :param aDestinationFolder: absolute path of the destination folder
    :type aContext: :class:`.Context`
    :type aPsdFileAbsPath: str
    :type aDestinationFolder: str
    :return: the output path as a string
    """
    psdExePath = aContext.getPSDParseExePath()
    if not psdExePath:
        raise SBSImpossibleActionError(__errorPSDParseMissing)

    try:
        cmd = python_helpers.encodeCommandForSubProcess(
            [psdExePath, '-m', '-n', '-w', '--writepsd', '-d', aDestinationFolder, aPsdFileAbsPath])

        subprocess.check_output(cmd)
        return os.path.join(aDestinationFolder, os.path.basename(aPsdFileAbsPath))+'.png'
    except BaseException as error:
        log.error('Failed to use psdparse on the given file: %s', aPsdFileAbsPath)
        raise error

@handle_exceptions()
def extractLayerTo(aContext, aPsdFileAbsPath, aLayer, aDestinationFolder):
    """
    extractLayerTo(aContext, aPsdFileAbsPath, aLayer, aDestinationFolder)
    Extract the layer image of the given .psd file into a .png file, and save it in the destination folder.

    :param aContext: current execution context
    :param aPsdFileAbsPath: path of the .psd file
    :param aLayer: layer to extract
    :param aDestinationFolder: absolute path of the destination folder
    :type aContext: :class:`.Context`
    :type aPsdFileAbsPath: str
    :type aLayer: :class:`.PSDLayer`
    :type aDestinationFolder: str
    :return: the output path as a string
    """
    psdExePath = aContext.getPSDParseExePath()
    if not psdExePath:
        raise SBSImpossibleActionError(__errorPSDParseMissing)

    try:
        cmd = python_helpers.encodeCommandForSubProcess(
            [psdExePath, '-m', '-w', '-n', '--layernameno', aLayer.mLayerNo, '-d', aDestinationFolder, aPsdFileAbsPath])

        subprocess.check_output(cmd)
        return os.path.join(aDestinationFolder, aLayer.mLayerNo)+'.png'
    except BaseException as error:
        log.error('Failed to use psdparse on the given file: %s', aPsdFileAbsPath)
        raise error

def getPsdLayerFromList(aPsdLayerList, aLayerName):
    """
    getPsdLayerFromList(aPsdLayerList, aLayerName)

    :param aPsdLayerList: list of layer
    :type aPsdLayerList: list of :class:`.PSDLayer`
    :param aLayerName: the layer to find
    :type aLayerName: str
    :return: the :class:`.PSDLayer` object if found, None otherwise
    """
    return next((aLayer for aLayer in aPsdLayerList if aLayerName == aLayer.mName), None)

def getPsdLayerNameFromResource(aResource):
    """
    getPsdLayerNameFromResource(aResource)

    :param aResource: A Resource which should be based on a .psd layer
    :type aResource: class:`.SBSResource`
    :return: The layer name as save in the .psd file, or None if the resource is not extracted from a .psd file
    """
    begin = aResource.mFilePath.find('.psd/')
    if begin >= 0 and aResource.mFilePath.endswith('.png'):
        return aResource.mFilePath[begin+5:-4]
    return None
