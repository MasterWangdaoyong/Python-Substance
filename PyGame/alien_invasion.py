# 时间：20201015
# 功能：12.3.1 创建Pygame窗口以及响应用户输入
# Main function

import sys
import pygame
from settings import Settings
from ship import Ship
import game_functions as gf
from pygame.sprite import Group

def run_game():
    
    pygame.init() # 初始化游戏并创建一个屏幕对象
    ai_settings = Settings() #初始化屏幕设置 
    screen = pygame.display.set_mode((ai_settings.screen_width, 
                                    ai_settings.screen_height)) #画布设置，面布大小

    pygame.display.set_caption("Alien Invasion") #项目名称   

    ship = Ship(ai_settings, screen) # 新画布上创建飞船
    bullets = Group() # 实例精灵图组
    
    while True:  # 游戏主循环
        gf.check_events(ai_settings, screen, ship, bullets) # 事件循环 侦探
        ship.update() # 物件循环
        bullets.update()    # 遍历精灵图组 并自动更新
        gf.update_screen(ai_settings, screen, ship, bullets)  # 渲染管线设置 帧循环

run_game()
