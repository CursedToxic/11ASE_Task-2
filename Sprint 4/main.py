# Thanks to Ursina Tutorials on YouTube for most of the Player Class
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
import random
import time
import os 

window.vsync = False 
app = Ursina(borderless=False)
sky = Sky(texture='assets/sky')

game_started = False  # Flag to check if the game has started
round_number = 0  # Current wave/round number
enemy_list = []  # List to store all enemy entities
wave_cleared = False  # Flag to check if the current wave is cleared

class Player(Entity):
    def __init__(self, **kwargs): 
        self.controller = FirstPersonController(**kwargs) # Set player controller to FirstPersonController
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
                               visible=False)
        
        self.knife = Entity(parent=self.controller.camera_pivot,
                               scale=0.1,
                               position=Vec3(1,-0.5,1.5),
                               rotation=Vec3(60,-10,90),
                               model='assets/knife.obj',
                               color=color.gray,
                               visible=False)
        
        self.weapons = [self.gun, self.knife]
        self.current_weapon = 0 
        self.switch_weapon()

    def switch_weapon(self): 
        for i, v in enumerate(self.weapons):  
            v.visible = (i == self.current_weapon)  # Only show current weapon

    def input(self, key):  # Handle input events
        global paused  # Use global paused flag
        if key == 'escape':
            if not ('win_screen_shown' in globals() and win_screen_shown):  # Only show pause on right conditions
                toggle_pause()
            return
        if paused:  # Ignore player input while paused
            return
        
        try:
            self.current_weapon = int(key) - 1  # Weapon selection system
            self.switch_weapon()
        except ValueError:
            return  # Ensures accurate switching

        if key == 'scroll up':  # Mouse scroll up
            self.current_weapon = (self.current_weapon + 1) % len(self.weapons)  # Next weapon
            self.switch_weapon()
        
        if key == 'scroll down':  # Mouse scroll down
            self.current_weapon = (self.current_weapon - 1) % len(self.weapons)  # Previous weapon
            self.switch_weapon()
        
        if key == 'left mouse down' and self.current_weapon == 0:  # Shoot gun
            Bullet(model='sphere',
                   color=color.black,
                   scale=0.1,
                   position=self.controller.camera_pivot.world_position,
                   rotation=self.controller.camera_pivot.world_rotation)
        
        if key == 'right mouse down' and self.current_weapon == 0:  # Aim down sights
            camera.fov = 30
        elif key == 'right mouse up' and self.current_weapon == 0:  # Stop aiming
            camera.fov = 90

        if key == 'left mouse down' and self.current_weapon == 1:  # Knife attack
            self.slash()

    def update(self):  # Player Update
        if held_keys['shift']:
            self.controller.speed = 25 
        else:
            self.controller.speed = 5
        self.controller.camera_pivot.y = 2 - held_keys['left control']  # Crouch if control key held

    def slash(self):  # Knife attack logic
        if not hasattr(self, 'knife_cooldown'):
            self.knife_cooldown = 0  # Initialize cooldown
        if time.time() - self.knife_cooldown < 0.5:  # Cooldown check
            return  # Cooldown between slashes

        self.knife_cooldown = time.time()  # Reset cooldown

        # Animate slash
        knife = self.knife  # Get knife entity
        knife.animate_rotation(Vec3(60, -10, 90) + Vec3(-90, 0, 0), duration=0.1) 
        knife.animate_rotation(Vec3(60, -10, 90), duration=0.1, delay=0.1)  # Reset rotation

        # Melee hit detection
        hit = raycast(self.controller.camera_pivot.world_position, self.controller.forward, distance=2)  # Raycast for hit
        if hit.hit:  # If hit something
            if hasattr(hit.entity, 'health'):  # If entity has health
                hit.entity.health -= 150  # One shot normal enemies
                # Update boss health bar immediately if boss
                if hasattr(hit.entity, 'is_boss') and hit.entity.is_boss:
                    global boss_health_bar
                    if boss_health_bar:
                        boss_health_bar.value = hit.entity.health

                if hit.entity.health <= 0:  # If enemy dead
                    destroy(hit.entity)  # Destroy enemy
                    
