from twisted.internet import protocol
from shared.network.packet import Packet
from shared.network.opcodes import Opcodes, defineOpcodes

from client.entities.world_object import WorldObject
from client.world import World

import sfml as sf

class WorldSession(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory

        self.currentPacket = Packet()
        self.lastBytes = bytes()

        self.world = None

    def connectionMade(self):
        print ('Connected to server.')
        self.sendInitialConnection()

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        print ('Received data: %s' % (data))

        while len(data) >= Packet.HeaderSize:
            if not self.currentPacket.isHeaderComplete():
                bytesRead = self.currentPacket.consumeHeader(data)
                data = data[bytesRead:]

            if self.currentPacket.isHeaderComplete():
                bytesRead = self.currentPacket.consumeContent(data)
                data = data[bytesRead:]

            if self.currentPacket.isComplete():
                self.handlePacket(self.currentPacket)
                self.currentPacket = Packet()

        self.lastBytes = data


    def handlePacket(self, packet):
        if packet.opcode == Opcodes.MSG_NULL:
            print ('Received a NULL opcode!')

        print ('Received %s opcode.' % (self.factory.opcodesTable[packet.opcode].name))
        self.factory.opcodesTable[packet.opcode].handler(self, packet)

    def handleNULL(self, packet):
        # Received either a NULL or unexpected packet.
        pass

    def handleInitialConnection(self, packet):
        success = packet.readBool()
        if success:
            playerId = packet.readUint64()
            mapId = packet.readUint32()

            self.world = World(playerId, mapId)
            self.world.load()

            self.factory.game.popAllState()
            self.factory.game.pushState(self.world)

            pckt = Packet.construct(Opcodes.CMSG_SPAWN_INGAME)
            self.sendPacket(pckt)
        else:
            print ('Initial connection refused by the server.')

    def handleCastSpell(self, packet):
        pass

    def handleNotification(self, packet):
        message = packet.readString()

    def handleMoveObject(self, packet):
        objectId = packet.readUint64()
        x, y = packet.read("!II")
        self.world.worldObjects[objectId].updatePosition(sf.Vector2f(x, y))

    def handleRemoveObject(self, packet):
        objectId = packet.readUint64()
        self.world.removeObject(objectId)

    def handleAddObject(self, packet):
        objectId = packet.readUint64()

        worldObject = WorldObject(objectId)
        worldObject.load(self.world, packet)

        self.world.addObject(worldObject)

    def handleChatMessage(self, packet):
        message = packet.readString()

    def sendInitialConnection(self):
        pckt = Packet.construct(Opcodes.MSG_INITIAL_CONNECTION)
        pckt.writeString("Raito Bezarius", "dg_classm32.gif")
        pckt.writeUint16(32)
        pckt.writeUint32(0, 0)

        self.sendPacket(pckt)

    def sendPacket(self, pckt):
        self.transport.write(pckt.serialize())


class WorldSessionFactory(protocol.ClientFactory):

    def __init__(self, gameInstance):
        self.game = gameInstance
        self.opcodesTable = defineOpcodes([
                ("MSG_INITIAL_CONNECTION", WorldSession.handleInitialConnection),
                ("SMSG_NOTIFICATION", WorldSession.handleNotification),
                ("SMSG_MOVE_OBJECT", WorldSession.handleMoveObject),
                ("SMSG_ADD_OBJECT", WorldSession.handleAddObject),
                ("SMSG_REMOVE_OBJECT", WorldSession.handleRemoveObject),
                ("MSG_CHAT_MESSAGE", WorldSession.handleChatMessage)
            ], WorldSession.handleNULL)

    def buildProtocol(self, addr):
        print ('%s connected.' % (addr))
        return WorldSession(self)

    def clientConnectionLost(self, connector, reason):
        print ('Lost connection, reason: %s' % (reason))
        self.game.window.close()
        # connector.connect()
