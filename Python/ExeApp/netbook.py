 # -*- coding: utf-8 -*-
# import tkinter as tk  #装载tkinter模块,用于Python3
# from tkinter import ttk  #装载tkinter.ttk模块,用于Python3
# from tkinter import filedialog  #获取文件夹

# #------------HP_tk2中Notebook2模块
# class Notebook2(tk.Frame): # 继承Frame类的Notebook类
#     def __init__(self, master=None):  
#         tk.Frame.__init__(self, master)  
#         self.root = master #定义内部变量root

#         self.datapath = 'StringVar()' #指定类型

#         self.pack()
#         self.add()

#     def add(self):
#         # self.c=tk.Frame(self)
#         # self.c.pack(side=tk.TOP)
#         self.button = tk.Button(self, width=10,text='text')
#         self.button["command"] = self.get_data_path
#         self.button.grid()

#     def get_data_path(self):
#         self.datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径)
#         print('ccccccccccccccc')  #把目录显示出来    
# #------上面是class Notebook2定义

# root =tk.Tk()  # 创建窗口对象
# root.title(string = 'ttk.Notebook演示')  #设置窗口标题
# root.geometry('800x600+200+200')

# tabControl = ttk.Notebook(root)  #创建Notebook
# tab1 = tk.Frame(tabControl,)  #增加新选项卡
# tabControl.add(tab1, text='信息窗')  #把新选项卡增加到Notebook
# tab2 = tk.Frame(tabControl)
# tabControl.add(tab2, text='综合信息')
# # tab3 = tk.Frame(tabControl,bg='green')
# # tabControl.add(tab3, text='技术分析')
# # tab4 = tk.Frame(tabControl,bg='blue')
# # tabControl.add(tab4, text='编写代码')
# # tab5 = tk.Frame(tabControl,bg='blue') 
# # tabControl.add(tab5, text='模拟回测')

# # tab6 = ttk.Frame(tabControl) 
# # tabControl.add(tab6, text='双色球')
# # tab7 = ttk.Frame(tabControl) 
# # tabControl.add(tab7, text='大乐透')
# tabControl.pack(expand=1, fill="both")

# # tabControl.select(tab1) #选择tab1
# #---------------演示1------------------------------------
# # mytabControl=Notebook2(tab1,anchor=tk.SW)
# # mytab1 = tk.Frame(mytabControl,bg='red')  #增加新选项卡
# # mytabControl.add(mytab1,text='信息1')
# # mytab2 = tk.Frame(mytabControl,bg='blue')  #增加新选项卡
# # mytabControl.add(mytab2,text='信息2')
# # mytab3 = tk.Frame(mytabControl,bg='yellow')  #增加新选项卡
# # mytabControl.add(mytab3,text='信息3')
# #---------------演示2------------------------------------
# mytabControl2=Notebook2(tab2)
# # mytabControl3=Notebook2(tab3,m=4,anchor=tk.SW)
# # mytabControl4=Notebook2(tab4,m=5,anchor=tk.S)
# # mytabControl5=Notebook2(tab5,m=4,anchor=tk.N)
# # mytabControl6=Notebook2(tab6,m=5,anchor=tk.SE)
# # mytabControl7=Notebook2(tab7,m=4,anchor=tk.NE)

# root.mainloop()     # 进入消息循环








 # -*- coding: utf-8 -*-
import tkinter as tk  #装载tkinter模块,用于Python3
from tkinter import ttk  #装载tkinter.ttk模块,用于Python3

