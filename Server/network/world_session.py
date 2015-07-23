from twisted.internet import protocol
from packet import Packet
from opcodes import Opcodes, defineOpcodes

class WorldSession(protocol.Protocol):

    def __init__(self):
        self.currentPacket = Packet()
        self.currentBytes = bytes()

        self.player = None
        self.opcodesTable = defineOpcodes([
                ("MSG_NULL", self.handleNULL),
                ("MSG_INITIAL_CONNECTION", self.handleInitialConnection),
                ("MSG_CAST_SPELL", self.handleCastSpell),
                ("CMSG_MOVE", self.handleMove)
                ("SMSG_NOTIFICATION", self.handleNULL),
                ("SMSG_MOVE_OBJECT", self.handleNULL),
                ("SMSG_REMOVE_SPELL", self.handleNULL),
                ("MSG_CHAT_MESSAGE", self.handleChatMessage)
            ])

    def assertValidPlayer(self):
        if not self.player:
            self.transport.loseConnection()

    def connectionMade(self):
        print ('Player connected.')

    def connectionLost(self):
        plr.cleanup()

    def dataReceived(self, data):
        data = self.currentBytes + data
        self.currentBytes = bytes()

        if not self.currentPacket.isHeaderComplete():
            bytesRead = self.currentPacket.consumeHeader(data)
            self.currentBytes += data[bytesRead:]
        else:
            bytesRead = self.currentPacket.consumeContent(data)
            self.currentBytes += data[bytesRead:]

        if self.currentPacket.isComplete():
            self.handlePacket(self.currentPacket)
            self.currentPacket = Packet()


    def handlePacket(self, packet):
        if packet.opcode == Opcodes.MSG_NULL:
            print ('Received a NULL opcode!')

        print ('Received %s opcode.' % (self.opcodesTable[packet.opcode].name))
        self.opcodesTable[packet.opcode].handler(packet)

    def handleNULL(self, packet):
        # Received either a NULL or unexpected packet.
        pass

    def handleInitialConnection(self, packet):
        # Received initial parameters from client.
        # Window size, player name, etc...
        playerName = packet.readString()

        plr = Player(playerName)
        plr.bindSession(self)

        self.player = plr

        # Answer by a initial connection with the player ID.
        pckt = Packet.construct(MSG_INITIAL_CONNECTION)
        pckt.writeBool(True)
        pckt.writeUint64(self.player.objectId)

        self.sendPacket(pckt)

        print ('Connection established with player: {}'.format(playerName))

    def handleCastSpell(self, packet):
        self.assertValidPlayer()
        spellId = packet.readUint32()
        angle = packet.readFloat()


    def handleMove(self, packet):
        # Handle player's movements.
        direction = packet.readUint8()
        if player.move(direction):
            player.sendPositionUpdateToMap()

    def sendPacket(self, pckt):
        self.transport.write(pckt.serialize())

    def sendNotification(self, message):
        pckt = Packet.construct(SMSG_NOTIFICATION);
        pckt.writeString(message)

        self.sendPacket(pckt)


class WorldSessionFactory(protocol.Factory):

    def buildProtocol(self, addr):
        print ('%s connected.' % (addr))
        return WorldSession()
