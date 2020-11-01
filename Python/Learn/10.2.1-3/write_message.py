#20201009  第10章 第二节

# 10.2.1  写入空文件
# filename = 'F:/Main_Project/Python/Learn/10.2.1-3/programming.txt'   #绝对路径 
# #相对路径会把文件创建在 Python这个文件夹内
# with open(filename, 'w') as file_object:
#     file_object.write('I love TA.')

# 10.2.2  写入多行
# filename = 'F:/Main_Project/Python/Learn/10.2.1-3/programming.txt'   #绝对路径 
# #相对路径会把文件创建在 Python这个文件夹内
# with open(filename, 'w') as file_object:
#     file_object.write('I love TA.')
#     file_object.write('I love Creating new game.\n')
#     file_object.write('I love TA.\n')
#     file_object.write('I love Creating new game.\n')

# 10.2.3  附加到文件
# filename = 'F:/Main_Project/Python/Learn/10.2.1-3/programming.txt'   #绝对路径 
# #相对路径会把文件创建在 Python这个文件夹内
# with open(filename, 'a') as file_object:
#     file_object.write('A.')
#     file_object.write('BBB.\n')
#     file_object.write('C CC.\n')
#     file_object.write('DDD D.\n')