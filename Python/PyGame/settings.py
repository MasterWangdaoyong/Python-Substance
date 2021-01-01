# 时间：20201015
# 功能：12.3.3 创建设置类

class Settings():
    """存储《外星人入侵》的所有设置的类"""
    
   
    def __init__(self):    
        """初始化游戏的设置"""
        
        # 屏幕设置
        self.screen_width = 1200 #屏宽
        self.screen_height = 800    #屏高
        self.bg_color = (230, 230, 230) #屏色
        
        # 飞船设置
        self.ship_speed_factor = 1.5 # 飞船的速度
        self.ship_limit = 3
        
        # 子弹设置
        self.bullet_speed_factor = 3 #速度
        self.bullet_width = 300  #图宽
        self.bullet_height = 15  #图高
        self.bullet_color = 60, 60, 60  #图色
        self.bullet_allowed = 3 #数量

        # 外星人设置
        self.alien_speed_factor = 0.5 
        self.fleet_drop_speed = 10
        # fleet_direction 为1表示向右移，为－1表示向左移
        self.fleet_direction = 1

        
