from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
import random, time, os

# --- Globals ---
window.vsync = False
app = Ursina(borderless=False)
sky = Sky()
sky.texture = 'assets/sky'

game_started = False
round_number = 0
enemy_list = []
wave_cleared = False
paused = False
pause_entities = []
boss_health_bar = None
wake_text_disabled = True
win_screen_shown = False

# --- UI ---
wave_text = Text(text=f'Wave: {round_number}', position=(-0, 0.45), scale=1, origin=(0,0), background=True)
wake_text_disabled = True
wave_text.disable()
enemies_left_text = Text(text=f'Enemies Left: 0', position=(0.5, 0.45), scale=1, origin=(0,0), background=True)
enemies_left_text.disable()

def set_enemy_follow_enabled(enabled):
    for enemy in enemy_list:
        for script in enemy.scripts:
            if isinstance(script, SmoothFollow):
                script.enabled = enabled

def toggle_pause():
    global paused, pause_entities
    if win_screen_shown:
        return
    paused = not paused
    set_enemy_follow_enabled(not paused)
    player.controller.enabled = not paused
    if paused:
        mouse.locked = False
        pause_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=2)
        pause_text = Text(text='PAUSED', color=color.azure, scale=4, origin=(0,0), y=0.1, z=2, background=True)
        resume_button = Button(text='Resume', color=color.green, scale=(0.3, 0.1), y=-0.1, z=2)
        quit_button = Button(text='Quit', color=color.red, scale=(0.3, 0.1), y=-0.25, z=2)
        resume_button.on_click = toggle_pause
        quit_button.on_click = app.userExit
        pause_entities = [pause_bg, pause_text, resume_button, quit_button]
    else:
        for e in pause_entities:
            e.disable()
        pause_entities = []
        mouse.locked = True

# --- Entities ---
class Player(Entity):
    def __init__(self, **kwargs):
        self.controller = FirstPersonController(**kwargs)
        super().__init__(parent=self.controller)
        self.collider = CapsuleCollider(self, center=Vec3(0.5,2.5,0.5), height=5, radius=0.25)
        self.health = 100
        self.health_bar = HealthBar(bar_color=color.lime.tint(-.25), roundness=0.5, max_value=100, value=self.health, scale=(.25,.02), position=(-0.85,-0.45))
        self.gun = Entity(parent=self.controller.camera_pivot, scale=0.1, position=Vec3(1,-1,1.5), rotation=Vec3(0,170,0), model='assets/scifi_gun.obj', color=color.yellow, visible=False)
        self.knife = Entity(parent=self.controller.camera_pivot, scale=0.1, position=Vec3(1,-0.5,1.5), rotation=Vec3(60,-10,90), model='assets/knife.obj', color=color.gray, visible=False)
        self.weapons = [self.gun, self.knife]
        self.current_weapon = 0
        self.switch_weapon()
    def switch_weapon(self):
        for i, v in enumerate(self.weapons):
            v.visible = (i == self.current_weapon)
    def input(self, key):
        global paused
        if key == 'p' and not win_screen_shown:
            toggle_pause(); return
        if paused: return
        try:
            self.current_weapon = int(key) - 1
            self.switch_weapon()
        except ValueError: pass
        if key == 'scroll up':
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)
            self.switch_weapon()
        if key == 'scroll down':
            self.current_weapon = (self.current_weapon - 1) % len(self.weapons)
            self.switch_weapon()
        if key == 'left mouse down' and self.current_weapon == 0:
            # Always shoot in camera.forward direction
            muzzle_pos = self.gun.world_position
            direction = camera.forward.normalized()
            Bullet(model='sphere', color=color.black, scale=0.15, position=muzzle_pos, direction=direction)
        if key == 'right mouse down' and self.current_weapon == 0:
            camera.fov = 30
        elif key == 'right mouse up' and self.current_weapon == 0:
            camera.fov = 90
        if key == 'left mouse down' and self.current_weapon == 1:
            self.slash()
        if key == 'escape':
            mouse.locked = not mouse.locked
    def update(self):
        self.controller.speed = 10 if held_keys['shift'] else 5
        self.controller.camera_pivot.y = 2 - held_keys['left control']
    def slash(self):
        if not hasattr(self, 'knife_cooldown'):
            self.knife_cooldown = 0
        if time.time() - self.knife_cooldown < 0.5:
            return
        self.knife_cooldown = time.time()
        knife = self.knife
        knife.animate_rotation(Vec3(60, -10, 90) + Vec3(-90, 0, 0), duration=0.1)
        knife.animate_rotation(Vec3(60, -10, 90), duration=0.1, delay=0.1)
        # Distance-based melee hit detection
        for enemy in enemy_list:
            if hasattr(enemy, 'health') and distance(self.controller.camera_pivot.world_position, enemy.world_position) < 2:
                enemy.health -= 75
                if hasattr(enemy, 'is_boss') and enemy.is_boss and boss_health_bar:
                    boss_health_bar.value = enemy.health
                if enemy.health <= 0:
                    destroy(enemy)

