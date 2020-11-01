# 时间：20201011－1011
# 制作：JianpingWang  
# 功能：SBS 批量生成 SBSAR
# 参考：demos_batchtools.py Substance Automation Toolkit\Python API\Pysbs-2020.1.3\pysbs_demos 

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


from pysbs.api_exceptions import SBSIncompatibleVersionError
from pysbs import sbsenum
from pysbs import context



@doc_source_code
def demoUdimPipeline(aContext, aPackagesFolderRootDir, aOutputSbsarPath=None):
    """
    aContext（context.Context）–执行上下文
    aPackagesFolderRootDir：包含要更新的软件包的根文件夹
    aOutputSbsarPath（str ，可选）–保存每个udim专用的输出.sbsar的文件夹路径。如果不需要保留.sbsar，则将该值保留为None。
    """
    _context = aContext
    _inputSbs = aPackagesFolderRootDir
    _outputCookPath = aOutputSbsarPath

    def cookAndRender(_context, _inputSbs, _outputCookPath):
        """
        使用提供的udim调用sbscooker，然后在生成的.sbsar上sbsrender

        ：param _context：API执行上下文
        ：param _inputSbs：要烹饪的.sbs文件的路径
        ：param _outputCookPath：.sbsar的输出文件夹路径
        :type _context: :class:`context.Context`
        :type _inputSbs: str
        :type _outputCookPath: str
        """
        _sbsarName = os.path.splitext(os.path.basename(_inputSbs))[0]
        _outputName = '%s_%s' % (_sbsarName)

        batchtools.sbscooker(inputs=_inputSbs,
                             includes=_context.getDefaultPackagePath(),
                             output_path=_outputCookPath,
                             output_name=_outputName,
                             compression_mode=2).wait()

        # batchtools.sbsrender_render(inputs=os.path.join(_outputCookPath, _outputName+'.sbsar'),
        #                             input_graph=_inputGraphPath,
        #                             output_path=_outputRenderPath,
        #                             output_name=_outputName,
        #                             set_value='$outputsize@%s,%s' % (_outputSize,_outputSize),
        #                             png_format_compression="best_speed").wait()

    try:
        python_helpers.createFolderIfNotExists(aPackagesFolderRootDir) 

        # 解析.sbs文件并获取所需的数据
        aRootDir = os.path.normpath(aPackagesFolderRootDir)
        for root, subFolders, files in os.walk(aRootDir):
            for aFile in files:
                if aFile.endswith('.sbs'):   
                    aPackagePath = os.path.join(root, aFile)     
                    sbsDoc = substance.SBSDocument(aContext=aContext, aFileAbsPath=aPackagePath)
                    try:
                        sbsDoc.parseDoc()
                    except SBSIncompatibleVersionError:
                        print("-------------------------------------------parseDoc错误")
                    graph = sbsDoc.getSBSGraphList()
                    print(sbsDoc)
                    print(graph)

        # destSbsar = aOutputSbsarPath

        # # 必要时创建输出目录
        # python_helpers.createFolderIfNotExists(destSbsar)
        # python_helpers.createFolderIfNotExists(aPackagesFolderRootDir)
        
        # # 多个线程上运行
        # log.info('Rendering into %s ...' % aPackagesFolderRootDir)    
        # cookAndRender(aContext, graph, aPackagesFolderRootDir)

        # return True

    except BaseException as error:
        log.error("-------------------------------------------错误")
        raise error

if __name__ == "__main__":    
    apiContext = context.Context()
    folder = os.path.abspath(os.path.join( 'L:\Main substance designer project\library_TEST'))
    demoUdimPipeline(aContext = apiContext,
                    aPackagesFolderRootDir = folder,
                    aOutputSbsarPath = folder)





