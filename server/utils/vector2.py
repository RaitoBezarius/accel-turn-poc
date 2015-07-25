import sfml as sf

Vector2 = sf.Vector2

def applyPosition(initial, delta):
    dx, dy = None, None

    if isinstance(delta, tuple):
        dx, dy = delta
    else:
        dx, dy = delta.x, delta.y

    newPos = Vector2(initial.x + dx, initial.y + dy)
    return newPos
