from client.entities.map import TileMap
from client.utils.texture_loader import TextureLoader

import sfml as sf

class World(object):

    def __init__(self, objectId, mapId, session):
        self.me_id = objectId
        self.session = session
        self.worldObjects = {}
        self.map = TileMap(mapId)

        self.texture_loader = TextureLoader()

    def load(self):
        print ('World loading...')
        self.map.load(self.texture_loader)
        print ('World loaded.')

    def update(self, diff):
        map(lambda world_object: world_object.update(diff), self.worldObjects.values())

    def draw(self, window):
        window.draw(self.map)
        map(lambda world_object: world_object.draw(window), self.worldObjects.values())

    def handleEvent(self, window, event):
        moves_actions = [sf.Keyboard.UP, sf.Keyboard.DOWN, sf.Keyboard.LEFT, sf.Keyboard.RIGHT]
        if type(event) is sf.KeyEvent and event.pressed:
            if event.code in moves_actions:
                self.session.sendMovementRequest(event.code)


    def addObject(self, world_object):
        self.worldObjects[world_object.objectId] = world_object

    def removeObject(self, world_object):
        self.worldObjects.remove(world_object)
