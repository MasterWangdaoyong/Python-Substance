# 时间：20201015
# 功能：12.3.1 创建Pygame窗口以及响应用户输入
# Main function

import sys
import pygame
from settings import Settings
from ship import Ship

def run_game():
    
    pygame.init() # 初始化游戏并创建一个屏幕对象
    ai_settings = Settings() #初始化设置 函数调取
    screen = pygame.display.set_mode((ai_settings.screen_width, 
                                    ai_settings.screen_height)) #面布大小
    pygame.display.set_caption("Alien Invasion") #名称

    # 创建一艘飞船
    ship = Ship(screen)
    
    while True:  # 游戏主循环
        
        for event in pygame.event.get():  #次循环 监视键盘和鼠标事件
            if event.type == pygame.QUIT: #判断事件
                sys.exit()  #系统退出
        
        screen.fill(ai_settings.bg_color) # 每次循环时都重绘屏幕 # 设置背景色
        ship.blitme() #渲染队列应该在前面 背景前
        pygame.display.flip()  # 让最近绘制的屏幕可见

run_game()
