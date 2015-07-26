from twisted.internet import protocol
from shared.network.packet import Packet
from shared.network.opcodes import Opcodes, defineOpcodes
from server.entities.player import Player
from server.utils.vector2 import Vector2

class WorldSession(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory

        self.currentPacket = Packet()
        self.lastBytes = str()

        self.player = None

    def assertValidPlayer(self):
        if not self.player:
            self.transport.loseConnection()

    def connectionMade(self):
        print ('Player connected.')

    def connectionLost(self, reason):
        print ('Player lost the connection: %s.' % (reason))
        if self.player:
            self.player.cleanup()

    def dataReceived(self, data):
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
        # Received initial parameters from client.
        # Window size, player name, etc...
        playerName = packet.readString()
        tilesetFilename = packet.readString()
        tileSize = packet.readUint16()
        tx, ty = packet.read('!II')
        tilesetPos = Vector2(tx, ty)

        plr = Player(playerName, tileSize, tilesetFilename, tilesetPos)
        plr.bindSession(self)

        self.player = plr

        # Answer by a initial connection with the player ID.
        pckt = Packet.construct(Opcodes.MSG_INITIAL_CONNECTION)
        pckt.writeBool(True)
        pckt.writeUint64(self.player.objectId)
        pckt.writeUint32(1)

        self.sendPacket(pckt)

        print ('Initial connection established with player: {}'.format(playerName))

    def handleSpawnInGame(self, packet):
        if self.player.isInWorld():
            return

        self.player.registerOnMap(self.factory.world.worldMap)
        print ('Player {} spawned in the world map.'.format(self.player.name))

    def handleCastSpell(self, packet):
        self.assertValidPlayer()
        spellId = packet.readUint32()
        angle = packet.readFloat()


    def handleMove(self, packet):
        # Handle player's movements.
        direction = packet.readUint32()
        pcktId = packet._id

        self.player.move(pcktId, direction)

    def handleChatMessage(self, packet):
        pass

    def sendPacket(self, pckt):
        self.transport.write(pckt.serialize())

    def sendNotification(self, message):
        pckt = Packet.construct(SMSG_NOTIFICATION);
        pckt.writeString(message)

        self.sendPacket(pckt)


class WorldSessionFactory(protocol.Factory):

    def __init__(self, world):
        self.world = world
        self.opcodesTable = defineOpcodes([
                ("MSG_INITIAL_CONNECTION", WorldSession.handleInitialConnection),
                ("CMSG_CAST_SPELL", WorldSession.handleCastSpell),
                ("CMSG_MOVE", WorldSession.handleMove),
                ("CMSG_SPAWN_INGAME", WorldSession.handleSpawnInGame),
                ("MSG_CHAT_MESSAGE", WorldSession.handleChatMessage)
            ], WorldSession.handleNULL)

    def buildProtocol(self, addr):
        print ('%s connected.' % (addr))
        return WorldSession(self)
