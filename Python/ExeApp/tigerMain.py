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

        self.turnformat()

        self.run()   
        self._layout()


    def data_path(self):
        self.ui_datapath = ttk.Button(self)
        self.ui_datapath["text"] = "获取资源目录"
        self.ui_datapath["command"] = self.get_data_path
        self.ui_datapath_labe = ttk.Label(textvariable=self.datapathshow)

    def save_data_path(self):
        self.ui_save_data_path = ttk.Button(self)
        self.ui_save_data_path["text"] = "存放目录"
        self.ui_save_data_path["command"] = self.get_save_datapath
        self.ui_save_data_path_labe = ttk.Label(textvariable=self.savedatapathshow)   

    def run(self):
        self.ui_run = ttk.Button(self)
        self.ui_run["text"] = "开始执行合并"
        self.ui_run["command"] = self.get_run

    def get_run(self):
        """启动获取动作"""
        print ("-------------程序开始运行-------------")
        list = get_filelist(self.datapath, []) #遍历文件夹，得到文件
        print('---------------list')
        print(list)
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

    def turnformat(self):
        self.ui_turnformat = ttk.Button(self)
        self.ui_turnformat["text"] = "批量转格式"
        self.ui_turnformat["command"] = self.get_turnformat
        
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


    def _layout(self):
        self.master.title("TimeMachine") # 标题
        self.master.geometry('1024x512+50+50') # 尺寸
        self.grid()
        
        self.ui_datapath.grid(row=0) 
        self.ui_datapath_labe.grid(row=0, column=1)
        self.ui_save_data_path.grid(row=1)
        self.ui_save_data_path_labe.grid(row=1, column=1)
        self.ui_run.grid(row=2)
        self.ui_turnformat.grid(row=3)

        # self.hi_there2.grid(row=1, column=0, sticky=(N, W, E, S))
        # self.print_labe2.grid(row=1, column=1, sticky=(E))


    def get_data_path(self):
        self.datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)

        list = get_filelist(self.datapath, [])
        print('文件夹内贴图总数：' + str(len(list))) #得到文件数量
        print('---------------list')
        print(list)

        responses = {} #创建字典
        a = 0
        for e in list:
            # img = Image.open(e) #读取图像

            end = e.split("_")[3]  #文件名分割判断  而不是整个目录
            end2 = end.split(".")[0] #文件名再次分割判断 
            # print('-------end2')
            # print(end2)
            if end2 == 'Normal':
                name = 'Normal' #类型：字符串   字典中的key          
                responses.setdefault(name,[]).append(e)  #类型：数据内存 字典中的多值
                # https://www.cnblogs.com/rrttp/p/8493264.html
            elif end2 == 'Emiss':
                name1 = 'Emiss'            
                responses.setdefault(name1,[]).append(e)
            elif end2 == 'Mask':
                name2 = 'Mask'                
                responses.setdefault(name2,[]).append(e)
            else:
                name3 = 'Albedo' 
                responses.setdefault(name3,[]).append(e)
            # print("---------------responses")
            # print(responses[a].)

            # canvas[a]=tk.Canvas(self.master ,height=size, width=size, highlightthickness=0, bg='#ff0000')
            # canvas[a].grid(row=5, column=1+a, sticky=tk.W, columnspan=3)

            # size = 128
            # global imga   #要申明全局变量我猜测是调用了canvas
            # re_image = resize(img)  # 调用函数
            # imga = ImageTk.PhotoImage(re_image)  # PhotoImage类是用来在label和canvas展示图片用的
            # # print("---------------imga")
            # # print(imga)
            # canvas = tk.Canvas(self.master, width=size, height=size, bg = '#262626')
            # canvas.create_image(size/2+1, size/2+1, image=imga) #中心填充
            # canvas.grid(row=5, column=a)


            a += 1

        print("\n--- responses ---")
        a = 0
        for name, b in responses.items():    #循环打印
            print(name.title())
            print(b) 
            # for bb in b:
            #     print(bb)
            newimg = Image.new('RGB',(2048,2048),(128,128,128)) #建立一个新图片
            cc = 0
            for bb in b:
                print("\n--- BB ---K")
                print(bb)
                print("\n--- BB ---END")          
                img = Image.open(bb) #读取图像
                if cc == 0:
                    newimg.paste(img, (0,0))    #转填充图像，以512大小为例，00为左上，256，256为中心
                elif cc == 1:
                    newimg.paste(img, (0,1024))
                elif cc == 2:
                    newimg.paste(img, (1024,0))
                else :
                    newimg.paste(img, (1024,1024))                
                # print('-------------a-----k')
                # print(a)
                # print('-------------a-----e')
                cc +=1

            a += 1
            texture_name = str(a) + 'T2.png'
            texture_mode = 'png'
            newimg.save(self.save_datapath + '/' + texture_name, texture_mode)    
        print("\n--- responses ---!")            

        # https://bbs.csdn.net/topics/391902047?page=1
        # from tkinter import *
        
        # root = Tk()
        # cv = Canvas(root, bg = 'white', width = 500, height = 650) 
        # rt = cv.create_rectangle(10,10,110,110,outline='red',stipple='gray12',fill='green')
        # imgs= [PhotoImage(file='/tmp/'+str(i)+'.gif') for i in range(3)]
        # for img in imgs:
        #   cv.create_image((20*i,200*i),image=img) 
        # cv.pack()
        # root.mainloop() 
            
            

        # size = 1024
        # canvas[a]=tk.Canvas(self.master ,height=size, width=size, highlightthickness=0, bg='#ff0000')
        # canvas[a].grid(row=5, column=1+a, sticky=tk.W, columnspan=3)
        # global imga   #要申明全局变量我猜测是调用了canvas
        # re_image = resize(img)  # 调用函数
        # imga = ImageTk.PhotoImage(re_image)  # PhotoImage类是用来在label和canvas展示图片用的
        # canvas[a].create_image(256, 256, image=imga)
            
            
        # for name, b in responses.items():
        #     print(name)
        #     print(b)
        self.datapathshow.set(self.datapath)  #把目录显示出来

    def get_save_datapath(self):
        self.save_datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
        self.savedatapathshow.set(self.save_datapath)



def resize(image):
    # w, h = image.size
    # mlength = max(w, h)  # 找出最大的边
    # mul = 400 / mlength  # 缩放倍数
    # w1 = int(w * mul)  # 重新获得高和宽
    # h1 = int(h * mul)
    size = 128
    return image.resize((size, size))    


root = Tk()
app = App(root)
app.mainloop()