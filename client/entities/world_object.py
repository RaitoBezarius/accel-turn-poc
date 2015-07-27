import sfml as sf

from shared.constants.movement import MOVEMENT_VALUES
from client.utils.motion_controller import LocalController, RemoteController

from collections import deque

class WorldObject(object):

    def __init__(self, objectId, local):
        self.objectId = objectId
        self.tileSize = None
        self.sprite = None
        self.name = None
        self.velocity = None
        self.local = local

        if self.local:
            self.motionController = LocalController(self)
        else:
            self.motionController = RemoteController(self)

        self.nextPositions = deque()
        self.updateMutex = sf.Mutex()

    def load(self, world, packet):
        self.name = packet.readString()
        tileset = packet.readString()
        self.tileSize = packet.readUint16()

        x, y, vx, vy, tx, ty = packet.read('!iiiiii')

        texture = world.texture_loader.load(tileset, color_mask=sf.Color.WHITE)
        self.sprite = sf.Sprite(texture)
        self.sprite.color = sf.Color.WHITE
        self.sprite.texture_rectangle = sf.Rectangle(sf.Vector2(tx * self.tileSize, ty * self.tileSize), sf.Vector2(self.tileSize, self.tileSize))
        self.sprite.position = sf.Vector2(x * self.tileSize, y * self.tileSize)

        self.velocity = sf.Vector2(vx, vy)

        print ('World object (id: %d, name: %s) loaded in the world.' % (self.objectId, self.name))

    def updatePosition(self, position):
        self.sprite.position = self.toLocalPosition(position)

    def update(self, diff):
        self.updateMutex.lock()
        nextState = self.motionController.apply()
        if nextState is not None:
            nextState.simulate(self.world_position, self.velocity)
            self.updatePosition(nextState.position)
            self.motionController.applied(nextState)
            print ('Updated position with: {}'.format(nextState))
        self.updateMutex.unlock()

    @property
    def world_position(self):
        pos = self.sprite.position
        return sf.Vector2(pos.x / self.tileSize, pos.y / self.tileSize)

    def toLocalPosition(self, pos):
        return sf.Vector2(pos.x * self.tileSize, pos.y * self.tileSize)

    def enqueuePositionUpdate(self, pos):
        self.motionController.enqueuePosition(pos)

    def moveObject(self, packet):
        self.updateMutex.lock()
        self.motionController.validate(packet)
        self.updateMutex.unlock()

    def doMovePrediction(self, predictionId, direction):
        assert (self.local)
        self.updateMutex.lock()
        self.motionController.predict(predictionId, direction)
        self.updateMutex.unlock()

    def draw(self, window):
        if self.sprite:
            window.draw(self.sprite)
