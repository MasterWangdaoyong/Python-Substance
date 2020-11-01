# 20201010 自定义笔记

# ################################################################################################
# # https://docs.substance3d.com/sat/pysbs-python-api/overview/basic-manipulation
# #从现有的.sbs文件创建SBSDocument对象，解析并写入
# sbsDoc = substance.SBSDocument(aContext, aSBSFileAbsPath)
# sbsDoc.parseDoc()          # 解析.sbs文件并将其包含在sbsDoc中的对象结构实质
# sbsDoc.writeDoc()          # 将对象结构写回到磁盘上的同一.sbs文件中

# # sbs和sbsar软件包均提供以下功能：
# # 获取包的所有图
# aGraphList = aDoc.getSBSGraphList（）

# #获取图的输出
# aOutputList = aGraph.getGraphOutputs（）#获取图的所有输出
# aOutput = aGraph.getGraphOutput（aOutputIdentifier ='MyOutput'）#获取特定的输出
# aOutput = aGraph.getGraphOutputWithUsage（aUsage = sbsenum.UsageEnum.ROUGHNESS）#根据给定的用法获取特定的输出
# aOutput = aGraph.getGraphOutputWithUsage（aUsage ='MyCustomUsage'）#相同，但具有自定义用法

# #获取输入图
# aInputList = aGraph.getAllInputs（）#获取所有输入（图像和参数）
# aInputList = aGraph.getAllInputsInGroup（aGroup ='MyGroup'）#获取名为'MyGroup'的特定GUI组的所有输入
# aParamList = aGraph.getInputParameters（）#仅获取输入参数
# aImageList = aGraph.getInputImages（）#仅获取输入图像

# #或获得特定的输入：
# aInput = aGraph.getInput（aInputIdentifier ='MyInput'）
# aParam = aGraph.getInputParameter（aInputParamIdentifier ='MyInputParam'）
# aImage = aGraph.getInputImage（aInputImageIdentifier ='MyInputImage'）
# aImage = aGraph.getInputImageWithUsage （aUsage = sbsenum.UsageEnum.ROUGHNESS）

# #获取参数定义：
# aParam.getWidget（）
# aParam.getDefaultValues（）
# aParam。getMinValue（）
# aParam.getMaxValue（）
# aParam.getClamp（）
# aParam.getStep（）
# aParam.getLabels（）
# aParam.getDropDownList（）

# #获取图形，输入或输出的
# 属性aGraph.getAttribute（aAttributeIdentifier = sbsenum.AttributeEnum.Author）
# aInput.getAttribute（aAttributeIdentifier = sbsenum.AttributeEnum.Description）
# aOutput.getAttribute（aAttributeIdentifier = sbsenum.AttributeEnum.Label）

# #获取在图形上定义的参数预设
# aPresetList = aGraph.getAllPresets（）#获取在图形上定义的所有预设
# aPreset = aGraph.getPreset（aPresetLabel ='MyPresetLabel'）#从标签中获取一个特定的预设
# aPresetInputList = aPreset.getPresetInputs（）#获取预设的所有预设输入
# aPresetInput = aPreset.getPresetInput（aInputParam = aParam）#获取与图形参数关联的预设输入
# aPresetInput = aPreset.getPresetInputSetFromIdentifier（aInputParamIdentifier ='MyInputParam'）#获取与图形参数标识符关联的预设输入

# 在图表（SBSGraph）上，例如可以进行以下修改：
# https://docs.substance3d.com/sat/pysbs-python-api/overview/substances-modification
# #使用RGBA颜色小部件创建一个名为'InputColor'的新输入参数。
# aParam = aSubGraph.addInputParameter（aIdentifier ='InputColor'，
#                                      aWidget = sbsenum.WidgetEnum.COLOR_FLOAT4，
#                                      aDefaultValue = [1,1,1,1]，
#                                      aLabel ='输入颜色'）

# #修改基本参数：设置实例的输出大小
# aGraph.setBaseParameterValue（aParameter = sbsenum.CompNodeParamEnum.OUTPUT_SIZE，
#                              aParamValue = [sbsenum.OutputSizeEnum.SIZE_1024，sbsenum.OutputSizeEnum.SIZE_1024]，
#                              aRelativeTo = sbsenum.ParamInheritanceEnum.ABSOLUTE）

# #设置属性和图标
# aGraph.setAttribute（aAttributeIdentifier = sbsenum.AttributesEnum.Author，aAttributeValue ='Substance Designer API'）
# aGraph.setIcon（aIconAbsPath = myIconPath））

# #创建参数预设
# aPreset = aGraph.createPreset（aLabel ='DefaultPreset'，setCurrentDefaultValues = True）
# aPreset.setPresetInput（aInputParam = aParam，aPresetValue = [0.1，0.2，0.3，1]）

# #连接/断开两个节点（可以指定输入和输出，取决于可能的歧义）
# aGraph.connectNodes（aLeftNode = aFirstNode，aRightNode = aSecondNode）
# aGraph.connectNodes（aLeftNode = aFirstNode，aRightNode = aSecondNode，aLeftNodeOutput ='myOutput'，aRightNodeInput = sbsenum.InputEnum.OPACITY）
# aGraph.disconnectNodes（aLeftNode = aFirstNode，aRightNode = aSecondNode）

# #将一个引脚输入/输出上的连接移至另一个引脚输入/输出
# aGraph.moveConnectionsOnPinOutput（aInitialNode = rgbaSplitNode，aInitialNodeOutput ='R'，
#                                   aTargetNode = rgbaSplitNode，aTargetNodeOutput ='G'）
# aGraph.moveConnectionOnPinInput（aInitialNode = blendNode，aInitialNodeInput = sbsenum.InputEnum.DESTINATION，
#                                 aTargetNode = embossNode，aTargetNodeInput = sbsenum.InputEnum.INPUT_GRADIENT）



# https://docs.substance3d.com/sat/pysbs-python-api/api-content/libraries/sbsenum#sbsenum.AttributesEnum

# class sbsenum.AttributesEnum
# Enumeration of the different attributes available on a SBSGraph or a SBSFunction

# Category     = 0
# Label        = 1
# Author       = 2
# AuthorURL    = 3
# Tags         = 4
# Description  = 5
# UserTags     = 6
# Icon         = 7
# HideInLibrary= 8
# PhysicalSize = 9

# ################################################################################################