# # class textureCombine():
# #     def __init__(self):

# #         self.dir = 'a'
# #         self.Filelist = 'a'
# #         self.savepath = 'a'
# #         self.datapath = 'a'

# def get_filelist(dir, Filelist):     
#     """遍历文件夹内的文件"""
#     newDir = dir 
#     if os.path.isfile(dir): 
#         Filelist.append(dir) 
#         # # 若只是要返回文件文，使用这个 
#         # Filelist.append(os.path.basename(dir)) 
#     elif os.path.isdir(dir): 
#         for s in os.listdir(dir): 
#             # 如果需要忽略某些文件夹，使用以下代码 
#             #if s == "xxx": 
#                 #continue 
#             newDir=os.path.join(dir, s) 
#             get_filelist(newDir, Filelist) 
#     return Filelist        

# def savepath():
#     """合并后的贴图存放哪"""
#         #弹开面板，选择获取文件夹，得到路径
#     savepath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径
#     print(savepath)

# def datapath():
#     """合并前资源目录"""
#     datapath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径
#     print(datapath)

# def run():
#     """启动获取动作"""
#     print ("程序开始运行")
#     Folderpath = filedialog.askdirectory() #弹开面板，选择获取文件夹，得到路径
#     # print(Folderpath)
#     newimg = Image.new('RGB',(512,512),(128,128,128)) #建立一个新图片
#     list = get_filelist(Folderpath, []) #遍历文件夹，得到文件
#     print(list)
#     print(len(list)) #得到文件数量
#     a = 0
#     for e in list:        
#         # outfile = os.path.splitext(e)[0] + ".png"
#         # if e != outfile:
#         #     try:
#         #         Image.open(e).save(outfile)
#         #     except IOError:
#         #         print ("cannot convert", e)
#         print(e)        
#         img = Image.open(e) #读取图像
#         if a == 0:
#             newimg.paste(img, (0,0))    #转填充图像，以512大小为例，00为左上，256，256为中心
#         elif a == 1:
#             newimg.paste(img, (0,256))
#         elif a == 2:
#             newimg.paste(img, (256,0))
#         else :
#             newimg.paste(img, (256,256))
#         a += 1
#         # img = Image.open(e)
#         # print(img.format, img.size, img.mode)

#     #新建图像，用与合并
#     newimg.save(Folderpath + '/' + 'T2.png', 'png') #Folderpath为路径， ‘/’文件夹目录去除，不然会添加上文件夹名称在图片名上， 'jpeg'为格式        
#     print("-------------图像合并完成-------------")

# # 字符输入
# # pathA = "路径选择"
# # iptCookie = ttk.Entry(mainUI, textvariable=pathA)
# # iptCookie.grid(row = 3,column=1, ipady=20, sticky='WE')   

# # def textureCombine_ui(self):
       

            


# mainUI = Tk()   #新建主面板
# mainUI.title('172099994@qq.com')    #主面板名
# # mainUI.resizable(width=False, height=False)
# # mainUI.config(background='#EEE')
# mainUI.geometry('500x240')  #主面板大小

# # 合并前 资源目录 按钮
# bt = ttk.Button(mainUI, text='贴图在哪', width=30, command=datapath)
# bt.grid(row = 0, column=2, padx=10, ipady=10, ipadx=10, sticky=E)

# # 合并后 目录 按钮
# bt2 = ttk.Button(mainUI, text='合并后的贴图存放哪', width=30, command=savepath)
# bt2.grid(row = 1, column=2, padx=10, ipady=10, ipadx=10, sticky=E)

# # 执行贴图合并 按钮
# bt3 = ttk.Button(mainUI, text='确认合并贴图', width=30, command=run)
# bt3.grid(row = 2, column=2, padx=10, ipady=10, ipadx=10, sticky=E)   

# mainUI.mainloop()   #面板刷新循环



# # cars = ["bmw", "audi", "toyota", "subaru"]   #前提条件，注意字母大小写时的混搭
# # cars.sort()  #对列表永久性修改顺序，按字母排序
# # print(cars)
# # cars.sort(reverse = True) #逆向排序，永久性的修改
# # print(cars)
# # print(sorted(cars))  #临时按字母排序，不对原始数据修改

# # name = []
# # name.append("jianpingWang")
# # name.append("huangwenghua")
# # print(name)
# # print(name[1])


# # data = {
# #     'Normal' : ['normal1', 'normal2'],
# #     'Albedo' : ['albedo1', 'albedo2'],
# #     'Mask' : ['mask1', 'mask2'],
# # }  
# # for name, languages in data.items():
# #     print('\n' + name.title())
# #     for language in languages:
# #         print('\t' + language.title())

# # 6.1  一个简单的字典
# # alien_0 = {'color': 'green', 'point' : 5}   #类枚举功能 #类引用  #类似指针
# # print(alien_0['color'])
# # print(alien_0['point'])

