from shared.network.packet import Packet
from shared.network.opcodes import Opcodes
from server.utils.vector2 import Vector2

class WorldObject(object):

    def __init__(self, objectId):
        self.objectId = objectId
        self.position = Vector2(0, 0)
        self.map = None

    def isInWorld(self):
        return self.map is not None

    def registerOnMap(self, mapObject):
        self.map = mapObject
        self.map.addToTileGrid(self)

    def sendPositionUpdateToMap(self):
        pckt = Packet.construct(Opcodes.MSG_MOVE_OBJECT)
        pckt.writeUint64(self.objectId)
        pckt.writeInt32(self.position.x, self.position.y)

        self.map.broadcastPlayers(pckt)

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
