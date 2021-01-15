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

def get_filelist(dir, Filelist):
    """遍历文件夹内的文件"""
    newDir = dir
    if os.path.isfile(dir): 
        Filelist.append(dir) 
    elif os.path.isdir(dir): 
        for s in os.listdir(dir): 
            newDir=os.path.join(dir, s) 
            get_filelist(newDir, Filelist) 
    return Filelist

def resize(image):
    size = 128
    return image.resize((size, size))  

class mainTab1(ttk.Frame):
    """批量转换格式"""
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master

        self.datapath = 'StringVar()' #指定类型
        self.datapathshow = StringVar() #注意声明变量时的  前后位置

        self.save_datapath = 'StringVar()'
        self.save_datapathshow = StringVar()










        self.grid() #必不可少 面板类别定义 循环
        self.UIupdate()       

    def UIupdate(self):
        self.action = ttk.Button(self,text="资源目录",width=10) 
        self.action["command"] = self.get_data_path  
        self.action.grid(column=0,row=0, pady=10)
        ttk.Label(self, textvariable=self.datapathshow).grid(column=1, row=0,sticky='W')

        ttk.Label(self, text="--格式选择-->").grid(column=0, row=1,sticky='W')

        self.book = tk.StringVar()
        self.bookChosen = ttk.Combobox(self, width=12, textvariable=self.book)
        self.bookChosen['values'] = ('JPEG', 'TGA','PNG')
        self.bookChosen.grid(column=3, row=1)
        self.bookChosen.current(0)  #设置初始显示值，值为元组['values']的下标
        self.bookChosen.config(state='readonly')  #设为只读模式

        ttk.Label(self, text="--转到-->").grid(column=4, row=1,sticky='W')

        self.book2 = tk.StringVar()
        self.bookChosen2 = ttk.Combobox(self, width=12, textvariable=self.book2)
        self.bookChosen2['values'] = ('JPEG', 'TGA','PNG')
        self.bookChosen2.grid(column=5, row=1)
        self.bookChosen2.current(0)  #设置初始显示值，值为元组['values']的下标
        self.bookChosen2.config(state='readonly')  #设为只读模式

        self.action = ttk.Button(self,text="输出目录",width=10)
        self.action["command"] = self.save_data_path
        self.action.grid(column=0,row=3)
        ttk.Label(self, textvariable=self.save_datapathshow).grid(column=1, row=3,sticky='W')

        self.action = ttk.Button(self,text="确认转换",width=10)  
        self.action["command"] = self.get_turnformat 
        self.action.grid(column=0,row=4)        

    def get_turnformat(self):
        """批量转图片格式"""
        print ("-------------程序开始运行-------------")
        list = get_filelist(self.datapath, []) #遍历文件夹，得到文件
        for e in list:
            print(e)
            img = Image.open(e)
            saveformat = '.png'
            outfile = os.path.splitext(e)[0] + saveformat
            #JPEG
            if img.format == 'TGA':
                if e != outfile:                
                    try:
                        Image.open(e).save(outfile)
                    except IOError:
                        print ("cannot convert", e)            
        print("-------------图像转换完成-------------")     

    def get_data_path(self):
        self.datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
        self.datapathshow.set(self.datapath)  #把目录显示出来

    def save_data_path(self):
        self.save_datapath = filedialog.askdirectory() 
        self.save_datapathshow.set(self.save_datapath)  

 



# class App(ttk.Frame):
#     def __init__(self, master=None):
#         tk.Frame.__init__(self, master)
#         self.master = master

#         self.datapathshow = StringVar() #注意声明变量时的  前后位置
#         self.datapath = 'StringVar()' #指定类型
#         self.data_path()
#         self._GUI()

#     def data_path(self):
#         self.ui_datapath = ttk.Button(self)
#         self.ui_datapath["text"] = "获取资源目录"
#         self.ui_datapath["command"] = self.get_data_path
#         self.ui_datapath_labe = ttk.Label(textvariable=self.datapathshow)

#     def get_data_path(self):
#         self.datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
#         self.datapathshow.set(self.datapath)  #把目录显示出来        

#     def _GUI(self):
#         self.ui_datapath.grid(row=0) 
#         self.ui_datapath_labe.grid(row=0, column=1)





# from tkinter import *
# from tkinter import ttk
# from tkinter import filedialog  #获取文件夹
# from PIL import Image
# from PIL import ImageFilter
# from PIL import ImageEnhance
# import os
# from tkinter import ttk, Tk
# from tkinter import N, W, E, S
# from tkinter import StringVar
# import tkinter as tk
# from PIL import ImageTk
# import webbrowser
# from tigerPublic import *

# class App(ttk.Frame):
#     def __init__(self, master=None):
#         tk.Frame.__init__(self, master)
#         self.master = master

