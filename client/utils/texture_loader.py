import sys
import sfml as sf

class TextureLoader(object):

    def __init__(self):
        self.textures = {}

    def load(self, filename):
        if filename in self.textures:
            return self.textures[filename]

        try:
            self.textures[filename] = sf.Texture.from_file(filename)
            return self.textures[filename]
        except IOError as e:
            print ('Error when trying to load texture: %s (%s)' % (filename, e))
            sys.exit(1)
