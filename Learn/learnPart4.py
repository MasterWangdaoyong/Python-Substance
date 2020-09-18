#learn 4 操作列表

#learn 4.1遍历整个列表    20200727
# for 循环
# magicians = ["alice", 'david', 'carolina']
# for x in magicians:   #1声明一个临时变量，指出在哪个空间内
#     print(x)          #2打印

#4.1.1  # 描述性命名变量名称很重要。
# for dog in dogs:
#     print(dog)
# for cat in cats:
#     print(cat)
# for item in list_of_items:
#     print(item)


#4.1.2  for 循环的更多操作
# magicians = ['alice', 'david', 'carolina']
# for magician in magicians:
#     print(magician.title() + ", that was a great trick!")   #字符串拼接
#     print("I can't wait to see your next trick, " + magician.title() + ".\n")   #字符串拼接

# 4.1.3   for 循环结束后执行其他操作
# magicians = ['alice', 'david', 'carolina']
# for magician in magicians:
#     print(magician.title() + ", that was a great trick!")   #字符串拼接
#     print("I can't wait to see your next trick, " + magician.title() + ".\n")   #字符串拼接
# print('Thank you, everyone, That was a great magic show!')   #无缩进，所以不在for循环内。只打印一次

# 4.1.2   for 循环避免缩进错误
# 4.2.1 忘记缩进
# magicians = ['alice', 'david', 'carolina']
# for magician in magicians:
# print(magician)

# 4.2.2   忘记缩进额外的代码行
# magicians = ['alice', 'david', 'carolina']
# for magician in magicians:
#     print(magician.title() + ", that was a great trick!")
# print("I can't wait to see your next trick, " + magician.title() + ".\n")  #结果不是想要的

# 4.2.3   不必要的缩进
# message = "Hello Python world"
#     print(message)      #只有在 for 循环时才用缩进

# 4.2.4   循环后不必要的缩进
# magicians = ['alice', 'david', 'carolina']
# for magician in magicians:
#     print(magician.title() + ", that was a great trick!")   #字符串拼接
#     print("I can't wait to see your next trick, " + magician.title() + ".\n")   #字符串拼接

#     print('Thank you, everyone, That was a great magic show!')   #循环后不必要的缩进，变成了 for 循环下的功能

# 4.2.5   遗漏了冒号
# magicians = ['alice', 'david', 'carolina']
# for magician in magicians  #遗漏了冒号
#     print(magician)

# 4.3     创建数字列表
# 4.3.1   使用函数range()
# for value in range(1, 5):
#     print(value)
# for value2 in range(1, 6):
#     print(value2)

# 4.3.2   使用range() 创建数字列表
# number = list(range(1, 6))  
# print(number)

# number = list(range(1, 10, 2))  #索引 内存位置 + 2步长
# print(number)

# squares = []    #创建空列表
# for value in range(1,11):     #循环注入
#     square = value **2        #乘2次方，并赋值给变量
#     squares.append(square)    #添加到尾
# print(squares)                #打印列表

# squares = []    #创建空列表
# for value in range(1,11):     #循环注入
#     squares.append(value **2) #可直接赋值到尾
# print(squares)                #打印列表

# 4.3.4   列表解析
# squares = [value**2 for value in range(1,11)]
# # 变量名 ＝ 方括号 算法 for循环没冒号
# print(squares)

# 4.4     使用列表的一部分
# 4.4.1   切片
# players = ['charles', 'martina', 'michael', 'florence', 'eli']
# print(players[0:3])   #0到第三个
# print(players[1:4])   #1到第4个
# print(players[:4])    #没有指定所以从头开始，到第4个
# print(players[2:])    #没有指定结尾所以到末尾
# print(players[-3:])   #指定最后的三个，结束至最后尾

# 4.4.2   遍历切片   字符串组遍历
# players = ['charles', 'martina', 'michael', 'florence', 'eli']
# print("Here are the first three palyers on my team.")
# for play in players[:3]:
#     print(play.title())

# 4.4.3   复制列表
# my_foods = ['pizza', 'falafel', 'carrot cake']
# friend_foods = my_foods[:]      #复制列表，重赋值
# print("My favorite foods are:")
# print(my_foods)
# print("\nMy friend's favorite foods are:")
# print(friend_foods)

# my_foods = ['pizza', 'falafel', 'carrot cake']
# friend_foods = my_foods[:]      #复制列表，重赋值
# my_foods.append('cannoli')      #在数组尾，加上字符串
# friend_foods.append('ice cream')    #在数组尾，加上字符串
# print("My favorite foods are:")
# print(my_foods)
# print("\nMy friend's favorite foods are:")
# print(friend_foods)

# my_foods = ['pizza', 'falafel', 'carrot cake']
# friend_foods = my_foods   #[：]   #没有使用切片复制列表，重赋值。所以只能得到一个数组，而不是两个数组
# my_foods.append('cannoli')      #在数组尾，加上字符串
# friend_foods.append('ice cream')    #在数组尾，加上字符串
# print("My favorite foods are:")
# print(my_foods)
# print("\nMy friend's favorite foods are:")
# print(friend_foods)

# 4.5     元组    #类似const值    #不可变的
# 4.5.1   定义元组
# dimensions = (200, 50)
# print(dimensions[0])
# print(dimensions[1])
# dimensions[0] = 300   #不能修改元组数据，这样是错误的

# 4.5.2   遍历元组中的所有值
# dimensions = (200, 50)
# for dim in dimensions:
#     print(dim)

# 4.5.3   修改元组变量
# dimensions = (200, 50)      
# print("Original dimensions:")
# for dimension in dimensions:
#     print(dimension)
# dimensions = (400, 350)     #这样处理是正确的
# print("\nModified dimensions:")
# for dimension in dimensions:
#     print(dimension)

# 4.6     设置代码格式
# 4.7     小结