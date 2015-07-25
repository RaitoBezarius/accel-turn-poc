from unit import Unit
from shared.network.packet import Packet
from shared.network.opcodes import Opcodes

class Player(Unit):

    def __init__(self, name, tileSize, tilesetFilename, tilesetPos):
        super(Unit, self).__init__(1) # Should generate purely randomly one.
        self.name = name
        self.session = None

        self.tileSize = tileSize
        self.tilesetFilename = tilesetFilename
        self.tilesetPos = tilesetPos

        self.lastDirection = None

    def update(self, diff):
        pass

    def packData(self):
        pckt = Packet.construct(Opcodes.SMSG_ADD_OBJECT)
        pckt.writeUint64(self.objectId)
        pckt.writeString(self.name, self.tilesetFilename)
        pckt.writeUint16(self.tileSize)
        pckt.writeUint32(self.position.x, self.position.y)
        pckt.writeUint32(self.tilesetPos.x, self.tilesetPos.y)

        return pckt

    def onInteract(self):
        pass

    def registerOnMap(self, mapObject):
        mapObject.registerPlayer(self)
        super(Player, self).registerOnMap(mapObject)

    def cleanup(self):
        if self.map:
            self.map.removeFromTileGrid(self)
            self.map.unregisterPlayer(self)
        print ('Cleaned player %s successfully.' % (self.name))

    def bindSession(self, session):
        self.session = session

    def move(direction):
        lastDirection = direction
        if self.currentMap.checkIfOutside(self.pos, direction):
            return False

        # Check if there is nothing to collide with.
        # If not, let's update our position from Map.

        return False

    def sendPacket(self, packet):
        assert (self.session is not None)
        self.session.sendPacket(packet)
