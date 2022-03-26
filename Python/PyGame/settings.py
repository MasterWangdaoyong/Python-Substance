# 时间：20201015
# 功能：12.3.3 创建设置类

class Settings():
    """存储《外星人入侵》的所有设置的类"""
    
   
    def __init__(self):    
        """初始化游戏，静态设置"""
        
        # 屏幕设置
        self.screen_width = 1200 #屏宽
        self.screen_height = 800    #屏高
        self.bg_color = (230, 230, 230) #屏色
        
        # 飞船设置
        self.ship_speed_factor = 10 # 飞船的速度
        self.ship_limit = 3
        
        # 子弹设置
        self.bullet_speed_factor = 3 #速度
        self.bullet_width = 160  #图宽
        self.bullet_height = 15  #图高
        self.bullet_color = 60, 60, 60  #图色
        self.bullet_allowed = 3 #数量

        # 外星人设置
        self.alien_speed_factor = 0.5 
        self.fleet_drop_speed = 5
        # fleet_direction 为1表示向右移，为－1表示向左移
        self.fleet_direction = 1

        # 以什么样的速度加快游戏节奏
        self.speedup_scale = 3
        self.score_scale = 1.5  #将分数纳入到速度控制里
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化游戏，动态属性设置"""
        self.ship_speed_factor = 1
        self.bullet_speed_factor = 3
        self.alien_speed_factor = 1

        # fleet_direction为1表示向右；为-1表示向左
        self.fleet_direction = 1

        # 记分：外星人一个多少
        self.alien_points = 50

    def increase_speed(self):
        """提高速度设置和外星人点数"""
        self.ship_speed_factor *= self.speedup_scale
        self.bullet_speed_factor *= self.speedup_scale
        self.alien_speed_factor *= self.speedup_scale        

        self.alien_points = int(self.alien_points * self.score_scale)
        print(self.alien_points)

        
