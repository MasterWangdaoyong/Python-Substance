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

# // https://www.jianshu.com/p/54cdeb2e52da  #注意 这个set 功能 self.var.set("看这里！")
# https://www.jianshu.com/p/c1be837ca646

def get_filelist(dir, Filelist):     
    """遍历文件夹内的文件"""
    newDir = dir
    if os.path.isfile(dir): 
        Filelist.append(dir) 
        # # 若只是要返回文件文，使用这个 
        # Filelist.append(os.path.basename(dir)) 
    elif os.path.isdir(dir): 
        for s in os.listdir(dir): 
            # 如果需要忽略某些文件夹，使用以下代码 
            #if s == "xxx": 
                #continue 
            newDir=os.path.join(dir, s) 
            get_filelist(newDir, Filelist) 
    return Filelist  

class App(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.datapathshow = StringVar() #注意声明变量时的  前后位置
        self.savedatapathshow = StringVar()
        self.savedatapathshowA = StringVar() #1 变量声明         
        self.datapath = 'StringVar()' #指定类型
        self.data_path()
        self.save_datapath = 'StringVar()' 
        self.save_data_path()

        self.imageshow()

        self.run()   
        self._layout()

    def data_path(self):
        self.hi_there = ttk.Button(self)
        self.hi_there["text"] = "获取资源目录"
        self.hi_there["command"] = self.get_data_path
        self.print_label = ttk.Label(textvariable=self.datapathshow)

    def save_data_path(self):
        self.hi_there2 = ttk.Button(self)
        self.hi_there2["text"] = "存放目录"
        self.hi_there2["command"] = self.get_save_datapath
        self.print_labe2 = ttk.Label(textvariable=self.savedatapathshow)   

    def run(self):
        self.hi_there3 = ttk.Button(self)
        self.hi_there3["text"] = "开始执行合并"
        self.hi_there3["command"] = self.get_run

    def imageshow(self):
        self.hi_there4 = PhotoImage(r'F:\Main_Project\Python-Substance\Python\PyGame\images\alien.bmp')
        self.label=Label(image=self.hi_there4)
        self.label.image=self.hi_there4

    def get_run(self):
        """启动获取动作"""
        print ("-------------程序开始运行-------------")
        list = get_filelist(self.datapath, []) #遍历文件夹，得到文件
        print('文件夹内包含贴图总数量：' + str(len(list))) #得到文件数量
        newimg = Image.new('RGB',(512,512),(128,128,128)) #建立一个新图片
        a = 0
        for e in list:
            print(e)
            img = Image.open(e) #读取图像
            if a == 0:
                newimg.paste(img, (0,0))    #转填充图像，以512大小为例，00为左上，256，256为中心
            elif a == 1:
                newimg.paste(img, (0,256))
            elif a == 2:
                newimg.paste(img, (256,0))
            else :
                newimg.paste(img, (256,256))
            a += 1
        #新建图像，用与合并
        texture_name = 'T2.png'
        texture_mode = 'png'
        newimg.save(self.save_datapath + '/' + texture_name, texture_mode) #Folderpath为路径， ‘/’文件夹目录去除，不然会添加上文件夹名称在图片名上， 'jpeg'为格式  
        self.savedatapathshowA.set(texture_name)    # 2 StringVar 转换到 str格式
        self.print_label = ttk.Label(textvariable=self.savedatapathshowA) #3 调取变量
        self.print_label.grid(row=3, column=1, sticky=(N)) # 4 显示标签

        print("图像已合并为：" + texture_name + " 格式为：" + texture_mode)
        print("-------------图像合并完成-------------")



    def _layout(self):
        self.master.title("简单的 GUI") # 标题
        self.master.geometry('1024x512+50+50') # 尺寸
        self.grid()
        
        self.hi_there.grid(row=0) 
        self.print_label.grid(row=0, column=1)
        self.hi_there2.grid(row=1)
        self.print_labe2.grid(row=1, column=1)
        self.hi_there3.grid(row=2)

        self.label.grid(row=3,column=3)
        # self.hi_there2.grid(row=1, column=0, sticky=(N, W, E, S))
        # self.print_labe2.grid(row=1, column=1, sticky=(E))


    def get_data_path(self):
        self.datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)

        canvas=tk.Canvas(self.master ,height=400,width=400)
        canvas.grid(row=4,column=4)

        list = get_filelist(self.datapath, [])
        print('文件夹内包含贴图总数量：' + str(len(list))) #得到文件数量
        # newimg = Image.new('RGB',(512,512),(128,128,128)) #建立一个新图片
        a = 0
        for e in list:
            print(e)
            img = Image.open(e) #读取图像  

            
            a += 1


        global imga   #要申明全局变量我猜测是调用了canvas
        re_image = resize(img)  # 调用函数
        imga = ImageTk.PhotoImage(re_image)  # PhotoImage类是用来在label和canvas展示图片用的
        canvas.create_image(500, 500, image=imga)

        self.datapathshow.set(self.datapath)  #把目录显示出来

    def get_save_datapath(self):
        self.save_datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
        self.savedatapathshow.set(self.save_datapath)



def resize(image):
    w, h = image.size
    mlength = max(w, h)  # 找出最大的边
    mul = 400 / mlength  # 缩放倍数
    w1 = int(w * mul)  # 重新获得高和宽
    h1 = int(h * mul)
    return image.resize((w1, h1))    


root = Tk()


app = App(root)
app.mainloop()