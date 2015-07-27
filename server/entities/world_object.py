from shared.network.packet import Packet
from shared.network.opcodes import Opcodes

import sfml as sf

class WorldObject(object):

    def __init__(self, objectId):
        self.objectId = objectId
        self.position = sf.Vector2(0, 0)
        self.velocity = sf.Vector2(1, 1)
        self.map = None

    def isInWorld(self):
        return self.map is not None

    def registerOnMap(self, mapObject):
        self.map = mapObject
        self.map.addToTileGrid(self)

    def sendPositionUpdateToMap(self, diff, packetId=None, ignoreMyself=False):
        pckt = Packet.construct(Opcodes.SMSG_MOVE_OBJECT)
        pckt.writeUint64(self.objectId)
        pckt.writeVector(self.position, self.velocity)

        self.map.broadcastPlayers(pckt, exclude=[self.objectId])

        if not ignoreMyself:
            if packetId is not None:
                pckt.writeUint64(packetId)

            self.sendPacket(pckt)

    def updatePosition(self, pos):
        self.map.removeFromTileGrid(self)
        self.position = pos
        self.map.addToTileGrid(self)
        self.sendPositionUpdateToMap()

    def __eq__(self, other):
        return self.objectId == other.objectId

    def update(self, diff):
        raise NotImplemented

    def packData(self):
        raise NotImplemented

    def onInteract(self):
        raise NotImplemented

    # It's a no-op for most of classes except Player.
    def sendPacket(self, packet):
        pass
