import os
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Final

import pixpy as pix
from utils.list_box import ListBox


class Repl:
    def __init__(self, con: pix.Console):
        self.con: Final = con
        self.prompt()

    def prompt(self):
        self.con.write("\n>")
        self.con.read_line()

    def update(self, screen: pix.Canvas, events: list[pix.event.AnyEvent]):
        for e in events:
            if isinstance(e, pix.event.Text):
                try:
                    f = StringIO()
                    with redirect_stdout(f):
                        exec(e.text)
                    self.con.write("\n")
                    self.con.write(f.getvalue())
                except Exception as e:
                    print(e)
                self.prompt()
            elif isinstance(e, pix.event.Key):
                pass

    def render(self, target: pix.Canvas):
        target.draw(self.con, size=self.con.size)


fwd = Path(os.path.dirname(os.path.abspath(__file__)))
hack_font = (fwd / "data" / "Hack.ttf").as_posix()


def main():
    global screen
    screen = pix.open_display(
        width=120 * 13, height=40 * 24, full_screen=False, visible=True
    )
    font_size = 24
    font = pix.load_font(hack_font, font_size)
    ts = pix.TileSet(font)
    con = pix.Console(80, 25, ts)

    box = pix.Console(20, 10, ts)

    list_box = ListBox(box)
    xy = pix.Float2(50, 50)

    list_box.set_lines(["a", "b"])
    con.clear()
    canvas = pix.Image(size=screen.size)
    canvas.clear(pix.color.TRANSP)
    repl = Repl(con)
    while pix.run_loop():
        screen.clear()
        repl.update(canvas, pix.all_events())
        repl.render(screen)
        screen.draw(canvas)
        # list_box.render(screen, xy)
        screen.swap()


if __name__ == "__main__":
    main()
