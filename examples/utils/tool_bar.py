
import pixpy as pix
from typing import Callable, Final, Self
from dataclasses import dataclass

@dataclass
class ToolbarEvent:
    button: int = -1

class ToolBar:
    def __init__(
        self,
        tile_set: pix.TileSet | None = None,
        pos: pix.Float2 = pix.Float2.ZERO,
        canvas: pix.Canvas | None = None,
        bg_color: int = pix.color.BLACK,
    ):
        self.canvas: pix.Canvas = canvas or pix.get_display()
        self.tile_set: Final = tile_set or pix.TileSet(tile_size=(48, 48))
        self.pos: pix.Float2 = pos
        tw = self.tile_set.tile_size.x
        cols = int((self.canvas.size.x + tw-1) // tw)
        self.add_pos: pix.Int2 = pix.Int2(0, 0)
        self.console: Final = pix.Console(rows=1, cols=cols, tile_set=self.tile_set)
        self.console.set_color(pix.color.WHITE, bg_color)
        self.console.clear()
        self.height: int = 48
        self.handler: None | Callable[[int], None] = None
        _ = pix.add_event_listener(self.__toolbar_click, 0)

    def on_click(self, handler: Callable[[int], None]) -> Self:
        self.handler = handler
        return self

    def add_button(self, tno: int, color: int) -> Self:
        self.console.put(self.add_pos, tno, color)
        self.add_pos += (1, 0)
        return self

    def set_button(self, index: int, tno: int, color: int):
        self.console.put((index, 0), tno, color)

    def render(self):
        self.canvas.draw(self.console, self.pos, size=self.console.size)

    def __toolbar_click(self, event: pix.event.AnyEvent):
        if isinstance(event, pix.event.Click):
            if event.y < self.height:
                x = int(event.x // 48)
                if x < self.add_pos.x:
                    print("POST")
                    pix.post_event(ToolbarEvent(x))
                    if self.handler is not None:
                        self.handler(x)
                    return False
        return True

