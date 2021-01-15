# # 作者：王健平
# # 时间：20210103 － 0110
# # 功能：1、合并贴图；2、批量另存格式

from tkinter import *
from tkinter import ttk
from tkinter import filedialog  #获取文件夹
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
import os
from tkinter import ttk, Tk
from tkinter import N, W, E, S
from tkinter import StringVar
import tkinter as tk
from PIL import ImageTk
import webbrowser

from tigerFunction import *

# class App(ttk.Frame):
#     def __init__(self, master=None):
#         super().__init__(master)
#         self.master = master

#         self.datapathshow = StringVar() #注意声明变量时的  前后位置
#         self.savedatapathshow = StringVar()
#         self.savedatapathshowA = StringVar() #1 变量声明         
#         self.datapath = 'StringVar()' #指定类型
#         self.data_path()
#         self.save_datapath = 'StringVar()' 
#         self.save_data_path()
#         self.turnformat()
#         self.run()   
#         self._layout()


#     def data_path(self):
#         self.ui_datapath = ttk.Button(self)
#         self.ui_datapath["text"] = "获取资源目录"
#         self.ui_datapath["command"] = self.get_data_path
#         self.ui_datapath_labe = ttk.Label(textvariable=self.datapathshow)

#     def save_data_path(self):
#         self.ui_save_data_path = ttk.Button(self)
#         self.ui_save_data_path["text"] = "存放目录"
#         self.ui_save_data_path["command"] = self.get_save_datapath
#         self.ui_save_data_path_labe = ttk.Label(textvariable=self.savedatapathshow)   

#     def run(self):
#         self.ui_run = ttk.Button(self)
#         self.ui_run["text"] = "开始执行合并"
#         self.ui_run["command"] = self.get_run

#     def get_run(self):
#         """启动获取动作"""
#         print ("-------------程序开始运行-------------")
#         list = get_filelist(self.datapath, []) #遍历文件夹，得到文件
#         print('---------------list')
#         print(list)
#         print('文件夹内包含贴图总数量：' + str(len(list))) #得到文件数量
#         newimg = Image.new('RGB',(512,512),(128,128,128)) #建立一个新图片
#         a = 0
#         for e in list:
#             print(e)
#             img = Image.open(e) #读取图像
#             if a == 0:
#                 newimg.paste(img, (0,0))    #转填充图像，以512大小为例，00为左上，256，256为中心
#             elif a == 1:
#                 newimg.paste(img, (0,256))
#             elif a == 2:
#                 newimg.paste(img, (256,0))
#             else :
#                 newimg.paste(img, (256,256))
#             a += 1
#         #新建图像，用与合并
#         texture_name = 'T2.png'
#         texture_mode = 'png'
#         newimg.save(self.save_datapath + '/' + texture_name, texture_mode) #Folderpath为路径， ‘/’文件夹目录去除，不然会添加上文件夹名称在图片名上， 'jpeg'为格式  
#         self.savedatapathshowA.set(texture_name)    # 2 StringVar 转换到 str格式
#         self.print_label = ttk.Label(textvariable=self.savedatapathshowA) #3 调取变量
#         self.print_label.grid(row=3, column=1, sticky=(N)) # 4 显示标签

#         print("图像已合并为：" + texture_name + " 格式为：" + texture_mode)
#         print("-------------图像合并完成-------------")

#     def turnformat(self):
#         self.ui_turnformat = ttk.Button(self)
#         self.ui_turnformat["text"] = "批量转格式"
#         self.ui_turnformat["command"] = self.get_turnformat
        
#     def get_turnformat(self):
#         """批量转图片格式"""
#         print ("-------------程序开始运行-------------")
#         list = get_filelist(self.datapath, []) #遍历文件夹，得到文件
#         for e in list:
#             print(e)
#             img = Image.open(e)
#             saveformat = '.png'
#             outfile = os.path.splitext(e)[0] + saveformat
#             #JPEG
#             if img.format == 'TGA':
#                 if e != outfile:                
#                     try:
#                         Image.open(e).save(outfile)
#                     except IOError:
#                         print ("cannot convert", e)            
#         print("-------------图像转换完成-------------")


#     def _layout(self):
#         self.master.title("TimeMachine") # 标题
#         self.master.geometry('1024x512+50+50') # 尺寸
#         self.grid()

#         self.ui_datapath.grid(row=0) 
#         self.ui_datapath_labe.grid(row=0, column=1)
#         self.ui_save_data_path.grid(row=1)
#         self.ui_save_data_path_labe.grid(row=1, column=1)
#         self.ui_run.grid(row=2)
#         self.ui_turnformat.grid(row=3)


