from collections.abc import Iterator
from typing import cast, override

import pixpy as pix

Int2 = pix.Int2


def clamp[T: (int, float)](v: T, lo: T, hi: T) -> T:
    "Clamp value between `lo` inclusive and `hi` exclusive."
    if v < lo:
        return lo
    if v >= hi:
        return cast(T, hi - 1)
    return v


Char = tuple[int, int]
"""A `Char` holds a character and a color index"""


class TextRange:
    """Represent a range of text in list of strings"""

    def __init__(self, start: Int2, end: Int2, arg: int = -1):
        self.start = start
        self.end = end
        self.arg = arg

    @override
    def __repr__(self):
        return f"{self.start} -> {self.end}"

    def lines_reversed(self) -> Iterator[tuple[int, int, int]]:
        msc, msl = self.start
        mec, mel = self.end
        for line_no in range(mel, msl - 1, -1):
            col0 = msc if line_no == msl else 0
            col1 = mec if line_no == mel else -1
            yield (line_no, col0, col1)

    def lines(self) -> Iterator[tuple[int, int, int]]:
        msc, msl = self.start
        mec, mel = self.end
        for line_no in range(msl, mel + 1):
            col0 = msc if line_no == msl else 0
            col1 = mec if line_no == mel else -1
            yield (line_no, col0, col1)


class TextViewer:
    """
    Non-interactive text viewer using a `pix.Console`.
    Handles text display, scrolling, highlighting, and color management.
    """

    def __init__(self, con: pix.Console):
        self.lines: list[list[Char]] = [[]]
        self.horizontal_scroll: int = 0
        self.vertical_scroll: int = 0
        self.dirty: bool = True
        """Indicate that the console text need to be updated"""

        self.cols: int = con.grid_size.x
        self.rows: int = con.grid_size.y
        self.console: pix.Console = con

        self.fg_color: int = pix.color.GREEN
        self.bg_color: int = 0x202330
        self.palette: list[tuple[int, int]] = [(0, 0)] * 128
        self.palette[0] = (self.bg_color, self.bg_color)

        self.selection_color = 100
        self.palette[100] = (pix.color.WHITE, pix.color.LIGHT_BLUE)

        self.show_cursor = True

        self.console.cursor_on = True
        self.console.wrapping = False

    def get_text(self, lines: list[list[Char]] | None = None):
        if lines is None:
            lines = self.lines
        return "\n".join(["".join([chr(c[0]) for c in line]) for line in lines])

    def get_codepoints(self) -> list[int]:
        eol = 10
        return list(
            [
                codepoint
                for line in self.lines
                for codepoint in ([c[0] for c in line] + [eol])
            ]
        )

    def highlight(self, tranges: list[TextRange]):
        """Set the color of all passed textranges, using `arg` as color"""
        for trange in tranges:
            color = trange.arg
            for ln, col0, col1 in trange.lines():
                if ln >= len(self.lines):
                    break
                line = self.lines[ln]
                if col1 == -1:
                    col1 = len(line)
                for j in range(col0, col1):
                    line[j] = (line[j][0], color)

    def set_text(self, text: str):
        lines = text.split("\n")
        self.lines = []
        for line in lines:
            self.lines.append([(ord(c), 1) for c in line])
        self.dirty = True

    def set_console(self, console: pix.Console):
        self.console = console
        self.console.cursor_on = self.show_cursor
        self.console.wrapping = False
        self.fg_color = pix.color.GREEN
        self.cols = self.console.grid_size.x
        self.rows = self.console.grid_size.y
        self.dirty = True

    def set_color(self, fg: int, bg: int):
        self.fg_color = fg
        self.bg_color = bg

    def set_palette(self, colors: list[int]):
        """Set palette. 0 = default bg, 1 = default text"""
        self.bg_color = (colors[0] << 8) | 0xFF
        self.fg_color = (colors[1] << 8) | 0xFF
        for i, c in enumerate(colors):
            self.palette[i] = ((c << 8) | 0xFF, self.bg_color)
        self.console.set_color(self.fg_color, self.bg_color)

    def scroll_screen(self, y: int):
        self.horizontal_scroll -= y
        y = self.rows - 1
        l = len(self.lines)
        if self.horizontal_scroll < 0:
            self.horizontal_scroll = 0
        if self.horizontal_scroll > l - y:
            self.horizontal_scroll = l - y

    def render(
        self,
        selection: TextRange | None = None,
        cursor_pos: pix.Int2 | None = None,
    ):
        """
        Update the characters in the Console from the internal text state.
        Needs to be done when text, highlighting or scroll position changes.
        """
        if self.dirty:
            self.render_editor(selection)

        # If cursor position provided and visible, show cursor
        if cursor_pos is not None:
            if (
                cursor_pos.y >= self.horizontal_scroll
                and cursor_pos.y <= self.horizontal_scroll + self.console.size.y
            ):
                self.console.cursor_on = self.show_cursor
                self.console.cursor_pos = pix.Int2(
                    cursor_pos.x - self.vertical_scroll, cursor_pos.y - self.horizontal_scroll
                )
            else:
                self.console.cursor_on = False

    def render_editor(self, selection: TextRange | None = None):
        self.dirty = False
        self.console.set_color(self.fg_color, self.bg_color)
        self.console.clear()
        for y in range(self.rows):
            i = y + self.horizontal_scroll
            if i >= len(self.lines):
                break
            left_cropped = False
            right_cropped = False
            mark_startx = -1
            mark_endx = -1
            if selection is not None:
                # Figure if parts of this line should be marked
                my0 = i - selection.start.y
                my1 = selection.end.y - i
                if my0 == 0:
                    mark_startx = selection.start.x
                elif my0 > 0:
                    mark_startx = 0
                if my1 == 0:
                    mark_endx = selection.end.x - 1
                elif my1 > 0:
                    mark_endx = 999999
                else:
                    mark_startx = -1

            for x, (t, c) in enumerate(self.lines[i], -self.vertical_scroll):
                if x < 0:
                    if t != 0x20:
                        left_cropped = True
                elif x >= self.cols - 1:
                    if t != 0x20:
                        right_cropped = True
                else:
                    if mark_startx >= 0 and x >= mark_startx and x <= mark_endx:
                        fg, bg = self.palette[self.selection_color]
                    else:
                        fg, bg = self.palette[c]
                    self.console.put((x, y), t, fg, bg)

            if left_cropped:
                self.console.put(
                    (0, y),
                    ord("$"),
                    pix.color.LIGHT_RED,
                    pix.color.BLACK,
                )
            if right_cropped:
                self.console.put(
                    (self.cols - 1, y),
                    ord("$"),
                    pix.color.LIGHT_RED,
                    pix.color.BLACK,
                )
