# coding: utf-8
from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
from pysbs.api_decorators import doc_source_code_enum
import os
import platform
import ctypes
import sys
import math
from pysbs import python_helpers
from pysbs import sbsenum

if   platform.system() == 'Windows':  _libFilenames = ['FreeImage.dll','FreeImaged.dll']
elif platform.system() == 'Darwin':   _libFilenames = ['libFreeImage.dylib','libFreeImaged.dylib']
elif platform.system() == 'Linux':    _libFilenames = ['libFreeImage.so','libFreeImaged.so']
else: _libFilenames = []
_freeImageWrapper = None

@doc_source_code_enum
class ImageFormat:
    """
    Enumeration of all image formats known to FreeImage
    """
    FIF_UNKNOWN = -1
    FIF_BMP     = 0
    FIF_ICO     = 1
    FIF_JPEG    = 2
    FIF_JNG     = 3
    FIF_KOALA   = 4
    FIF_LBM     = 5
    FIF_IFF = FIF_LBM
    FIF_MNG     = 6
    FIF_PBM     = 7
    FIF_PBMRAW  = 8
    FIF_PCD     = 9
    FIF_PCX     = 10
    FIF_PGM     = 11
    FIF_PGMRAW  = 12
    FIF_PNG     = 13
    FIF_PPM     = 14
    FIF_PPMRAW  = 15
    FIF_RAS     = 16
    FIF_TARGA   = 17
    FIF_TIFF    = 18
    FIF_WBMP    = 19
    FIF_PSD     = 20
    FIF_CUT     = 21
    FIF_XBM     = 22
    FIF_XPM     = 23
    FIF_DDS     = 24
    FIF_GIF     = 25
    FIF_HDR     = 26
    FIF_FAXG3   = 27
    FIF_SGI     = 28
    FIF_EXR     = 29
    FIF_J2K     = 30
    FIF_JP2     = 31
    FIF_PFM     = 32
    FIF_PICT    = 33
    FIF_RAW     = 34
    FIF_WEBP    = 35
    FIF_JXR     = 36

@doc_source_code_enum
class ImageType:
    """
    Enumeration of all image types known to FreeImage
    """
    FIT_UNKNOWN,\
    FIT_BITMAP ,\
    FIT_UINT16,\
    FIT_INT16,\
    FIT_UINT32,\
    FIT_INT32,\
    FIT_FLOAT,\
    FIT_DOUBLE,\
    FIT_COMPLEX,\
    FIT_RGB16,\
    FIT_RGBA16,\
    FIT_RGBF,\
    FIT_RGBAF \
    = range(13)

@doc_source_code_enum
class ImageColorType:
    """
    Enumeration of all image color types known to FreeImage
    """
    FIC_MINISWHITE,\
    FIC_MINISBLACK,\
    FIC_RGB,\
    FIC_PALETTE,\
    FIC_RGBALPHA,\
    FIC_CMYK5\
    = range(6)

class ImageData:
    def __init__(self, width, height, bpp, imageType, colorType):
        self.width = width
        self.height = height
        self.bpp = bpp
        self.imageType = imageType
        self.colorType = colorType