class Bullet(Entity): 
    def __init__(self, speed=500, lifetime=0.5, direction=camera.forward.normalized(), **kwargs):
        super().__init__(**kwargs) 
        self.speed = speed  
        self.lifetime = lifetime 
        self.direction = direction  
        self.origin = Vec3(-1.5,1,0) 
        self.start = time.time()
        self.look_at(camera.forward * 5000)
        self.world_parent = scene
    
    def update(self): 
        if 'paused' in globals() and paused:  # Set no bullets shot when paused
            return
        ray = raycast(self.world_position, self.forward, distance=self.speed*time.dt) 
        if not ray.hit and time.time() - self.start < self.lifetime:  # If bullet not hit anything and not expired
            self.world_position += self.forward * self.speed * time.dt 
        
        if time.time() - self.start >= self.lifetime: # Remove bullet when past lifetime
            destroy(self)

        if ray.hit: 
            if hasattr(ray.entity, 'is_enemy') and ray.entity.is_enemy:  # If bullet hits enemy
                ray.entity.health -= 50  # Three shot enemies, this was there is some difficulty
                print(f"Enemy Health: {ray.entity.health}")
                # Update boss health bar immediately when boss hit (identified using the is_boss classification)
                if hasattr(ray.entity, 'is_boss') and ray.entity.is_boss:
                    global boss_health_bar
                    if boss_health_bar:
                        boss_health_bar.value = ray.entity.health
            if hasattr(ray.entity, 'health') and ray.entity.health <= 0:  # If any enemy class dead
                destroy(ray.entity)
            destroy(self)

class Enemy(Entity):
    def __init__(self, position, target, health=150, damage=5):
        super().__init__(model='assets/sahur.obj', texture='assets/sahur_skin.png', scale=1, position=position, collider='box')  # Set enemy appearance
        self.speed = 5
        self.is_enemy = True  # Classification as enemy
        self.health = health 
        self.target = player  # Set the target as the player
        self.damage = damage
        # self.add_script(SmoothFollow(target=player.controller, speed=0.5))  # Smooth follow script, originally used this
        self.damage_cooldown = 1.0  # Seconds between hits, so that damage is consistent
        self.time_since_last_hit = 0.0  # Time since last hit, again, ensuring damage is consistent
        self.collider = BoxCollider(self, center=Vec3(0.25,1.25,0.25), size=Vec3(1,5,1))

        # Make sure enemy spawn is not in wall, try spawning again if that is the case
        max_attempts = 20
        attempts = 0
        while True:
            collides = False
            for entity in scene.entities:
                if hasattr(entity, 'is_map') and entity.is_map and entity != ground:
                    if self.intersects(entity).hit:
                        collides = True
                        break
            if not collides:
                break
            # Try spawning on a new random position on the map
            self.position = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))
            attempts += 1
            if attempts >= max_attempts:
                break  # Stop spawning after too many attempts to spawn
    
    def prevent_merging(self):  # Prevent enemies from merging into one
        for other in enemy_list:  # Loop through all enemies
            if other == self:
                continue
            if self.intersects(other).hit:  # If colliding with another enemy
                # Push the enemy away slightly
                push_dir = (self.position - other.position).normalized()  # Direction to push
                self.position += push_dir * time.dt * 5  # Setting new position after begin pushed

    def update(self):
        global paused  # Use global paused flag
        if 'paused' in globals() and paused: 
            return
        # Prevent enemy from going under the ground
        if self.y < 1:
            self.y = 1
        # Rotate enemy to face player
        direction = self.player.world_position - self.world_position  # Direction to player from enemy (self)
        direction.y = 0  # Make it so the rotation is only on the ground
        target_angle = math.degrees(math.atan2(direction.x, direction.z))  # Calculate target angle using trigonometry
        self.rotation_y = lerp(self.rotation_y, target_angle, 6 * time.dt)  # Rotate towards player

        # Enemy movement to avoid walls
        move_directions = [0, 45, -45, 90, -90]  # Try common angles 
        moved = False # Tells the game that enemy has not moved towards player yet
        for angle in move_directions:
            # Rotate direction by angle
            rad = math.radians(angle) # Use radians to calculate angle
            dir_vec = Vec3(
                direction.x * math.cos(rad) - direction.z * math.sin(rad),
                0,
                direction.x * math.sin(rad) + direction.z * math.cos(rad)
            ).normalized()
            move_step = dir_vec * self.speed * time.dt
            new_position = self.world_position + move_step
            blocked = False
            for entity in scene.entities:
                if hasattr(entity, 'is_map') and entity.is_map and entity != ground:
                    old_pos = self.world_position
                    self.world_position = new_position
                    if self.intersects(entity).hit:
                        blocked = True
                        self.world_position = old_pos
                        break
                    self.world_position = old_pos
            if not blocked:
                self.world_position = new_position
                moved = True
                break
        # If all directions blocked, don't move

        self.time_since_last_hit += time.dt  # Update hit timer
        self.prevent_merging()  # Prevent merging

        # Check distance to player instead of collider comparison
        if distance(self.world_position, self.player.world_position) < 2:  # If close to player
            if self.time_since_last_hit >= self.damage_cooldown:  # If cooldown passed
                self.player.health -= self.damage  # Damage player
                self.player.health_bar.value = self.player.health  # Update health bar
                print(f'Player Health: {self.player.health}')  # Print health
                self.time_since_last_hit = 0  # Reset hit timer

                if self.player.health <= 0:  # If player dead
                    self.player.health = 0
                    print("player died")
                    death_screen = Text(text='YOU DIED', color=color.red, position=(0,0), scale=9, origin=(0,0), background=True, z=0)  # Show death screen
                    death_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)  # Show background
                    # Hide use pause screen but don't display pause text
                    player.health_bar.disable()
                    wave_text.disable()
                    enemies_left_text.disable()
                    paused = True
                    set_enemy_follow_enabled(False)
                    player.controller.enabled = False
                    mouse.locked = False

