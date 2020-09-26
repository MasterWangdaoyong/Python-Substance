#20200926  第9章 类

# 9.1  创建和使用类
# 6.1.1  创建 Dog 类
# class Dog():
#     """一次模拟小狗的简单尝试"""

#     def __init__(self, name, age):
#         """初始化属性name 和age"""
#         self.name = name
#         self.age = age
    
#     def sit(self):
#         """模拟小狗被命令时蹲下"""
#         print(self.name.title() + " is now sitting.")
    
#     def roll_over(self):
#         """模拟小狗被命令时打滚"""
#         print(self.name.title() + " rolled over!")

# 9.1.2  根据类创建实例
# class Dog():
#     """一次模拟小狗的简单尝试"""
    
#     def __init__(self, name, age):
#         """初始化属性name 和age"""
#         self.name = name
#         self.age = age
    
#     def sit(self):
#         """模拟小狗被命令时蹲下"""
#         print(self.name.title() + " is now sitting.")
    
#     def roll_over(self):
#         """模拟小狗被命令时打滚"""
#         print(self.name.title() + " rolled over!")

# my_dog = Dog('willie', 6)
# your_dog = Dog('lucy', 3)
# print("My dog's name is " + my_dog.name.title() + ".")
# print("My dog is " + str(my_dog.age) + " years old.")
# my_dog.sit()

# print("\nYour dog's name is " + your_dog.name.title() + ".")
# print("Your dog is " + str(your_dog.age) + " years old.")
# your_dog.sit()


# 9.2.1  Car 类