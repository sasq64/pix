import pixpy as pix
from typing import List, Any


CMD = 0x10000000
CTRL = 0x20000000

def clamp(v: Any, lo: Any, hi: Any):
    if v < lo:
        return lo
    if v >= hi:
        return hi - 1
    return v

class TextEdit:

    def __init__(self, font = None, cols = 120, rows = 50):
        self.lines : List[List[str] ]= [[]]
        self.line = self.lines[0]
        self.scroll_pos = 0
        self.xpos = 0
        self.ypos = 0
        self.yank = []
        if font == None:
            font = pix.TileSet(pix.Font.UNSCII_FONT)

        self.rows = rows
        self.cols = cols
        self.con = pix.Console(rows=rows, cols=cols, tile_set=font)
        self.con.cursor_on = True
        self.con.wrapping = False
        self.con.cursor_pos = pix.Int2(0, 0)
        self.fg = pix.color.GREEN
        self.bg = pix.color.BLACK

        self.moves = {
            pix.key.LEFT: lambda: (self.xpos-1, self.ypos),
            pix.key.RIGHT: lambda: (self.xpos+1, self.ypos),
            CMD | pix.key.RIGHT: lambda: (self.next_word(), self.ypos),
            CMD | pix.key.LEFT: lambda: (self.pre_word(), self.ypos),
            pix.key.END: lambda: (len(self.line), self.ypos),
            pix.key.HOME: lambda: (0, self.ypos),
            pix.key.UP: lambda: (self.xpos, self.ypos-1),
            pix.key.DOWN: lambda: (self.xpos, self.ypos+1),
            pix.key.PAGEUP: lambda: (self.xpos, self.ypos-self.rows),
            pix.key.PAGEDOWN: lambda: (self.xpos, self.ypos+self.rows),
            CMD | pix.key.UP: lambda: (self.xpos, 0),
            CMD | pix.key.DOWN: lambda: (self.xpos, len(self.lines)),
        }


    def console(self):
        return self.con

    def goto_line(self, y: int):
        if y < 0:
            y = 0
        elif y >= len(self.lines):
            y = len(self.lines)-1
        if self.ypos == y:
            return False
        self.ypos = y
        self.line = self.lines[y]
        self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
        return True

    def get_text(self):
        return "\n".join(["".join(l) for l in self.lines])

    def set_text(self, text):
        lines = text.split("\n")
        self.lines = [[]]
        for line in lines:
            self.lines.append([*line])
        self.ypos = 0
        self.xpos = 0
        self.line = self.lines[0]

    def next_word(self):
        x = self.xpos
        while x < len(self.line) and self.line[x] != ' ':
            x += 1
        while x < len(self.line) and self.line[x] == ' ':
            x += 1
        return x

    def pre_word(self):
        x = self.xpos
        while x > 0 and self.line[x-1] == ' ':
            x -= 1
        while x > 0 and self.line[x-1] != ' ':
            x -= 1
        return x

    def handle_key(self, key: int, mods: int):

        k = key | CMD if mods & 8 != 0 else key
        if k in self.moves:
            (x,y) = self.moves[k]()
            self.xpos = x
            if self.ypos != y :
                self.goto_line(y)
        elif mods & 2 != 0: 
            if key == ord('k'):
                self.line[self.xpos:] = []
            elif key == ord('d'):
                self.yank[:] = self.line
                if len(self.lines) == 1:
                    self.line[:] = []
                    self.xpos = 0
                elif len(self.lines) > 1:
                    del self.lines[self.ypos]
                    if self.ypos >= len(self.lines):
                        self.ypos = len(self.lines)-1
                    self.line = self.lines[self.ypos]
            elif key == ord('p'):
                self.lines.insert(self.ypos, self.yank[:])
                self.ypos += 1
                self.line = self.lines[self.ypos]
            return
        elif key == pix.key.TAB:
            if mods & 1 != 0:
                i = 0
                while self.line[i] == ' ' and i < 4:
                    i += 1
                self.line[0:i] = []
                self.xpos -= i
                if self.xpos < 0 :
                    self.xpos = 0
            else:
                self.line[self.xpos:self.xpos] = [' '] * 4
                self.xpos += 4
        elif key == pix.key.ENTER:
            rest = self.line[self.xpos:]
            self.lines[self.ypos] = [] if self.xpos == 0 else self.line[
                                                              :self.xpos]
            self.lines.insert(self.ypos + 1, rest)
            self.goto_line(self.ypos + 1)
            self.xpos = 0
            if self.ypos > 0:
                # Simple auto indent
                i = 0
                last_line = self.lines[self.ypos - 1]
                while i < len(last_line) and last_line[i] == ' ':
                    i += 1
                if i and i < len(last_line):
                    self.line[0:0] = [' '] * i
                    self.xpos = i
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
        l = self.rows - 1
        if self.ypos >= self.scroll_pos + l:
            self.scroll_pos = self.ypos - l

    def update(self, events: List[pix.event.AnyEvent]):
        for e in events:
            if isinstance(e, pix.event.Text):
                self.line.insert(self.xpos, e.text)
                self.xpos += len(e.text)
            if isinstance(e, pix.event.Key):
                self.handle_key(e.key, e.mods)
        self.wrap_cursor()

    def set_color(self, fg, bg):
        self.fg = fg;
        self.bg = bg;

    def render(self, context: pix.Context):
        self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
        self.con.clear()
        for y in range(self.rows):
            i = y + self.scroll_pos
            if i >= len(self.lines):
                break
            self.con.cursor_pos = (0, y)
            self.con.write(self.lines[i])

        self.con.cursor_pos = (0, self.rows-1)
        self.con.set_color(pix.color.WHITE, pix.color.BLUE)
        self.con.write(f" LINE {self.ypos + 1} COL {self.xpos + 1} " + " " * (self.cols - 14))
        self.con.set_color(self.fg, self.bg)

        # If current line is visible, move the cursor to the edit position
        if self.ypos >= self.scroll_pos:
            self.con.cursor_pos = (self.xpos, self.ypos - self.scroll_pos)

        self.con.render(context, size = context.size)


def main():
    screen = pix.open_display(width=60 * 16, height=50 * 16)
    edit = TextEdit(rows = 50//2, cols = 120//2)
    while pix.run_loop():
        edit.update(pix.all_events())
        edit.render(screen.context)
        screen.swap()

if __name__ == "__main__":
    main()
