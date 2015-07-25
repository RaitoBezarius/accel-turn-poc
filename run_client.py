from twisted.internet import reactor
import math
import time
import sfml as sf

from client.network.world_session import WorldSessionFactory
from client.screens.loading_screen import LoadingScreen

class Game:

    def __init__(self):
        self.state = []
        self.lastDiff = 0

    def initialize(self):
        self.context = sf.Context()
        self.window = sf.RenderWindow(sf.VideoMode(1024, 768), "Acceleration - Proof of Concept")
        self.window.framerate_limit = 60

    def pushState(self, state):
        self.state.append(state)

    def popState(self, state):
        self.state.pop(0)

    def popAllStates(self):
        self.state = []

    def loop(self):
        self.initialize()

        if not self.state:
            print ('No state provided !')
            reactor.stop()
            return

        while self.window.is_open:
            diff = time.time() - self.lastDiff

            for event in self.window.events:
                if type(event) is sf.CloseEvent:
                    reactor.stop()
                    self.window.close()

                self.state[0].handleEvent(self.window, event)

            self.state[0].update(diff)
            self.window.clear()
            self.state[0].draw(self.window)
            self.window.display()

            self.lastDiff += diff

def main():
    game = Game()

    game.pushState(LoadingScreen())
    reactor.callInThread(game.loop)

    reactor.connectTCP("127.0.0.1", 8799, WorldSessionFactory(game))
    try:
        reactor.run()
    except KeyboardInterrupt:
        if reactor.running:
            reactor.stop()


if __name__ == '__main__':
    main()
