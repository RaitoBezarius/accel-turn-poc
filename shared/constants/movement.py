import sfml as sf

MOVEMENT_VALUES = {
    None: (0, 0), # a.k.a Idle
    sf.Keyboard.UP: (0, -1),
    sf.Keyboard.DOWN: (0, 1),
    sf.Keyboard.LEFT: (-1, 0),
    sf.Keyboard.RIGHT: (1, 0)
}
