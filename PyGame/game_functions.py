# 时间：20201016
# 功能：重构：模块game_functions 12.5.1 函数check_events() 
# 重构目的：简单明了，思维清晰

import sys
import pygame
from bullet import Bullet

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT: #方向右键监听
        ship.moving_right = True # 传递真
    elif event.key == pygame.K_LEFT: #方向左键监听
        ship.moving_left = True # 传递真
    elif event.key == pygame.K_SPACE: #空格键监听
        # 创建一颗子弹，并将其加入到bullets中
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)

def check_keyup_events(event, ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT: #方向右键监听
        ship.moving_right = False # 传递假
    elif event.key == pygame.K_LEFT: #方向左键监听
        ship.moving_left = False # 传递假       

def check_events(ai_settings, screen, ship, bullets):
    """响应按键和鼠标事件"""
    for event in pygame.event.get(): #次循环 监视键盘和鼠标事件
        if event.type == pygame.QUIT:   #判断事件
            sys.exit()  #系统退出
        elif event.type == pygame.KEYDOWN: #按下
            check_keydown_events(event, ai_settings, screen, ship, bullets) #调用上面的函数
        elif event.type == pygame.KEYUP:    #抬起
            check_keyup_events(event, ship) #调用上面的函数  

def update_screen(ai_settings, screen, ship, bullets):
    """更新屏幕上的图像，并切换到新屏幕"""    
    # 每次循环时都重绘屏幕
    screen.fill(ai_settings.bg_color) # 每次循环时都重绘屏幕 # 1设置背景色
    """在飞船和外星人后面重绘所有子弹"""
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme() #渲染队列应该在背景前面,注意前后顺序 2渲染物件 
    pygame.display.flip() # 让最近绘制的屏幕可见   3帧刷新     
