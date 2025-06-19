# Import Ursina game engine and required modules
from ursina import *  # Ursina core
from ursina.prefabs.first_person_controller import FirstPersonController  # First person controller prefab
from ursina.prefabs.health_bar import HealthBar  # Health bar prefab
import random  # For random number generation
import time  # For time-based operations
import os  # For file existence checking

window.vsync = False  # Disable vertical sync for the window
app = Ursina(borderless=False)  # Create the Ursina app window
sky = Sky()  # Add a sky to the scene
sky.texture = 'assets/sky'  # Set your custom sky image here (make sure 'my_sky.jpg' is in your project folder)

game_started = False  # Flag to check if the game has started
round_number = 0  # Current wave/round number
enemy_list = []  # List to store all enemy entities
wave_cleared = False  # Flag to check if the current wave is cleared

# Player class definition
class Player(Entity):  # Inherit from Ursina's Entity
    def __init__(self, **kwargs):  # Player constructor
        self.controller = FirstPersonController(**kwargs)  # Add first person controller
        super().__init__(parent=self.controller)  # Initialize Entity with controller as parent
        self.collider = CapsuleCollider(self, center=Vec3(0.5,2.5,0.5), height=5, radius=0.25)  # Add capsule collider
        self.health = 100  # Set player health
        self.health_bar = HealthBar(bar_color=color.lime.tint(-.25), roundness=0.5, max_value=100, value=self.health, scale=(.25,.02), position=(-0.85,-0.45))  # Health bar UI

        self.gun = Entity(parent=self.controller.camera_pivot,  # Gun entity
                               scale=0.1,
                               position=Vec3(1,-1,1.5),
                               rotation=Vec3(0,170,0),
                               model='assets/scifi_gun.obj',
                               color=color.yellow,
                               visible=False)
        
        self.knife = Entity(parent=self.controller.camera_pivot,  # Knife entity
                               scale=0.1,
                               position=Vec3(1,-0.5,1.5),
                               rotation=Vec3(60,-10,90),
                               model='assets/knife.obj',
                               color=color.gray,
                               visible=False)
        
        self.weapons = [self.gun, self.knife]  # List of weapons
        self.current_weapon = 0  # Index of current weapon
        self.switch_weapon()  # Set initial weapon

    def switch_weapon(self):  # Switch weapon visibility
        for i, v in enumerate(self.weapons):  # Loop through weapons
            v.visible = (i == self.current_weapon)  # Show only the current weapon

    def input(self, key):  # Handle input events
        global paused  # Use global paused flag
        if key == 'escape':  # Pause key
            if not ('win_screen_shown' in globals() and win_screen_shown):  # If win screen not shown
                toggle_pause()  # Toggle pause
            return
        if paused:  # If paused, ignore input
            return
        try:
            self.current_weapon = int(key) - 1  # Number key to select weapon
            self.switch_weapon()  # Switch weapon
        except ValueError:
            pass  # Ignore if not a number

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
                    
