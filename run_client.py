from twisted.internet import reactor
import math
import time
import sfml as sf

from client.network.world_session import WorldSessionFactory
from client.screens.loading_screen import LoadingScreen

class Game:

    def __init__(self):
        self.window = sf.RenderWindow(sf.VideoMode(640, 480), "Acceleration - Proof of Concept")
        self.window.framerate_limit = 60
        self.state = []
        self.lastDiff = 0

    def pushState(self, state):
        self.state.append(state)

    def popState(self, state):
        self.state.pop(0)

    def popAllStates(self):
        self.state = []

    def loop(self):
        if not self.state:
            print ('No state provided !')
            reactor.stop()
            return

        while self.window.is_open:
            diff = time.time() - self.lastDiff

            for event in self.window.events:
                if type(event) is sf.CloseEvent:
                    self.window.close()

                self.state[0].handleEvent(self.window, event)

            self.window.clear()
            self.state[0].draw(self.window)
            self.window.display()
            # print ('Game loop executed in {} ms.'.format(math.floor(diff * 100)))
            self.state[0].update(diff)

            self.lastDiff += diff

        reactor.stop()

def main():
    game = Game()

    game.pushState(LoadingScreen())
    reactor.callInThread(game.loop)

    reactor.connectTCP("127.0.0.1", 8799, WorldSessionFactory(game))
    reactor.run()


if __name__ == '__main__':
    main()
