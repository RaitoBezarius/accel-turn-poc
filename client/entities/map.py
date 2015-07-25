import json
import sfml as sf

class Map(object):

    def __init__(self, filename):
        self.size = (0, 0)
        self.map_id = None
        self.filename = filename

    def multiply_size(self, mul):
        width, height = self.size
        width *= mul
        height *= mul
        self.size = (width, height)

    def load(self):
        raise NotImplemented

    def save(self):
        raise NotImplemented

    def draw(self, window):
        raise NotImplemented

class TileMap(Map, sf.Drawable):

    def __init__(self, map_id):
        sf.Drawable.__init__(self)
        super(TileMap, self).__init__("data/maps/map{id}.map".format(id=map_id))
        self.map_id = map_id

        self.tilesetFilename = None
        self.tilesetTexture = None
        self.tileSize = None

        self.tileMap = sf.VertexArray(sf.PrimitiveType.QUADS)

    def load(self, texture_loader):
        try:
            data_file = None
            with open(self.filename, 'r') as map_file:
                data_file = map_file.read()

            structured_data = json.loads(data_file)
            self.size = (structured_data['width'], structured_data['height'])
            print ('Map size: %d, %d' % self.size)
            self.tilesetFilename = structured_data['tileset']['filename']
            print ('Map tileset: %s' % (self.tilesetFilename))
            self.tileSize = structured_data['tileset']['size']
            print ('Map tilesize: %d' % (self.tileSize))

            self.tilesetTexture = texture_loader.load(self.tilesetFilename)

            self.tileMap.resize(self.size[0] * self.size[1] * 4)
            self.multiply_size(self.tileSize)

            index = 0

            for x, y, tx, ty in structured_data['map']:
                variations = [(0, 0), (0, 1), (1, 1), (1, 0)]
                for delta_index, delta_pos in enumerate(variations):
                    dx, dy = delta_pos
                    self.tileMap[index + delta_index].position = sf.Vector2((x + dx) * self.tileSize, (y + dy) * self.tileSize)
                    self.tileMap[index + delta_index].tex_coords = sf.Vector2((tx + dx) * self.tileSize, (ty + dy) * self.tileSize)

                index += 4
        except IOError as e:
            print ('Failed to load map (reason: %s)' % (e))

    def save(self):
        self._save(self._getMapContent())

    def _save(self, map_content):
        map_data = {
            'width': self.size[0],
            'height': self.size[1],
            'tileset': {
                'filename': self.tilesetFilename,
                'size': self.tileSize
            },
            'map': map_content
        }

        with open(self.filename, 'w') as map_file:
            map_file.write(json.dumps(map_data, sort_keys=True, indent=2))

    def _getMapContent(self):
        map_content = []
        for tile in self.tileMap[::4]:
            tpl = (tile.position.x, tile.position.y, tile.position.tx, tile.position.ty)
            map_content.append(tpl)

    def draw(self, target, states):
        states.texture = self.tilesetTexture
        target.draw(self.tileMap, states)