#------------HP_tk2中Notebook2模块
class Notebook2(tk.Frame): # 继承Frame类的Notebook类
    def __init__(self, master=None,m=0,anchor=tk.NW, size=9,width=10,**kw):  
        tk.Frame.__init__(self, master,**kw)  
        self.root = master #定义内部变量root
        self.m=m
        self.width=width
        self.size=size
        self.anchor=anchor
        self.s1=tk.TOP
        self.s2=tk.BOTTOM
        if (self.anchor in [tk.SW,tk.S,tk.SE]):
            self.s1=tk.BOTTOM
            self.s2=tk.TOP
        self.t=[]
        self.v=[]
        self.view=None
        self.pack(side=self.s2, fill=tk.BOTH, expand=1,ipady=1,pady=1,ipadx=1,padx=1)

        self.tab()


    def add(self,tab=None,text=''):
        if (tab!=None):
            self.m=self.m+1
            def handler (self=self, i=self.m-1 ):
                self.select(i)
            
            if (self.anchor in [tk.NW,tk.N,tk.SW,tk.S]):
                self.button = tk.Button(self.tab, width=self.width,text=text, cursor='hand2',
                                        anchor=tk.S,
                                        font=('Helvetica', '%d'%self.size),
                                        command=handler)
                self.t.append(self.button)
                self.button.pack(side=tk.LEFT)
                self.v.append(tab)
                if (self.m==1):
                    self.select(0)


            if (self.anchor in [tk.NE,tk.SE]):
                self.button = tk.Button(self.tab, width=self.width,text=text, cursor='hand2',
                                        anchor=tk.S,
                                        font=('Helvetica','%d'%self.size),
                                        command=handler)
                self.t.append(self.button)
                self.button.pack(side=tk.RIGHT)
                self.v.append(tab)
                if (self.m==1):
                    self.select(0)


    def tab(self):
        self.tab=tk.Frame(self)
        if (self.anchor in [tk.N,tk.S]):
            self.tab.pack(side=self.s1)
        if (self.anchor in [tk.NW,tk.NE,tk.SW,tk.SE]):
            self.tab.pack(side=self.s1,fill=tk.X)

        
        for i in range(self.m):
            def handler (self=self, i=i ):
                self.select(i)
            self.button = tk.Button(self.tab, width=self.width,text='Tab%d'%i, cursor='hand2',
                                    anchor=tk.S,
                                    font=('Helvetica','%d'%self.size),
                                    command=handler)
            self.t.append(self.button)
            self.v.append(None)
            if (self.anchor in [tk.NW,tk.SW]) :
                self.button.pack(side=tk.LEFT)
            else:
                self.button.pack(side=tk.RIGHT)
            
        self.update()

         
    def frame(self):
        self.frame=tk.Frame(self,bd=2,
                            borderwidth=2,  #边框宽度
                            padx=1,  #部件x方向间距
                            pady=1, #部件y方向间距
                            )
        self.frame.pack(side=self.s2,fill=tk.BOTH, expand=1)         


    def select(self,x):
        print(x)
        if (self.view!=None):
            self.view.pack_forget()
        for i in range(self.m):
            self.t[i]['relief']=tk.RIDGE
            self.t[i]['anchor']=tk.S
            self.t[i]['bg']="#F0F0ED"
            
        self.t[x]['anchor']=tk.N
        self.t[x]['bg']='white'
        self.view=self.v[x]
        if (self.view!=None):
            self.view.pack(fill=tk.BOTH, expand=1)   


    def modify(self,x,tab=None,text=''):
        if (x>self.m-1):
            return
        if (tab!=None):
            self.v[x]=tab
        if (text!=''):
            self.t[x]['text']=text
#------上面是class Notebook2定义

root =tk.Tk()  # 创建窗口对象
root.title(string = 'ttk.Notebook演示')  #设置窗口标题
root.geometry('800x600+200+200')

tabControl = ttk.Notebook(root)  #创建Notebook
tab1 = tk.Frame(tabControl,bg='blue')  #增加新选项卡
tabControl.add(tab1, text='信息窗')  #把新选项卡增加到Notebook
tab2 = tk.Frame(tabControl,bg='yellow')
tabControl.add(tab2, text='综合信息')
tab3 = tk.Frame(tabControl,bg='green')
tabControl.add(tab3, text='技术分析')
tab4 = tk.Frame(tabControl,bg='blue')
tabControl.add(tab4, text='编写代码')
tab5 = tk.Frame(tabControl,bg='blue') 
tabControl.add(tab5, text='模拟回测')

tab6 = ttk.Frame(tabControl) 
tabControl.add(tab6, text='双色球')
tab7 = ttk.Frame(tabControl) 
tabControl.add(tab7, text='大乐透')
tabControl.pack(expand=1, fill="both")

tabControl.select(tab1) #选择tab1
#---------------演示1------------------------------------
mytabControl=Notebook2(tab1,anchor=tk.SW)
mytab1 = tk.Frame(mytabControl,bg='red')  #增加新选项卡
mytabControl.add(mytab1,text='信息1')
mytab2 = tk.Frame(mytabControl,bg='blue')  #增加新选项卡
mytabControl.add(mytab2,text='信息2')
mytab3 = tk.Frame(mytabControl,bg='yellow')  #增加新选项卡
mytabControl.add(mytab3,text='信息3')
#---------------演示2------------------------------------
mytabControl2=Notebook2(tab2,m=3)
mytabControl3=Notebook2(tab3,m=4,anchor=tk.SW)
mytabControl4=Notebook2(tab4,m=5,anchor=tk.S)
mytabControl5=Notebook2(tab5,m=4,anchor=tk.N)
mytabControl6=Notebook2(tab6,m=5,anchor=tk.SE)
mytabControl7=Notebook2(tab7,m=4,anchor=tk.NE)

root.mainloop()     # 进入消息循环
