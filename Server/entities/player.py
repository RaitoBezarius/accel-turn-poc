from unit import Unit

class Player(Unit):

    def __init__(self, name):
        super(Unit, self).__init__(1) # Should generate purely randomly one.
        self.name = name
        self.session = None

        self.lastDirection = None

    def cleanup(self):
        self.map.removeFromTileMap(self)
        self.map.unregisterPlayer(self)

    def bindSession(session):
        self.session = session

    def move(direction):
        lastDirection = direction
        if self.currentMap.checkIfOutside(self.pos, direction):
            return False

        # Check if there is nothing to collide with.
        # If not, let's update our position from Map.

        return False

    def sendPacket(self, packet):
        assert (self.session is not None)
        self.session.sendPacket(packet)
