#20201009  第10章 第四节
# 10.4.1  A 使用 json.dump()
import json

numbers = [2,3,4,55,7,9]
filename = 'F:/Main_Project/Python/Learn/10.4.1/number.json'
with open(filename, 'w') as fobj:
    json.dump(numbers, fobj) #前参是需要写入的数值  后参是对象文件名、类型、路径