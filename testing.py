from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar

window.vsync = False
app= Ursina()
Sky()

class Player(Entity):
    def __init__(self, **kwargs):
        self.controller = FirstPersonController(**kwargs)
        super().__init__(parent=self.controller)
        self.health = 100
        self.health_bar = HealthBar(bar_color=color.lime.tint(-.25), roundness=.5, max_value=100, value=100, scale=(.25,.02), position=(-0.85,-0.45))

        self.gun = Entity(parent=self.controller.camera_pivot,
                               scale=0.1,
                               position=Vec3(1,-1,1.5),
                               rotation=Vec3(0,170,0),
                               model='scifi_gun.obj',
                               color=color.yellow,
                               visible= False)
        
        self.knife = Entity(parent=self.controller.camera_pivot,
                               scale=0.1,
                               position=Vec3(1,-0.5,1.5),
                               rotation=Vec3(60,-10,90),
                               model='knife.obj',
                               color=color.gray,
                               visible= False)
        
        self.weapons = [self.gun,self.knife]
        self.current_weapon = 0
        self.switch_weapon()

    def switch_weapon(self):
        for i,v in enumerate(self.weapons):
            if i == self.current_weapon:
                v.visible = True
            else:
                v.visible = False
    
    def input(self,key):
        try:
            self.current_weapon = int(key) - 1
            self.switch_weapon()
        except ValueError:
            pass

        if key == 'scroll up':
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
            self.switch_weapon()
        
        if key == 'scroll down':
            self.current_weapon = (self.current_weapon - 1) % len(self.weapons)
            self.switch_weapon()
        
        if key == 'left mouse down' and self.current_weapon == 0:
            Bullet(model='sphere',
                   color=color.black,
                   scale=0.15,
                   position=self.controller.camera_pivot.world_position,
                   rotation=self.controller.camera_pivot.world_rotation)
        
        if key == 'right mouse down' and self.current_weapon == 0:
            camera.fov = 30
        elif key == 'right mouse up' and self.current_weapon == 0:
            camera.fov = 90

        if key == 'left mouse down' and self.current_weapon == 1:  # Knife is weapon 1
            self.slash()

        if key == 'escape':
            mouse.locked = not mouse.locked

    def update(self):
        self.controller.camera_pivot.y = 2 - held_keys['left control']

    def slash(self):
        if not hasattr(self, 'knife_cooldown'):
            self.knife_cooldown = 0
        if time.time() - self.knife_cooldown < 0.5:
            return  # Cooldown between slashes

        self.knife_cooldown = time.time()

    # Basic forward slash animation (optional visual)
        knife = self.knife
        knife.animate_rotation_x(knife.rotation_x - 9000, duration=0.2)
        knife.animate_rotation_x(knife.rotation_x - 9000, duration=0.1, delay=0.1)

    # Melee hit detection
        hit = raycast(self.controller.camera_pivot.world_position, self.controller.forward, distance=2)
        if hit.hit:
            print(f"Knife hit: {hit.entity}")

            if hasattr(hit.entity, 'health'):
                hit.entity.health -= 75  # Big damage for melee
                print(f"Enemy health: {hit.entity.health}")

                if hit.entity.health <= 0:
                    destroy(hit.entity)

    def take_damage(self, amount):
        self.health -= amount
        self.health = max(self.health, 0)
        self.health_bar.value = self.health
        print(f"Player health: {self.health}")

        if self.health <= 0:
            self.die()

    def die(self):
        print("You died!")
        application.pause()  # Freeze the game
        death_text = Text("YOU DIED", origin=(0,0), scale=3, color=color.red)

class Bullet(Entity):
    def __init__(self, speed=250, lifetime=10, direction=camera.forward.normalized(),**kwargs):
        super().__init__(**kwargs)
        self.speed = speed
        self.lifetime = lifetime
        self.direction = direction
        self.origin = Vec3(-1.5,1,0)
        self.start = time.time()
        self.look_at(camera.forward * 5000)
        self.world_parent = scene
    
    def update(self):
        ray = raycast(self.world_position, self.forward, distance=self.speed*time.dt)
        if not ray.hit and time.time() - self.start < self.lifetime:
            self.world_position += self.forward * self.speed * time.dt

        if ray.hit:
            if hasattr(ray.entity, 'is_enemy') and ray.entity.is_enemy:
                ray.entity.health -= 50
                print(f"Enemy hit! Health: {ray.entity.health}")
            if ray.entity.health <= 0:
                destroy(ray.entity)
            destroy(self)

class Enemy(Entity):
    def __init__(self, position, player, health=150):
        super().__init__(model='cube', color=color.red, scale_x=1, scale_y=5, scale_z=1, position=position, collider='box')
        self.speed = 2
        self.is_enemy = True
        self.health = health
        self.player = player  # Make the player recogniseable
        self.add_script(SmoothFollow(target=player.controller, speed=0.5))
        self.damage_cooldown = 1.0  # seconds between hits
        self.time_since_last_hit = 0.0
    
    def update(self):
        # Update timer
        self.time_since_last_hit += time.dt

        # Check collision with player
        if self.intersects(self.player.controller).hit:
            if self.time_since_last_hit >= self.damage_cooldown:
                self.player.take_damage(10)
                self.player.health -= 10  # Deal 10 damage
                self.time_since_last_hit = 0

class Map(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.health = float('inf')  # Infinite health
        self.is_map = True  # Tag to identify map objects

player = Player()

ground = Map(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='grass', texture_scale=(500,500), collider='box')
border_one = Map(model='cube', scale=(100, 5, 0.1), position=(50, 2.5, 0), rotation=(0,90,0), collider='box', texture='grass')
border_two = Map(model='cube', scale=(100, 5, 1), position=(0, 2.5, 50), rotation=(0,0,0), collider='box', texture='grass')
border_three = Map(model='cube', scale=(1, 5, 100), position=(0, 2.5, -50), rotation=(0,90,0), collider='box', texture='grass')
border_four = Map(model='cube', scale=(1, 5, 100), position=(-50, 2.5, 0), rotation=(0,0,0), collider='box', texture='grass')

round_number = 1
enemy_list = []
wave_cleared = False

wave_text = Text(text=f'Round: {round_number}', position=(-0, 0.45), scale=1, origin=(0,0), background=True)

def spawn_wave():
    global enemy_list, round_number, wave_cleared
    print(f"Spawning wave {round_number}")
    enemy_list = []
    wave_cleared = False

    for _ in range(round_number * 2):  # Increase number of enemies each wave
        pos = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))
        e = Enemy(position=pos, player=player)
        enemy_list.append(e)

    wave_text.text = f'Round: {round_number}'

def update():
    global wave_cleared

    player.update()
    # Update enemies
    for bullet in scene.entities:
        if isinstance(bullet, Bullet):
            bullet.update()

    for e in enemy_list[:]:  # Copy the list to avoid iteration issues
        if e.health <= 0:
            destroy(e)
            enemy_list.remove(e)

    # Check for end of wave
    if len(enemy_list) == 0 and not wave_cleared:
        wave_cleared = True
        invoke(start_next_wave, delay=3)  # Delay before next wave

def start_next_wave():
    global round_number
    round_number += 1
    spawn_wave()

spawn_wave()
app.run()