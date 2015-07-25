import time
import math
from network.world_session import WorldSessionFactory
from entities.map import Map

from twisted.internet import task
from twisted.internet import endpoints
from twisted.internet import reactor

class World(object):

    def __init__(self, heartbeat_delay=50):
        self.heartbeat_delay = heartbeat_delay / 100.0
        self.heartbeat = task.LoopingCall(self.update)

        self.lastDiff = time.time()

        self.maps = {}
        self.worldMap = Map(1, 30, 20)

        self.maps['default'] = self.worldMap

    def initialize(self):
        print ('Initializing the world...')

        # Accept new players.
        endpoints.serverFromString(reactor, "tcp:8799").listen(WorldSessionFactory(self))

        # Start the heartbeat
        self.heartbeat.start(self.heartbeat_delay)

        # Call the CLI handler.
        reactor.callInThread(self.CLI)

        print ('World initialized.')

    def update(self):
        diff = (time.time() - self.lastDiff)
        # print ('World updated in {} ms.'.format(math.floor(diff * 100)))
        for mapId, mapObject in self.maps.items():
            mapObject.update(diff)
        self.lastDiff += diff

    def CLI(self):
        pass
