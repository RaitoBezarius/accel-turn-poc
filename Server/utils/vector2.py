from collections import namedtuple

Vector2 = namedtuple('Vector2', 'x y')

def applyPosition(initial, delta):
    initial.x += delta.x
    initial.y += delta.y
    return initial
