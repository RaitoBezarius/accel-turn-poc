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

        x, y, tx, ty = packet.read('!iiII')

        texture = world.texture_loader.load(tileset, color_mask=sf.Color.WHITE)
        self.sprite = sf.Sprite(texture)
        self.sprite.color = sf.Color.WHITE
        self.sprite.texture_rectangle = sf.Rectangle(sf.Vector2(tx * self.tileSize, ty * self.tileSize), sf.Vector2(self.tileSize, self.tileSize))
        self.sprite.position = sf.Vector2(x * self.tileSize, y * self.tileSize)

        print ('World object (id: %d, name: %s) loaded in the world.' % (self.objectId, self.name))

    def update(self, diff):
        pass

    def updatePosition(self, newPos):
        pos = sf.Vector2(newPos.x * self.tileSize, newPos.y * self.tileSize)
        print ("New pos is %f;%f" % (pos.x, pos.y))
        self.sprite.position = pos

    def draw(self, window):
        if self.sprite:
            window.draw(self.sprite)
