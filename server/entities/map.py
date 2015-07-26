from server.utils.grid import WorldObjectGrid
from server.utils.vector2 import applyPosition
from shared.network.packet import Packet
from shared.network.opcodes import Opcodes
from shared.constants.movement import MOVEMENT_VALUES

from functools import partial

from player import Player


class Map:

    def __init__(self, guid, width, height):
        self.grid = WorldObjectGrid(width, height)

        self.spells = set()
        self.spellBoxID = 0

    def isValidPos(self, pos):
        if pos.x < 0 or pos.x > self.grid.width:
            return False
        elif pos.y < 0 or pos.y > self.grid.height:
            return False
        else:
            return True

    def checkIfOutside(self, pos, direction):
        return (not self.isValidPos(applyPosition(pos, MOVEMENT_VALUES[direction])))

    def update(self, diff):
        map(partial(self.unitUpdate, diff), self.grid)

    def unitUpdate(self, diff, unit):
        for spellBox in self.spells:
            if spellBox.caster != unit and spellBox.collidesWith(unit):
                unit.spellHit(spellBox)
                spells.remove(spellBox)

        unit.update(diff)

    def addToTileGrid(self, wObject):
        self.grid.add(wObject)

    def removeFromTileGrid(self, wObject):
        self.grid.remove(wObject)

    def updateOnTileGrid(self, oldPos, wObject):
        if self.isValidPos(oldPos) and self.isValidPos(wObject.position):
            self.grid.updatePosition(oldPos, wObject)

    def addSpell(self, caster, spellTemplate, angle):
        raise NotImplemented

    def registerPlayer(self, player):
        newPlrData = player.packData()
        assert (isinstance(newPlrData, Packet))

        for unit in self.grid:
            unitData = unit.packData()
            assert (isinstance(unitData, Packet))
            player.sendPacket(unitData)
            unit.sendPacket(newPlrData)

        player.sendPacket(newPlrData)

    def unregisterPlayer(self, player):
        pckt = Packet.construct(Opcodes.SMSG_REMOVE_OBJECT)
        pckt.writeUint64(player.objectId)

        for unit in self.grid:
            unit.sendPacket(pckt)

    def broadcastPlayers(self, pckt, exclude=None):
        if exclude is None:
            exclude = []

        map(lambda player: player.sendPacket(pckt), filter(lambda unit: (isinstance(unit, Player)) and (unit.objectId not in exclude), self.grid))

