import sfml as sf

class LoadingScreen(object):

    def __init__(self):
        pass

    def handleEvent(self, window, event):
        pass

    def update(self, diff):
        pass

    def draw(self, window):
        text = sf.Text("Loading...")

        text.character_size = 50
        text.color = sf.Color.BLUE
        text.position = sf.Vector2(320, 220)

        window.draw(text)
