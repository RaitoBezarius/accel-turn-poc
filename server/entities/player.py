from unit import Unit
from shared.network.packet import Packet
from shared.network.opcodes import Opcodes
from shared.constants.movement import MOVEMENT_VALUES
from server.utils.vector2 import Vector2

from collections import deque

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

        self.movesHistory = deque()
        self.lastDirection = None

        self.simulationTime = 0

        Player.seqId += 1

    def applyMove(self, direction):
        oldPos = self.position
        dx, dy = MOVEMENT_VALUES[direction]
        position = Vector2(oldPos.x + (dx * self.velocity.x), oldPos.y + (dy * self.velocity.y))

        if not self.map.isValidPos(position):
            return False

        self.position = position
        if self.position != oldPos:
            self.map.updateOnTileGrid(oldPos, self)

        print ('({oldPos.x}, {oldPos.y}) => ({newPos.x}, {newPos.y})'
            .format(oldPos=oldPos, newPos=position))

        return True

    def update(self, diff):
        packetId = None
        oldPosition = self.position
        if len(self.movesHistory) > 0:
            packetId, direction = self.movesHistory.popleft()

            self.applyMove(direction)

        self.simulationTime += (diff * 100)
        self.sendPositionUpdateToMap(diff, packetId, ignoreMyself=(oldPosition == self.position))
        print ('Sent position at t = {} ms.'.format(self.simulationTime))


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
        self.movesHistory.append((pcktId, direction))


    def sendPacket(self, packet):
        assert (self.session is not None)
        self.session.sendPacket(packet)