# # 6.2.1  访问字典中的值
# # alien_0 = {'color': 'green', 'point' : 5}
# # print(alien_0['color'])
# # new_points = alien_0['point']
# # print('You must earned ' + str(new_points) + ' points!')

# # 6.2.2  添加键－值对(添加枚举，并指定上枚举包含的值，类似理解)
# # alien_0 = {'color': 'green', 'point' : 5}
# # print(alien_0)
# # alien_0['x_position'] = 0
# # alien_0['y_position'] = 1024
# # print(alien_0)

# # 6.2.3  先创建一个空字典   20200824
# # alien_0 = {}
# # #空字典
# # alien_0['color'] = 'green'
# # #字典名 变量名       值
# # alien_0['point'] = 5
# # print(alien_0)

# # aline_0 = {'x_position' : 0, 'y_position' : 25, 'speed' : 'medium'}
# # print('Original x-position: ' + str(aline_0['x_position']))
# # if aline_0['speed'] == 'slow':
# #     x_increment = 1
# # elif aline_0['speed'] == 'medium':
# #     x_increment = 2
# # else:
# #     x_increment = 3
# # aline_0['x_position'] = aline_0['x_position'] + x_increment
# # print('New x_position: ' + str(aline_0['x_position']))

# # 6.3  遍历字典
# # 6.3.1  遍历所有的键值对
# # user_0 = {
# #     'username' : 'efermi',
# #     'first' : 'enrico',
# #     'last' : 'fermi',
# # }
# # for key, value in user_0.items():
# #     print('\nkey: ' + key)
# #     print('Value: ' + value)

# # 6.3.2  遍历字典中的所有键
# # favorite_languages = {
# #     'jen' : 'python',
# #     'sarah' : 'c',
# #     'edward' : 'ruby',
# #     'phil' : 'python',
# # }
# # for name in favorite_languages.keys():
# #     print(name.title())
# # for name in favorite_languages:  #可以省略.keys()  显式的写上，增加代码可读率
# #     print('2 ' + name.title())

# # 6.3.2  遍历字典中的所有键
# # favorite_languages = {
# #     'jen' : 'python',
# #     'sarah' : 'c',
# #     'edward' : 'ruby',
# #     'phil' : 'python',
# # }
# # for name in favorite_languages.keys():
# #     print(name.title())
# # for name in favorite_languages:  #可以省略.keys()  显式的写上，增加代码可读率
# #     print('2 ' + name.title())

# # 7.3  使用 while 循环来处理列表和字典
# # 7.3.1  在列表之间移动元素
# # unID = ['alice', 'brian', 'candace']
# # ID = []
# # while unID :
# #     user = unID.pop()
# #     print("verifying user: " + user.title())
# #     ID.append(user)
# # print("\nThe following users have been confirmed:")
# # for user in ID:
# #     print(user.title())

# # 7.3.3  使用用户输入来填充字典
# # responses = {}  #创建字典
# # polling_active = True   #创建判断条件
# # while polling_active:   #循环输入
# #     name = input("\nWhat is your name? ")       
# #     b = input("Which mountain would you like to climb someday? ")
# #     responses[name] = b    #输入key值，和key的对应值   同时赋值

# #     repeat = input("Would you like to let another person respond? (yes/no) ")   #循环终于的判断条件输入
# #     if repeat == 'no':          
# #         polling_active = False      #指定为否  终于循环

# # print("\n--- Poll Results ---")
# # for name, b in responses.items():    #循环打印
# #     print(name + " would like to climb " + b + '.')   

# # number = list(range(1, 10, 2))  #索引 内存位置 + 2步长
# # print(number)

# # 4.4.1   切片
# # players = ['charles', 'martina', 'michael', 'florence', 'eli']
# # print(players[0:3])   #0到第三个
# # print(players[1:4])   #1到第4个
# # print(players[:4])    #没有指定所以从头开始，到第4个
# # print(players[2:])    #没有指定结尾所以到末尾
# # print(players[-3:])   #指定最后的三个，结束至最后尾

# # players = 'charles'
# # print(players[-3:])   #指定最后的三个，结束至最后尾

# # 4.4.2   遍历切片   字符串组遍历
# # players = ['charles', 'martina', 'michael', 'florence', 'eli']
# # print("Here are the first three palyers on my team.")
# # for play in players[:3]:
# #     print(play.title())

# # cars = ['audi', 'bmw', 'subaru', 'toyota']
# # for car in cars:
# #     if car == 'bmw':
# #         print(car.upper())
# #     else:
# #         print(car.title())

# # 5.2.7   检查特定值是否不包含在列表中  20200814
# # banned_users = ['andrew', 'carolina', 'david']
# # user = 'marie'
# # if user not in banned_users:
# #     print(user.title() + ", you can post a response if you wish.") 

# # 5.4   使用if语句处理列表
# # 5.4.1   检查特殊元素
# # ra = ['aa', 'bb', 'cc']
# # for data in ra:
# #     print("Adding " + data + ".")
# # print("\n finished making your pizza!")