boss_health_bar = None  # Boss health bar global variable
class Boss(Enemy):
    def __init__(self, position, player): 
        super().__init__(position=position, player=player, health=1000, damage=30) 
        self.model = 'assets/sahur.obj'  
        self.texture = 'assets/sahur_skin.png' 
        self.scale = 5 # Make the boss bigger than the enemies
        self.is_boss = True  # Classification, same as for Enemy
        global boss_health_bar
        boss_health_bar = HealthBar(bar_color=color.red, roundness=0.5, max_value=10000, value=1000, scale=(1,0.01), position=(-0.50,0.40))  # Boss health bar

    def update(self):
        if 'paused' in globals() and paused:
            return
        # Prevent boss from going under the ground
        if self.y < 1:
            self.y = 1
        # Do the same thing as the enemy, there is no enemy variable yet
        direction = self.player.world_position - self.world_position
        direction.y = 0 
        target_angle = math.degrees(math.atan2(direction.x, direction.z)) 
        self.rotation_y = lerp(self.rotation_y, target_angle, 6 * time.dt)
        super().update()
        global boss_health_bar
        if boss_health_bar:
            boss_health_bar.value = self.health  # Set the boss health bar to display its health
        if self.health <= 0 and boss_health_bar: 
            boss_health_bar.disable()  # Hide health bar when boss dies
            boss_health_bar = None

class Map(Entity):
    def __init__(self, **kwargs): 
        if 'texture' not in kwargs:
            kwargs['texture'] = 'assets/tung_wall.png'  # Set defaults for Map entities
        if 'model' not in kwargs:
            kwargs['model'] = 'cube'
        if 'collider' not in kwargs:
            kwargs['collider'] = 'box'
        super().__init__(**kwargs)
        self.health = float('inf')  # Set infinite health
        self.is_map = True  # Classification, same as for Enemy

player = Player()  # Create player

# Hide health bar and wave text at start
player.health_bar.disable()  # Hide health bar

ground = Map(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='assets/sahur_ground.png', texture_scale=(1,1))  # Ground entity
border_one = Map(scale=(100, 5, 0.1), position=(50, 2.5, 0), rotation=(0,90,0))  # Border 1
border_two = Map(scale=(100, 5, 1), position=(0, 2.5, 50), rotation=(0,0,0))  # Border 2
border_three = Map(scale=(1, 5, 100), position=(0, 2.5, -50), rotation=(0,90,0))  # Border 3
border_four = Map(scale=(1, 5, 100), position=(-50, 2.5, 0), rotation=(0,0,0))  # Border 4

