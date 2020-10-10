# 11.2  测试类 3/3
#20201010 

import unittest
from survey import AnonymousSurvey

class TextAnonymousSurvey(unittest.TestCase):
    """针对AnonymousSurvey类的测试"""

    def setUp(self):  #测试setUp方法
        """创建一个调查对象和一组答案，供使用的测试方法使用"""
        question = "what language did you first learn to speak?"
        self.my_survey = AnonymousSurvey(question) #创建对象
        self.responses = ['English', 'Spanish', 'Mandarin'] #创建答案列表

    def test_store_sigle_response(self):
        """测试单个答案会被妥善地存储"""        
        self.my_survey.store_response(self.responses[0])
        self.assertIn(self.responses[0], self.my_survey.responses) #测试English是否在my_survey.responses里面

    def test_store_three_response(self):
        """测试三个答案会被妥善地存储"""
        for response in self.responses:
            self.my_survey.store_response(response)
        for response in self.responses:
            self.assertIn(response, self.my_survey.responses) #测试English是否在my_survey.responses里面
        
unittest.main()