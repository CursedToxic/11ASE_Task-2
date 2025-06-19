from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

window.vsync = False
app = Ursina(fullscreen=True)
Sky()

ground = Entity(model='plane', scale=(100,1,100), color=color.yellow.tint(-.2), texture='grass', texture_scale=(100,100), collider='box')
player = FirstPersonController(y=2, origin_y=-.5)
player.gun = None

gun = Button(parent=scene, model='assets/gun.obj', color=color.dark_gray, origin_y=-.5, position=(0,0,0), collider='box', scale=(.2,.2,.1))
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