class Bullet(Entity):
    def __init__(self, speed=500, lifetime=0.5, direction=None, **kwargs):
        if direction is None:
            direction = camera.forward.normalized()
        super().__init__(**kwargs)
        self.speed = speed
        self.lifetime = lifetime
        self.direction = direction
        self.start = time.time()
        self.look_at(camera.forward * 5000)
        self.world_parent = scene
    def update(self):
        if paused: return
        ray = raycast(self.world_position, self.forward, distance=self.speed*time.dt)
        if not ray.hit and time.time() - self.start < self.lifetime:
            self.world_position += self.forward * self.speed * time.dt
        if time.time() - self.start >= self.lifetime:
            destroy(self)
            return
        if ray.hit:
            if hasattr(ray.entity, 'is_enemy') and ray.entity.is_enemy:
                ray.entity.health -= 50
                if hasattr(ray.entity, 'is_boss') and ray.entity.is_boss and boss_health_bar:
                    boss_health_bar.value = ray.entity.health
            if hasattr(ray.entity, 'health') and ray.entity.health <= 0:
                destroy(ray.entity)
            destroy(self)

class Enemy(Entity):
    def __init__(self, position, player, health=150, damage=10):
        super().__init__(model='assets/sahur.obj', texture='assets/sahur_skin.png', scale=1, position=position, collider='box')
        self.speed = 2
        self.is_enemy = True
        self.health = health
        self.player = player
        self.damage = damage
        self.damage_cooldown = 1.0
        self.time_since_last_hit = 0.0
        self.collider = BoxCollider(self, center=Vec3(0.25,1.25,0.25), size=Vec3(1,5,1))
    def prevent_merging(self):
        for other in enemy_list:
            if other == self: continue
            if self.intersects(other).hit:
                push_dir = (self.position - other.position).normalized()
                self.position += push_dir * time.dt * 5
    def update(self):
        global paused
        if paused: return
        if self.y < 1: self.y = 1
        direction = self.player.world_position - self.world_position
        direction.y = 0
        target_angle = math.degrees(math.atan2(direction.x, direction.z))
        self.rotation_y = lerp(self.rotation_y, target_angle, 6 * time.dt)
        move_directions = [0, 45, -45, 90, -90]
        for angle in move_directions:
            rad = math.radians(angle)
            dir_vec = Vec3(
                direction.x * math.cos(rad) - direction.z * math.sin(rad),
                0,
                direction.x * math.sin(rad) + direction.z * math.cos(rad)
            ).normalized()
            move_step = dir_vec * self.speed * time.dt
            new_position = self.world_position + move_step
            blocked = False
            # Check collision with map
            for entity in scene.entities:
                if hasattr(entity, 'is_map') and entity.is_map and entity != ground:
                    old_pos = self.world_position
                    self.world_position = new_position
                    self.scale = Vec3(1,5,1)
                    if self.intersects(entity).hit:
                        blocked = True
                        self.world_position = old_pos
                        break
                    self.world_position = old_pos
            # Check collision with other enemies
            if not blocked:
                for other in enemy_list:
                    if other is not self:
                        old_pos = self.world_position
                        self.world_position = new_position
                        if self.intersects(other).hit:
                            blocked = True
                            self.world_position = old_pos
                            break
                        self.world_position = old_pos
            # Check collision with player
            if not blocked:
                old_pos = self.world_position
                self.world_position = new_position
                if self.intersects(self.player).hit:
                    blocked = True
                    self.world_position = old_pos
                else:
                    self.world_position = old_pos
            if not blocked:
                self.world_position = new_position
                break
        self.time_since_last_hit += time.dt
        self.prevent_merging()
        if distance(self.world_position, self.player.world_position) < 2:
            if self.time_since_last_hit >= self.damage_cooldown:
                self.player.health -= self.damage
                self.player.health_bar.value = self.player.health
                self.time_since_last_hit = 0
                if self.player.health <= 0:
                    self.player.health = 0
                    death_screen = Text(text='YOU DIED', color=color.red, position=(0,0), scale=9, origin=(0,0), background=True, z=3)
                    death_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)
                    player.health_bar.disable()
                    wave_text.disable()
                    enemies_left_text.disable()
                    paused = True
                    set_enemy_follow_enabled(False)
                    player.controller.enabled = False
                    mouse.locked = False

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
        if paused: return
        if self.y < 1: self.y = 1
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