class FreeImageWrapper:
    """
    Wrapper for the FreeImage library.
    No intention to wrap the library completely,
    just the functionality needed for now
    """
    @staticmethod
    def initApiFunction(fn, argtypes, restype):
        """
        Helper for setting argument types and return types for a function in a dll

        :param fn: The function to operate on
        :type fn: _ctypes._FuncPtr
        :param argtypes: list of argument types
        :type argtypes: [_ctypes.PyCSimpleType]
        :param restype: the type for the return value
        :type restype: _ctypes.PyCSimpleType

        :return:  _ctypes._FuncPtr
        """
        res = fn
        res.argtypes = argtypes
        res.restype = restype
        return res

    def __init__(self, dll_path):
        if python_helpers.isPython2():
            aPath = dll_path.encode(sys.getfilesystemencoding())
        else:
            aPath = dll_path
        if python_helpers.isPython32Bit():
            raise OSError('FreeImage support only works in 64bit python')

        if platform.system() == 'Windows':
            self.freeImageLib = ctypes.WinDLL(aPath)
        else:
            self.freeImageLib = ctypes.CDLL(aPath)
        self.GetVersion = self.initApiFunction(self.freeImageLib.FreeImage_GetVersion,
            [],
            ctypes.c_char_p)
        self.GetFIFCount = self.initApiFunction(self.freeImageLib.FreeImage_GetFIFCount,
            [],
            ctypes.c_int)
        self.GetFormatFromFIF = self.initApiFunction(self.freeImageLib.FreeImage_GetFormatFromFIF,
            [ctypes.c_int],
            ctypes.c_char_p)
        self.GetFIFDescription = self.initApiFunction(self.freeImageLib.FreeImage_GetFIFDescription,
            [ctypes.c_int],
            ctypes.c_char_p)
        self.GetFIFExtensionList = self.initApiFunction(self.freeImageLib.FreeImage_GetFIFExtensionList,
            [ctypes.c_int],
            ctypes.c_char_p)
        self.GetFileType = self.initApiFunction(self.freeImageLib.FreeImage_GetFileType,
            [ctypes.c_char_p, ctypes.c_int],
            ctypes.c_int)
        self.GetFIFFromFilename = self.initApiFunction(self.freeImageLib.FreeImage_GetFIFFromFilename,
            [ctypes.c_char_p],
            ctypes.c_int)
        self.FIFSupportsReading = self.initApiFunction(self.freeImageLib.FreeImage_FIFSupportsReading,
            [ctypes.c_int],
            ctypes.c_bool)
        self.Load = self.initApiFunction(self.freeImageLib.FreeImage_Load,
            [ctypes.c_int, ctypes.c_char_p, ctypes.c_bool],
            ctypes.c_void_p)
        self.Unload = self.initApiFunction(self.freeImageLib.FreeImage_Unload,
            [ctypes.c_void_p],
            None)
        self.GetImageType = self.initApiFunction(self.freeImageLib.FreeImage_GetImageType,
            [ctypes.c_void_p],
            ctypes.c_int)
        self.GetBPP = self.initApiFunction(self.freeImageLib.FreeImage_GetBPP,
            [ctypes.c_void_p],
            ctypes.c_int)
        self.GetWidth = self.initApiFunction(self.freeImageLib.FreeImage_GetWidth,
            [ctypes.c_void_p],
            ctypes.c_int)
        self.GetHeight = self.initApiFunction(self.freeImageLib.FreeImage_GetHeight,
            [ctypes.c_void_p],
            ctypes.c_int)
        self.GetColorType= self.initApiFunction(self.freeImageLib.FreeImage_GetColorType,
            [ctypes.c_void_p],
            ctypes.c_int)


class Image:
    """
    Class representing an image
    Currently with a very limited API given the limited use of images in pysbs
    """
    def __init__(self, filename, fi):
        self.filename = filename
        self.fi = fi
        # Make sure self.image exists in case _load_image throws
        # otherwise __del__ will fail
        self.image_ptr = None
        self.image_ptr = self._load_image(filename)

    def _load_image(self, filename):
        """
        Loads an image from a file

        :param filename: The filename for the image
        :type filename: string

        :return: ctypes.c_void_p
        """
        # Make sure there is a file on disk at all
        if not os.path.isfile(filename):
            raise IOError('File not found: %s' % filename)

        filename_buf = python_helpers.ctypesStringBuffer(filename)

        # Check if the file is readable
        fif = self.fi.GetFileType(filename_buf, 0)
        if fif is ImageFormat.FIF_UNKNOWN:
            # No signature, try to guess format from extensions
            fif = self.fi.GetFIFFromFilename(filename_buf)

            # Check if the file format is known after guessing
            if fif is ImageFormat.FIF_UNKNOWN:
                raise IOError('Image format unknown: %s' % filename)

        # Check that the plugin has reading capabilities
        if not self.fi.FIFSupportsReading(fif):
            raise IOError('Image format not supported: %s' % filename)

        dib = self.fi.Load(fif, filename_buf, 0)
        if dib is None:
            raise IOError('Image reading failed: %s' % filename)
        return dib

    def getImageInformation(self):
        """
        Returns width, height and bits per pixel for an image

        :param self: self
        :type self: Image

        :return: ImageData with information about this image
        """
        if self.image_ptr is None:
            raise IOError('Image not initialized')
        return ImageData(self.fi.GetWidth(self.image_ptr),
                         self.fi.GetHeight(self.image_ptr),
                         self.fi.GetBPP(self.image_ptr),
                         self.fi.GetImageType(self.image_ptr),
                         self.fi.GetColorType(self.image_ptr))

    def unload(self):
        """
        Unloads the image. Called in the destructor if not done manually

        :param self: self
        :type self: Image
        """
        if self.image_ptr:
            self.fi.Unload(self.image_ptr)
            self.image_ptr = None

    def __del__(self):
        """
        Destructor, unloads the image

        :param self: self
        :type self: Image
        """
        self.unload()

