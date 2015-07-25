from server.entities.unit import Unit

def isUnit(entity):
    return issubclass(entity.__class__, Unit)

class WorldObjectGrid:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[None] * height for _ in range(width)]
        self.objects = set()

    def __iter__(self):
        return iter(self.objects)

    def add(self, wObject):
        if isUnit(wObject):
            self.objects.add(wObject)

        self.grid[wObject.position.x][wObject.position.y] = wObject

    def remove(self, wObject):
        if isUnit(wObject):
            self.objects.remove(wObject)

        self.grid[wObject.position.x][wObject.position.y] = None

    def updatePosition(self, oldPos, wObject):
        try:
            self.grid[oldPos.x][oldPos.y] = None
            self.grid[wObject.position.x][wObject.position.y] = wObject
        except IndexError:
            print ('Failed to update position, bad position in the grid.')
