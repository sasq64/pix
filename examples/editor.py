from array import array
from pathlib import Path
from typing import Final, cast

import pixpy as pix

from edit_cmd import EditCmd, EditDelete, EditInsert, EditJoin, EditSplit, CmdStack

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

"""
Removing 'remove' chars starting at 'line'/'col':

n = min(r, rest)

del lines[line][col:n]

        r = self.remove
        lino = self.line
        col = self.col
        while r > 0:
            n = min(r, len(target[lino][col:-1]))
            del target[lino][col:n]
            r -= n
            lino += 1
            col = 0
        lines = [
            list(a[1])
            for a in itertools.groupby(self.add, lambda c: c[0] == 10)
            if not a[0]
        ]

        for line in lines:
"""


class TextEdit:
    """
    Text editor using a `pix.Console`.
    """

    def __init__(self, con: pix.Console):
        self.lines: list[list[Char]] = [[]]
        self.line: list[Char] = self.lines[0]
        self.scroll_pos: int = 0
        self.last_scroll: int = -1
        self.last_scrollx: int = -1
        self.xpos: int = 0
        self.ypos: int = 0
        self.keepx: int = -1
        self.yank: list[Char] = []
        self.cmd_stack: CmdStack = CmdStack()

        self.cols: int = con.grid_size.x
        self.rows: int = con.grid_size.y
        self.con: pix.Console = con
        self.dirty: bool = True
        self.con.cursor_on = True
        self.con.wrapping = False

        self.scrollx: int = 0

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

    def apply(self, cmd: EditCmd, join_prev: bool = False):
        self.cmd_stack.apply(cmd, self.lines, join_prev)

    def undo(self):
        pos = self.cmd_stack.undo(self.lines)
        if pos is not None:
            self.ypos, self.xpos = pos
            self.line = self.lines[self.ypos]
            self.dirty = True

    def redo(self):
        pos = self.cmd_stack.redo(self.lines)
        if pos is not None:
            self.ypos, self.xpos = pos
            self.line = self.lines[self.ypos]
        self.dirty = True

    def insert(self, text: list[Char], join_prev: bool = False):
        self.apply(EditInsert(self.ypos, self.xpos, text), join_prev)

    def remove(self, count: int):
        self.apply(EditDelete(self.ypos, self.xpos, count))

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
            if key == ord("z"):
                self.undo()
            elif key == ord("r"):
                self.redo()
            elif key == ord("k"):
                length = len(self.line) - self.xpos
                self.apply(EditDelete(self.ypos, self.xpos, length))
                return True
            elif key == ord("d"):
                self.yank[:] = self.line
                length = len(self.line)
                self.apply(EditDelete(self.ypos, 0, length))
                if self.ypos < len(self.lines) - 1:
                    self.apply(EditJoin(self.ypos), True)
                self.line = self.lines[self.ypos]
                self.wrap_cursor()
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
                self.insert([(0x20, 0)] * 4)
                # self.line[self.xpos : self.xpos] = [(0x20, 0)] * 4
                self.xpos += 4
            return True
        elif key == pix.key.ENTER:
            i = 0
            while i < len(self.line) and self.line[i][0] == 0x20:
                i += 1
            if i >= len(self.line):
                i = 0
            self.apply(EditSplit(self.ypos, self.xpos))
            _ = self.goto_line(self.ypos + 1)
            self.xpos = 0
            if i:
                self.insert([(0x20, 0)] * i, join_prev=True)
                self.xpos = i
            # if self.ypos > 0:
            #     # Simple auto indent
            #     i = 0
            #     last_line = self.lines[self.ypos - 1]
            #     while i < len(last_line) and last_line[i][0] == 0x20:
            #         i += 1
            #     if i and i < len(last_line):
            #         self.line[0:0] = [(0x20, 0)] * i
            #         self.xpos = i
            self.wrap_cursor()
            return True
        elif key == pix.key.BACKSPACE:
            if self.xpos > 0:
                self.xpos -= 1
                self.remove(1)
            elif self.ypos > 0:
                # Handle backspace at beginning of line
                ll = len(self.lines[self.ypos - 1])
                self.apply(EditJoin(self.ypos - 1))
                _ = self.goto_line(self.ypos - 1)
                self.xpos = ll
            return True
        self.keepx = -1
        return False

    def goto(self, xpos: int, ypos: int):
        self.xpos = xpos
        self.ypos = ypos
        self.wrap_cursor()

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

        # The current line needs to be scrolled so the cursor is visible

        if self.xpos > self.cols - 2:
            self.scrollx = self.xpos - self.cols + 2
        else:
            self.scrollx = 0

        # if self.xpos < self.scrollx:
        #     self.scrollx = self.xpos
        # if self.xpos >= self.scrollx + (self.cols - 1):
        #     self.scrollx = self.xpos - (self.cols - 1)
        # print(self.scrollx)

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

    def update(self, events: list[pix.event.AnyEvent]):
        for e in events:
            if isinstance(e, pix.event.Text):
                if e.device != 0:
                    continue
                self.insert([(ord(e.text), 1)])
                # self.line.insert(self.xpos, (ord(e.text), 1))
                self.xpos += len(e.text)
                self.wrap_cursor()
                self.dirty = True
                self.keepx = -1
            elif isinstance(e, pix.event.Scroll):
                self.scroll_pos -= int(e.y * 3)
                y = self.rows - 1
                l = len(self.lines)
                if self.scroll_pos < 0:
                    self.scroll_pos = 0
                if self.scroll_pos > l - y:
                    self.scroll_pos = l - y
            elif isinstance(e, pix.event.Key):
                if self.handle_key(e.key, e.mods):
                    self.dirty = True
                # Scroll cursor into view after any keyboard event
                self.wrap_cursor()
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
        if (
            self.dirty
            or self.last_scroll != self.scroll_pos
            or self.scrollx != self.last_scrollx
        ):
            self.last_scroll = self.scroll_pos
            self.last_scrollx = self.scrollx
            self.dirty = False
            self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
            self.con.set_color(self.fg, self.bg)
            self.con.clear()
            for y in range(self.rows):
                i = y + self.scroll_pos
                if i >= len(self.lines):
                    break
                left_cropped = False
                right_cropped = False
                for x, (t, c) in enumerate(self.lines[i], -self.scrollx):
                    if x < 0:
                        if t != 0x20:
                            left_cropped = True
                    elif x >= self.cols - 1:
                        if t != 0x20:
                            right_cropped = True
                    else:
                        fg, bg = self.palette[c]
                        self.con.put((x, y), t, fg, bg)

                if left_cropped:
                    self.con.put(
                        (0, y),
                        ord("$"),
                        pix.color.LIGHT_RED,
                        pix.color.BLACK,
                    )
                if right_cropped:
                    self.con.put(
                        (self.cols - 1, y),
                        ord("$"),
                        pix.color.LIGHT_RED,
                        pix.color.BLACK,
                    )

        # If current line is visible, move the cursor to the edit position
        if (
            self.ypos >= self.scroll_pos
            and self.ypos <= self.scroll_pos + self.con.size.y
        ):
            self.con.cursor_on = True
            self.con.cursor_pos = Int2(
                self.xpos - self.scrollx, self.ypos - self.scroll_pos
            )
        else:
            self.con.cursor_on = False

    def draw_scrollbar(self, canvas: pix.Canvas, editor_rect: pix.Float2, offset_y: float = 0):
        """Draw a scroll bar on the right side of the editor area"""
        if len(self.lines) <= self.rows:
            return  # No scrollbar needed if all content fits

        # Scrollbar dimensions
        scrollbar_width = 8
        scrollbar_x = editor_rect.x - scrollbar_width - 2
        scrollbar_y = offset_y
        scrollbar_height = editor_rect.y

        # Background track
        canvas.draw_color = pix.color.DARK_GREY
        canvas.filled_rect(
            top_left=pix.Float2(scrollbar_x, scrollbar_y),
            size=pix.Float2(scrollbar_width, scrollbar_height)
        )

        # Calculate thumb position and size
        total_lines = len(self.lines)
        visible_lines = self.rows
        thumb_height = max(20, (visible_lines / total_lines) * scrollbar_height)
        
        # Calculate thumb position (avoid division by zero)
        max_scroll = max(1, total_lines - visible_lines)
        thumb_y = (self.scroll_pos / max_scroll) * (scrollbar_height - thumb_height)

        # Draw thumb
        canvas.draw_color = pix.color.LIGHT_GREY
        canvas.filled_rect(
            top_left=pix.Float2(scrollbar_x, scrollbar_y + thumb_y),
            size=pix.Float2(scrollbar_width, thumb_height)
        )


data_dir = Path(__file__).absolute().parent / "data"


def main():
    screen = pix.open_display(width=60 * 16, height=50 * 16)
    sz = screen.size.toi() // (8 * 2, 16 * 2)
    con = pix.Console(sz.x, sz.y, font_file=data_dir / "Hack.ttf", font_size=24)
    edit = TextEdit(con)
    while pix.run_loop():
        edit.update(pix.all_events())
        edit.render()
        screen.clear(pix.color.DARK_GREY)
        screen.draw(con)
        screen.swap()


if __name__ == "__main__":
    main()
