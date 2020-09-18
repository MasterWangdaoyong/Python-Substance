
# 第五章  if语句  20200803

# 5.1     一个简单的示例
# cars = ['audi', 'bmw', 'subaru', 'toyota']
# for car in cars:
#     if car == 'bmw':
#         print(car.upper())
#     else:
#         print(car.title())

# 5.2     条件测试
# 5.2.1   检查是否相等
# 5.2.2   检查是否相等时不考虑大小写

# 5.2.3   检查是否不相等
# requested_topping = 'mushrooms'
# if requested_topping != 'anchovies' :
#     print("Hold the anchovies!")

# 5.2.4   比较数字
# answer = 250
# if answer != 33:
#     print("That is not the correct answer. Please try again!")

# 5.2.5   检查多个条件
# answer = 250
# if (answer >= 33) and (answer >= 322):
#     print("0.1  That is not the correct answer. Please try again!")
# if (answer >= 33) or (answer <= 322):
#     print("0.2  That is not the correct answer. Please try again!")

# 5.2.6   检查特定值是否包含在列表中  用in

# 5.2.7   检查特定值是否不包含在列表中  20200814
# banned_users = ['andrew', 'carolina', 'david']
# user = 'marie'
# if user not in banned_users:
#     print(user.title() + ", you can post a response if you wish.") 

# 5.2.8   布尔表达式

# 5.3     if 语句

# 5.3.1   简单的if 语句
# age = 30
# if age >= 25:
#     print("You are old enough to vote!")
#     print("Have you registered to vote yet?")

# 5.3.2   if-sles 语句
# age = 31
# if age >= 25:
#     print("A")
# else :
#     print("B")

# 5.3.3   if-elif-else 结构
# age = 12
# if age < 4:
#     print("Your admission cost is $0.")
# elif age < 18:
#     print("Your admission cost is $5.")
# else:
#     print("Your admission cost is $10.")

# age = 12
# if age < 4:
#     price = 0
# elif age < 18:
#     price = 5
# else:
#     price = 10    
# print("Your admission cost is $" + str(price)+ " .")

# 5.3.4   使用多个elif代码块
# age = 12
# if age < 4:
#     price = 0
# elif age < 18:
#     price = 5
# elif age < 65:
#     price = 15
# else:
#     price = 10    
# print("Your admission cost is $" + str(price)+ " .")

# 5.3.5   省略 else 代码块
# age = 12
# if age < 4:
#     price = 0
# elif age < 18:
#     price = 5
# elif age < 65:
#     price = 15
# print("Your admission cost is $" + str(price)+ " .")

# 5.3.6   测试多个条件
# requ = ['aa', 'bb']
# if 'aa' in requ:
#     print("add")
# if 'cc' in requ:
#     print('add')
# else:
#     print("non")
# if 'bb' in requ:
#     print("add")
# print("\n Yeah!")



# 5.4   使用if语句处理列表
# 5.4.1   检查特殊元素
# ra = ['aa', 'bb', 'cc']
# for data in ra:
#     print("Adding " + data + ".")
# print("\n finished making your pizza!")

# ra = ['aa', 'bb', 'cc']
# for data in ra:
#     if data == 'cc':
#         print("Adding " + data + ".")
#     else:
#         print("non")
# print("\n finished making your pizza!")

# 5.4.2   确定列表不是空的
# ra = []
# if ra :
#     for data in ra:
#         print("Y")
#     print("N")
# else:     
#     print("C")

# 5.4.3   使用多个列表 (多个列表内容，元素对比)
# ava = ['aa', 'bb', 'cc', 'dd', 'ee', 'ff']
# ra = ['aa', 'bbb', 'ee']
# for radata in ra:
#     if radata in ava:
#         print( radata + " in ava")
#     else:
#         print(radata + " no ava")
# print("your pizza!")
