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

        text.character_size = 30
        text.color = sf.Color.BLUE

        window.draw(text)
