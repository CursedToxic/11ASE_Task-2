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