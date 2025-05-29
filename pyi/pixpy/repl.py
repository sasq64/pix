import os

import pixpy as pix
from pixpy.editor import TextEdit
from pathlib import Path
from typing import Optional

class Canvas(pix.Image):
    def clear(self, color: int):
        pix.Image.clear(self, color & 0xffffff00)


class Repl:

    def cprint(self, *text, end: str = '\n'):
        for t in text:
            self.console.write(str(t))
        self.console.write(end)

    def edit(self, what=None):
        if what and os.path.exists(what):
            with open(what, 'r') as f:
                text = [l.rstrip() for l in f.readlines()]
                self.textedit.set_lines(text)

        self.console.cancel_line()
        self.editing = True

    def help(self):
        self.console.write("Sorry, not yet!\n")

    def list(self):
        i = 1
        for line in self.textedit.get_lines():
            self.console.write(f"{i:02} {''.join(line)}\n")
            i += 1

    def run(self):
        code = self.textedit.get_text()
        try:
            exec(code, None, self.scope)
        except Exception as e:
            self.console.write(f"\n## {e}\n> ")

    def run_line(self, line: str):
        try:
            return eval(line, None, self.scope)
        except SyntaxError as e:
            exec(line, None, self.scope)
            return None

    def __init__(self):
        self.editing = False
        self.screen = pix.open_display(width=1280, height=720)
        self.border = pix.Float2(64, 64)
        grid_size = (self.screen.size - self.border * 2) // (8, 16) // 2
        self.console = pix.Console(cols=int(grid_size.x), rows=int(grid_size.y))
        self.ed_con = pix.Console(cols=int(grid_size.x), rows=int(grid_size.y))
        self.canvas: Canvas = Canvas(size=self.screen.size - self.border * 2)
        self.history = []
        self.history_file = str(Path.home()) + '/.pix_history'
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = f.readlines()
            self.history = [h.rstrip() for h in self.history]
        self.pos = len(self.history)
        self.textedit = TextEdit(self.ed_con)

        self.scope = {'print': self.cprint,
                      'screen': self.screen,
                      'edit': self.edit,
                      'run': self.run,
                      'console': self.console,
                      'canvas': self.canvas,
                      'list': self.list}

        self.console.write("pixpy REPL\n")
        self.console.write('> ')
        self.console.read_line()

    def run_repl(self):
        while pix.run_loop():
            self.screen.clear(pix.color.LIGHT_BLUE)
            if self.editing:
                self.textedit.update(pix.all_events())
                if self.textedit.want_to_quit:
                    self.editing = False
                    self.textedit.want_to_quit = False
                    self.console.read_line()
            for e in pix.all_events():
                if type(e) == pix.event.Resize:
                    self.canvas = Canvas(self.screen.size)
                    self.scope['canvas'] = self.canvas
                if type(e) == pix.event.Key:
                    if e.key == pix.key.UP:
                        if self.pos > 0:
                            self.pos -= 1
                            self.console.set_line(self.history[self.pos])
                    if e.key == pix.key.DOWN:
                        if self.pos < len(self.history):
                            pos += 1
                            if pos < len(self.history):
                                self.console.set_line(self.history[self.pos])
                            else:
                                self.console.set_line("")
                if type(e) == pix.event.Text:
                    line = e.text.rstrip()
                    self.history.append(line)
                    self.pos = len(self.history)
                    with open(self.history_file, 'w') as f:
                        for hl in self.history:
                            f.writelines(hl + '\n')
                    pos = len(self.history)
                    self.console.write("\n")
                    try:
                        s = self.run_line(line)
                        if s is not None:
                            self.console.write(f":{s}\n> ")
                        else:
                            self.console.write("> ")
                    except NameError as e:
                        self.console.write(f"## {e}\n> ")
                    except Exception as e:
                        self.console.write(f"## {e}\n> ")
                    if not self.editing:
                        self.console.read_line()

            con = self.console
            if self.editing:
                con = self.ed_con
            con.render(self.screen.context, self.border, self.screen.size - self.border*2)

            self.screen.draw(image=self.canvas, top_left=self.border)
            self.screen.swap()


if __name__ == "__main__":
    repl = Repl()
    repl.run_repl()