# Bullet class definition
class Bullet(Entity):  # Inherit from Entity
    def __init__(self, speed=500, lifetime=0.5, direction=camera.forward.normalized(), **kwargs):  # Bullet constructor
        super().__init__(**kwargs)  # Initialize Entity
        self.speed = speed  # Bullet speed
        self.lifetime = lifetime  # Bullet lifetime
        self.direction = direction  # Bullet direction
        self.origin = Vec3(-1.5,1,0)  # Origin (unused)
        self.start = time.time()  # Start time
        self.look_at(camera.forward * 5000)  # Orient bullet
        self.world_parent = scene  # Set world parent
    
    def update(self):  # Update bullet each frame
        if 'paused' in globals() and paused:  # If paused, do nothing
            return
        ray = raycast(self.world_position, self.forward, distance=self.speed*time.dt)  # Raycast ahead
        if not ray.hit and time.time() - self.start < self.lifetime:  # If not hit and not expired
            self.world_position += self.forward * self.speed * time.dt  # Move bullet
        
        if time.time() - self.start >= self.lifetime:  # If bullet expired
            destroy(self)  # Destroy bullet

        if ray.hit:  # If hit something
            if hasattr(ray.entity, 'is_enemy') and ray.entity.is_enemy:  # If hit enemy
                ray.entity.health -= 100  # Damage enemy
                print(f"Enemy hit! Health: {ray.entity.health}")  # Print health
                # Update boss health bar immediately if boss
                if hasattr(ray.entity, 'is_boss') and ray.entity.is_boss:
                    global boss_health_bar
                    if boss_health_bar:
                        boss_health_bar.value = ray.entity.health
            if hasattr(ray.entity, 'health') and ray.entity.health <= 0:  # If enemy dead
                destroy(ray.entity)  # Destroy enemy
            destroy(self)  # Destroy bullet

# Enemy class definition
class Enemy(Entity):  # Inherit from Entity
    def __init__(self, position, player, health=150, damage=5):  # Enemy constructor
        super().__init__(model='assets/sahur.obj', texture='assets/sahur_skin.png', scale=1, position=position, collider='box')  # Enemy appearance
        self.speed = 5  # Enemy speed
        self.is_enemy = True  # Tag as enemy
        self.health = health  # Enemy health
        self.player = player  # Reference to player
        self.damage = damage  # Damage to player
        # self.add_script(SmoothFollow(target=player.controller, speed=0.5))  # Smooth follow script (disabled for manual movement)
        self.damage_cooldown = 1.0  # seconds between hits
        self.time_since_last_hit = 0.0  # Time since last hit
        self.collider = BoxCollider(self, center=Vec3(0.25,1.25,0.25), size=Vec3(1,5,1))  # Enemy collider

        # --- Ensure enemy does not spawn inside a wall ---
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
            # Try a new random position
            self.position = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))
            attempts += 1
            if attempts >= max_attempts:
                break  # Give up after too many attempts
    
    def prevent_merging(self):  # Prevent enemies from merging
        for other in enemy_list:  # Loop through all enemies
            if other == self:  # Skip self
                continue
            if self.intersects(other).hit:  # If colliding with another enemy
                # Push the enemy away slightly
                push_dir = (self.position - other.position).normalized()  # Direction to push
                self.position += push_dir * time.dt * 5  # Tune this push strength

    def update(self):  # Update enemy each frame
        global paused  # Use global paused flag
        if 'paused' in globals() and paused:  # If paused, do nothing
            return
        # Prevent enemy from going under the ground
        if self.y < 1:
            self.y = 1
        # Smoothly rotate enemy to face the player
        direction = self.player.world_position - self.world_position  # Vector to player
        direction.y = 0  # Ignore vertical difference for rotation
        target_angle = math.degrees(math.atan2(direction.x, direction.z))  # Calculate target angle
        self.rotation_y = lerp(self.rotation_y, target_angle, 6 * time.dt)  # Smoothly rotate

        # Wall avoidance: try direct path, then angles if blocked
        move_directions = [0, 45, -45, 90, -90]  # degrees to try
        moved = False
        for angle in move_directions:
            # Rotate direction by angle
            rad = math.radians(angle)
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

