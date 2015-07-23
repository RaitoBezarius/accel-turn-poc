from utils.grid import WorldObjectGrid
from utils.vector2 import applyPosition

from functools import partial

from player import Player

class Map:

    def __init__(self, guid, width, height):
        self.grid = WorldObjectGrid(width, height)

        self.spells = set()
        self.spellBoxID = 0

    def isValidPos(self, pos):
        for coordinate in (self.pos.x, self.pos.y):
            if coordinate < 0:
                return False

        if self.pos.x > self.grid.width or self.pos.y > self.grid.height:
            return False


    def checkOutside(self, pos, direction):
        moves = {
            MOVE_UP: (0, 1),
            MOVE_DOWN: (0, -1),
            MOVE_LEFT: (-1, 0),
            MOVE_RIGHT: (1, 0)
        }

        newPos = applyPosition(pos, self.moves[direction])
        return self.isValidPos(newPos)

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

    def addSpell(self, caster, spellTemplate, angle):
        raise NotImplemented

    def registerPlayer(self, player):
        newPlrData = player.packData()

        for unit in self.grid:
            unitData = unit.packData()
            player.sendPacket(unitData)
            unit.sendPacket(newPlrData)

        player.sendPacket(newPlrData)

    def unregisterPlayer(self, player):
        pckt = Packet.construct(Opcode.SMSG_REMOVE_OBJECT)
        pckt.writeUint64(player.objectId)

        self.grid.remove(player)
        for unit in self.grid:
            unit.sendPacket(pckt)

    def broadcastPacket(self, pckt):
        map(lambda player: player.sendPacket(pckt), filter(lambda unit: isinstance(unit, Player), self.grid))

