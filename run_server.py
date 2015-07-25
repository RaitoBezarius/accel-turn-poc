from twisted.internet import reactor, endpoints
from server.world import World

def main():
    theWarudo = World()
    theWarudo.initialize()

    reactor.run()

if __name__ == '__main__':
    main()
