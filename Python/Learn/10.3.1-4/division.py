#20201009  第10章 第三节

# 10.2  异常

# 10.3.1  处理ZeroDivisionError 异常
# print(5/0)

# 10.3.2  使用 try-except 代码块
# try:
#     print(5/0)
# except ZeroDivisionError:  #ZeroDivisionError 异常变量名
#     print("You can't divide by zero!")

# 10.3.3  使用异常避免崩溃
# print("Give me two numbers, and I'll divide them.")
# print("Enter 'q' to quit")
# while True:
#     first_number = input("\nFirst number: ")
#     if first_number == 'q':
#         break
#     second_number = input("Second number: ")
#     if second_number == 'q':
#         break 
#     answer = int(first_number) / int(second_number)
#     print(answer)

# 10.3.4 else 代码块
# print("Give me two numbers, and I'll divide them.")
# print("Enter 'q' to quit")
# while True:
#     first_number = input("\nFirst number: ")
#     if first_number == 'q':
#         break
#     second_number = input("Second number: ")
#     try:
#         answer = int(first_number) / int(second_number)
#     except ZeroDivisionError:
#         print("You can't divide by 0!")
#     else:
#         print(answer)

      