# L-shaped walls for symmetry (yes, symmetry is necessary)
num_layers = 1  # Set the number of times to spawn walls inward
layer_gap = 10
min_length = 14  # Minimum and maximum wall lengths, so the game can make them have similar gap size between them
max_length = 34 
wall_thickness = 1
for i in range(num_layers):
    # Proportional wall length based on distance from center, so the wall edges align evenly
    t = (num_layers - 1 - i) / (num_layers - 1) if num_layers > 1 else 1
    wall_length = min_length + (max_length - min_length) * t
    offset = layer_gap * (i + 1) + wall_thickness * i
    # Top-left corner
    tl_x = -50 + offset + wall_thickness/2
    tl_z = 50 - offset - wall_length/2
    Map(scale=(1, 5, wall_length), position=(tl_x, 2.5, tl_z))  # The position of the outermost vertical and horizontal walls is fixed
    Map(scale=(wall_length, 5, 1), position=(-50 + offset + wall_length/2, 2.5, 50 - offset - wall_thickness/2))
    # Top-right corner
    tr_x = 50 - offset - wall_thickness/2
    tr_z = 50 - offset - wall_length/2
    Map(scale=(1, 5, wall_length), position=(tr_x, 2.5, tr_z))
    Map(scale=(wall_length, 5, 1), position=(50 - offset - wall_length/2, 2.5, 50 - offset - wall_thickness/2))
    # Bottom-left corner
    bl_x = -50 + offset + wall_thickness/2
    bl_z = -50 + offset + wall_length/2
    Map(scale=(1, 5, wall_length), position=(bl_x, 2.5, bl_z))
    Map(scale=(wall_length, 5, 1), position=(-50 + offset + wall_length/2, 2.5, -50 + offset + wall_thickness/2))
    # Bottom-right corner
    br_x = 50 - offset - wall_thickness/2
    br_z = -50 + offset + wall_length/2
    Map(scale=(1, 5, wall_length), position=(br_x, 2.5, br_z))
    Map(scale=(wall_length, 5, 1), position=(50 - offset - wall_length/2, 2.5, -50 + offset + wall_thickness/2))

    
wave_text = Text(text=f'Wave: {round_number}', position=(-0, 0.45), scale=1, origin=(0,0), background=True)  # Wave text UI
wake_text_disabled = True  # State to make wave text disabled when not needed.
wave_text.disable() 

# Enemies left text UI
enemies_left_text = Text(text=f'Enemies Left: 0', position=(0.65, 0.45), scale=1, origin=(0,0), background=True)
enemies_left_text.disable()

def spawn_wave():  # Spawn a new wave of enemies
    global enemy_list, round_number, wave_cleared, boss_health_bar

    enemy_list = []  # Clear enemy list at the start of a new wave
    wave_cleared = False  # Wave state is reset (wave is not cleared)

    if round_number == 10:
        # Spawn only the boss
        pos = Vec3(0, 1, 0)
        boss = Boss(position=pos, player=player)  # Create boss enemy
        enemy_list.append(boss)  # Add boss to enemy list (a boss in an enemy)
    else:
        for _ in range(4 * round_number):  # Set the munber of enemies per wave to four times the wave number
            pos = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))  # Random enemy spawn position
            enemy = Enemy(position=pos, player=player)  # Create enemy
            enemy_list.append(enemy)  # Add enemy to list

    if 'paused' in globals() and paused:
        set_enemy_follow_enabled(False)  # Disable the enemy following the player when paused

    wave_text.text = f'Wave: {round_number}'  # Update wave text each wave

