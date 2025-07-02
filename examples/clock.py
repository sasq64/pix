import math
import time
import pixpy as pix
from pathlib import Path

pwd = Path(__file__).absolute().parent

screen = pix.open_display(size=(720 * 2, 480 * 2))
r = screen.size.y / 2 - 20
center = screen.size / 2

clock_back = pix.Image(size=screen.size)

clock_back.filled_circle(center=center, radius=r)

font = pix.load_font(pwd / "data/lazenby.ttf")

clock_back.draw_color = pix.color.BLACK
for i in range(12):
    img = font.make_image(f"{i}", 48)
    img.set_texture_filter(True, True)
    a = math.pi * 2 * i / 12 - math.pi / 2
    pos = pix.Float2.from_angle(a) * r * 0.8
    clock_back.draw(img, center=center + pos)


def clock_hand(
    angle: float,
    length: float,
    r0: float = 10,
    r1: float = 2,
    color: int = pix.color.BLACK,
):
    pos = pix.Float2.from_angle(angle - math.pi / 2) * length
    screen.draw_color = color
    screen.rounded_line(center, r0, center + pos, r1)


while pix.run_loop():
    screen.draw_color = pix.color.WHITE
    screen.draw(clock_back, size=clock_back.size)
    t = time.localtime()

    secs = t.tm_sec + t.tm_min * 60 + t.tm_hour * 60 * 60

    sa = (secs % 60) * math.pi * 2 / 60
    ma = (secs / 60) * math.pi * 2 / 60
    ha = (secs / 3600) * math.pi * 2 / 12

    clock_hand(ha, r * 0.5, 10, 5)
    clock_hand(ma, r * 0.65, 10, 3, pix.color.BLUE)
    clock_hand(sa, r * 0.8, 2, 2, pix.color.RED)
    screen.draw_color = pix.color.YELLOW
    screen.filled_circle(center, 15)

    screen.swap()
