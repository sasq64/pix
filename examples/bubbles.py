import math

import pixpy as pix

screen = pix.open_display(size=(1280, 720))

n = 250
r = 2 * math.pi / 195
x, y, v, t = 0.0, 0.0, 0.0, 0.0
points = [0.0] * n * n * 2
colors = [0] * n * n
screen.point_size = 8.0
while pix.run_loop():
    screen.clear()
    cx, cy = screen.size / 2
    s = screen.size.y / 4.1
    screen.point_size = screen.size.y / 300

    for i in range(n):
        col = pix.rgba(i / n, 0, 99 / 200, 0.5)
        ri = r * i
        for j in range(i * n, (i + 1) * n):
            u = math.sin(i + v) + math.sin(ri + x)
            v = math.cos(i + v) + math.cos(ri + x)
            x = u + t
            colors[j] = col
            # `u` and `v` are between -2 and 2 at this point
            # We need to scale them up and move them to the center
            points[j * 2] = u * s + cx
            points[j * 2 + 1] = v * s + cy
            col += 0x00010002
    t += 0.005
    screen.plot(points, colors)
    screen.swap()

