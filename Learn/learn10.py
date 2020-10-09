#20201009  第10章 文件和异常

# 10.1  从文件中读取数据
# 10.1.1  读取整个文件

# 10.1.2  文件路径
# 相对路径 好像在PC系统内需要把文件夹path放置在环境变量中才能找到 不然就得给上绝对路径
# with open('text_files/filename.txt') as file_object:  #Linux OS X系统方法
# with open('text_files\filename.txt') as file_object:  #windows 系统方法是反斜杠
# 例如这个

# 绝对路径
#Linux OS X系统方法
# file_path = '/home/ehmatthes/other_files/text_files/filename_txt'
# with open(file_path) as file_object:
#windows 系统方法是反斜杠
# file_path = 'C:\Users\ehmatthes\other_files\text_files\filename_txt'
# with open(file_path) as file_object:

# 10.1.3  每行读取

# 10.1.4  创建一个包含文件各行内容的列表

# 10.1.5  使用文件的内容

# 10.1.6  包含一百万位的大型文件

# 10.1.7  圆周率值中包含你的生日吗

# 10.2  写入文件
# 10.2.1  写入空文件

# 10.2.2  写入多行

# 10.2.3  附加到文件

# 10.2  异常
# 10.3.1  处理ZeroDivisionError 异常
# 10.3.2  使用 try-except 代码块
# 10.3.3  使用异常避免崩溃
# 10.3.4 else 代码块

# 10.3.5  处理 FileNotFoundError 异常
# 10.3.6  分析文本

# 10.3.7  使用多个文件
# 10.3.8  失败时一声不吭

# 10.4  存储数据
# 10.4.1  使用 json.dump() 和 json.load()
# dump是写 包含两个参数，#前参是需要写入的数值  后参是对象文件名、类型、路径 
# load是读 只有一个对象参数

# 10.4.2  保存和读取用户生成的数据
# 10.4.3  重构 改进、能更清晰、更易于理解、更容易扩展