# 11ASE Task 2 - First Person Shooter Dungeon Game
#### By Victor Guo 11ASE6
# Sprint 1
## Requirements Definition
### Functional Rqeuirements
**Data Retrieval:** What does the user need to be able to view in the system?\
The user must be able to move around, shoot weapon and see objects on screen.\
**User Interface:** What is required for the user to interact with the system?\
The user needs to know the basic controls for a First Person Shooter game. This includes: W, A, S, D to move and left mouse button to shoot.\
**Data Display:** What information does the user need to obtain from the system? What needs to be output for the user?\
The user does not need to obtain anything from the system at this stage. The output for the user would be that once the user clears a wave, the next wave begins. However, this will be implemented in future sprints.

### Non-Functional Requirements
**Performance:** How well does the system need to perform?\
The system needs to be able to run at least 60 fps at any stage of gameplay. This ensures a smooth and enjoyable experience while allowing the player to have a good reaction time.\
**Reliability:** How reliable does the system and data need to be?\
The system will need to have minimal crashes due to errors, and hacks or exploits should not be able to be created.\
**Usability and Accessibility:** How easy to navigate does the system need to be? What instructions will we need for users to access the system?\
The system navigation needs to be clear and easy to grasp. This would be beneficial for the player, who will have to close the game at some point.

## Determining Specifications
### Functional Specifications
**User Requirements:** What does the user need to be able to do? List all specifications here.\
The user needs to be able to move around for this sprint. For future sprints the user will need to be also able to shoot and kill enemies.\
**Inputs & Outputs:** What inputs will the system need to accept and what outputs will it need to display?\
The system will need to accept keyboard and mouse inputs. The player will move or shoot accordingly, shown on screen.\
**Core Features:** At its core, what specifically does the program need to be able to do?\
The user needs to be able to move around the map without falling off.\
**User Interaction:** How will users interact with the system (e.g. command-line, GUI?) and what information will it need to provide to help users navigate?\
Since this program is a game the user will have a graphical interface that changes based on user input.\
**Error Handling:** What possible errors could you face that need to be handled by the system?\
User tries to change something and modifies the program, causing an error to occur. The game should either not run or not apply the changes.

### Non-Functional Specifications
**Performance:** How quickly should we try to get the system to perform tasks, what efficiency is required to maintain user engagement? How can we ensure our program remains efficient?\
The system assets should already be loaded once the game is installed. This way the program remains efficient and performs optimally.

**Useability / Accessibility:** How might you make your application more accessible? What could you do with the User Interface to improve usability?\
This program should be able to be able to run without fail after downloading all the necessary required modules straight from my GitHub page.

**Reliability:** What could perhaps not crash the whole system, but could be an issue and needs to be addressed? Data integrity? Illogical calculation? Menu navigation going to wrong places?\
The bullet should come from the gun and go straight towards the crosshair. This needs to be adressed as the player will use the crosshair to aim their shots.

### Use Case
&nbsp;&nbsp; **Actor:** Player\
&nbsp;&nbsp; **Preconditions:** Player knows where the W,A,S,D keys are and how to use a mouse.\
&nbsp;&nbsp; **Main Flow:**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;1. Application Run – Player opens the application.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. Load Into Game – Player is able to now move on the map.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;3. Look Around Map – Player uses their mouse to look around the map smoothly.\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4. Defeat Enemies – Player defeats enemies and progresses through the waves.\
&nbsp;&nbsp; **Postconditions:** User plays game, either eliminating or failing to eliminate all enemies.

## Design
### Storyboard
![alt text](images/storyboard.png)
Note: In my game it will display the text 'wave' instead of 'round'.
### Level 0 and 1 Data Flow Diagram
![alt text](images/dataflowdiagram.png)
### Gantt Chart
![alt text](images/gantt.png)
Here is the link to the Gantt Chart for further clarity:\
https://lucid.app/lucidspark/e910e7d9-f9af-4310-921d-bc1eebee65be/edit?view_items=aDZkTitw_bmh&invitationId=inv_eea91d2c-d768-452b-84cc-376c02aacc6d

