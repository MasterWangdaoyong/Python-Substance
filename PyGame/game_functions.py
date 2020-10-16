# 时间：20201016
# 功能：重构：模块game_functions 12.5.1 函数check_events() 
# 重构目的：简单明了，思维清晰

import sys
import pygame


def check_events(ship):
    """响应按键和鼠标事件"""
    for event in pygame.event.get(): #次循环 监视键盘和鼠标事件
        if event.type == pygame.QUIT:   #判断事件
            sys.exit()  #系统退出
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT: #向右移动飞船
                ship.rect.centerx += 10 #数值大些明显点
            

def update_screen(ai_settings, screen, ship):
    """更新屏幕上的图像，并切换到新屏幕"""
    # 每次循环时都重绘屏幕
    screen.fill(ai_settings.bg_color) # 每次循环时都重绘屏幕 # 1设置背景色
    ship.blitme()  #渲染队列应该在背景前面,注意前后顺序 2渲染物件 
    pygame.display.flip() # 让最近绘制的屏幕可见   3帧刷新     