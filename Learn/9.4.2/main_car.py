# 9.4.2 b   20200929 在一个模块中存储多个类
from car import ElectricCar

my_tesla = ElectricCar('tesla', 'modle s', 2016)
print(my_tesla.get_descriptive_name())
my_tesla.bettery.describe_battery()  
my_tesla.bettery.get_range()