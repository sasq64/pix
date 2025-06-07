from typing import Any, Callable
import pixpy as pix
from tween import tween, Ease

Float2 = pix.Float2

screen = pix.open_display(size=(1280, 720))

pos = Float2(-400, screen.size.y / 2).tween_to(screen.size / 2, 4.0, Ease.out_bounce)

font = pix.load_font("data/hyperspace_bold.ttf")
hello_image = font.make_image("Hello World", size=64, color=pix.color.ORANGE)

screen.draw_color = pix.color.YELLOW
screen.line_width = 4.0


# t = tween(Float2(-300, 300), Float2(500, 300), 100, Ease.out_sine)
# pos = pix.Float2(0, 0)
# pos.iterate(t)

while pix.run_loop():
    screen.clear(pix.color.BLACK)
    screen.draw(image=hello_image, center=pos, rot=pos.x / 100)
    screen.circle(center=pos, radius=pos.x / 4)
    screen.swap()
