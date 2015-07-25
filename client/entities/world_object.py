import sfml as sf

class WorldObject(object):

    def __init__(self, objectId):
        self.objectId = objectId
        self.tileSize = None
        self.sprite = None
        self.name = None

    def load(self, world, packet):
        self.name = packet.readString()
        tileset = packet.readString()
        self.tileSize = packet.readUint16()

        x, y, tx, ty = packet.read('!IIII')

        texture = world.texture_loader.load(tileset)
        self.sprite = sf.Sprite(texture)
        self.sprite.color = sf.Color.WHITE
        self.sprite.texture_rectangle = sf.IntRect(tx * self.tileSize, ty * self.tileSize, self.tileSize, self.tileSize)
        self.sprite.position = sf.Vector2f(x * self.tileSize, y * self.tileSize)

        print ('World object (id: %d, name: %s) loaded in the world.' % (self.objectId, self.name))

    def update(self, diff):
        pass

    def updatePosition(self, newPos):
        pos = sf.Vector2f(newPos.x * self.tileSize, newPos.y * self.tileSize)
        self.sprite.position = pos

    def draw(self, window):
        window.draw(self.sprite)
