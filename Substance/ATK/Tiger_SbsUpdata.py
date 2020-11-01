# 时间：20200930－1011
# 制作：JianpingWang  
# 功能：SBS 批量版本更新（外带属性赋加）
# 参考：script_update_with_sbsupdater.py Substance Automation Toolkit\Python API\Pysbs-2020.1.3\pysbs_demos 

from __future__ import unicode_literals
import logging
log = logging.getLogger(__name__)
import os
import subprocess
import sys



import time 
from pysbs import python_helpers

try:
    import pysbs
except ImportError:
    try:
        pysbsPath = bytes(__file__).decode(sys.getfilesystemencoding())
    except:
        pysbsPath = bytes(__file__, sys.getfilesystemencoding()).decode(sys.getfilesystemencoding())
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.split(pysbsPath)[0], '..')))

from pysbs.api_decorators import doc_source_code
from pysbs.api_exceptions import SBSIncompatibleVersionError
from pysbs import sbsenum
from pysbs import context
from pysbs import substance


@doc_source_code
def scriptUpdatePackagesVersion(aContext, aPreviousVersion, aPreviousUpdaterVersion, aPackagesFolderRootDir, aBatchToolsFolder = None):
    """ 
     允许使用Mutator Batch Tool递归包含在给定文件夹路径中的所有.sbs更新到Substance Designer的当前版本。

     ：param aContext：执行上下文
     ：param aPreviousVersion：以前的版本号。 只有具有此版本的.sbs会更新
     ：param aPreviousUpdaterVersion：先前的更新程序版本号。 仅具有此更新程序版本的.sbs将被更新
     ：param aPackagesFolderRootDir：包含要更新的软件包的根文件夹
     ：param aBatchToolsFolder：包含批处理工具可执行文件的文件夹。 如果未提供，将使用由给定上下文标识的Substance Designer路径。
     ：type aContext：context.Context
     ：type aPreviousVersion：str
     ：type aPreviousUpdaterVersion：str
     ：type aBatchToolsFolder：str，可选
     ：return：成功则为True
    """

    aUpdaterPath = aContext.getBatchToolExePath(aBatchTool=sbsenum.BatchToolsEnum.UPDATER, aBatchToolsFolder=aBatchToolsFolder)
    aPresetPackagePath = aContext.getDefaultPackagePath()
    try:
        aCommand = [aUpdaterPath, '--no-dependency', '--output-path', '{inputPath}', '--output-name', '{inputName}', '--presets-path', aPresetPackagePath]
        log.info(aCommand)

        aRootDir = os.path.normpath(aPackagesFolderRootDir)

        #-------------------------------------
        Atime = time.strftime("%Y-%m-%d", time.localtime()) #当前时间
        Main_JianpingWang = ['PBR Materials/JianpingWang', '', 'JianpingWang', '172099994@qq.com', '', Atime + '\nJianpingWangAutomationToolkit \n172099994@qq.com', '']
        # Category     = 0
        # Author       = 2
        # AuthorURL    = 3
        # Description  = 5
        #-------------------------------------

        for root, subFolders, files in os.walk(aRootDir):
            for aFile in files:
                if aFile.endswith('.sbs'):
                    aPackagePath = os.path.join(root, aFile)
                    aDoc = substance.SBSDocument(aContext=aContext, aFileAbsPath=aPackagePath)
                    log.info('Parse substance '+aPackagePath)
                    try:
                        aDoc.parseDoc()
                    except SBSIncompatibleVersionError:
                        print("-------------------------------------------parseDoc错误")

                    if aDoc.mFormatVersion == aPreviousVersion and aDoc.mUpdaterVersion == aPreviousUpdaterVersion:
                        aMutatorCmd = aCommand + ['--input', aPackagePath]
                        log.info('Update substance '+aPackagePath)
                        subprocess.check_call(aMutatorCmd)

                    #-------------------------------------
                    aDoc.setDescription(Main_JianpingWang[5]) #设置给定的描述
                    setallSBSGraph = aDoc.getSBSGraphList()  #1/3获取.sbs文件中定义的所有图形的列表，当一个SBS内含N个子graph都可以                    
                    b = len(setallSBSGraph) #得到列表长度
                    number = 0
                    number2 = 0
                    while number < b:
                        while number2 < 6:                         
                            setallSBSGraph[number].setAttribute(aAttributeIdentifier = number2, aAttributeValue = Main_JianpingWang[number2])
                            number2 += 1
                        number += 1
                        number2 = 0                                               
                    aDoc.SBSGraph = setallSBSGraph #2/3赋回修改的属性
                    #测试用                    
                    # for a in setallSBSGraph:
                    #     print(a.getAttribute(aAttributeIdentifier = 5)) #测试setAttribute值 
                        #a 就是graph类 所以直接调用其他成员函数      
                    # print(aDoc.getDescription()) #测试setDescription物质描述
                    #列表最后一个是文件夹Document属性，非graph                    
                    aDoc.writeDoc() #3/3重写入 文件夹Document属性                    
                    #-------------------------------------

        log.info('=> All packages have been updated using the Mutator Batch Tool')
        return True

    except BaseException as error:
        log.error("!!! [demoUpdatePackagesVersion] Failed to update a package")
        raise error


if __name__ == "__main__":
    apiAliasPath = os.path.abspath(os.path.join(os.path.split(__file__)[0], '../pysbs_demos/sample'))
    apiContext = context.Context()
    apiContext.getUrlAliasMgr().setAliasAbsPath('api', apiAliasPath)

    here = os.path.split(__file__)[0]
    folders = [os.path.abspath(os.path.join(here, 'L:\Main substance designer project\library_TEST')),
               os.path.abspath(os.path.join(here, '../pysbs_demos'))]
    for f in folders:
        scriptUpdatePackagesVersion(aContext=apiContext,
                                    aPreviousVersion="1.1.0.201806",
                                    aPreviousUpdaterVersion="1.1.0.201806",
                                    aPackagesFolderRootDir = f)


