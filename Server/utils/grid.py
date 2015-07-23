class WorldObjectGrid:

    def __init__(self, width, height):
        self.grid = [[None] * height for _ in range(width)]
        self.objects = set()

    def __iter__(self):
        return iter(self.objects)

    def add(self, wObject):
        if issubclass(wObject, Unit):
            self.objects.add(wObject)

        self.grid[wObject.x][wObject.y] = wObject

    def remove(self, wObject):
        if issubclass(wObject, Unit):
            self.objects.remove(wObject)

        self.grid[wObject.x][wObject.y] = None
