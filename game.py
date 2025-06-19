from ursina import *
from player import *
from bullet import *
from enemy import *
from boss import *
from map import *
import random
import os

# --- Global variables and stubs required by classes.py ---
paused = False
enemy_list = []
boss_health_bar = None
win_screen_shown = False

def set_enemy_follow_enabled(enabled):
    pass  # Stub, real logic is below

def toggle_pause():
    pass  # Stub, real logic is below

# wave_text, enemies_left_text, and ground are defined later in the script

window.vsync = False
app = Ursina(borderless=False)
sky = Sky()
sky.texture = 'assets/sky'

game_started = False
round_number = 0
enemy_list = []
wave_cleared = False

player = Player()
player.health_bar.disable()

ground = Map(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture_scale=(500,500))
border_one = Map(scale=(100, 5, 0.1), position=(50, 2.5, 0), rotation=(0,90,0))
border_two = Map(scale=(100, 5, 1), position=(0, 2.5, 50), rotation=(0,0,0))
border_three = Map(scale=(1, 5, 100), position=(0, 2.5, -50), rotation=(0,90,0))
border_four = Map(scale=(1, 5, 100), position=(-50, 2.5, 0), rotation=(0,0,0))

num_layers = 1  # Only keep the innermost layer
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

wave_text = Text(text=f'Wave: {round_number}', position=(-0, 0.45), scale=1, origin=(0,0), background=True)
wake_text_disabled = True
wave_text.disable()

enemies_left_text = Text(text=f'Enemies Left: 0', position=(0.5, 0.45), scale=1, origin=(0,0), background=True)
enemies_left_text.disable()

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
    print(f"Spawning wave {round_number}")
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
                enemy = Enemy(position=pos, player=player, enemy_list=enemy_list)
                enemy_list.append(enemy)
    if 'paused' in globals() and paused:
        set_enemy_follow_enabled(False)
    wave_text.text = f'Wave: {round_number}'

def update():
    global paused, wave_cleared, win_screen_shown
    if not game_started:
        return
    if paused:
        return
    enemies_left_text.text = f'Enemies Left: {len(enemy_list)}'
    if not wake_text_disabled:
        enemies_left_text.enable()
    else:
        enemies_left_text.disable()
    if 'win_screen_shown' in globals() and win_screen_shown:
        return
    player.update()
    for bullet in scene.entities:
        if isinstance(bullet, Bullet):
            bullet.update()
    # Remove and destroy dead enemies first
    for enemy in enemy_list[:]:
        if enemy.health <= 0:
            if hasattr(enemy, 'is_boss') and enemy.is_boss:
                global boss_health_bar
                if boss_health_bar:
                    boss_health_bar.disable()
                    boss_health_bar = None
            destroy(enemy)
            enemy_list.remove(enemy)
    # Now update only the remaining enemies
    for enemy in enemy_list:
        enemy.update()
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
        game_started = True
        mouse.locked = True
        camera.position = (0,0,0)
        player.health_bar.enable()
        wave_text.enable()
        wake_text_disabled = False
        update()
    def quit_game():
        app.userExit()
    play_button.on_click = start_game
    quit_button.on_click = quit_game

paused = False
pause_entities = []
def set_enemy_follow_enabled(enabled):
    for enemy in enemy_list:
        for script in enemy.scripts:
            if isinstance(script, SmoothFollow):
                script.enabled = enabled

def toggle_pause():
    global paused, pause_entities
    if 'win_screen_shown' in globals() and win_screen_shown:
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
        def resume():
            toggle_pause()
        def quit_game():
            app.userExit()
        resume_button.on_click = resume
        quit_button.on_click = quit_game
        pause_entities = [pause_bg, pause_text, resume_button, quit_button]
    else:
        for e in pause_entities:
            e.disable()
        pause_entities = []
        mouse.locked = True

title_screen()
app.run()
