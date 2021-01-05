# 作者：王健平
# 时间：20210103
# 功能：主函数

from tkinter import *
from tkinter import ttk

# 创建窗体
mainUI = Tk()
mainUI.title('172099994@qq.com')
# mainUI.resizable(width=False, height=False)
# mainUI.config(background='#EEE')
mainUI.geometry('500x240')

# 启动获取动作
def run():
    # getAll(cookieStr)
    print ("hi there, everyone!")

# 路径选择
pathA = StringVar()
pathA.set('路径选择')
iptCookie = ttk.Entry(mainUI, textvariable=pathA)
iptCookie.grid(row = 0,column=1, ipady=20, sticky='WE')

# 嗅探资源
bt = ttk.Button(mainUI, text='开始嗅探资源类别', width=30, command=run)
bt.grid(row = 0, column=2, padx=10, ipady=10, ipadx=10, sticky=E)

mainUI.mainloop()
