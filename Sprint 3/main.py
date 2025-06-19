from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar

window.vsync = False
app= Ursina(borderless=False)
Sky()

class Player(Entity):
    def __init__(self, **kwargs):
        self.controller = FirstPersonController(**kwargs)
        super().__init__(parent=self.controller)
        self.collider = CapsuleCollider(self, center=Vec3(0.5,2.5,0.5), height=5, radius=0.25)
        self.health = 100
        self.health_bar = HealthBar(bar_color=color.lime.tint(-.25), roundness=0.5, max_value=100, value=self.health, scale=(.25,.02), position=(-0.85,-0.45))

        self.gun = Entity(parent=self.controller.camera_pivot,
                               scale=0.1,
                               position=Vec3(1,-1,1.5),
                               rotation=Vec3(0,170,0),
                               model='assets/scifi_gun.obj',
                               color=color.yellow,
                               visible= False)
        
        self.knife = Entity(parent=self.controller.camera_pivot,
                               scale=0.1,
                               position=Vec3(1,-0.5,1.5),
                               rotation=Vec3(60,-10,90),
                               model='assets/knife.obj',
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
        knife.animate_rotation(Vec3(60, -10, 90) + Vec3(-90, 0, 0), duration=0.1)
        knife.animate_rotation(Vec3(60, -10, 90), duration=0.1, delay=0.1)

    # Melee hit detection
        hit = raycast(self.controller.camera_pivot.world_position, self.controller.forward, distance=2)
        if hit.hit:
            print(f"Knife hit: {hit.entity}")

            if hasattr(hit.entity, 'health'):
                hit.entity.health -= 75  # Big damage for melee
                print(f"Enemy health: {hit.entity.health}")

                if hit.entity.health <= 0:
                    destroy(hit.entity)

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
    def __init__(self, position, player, health=150, damage=10):
        super().__init__(model='cube', color=color.blue, scale_x=1, scale_y=5, scale_z=1, position=position, collider='box')
        self.speed = 2
        self.is_enemy = True
        self.health = health
        self.player = player
        self.damage = damage  # Make the player recogniseable
        self.add_script(SmoothFollow(target=player.controller, speed=0.5))
        self.damage_cooldown = 1.0  # seconds between hits
        self.time_since_last_hit = 0.0
        self.collider = BoxCollider(self, center=Vec3(0.25,1.25,0.25), size=Vec3(1,5,1))
    
    def prevent_merging(self):
        for other in enemy_list:
            if other == self:
                continue
            if self.intersects(other).hit:
                # Push the enemy away slightly
                push_dir = (self.position - other.position).normalized()
                self.position += push_dir * time.dt * 5  # Tune this push strength

    def update(self):
        self.time_since_last_hit += time.dt
        self.prevent_merging()

        # Check distance to player instead of collider comparison
        if distance(self.world_position, self.player.world_position) < 2:
            if self.time_since_last_hit >= self.damage_cooldown:
                self.player.health -= self.damage
                self.player.health_bar.value = self.player.health
                print(f'Player Health: {self.player.health}')
                self.time_since_last_hit = 0

                if self.player.health <= 0:
                    self.player.health = 0
                    print("player died")
                    death_screen = Text(text='YOU DIED', color=color.red, position=(0,0), scale=9, origin=(0,0), background=True)
    
    def spawn_wave():
        global enemy_list, round_number, wave_cleared

        print(f"Spawning wave {round_number}")
        enemy_list = []
        wave_cleared = False

        for _ in range(round_number * 2):  # Increase number of enemies each wave
            pos = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))
            enemy = Enemy(position=pos, player=player)
            enemy_list.append(enemy)

        wave_text.text = f'Wave: {round_number}'

    def system():
        if not game_started:
            return  # Don't run the game until user presses Play

        global wave_cleared

        player.update()
        # Update enemies
        for bullet in scene.entities:
            if isinstance(bullet, Bullet):
                bullet.update()

        for enemy in enemy_list[:]:  # Copy the list to avoid iteration issues
            if enemy.health <= 0:
                destroy(enemy)
                enemy_list.remove(enemy)

        # Check for end of wave
        if len(enemy_list) == 0 and not wave_cleared and player.health >0 :
            wave_cleared = True
            invoke(start_next_wave, delay=3)  # Delay before next wave

    def start_next_wave():
        global round_number
        if round_number < 10:
            round_number += 1
            spawn_wave()
        if round_number == 10:
            print("yay")


                    
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

game_started = False

round_number = 0
enemy_list = []
wave_cleared = False

def title_screen():
    # Title Text
    title_text = Text(text="Sahur Shooter", color=color.white, scale=3, origin=(0,0), y=0.35, z=0.1, background=True)

    # Play Button
    play_button = Button(text='Play', color=color.green, scale=(0.3, 0.1), y=-0.2)
    
    # Quit Button
    quit_button = Button(text='Quit', color=color.red, scale=(0.3, 0.1), y=-0.4)

    # Background UI
    title_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)

    mouse.locked = False
    camera.fov = 90
    camera.position = (0, 0, -20)  # Optional: move camera away from gameplay view
    camera.rotation = (0, 0, 0)

    def start_game():
        global game_started, play_again

        title_bg.disable()
        title_text.disable()
        play_button.disable()
        quit_button.disable()
        game_started = True
        mouse.locked = True
        camera.position = (0,0,0)
        update()

    def quit_game():
        app.userExit()

    play_button.on_click = start_game
    quit_button.on_click = quit_game

wave_text = Text(text=f'Wave: {round_number}', position=(-0, 0.45), scale=1, origin=(0,0), background=True)

def spawn_wave():
    global enemy_list, round_number, wave_cleared

    print(f"Spawning wave {round_number}")
    enemy_list = []
    wave_cleared = False

    for _ in range(round_number * 2):  # Increase number of enemies each wave
        pos = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))
        enemy = Enemy(position=pos, player=player)
        enemy_list.append(enemy)

    wave_text.text = f'Wave: {round_number}'

def update():
    if not game_started:
        return  # Don't run the game until user presses Play

    global wave_cleared

    player.update()
        # Update enemies
    for bullet in scene.entities:
        if isinstance(bullet, Bullet):
            bullet.update()

    for enemy in enemy_list[:]:  # Copy the list to avoid iteration issues
        if enemy.health <= 0:
            destroy(enemy)
            enemy_list.remove(enemy)

        # Check for end of wave
    if len(enemy_list) == 0 and not wave_cleared and player.health >0 :
        wave_cleared = True
        invoke(start_next_wave, delay=3)  # Delay before next wave

def start_next_wave():
    global round_number
    if round_number < 10:
        round_number += 1
        spawn_wave()
    if round_number == 10:
        print("yay")

title_screen()
app.run()