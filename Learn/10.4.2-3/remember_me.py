#20201009  第10章 第四节


import json
# 10.4.2 A 保存和读取用户生成的数据
# username = input("What's your name? ")
# filename = 'F:/Main_Project/Python/Learn/10.4.2/username.json'
# with open(filename, 'w') as fobj:
#     json.dump(username, fobj)
#     print("We'll remeber you when you come back, " + username + '!')

# # 10.4.2 A2 保存和读取用户生成的数据
# # 如果以前存储了用户名，就加载它
# # 否则，就提示用户输入用户名并存储它
# filename = 'F:/Main_Project/Python/Learn/10.4.2/username.json'
# #以单个文件来存储
# try:
#     with open(filename) as fobj: #尝试打开
#         username = json.load(fobj) #读取到内存中
# except FileNotFoundError: #异常检测
#     username = input("What is your name? ") #新输入
#     with open(filename, 'w') as fobj:
#         json.dump(username, fobj)
#         print("We'll remeber you when you come back, " + username + '!')
# else: #文件存在时，常规执行
#     print("Welcome back, " + username + '! ') 

# 10.4.3  重构 改进、能更清晰、更易于理解、更容易扩展
def get_stored_username():
    """如果存储了用户名，就获取他"""
    filename = 'F:/Main_Project/Python/Learn/10.4.2-3/username.json'
    try:
        with open(filename) as fobj: #尝试打开
            username = json.load(fobj) #读取到内存中
    except FileNotFoundError: #异常检测
        return None
    else:
        return username

def get_new_username():
    """提示用户输入用户名"""
    username = input("What is your name? ")
    filename = 'F:/Main_Project/Python/Learn/10.4.2-3/username.json'
    with open(filename, 'w') as fobj:
        json.dump(username, fobj)
    return username

def greet_user():
    """问候用户，并指出其名字"""
    username = get_stored_username()
    if username:
        print("Welcome back, " + username + '! ')
    else:
        username = get_new_username()
        print("We'll remeber you when you come back, " + username + '!')

greet_user()