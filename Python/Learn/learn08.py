#20200926  第8章 函数

# 8.1  定义函数
# def greet_user():
#     """显示简单的问候语"""
#     print("Hello!")
# greet_user()

# 8.1.1  向函数传递信息
# def greet_user(username):
#     """显示简单的问候语"""
#     print("Hello!" + username.title() + " !")
# greet_user("Jesse")    

# 8.1.2  实参与形参

# 8.2  传递实参
# 8.2.1  位置实参
# def describe_pet(animal_type, pet_name):
#     """显示宠物的信息"""
#     print("\nI have a " + animal_type + ".")
#     print("My " + animal_type + "'s name is " + pet_name.title() + ".")
# describe_pet("hamster", 'harry')
# describe_pet("dog", 'willie')
# describe_pet("harry", 'hamster')

# 8.2.2  关键字实参
# def describe_pet(animal_type, pet_name):
#     """显示宠物的信息"""
#     print("\nI have a " + animal_type + ".")
#     print("My " + animal_type + "'s name is " + pet_name.title() + ".")
# describe_pet( animal_type = "a", pet_name = 'b')
# describe_pet( pet_name = 'b', animal_type = "a")

# 8.2.3  默认值
# def describe_pet(pet_name, animal_type ='dog'):   #跟C++ 一样默认参数要从右至左，一个给默认一个没给。给的要放在右边，从右至左。
#     """显示宠物的信息"""
#     print("\nI have a " + animal_type + ".")
#     print("My " + animal_type + "'s name is " + pet_name.title() + ".")
# describe_pet( pet_name = 'bbbbbbbb')
# describe_pet( 'aaaaaaaaaaaaa')

# 8.2.4  等效的函数调用  #不是以位置，来决定，而是以变量名来决定 输入顺序
# def describe_pet( pet_name, animal_type = 'dog'):
#     """显示宠物的信息"""
#     print("\nI have a " + animal_type + ".")
#     print("My " + animal_type + "'s name is " + pet_name.title() + ".")
# describe_pet( 'willie')
# describe_pet( pet_name = 'willie')
# describe_pet('harry', 'hamster')
# describe_pet(pet_name = 'harry', animal_type = 'hamster') #不是以位置，来决定，而是以变量名来决定
# describe_pet(animal_type = 'hamster', pet_name = 'harry') #不是以位置，来决定，而是以变量名来决定

# 8.3  返回值
# 8.3.1  返回简单值
# def get_formatted_name(first_name, last_name):
#     """返回整洁的姓名"""
#     full_name = first_name + " " + last_name
#     return full_name.title()
# muis = get_formatted_name('jimi', 'hendrix')
# print(muis)

# 8.3.2  让实参变成可选的
#1
# def get_formatted_name(first_name, middle_name, last_name):
#     """返回整洁的姓名"""
#     full_name = first_name + " " + middle_name + " " + last_name
#     return full_name.title()
# muis = get_formatted_name('jimi', 'lee', 'hendrix')
# print(muis)

#2
# def get_formatted_name(first_name, last_name,  middle_name = ''):  #注意声明的位置， 需要注意函数调用时的位置
#     """返回整洁的姓名"""
#     full_name = first_name + " " + middle_name + " " + last_name
#     return full_name.title()
# muis = get_formatted_name('jimi', 'hendrix')
# print(muis)
# muis = get_formatted_name('jimi', 'lee', 'hendrix')
# print(muis)

# 8.3.3  返回字典
# def build_person(first_name, last_name):
#     person = {'first': first_name, 'last': last_name}
#     return person
# mus = build_person('jimi', 'hen')
# print(mus)

# 8.3.4  结合使用函数和while循环
# def get_formatted_name(first_name, last_name):
#     """返回整洁的姓名"""
#     full_name = first_name + " "  + last_name
#     return full_name.title()
# while True:
#     print("\nPlease tell me your name:")
#     print("(Enter 'q' at any time to quit)")
#     f_name = input("First name: ")
#     if f_name == 'q':
#         break
#     l_name = input("Last name: ")
#     if l_name == 'q':
#         break
#     formatted_name = get_formatted_name(f_name, l_name)
#     print("\nHello, " + formatted_name + "!")

# 8.4  传递列表
# def greet_user(names):
#     for name in names:
#         msg = "Hello, " + name.title() + "!"
#         print(msg)
# usrsnames = ['haha', 'ty', 'magot']
# greet_user(usrsnames)

