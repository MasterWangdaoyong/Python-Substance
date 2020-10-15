#20200926  第9章 类

# 9.1  创建和使用类
# 9.1.1  创建 Dog 类
# class Dog():
#     """一次模拟小狗的简单尝试"""

#     def __init__(self, name, age):
    """
        ❸处的方法__init__() 是一个特殊的方法，每当你根据Dog 类创建新实例时，Python都会自动运行它。在这个方法的名称中，开头和末尾各有两个下划线，这是一种约定，
        旨在避免Python默认方法与普通方法发生名称冲突。我们将方法__init__() 定义成了包含三个形参：self 、name 和age 。在这个方法的定义中，形参self 必不可少，
        还必须位于其他形参的前面。为何必须在方法定义中包含形参self 呢？因为Python调用这个__init__() 方法来创建Dog 实例时，将自动传入实参self 。每个与类相关联
        的方法调用都自动传递实参self ，它是一个指向实例本身的引用，让实例能够访问类中的属性和方法。我们创建Dog 实例时，Python将调用Dog 类的方法__init__() 。
        我们将通过实参向Dog() 传递名字和年龄；self 会自动传递，因此我们不需要传递它。每当我们根据Dog 类创建实例时，都只需给最后两个形参（name 和age ）提供值。
    """
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
# 9.3.1  子类的方法  __init__()  书页P148面祥细解说
# class Car():    #20200929
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

# class ElectricCar(Car):
#     """电动汽车的独特之处"""

#     def __init__(self, make, model, year):
#         """初始化父类的属性"""
#         super().__init__(make, model, year) #特殊函数 关联父类  父类也叫超类 superclass

# my_tesla = ElectricCar('tesla', 'modle s', 2016)
# print(my_tesla.get_descriptive_name())


# 9.3.2  Python 2.7 中的继承 过

# 9.3.3  给子类定义属性和方法
# class Car():    #20200929
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

# class ElectricCar(Car):
#     """电动汽车的独特之处"""

#     def __init__(self, make, model, year):
#         """初始化父类的属性"""
#         super().__init__(make, model, year) #特殊函数 关联父类  父类也叫超类 superclass
#         self.bettery_size = 70
    
#     def describe_battery(self):
#         """打印一条描述电瓶变量的消息"""
#         print("This car has a " + str(self.bettery_size) + "-kwh battery.")        

# my_tesla = ElectricCar('tesla', 'modle s', 2016)
# print(my_tesla.get_descriptive_name())
# my_tesla.describe_battery()


# 9.3.4  重写父类的方法
# class Car():
#     def __init__(self, a, b):
#         self.a = a
#         self.b = b

#     def fill_gas_tank(self):
#         print(self.a)

# class ElectricCar(Car):

#     def fill_gas_tank(self):
#         """电动汽车没有油箱"""
#         print("This car doesn't need a gas tank!")


# 9.3.5  将实例用作属性
#1
# class Car():    #20200929
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

# class Battery():
#     """一次模拟电动汽车电瓶的简单尝试"""
#     def __init__(self, bettery_size=70):
#         """初始化电瓶的属性"""
#         self.bettery_size = bettery_size
#     def describe_battery(self):
#         """打印一条描述电瓶容易的消息"""
#         print("This car has a " + str(self.bettery_size) + "-kwh battery.")

# class ElectricCar(Car):
#     """电动汽车的独特之处"""
#     def __init__(self, make, model, year):
#         """初始化父类的属性"""
#         super().__init__(make, model, year) #特殊函数 关联父类  父类也叫超类 superclass
#         self.bettery = Battery() #将函数当个值使用，传递进来

# my_tesla = ElectricCar('tesla', 'modle s', 2016)
# print(my_tesla.get_descriptive_name())
# my_tesla.bettery.describe_battery()  #将函数当个值使用，当值调用函数


#2
# class Car():    #20200929
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

# class Battery():
#     """一次模拟电动汽车电瓶的简单尝试"""
#     def __init__(self, bettery_size=70):
#         """初始化电瓶的属性"""
#         self.bettery_size = bettery_size
#     def describe_battery(self):
#         """打印一条描述电瓶容易的消息"""
#         print("This car has a " + str(self.bettery_size) + "-kwh battery.")
#     def get_range(self):
#         """打印一条消息，指出电瓶的续航里程"""
#         if self.bettery_size == 70:
#             range = 240
#         elif self.bettery_size == 85:
#             range = 270
#         message = "This car can go approximately " + str(range)
#         message += " miles on full charge."
#         print(message)

# class ElectricCar(Car):
#     """电动汽车的独特之处"""
#     def __init__(self, make, model, year):
#         """初始化父类的属性"""
#         super().__init__(make, model, year) #特殊函数 关联父类  父类也叫超类 superclass
#         self.bettery = Battery() #将类当个值使用，传递进来

# my_tesla = ElectricCar('tesla', 'modle s', 2016)
# print(my_tesla.get_descriptive_name())
# my_tesla.bettery.describe_battery()  #将类当个值使用，当值调用类里面的函数
# my_tesla.bettery.get_range()


# 9.3.6  模拟实物


# 9.4  导入类
# 9.4.1  导入单个类

# 9.4.2  在一个模块中存储多个类

# 9.4.3  从一个模块中导入多个类
# from car import Car, ElectricCar
# my_beetle = Car('volkswage', 'beetle', 2016)
# print(my_beetle.get_descriptive_name())
# my_tesla = ElectricCar('tesla', 'modle s', 2016)
# print(my_tesla.get_descriptive_name())

# 9.4.4  导入整个模块
# import car
# my_beetle = car.Car('volkswage', 'beetle', 2016)
# print(my_beetle.get_descriptive_name())
# my_tesla = car.ElectricCar('tesla', 'modle s', 2016)
# print(my_tesla.get_descriptive_name())

# 9.4.5  导入模块中的所有类   不推荐使用此方法
# from A import * 

# 9.4.6  在一个模块中导入另一个模块 祥见书页P158
# 书中排版有点颠倒！  应该先写car文件  再写electricCar文件 然后最后写main文件
# 分三个文件，两个头文件，并且一个头文件调用了另一个头文件；一个main文件调用头文件。
# main文件可以调用一个，也可以调用两个头文件。

# 9.5  Python 标准库
# 9.6  类编码风格 略过
