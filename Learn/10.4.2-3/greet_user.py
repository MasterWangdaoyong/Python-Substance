#20201009  第10章 第四节
# 10.4.2 B 保存和读取用户生成的数据

import json

filename = 'F:/Main_Project/Python/Learn/10.4.2-3/username.json'
with open(filename) as fobj:
    username = json.load(fobj)
    print("Welcome back, " + username + '! ')