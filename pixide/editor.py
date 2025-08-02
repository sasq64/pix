from pathlib import Path
from typing import Final, cast, override

import pixpy as pix

from .edit_cmd import (
    CombinedCmd,
    EditCmd,
    EditDelete,
    EditInsert,
    EditJoin,
    EditSplit,
    CmdStack,
)
from .viewer import TextViewer, TextRange, Char

Int2 = pix.Int2


CMD = 0x10000000
CTRL = 0x20000000


def clamp[T: (int, float)](v: T, lo: T, hi: T) -> T:
    "Clamp value between `lo` inclusive and `hi` exclusive."
    if v < lo:
        return lo
    if v >= hi:
        return cast(T, hi - 1)
    return v


class TextEdit(TextViewer):
    """
    Text editor using a `pix.Console`.
    """

    def __init__(self, con: pix.Console):
        super().__init__(con)
        
        # Additional editor-specific properties
        self.last_scroll: int = -1
        self.last_scrollx: int = -1
        self.cursor_col: int = 0
        self.cursor_line: int = 0
        self.preserved_col: int = -1
        self.yank_buffer: list[Char] = []
        self.cmd_stack: CmdStack = CmdStack()

        self.indent_size = 4
        self.selection = TextRange(Int2.ZERO, Int2.ZERO)
        self.selection_active: bool = False
        self.last_clicked: pix.Int2 | None = None
        self.start_pos: pix.Int2 | None = None

        self.moves: Final = {
            pix.key.LEFT: lambda: (self.cursor_col - 1, self.cursor_line),
            pix.key.RIGHT: lambda: (self.cursor_col + 1, self.cursor_line),
            CMD | pix.key.RIGHT: lambda: (self.next_word(), self.cursor_line),
            CMD | pix.key.LEFT: lambda: (self.pre_word(), self.cursor_line),
            pix.key.END: lambda: (len(self.lines[self.cursor_line]), self.cursor_line),
            pix.key.HOME: lambda: (int(0), self.cursor_line),
            pix.key.UP: lambda: (self.cursor_col, self.cursor_line - 1),
            pix.key.DOWN: lambda: (self.cursor_col, self.cursor_line + 1),
            pix.key.PAGEUP: lambda: (self.cursor_col, self.cursor_line - self.rows),
            pix.key.PAGEDOWN: lambda: (self.cursor_col, self.cursor_line + self.rows),
            CMD | pix.key.UP: lambda: (self.cursor_col, int(0)),
            CMD | pix.key.DOWN: lambda: (self.cursor_col, len(self.lines)),
        }
        """Key bindings for keys that move the cursor."""

    @property
    def current_line(self) -> list[Char]:
        return self.lines[self.cursor_line]

    def select(self, start: pix.Int2, end: pix.Int2):

        if start.y > end.y or (start.y == end.y and start.x > end.x):
            start, end = end, start

        m = TextRange(start, end)
        if m != self.selection:
            self.selection = m
            self.dirty = True
            self.selection_active = True

    def deselect(self):
        if self.selection_active:
            self.dirty = True
        self.selection_active = False

    @override
    def set_console(self, console: pix.Console):
        super().set_console(console)
        self.wrap_cursor()

    def goto(self, xpos: int, ypos: int):
        self.cursor_col = xpos
        self.cursor_line = ypos
        self.wrap_cursor()

    def goto_line(self, line_no: int):
        """Goto line, try to keep X-position. Return `False` if cursor did not move"""

        if line_no < 0:
            line_no = 0
        elif line_no >= len(self.lines):
            line_no = len(self.lines) - 1
        if self.cursor_line == line_no:
            return False
        self.cursor_line = line_no
        if self.preserved_col >= 0:
            self.cursor_col = self.preserved_col
        new_xpos = clamp(self.cursor_col, 0, len(self.current_line) + 1)
        if new_xpos != self.cursor_col:
            self.preserved_col = self.cursor_col
        self.cursor_col = new_xpos
        return True

    def get_location(self):
        return self.cursor_col, self.cursor_line

    @override
    def set_text(self, text: str):
        super().set_text(text)
        self.cursor_line = 0
        self.cursor_col = 0

    def next_word(self) -> int:
        x = self.cursor_col
        length = len(self.current_line)
        while x < length and self.current_line[x][0] != 0x20:
            x += 1
        while x < length and self.current_line[x][0] == 0x20:
            x += 1
        return x

    def pre_word(self) -> int:
        x = self.cursor_col
        while x > 0 and self.current_line[x - 1][0] == 0x20:
            x -= 1
        while x > 0 and self.current_line[x - 1][0] != 0x20:
            x -= 1
        return x

    def apply(self, cmd: EditCmd, join_prev: bool = False):
        self.cmd_stack.apply(cmd, self.lines, join_prev)
        self.dirty = True
        self.deselect()

    def undo(self):
        pos = self.cmd_stack.undo(self.lines)
        if pos is not None:
            self.cursor_line, self.cursor_col = pos
            self.dirty = True

    def redo(self):
        pos = self.cmd_stack.redo(self.lines)
        if pos is not None:
            self.cursor_line, self.cursor_col = pos
        self.dirty = True

    def insert(self, text: list[Char], join_prev: bool = False):
        self.apply(EditInsert(self.cursor_line, self.cursor_col, text), join_prev)

    def remove(self, count: int):
        self.apply(EditDelete(self.cursor_line, self.cursor_col, count))

    def copy(self):
        data: list[list[Char]] = []
        for line_no, col0, col1 in self.selection.lines_reversed():
            if col1 == -1:
                col1 = len(self.lines[line_no])
            data.insert(0, self.lines[line_no][col0:col1])
        return data

    def cut(self):
        """Cut (delete) the current selection using EditCommands"""
        cut_data: list[list[Char]] = []

        commands: list[EditCmd] = []
        lines_to_process = list(self.selection.lines_reversed())

        for line_no, col0, col1 in lines_to_process:
            if col1 == -1:
                col1 = len(self.lines[line_no])
            cut_data.insert(0, self.lines[line_no][col0:col1])
            commands.append(EditDelete(line_no, col0, col1 - col0))

        for _ in range(len(lines_to_process) - 1):
            commands.append(EditJoin(self.selection.start.y))

        if commands:
            self.apply(CombinedCmd(commands))
            # Position cursor at the start of the selection
            self.cursor_col = self.selection.start.x
            self.cursor_line = self.selection.start.y
            self.selection_active = False
            self.dirty = True
        return cut_data

    def indent(self, shift: int):
        """
        Indent current line or selection by `shift` columns, in either
        direction. Will stop at left edge.
        """
        lines = [self.cursor_line]

        if self.selection_active:
            lines.clear()
            for line, _, _ in self.selection.lines():
                lines.append(line)
            if self.selection.end[0] == 0:
                lines.pop()
                self.selection.end = Int2(1, self.selection.end[1] - 1)

        commands: list[EditCmd] = []

        if shift > 0:
            for line in lines:
                commands.append(EditInsert(line, 0, [(0x20, 0)] * shift))
        else:
            n = -shift
            for line in lines:
                n = self.get_leading_spaces(line)
                if n > -shift:
                    n = -shift
                commands.append(EditDelete(line, 0, n))
            shift = -n
        if not self.selection_active:
            self.cursor_col += shift
        self.cmd_stack.apply(CombinedCmd(commands), self.lines)
        self.dirty = True
        if self.selection_active:
            self.selection.start = Int2(0, self.selection.start[1])
            self.selection.end = Int2(
                len(self.lines[self.selection.end[1]]), self.selection.end[1]
            )

    def get_leading_spaces(self, line_no: int) -> int:
        i = 0
        line = self.lines[line_no]
        while i < len(line) and line[i][0] == 0x20:
            i += 1
        if i >= len(line):
            i = 0
        return i

    def paste(self, lines: list[list[Char]]):
        """Paste (insert) the provided lines using EditCommands"""
        if not lines:
            return

        commands: list[EditCmd] = []

        x = self.cursor_col
        for i, line in enumerate(lines):
            commands.append(EditInsert(self.cursor_line + i, x, line))
            # Split after this line content unless it's the last line
            if i < len(lines) - 1:
                commands.append(EditSplit(self.cursor_line + i, x + len(line)))
                x = 0

        if commands:
            self.apply(CombinedCmd(commands))
            # Position cursor at end of pasted content
            self.cursor_col = x + len(lines[-1])
            self.cursor_line = self.cursor_line + len(lines) - 1
            self.dirty = True

    def handle_key(self, key: int, mods: int):
        k = key | CMD if mods & 8 != 0 else key
        shift = mods & 1 != 0
        if k in self.moves:
            # Cursor movement action
            (x, y) = self.moves[k]()
            prev = pix.Int2(self.cursor_col, self.cursor_line)
            if self.cursor_col != x:
                self.preserved_col = -1
                self.cursor_col = x
            if self.cursor_line != y:
                _ = self.goto_line(y)
            if shift:
                if not self.start_pos:
                    self.start_pos = prev
                self.select(self.start_pos, pix.Int2(self.cursor_col, self.cursor_line))
            else:
                self.deselect()
                self.start_pos = None
            self.wrap_cursor()
            return
        if mods & 10 != 0:
            # Ctrl or Command
            if key == ord("z"):
                self.undo()
            elif key == ord("r"):
                self.redo()
            elif key == ord("x"):
                data = self.cut()
                pix.set_clipboard(self.get_text(data))
            elif key == ord("c"):
                data = self.copy()
                pix.set_clipboard(self.get_text(data))
            elif key == ord("v"):
                clipboard = pix.get_clipboard()
                lines: list[list[Char]] = []
                for line in clipboard.splitlines():
                    lines.append([(ord(c), 1) for c in line])
                if self.selection_active:
                    self.cut()
                self.paste(lines)
            elif key == ord("k"):
                length = len(self.current_line) - self.cursor_col
                self.apply(EditDelete(self.cursor_line, self.cursor_col, length))
            elif key == ord("d"):
                self.yank_buffer[:] = self.current_line
                length = len(self.current_line)
                self.apply(EditDelete(self.cursor_line, 0, length))
                if self.cursor_line < len(self.lines) - 1:
                    self.apply(EditJoin(self.cursor_line), True)
                self.wrap_cursor()
        elif key == pix.key.TAB:
            shiftx = -self.indent_size if (mods & 1 != 0) else self.indent_size
            self.indent(shiftx)
        elif key == pix.key.ENTER:
            i = self.get_leading_spaces(self.cursor_line)
            self.apply(EditSplit(self.cursor_line, self.cursor_col))
            _ = self.goto_line(self.cursor_line + 1)
            self.cursor_col = 0
            if i:
                self.insert([(0x20, 0)] * i, join_prev=True)
                self.cursor_col = i
            self.wrap_cursor()
        elif key == pix.key.BACKSPACE:
            if self.selection_active:
                self.cut()
            else:
                if self.cursor_col > 0:
                    self.cursor_col -= 1
                    self.remove(1)
                elif self.cursor_line > 0:
                    # Handle backspace at beginning of line
                    ll = len(self.lines[self.cursor_line - 1])
                    self.apply(EditJoin(self.cursor_line - 1))
                    _ = self.goto_line(self.cursor_line - 1)
                    self.cursor_col = ll
        self.preserved_col = -1

    def wrap_cursor(self):
        """Check if cursor is out of bounds and move it to a correct position"""
        if self.cursor_col < 0:
            # Wrap to end of previous line
            if self.goto_line(self.cursor_line - 1):
                self.cursor_col = len(self.current_line)
            else:
                self.cursor_col = 0

        if self.cursor_col > len(self.current_line):
            # Wrap to beginning of next line
            if self.goto_line(self.cursor_line + 1):
                self.cursor_col = 0
            else:
                self.cursor_col = len(self.current_line)

        # Scroll screen if ypos not visible
        if self.cursor_line < self.horizontal_scroll:
            self.horizontal_scroll = self.cursor_line
        y = self.rows - 1
        if self.cursor_line >= self.horizontal_scroll + y:
            self.horizontal_scroll = self.cursor_line - y

        # The current line needs to be scrolled so the cursor is visible
        if self.cursor_col > self.cols - 2:
            self.vertical_scroll = self.cursor_col - self.cols + 2
        else:
            self.vertical_scroll = 0

    @override
    def scroll_screen(self, y: int):
        super().scroll_screen(y)

    def click(self, x: int, y: int):
        """Handle mouse click to position cursor at clicked location."""
        # Ignore clicks outside editor area
        if x < 0 or y < 0:
            return
        # Reset horizontal position tracking
        self.preserved_col = -1
        grid_pos = Int2(x, y) // self.console.tile_size
        text_pos = grid_pos + (0, self.horizontal_scroll)
        self.last_clicked = text_pos

        self.cursor_col = text_pos.x
        if self.cursor_line != text_pos.y:
            _ = self.goto_line(text_pos.y)
        if self.cursor_col > len(self.current_line):
            self.cursor_col = len(self.current_line)
        self.console.cursor_pos = Int2(self.cursor_col, self.cursor_line)

    def update(self, events: list[pix.event.AnyEvent]):
        for e in events:
            if isinstance(e, pix.event.Text):
                if e.device != 0:
                    continue
                code = ord(e.text)
                if code > 0xFFFF:
                    continue
                if self.selection_active:
                    self.cut()
                    self.start_pos = None
                    self.selection_active = False
                self.insert([(code, 1)])
                self.cursor_col += len(e.text)
                self.wrap_cursor()
                self.dirty = True
                self.preserved_col = -1
            elif isinstance(e, pix.event.Scroll):
                self.scroll_screen(int(e.y * 3))
            elif isinstance(e, pix.event.Key):
                self.handle_key(e.key, e.mods)
                # Scroll cursor into view after any keyboard event
                self.wrap_cursor()
            elif isinstance(e, pix.event.Click):
                self.click(int(e.x), int(e.y))
            elif isinstance(e, pix.event.Move):
                if e.buttons and self.last_clicked:
                    grid_pos = Int2(e.x, e.y) // self.console.tile_size
                    text_pos = grid_pos + (0, self.horizontal_scroll)
                    if text_pos != self.selection.end:
                        # print(f"{self.last_clicked} to {text_pos}")
                        self.select(self.last_clicked, text_pos)
                else:
                    self.last_clicked = None

    @override
    def render(self, selection: TextRange | None = None, cursor_pos: pix.Int2 | None = None):
        """
        Update the characters in the Console from the internal text state.
        Needs to be done when text, hihlighting or scroll position changes.
        """
        # Update dirty flag based on scroll changes
        if (
            self.last_scroll != self.horizontal_scroll
            or self.vertical_scroll != self.last_scrollx
        ):
            self.dirty = True
            self.last_scroll = self.horizontal_scroll
            self.last_scrollx = self.vertical_scroll

        # Clamp cursor position
        self.cursor_col = clamp(self.cursor_col, 0, len(self.current_line) + 1)

        # Call parent render with selection and cursor position
        # Use provided parameters or fall back to internal state
        if selection is None:
            selection = self.selection if self.selection_active else None
        if cursor_pos is None:
            cursor_pos = pix.Int2(self.cursor_col, self.cursor_line)
        super().render(selection, cursor_pos)


def main():
    data_dir = Path(__file__).absolute().parent / "data"
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
