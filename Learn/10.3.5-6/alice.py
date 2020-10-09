#20201009  第10章 第三节

# 10.3.5  处理 FileNotFoundError 异常
# filename = 'alice.txt'
# try:
#     with open(filename) as file_object:
#         contents = file_object.read()
# except FileNotFoundError:
#     msg = "Sorry, the file " + filename + " does not exist."
#     print(msg)

# 10.3.6  分析文本
# filename = 'F:/Main_Project/Python/Learn/10.2.1-3/programming.txt'
# try:
#     with open(filename) as file_object:
#         contents = file_object.read()
# except FileNotFoundError:
#     msg = "Sorry, the file " + filename + " does not exist."
#     print(msg)
# else:
#     #计算文件大致包含多少个单词
#     words = contents.split()
#     num_words = len(words)
#     print("The file " + filename + " has about " + str(num_words) + " words.")