class Map(Entity):
    def __init__(self, **kwargs):
        if 'texture' not in kwargs:
            kwargs['texture'] = 'grass'
        if 'model' not in kwargs:
            kwargs['model'] = 'cube'
        if 'collider' not in kwargs:
            kwargs['collider'] = 'box'
        super().__init__(**kwargs)
        self.health = float('inf')
        self.is_map = True

def find_valid_enemy_spawn_position(max_attempts=10):
    for _ in range(max_attempts):
        pos = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))
        temp_entity = Entity(position=pos, model='cube', collider='box', scale=(1,5,1), visible=False)
        collides = False
        for entity in scene.entities:
            if hasattr(entity, 'is_map') and entity.is_map and entity != ground:
                if temp_entity.intersects(entity).hit:
                    collides = True
                    break
        destroy(temp_entity)
        if not collides:
            return pos
    return None

def spawn_wave():
    global enemy_list, round_number, wave_cleared, boss_health_bar
    enemy_list = []
    wave_cleared = False
    if round_number == 10:
        pos = Vec3(0, 1, 0)
        boss = Boss(position=pos, player=player)
        enemy_list.append(boss)
    else:
        for _ in range(4 * round_number):
            pos = find_valid_enemy_spawn_position()
            if pos is not None:
                enemy = Enemy(position=pos, player=player)
                enemy_list.append(enemy)
    if paused:
        set_enemy_follow_enabled(False)
    wave_text.text = f'Wave: {round_number}'

def update():
    global paused, wave_cleared, win_screen_shown
    if not game_started or paused: return
    enemies_left_text.text = f'Enemies Left: {len(enemy_list)}'
    if not wake_text_disabled:
        enemies_left_text.enable()
    else:
        enemies_left_text.disable()
    if win_screen_shown: return
    player.update()
    for bullet in scene.entities:
        if isinstance(bullet, Bullet):
            bullet.update()
    for enemy in enemy_list[:]:
        if enemy.health <= 0:
            if hasattr(enemy, 'is_boss') and enemy.is_boss:
                global boss_health_bar
                if boss_health_bar:
                    boss_health_bar.disable()
                    boss_health_bar = None
            destroy(enemy)
            enemy_list.remove(enemy)
    if round_number == 10 and len(enemy_list) == 0 and player.health > 0:
        win_screen_shown = True
        win_text = Text(text='YOU WIN!', color=color.lime, position=(0,0), scale=9, origin=(0,0), background=True, z=0, parent=camera.ui)
        win_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)
        mouse.locked = False
        paused = True
        player.controller.enabled = False
        def wait_for_exit(key):
            if key == 'escape' or key == 'enter':
                app.userExit()
        win_text.input = wait_for_exit
        window.input = wait_for_exit
        return
    if len(enemy_list) == 0 and not wave_cleared and player.health > 0:
        wave_cleared = True
        invoke(start_next_wave, delay=3)

