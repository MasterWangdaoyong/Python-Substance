# 时间：20201016
# 功能：重构：模块game_functions 12.5.1 函数check_events() 
# 重构目的：简单明了，思维清晰

import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep

def get_number_rows(ai_settings, ship_height, alien_height):
    """计算屏幕可容纳多少行外星人"""
    available_space_y = ai_settings.screen_height - (3 * alien_height) - ship_height # 用屏总高减去3个外星高度 减去飞船后的总宽
    number_rows = int(available_space_y / (2 * alien_height))  # 用得到后的总高去 得到同比高度 隔一显一行的总行数
    return number_rows

def get_number_aliens_x(ai_settings, alien_width):
    """计算每行可容纳多个少外星人"""
    available_space_x = ai_settings.screen_width - 2 * alien_width # 用屏总宽减去两侧过后的总宽
    number_aliens_x = int(available_space_x / (2 * alien_width)) # 用得到后的总宽去 得到同比宽度 隔一个显一个的总个数
    return number_aliens_x

def create_alien(ai_settings, screen, aliens, alien_number, row_number):
        """创建一个外星人并将其放在当前行"""
        alien = Alien(ai_settings, screen) #创建资源
        alien_width = alien.rect.width # 得到间个宽度 并保存下来
        alien.x = alien_width + 2 * alien_width * alien_number #位移坐标
        alien.rect.x = alien.x #把位移后的坐标赋值到 资源载体面板上
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number #位移行数生成 隔一行生成一行
        aliens.add(alien) #循环遍历生成的资源 添加进组中

def create_fleet(ai_settings, screen, ship, aliens):
    """创建外星人群"""
    # 创建一个外星人， 并计算一行可容纳多少个外星人
    # 外星人间距为外星人宽度
    alien = Alien(ai_settings, screen) # 需要知道资源宽高 先创建一个得到宽高
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height) #得到行数

    """创建第一行外星人"""
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):  #遍历总个数
            # 创建一个外星人并将其加入当前行
            create_alien(ai_settings, screen, aliens, alien_number, row_number)

def check_keydown_events(event, ai_settings, screen, ship, bullets):
    """响应按键"""
    if event.key == pygame.K_RIGHT or event.key == pygame.K_d: #方向右键监听
        ship.moving_right = True # 传递真
    elif event.key == pygame.K_LEFT or event.key == pygame.K_a: #方向左键监听
        ship.moving_left = True # 传递真
    elif event.key == pygame.K_SPACE: #空格键监听
        # 创建一颗子弹，并将其加入到bullets中
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()     
    
def fire_bullet(ai_settings, screen, ship, bullets):
    """如果还没有到达限制，就发射一颗子弹"""
    #创建新子弹，并将其加入到编组bullets中
    if len(bullets) < ai_settings.bullet_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)            

def check_keyup_events(event, ship):
    """响应松开"""
    if event.key == pygame.K_RIGHT or event.key == pygame.K_d: #方向右键监听
        ship.moving_right = False # 传递假
    elif event.key == pygame.K_LEFT or event.key == pygame.K_a: #方向左键监听
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

def update_bullets(ai_settings, screen, ship, aliens, bullets):
    bullets.update() # 遍历子弹精灵图组 并自动更新
    for bullet in bullets.copy(): # 副本中删除 删除已消失的子弹
        if bullet.rect.bottom <= 0:  # 检查位置是否已到顶部外
            bullets.remove(bullet)  # 将其从bullets中删除   
    # 检查是否有子弹击中了外星人
    # 如果是这样，就删除相应的子弹和外星人
    check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets)

def check_bullet_alien_collisions(ai_settings, screen, ship, aliens, bullets):
    """响应子弹和外星人的碰撞"""
    # 删除发生碰撞的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True) #字典中添加键－值 碰撞检测 消除资源

    if len(aliens) == 0:
    # 删除现有的所有子弹，并创建一个新的外星人群
        bullets.empty()
        create_fleet(ai_settings, screen, ship, aliens) 

def update_screen(ai_settings, screen, ship, alien, bullets):
    """更新屏幕上的图像，并切换到新屏幕"""    
    # 每次循环时都重绘屏幕
    screen.fill(ai_settings.bg_color) # 每次循环时都重绘屏幕 # 1、设置背景色
    """在飞船和外星人后面重绘所有子弹"""
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme() #渲染队列应该在背景前面,注意前后顺序 2、渲染物件 
    alien.draw(screen) #让外星人出现在屏幕布上
    pygame.display.flip() # 让最近绘制的屏幕可见   3、帧刷新     

def check_fleet_edges(ai_settings, aliens):
    """有外星人到达边缘时采取相应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break     

def change_fleet_direction(ai_settings, aliens):
    """将整群外星人下移，并改变它们的方向"""
    for alien in aliens.sprites():
         alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1    

def ship_hit(ai_settings, stats, screen, ship, aliens, bullets):
    """响应被外星人撞到的飞船"""
    if stats.ships_left > 0:
        # 将ships_left减1
        stats.ships_left -= 1
        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()
        # 创建一群新的外星人，并将飞船放到屏幕底端中央
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()    
        # 暂停
        sleep(0.5)  
    else:
        stats.game_active = False  

def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets):
    """检查是否有外星人到达了屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprite():
        if alien.rect.bottom >= screen_rect.bottom:
            # 像飞船被撞到一样的进行处理
            ship_hit(ai_settings, stats, screen, ship, alien, bullets)
            break    

def update_aliens(ai_settings, stats, screen, ship, aliens, bullets):
    """
    检查是否有外星人位于屏幕边缘，并更新整群外星人的位置
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # 检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, screen, ship, aliens, bullets)
        print("Ship hit!!!") 

    # 检查是否有外星人到达屏幕底端
    check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets)


