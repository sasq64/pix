import pixpy as pix
from array import array


def clamp(v, lo, hi):
    if v < lo:
        return lo
    if v >= hi:
        return hi - 1
    return v


class TextEdit:

    def __init__(self, console):
        self.lines = [[]]
        self.line = self.lines[0]
        self.scroll_pos = 0
        self.xpos = 0
        self.ypos = 0
        self.want_to_quit = False
        self.con = console
        self.con.cursor_on = True
        self.con.cursor_pos = (0, 0)
        self.cols = int(console.grid_size.x)
        self.rows = int(console.grid_size.y)

    def goto_line(self, y):
        if y < 0 or y >= len(self.lines):
            return False
        self.ypos = y
        self.line = self.lines[y]
        self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
        return True

    def get_text(self):
        return "\n".join(["".join(l) for l in self.lines])

    def set_lines(self, lines):
        self.lines = lines
        self.scroll_pos = 0
        self.xpos = self.ypos = 0
        self.line = self.lines[0]

    def get_lines(self):
        return self.lines

    def handle_key(self, key, mods):
        if mods & 2:
            if key == ord('x'):
                self.want_to_quit = True
            return
        elif key == pix.key.LEFT:
            self.xpos -= 1
        elif key == pix.key.RIGHT:
            self.xpos += 1
        elif key == pix.key.TAB:
            self.line[self.xpos:self.xpos] = [' '] * 4
            self.xpos += 4
        elif key == pix.key.HOME:
            self.xpos = 0
        elif key == pix.key.END:
            self.xpos = len(self.line)
        elif key == pix.key.UP:
            self.goto_line(self.ypos - 1)
        elif key == pix.key.DOWN:
            self.goto_line(self.ypos + 1)
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

    def update(self, events):
        for e in events:
            #print(f"EVENT: {e}")
            if type(e) == pix.event.Text:
                self.line.insert(self.xpos, e.text)
                self.xpos += len(e.text)
            if type(e) == pix.event.Key:
                #print(f"{e.key} {e.mods}\n")
                self.handle_key(e.key, e.mods)

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
        if self.ypos >= self.scroll_pos + (self.rows-2):
            self.scroll_pos = self.ypos - (self.rows-2)

        self.xpos = clamp(self.xpos, 0, len(self.line) + 1)
        self.con.clear()
        for y in range(self.rows-1):
            i = y + self.scroll_pos
            if i >= len(self.lines):
                break
            self.con.cursor_pos = (0, y)
            self.con.write(self.lines[i])

        self.con.cursor_pos = (0, self.rows-1)
        self.con.set_color(pix.color.WHITE, pix.color.BLUE)
        info = f" LINE {(self.ypos + 1):03} COL {(self.xpos + 1):03}" + \
               " : CTRL-X to exit"
        self.con.write(info + " " * (self.cols-len(info)-1))
        self.con.set_color(pix.color.GREEN, pix.color.BLACK)

        # If current line is visible, move the cursor to the edit position
        if self.ypos >= self.scroll_pos:
            self.con.cursor_pos = (self.xpos, self.ypos - self.scroll_pos)


def run():
    screen = pix.open_display(1280, 720)
    con = pix.Console(1280//8, 720//16)
    edit = TextEdit(con)
    while pix.run_loop() and not edit.want_to_quit:
        edit.update(pix.all_events())
        screen.draw(con)
        screen.swap()


if __name__ == "__main__":
    run()