def start_next_wave():
    global round_number
    if round_number < 10:
        round_number += 1
        spawn_wave()
    if round_number == 10:
        print("yay")

def title_screen():
    title_text = Text(text="Sahur Shooter", color=color.white, scale=5, origin=(0,0), y=0.1, z=0.1, background=True)
    play_button = Button(text='Play', color=color.green, scale=(0.3, 0.1), x=-0.175, y=-0.25)
    quit_button = Button(text='Quit', color=color.red, scale=(0.3, 0.1), x=0.175, y=-0.25)
    title_bg_image = 'title_bg.jpg'
    if os.path.exists(title_bg_image):
        title_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.white, z=1, texture=title_bg_image)
    else:
        title_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)
    mouse.locked = False
    camera.fov = 90
    camera.position = (0, 0, -20)
    camera.rotation = (0, 0, 0)
    def start_game():
        global game_started, wake_text_disabled
        title_bg.disable()
        title_text.disable()
        play_button.disable()
        quit_button.disable()
        global round_number
        game_started = True
        round_number = 1
        mouse.locked = True
        camera.position = (0,0,0)
        player.health_bar.enable()
        wave_text.enable()
        wake_text_disabled = False
        spawn_wave()
        update()
    def quit_game():
        app.userExit()
    play_button.on_click = start_game
    quit_button.on_click = quit_game

# --- Map and Player ---
player = Player()
player.health_bar.disable()
ground = Map(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture_scale=(500,500))
border_one = Map(scale=(100, 5, 0.1), position=(50, 2.5, 0), rotation=(0,90,0))
border_two = Map(scale=(100, 5, 1), position=(0, 2.5, 50), rotation=(0,0,0))
border_three = Map(scale=(1, 5, 100), position=(0, 2.5, -50), rotation=(0,90,0))
border_four = Map(scale=(1, 5, 100), position=(-50, 2.5, 0), rotation=(0,0,0))

num_layers = 1
layer_gap = 10
min_length = 14
max_length = 34
wall_thickness = 1
for i in range(num_layers):
    t = (num_layers - 1 - i) / (num_layers - 1) if num_layers > 1 else 1
    wall_length = min_length + (max_length - min_length) * t
    offset = layer_gap * (i + 1) + wall_thickness * i
    tl_x = -50 + offset + wall_thickness/2
    tl_z = 50 - offset - wall_length/2
    Map(scale=(1, 5, wall_length), position=(tl_x, 2.5, tl_z))
    Map(scale=(wall_length, 5, 1), position=(-50 + offset + wall_length/2, 2.5, 50 - offset - wall_thickness/2))
    tr_x = 50 - offset - wall_thickness/2
    tr_z = 50 - offset - wall_length/2
    Map(scale=(1, 5, wall_length), position=(tr_x, 2.5, tr_z))
    Map(scale=(wall_length, 5, 1), position=(50 - offset - wall_length/2, 2.5, 50 - offset - wall_thickness/2))
    bl_x = -50 + offset + wall_thickness/2
    bl_z = -50 + offset + wall_length/2
    Map(scale=(1, 5, wall_length), position=(bl_x, 2.5, bl_z))
    Map(scale=(wall_length, 5, 1), position=(-50 + offset + wall_length/2, 2.5, -50 + offset + wall_thickness/2))
    br_x = 50 - offset - wall_thickness/2
    br_z = -50 + offset + wall_length/2
    Map(scale=(1, 5, wall_length), position=(br_x, 2.5, br_z))
    Map(scale=(wall_length, 5, 1), position=(50 - offset - wall_length/2, 2.5, -50 + offset + wall_thickness/2))

title_screen()
app.run()
