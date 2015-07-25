from client.entities.map import TileMap
from client.utils.texture_loader import TextureLoader

import sfml as sf

class World(object):

    def __init__(self, objectId, mapId):
        self.me_id = objectId
        self.worldObjects = {}
        self.map = TileMap(mapId)

        self.texture_loader = TextureLoader()

    def load(self):
        self.map.load(self.texture_loader)

    def update(self, diff):
        map(lambda world_object: world_object.update(diff), self.worldObjects.values())

    def draw(self, window):
        self.map.draw(window)
        map(lambda world_object: world_object.draw(window), self.worldObjects.values())

    def handleEvent(self, window, event):
        pass

    def addObject(self, world_object):
        self.worldObjects[world_object.objectId] = world_object

    def removeObject(self, world_object):
        self.worldObjects.remove(world_object)
