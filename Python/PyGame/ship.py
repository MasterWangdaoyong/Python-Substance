# 时间：20201016
# 功能：12.4.1 创建Ship类

import pygame

class Ship():

    def __init__(self, ai_settings, screen):
        """初始化飞船并设置其初始位置"""
        
        self.screen = screen
        self.ai_settings = ai_settings
        # 加载飞船图像并获取其外接矩形
        self.image = pygame.image.load(r'F:\Main_Project\Python\PyGame\images\ship.bmp') #加载图像
        # 如果报错，需要给绝对路径
        self.rect = self.image.get_rect()   #获取贴图属性 矩形高效
        self.screen_rect = screen.get_rect()    #获取画布属性

        # 将每艘新飞船放在屏幕底部中央
        self.rect.centerx = self.screen_rect.centerx #中心X坐标
        self.rect.bottom = self.screen_rect.bottom #矩形底部属性
        self.center = float(self.rect.centerx) # 在飞船的属性center中存储小数值

        self.moving_right = False #右移动标志
        self.moving_left = False #左移动

    def update(self):
        """根据移动标志调整飞船的位置"""
        if self.moving_right and self.rect.right < self.screen_rect.right: # 限制在屏幕范围内
            self.center += self.ai_settings.ship_speed_factor  #向右移动
        if self.moving_left and self.rect.left > 0: # 限制在屏幕范围内
            self.center -= self.ai_settings.ship_speed_factor  #向右移动
        
        self.rect.centerx = self.center #根据self.center更新rect对象      
    
    def blitme(self):
        """在指定位置绘制飞船"""
        self.screen.blit(self.image, self.rect) #根据self.rect 指定的位置将图像绘制到屏幕上
        #画布声明 再把图片信息采样到画布上