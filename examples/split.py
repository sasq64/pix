from pathlib import Path
import pixpy as pix
import utils.tween as tween

data_dir = Path(__file__).absolute().parent / "data"

s = 3
screen = pix.open_display(size=(320 * s, 200 * s))
image = pix.load_png(data_dir / "face.png")
sprites = [(sprite, sprite.pos) for sprite in image.split(width=32, height=32)]

for sprite in sprites:
    sprite[1].tween_from(screen.size.random(), 4, tween.Ease.in_out_elastic)

while pix.run_loop():
    screen.clear()
    for sprite in sprites:
        screen.draw(image=sprite[0], top_left=sprite[1] * s, size=sprite[0].size * s)
    screen.swap()

