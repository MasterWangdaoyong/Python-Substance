# 11.1  测试函数 1/3
#20201010 

def get_formatted_name(first, middle, last): #多样变体
    """生成整洁的姓名"""
    if middle:
        full_name = first + ' ' + middle + ' ' + last
    else:
        full_name = first + ' ' + last
    
    return full_name.title()