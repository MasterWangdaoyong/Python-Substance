# 作者：王健平
# 时间：20210103
# 功能：主函数

from tkinter import *
from tkinter import ttk
from tkinter import filedialog  #获取文件夹
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
import os

# 创建窗体
mainUI = Tk()
mainUI.title('172099994@qq.com')
# mainUI.resizable(width=False, height=False)
# mainUI.config(background='#EEE')
mainUI.geometry('500x240')

# 启动获取动作
def run():
    print ("hi there, everyone!")
    Folderpath = filedialog.askdirectory() #获取文件夹
    print(Folderpath)
    list = get_filelist(Folderpath,[])
    print(len(list))
    for e in list:        
        outfile = os.path.splitext(e)[0] + ".png"
        if e != outfile:
            try:
                Image.open(e).save(outfile)
            except IOError:
                print ("cannot convert", e)
        print(e)
        
    # img = Image.open(e)
    # print(img.format)		 # 输出图片基本信息
    # print(img.mode)
    # print(img.size)
    # img_resize = img.resize((256,256)) # 调整尺寸
    # img_resize.save("dogresize.jpg")
    # img_rotate = img.rotate(45)         # 旋转
    # img_rotate.save("dogrotate.jpg")
    # om=img.convert('L')				# 灰度处理
    # om.save('doggray.jpg')
    # om = img.filter(ImageFilter.CONTOUR)		# 图片的轮廓
    # om.save('dogcontour.jpg')
    # om = ImageEnhance.Contrast(img).enhance(20)		# 对比度为初始的10倍
    # om.save('dogencontrast.jpg')
    
    # filelist =[e,
    #         "dogcontour.jpg",
    #         "dogencontrast.jpg",
    #         "doggray.jpg",
    #         "dogresize.jpg",
    #         "dogrotate.jpg",
    #         ]
    # for infile in filelist:
    #     outfile = os.path.splitext(infile)[0] + ".png"
    #     if infile != outfile:
    #         try:
    #             Image.open(infile).save(outfile)
    #         except IOError:
    #             print ("cannot convert", infile)


# 路径选择
pathA = "路径选择"
iptCookie = ttk.Entry(mainUI, textvariable=pathA)
iptCookie.grid(row = 0,column=1, ipady=20, sticky='WE')

# 嗅探资源
bt = ttk.Button(mainUI, text='开始嗅探资源类别', width=30, command=run)
bt.grid(row = 0, column=2, padx=10, ipady=10, ipadx=10, sticky=E)

def get_filelist(dir, Filelist):     
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
            newDir=os.path.join(dir,s) 
            get_filelist(newDir, Filelist) 
    return Filelist


mainUI.mainloop()
