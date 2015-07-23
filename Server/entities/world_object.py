from network.packet import Packet
from network.opcodes import Opcodes

class WorldObject(object):

    def __init__(self, objectId):
        self.objectId = objectId
        self.position = Vector2(0, 0)
        self.map = None

    def sendPositionUpdateToMap(self):
        pckt = Packet.construct(Opcodes.MSG_MOVE_OBJECT)
        pckt.writeUint64(self.objectId)
        pckt.writeInt32(self.position.x)
        pckt.writeInt32(self.position.y)

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
