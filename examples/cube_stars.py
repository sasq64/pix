# Solid cube with starfield - example for pixpy

from typing import Final
import pixpy as pix
import numpy as np
import math
import random


def make_x_mat(a: float):
    """Create a matrix that rotates a 3D point around the X-axis by `a` degrees"""
    return np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(a), -math.sin(a)],
            [0.0, math.sin(a), math.cos(a)],
        ]
    )


def make_y_mat(a: float):
    """Create a matrix that rotates a 3D point around the Y-axis by `a` degrees"""
    return np.array(
        [
            [math.cos(a), 0.0, math.sin(a)],
            [0.0, 1.0, 0.0],
            [-math.sin(a), 0.0, math.cos(a)],
        ]
    )


def make_z_mat(a: float):
    """Create a matrix that rotates a 3D point around the Z-axis by `a` degrees"""
    return np.array(
        [
            [math.cos(a), -math.sin(a), 0.0],
            [math.sin(a), math.cos(a), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )


vertices = np.array(
    [
        [1, 1, 1],
        [1, 1, -1],
        [1, -1, 1],
        [1, -1, -1],
        [-1, 1, 1],
        [-1, 1, -1],
        [-1, -1, 1],
        [-1, -1, -1],
    ]
)

normals = np.array(
    [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]]
)

quads = np.array(
    [[3, 2, 0, 1], [6, 7, 5, 4], [4, 5, 1, 0], [3, 7, 6, 2], [2, 6, 4, 0], [5, 7, 3, 1]]
)


class CubeDemo:

    def __init__(self, screen: pix.Screen):

        self.screen: Final = screen
        self.speed: tuple[float, float, float] = (2.8, 0.2, 0.05)
        self.rgb: tuple[float, float, float] = (0.5, 0.2, 1)

        # Create starfield
        sz = screen.size / 3
        self.planes: Final = [pix.Image(size=sz) for _ in range(3)]
        for i, plane in enumerate(self.planes):
            v = (i + 1) / 3
            c = pix.rgba(v, v, v, 1)
            for y in range(plane.size.toi().y // 3):
                plane.set_pixel((random.randint(0, plane.size.toi().x), y * 3 + i), c)

    def render(self):
        self.screen.clear()
        # Render starfield
        self.screen.draw_color = pix.color.WHITE
        for i, plane in enumerate(self.planes):
            x = (self.screen.seconds * 50 * (i + 1)) % self.screen.size.x
            self.screen.draw(image=plane, top_left=(x, 0), size=self.screen.size)
            self.screen.draw(
                image=plane, top_left=(x - self.screen.size.x, 0), size=self.screen.size
            )

        # Rotate cube
        t = self.screen.seconds
        center = self.screen.size / 2
        xa = t * self.speed[0]
        ya = t * self.speed[1]
        za = t * self.speed[2]

        # Transform points
        mat = make_x_mat(xa) @ make_y_mat(ya) @ make_z_mat(za)

        points = [v @ mat for v in vertices]
        norms = [v @ mat for v in normals]
        points2d: list[pix.Float2] = [
            pix.Float2(v[0], v[1]) * (5 / (v[2] + 4)) * center.y / 3 + center
            for v in points
        ]

        # Render cube
        for i, q in enumerate(quads):
            c: float = -norms[i][2]
            if c > 0:
                r, g, b = self.rgb
                self.screen.draw_color = pix.rgba(r * c, g * c, b * c, 1)
                self.screen.polygon([points2d[x] for x in q], convex=True)


def main():
    screen = pix.open_display(size=(1280, 720))
    screen.fps = 0
    demo = CubeDemo(screen)
    while pix.run_loop():
        demo.render()
        screen.swap()


if __name__ == "__main__":
    main()
