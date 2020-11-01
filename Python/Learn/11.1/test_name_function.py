# 11.1  测试函数 3/3
#20201010 

import unittest
#导入模块
from name_function import get_formatted_name
#导入函数

class NameTestCase(unittest.TestCase): #创建类 继承类unittest.TestCase 必须的
    """测试name_function.py"""

    def test_first_last_name(self):
        """能够正确的处理像Janis Joplin这样的姓名吗?"""
        formatted_name = get_formatted_name('janis', 'joplin')
        self.assertEqual(formatted_name, 'Janis Joplin') #判断是否相等 必须的
    
    def test_first_last_middle_name(self):
        """能够正确的处理像Janis middle Joplin这样的姓名吗?"""
        formatted_name = get_formatted_name('janis', 'middle' ,'joplin')
        self.assertEqual(formatted_name, 'Janis Middle Joplin') #判断是否相等 必须的

unittest.main()  #运行文件中的测试 