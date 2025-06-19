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

gun = Button(parent=scene, model='assets/gun.obj', color=color.yellow, origin_y=-.5, position=(3,0,3), collider='box', scale=(0.2,0.2,0.1))
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