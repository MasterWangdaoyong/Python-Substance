# 时间：20200930－1009
# 制作：JianpingWang  
# 功能：SBS生成
# 参考: https://docs.substance3d.com/sat/pysbs-python-api/overview/substance-creation

import sys
import os
from pysbs import substance
from pysbs import batchtools
import os.path
import pathlib
import shutil
import platform
import math
import time 

from pysbs import context, sbsenum, sbsgenerator

myContext = context.Context()

# 使用名为“ DemoGraph”的图创建一个新的物质
sbsDoc = sbsgenerator.createSBSDocument(aContext = myContext,
                    aFileAbsPath = 'D:/soft/Substance Automation Toolkit/resources/templates/Path.sbs/',  #注意这里的斜杠
                    aGraphIdentifier = 'DemoGraph')

# 在此物质中创建另一个带有某些参数的图形
secondGraph = sbsDoc.createGraph(aGraphIdentifier = 'SecondGraph')

#设置图形属性和图标 
time = time.strftime("%Y-%m-%d", time.localtime()) #当前时间
Main_JianpingWang = ['PBR Materials/JianpingWang', '', 'JianpingWang', '172099994@qq.com', '', time + '\nJianpingWang \n172099994@qq.com', '']
number = 0
while  number < 6:
    secondGraph.setAttribute(aAttributeIdentifier = number, aAttributeValue = Main_JianpingWang[number])
    number += 1

# # 创建一个函数并将其放在新文件夹“ Functions”下
# myFunction = sbsDoc.createFunction(aFunctionIdentifier = 'myFct', aParentFolder = 'Functions')


# # 资源创建
# myRes = sbsDoc.createLinkedResource(aResourcePath = 'D:/soft/Substance Automation Toolkit/resources/templates/Path.sbs/HSL.png',
#                     aResourceTypeEnum = sbsenum.ResourceTypeEnum.BITMAP)

# # 图形版
# # ###############
# xOffset = [192,0,0]

# # 获取使用文档创建的图形
# demoGraph = sbsDoc.getSBSGraph(aGraphIdentifier = 'DemoGraph')

# # -使用先前创建的资源的位图节点
# # （如果给出了绝对路径，此方法也可以创建资源）
# bitmapNode = demoGraph.createBitmapNode(aSBSDocument = sbsDoc,
#                     aResourcePath = myRes.getPkgResourcePath(),
#                     aParameters   = {sbsenum.CompNodeParamEnum.COLOR_MODE:sbsenum.ColorModeEnum.COLOR})

# # - -默认软件包库中的Blur HQ实例
# blurHQNode = demoGraph.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc,
#                     aPath       = 'sbs://blur_hq.sbs/blur_hq',
#                     aGUIPos     = bitmapNode.getOffsetPosition(xOffset),
#                     aParameters = {'Intensity':3.2})

# # - 使用baseColor的输出节点
# outputNode = demoGraph.createOutputNode(aIdentifier = 'DemoOutput',
#                     aGUIPos       = blurHQNode.getOffsetPosition(xOffset),
#                     aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,
#                     aUsages       = {sbsenum.UsageEnum.BASECOLOR: sbsenum.ComponentsEnum.RGBA})

# aGraph.connectNodes(aLeftNode = bitmapNode, aRightNode = blurHQNode)
# aGraph.connectNodes(aLeftNode = blurHQNode, aRightNode = outputNode)

# 写文件
sbsDoc.writeDoc()