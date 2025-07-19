from typing import Final

import pixpy as pix


class ListBox:
    """
    A list of selectable items backed by a console
    """

    def __init__(self, console: pix.Console):
        self.con: Final = console
        self.xy: pix.Int2 = pix.Int2(0, 0)
        self.selected: int = 0
        self.scroll: int = 0
        self.lines: list[str] = []

    def set_lines(self, lines: list[str]):
        """
        Set the lines to show in the listbox
        """
        old_line = self.get_selection()
        self.lines = lines
        self.selected = 0
        if old_line is not None:
            try:
                self.selected = self.lines.index(old_line)
            except ValueError:
                pass
        self.update()

    def update(self):
        pos = pix.Int2(0, 0)
        self.con.set_color(pix.color.WHITE, pix.color.BLACK)
        self.con.clear()
        for i in range(self.scroll, self.scroll + self.con.grid_size.y):
            if i >= 0 and i < len(self.lines):
                line = self.lines[i]
                self.con.cursor_pos = pos
                if self.selected == i:
                    self.con.set_color(pix.color.WHITE, pix.color.BLUE)
                else:
                    self.con.set_color(pix.color.WHITE, pix.color.BLACK)
                self.con.write(line)
            pos += (0, 1)

    def move(self, dy: int):
        h = self.con.grid_size.y
        self.selected += dy
        if self.selected < 0:
            self.selected = 0
        if self.selected >= len(self.lines):
            self.selected = len(self.lines) - 1
        if self.selected < self.scroll:
            self.scroll = self.selected
        if self.selected > self.scroll + h:
            self.scroll = self.selected - h

        self.update()

    def render(self, screen: pix.Canvas, xy: pix.Float2):
        screen.draw_color = 0xFFFFFFFF
        screen.filled_rect(top_left=xy, size=self.con.size + (8, 8))
        screen.draw(self.con, top_left=xy + (4, 4))

    def get_selection(self) -> str | None:
        if len(self.lines) > self.selected:
            return self.lines[self.selected]
        return None
