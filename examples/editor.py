from array import array
from typing import Final, cast

import pixpy as pix

Int2 = pix.Int2

CMD = 0x10000000
CTRL = 0x20000000


def clamp[T: float | int](v: T, lo: T, hi: T) -> T:
    "Clamp value between `lo` inclusive and `hi` exclusive."
    if v < lo:
        return lo
    if v >= hi:
        return cast(T, hi - 1)
    return v


Char = tuple[int, int]
"""A `Char` holds a character and a color index"""


class TextEdit:
    """
    Text editor using a `pix.Console`.
    """

    def __init__(self, con: pix.Console):
        self.lines: list[list[Char]] = [[]]
        self.line: list[Char] = self.lines[0]
        self.scroll_pos: int = 0
        self.last_scroll: int = -1
        self.xpos: int = 0
        self.ypos: int = 0
        self.keepx: int = -1
        self.yank: list[Char] = []

        self.cols: int = con.grid_size.x
        self.rows: int = con.grid_size.y
        self.con: pix.Console = con
        self.dirty: bool = True
        self.con.cursor_on = True
        self.con.wrapping = False

        self.fg: int = pix.color.GREEN
        self.bg: int = 0x202330
        self.palette: list[tuple[int, int]] = [(0, 0)] * 128
        self.palette[0] = (self.bg, self.bg)
        self.palette[1] = (0xEECE6A, self.bg)
        self.palette[2] = (0x5159ED, self.bg)

        self.moves: Final = {
            pix.key.LEFT: lambda: (self.xpos - 1, self.ypos),
            pix.key.RIGHT: lambda: (self.xpos + 1, self.ypos),
            CMD | pix.key.RIGHT: lambda: (self.next_word(), self.ypos),
            CMD | pix.key.LEFT: lambda: (self.pre_word(), self.ypos),
            pix.key.END: lambda: (len(self.line), self.ypos),
            pix.key.HOME: lambda: (int(0), self.ypos),
            pix.key.UP: lambda: (self.xpos, self.ypos - 1),
            pix.key.DOWN: lambda: (self.xpos, self.ypos + 1),
            pix.key.PAGEUP: lambda: (self.xpos, self.ypos - self.rows),
            pix.key.PAGEDOWN: lambda: (self.xpos, self.ypos + self.rows),
            CMD | pix.key.UP: lambda: (self.xpos, int(0)),
            CMD | pix.key.DOWN: lambda: (self.xpos, len(self.lines)),
        }
        "Key bindings for keys that move the cursor."

    def set_console(self, console: pix.Console):
        self.con = console
        self.con.cursor_on = True
        self.con.wrapping = False
        self.fg = pix.color.GREEN
        # self.bg = 0x202330
        self.cols = self.con.grid_size.x
        self.rows = self.con.grid_size.y
        self.wrap_cursor()
        self.dirty = True

    # def console(self):
    #    return self.con

    def goto_line(self, y: int):
        """Goto line, try to keep X-position. Return `False` if cursor did not move"""

        if y < 0:
            y = 0
        elif y >= len(self.lines):
            y = len(self.lines) - 1
        if self.ypos == y:
            return False
        self.ypos = y
        self.line = self.lines[y]
        if self.keepx >= 0:
            self.xpos = self.keepx
        new_xpos = clamp(self.xpos, 0, len(self.line) + 1)
        if new_xpos != self.xpos:
            self.keepx = self.xpos
        self.xpos = new_xpos
        return True

    def get_text(self):
        return "\n".join(["".join([chr(c[0]) for c in line]) for line in self.lines])

    def get_utf16(self):
        eol = 10
        code_units = array(
            "H",
            (
                codepoint
                for line in self.lines
                for codepoint in ([c[0] for c in line] + [eol])
            ),
        )
        return code_units.tobytes()

    def hl_line(self, line: list[Char], color: int, start: int, end: int):
        """Set color of a section of the given line"""

        if end > len(line):
            end = len(line)
        for j in range(start, end):
            line[j] = (line[j][0], color)

    def highlight(self, start: int, end: int, color: int):
        """Set the color of a given section of the entire text"""

        offset = 0  # Start of current line
        for _, line in enumerate(self.lines):
            ll = len(line) + 1
            if start >= offset and start < (offset + ll):
                self.hl_line(line, color, start - offset, end - offset)
                start = offset + ll
            if end > offset and end < (offset + ll):
                break
            offset += ll

    def highlight_lines(self, line0: int, col0: int, line1: int, col1: int, color: int):
        """Set the color of a section of text, given lines & columns"""

        for ln in range(line0, line1 + 1):
            line = self.lines[ln]
            ll = len(line) + 1
            c0 = col0 if ln == line0 else 0
            c1 = col1 if ln == line1 else ll
            # print(f"HIGHTLIGHT {ln} ({c0}-{c1}) with {color}")
            self.hl_line(line, color, c0, c1)

    def get_location(self):
        return self.xpos, self.ypos

    def get_char(self, x: int):
        return self.line[x][0]

    def set_text(self, text: str):
        lines = text.split("\n")
        self.lines = [[]]
        for line in lines:
            self.lines.append([(ord(c), 1) for c in line])
        self.ypos = 0
        self.xpos = 0
        self.line = self.lines[0]
        self.dirty = True

    def next_word(self) -> int:
        x = self.xpos
        while x < len(self.line) and self.line[x][0] != 0x20:
            x += 1
        while x < len(self.line) and self.line[x][0] == 0x20:
            x += 1
        return x

    def pre_word(self) -> int:
        x = self.xpos
        while x > 0 and self.line[x - 1][0] == 0x20:
            x -= 1
        while x > 0 and self.line[x - 1][0] != 0x20:
            x -= 1
        return x

    def insert(self, text: str):
        self.line[self.xpos : self.xpos] = list([(ord(t), 1) for t in text])
        self.xpos += len(text)
        self.dirty = True

    def handle_key(self, key: int, mods: int) -> bool:
        k = key | CMD if mods & 8 != 0 else key
        if k in self.moves:
            # Cursor movement action
            (x, y) = self.moves[k]()
            if self.xpos != x:
                self.keepx = -1
                self.xpos = x
            if self.ypos != y:
                _ = self.goto_line(y)
            self.wrap_cursor()
            return False
        elif mods & 2 != 0:
            # Ctrl command
            if key == ord("k"):
                self.line[self.xpos :] = []
                return True
            elif key == ord("d"):
                self.yank[:] = self.line
                if len(self.lines) == 1:
                    self.line[:] = []
                    self.xpos = 0
                elif len(self.lines) > 1:
                    del self.lines[self.ypos]
                    if self.ypos >= len(self.lines):
                        self.ypos = len(self.lines) - 1
                    self.line = self.lines[self.ypos]
                self.ypos += 1
                self.line = self.lines[self.ypos]
                return True
            return False
        elif key == pix.key.TAB:
            if mods & 1 != 0:
                i = 0
                while self.line[i][0] == 0x20 and i < 4:
                    i += 1
                self.line[0:i] = []
                self.xpos -= i
                if self.xpos < 0:
                    self.xpos = 0
            else:
                self.line[self.xpos : self.xpos] = [(0x20, 0)] * 4
                self.xpos += 4
            return True
        elif key == pix.key.ENTER:
            rest = self.line[self.xpos :]
            self.lines[self.ypos] = [] if self.xpos == 0 else self.line[: self.xpos]
            self.lines.insert(self.ypos + 1, rest)
            _ = self.goto_line(self.ypos + 1)
            self.xpos = 0
            if self.ypos > 0:
                # Simple auto indent
                i = 0
                last_line = self.lines[self.ypos - 1]
                while i < len(last_line) and last_line[i][0] == 0x20:
                    i += 1
                if i and i < len(last_line):
                    self.line[0:0] = [(0x20, 0)] * i
                    self.xpos = i
            self.wrap_cursor()
            return True
        elif key == pix.key.BACKSPACE:
            if self.xpos > 0:
                self.xpos -= 1
                del self.line[self.xpos]
            elif self.ypos > 0:
                # Handle backspace at beginning of line
                y = self.ypos
                ll = len(self.lines[y - 1])
                self.lines[y - 1] = self.lines[y - 1] + self.line
                del self.lines[y]
                _ = self.goto_line(y - 1)
                self.xpos = ll
            return True
        self.keepx = -1
        return False

    def wrap_cursor(self):
        """Check if cursor is out of bounds and move it to a correct position"""
        if self.xpos < 0:
            # Wrap to end of previous line
            if self.goto_line(self.ypos - 1):
                self.xpos = len(self.line)
            else:
                self.xpos = 0

        if self.xpos > len(self.line):
            # Wrap to beginning of next line
            if self.goto_line(self.ypos + 1):
                self.xpos = 0
            else:
                self.xpos = len(self.line)

        # Scroll screen if ypos not visible
        if self.ypos < self.scroll_pos:
            self.scroll_pos = self.ypos
        y = self.rows - 1
        if self.ypos >= self.scroll_pos + y:
            self.scroll_pos = self.ypos - y

    def click(self, x: int, y: int):
        self.keepx = -1
        p = Int2(x, y) // self.con.tile_size
        p += (0, self.scroll_pos)
        self.xpos = p.x
        if self.ypos != p.y:
            _ = self.goto_line(p.y)
        if self.xpos > len(self.line):
            self.xpos = len(self.line)
        self.con.cursor_pos = Int2(self.xpos, self.ypos)
        print("CLICKED")

    def update(self, events: list[pix.event.AnyEvent]):
        for e in events:
            if isinstance(e, pix.event.Text):
                self.line.insert(self.xpos, (ord(e.text), 1))
                self.xpos += len(e.text)
                self.dirty = True
                self.keepx = -1
            elif isinstance(e, pix.event.Key):
                if self.handle_key(e.key, e.mods):
                    self.dirty = True
            elif isinstance(e, pix.event.Click):
                self.click(int(e.x), int(e.y))

    def set_color(self, fg: int, bg: int):
        self.fg = fg
        self.bg = bg

    def set_palette(self, colors: list[int]):
        """Set palette. 0 = default bg, 1 = default text"""
        self.bg = (colors[0] << 8) | 0xFF
        self.fg = (colors[1] << 8) | 0xFF
        for i, c in enumerate(colors):
            self.palette[i] = ((c << 8) | 0xFF, self.bg)
        self.con.set_color(self.fg, self.bg)

    def render(self):
        if self.dirty or self.last_scroll != self.scroll_pos:
            self.last_scroll = self.scroll_pos
            self.dirty = False
            self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
            self.con.set_color(self.fg, self.bg)
            self.con.clear()
            for y in range(self.rows):
                i = y + self.scroll_pos
                if i >= len(self.lines):
                    break
                # self.con.cursor_pos = Int2(0, y)
                for x, (t, c) in enumerate(self.lines[i]):
                    if x >= self.cols:
                        self.con.put(
                            (x - 1, y), ord("$"), pix.color.LIGHT_RED, pix.color.BLACK
                        )
                        break
                    fg, bg = self.palette[c]
                    self.con.put((x, y), t, fg, bg)

        # If current line is visible, move the cursor to the edit position
        if self.ypos >= self.scroll_pos:
            self.con.cursor_pos = Int2(self.xpos, self.ypos - self.scroll_pos)


def main():
    screen = pix.open_display(width=60 * 16, height=50 * 16)
    sz = screen.size.toi() // (8 * 2, 16 * 2)
    con = pix.Console(sz.x, sz.y, font_file="data/Hack.ttf", font_size=24)
    edit = TextEdit(con)
    while pix.run_loop():
        edit.update(pix.all_events())
        edit.render()
        screen.clear(pix.color.DARK_GREY)
        screen.draw(con)
        screen.swap()


if __name__ == "__main__":
    main()
