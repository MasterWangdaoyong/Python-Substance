

# https://www.jianshu.com/p/91844c5bca78
# https://www.jianshu.com/p/a54a5eab7e17
# https://www.liaoxuefeng.com/wiki/1016959663602400/1017786914566560


atotal = 32  # 总文章数量
cookiestr = ''  # cookie全局变量


def genInfoStr():  # 拼接信息字符串
    global atotal
    global afini
    infoStr = '正在获取('+str(afini)+'/'+str(atotal)+'):'
    per = int(atotal/15)
    fi = int(afini/per)
    for _ in range(fi):
        infoStr += '■'
    for _ in range(15-fi):
        infoStr += '□'
    return infoStr


def getAll(cookieStr):  # 获取全部
    t = Thread(target=getArticles, args=(cookiestr,))  # 多线程，避免锁死界面
    t.start()
    return 'getAll OK!'
