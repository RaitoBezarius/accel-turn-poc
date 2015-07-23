from world_object import WorldObject
from network.packet import Packet
from network.opcodes import Opcodes

class Unit(WorldObject):

    def __init__(self, objectId):
        super(Unit, self).__init__(objectId)

        self.health = 100

    def teleport(pos):
        self.updatePosition(pos)

    def spellHit(spellBox):
        pckt = Packet.construct(Opcodes.MSG_REMOVE_SPELL)
        pckt.writeUint16(spellBox.boxId)
        self.map.broadcastPacket(pckt)
        self.takeDamage(spellBox.template.value, spellBox.caster)

    def castSpell(spell, angle):
        pckt = Packet.construct(Opcodes.MSG_CAST_SPELL)
        pckt.writeUint64(self.objectId)
        pckt.writeUint32(spell.effect)
        pckt.writeUint32(spell.displayId)
        pckt.writeFloat(angle)
        pckt.writeUint16(self.map.generateSpellBoxID())

        self.map.broadcastPacket(pckt)
        self.map.addSpell(self, spell, angle)

    def say(text):
        self.onChat(text)

        pckt = Packet.construct(MSG_CHAT_MESSAGE)
        pckt.writeUint64(self.objectId)
        pckt.writeString(text)

        self.map.broadcastPacket(pckt)

    def takeDamage(damage, attacker):
        self.health = 0 if self.health - damage <= 0 else self.health - damage

    def dealDamage(damage, target):
        target.takeDamage(damage, self)

    def isAlive(self):
        return self.health > 0

    def kill(self):
        self.health = 0
