# 时间：20201015
# 功能：12.3.1 创建Pygame窗口以及响应用户输入
# Main function

import sys
import pygame
from settings import Settings
from ship import Ship
from alien import Alien
import game_functions as gf 
from pygame.sprite import Group
from game_stats import GameStats

def run_game():
    
    pygame.init() # 初始化游戏并创建一个屏幕对象
    ai_settings = Settings() #初始化设置 
    screen = pygame.display.set_mode((ai_settings.screen_width, 
                                    ai_settings.screen_height)) #画布设置，面布大小

    pygame.display.set_caption("Alien Invasion") #项目名称
    stats = GameStats(ai_settings)   #创建一个用于存储游戏统计信息的实例

    ship = Ship(ai_settings, screen) # 新画布上创建飞船
    bullets = Group() # 实例精灵图组
    aliens = Group() # 画布上创建外星人
    gf.create_fleet(ai_settings, screen, ship, aliens) # 创建外星人群
     
    while True:  # 游戏主循环
        gf.check_events(ai_settings, screen, ship, bullets) # 事件循环 侦探
        if stats.game_active:
            ship.update() # 物件循环
            gf.update_bullets(ai_settings, screen, ship, aliens, bullets) # 子弹模块
            print(len(bullets))  # 游戏运行时打印消息（在控制台内）子弹循环测试
            gf.update_aliens(ai_settings, stats, screen, ship, aliens, bullets) #外星人模块      
        gf.update_screen(ai_settings, screen, ship, aliens, bullets)  # 渲染管线设置 帧循环
run_game()