# --- Boss class ---
boss_health_bar = None  # Global boss health bar
class Boss(Enemy):  # Boss inherits from Enemy
    def __init__(self, position, player):  # Boss constructor
        super().__init__(position=position, player=player, health=1000, damage=30)  # Call Enemy constructor
        self.model = 'assets/sahur.obj'  # Boss model
        self.texture = 'assets/sahur_skin.png' # Boss color
        self.scale = 5 # Make the boss bigger than the enemies
        self.is_boss = True  # Tag as boss
        global boss_health_bar
        boss_health_bar = HealthBar(bar_color=color.red, roundness=0.5, max_value=10000, value=1000, scale=(1,0.01), position=(-0.50,0.40))  # Boss health bar

    def update(self):  # Update boss each frame
        if 'paused' in globals() and paused:  # If paused, do nothing
            return
        # Prevent boss from going under the ground
        if self.y < 1:
            self.y = 1
        # Smoothly rotate boss to face the player
        direction = self.player.world_position - self.world_position  # Vector to player
        direction.y = 0  # Ignore vertical difference for rotation
        target_angle = math.degrees(math.atan2(direction.x, direction.z))  # Calculate target angle
        self.rotation_y = lerp(self.rotation_y, target_angle, 6 * time.dt)  # Smoothly rotate
        super().update()  # Call Enemy update
        global boss_health_bar
        if boss_health_bar:
            boss_health_bar.value = self.health  # Update boss health bar
        if self.health <= 0 and boss_health_bar:  # If boss dead
            boss_health_bar.disable()  # Hide health bar
            boss_health_bar = None

# Map class definition
class Map(Entity):  # Inherit from Entity
    def __init__(self, **kwargs):  # Map constructor
        if 'texture' not in kwargs:
            kwargs['texture'] = 'assets/tung_wall.png'  # Default texture for all Map entities
        if 'model' not in kwargs:
            kwargs['model'] = 'cube'  # Default model for all Map entities
        if 'collider' not in kwargs:
            kwargs['collider'] = 'box'  # Default collider for all Map entities
        super().__init__(**kwargs)  # Initialize Entity
        self.health = float('inf')  # Infinite health
        self.is_map = True  # Tag to identify map objects

player = Player()  # Create player

# Hide health bar and wave text at start
player.health_bar.disable()  # Hide health bar

ground = Map(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='assets/sahur_ground.png', texture_scale=(1,1))  # Ground entity
border_one = Map(scale=(100, 5, 0.1), position=(50, 2.5, 0), rotation=(0,90,0))  # Border 1
border_two = Map(scale=(100, 5, 1), position=(0, 2.5, 50), rotation=(0,0,0))  # Border 2
border_three = Map(scale=(1, 5, 100), position=(0, 2.5, -50), rotation=(0,90,0))  # Border 3
border_four = Map(scale=(1, 5, 100), position=(-50, 2.5, 0), rotation=(0,0,0))  # Border 4

# --- Four L-shaped walls, one in each corner ---
# L-shaped wall layers in each corner, repeated 5 times with uniform gaps
num_layers = 1  # Only keep the innermost layer
layer_gap = 10
min_length = 14  # Minimum wall length (innermost, slightly larger)
max_length = 34  # Maximum wall length (outermost, slightly larger)
wall_thickness = 1
for i in range(num_layers):
    # Proportional wall length based on distance from center, so the wall edges align evenly
    t = (num_layers - 1 - i) / (num_layers - 1) if num_layers > 1 else 1
    wall_length = min_length + (max_length - min_length) * t
    offset = layer_gap * (i + 1) + wall_thickness * i
    # Top-left corner
    tl_x = -50 + offset + wall_thickness/2
    tl_z = 50 - offset - wall_length/2
    Map(scale=(1, 5, wall_length), position=(tl_x, 2.5, tl_z))  # vertical (outer edge fixed)
    Map(scale=(wall_length, 5, 1), position=(-50 + offset + wall_length/2, 2.5, 50 - offset - wall_thickness/2))  # horizontal (outer edge fixed)
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
wake_text_disabled = True  # Flag for wave text
wave_text.disable()  # Hide wave text

# Enemies left text UI
enemies_left_text = Text(text=f'Enemies Left: 0', position=(0.5, 0.45), scale=1, origin=(0,0), background=True)
enemies_left_text.disable()

