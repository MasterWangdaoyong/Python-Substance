#20201009  第10章 第四节
# 10.4.1  B 使用 json.load()
import json 

filename = 'F:/Main_Project/Python/Learn/10.4.1/number.json'
with open(filename) as fobj:
    number = json.load(fobj)
print(number)