# # ra = ['aa', 'bb', 'cc']
# # for data in ra:
# #     if data == 'cc':
# #         print("Adding " + data + ".")
# #     else:
# #         print("non")
# # print("\n finished making your pizza!")

# # 5.4.2   确定列表不是空的
# # ra = []
# # if ra :
# #     for data in ra:
# #         print("Y")
# #     print("N")
# # else:     
# #     print("C")











# # 8.3.3  返回字典
# # def build_person(first_name, last_name):
# #     person = {'first': first_name, 'last': last_name}
# #     return person
# # mus = build_person('jimi', 'hen')
# # print(mus)

# # 8.4  传递列表
# # def greet_user(names):
# #     for name in names:
# #         msg = "Hello, " + name.title() + "!"
# #         print(msg)
# # usrsnames = ['haha', 'ty', 'magot']
# # greet_user(usrsnames)

# # 8.5  传递任意数量的实参
# # def make_pizza(*toppins):   #在参数前加*  封装空元组  动态参数！！！！！！！！  第一次见可以动态参数数量 20200926
# #     """打印顾客的所有配料"""
# #     print("\nMaking a pizza with the following toppings:")
# #     for topping in toppins:
# #         print("- " + topping)
# # make_pizza('pepperoni')
# # make_pizza('mushrooms', 'green peppers', 'extra cheese')

# # 8.5.2  使用任意数量的关键字实参
# # def build_profile(first, last, **user_info): #两个*是一个字典
# #     profile = {}
# #     profile['first_name'] = first
# #     profile['last_name'] = last
# #     for key, value in user_info.items():
# #         profile[key] = value
# #     return profile
# # user_profile = build_profile('albert', 'base', location = 'ccc', field = 'ddd')
# # print(user_profile)





#     # import os
    
#     # def IsSubString(SubStrList,Str):
#     #     flag=True
#     #     for substr in SubStrList:
#     #         if not(substr in Str):
#     #             flag=False
#     #     return flag
    
#     # def GetFileList(FindPath,FlageStr):
#     #     FileList=[]
#     #     FileNames=os.listdir(FindPath)
#     #     for fn in FileNames:
#     #          if (IsSubString(FlagStr,fn)):
#     #              fullfilename=os.path.join(FindPath,fn)
#     #              FileList.append(fullfilename)
#     #     return FileList
    
#     # FindPath="/d3/MWRT/R20130805/"
#     # # 查找指定目录下文件名中包含F06925，EMS和txt字符的文件
#     # FlagStr=['F06925','EMS','txt']
#     # FileList=GetFileList(FindPath,FlagStr)
#     # print(FileList)






#             # img = Image.open(e)
#         # print(img.format)		 # 输出图片基本信息
#         # print(img.mode)
#         # print(img.size)
#         # img_resize = img.resize((256,256)) # 调整尺寸
#         # img_resize.save("dogresize.jpg")
#         # img_rotate = img.rotate(45)         # 旋转
#         # img_rotate.save("dogrotate.jpg")
#         # om=img.convert('L')				# 灰度处理
#         # om.save('doggray.jpg')
#         # om = img.filter(ImageFilter.CONTOUR)		# 图片的轮廓
#         # om.save('dogcontour.jpg')
#         # om = ImageEnhance.Contrast(img).enhance(20)		# 对比度为初始的10倍
#         # om.save('dogencontrast.jpg')
        
#         # filelist =[e,
#         #         "dogcontour.jpg",
#         #         "dogencontrast.jpg",
#         #         "doggray.jpg",
#         #         "dogresize.jpg",
#         #         "dogrotate.jpg",
#         #         ]
#         # for infile in filelist:
#         #     outfile = os.path.splitext(infile)[0] + ".png"
#         #     if infile != outfile:
#         #         try:
#         #             Image.open(infile).save(outfile)
#         #         except IOError:
#         #             print ("cannot convert", infile)

# import tkinter as tk
# from PIL import ImageTk
# from tkinter import filedialog       #获取文件全路径
# from tkinter import *

# from PIL import Image
# from PIL import ImageFilter
# from PIL import ImageEnhance

# root=tk.Tk()   #创建对象
# root.title('图片查看器')     #窗口的名称
# root.geometry('400x400')     #规定窗口大小

# l=tk.Label(root,text='pictures will show in this place', image=None)   #创建一个标签
# l.grid()     #放置标签

# def openpicture():
#     global img
#     filename=filedialog.askopenfilename()     #获取文件全路径
#     img=ImageTk.PhotoImage(Image.open(filename))   #tkinter只能打开gif文件，这里用PIL库
#     # 打开jpg格式的文件
#     l.config(image=img)    #用config方法将图片放置在标签中
 
# b=tk.Button(root,text='select a picture', command=openpicture)  #设置按钮，并给它openpicture命令
# b.grid()

# tk.mainloop()