import sfml as sf

from shared.constants.movement import MOVEMENT_VALUES

class WorldObject(object):

    def __init__(self, objectId):
        self.objectId = objectId
        self.tileSize = None
        self.sprite = None
        self.name = None
        self.velocity = None

        self.predictionHistory = {}

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
        pass

    @property
    def world_position(self):
        pos = self.sprite.position
        return sf.Vector2(pos.x / self.tileSize, pos.y / self.tileSize)

    def toLocalPosition(self, pos):
        return sf.Vector2(pos.x * self.tileSize, pos.y * self.tileSize)

    def updatePosition(self, originalPacketId, newPos, vel):
        if self.velocity != vel:
            self.velocity = vel

        pos = self.toLocalPosition(newPos)
        if originalPacketId not in self.predictionHistory:
            print ('Prediction correction (({oldPos.x}, {oldPos.y} vs ({newPos.x}, {newPos.y}))'.format(oldPos=self.world_position, newPos=newPos))
            self.sprite.position = pos
        else:
            del self.predictionHistory[originalPacketId]


    def doMovePrediction(self, pcktId, direction):
        oldPos = self.world_position
        dx, dy = MOVEMENT_VALUES[direction]
        newPos = sf.Vector2(oldPos.x + (dx * self.velocity.x), oldPos.y + (dy * self.velocity.y))

        self.predictionHistory[pcktId] = newPos
        self.sprite.position = self.toLocalPosition(newPos)

    def draw(self, window):
        if self.sprite:
            window.draw(self.sprite)
