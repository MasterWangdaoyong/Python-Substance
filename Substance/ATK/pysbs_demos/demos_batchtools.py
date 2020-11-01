# coding: utf-8
"""
Module **demos_batchtools** provides samples of usage of Pysbs in particular with the module batchtools.py.
"""
from __future__ import unicode_literals

import logging
log = logging.getLogger(__name__)
import os
import shutil
import sys

try:
    import pysbs
except ImportError:
    try:
        pysbsPath = bytes(__file__).decode(sys.getfilesystemencoding())
    except:
        pysbsPath = bytes(__file__, sys.getfilesystemencoding()).decode(sys.getfilesystemencoding())
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(pysbsPath)[0], '..')))

from pysbs.api_decorators import doc_source_code
from pysbs import base
from pysbs import python_helpers
from pysbs import substance
from pysbs import batchtools
from pysbs import sbsbakers



@doc_source_code
def demoUdimPipeline(aContext, aTemplateSbsPath, aDestSbsPath, aMeshPath, aUdimList, aOutputSize, aOutputBakingPath, aOutputRenderPath, aOutputSbsarPath=None):
    """
    | Demonstrates an automated pipeline implying a mesh with udim, executing this process:
    | sbsbaker => fill template .sbs with Pysbs => sbscooker => sbsrender

    :param aContext: Execution context
    :param aTemplateSbsPath: The absolute path of the template .sbs file
    :param aDestSbsPath: The absolute path of the .sbs file specified for the mesh.
    :param aMeshPath: The absolute path of the mesh to use to specify this template Substance
    :param aUdimList: The list of UDIM ids (MARI convention: "1001") available on this mesh. For instance "1001,1002"
    :param aOutputSize: Output size, as a power of two.
    :param aOutputBakingPath: Folder path where to save the output of the baking process for each udim
    :param aOutputRenderPath: Folder path where to save the output renderings of the Substance graph for each udim
    :param aOutputSbsarPath: Folder path where to save the output .sbsar specialized for each udim. Keep the value to None if there is no need to keep the .sbsar
    :type aContext: context.Context
    :type aTemplateSbsPath: str
    :type aDestSbsPath: str
    :type aMeshPath: str
    :type aUdimList: str
    :type aOutputSize: str
    :type aOutputBakingPath: str
    :type aOutputRenderPath: str
    :type aOutputSbsarPath: str, optional
    :return: True if success
    """

    def bakeUdim(_meshPath, _outputSize, _outputFormat, _outputBakingPath, _bakerName, _udim):
        """
        Call sbsbaker with the provided udim

        :param _meshPath: Path to the mesh
        :param _outputSize: Output size as a power of two
        :param _outputFormat: Output format of the baked map (e.g. extension)
        :param _outputBakingPath: Output folder path
        :param _bakerName: Name of the baker
        :param _udim: The udim to process
        :type _meshPath: str
        :type _outputSize: int
        :type _outputFormat: str
        :type _outputBakingPath: str
        :type _bakerName: str
        :type _udim: str
        """
        _outputName = '%s_%s' % (_bakerName,_udim)
        batchtools.sbsbaker_curvature(_meshPath,
                                      output_size=[_outputSize,_outputSize],
                                      output_format=_outputFormat,
                                      output_path=_outputBakingPath,
                                      udim=_udim,
                                      output_name=_outputName).wait()


    def cookAndRender(_context, _inputSbs, _inputGraphPath, _outputCookPath, _outputRenderPath, _outputSize, _udim):
        """
        Call sbscooker with the provided udim, and then sbsrender on the resulting .sbsar

        :param _context: API execution context
        :param _inputSbs: Path to the .sbs file to cook
        :param _inputGraphPath: Internal path of the graph to render
        :param _context: Path to the default packages folder
        :param _outputCookPath: Output folder path of the .sbsar
        :param _outputRenderPath: Output folder path of the rendered maps
        :param _outputSize: Output size as a power of two
        :param _udim: The udim to process
        :type _context: :class:`context.Context`
        :type _inputSbs: str
        :type _inputGraphPath: str
        :type _outputCookPath: str
        :type _outputRenderPath: str
        :type _outputSize: int
        :type _udim: str
        """
        _sbsarName = os.path.splitext(os.path.basename(_inputSbs))[0]
        _outputName = '%s_%s' % (_sbsarName,_udim)

        batchtools.sbscooker(inputs=_inputSbs,
                             includes=_context.getDefaultPackagePath(),
                             alias=_context.getUrlAliasMgr().getAllAliases(),
                             udim=_udim,
                             output_path=_outputCookPath,
                             output_name=_outputName,
                             compression_mode=2).wait()

        batchtools.sbsrender_render(inputs=os.path.join(_outputCookPath, _outputName+'.sbsar'),
                                    input_graph=_inputGraphPath,
                                    output_path=_outputRenderPath,
                                    output_name=_outputName,
                                    set_value='$outputsize@%s,%s' % (_outputSize,_outputSize),
                                    png_format_compression="best_speed").wait()


    if any([not i for i in [aTemplateSbsPath, aDestSbsPath, aMeshPath, aUdimList, aOutputSize, aOutputBakingPath, aOutputRenderPath]]):
        log.error("Please provide all the appropriate arguments for demoUdimPipeline ")
        return False

    try:
        # Get information from the mesh: materials and uvset count
        materials, _, uvsetCount = batchtools.sbsbaker_info_get_mesh_info(aMeshPath)

        # Bake mesh information
        log.info('Baking into %s ...' % aOutputBakingPath)

        python_helpers.createFolderIfNotExists(aOutputBakingPath)
        bakerName = sbsbakers.getBakerDefaultIdentifier(sbsbakers.BakerEnum.CURVATURE)
        bitmapExt = 'png'
        aOutputSize = int(aOutputSize)
        for udim in aUdimList.split(','):
            bakeUdim(aMeshPath, aOutputSize, bitmapExt, aOutputBakingPath, bakerName, udim)

        # Parse the .sbs file and get required data
        sbsDoc = substance.SBSDocument(aContext, aTemplateSbsPath)
        sbsDoc.parseDoc()
        graph = sbsDoc.getSBSGraphList()[0]
        graphPath = sbsDoc.getObjectInternalPath(graph.mUID, addDependencyUID=True)
        bitmapRes = sbsDoc.getSBSResourceList()[0]

        # Init a scene resource with the mesh information
        sceneRes = sbsDoc.createSceneResource(aResourcePath=aMeshPath, aIdentifier='mesh', isUDIM=True)

        # Proper configuration for the .sbs output so that it is correctly set for SD. This is not required if using only the batchtools:
        # - Set the material entries
        sceneRes.setMaterialMapEntries(aMaterialsList = materials, nbUVSet=uvsetCount)
        for matMapEntry in sceneRes.getMaterialMapEntries():
            for uvset in range(uvsetCount):
                matMapEntry.assignDefaultSBSGraph(aGraphPath=graphPath, aUVSet=uvset)

        # - Define the bitmap resource as the result of the mesh baking process
        bitmapRes.setResourceIsBakingOutput(sceneRes, sbsbakers.BakerEnum.CURVATURE_MAP_FROM_MESH)

        # Relocate the resource so that it points to the baking output
        sbsDoc.relocateResource(aResource=bitmapRes,
                                aNewPath=os.path.join(aOutputBakingPath, bakerName+'_$(udim).'+bitmapExt),
                                checkPathExists=False)

        # Write the output Substance specialised for the given mesh
        sbsDoc.writeDoc(aNewFileAbsPath=aDestSbsPath, aUpdateRelativePaths=True)

        # Save the .sbsar in a temporary folder if aOutputSbsarPath is not specified
        if not aOutputSbsarPath:
            destSbsar = aContext.getUrlAliasMgr().buildTmpFolderPath(graph.mIdentifier+'_OutputSbsar')
            os.mkdir(destSbsar)
        else:
            destSbsar = aOutputSbsarPath

        # Create output directories if necessary
        python_helpers.createFolderIfNotExists(destSbsar)
        python_helpers.createFolderIfNotExists(aOutputRenderPath)

        # Cook the substance for each Udim and render each resulting .sbsar
        # Run this on several threads with a task queue
        log.info('Rendering into %s ...' % aOutputRenderPath)
        graphPath = 'pkg://'+graph.mIdentifier
        for udim in aUdimList.split(','):
            cookAndRender(aContext, aDestSbsPath, graphPath, destSbsar, aOutputRenderPath, aOutputSize, udim)

        # Remove temporary folder
        if aOutputSbsarPath is None:
            shutil.rmtree(destSbsar)

        log.info('All renders have been generated')
        return True

    except BaseException as error:
        log.error("!!! [demoUdimPipeline] Failed to process mesh %s " % aMeshPath)
        raise error


# ==============================================================================
if __name__ == "__main__":
    base.CommandLineArgsProcessor(__name__).call()
