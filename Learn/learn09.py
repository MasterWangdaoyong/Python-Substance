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


# 9.2.1  Car 类     20200927
# class Car():
#     def __init__(self, make, model, year):
#         """初始化描述汽车的属性"""
#         self.make = make
#         self.model = model
#         self.year = year
    
#     def get_descriptive_name(self):
#         """返回整洁的描述性信息"""
#         long_name = str(self.year) + ' ' + self.make + ' ' + self.model
#         return long_name.title()
    
# my_new_car = Car('audi', 'a4', 2016)
# print(my_new_car.get_descriptive_name())


# 9.2.2  给属性指定默认值
# class Car():
#     def __init__(self, make, model, year):
#         """初始化描述汽车的属性"""
#         self.make = make
#         self.model = model
#         self.year = year
#         self.odometer_reading = 0   #可以理解成私有变量
    
#     def get_descriptive_name(self):
#         """返回整洁的描述性信息"""
#         long_name = str(self.year) + ' ' + self.make + ' ' + self.model
#         return long_name.title()
    
#     def read_odometer(self):        #调用了私用变量
#         """打印一条指出汽车里程的消息"""
#         print("This car has " + str(self.odometer_reading) + " miles on it.")
    
# my_new_car = Car('audi', 'a4', 2016)
# print(my_new_car.get_descriptive_name())
# my_new_car.read_odometer()          


# 9.2.3  修改属性的值
# class Car():
#     def __init__(self, make, model, year):
#         """初始化描述汽车的属性"""
#         self.make = make
#         self.model = model
#         self.year = year
#         self.odometer_reading = 0   #可以理解成私有变量
    
#     def get_descriptive_name(self):
#         """返回整洁的描述性信息"""
#         long_name = str(self.year) + ' ' + self.make + ' ' + self.model
#         return long_name.title()
    
#     def read_odometer(self):        #调用了私用变量
#         """打印一条指出汽车里程的消息"""
#         print("This car has " + str(self.odometer_reading) + " miles on it.")

#     def updata_odometer(self, mileage):
#         self.odometer_reading = mileage    
    
# my_new_car = Car('audi', 'a4', 2016)
# print(my_new_car.get_descriptive_name())
# my_new_car.read_odometer()  
# my_new_car.odometer_reading = 23
# my_new_car.read_odometer() 
# my_new_car.updata_odometer(33)
# my_new_car.read_odometer() 


# 9.3  继承
# 9.3.1  子类的方法  __init__()
