# 时间：20201015
# 功能：12.3.3 创建设置类

class Settings():
    """存储《外星人入侵》的所有设置的类"""
    
   
    def __init__(self):    
        # 屏幕设置
        """初始化游戏的设置"""
        self.screen_width = 1200 #屏宽
        self.screen_height = 800    #屏高
        self.bg_color = (230, 230, 230) #屏色
        
        self.ship_speed_factor = 1.5 # 飞船的速度
        
        # 子弹设置
        self.bullet_speed_factor = 1 #速度
        self.bullet_width = 3   #图宽
        self.bullet_height = 15  #图高
        self.bullet_color = 60, 60, 60  #图色