from array import array
from typing import List, cast

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


class TextEdit:
    """
    Text editor using a `pix.Console`.
    """

    def __init__(self, con: pix.Console):
        self.lines: List[List[Char]] = [[]]
        self.line = self.lines[0]
        self.scroll_pos: int = 0
        self.xpos: int = 0
        self.ypos: int = 0
        self.yank: List[Char] = []

        self.cols, self.rows = con.grid_size
        self.con = con
        self.dirty = True
        self.con.cursor_on = True
        self.con.wrapping = False
        # self.con.cursor_pos = pix.Int2(0, 0)
        self.fg = pix.color.GREEN
        self.bg = 0x202330
        self.palette: list[tuple[int, int]] = [(0, 0)] * 128
        self.palette[0] = (0x787C99, self.bg)
        self.palette[1] = (0xEECE6A, self.bg)
        self.palette[2] = (0x5159ED, self.bg)
        self.hl_pos = 0

        self.moves = {
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

    def console(self):
        return self.con

    def goto_line(self, y: int):
        if y < 0:
            y = 0
        elif y >= len(self.lines):
            y = len(self.lines) - 1
        if self.ypos == y:
            return False
        self.ypos = y
        self.line = self.lines[y]
        self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
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
        if end > len(line):
            end = len(line)
        for j in range(start, end):
            line[j] = (line[j][0], color)

    def highlight(self, start: int, end: int, color: int):
        offset = 0  # Start of current line
        for _, line in enumerate(self.lines):
            ll = len(line) + 1
            if start >= offset and start < (offset + ll):
                self.hl_line(line, color, start - offset, end - offset)
                start = offset + ll
            if end > offset and end < (offset + ll):
                break
            offset += ll

    def get_location(self):
        return self.xpos, self.ypos

    def get_char(self, x: int):
        return self.line[x][0]

    def set_text(self, text: str):
        lines = text.split("\n")
        self.lines = [[]]
        for line in lines:
            self.lines.append([(ord(c), 0) for c in line])
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
        self.line[self.xpos : self.xpos] = list([(ord(t), 0) for t in text])
        self.xpos += len(text)
        self.dirty = True

    def handle_key(self, key: int, mods: int):
        k = key | CMD if mods & 8 != 0 else key
        if k in self.moves:
            (x, y) = self.moves[k]()
            self.xpos = x
            if self.ypos != y:
                self.goto_line(y)
            self.wrap_cursor()
        elif mods & 2 != 0:
            if key == ord("k"):
                self.line[self.xpos :] = []
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
            return
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
        elif key == pix.key.ENTER:
            rest = self.line[self.xpos :]
            self.lines[self.ypos] = [] if self.xpos == 0 else self.line[: self.xpos]
            self.lines.insert(self.ypos + 1, rest)
            self.goto_line(self.ypos + 1)
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
                self.goto_line(y - 1)
                self.xpos = ll

    def wrap_cursor(self):
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
        p = Int2(x, y) // self.con.tile_size
        self.xpos = p.x
        if self.ypos != p.y:
            self.goto_line(p.y)
        self.con.cursor_pos = Int2(self.xpos, self.ypos)

    def update(self, events: List[pix.event.AnyEvent]):
        for e in events:
            if isinstance(e, pix.event.Text):
                self.line.insert(self.xpos, (ord(e.text), 0))
                self.xpos += len(e.text)
                self.dirty = True
            elif isinstance(e, pix.event.Key):
                self.handle_key(e.key, e.mods)
                self.dirty = True
            elif isinstance(e, pix.event.Click):
                self.click(int(e.x), int(e.y))

    def set_color(self, fg: int, bg: int):
        self.fg = fg
        self.bg = bg

    def set_palette(self, colors: list[int]):
        self.bg = (colors[0] << 8) | 0xFF
        self.fg = (colors[1] << 8) | 0xFF
        for i, c in enumerate(colors):
            self.palette[i] = ((c << 8) | 0xFF, self.bg)
        self.con.set_color(self.fg, self.bg)

    def render(self):
        if self.dirty:
            self.dirty = False
            self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
            self.con.set_color(self.fg, self.bg)
            self.con.clear()
            for y in range(self.rows):
                i = y + self.scroll_pos
                if i >= len(self.lines):
                    break
                self.con.cursor_pos = Int2(0, y)
                for x, (t, c) in enumerate(self.lines[i]):
                    fg, bg = self.palette[c]
                    self.con.put((x, y), t, fg, bg)
                # self.con.write(self.lines[i])
                # self.con.set_color(self.fg, self.bg)

            # self.con.cursor_pos = Int2(0, self.rows-1)
            # self.con.set_color(pix.color.WHITE, pix.color.BLUE)
            # self.con.write(f" LINE {self.ypos + 1} COL {self.xpos + 1} " + " " * (self.cols - 14))
            # self.con.set_color(self.fg, self.bg)

            # If current line is visible, move the cursor to the edit position
            if self.ypos >= self.scroll_pos:
                self.con.cursor_pos = Int2(self.xpos, self.ypos - self.scroll_pos)


def main():
    screen = pix.open_display(width=60 * 16, height=50 * 16)
    sz = screen.size // (8 * 2, 16 * 2)
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
