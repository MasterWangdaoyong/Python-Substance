# 第六章  字典  20200819

# 6.1  一个简单的字典
# alien_0 = {'color': 'green', 'point' : 5}   #类枚举功能 #类引用  #类似指针
# print(alien_0['color'])
# print(alien_0['point'])

# DarkGold = {'age':'30', 'work':'TA', 'tall':'1.65'}       #存在问题，待解决
# for DarkGold2 in DarkGold:
#     print('DarkGold is ' + DarkGold2)

# 6.2.1  访问字典中的值
# alien_0 = {'color': 'green', 'point' : 5}
# print(alien_0['color'])
# new_points = alien_0['point']
# print('You must earned ' + str(new_points) + ' points!')

# 6.2.2  添加键－值对(添加枚举，并指定上枚举包含的值，类似理解)
# alien_0 = {'color': 'green', 'point' : 5}
# print(alien_0)
# alien_0['x_position'] = 0
# alien_0['y_position'] = 1024
# print(alien_0)

# b = 140000    #本息等额计算
# r = 3.4833 / 100
# n = 36
# a1 = b * r + b * r / pow((1 + r), n - 1) 
# print(r)
# a1 = b * r + b * r / (pow((1 + r), n) - 1) 
# print(a1)
# a1 = b * r + b * r / ((1 + r) * n - 1)
# print(a1)

# 6.2.3  先创建一个空字典   20200824
# alien_0 = {}
# #空字典
# alien_0['color'] = 'green'
# #字典名 变量名       值
# alien_0['point'] = 5
# print(alien_0)

#6.2.4  修改字典中的值
# aline_0 = {'color':'green'}
# print("The aline is " + aline_0['color'] + " .")
# aline_0['color'] = 'yellow'
# print('The aline is now ' + aline_0['color'] + ' .')

# aline_0 = {'x_position' : 0, 'y_position' : 25, 'speed' : 'medium'}
# print('Original x-position: ' + str(aline_0['x_position']))
# if aline_0['speed'] == 'slow':
#     x_increment = 1
# elif aline_0['speed'] == 'medium':
#     x_increment = 2
# else:
#     x_increment = 3
# aline_0['x_position'] = aline_0['x_position'] + x_increment
# print('New x_position: ' + str(aline_0['x_position']))

# 6.2.5  删除键一值对   #20200827
# alien_0 = {'color': 'green', 'point' : 5}
# print(alien_0)
# del alien_0['color']
# print(alien_0)

# 6.2.6  由类似对象组成的字典
# favorite_languages = {
#     'jen' : 'python',
#     'sarah' : 'c',
#     'edward' : 'ruby',
#     'phil' : 'python',
# }
# print("Sarah's favorite language is " + favorite_languages['sarah'].title() + "." )

# 6.3  遍历字典
# 6.3.1  遍历所有的键值对
# user_0 = {
#     'username' : 'efermi',
#     'first' : 'enrico',
#     'last' : 'fermi',
# }
# for key, value in user_0.items():
#     print('\nkey: ' + key)
#     print('Value: ' + value)

# favorite_languages = {
#     'jen' : 'python',
#     'sarah' : 'c',
#     'edward' : 'ruby',
#     'phil' : 'python',
# }
# for name, language in favorite_languages.items():
#     print(name.title() + " 's favourite language is " + language.title() + '.')

# 6.3.2  遍历字典中的所有键
# favorite_languages = {
#     'jen' : 'python',
#     'sarah' : 'c',
#     'edward' : 'ruby',
#     'phil' : 'python',
# }
# for name in favorite_languages.keys():
#     print(name.title())
# for name in favorite_languages:  #可以省略.keys()  显式的写上，增加代码可读率
#     print('2 ' + name.title())

# friends = ['phil', 'sarah']           #声明
# for name in favorite_languages.keys():    #先循环
#     print(name.title())
#     if name in friends:       #包含在循环内的检测
#         print(' Hi ' + name.title() +' , I see your favorite language is ' + favorite_languages[name].title() + '!')

# if 'any' not in favorite_languages.keys():        #检查列表中是否存在XXXX
#     print('Any, please take our poll!')

# 6.3.3  按顺序遍历字典中的所有键
favorite_languages = {
    'jen' : 'python',
    'sarah' : 'c',
    'edward' : 'ruby',
    'phil' : 'python',
}