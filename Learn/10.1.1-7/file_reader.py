#20201009  第10章 第一节

# 10.1.2  文件路径
# 路径示例
# with open('F:/Main_Project/Python/Learn/10.1.1/pi_digits.txt') as file_object: #这里是绝对路径
# # with open('pi_digits.txt') as file_object: #这里是相对路径 需要放在工程Python这个文件夹内才能使用(可使用10.2.1写入空文件测试)
#     contents = file_object.read()   #file_object 是一个变量对象
#     print(contents)

# 10.1.3  每行读取
# 每行读取
# filename = 'F:/Main_Project/Python/Learn/10.1.1/pi_digits.txt' #这里是绝对路径
# with open(filename) as file_object: 
#     for a in file_object: #在with 代码块内
#         print(a.rstrip()) #删减后换行符

# 10.1.4  创建一个包含文件各行内容的列表
# filename = 'F:/Main_Project/Python/Learn/10.1.1/pi_digits.txt' #这里是绝对路径
# with open(filename) as file_object: 
#     lines = file_object.readlines()  #用对象调用方法， 得到对象信息并以特定的方式存储信息
# for line in lines:  #在with 代码块外
#     print(line.rstrip())

# 10.1.5  使用文件的内容
#txt文件是字符形式 如果需要数字 使用int() float()
# filename = 'F:/Main_Project/Python/Learn/10.1.1/pi_digits.txt' #这里是绝对路径
# with open(filename) as file_object: 
#     lines = file_object.readlines()  #用对象调用方法， 得到对象信息并以特定的方式存储信息
# pi_string = '' #字符串变量声明 
# for line in lines: #使用for 把各行添加进一行  使用的是字符串方式
#     # pi_string += line.rstrip() #整行 中有空格
#     pi_string += line.strip() #整行 没有空格  
# print(pi_string)
# print(len(pi_string))

# 10.1.6  包含一百万位的大型文件
# filename = 'F:/Main_Project/Python/Learn/10.1.1/pi_million_digits.txt' #这里是绝对路径
# with open(filename) as file_object: 
#     lines = file_object.readlines()  #用对象调用方法， 得到对象信息并以特定的方式存储信息
# pi_string = '' #字符串变量声明 
# for line in lines: #使用for 把各行添加进一行  使用的是字符串方式
#     # pi_string += line.rstrip() #整行 中有空格
#     pi_string += line.strip() #整行 没有空格  
# print(pi_string[:52] + "...")
# print(len(pi_string))

# 10.1.7  圆周率值中包含你的生日吗
# filename = 'F:/Main_Project/Python/Learn/10.1.1/pi_million_digits.txt' #这里是绝对路径
# with open(filename) as file_object: 
#     lines = file_object.readlines()  #用对象调用方法， 得到对象信息并以特定的方式存储信息
# pi_string = '' #字符串变量声明 
# for line in lines: #使用for 把各行添加进一行  使用的是字符串方式
#     # pi_string += line.rstrip() #整行 中有空格
#     pi_string += line.strip() #整行 没有空格  
# birthday = input("Enter your birthday, in the form mmddyy: ")
# if birthday in pi_string:
#     print("Your birthday appears in the first million digits of pi!")
# else:
#     print("Your birthday does not appear in the first million digits of PI.")