def spawn_wave():  # Spawn a new wave of enemies
    global enemy_list, round_number, wave_cleared, boss_health_bar

    print(f"Spawning wave {round_number}")  # Print wave number
    enemy_list = []  # Clear enemy list
    wave_cleared = False  # Reset wave cleared flag

    if round_number == 10:  # Boss wave
        # Spawn the boss only
        pos = Vec3(0, 1, 0)  # Boss position
        boss = Boss(position=pos, player=player)  # Create boss
        enemy_list.append(boss)  # Add boss to enemy list
    else:
        for _ in range(4 * round_number):  # Set the munber of enemies per wave to four times the wave number
            pos = Vec3(random.uniform(-40, 40), 1, random.uniform(-40, 40))  # Random enemy spawn position
            enemy = Enemy(position=pos, player=player)  # Create enemy
            enemy_list.append(enemy)  # Add enemy to list

    # Ensure new enemies are frozen if paused
    if 'paused' in globals() and paused:
        set_enemy_follow_enabled(False)  # Disable enemy following

    wave_text.text = f'Wave: {round_number}'  # Update wave text

def update():  # Main update loop
    global paused, wave_cleared, win_screen_shown
    if not game_started:  # If game not started
        return  # Don't run the game until user presses Play

    if paused:  # If paused
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
    title_text = Text(text="Sahur Shooter", color=color.white, scale=5, origin=(0,0), y=0.1, z=0.1, background=True)  # Title text

    # Play Button
    play_button = Button(text='Play', color=color.green, scale=(0.3, 0.1), x=-0.175, y=-0.25)  # Play button
    
    # Quit Button
    quit_button = Button(text='Quit', color=color.red, scale=(0.3, 0.1), x=0.175, y=-0.25)  # Quit button

    # Background UI (with image texture fallback)
    title_bg_image = 'title_bg.jpg'
    if os.path.exists(title_bg_image):
        title_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.white, z=1, texture=title_bg_image)
    else:
        title_bg = Entity(parent=camera.ui, model='quad', scale=(2,1), color=color.black, z=1)

    mouse.locked = False  # Unlock mouse
    camera.fov = 90  # Set camera FOV
    camera.position = (0, 0, -20)  # Optional: move camera away from gameplay view
    camera.rotation = (0, 0, 0)  # Reset camera rotation

    def start_game():  # Start game handler
        global game_started, wake_text_disabled

        title_bg.disable()  # Hide title background
        title_text.disable()  # Hide title text
        play_button.disable()  # Hide play button
        quit_button.disable()  # Hide quit button
        game_started = True  # Set game started
        mouse.locked = True  # Lock mouse
        camera.position = (0,0,0)  # Reset camera position
        # Show health bar and wave text
        player.health_bar.enable()  # Show health bar
        wave_text.enable()  # Show wave text
        wake_text_disabled = False  # Update flag
        update()  # Start update loop

    def quit_game():  # Quit game handler
        app.userExit()  # Exit app

    play_button.on_click = start_game  # Set play button handler
    quit_button.on_click = quit_game  # Set quit button handler

# --- Pause screen logic ---
paused = False  # Pause flag
pause_entities = []  # List of pause UI entities
def set_enemy_follow_enabled(enabled):  # Enable/disable enemy following
    for enemy in enemy_list:
        for script in enemy.scripts:
            if isinstance(script, SmoothFollow):
                script.enabled = enabled

def toggle_pause():  # Toggle pause state
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
            toggle_pause()  # Resume game
        def quit_game():
            app.userExit()  # Exit app
        resume_button.on_click = resume  # Set resume handler
        quit_button.on_click = quit_game  # Set quit handler
        pause_entities = [pause_bg, pause_text, resume_button, quit_button]  # Store pause UI
    else:
        for e in pause_entities:
            e.disable()  # Hide pause UI
        pause_entities = []  # Clear pause UI list
        mouse.locked = True  # Lock mouse

title_screen()  # Show title screen
app.run()  # Run the Ursina app
