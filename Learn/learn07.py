#20200918  第7章 用户输入和while循环

#7.1 函数 input()的工作原理
# message = input("Tell me something, and I will repeat it back to you: ")
# print(message)
    
#7.1.1  编写清晰的程序
#1
# name = input("Please enter your name: ")
# print("hello, " + name + " !")

#2
# pro = 'If you tell us who you are, we can personalize the messages you see.'
# pro += '\nWhat is your first name? '
# name = input(pro)
# print('\nHello, '+ name + '!')

# 7.1.2  使用int()来获取数值输入  20200926
# height = input("How tall are you, in inches? ")
# height = int(height)
# if height >= 36:
#     print("\nYou're tall enough to ride!")
# else:
#     print("\nYou'll be albe to ride when you're a little older.")

# 7.2.3  求模运算符
# number = input("Enter a number, and I'll tell you if it's even or odd: ")
# number = int(number)
# if number % 2 == 0:     #余数为零被整除
#     print("\nEnter number " + str(number) + " is even.")
# else:
#     print("\nEnter number " + str(number) + " is odd.")

# 7.2.1  使用while循环
# current_number = 1
# while current_number <= 5:
#     print(current_number)
#     current_number += 1

# 7.2.2 让用户选择何时退出
# prompt = "\nTell me something, and I will repeat it back to you: "
# prompt += "\nEnter 'quit' to end the program. "
# message = ''
# while message != 'quit':
#     message = input(prompt)
#     print(message)

# 7.2.3  使用标志
# prompt = "\nTell me something, and I will repeat it back to you: "
# prompt += "\nEnter 'quit' to end the program. "
# active = True
# while active:
#     message = input(prompt)
#     if message == 'quit':
#         active = False
#     else:
#         print(message)

# 7.2.4  使用break退出循环
# prompt = "\nTell me something, and I will repeat it back to you: "
# prompt += "\nEnter 'quit' to end the program. "
# active = True
# while active:
#     city = input(prompt)
#     if city == 'quit':
#        break
#     else:
#         print(city)

# 7.2.5  在循环中使用 continue
# corrent_number = 0 
# while corrent_number < 10:
#     corrent_number += 1
#     if corrent_number % 2 == 0:
#         continue
#     print(corrent_number)

# 7.2.6  避免无限循环

# 7.3  使用 while 循环来处理列表和字典
# 7.3.1  在列表之间移动元素
# unID = ['alice', 'brian', 'candace']
# ID = []
# while unID :
#     user = unID.pop()
#     print("verifying user: " + user.title())
#     ID.append(user)
# print("\nThe following users have been confirmed:")
# for user in ID:
#     print(user.title())

# 7.3.2  删除包含特定值的所有列表元素
# pets = ['dog', 'cat', 'dog', 'goldfish', 'cat', 'rabbit', 'cat']
# print(pets)
# while 'cat' in pets:
#     pets.remove('cat')
# print(pets)

# 7.3.3  使用用户输入来填充字典
# responses = {}  #创建字典
# polling_active = True   #创建判断条件
# while polling_active:   #循环输入
#     name = input("\nWhat is your name? ")       
#     b = input("Which mountain would you like to climb someday? ")
#     responses[name] = b    #输入key值，和key的对应值   同时赋值

#     repeat = input("Would you like to let another person respond? (yes/no) ")   #循环终于的判断条件输入
#     if repeat == 'no':          
#         polling_active = False      #指定为否  终于循环

# print("\n--- Poll Results ---")
# for name, b in responses.items():    #循环打印
#     print(name + " would like to climb " + b + '.')   
