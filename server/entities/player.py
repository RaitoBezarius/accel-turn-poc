from unit import Unit
from shared.network.packet import Packet
from shared.network.opcodes import Opcodes
from shared.constants.movement import MOVEMENT_VALUES
from server.utils.vector2 import Vector2

from collections import OrderedDict

import sfml as sf

class Player(Unit):

    seqId = 1

    def __init__(self, name, tileSize, tilesetFilename, tilesetPos):
        super(Unit, self).__init__(self.seqId)
        self.name = name
        self.session = None

        self.tileSize = tileSize
        self.tilesetFilename = tilesetFilename
        self.tilesetPos = tilesetPos

        self.movesHistory = OrderedDict()
        self.lastDirection = None

        Player.seqId += 1

    def update(self, diff):
        for pcktId, direction in self.movesHistory.items():
            oldPos = self.position
            dx, dy = MOVEMENT_VALUES[direction]
            self.position = Vector2(oldPos.x + (dx * self.velocity.x), oldPos.y + (dy * self.velocity.y))

            if not self.map.isValidPos(self.position):
                self.position = oldPos
                continue

            if self.position != oldPos:
                self.map.updateOnTileGrid(oldPos, self)
                self.sendPositionUpdateToMap(diff, pcktId)

        self.movesHistory.clear()


    def packData(self):
        pckt = Packet.construct(Opcodes.SMSG_ADD_OBJECT)
        pckt.writeUint64(self.objectId)
        pckt.writeString(self.name, self.tilesetFilename)
        pckt.writeUint16(self.tileSize)
        pckt.writeVector(self.position, self.velocity, self.tilesetPos)

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
        Player.seqId -= 1
        print ('Cleaned player %s successfully.' % (self.name))

    def bindSession(self, session):
        self.session = session

    def move(self, pcktId, direction):
        if self.map.checkIfOutside(self.position, direction):
            return

        # TODO: Check if there is nothing to collide with.
        # If not, let's add this position to our move history.

        lastDirection = direction
        self.movesHistory[pcktId] = direction


    def sendPacket(self, packet):
        assert (self.session is not None)
        self.session.sendPacket(packet)
