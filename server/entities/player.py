from unit import Unit
from shared.network.packet import Packet
from shared.network.opcodes import Opcodes
from shared.constants.movement import MOVEMENT_VALUES

from server.utils.vector2 import applyPosition

import sfml as sf

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
        pckt.writeInt32(self.position.x, self.position.y)
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

    def move(self, direction):
        lastDirection = direction
        if self.map.checkIfOutside(self.position, direction):
            return False

        oldPos = self.position

        self.position = applyPosition(self.position, MOVEMENT_VALUES[direction])
        self.map.updateOnTileGrid(oldPos, self)

        # TODO: Check if there is nothing to collide with.
        # If not, let's update our position from Map.

        return True

    def sendPacket(self, packet):
        assert (self.session is not None)
        self.session.sendPacket(packet)
