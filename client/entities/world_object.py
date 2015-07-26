import sfml as sf

from shared.constants.movement import MOVEMENT_VALUES

from collections import deque

class WorldObject(object):

    def __init__(self, objectId):
        self.objectId = objectId
        self.tileSize = None
        self.sprite = None
        self.name = None
        self.velocity = None

        self.predictionHistory = {}
        self.nextPositions = deque()

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

    def update(self, diff):
        while self.nextPositions:
            nextPos = self.nextPositions.pop()
            self.sprite.position = nextPos

    @property
    def world_position(self):
        pos = self.sprite.position
        return sf.Vector2(pos.x / self.tileSize, pos.y / self.tileSize)

    def toLocalPosition(self, pos):
        return sf.Vector2(pos.x * self.tileSize, pos.y * self.tileSize)

    def enqueuePositionUpdate(self, pos):
        self.nextPositions.append(pos)

    def updatePosition(self, originalPacketId, newPos, vel):
        if self.velocity != vel:
            self.velocity = vel

        pos = self.toLocalPosition(newPos)

        if originalPacketId is not None:
            if originalPacketId not in self.predictionHistory:
                print ('Prediction correction (({oldPos.x}, {oldPos.y} vs ({newPos.x}, {newPos.y}))'.format(oldPos=self.world_position, newPos=newPos))
                self.enqueuePositionUpdate(pos)
            else:
                del self.predictionHistory[originalPacketId]
        else:
            self.enqueuePositionUpdate(pos)


    def doMovePrediction(self, map, pcktId, direction):
        oldPos = self.world_position
        dx, dy = MOVEMENT_VALUES[direction]
        newPos = sf.Vector2(oldPos.x + (dx * self.velocity.x), oldPos.y + (dy * self.velocity.y))

        map_width, map_height = map.size
        if newPos.x < 0 or newPos.x > map_width:
            return

        if newPos.y < 0 or newPos.y > map_height:
            return

        self.predictionHistory[pcktId] = newPos
        self.enqueuePositionUpdate(self.toLocalPosition(newPos))

    def draw(self, window):
        if self.sprite:
            window.draw(self.sprite)
