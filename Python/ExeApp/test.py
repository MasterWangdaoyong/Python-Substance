import tkinter
import tkinter.ttk


def show():
    # 使用var.get()来获得目前选项内容
    varLabel.set(var.get())


root = tkinter.Tk()
var = tkinter.StringVar()
combobox = tkinter.ttk.Combobox(root, textvariable=var)
combobox['value'] = ('python', 'java', 'C', 'C++')
combobox.current(0)
combobox.pack(padx=5, pady=10)

varLabel = tkinter.StringVar()
label = tkinter.Label(root, textvariable=varLabel, width=20, height=3, bg='lightblue', fg='red')
label.pack()

button = tkinter.Button(root, text='print', command=show)
button.pack()

root.mainloop()