def update():
    global paused, wave_cleared, win_screen_shown
    if not game_started:
        return  # User must press Play button to start game

    if paused: 
        return

    # Update enemies left text
    enemies_left_text.text = f'Enemies Left: {len(enemy_list)}'
    if not wake_text_disabled:
        enemies_left_text.enable()
    else:
        enemies_left_text.disable()

    # Win screen logic
    if 'win_screen_shown' in globals() and win_screen_shown:
        return

    player.update()  # Update player
    # Update bullets
    for bullet in scene.entities:
        if isinstance(bullet, Bullet):
            bullet.update()  # Update bullet

    for enemy in enemy_list[:]:  # Copy the list to avoid iteration issues
        if enemy.health <= 0:  # If enemy dead
            # Hide boss health bar if boss is defeated
            if hasattr(enemy, 'is_boss') and enemy.is_boss:
                global boss_health_bar
                if boss_health_bar:
                    boss_health_bar.disable()
                    boss_health_bar = None
            destroy(enemy)  # Destroy enemy
            enemy_list.remove(enemy)  # Remove from list

    if round_number == 10 and len(enemy_list) == 0 and player.health > 0:
        win_screen_shown = True  # Show win screen if this is 'True'
        win_text = Text(text='YOU WIN!', color=color.lime, position=(0,0), scale=9, origin=(0,0), background=True, z=0, parent=camera.ui)  # Win text
        win_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)  # Win background=
        mouse.locked = False  # Unlock mouse
        paused = True  # Pause game
        player.controller.enabled = False  # Disable player
        def wait_for_exit(key):  # Wait for exit input
            if key == 'escape' or key == 'enter':
                app.userExit()
        win_text.input = wait_for_exit  # Set input handler
        # congrats.input = wait_for_exit
        window.input = wait_for_exit
        return

    # Check for end of wave
    if len(enemy_list) == 0 and not wave_cleared and player.health > 0:
        wave_cleared = True  # Set wave cleared
        invoke(start_next_wave, delay=3)  # Delay before next wave

def start_next_wave():  # Start the next wave
    global round_number
    if round_number < 10:
        round_number += 1  # Increment round
        spawn_wave()  # Spawn new wave
    if round_number == 10:
        print("yay")  # Print yay on boss wave

def title_screen():  # Show title screen
    # Title Text
    title_text = Text(text="Sahur Shooter", color=color.white, scale=5, origin=(0,0), y=0.1, z=0.1, background=True)
    # Play button
    play_button = Button(text='Play', color=color.green, scale=(0.3, 0.1), x=-0.175, y=-0.25)
    # Quit button
    quit_button = Button(text='Quit', color=color.red, scale=(0.3, 0.1), x=0.175, y=-0.25)
    # Title background (the image did not work)
    title_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)

    mouse.locked = False
    camera.fov = 90
    camera.position = (0, 0, -20)  # Move camera away from gameplay view so the player can't see the map beforehand
    camera.rotation = (0, 0, 0)  # Set camera rotation

    def start_game():  # Start game handler
        global game_started, wake_text_disabled

        title_bg.disable()
        title_text.disable()
        play_button.disable()
        quit_button.disable()
        game_started = True
        mouse.locked = True
        camera.position = (0,0,0) # Set campera position to first person pos
        player.health_bar.enable() 
        wave_text.enable()
        wake_text_disabled = False
        update()

    def quit_game(): 
        app.userExit()

    play_button.on_click = start_game 
    quit_button.on_click = quit_game

paused = False  # Indicate to the game that it is not paused.
pause_entities = []  # List of entities used in the Pause screen
def set_enemy_follow_enabled(enabled):  # Enable/disable enemy following
    for enemy in enemy_list:
        for script in enemy.scripts:
            if isinstance(script, SmoothFollow):
                script.enabled = enabled

def toggle_pause():
    global paused, pause_entities
    if 'win_screen_shown' in globals() and win_screen_shown:
        return
    paused = not paused  # Toggle paused flag
    set_enemy_follow_enabled(not paused)  # Enable/disable enemy following
    # Freeze/unfreeze player movement by disabling/enabling FirstPersonController
    player.controller.enabled = not paused
    if paused:
        mouse.locked = False  # Unlock mouse
        pause_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=2)  # Pause background
        pause_text = Text(text='PAUSED', color=color.azure, scale=4, origin=(0,0), y=0.1, z=2, background=True)  # Pause text
        resume_button = Button(text='Resume', color=color.green, scale=(0.3, 0.1), y=-0.1, z=2)  # Resume button
        quit_button = Button(text='Quit', color=color.red, scale=(0.3, 0.1), y=-0.25, z=2)  # Quit button
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

title_screen()  # Show title screen
app.run() 
