from ursina import *
from ursina.prefabs.health_bar import HealthBar

# Map class definition
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