# 8.4.1  在函数中修改列表
#1
# A = ['iphone', 'robot', 'dod']
# B = []
# while A:
#     C = A.pop()
#     print("Printing model:" + C)
#     B.append(C)   #存在data的A 转存至中间C中  然后把C添加到B中
# print("\nThe following models have been printed:")
# for D in B:  #声明D 再循环打印B中的data
#     print(D)   #这书真没法跟C++  plus比  太过混乱

#2
# def print_models(unprinted_designs, completed_models):
#     """模拟打印每个设计，直到没有未打印的设计为主
#     打印每个设计后，都将其移到列表completed_models中
#     """
#     while unprinted_designs:
#         current_desgin = unprinted_designs.pop()
#         #模拟根据设计制作3D打印模型的过程
#         print("Printing model: " + current_desgin)
#         completed_models.append(current_desgin)
# def show_completed_models(completed_models):
#     """显示打印好的所有模型"""
#     print("\nThe following models have been printed:")
#     for completed_model in completed_models:
#         print(completed_model)
# unprinted_designs = ['iphone', 'robot', 'dod']
# completed_models = []
# print_models(unprinted_designs, completed_models)
# show_completed_models(completed_models)

# 8.4.2  禁止函数修改列表
# print_models(unprinted_designs[:], completed_models)  #复制一份副本，不修改原数据  但会消耗更高的内存和性能与时间
#要有充分理由才使用此方法   正常情况下日常还是传递原始数据比较好

# 8.5  传递任意数量的实参
# def make_pizza(*toppins):   #在参数前加*  封装空元组  动态参数！！！！！！！！  第一次见可以动态参数数量 20200926
#     """打印顾客的所有配料"""
#     print("\nMaking a pizza with the following toppings:")
#     for topping in toppins:
#         print("- " + topping)
# make_pizza('pepperoni')
# make_pizza('mushrooms', 'green peppers', 'extra cheese')

# 8.5.1  结合使用位置实参和任意数量实参
# def make_pizza(size, *toppings):   #一个*只是一个一维数组
#     print("\nMaking a " + str(size) + "-inch pizza with the following toppings:")
#     for topping in toppings:
#         print("- " + topping)
# make_pizza(16, 'pepperoni')
# make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')

# 8.5.2  使用任意数量的关键字实参
# def build_profile(first, last, **user_info): #两个*是一个字典
#     profile = {}
#     profile['first_name'] = first
#     profile['last_name'] = last
#     for key, value in user_info.items():
#         profile[key] = value
#     return profile
# user_profile = build_profile('albert', 'base', location = 'ccc', field = 'ddd')
# print(user_profile)

# 8.6  将函数存储在模块中 (将函数存在独立的文件中)
# 8.6.1  导入整个模块  见文件夹 !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# 8.6.2  导入特定的函数
# import A #导入整个脚本 脚本内的任何东西 不管是数据还是函数 所有东西一起导入
# from A import function  #导入A脚本内的特定function函数
# from A import function0, function1, function2 #导入A脚本内的特定function0， 1， 2多个函数
# from pizza import make_pizza #导入pizza脚本内的 make_pizza函数

# 8.6.3  使用 as 给函数指定别名 #！！！－－－导入脚本文件时所需函数最好是用这种方法  －－－！！！  给一个自己的定义更加明白函数的调用
##！！！！！！  from A import function as newfunctionName 给函数名取个外号（别名），当存在函数名太长或者存在同名时可用 ！！！
# from pizza import make_pizza as mp
# mp(16, 'pepperoni')
# mp(12, 'mushrooms', 'green peppers', 'extra cheese')

# 8.6.4  使用 as 给模块指定别名 #不推荐
# import A as B   #将脚本A的内容 指定给一个新的名称B 
# B.make_pizza(16, 'pepperoni')
# B.make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese')

# 8.6.5  导入模块中的所有函数  #虽然简单明了  但不怎么推荐
# from pizza import *  # *号导入脚本内的所有函数 后面的调用就直接写函数名称即可 简短的脚本使用简单明了  大型长文件时就不太好了
# make_pizza(16, 'pepperoni')   #可能会存在同样的函数名称  
# make_pizza(12, 'mushrooms', 'green peppers', 'extra cheese'

# 8.7  函数编写指南   20200926
# 1、函数名称简短明了
# 2、全用小写和下划线
# 3、简短明了的注释说明：功能及注意
# 4、简短明了的注释说明：函数的定义（输入的参数需要是什么）
# 5、所有 import 语句都应该放在文件夹开头