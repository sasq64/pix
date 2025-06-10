import pixpy as pix
from random import random

from cube_stars import CubeDemo

screen = pix.open_display(size=(1280, 720))

splits = screen.split(size=(8, 6))
cubes: list[CubeDemo] = []
for split in splits:
    demo = CubeDemo(split)
    demo.rgb = (random() * 0.5 + 0.5, random() * 0.5 + 0.5, random() * 0.5 + 0.5)
    demo.speed = (random() * 2 - 1, random() * 2 - 1, random() * 2 - 1)
    cubes.append(demo)


while pix.run_loop():
    for cube in cubes:
        cube.render()
    screen.swap()
