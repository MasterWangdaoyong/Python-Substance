#lerar 3.3 20200703
# cars = ["bmw", "audi", "toyota", "subaru"]   #前提条件，注意字母大小写时的混搭
# cars.sort()  #对列表永久性修改顺序，按字母排序
# print(cars)
# cars.sort(reverse = True) #逆向排序，永久性的修改
# print(cars)

# #learn 3.3.2  
# print("Here is the original list:")
# print(cars)
# print("\nHere is the sorted list:")
# print(sorted(cars))  #临时按字母排序，不对原始数据修改
# print("\nHere is the original list again:")
# print(cars)

# #learn 3.3.3 倒着打印列表
# print(cars)
# cars.reverse()  #永久性的反转排列顺序，不是按字母反转；如果需要还原排列顺序，只需要再次调用reverse()
# print(cars)

# #learn 3.3.4 确定列表的长度
# len(cars) #终端命令，非文件内的代码

#learn 3.4 使用列表时避免索引错误 
# print(cars[4]) #跟C++ 一样开始为0
# print(cars[-1])  #打印倒数第一个
# abc = []
# print(abc[-1])   #列表为空时，不能使用倒数方法