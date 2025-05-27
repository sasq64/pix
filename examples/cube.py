import pixpy as pix
import numpy as np
import math


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


screen = pix.open_display(size=(1280, 720))
center = screen.size / 2
screen.line_width = 2

x_angle = 0.0
y_angle = 0.0
z_angle = 0.0

# 3D points that form the corners of a 1x1x1 cube
vertices = [[1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
            [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]]

# Indicates which points should be connected by lines
lines = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7),
         (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

screen.line_width = 6

while pix.run_loop():

    screen.clear()

    # Create a matrix that rotates a point around all 3 axises
    mat = make_x_mat(x_angle) @ make_y_mat(y_angle) @ make_z_mat(z_angle)

    # Rotate all points in `vertices` to `points`
    points = [v @ mat for v in vertices]

    # 3D -> 2D: Translate points to screen and add perspective
    points2d = [pix.Float2(v[0], v[1]) * (4/(v[2] + 3))
         * 150 + center for v in points]

    # Draw the lines using the transformed points
    for line in lines:
        screen.line(points2d[line[0]], points2d[line[1]])

    x_angle += 0.001
    y_angle += 0.002
    z_angle += 0.005
    screen.swap()