## Build and Test
```python
### From ideas.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
window.vsync = False
app = Ursina(fullscreen=True)
Sky()
player = FirstPersonController(model='cube', color=color.clear, scale_y=2, scale_x=0.5, scale_z=0.5, speed=10)
ground = Entity(model='plane', collider='box', scale=64, texture='grass', texture_scale=(4,4))

def update():
    player.x += held_keys['d'] * time.dt + time.dt
    player.x -= held_keys['a'] * time.dt + time.dt
    player.z += held_keys['w'] * time.dt + time.dt
    player.z -= held_keys['s'] * time.dt + time.dt

def jump(key):
    if key == 'space':
        player.y += 1
        invoke(setattr, player, 'y', player.y-1, delay=.25)

player.gun = None

gun = Button(parent=scene, model='gun.obj', color=color.yellow, origin_y=-.5, position=(3,0,3), collider='box', scale=(0.2,0.2,0.1))
def get_gun():
    gun.parent = camera
    gun.position = Vec3(0.2,-0.5,0.5)
    gun.rotation = (180,0,0)
    player.gun = gun
gun.on_click = get_gun

def input(key):
        if key == 'left mouse down' and player.gun:
            gun.blink(color.orange)
            bullet = Entity(parent=gun, model='cube', scale=(0.5, 0.5, 1), color=color.black)
            bullet.world_parent = scene
            bullet.animate_position(bullet.position+(bullet.forward*5000), curve=curve.linear, duration=1)
            destroy(bullet, delay=0.1)


app.run()
```
```python
### From main.py
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

window.vsync = False
app = Ursina(fullscreen=True)
Sky()

ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='grass', texture_scale=(100,100), collider='box')
player = FirstPersonController(y=2, origin_y=-.5)
player.gun = None

gun = Button(parent=scene, model='gun.obj', color=color.dark_gray, origin_y=-.5, position=(0,0,0), collider='box', scale=(.2,.2,.1))
def get_gun():
    gun.parent = camera
    gun.position = Vec3(0.3,-0.5,0.5)
    player.gun = gun
gun.on_click = get_gun

def input(key):
    if key == 'left mouse down' and player.gun:
        gun.blink(color.orange)
        bullet = Entity(parent=gun, model='cube', scale=.1, color=color.black)
        bullet.world_parent = scene
        bullet.origin_y_setter(-15)
        bullet.origin_z_setter(-30)
        bullet.origin_x_setter(-10)
        bullet.animate_position(bullet.position+(bullet.forward*1000), curve=curve.linear, duration=1)
        destroy(bullet, delay=1)

app.run()
```
## Review
**Evaluate how effectively your project meets the functional and non-functional requirements defined in your planning.**\
This project meets all of the fundemental requirements definied in my planning. However, the map itself could be improved on by adding walls so that the player cannot fall off regardless of how hard they try. Unfortunately enemies were not added and will be added in future sprints as they require knowledge of classes. Overall, my current project met some of the functional and non-functional requirements, requiring the implementation of the remaining requirements in future sprints.

**Analyse the performance of your program against the key use-cases you identified.**\
The program performs well so far, although it does not have much headroom for that many more entities in terms of frame rate. I tested fullscreen mode and this works slightly better, with more noticeable increments when increasing the resolution above 1080p (I have a 4k monitor). Without fullscreen, it has extreme fluctuations in framerate on my monitor i.e. does not run smoothly. It does not yet meet the "defeat enemies" use case as this is to be worked on in future sprints (likely sprints 2 and 3). Apart from these use-cases that have not yet been met, everything else has been checked off.

**Assess the quality of your code in terms of readability, structure, and maintainability.**\
Overall, my code is quite readable, being mostly straight from the Ursina FirstPersonController document. This means that it is relieable and understandable as everything is explained in their documentation on this website: https://www.ursinaengine.org/documentation.html, making it well structured and easy to maintain while being readable comprehensible.

