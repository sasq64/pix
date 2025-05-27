# Solid cube with starfield - example for pixpy

import pixpy as pix
import numpy as np
import math
import random


def make_x_mat(a: float):
    """Create a matrix that rotates a 3D point around the X-axis by `a` degrees"""
    return np.array([[1.0, 0.0, 0.0],
                    [0.0, math.cos(a), -math.sin(a)],
                    [0.0, math.sin(a), math.cos(a)]])


def make_y_mat(a: float):
    """Create a matrix that rotates a 3D point around the Y-axis by `a` degrees"""
    return np.array([[math.cos(a), 0.0, math.sin(a)],
                     [0.0, 1.0, 0.0],
                     [-math.sin(a), 0.0, math.cos(a)]])


def make_z_mat(a: float):
    """Create a matrix that rotates a 3D point around the Z-axis by `a` degrees"""
    return np.array([[math.cos(a), -math.sin(a), 0.0],
                     [math.sin(a), math.cos(a), 0.0],
                     [0.0, 0.0, 1.0]])


vertices = np.array([
    [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
    [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
])

normals = np.array([
    [1, 0, 0], [-1, 0, 0], [0, 1, 0],
    [0, -1, 0], [0, 0, 1], [0, 0, -1]
])

quads = np.array([
    [3, 2, 0, 1], [6, 7, 5, 4], [4, 5, 1, 0],
    [3, 7, 6, 2], [2, 6, 4, 0], [5, 7, 3, 1]
])

screen = pix.open_display(size=(1280, 720))
screen.fps = 0

# Create starfield
sz = screen.size / 3
planes = [pix.Image(size=sz) for _ in range(3)]
for i,plane in enumerate(planes):
    v = (i+1) / 3
    c = pix.rgba(v, v, v, 1)
    for y in range(plane.size.toi().y//3):
        plane.set_pixel((random.randint(0,plane.size.toi().x), y*3+i), c)

while pix.run_loop():

    screen.clear()

    # Render starfield
    screen.draw_color = pix.color.WHITE
    for i,plane in enumerate(planes):
        x = (screen.seconds * 50 * (i + 1)) % screen.size.x
        screen.draw(image=plane, top_left=(x, 0), size=screen.size)
        screen.draw(image=plane, top_left=(x - screen.size.x, 0), size=screen.size)

    # Rotate cube
    t = screen.seconds
    center = screen.size / 2
    xa = t * 0.8
    ya = t * 0.2
    za = t * 0.05

    # Transform points 
    mat = make_x_mat(xa) @ make_y_mat(ya) @ make_z_mat(za)

    points = [v @ mat for v in vertices]
    norms = [v @ mat for v in normals]
    points2d : list[pix.Float2] = [pix.Float2(v[0], v[1]) * (5/(v[2] + 4))
         * center.y/3 + center for v in points]

    # Render cube
    for i, q in enumerate(quads):
        c = -norms[i][2]
        if c > 0 :
            screen.draw_color = pix.rgba(0, 0, c, 1)
            screen.polygon([points2d[x] for x in q], convex = True)

    screen.swap()
