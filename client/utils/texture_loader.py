import sys
import sfml as sf

class TextureLoader(object):

    def __init__(self):
        self.images = {}
        self.textures = {}

    def load(self, filename, color_mask=None, alpha_mask=None):
        if filename in self.textures:
            return self.textures[filename]
        try:
            context = sf.Context()
            self.images[filename] = sf.Image.from_file("data/tilesets/{}".format(filename))
            if color_mask is not None:
                self.images[filename].create_mask_from_color(color_mask, alpha_mask or 0)
            self.textures[filename] = sf.Texture.from_image(self.images[filename])
            return self.textures[filename]
        except IOError as e:
            print ('Error when trying to load texture: %s (%s)' % (filename, e))