**Explain the improvements that should be made in the next stage of development.**\
Walls, Enemies and enemy mechanics need to be added. Bullet positioning needs to be fixed, as it does not fire directly to the crosshair. Once these have been fixed, I need to look into adding a wave system which will go hand in hand with the enemy spawning mechanics. These should be added in future sprints (sprint 2 and 3). A bare minimum for sprint 2 is to have enemies and walls that are displayed.

# Sprint 2
## Design
### Structure Chart
![alt text](images/structurechart.png)
### Pseudocode
```pseudocode
BEGIN
    class Player
        controller = FirstPersonController
        IF key = scroll up THEN
            DISPLAY previous weapon
        ENDIF

        IF key = scroll down THEN
            DISPLAY next weapon
        ENDIF

        IF key held = left control THEN
            DISPLAY crouch
        ENDIF

    class Bullet
        IF key = left mouse down THEN
            DISPLAY bullet start position
            DISPLAY bullet change position
            DISPLAY bullet end position

            IF bullet hits wall OR ground THEN
                DESTROY bullet
            ENDIF
        ENDIF

    class Enemy
        follow player
END
```

### Flowchart
Note: The flow chart is based off of the functions within the player class (this mainly just outlines the FirstPersonController within Ursina).
![alt text](images/playermain.png)
![alt text](images/shootchart.png)
![alt text](images/movearoundchart.png)
![alt text](images/updatefuncchart.png)


## Build and Test
```python
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

window.vsync = False
app = Ursina(fullscreen=True)
Sky()

ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='grass', texture_scale=(500,500), collider='box')
# player = FirstPersonController(y=2, origin_y=-.5)
# player.gun = None

# gun = Button(parent=scene, model='gun.obj', color=color.dark_gray, origin_y=-.5, position=(0,0,0), collider='box', scale=(.2,.2,.1))

border_one = Entity(model='cube', scale=(100, 5, 0.1), position=(50, 2.5, 0), rotation=(0,90,0), collider='box', color=color.gray)
border_two = Entity(model='cube', scale=(100, 5, 1), position=(0, 2.5, 50), roation=(0,90,0), collider='box', color=color.gray)
border_three = Entity(model='cube', scale=(1, 5, 100), position=(0, 2.5, -50), rotation=(0,90,0), collider='box', color=color.gray)
border_four = Entity(model='cube', scale=(1, 5, 100), position=(-50, 2.5, 0), rotation=(0,0,0), collider='box', color=color.gray)

class Player(Entity):
    def __init__(self, **kwargs):
        self.controller = FirstPersonController(**kwargs)
        super().__init__(parent=self.controller)

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
        
        if key == held_keys['right mouse down'] and self.current_weapon == 0:
            camera.fov_setter = 30

        if key == 'escape':
            mouse.locked = not mouse.locked

    def update(self):
        self.controller.camera_pivot.y = 2 - held_keys['left control']

class Enemy(Entity):
    def __init__(self, position, player):
        super().__init__(model='cube', color=color.red, scale_x=(1), scale_y=(5),scale_z=(1), position=position, collider='box')
        self.speed = 2
        self.add_script(SmoothFollow(target=player.controller, speed=0.5))

class Bullet(Entity):
    def __init__(self, speed=250, lifetime=10, direction=camera.forward.normalized(),**kwargs):
        super().__init__(**kwargs)
        self.speed = speed
        self.lifetime = lifetime
        self.direction = direction
        self.origin = Vec3(-1.5,1,-1.5)
        self.start = time.time()
        self.look_at(camera.forward * 5000)
        self.world_parent = scene
    
    def update(self):
        ray = raycast(self.world_position, self.forward, distance=self.speed*time.dt)
        if not ray.hit and time.time() - self.start < self.lifetime:
            self.world_position += self.forward * self.speed * time.dt

        else:
            destroy(self)

player = Player()
enemies = [Enemy(position=(random.randint(-500, 500), 1, random.randint(-500, 500)), player=player) for _ in range(1)]

app.run()
```
## Review
**Evaluate how effectively your project meets the functional and non-functional requirements defined in your planning.**\
In this iteration the walls and enemies were added. The walls were extremely functional, as they were tall enough so that the player could not jump over. Enemies were added, however, they do not yet take damage, tather just following the player around aimlessly. The enemy spawning and wave systems will be added in future sprints due to time constraints and the fact that I am quite far behind in terms of progression. Overall, my current project met more functional and non-functional requirements than sprint 1, however there are still requirements that I am yet to satisfy, those are to be implemented in sprint 3.

