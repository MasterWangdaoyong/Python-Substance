from tkinter import *
from tkinter import ttk
import random

# https://www.jianshu.com/p/91844c5bca78
# https://www.jianshu.com/p/a54a5eab7e17
# https://www.liaoxuefeng.com/wiki/1016959663602400/1017786914566560

root = Tk() #初始化
root.title('TimeM:172099994@qq.com') #项目名
# root.resizable(width=False, height=False)
# root.config(background='#EEE')
root.geometry('300x150')

def gen():
    val.set(repr(random.random()))

val = StringVar()
val.set('3.14')
ttk.Frame(root, height=20).grid()
lb=ttk.Entry(root,textvariable=val).grid(row=1, column=1, pady=10, padx=10,ipady=5,sticky='nsew')
bt = ttk.Button(root, text='Random', width=20, command=gen).grid(
    row=2, column=1, ipady=10, ipadx=10, sticky=E)

root.mainloop() #启动