def _getFreeImageWrapper(aContext):
    global _freeImageWrapper
    if _freeImageWrapper:
        return _freeImageWrapper

    # paths to look for for the freeimage dll
    fi_paths = [aContext.getAutomationToolkitInstallPath(),
                aContext.getSubstanceDesignerInstallPath()]

    # Initialize free image wrapper
    for (p,libName) in [(p,libName) for p in fi_paths for libName in _libFilenames]:
        try:
            if p is not None:
                _freeImageWrapper = FreeImageWrapper(os.path.join(p, libName))
                log.info('Using FreeImage library at: %s' % p)
                break
        # Exception handling, swallow known errors here
        # every call to GetImageInformation should be wrapped in a check of HasFreeImage to
        # check for failures here
        except OSError:
            pass

    if _freeImageWrapper is None:
        log.warning('Failed to load FreeImage, image sizes and bit depth won\'t be detected automatically for known file formats')
    else:
        log.info('FreeImage version %s' % _freeImageWrapper.GetVersion().decode("utf-8"))
    return _freeImageWrapper

def _bitsInMask(mask):
    return bin(mask).count('1')

def _closestPow2Above(size):
    return int(math.ceil(math.log(size, 2.0)))

def GetImageInformation(aFilePath, aContext):
    """
    GetImageInformation(aFilePath)
    Returns dimensions, color mode and format for the image aFilePath
    Check HasFreeImage before to validate that the dll has loaded correctly

    :param aFilePath: The path to the image to get information for
    :type aFilePath: str
    :param aContext: context to use to find paths to freeimage dll
    :type aContext: context.Context

    :return: (sbsenum.OutputSizeEnum, sbsenum.OutputSizeEnum, sbsenum.ColorModeEnum, sbsenum.OutputFormatEnum)
    """
    freeImageWrapper = _getFreeImageWrapper(aContext)
    if freeImageWrapper is None:
        raise BaseException('FreeImage not loaded')
    i = Image(aFilePath, freeImageWrapper)
    try:
        res = i.getImageInformation()
        color = sbsenum.ColorModeEnum.GRAYSCALE if (res.colorType is ImageColorType.FIC_MINISBLACK or res.colorType is ImageColorType.FIC_MINISWHITE) \
            else sbsenum.ColorModeEnum.COLOR

        w = _closestPow2Above(res.width)
        h = _closestPow2Above(res.height)
        if res.imageType is ImageType.FIT_BITMAP:
            # This is a standard image
            return w, h, color, sbsenum.OutputFormatEnum.FORMAT_8BITS
        elif (res.imageType is ImageType.FIT_UINT16) or \
                (res.imageType is ImageType.FIT_INT16) or \
                (res.imageType is ImageType.FIT_UINT32) or \
                (res.imageType is ImageType.FIT_INT32):
            return w, h, color, sbsenum.OutputFormatEnum.FORMAT_16BITS
        elif (res.imageType is ImageType.FIT_FLOAT) or \
                 (res.imageType is ImageType.FIT_DOUBLE):
            return w, h, color, sbsenum.OutputFormatEnum.FORMAT_32BITS_FLOAT
        elif (res.imageType is ImageType.FIT_RGB16) or \
             (res.imageType is ImageType.FIT_RGBA16):
            return w, h, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_16BITS
        elif (res.imageType is ImageType.FIT_RGBF) or \
                 (res.imageType is ImageType.FIT_RGBAF):
            return w, h, sbsenum.ColorModeEnum.COLOR, sbsenum.OutputFormatEnum.FORMAT_32BITS_FLOAT
        else:
            raise IOError("Failed to get image type for image")
    finally:
        i.unload()


def HasFreeImage(aContext):
    """
    Returns true if the freeimage dll loads cleanly on the machine

    :param aContext: context to use to find paths to freeimage dll
    :type aContext: context.Context

    :return: (sbsenum.OutputSizeEnum, sbsenum.OutputSizeEnum, sbsenum.ColorModeEnum, sbsenum.OutputFormatEnum)
    """
    return _getFreeImageWrapper(aContext) is not None