**Analyse the performance of your program against the key use-cases you identified.**\
For the most of this sprint, I tested in fullscreen mode and thus encountered no performance issues, handling inputs and outputs flawlessly. Unfortunately, the game still does not yet meet the "defeat enemies" use case as this is to be worked on in sprint 3. This was because implementing classes meant that I was in reality up to sprint 3, but I thought I was in this sprint, hence the inclusion of classes in the codeThis use case is slowly being checked off, hopefully I can just work on refining and optimising the game in sprint 4.

**Assess the quality of your code in terms of readability, structure, and maintainability.**\
Overall, my code is mostly neat and organised as it is from a YouTube tutorials by a channel called "Ursina Tutorials", making it quite high quality. This means that in the future I can easily identify where an error may lie. This makes it suitable for future iterations/sprints. One thing that I am yet to add to the script is comments and potentially docstrings so that my code can be more widely understood. These will be added in sprint 3.

**Explain the improvements that should be made in the next stage of development.**\
Now that the bullet positioning has been fixed, and walls and enemies have been implemented, all that is left is to implement their mechanics. The player health mechanics need to be added too, so that the game can fully function with some degree of sophistication. Once these have been completed, I need to look into adding a wave system, death screen, main menu, and enemy textures/models (this will be added in sprint 4 on top of the full functionality), adding most of these in sprint 3.

# Sprint 3
## Design
### UML Class Diagram
![alt text](images/UML.png)
## Build and Test
```python
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
```
## Review
**Evaluate how effectively your project meets the functional and non-functional requirements defined in your planning.**\
This project meets all of the fundemental requirements definied in my planning. However, the map itself could be improved on by adding walls so that the player cannot fall off regardless of how hard they try. Unfortunately enemies were not added and will be added in future sprints as they require knowledge of classes. Overall, my current project met some of the functional and non-functional requirements, requiring the implementation of the remaining requirements in future sprints.

**Analyse the performance of your program against the key use-cases you identified.**\
The program performs well so far, although it does not have much headroom for that many more entities in terms of frame rate. I tested fullscreen mode and this works slightly better, with more noticeable increments when increasing the resolution above 1080p (I have a 4k monitor). Without fullscreen, it has extreme fluctuations in framerate on my monitor i.e. does not run smoothly. It does not yet meet the "defeat enemies" use case as this is to be worked on in future sprints (likely sprints 2 and 3). Apart from these use-cases that have not yet been met, everything else has been checked off.

**Assess the quality of your code in terms of readability, structure, and maintainability.**\
Now that I have added my own classes and functions, my code is still readable but is slightly more difficult ot understand due to the lack of comments. This means that in the future I would really need to understand the code in order to make improvements. 

**Explain the improvements that should be made in the next stage of development.**\
Walls, Enemies and enemy mechanics need to be added. Bullet positioning needs to be fixed, as it does not fire directly to the crosshair. Once these have been fixed, I need to look into adding a wave system which will go hand in hand with the enemy spawning mechanics. These should be added in future sprints (sprint 2 and 3). A bare minimum for sprint 2 is to have enemies and walls that are displayed.


# Sprint 4
## Design
## Build and Test
## Review
## Evaluation of System