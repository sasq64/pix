import asyncio
from pathlib import Path
from typing import Any, Callable
import pixpy as pix
from utils.tween import tween, Ease

pwd = Path(__file__).absolute().parent
print(__file__)
print(pwd)
Float2 = pix.Float2

async def main():
    screen = pix.open_display(size=(1280, 720))

    pos = Float2(-200, screen.size.y / 2).tween_to(screen.size / 2, 10.0)

    font = pix.load_font(pwd / "data/hyperspace_bold.ttf")
    hello_image = font.make_image("Hello World", size=64, color=pix.color.ORANGE)

    screen.draw_color = pix.color.YELLOW
    screen.line_width = 4.0

    while pix.run_loop():
        screen.clear(pix.color.BLACK)
        screen.draw(image=hello_image, center=pos, rot=pos.x / 100)
        screen.circle(center=pos, radius=pos.x / 3)
        await screen.swap_async()

if __name__ == "__main__":
    asyncio.run(main())