#     def get_data_path(self):
#         self.datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
#         list = get_filelist(self.datapath, [])
#         print('文件夹内贴图总数：' + str(len(list))) #得到文件数量
#         print('---------------list-------------->')
#         print(list)
#         print('---------------list------------END')
#         responses = {} #创建字典
#         a = 0
#         for e in list:            
#             end = e.split("_")[3]  #文件名分割判断  而不是整个目录
#             end2 = end.split(".")[0] #文件名再次分割判断 
#             if end2 == 'Normal':
#                 name = 'Normal' #类型：字符串   字典中的key          
#                 responses.setdefault(name,[]).append(e)  #类型：数据内存 字典中的多值
#                 # https://www.cnblogs.com/rrttp/p/8493264.html
#             elif end2 == 'Emiss':
#                 name1 = 'Emiss'            
#                 responses.setdefault(name1,[]).append(e)
#             elif end2 == 'Mask':
#                 name2 = 'Mask'                
#                 responses.setdefault(name2,[]).append(e)
#             else:
#                 name3 = 'Albedo' 
#                 responses.setdefault(name3,[]).append(e)
#             a += 1
#         # print("---------------文件合并开始---------------")
#         # a512 = 0
#         # a1024 = 0        
#         # cc2 = 0
#         # newimg1 = Image.new('RGB',(1024,1024),(128,128,128)) #建立一个新图片
#         # newimg2 = Image.new('RGB',(2048,2048),(128,128,128)) #建立一个新图片
#         # for name, valueAll in responses.items():    #循环打印
#         #     cc = 0
#         #     for value in valueAll:
#         #         img = Image.open(value) #读取图像
#         #         w, h = img.size
#         #         texture_mode = 'png'
#         #         if w == 512:
#         #             if a512%4 == 1:
#         #                 print('----------------512----------------')
#         #                 print('----------------' + str(a512) + '----------------')
#         #                 # if cc == 0:
#         #                 #     newimg1.paste(img, (0,0))    #转填充图像，以512大小为例，00为左上，256，256为中心
#         #                 #     cc += 1
#         #                 # elif cc == 1:
#         #                 #     newimg1.paste(img, (0,512))
#         #                 #     cc += 1
#         #                 # elif cc == 2:
#         #                 #     newimg1.paste(img, (512,0))
#         #                 # else :
#         #                 #     newimg1.paste(img, (512,512))
#         #                 # texture_name = '_' + str(a512) + '.png'
#         #                 # newimg1.save(self.save_datapath + '/' + '512_' + texture_name, texture_mode)
#         #             a512 += 1                    
#         #         elif w == 1024:
#         #             if a1024%4 == 1:
#         #                 print('----------------1024----------------')
#         #                 print('----------------' + str(a1024) + '----------------')
#         #                 # if cc2 == 0:
#         #                 #     newimg2.paste(img, (1024,1024))    #转填充图像，以512大小为例，00为左上，256，256为中心
#         #                 # elif cc2 == 1:
#         #                 #     newimg2.paste(img, (0,0))
#         #                 # elif cc2 == 2:
#         #                 #     newimg2.paste(img, (0,1024))
#         #                 # else:
#         #                 #     newimg2.paste(img, (1024,0))
#         #                 # texture_name2 = '_' + str(a1024) + 'T2.png'
#         #                 # newimg2.save(self.save_datapath + '/' + '1024_' + texture_name2, texture_mode)
#         #             a1024 += 1
#         #         else:
#         #             print('----------------------------------------分辩率大小错误')                
                
#         #         cc2 += 1
#         # print("---------------文件合并结束---------------")
#         self.datapathshow.set(self.datapath)  #把目录显示出来

#     def get_save_datapath(self):
#         self.save_datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
#         self.savedatapathshow.set(self.save_datapath)





root = Tk()
root.title("TimeMachine批量图片处理－202101版")
root.geometry('1024x512+50+50') # 尺寸

tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='批量转换格式')
tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text='批量合并贴图')
tab3 = ttk.Frame(tabControl)
tabControl.add(tab3, text='批量重新命名')
tab4 = ttk.Frame(tabControl)
tabControl.add(tab4, text='声明及帮助')
tabControl.pack(expand=1, fill="both")

#---------------Tab控件------------------#
Tab1 = mainTab1(tab1)
Tab2 = mainTab2(tab2)
Tab3 = mainTab3(tab3)

def openweb():
    webbrowser.open("https://github.com/MasterWangdaoyong")
ttk.Label(tab4, text="--声明--").grid(column=0, row=0, pady=10, sticky='W')
ttk.Label(tab4, text="时间：2021年01月15").grid(column=0, row=1, sticky='W')
ttk.Label(tab4, text="版本：202101").grid(column=0, row=2, sticky='W')
action = ttk.Button(tab4,text="TimeMachine:",width=15, command=openweb)
action.grid(column=0,row=3,sticky='W')
ttk.Label(tab4, text="https://github.com/MasterWangdaoyong").grid(column=1, row=3, sticky='W')
#---------------Tab4控件------------------#

root.mainloop()