from ursina import *
from ursina.prefabs.health_bar import HealthBar
from enemy import *

# Boss class definition
boss_health_bar = None
class Boss(Enemy):
    def __init__(self, position, player):
        super().__init__(position=position, player=player, health=1000, damage=30)
        self.model = 'assets/sahur.obj'
        self.texture = 'assets/sahur_skin.png'
        self.scale_x = 3
        self.scale_y = 10
        self.scale_z = 3
        self.is_boss = True
        global boss_health_bar
        boss_health_bar = HealthBar(bar_color=color.red, roundness=0.5, max_value=1000, value=1000, scale=(1,0.01), position=(-0.50,0.40))

    def update(self):
        if globals().get('paused', False):
            return
        if self.y < 1:
            self.y = 1
        direction = self.player.world_position - self.world_position
        direction.y = 0
        target_angle = math.degrees(math.atan2(direction.x, direction.z))
        self.rotation_y = lerp(self.rotation_y, target_angle, 6 * time.dt)
        super().update()
        global boss_health_bar
        if boss_health_bar:
            boss_health_bar.value = self.health
        if self.health <= 0 and boss_health_bar:
            boss_health_bar.disable()
            boss_health_bar = None