#         self.datapathshow = StringVar() #注意声明变量时的  前后位置
#         self.savedatapathshow = StringVar()      
#         self.datapath = 'StringVar()' #指定类型
#         self.data_path()
#         self.save_datapath = 'StringVar()' 
#         self.save_data_path()
#         self.turnformat()
#         self._GUI()


#     def data_path(self):
#         self.ui_datapath = ttk.Button(self)
#         self.ui_datapath["text"] = "获取资源目录"
#         self.ui_datapath["command"] = self.get_data_path
#         self.ui_datapath_labe = ttk.Label(textvariable=self.datapathshow)

#     def get_data_path(self):
#         self.datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
#         self.datapathshow.set(self.datapath)  #把目录显示出来        

#     def save_data_path(self):
#         self.ui_save_data_path = ttk.Button(self)
#         self.ui_save_data_path["text"] = "存放目录"
#         self.ui_save_data_path["command"] = self.get_save_datapath
#         self.ui_save_data_path_labe = ttk.Label(textvariable=self.savedatapathshow)   

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
#         self.datapathshow.set(self.datapath)


#     def _GUI(self):
#         # self.master.title("TimeMachine") # 标题
#         # self.master.geometry('1024x512+50+50') # 尺寸
#         # self.grid()

#         self.ui_datapath.grid(row=0) 
#         self.ui_datapath_labe.grid(row=0, column=1)
#         self.ui_save_data_path.grid(row=1)
#         self.ui_save_data_path_labe.grid(row=1, column=1)
#         self.ui_turnformat.grid(row=3)    

#     def get_save_datapath(self):
#         self.save_datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
#         self.savedatapathshow.set(self.save_datapath)    

# # root = Tk()        
# # app = App(root)
# # app.mainloop()

class mainTab2(ttk.Frame):
    """批量合并贴图"""
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master

        self.grid() #必不可少 面板类别定义 循环
        self.UIupdate()       

    def UIupdate(self):
        self.action = ttk.Button(self,text="资源目录",width=10)   
        self.action.grid(column=0,row=0, pady=10)

        ttk.Label(self, text="--合并选择-->").grid(column=0, row=1,sticky='W')

        self.book3 = tk.StringVar()
        self.bookChosen = ttk.Combobox(self, width=12, textvariable=self.book3)
        self.bookChosen['values'] = ('PBR分类别4合1', '普通4合1')
        self.bookChosen.grid(column=1, row=1)
        self.bookChosen.current(0)  #设置初始显示值，值为元组['values']的下标
        self.bookChosen.config(state='readonly')  #设为只读模式

        self.action = ttk.Button(self,text="输出目录",width=10)   
        self.action.grid(column=0,row=4)

        self.action = ttk.Button(self,text="确认合并",width=10)   
        self.action.grid(column=0,row=5)









class mainTab3(ttk.Frame):
    """批量重新命名"""
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master

        self.grid() #必不可少 面板类别定义 循环
        self.UIupdate()       

    def UIupdate(self):
        self.action = ttk.Button(self,text="资源目录",width=10)   
        self.action.grid(column=0,row=0, pady=10)

        ttk.Label(self, text="--命名规则-->").grid(column=0, row=1,sticky='W')
        self.name = tk.StringVar()
        self.nameEntered = ttk.Entry(self, width=12, textvariable=self.name)
        self.nameEntered.grid(column=1, row=1, sticky='W')
        ttk.Label(self, text="-").grid(column=2, row=1,sticky='W')
        self.name2 = tk.StringVar()
        self.nameEntered = ttk.Entry(self, width=12, textvariable=self.name2)
        self.nameEntered.grid(column=3, row=1, sticky='W')
        ttk.Label(self, text="-").grid(column=4, row=1,sticky='W')
        self.name3 = tk.StringVar()
        self.nameEntered = ttk.Entry(self, width=12, textvariable=self.name3)
        self.nameEntered.grid(column=5, row=1, sticky='W')

        ttk.Label(self, text="--输出格式-->").grid(column=0, row=2,sticky='W')
        self.book4 = tk.StringVar()
        self.bookChosen2 = ttk.Combobox(self, width=9, textvariable=self.book4)
        self.bookChosen2['values'] = ('JPEG', 'TGA','PNG')
        self.bookChosen2.grid(column=1, row=2)
        self.bookChosen2.current(0)  #设置初始显示值，值为元组['values']的下标
        self.bookChosen2.config(state='readonly')  #设为只读模式

        self.action = ttk.Button(self,text="输出目录",width=10)   
        self.action.grid(column=0,row=3)

        self.action = ttk.Button(self,text="确认重命名",width=10)   
        self.action.grid(column=0,row=4)