#20201009  第10章 第三节

# 10.3.7  使用多个文件
#1 定义函数 2传参变量 3调用函数
# def count_words(filename): #1
#     """计算一个文件大致包含多少个单词"""
#     try:
#         with open(filename) as file_object:
#             contents = file_object.read()
#     except FileNotFoundError:
#         msg = "Sorry, the file " + filename + " does not exist."
#         print(msg)
#     else:
#         #计算文件大致包含多少个单词
#         words = contents.split()
#         num_words = len(words)
#         print("The file " + filename + " has about " + str(num_words) + " words.")

# filenames = ['F:/Main_Project/Python/Learn/10.3textResources/alice.txt',
#              'F:/Main_Project/Python/Learn/10.3textResources/cc.txt',
#              'F:/Main_Project/Python/Learn/10.3textResources/little_women.txt',
#              'F:/Main_Project/Python/Learn/10.3textResources/moby_dict.txt',
#             ] #2
# for filename in filenames:            
#     count_words(filename) #3

# 10.3.8  失败时一声不吭 在try except 后加 pass
def count_words(filename): #1
    """计算一个文件大致包含多少个单词"""
    try:
        with open(filename) as file_object:
            contents = file_object.read()
    except FileNotFoundError:
        pass #失败时一声不吭 在try except 后加 pass
    else:
        #计算文件大致包含多少个单词
        words = contents.split()
        num_words = len(words)
        print("The file " + filename + " has about " + str(num_words) + " words.")

filenames = ['F:/Main_Project/Python/Learn/10.3textResources/alice.txt',
             'F:/Main_Project/Python/Learn/10.3textResources/cc.txt',
             'F:/Main_Project/Python/Learn/10.3textResources/little_women.txt',
             'F:/Main_Project/Python/Learn/10.3textResources/moby_dict.txt',
            ] #2
for filename in filenames:            
    count_words(filename) #3