# 9.4.2 a   20200929
"""一个可用于表示汽车的类"""
class Car():    #20200929
    def __init__(self, make, model, year):
        """初始化描述汽车的属性"""
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0   #可以理解成私有变量    
    def get_descriptive_name(self):
        """返回整洁的描述性信息"""
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()    
    def read_odometer(self):        #调用了私用变量
        """打印一条指出汽车里程的消息"""
        print("This car has " + str(self.odometer_reading) + " miles on it.")
    def updata_odometer(self, mileage):
        if mileage >= self.odometer_reading:
            self.odometer_reading = mileage
        else:
            print("You can't roll back an odometer!")
    def increment_odometer(self, miles):
        """将里程表读数增加指定的量"""
        self.odometer_reading += miles

class Battery():
    """一次模拟电动汽车电瓶的简单尝试"""
    def __init__(self, bettery_size=70):
        """初始化电瓶的属性"""
        self.bettery_size = bettery_size
    def describe_battery(self):
        """打印一条描述电瓶容易的消息"""
        print("This car has a " + str(self.bettery_size) + "-kwh battery.")
    def get_range(self):
        """打印一条消息，指出电瓶的续航里程"""
        if self.bettery_size == 70:
            range = 240
        elif self.bettery_size == 85:
            range = 270
        message = "This car can go approximately " + str(range)
        message += " miles on full charge."
        print(message)

class ElectricCar(Car):
    """电动汽车的独特之处"""
    def __init__(self, make, model, year):
        """初始化父类的属性"""
        super().__init__(make, model, year) #特殊函数 关联父类  父类也叫超类 superclass
        self.bettery = Battery() #将类当个值使用，传递进来