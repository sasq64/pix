import os.path
#import traceback
from pathlib import Path
import pixpy as pix
from editor import TextEdit
import jedi # type: ignore
from jedi.api import Completion # type: ignore
import tree_sitter
import tree_sitter_python as tspython
import builtins

class ListBox:
    def __init__(self):
        self.con = pix.Console(20, 10, font_file="data/Hack.ttf", font_size=24)
        self.xy = pix.Int2(0,0)
        self.selected = 0
        self.lines : list[str] = []

    def set_lines(self, lines: list[str]):
        old_line = self.get_selection()
        self.lines = lines
        self.selected = 0
        if old_line is not None:
            try:
                self.selected = self.lines.index(old_line)
            except ValueError:
                pass
        self.update()

    def set_pos(self, xy: pix.Int2):
        self.xy = xy

    def update(self):
        pos = pix.Int2(0,0)
        self.con.set_color(pix.color.WHITE, pix.color.BLACK)
        self.con.clear()
        for i,line in enumerate(self.lines):
            self.con.cursor_pos = pos
            if self.selected == i:
                self.con.set_color(pix.color.WHITE, pix.color.BLUE)
            else:
                self.con.set_color(pix.color.WHITE, pix.color.BLACK)
            self.con.write(line)
            pos += (0,1)
    
    def move(self, dy: int):
        self.selected += dy
        if self.selected < 0:
            self.selected = 0
        if self.selected >= len(self.lines):
            self.selected = len(self.lines)-1
        self.update()

    def render(self, screen: pix.Context):
        screen.draw_color = 0xffffffff
        screen.filled_rect(top_left=self.xy, size=self.con.size + (8,8))
        screen.draw(self.con, top_left = self.xy + (4,4))
    
    def get_selection(self) -> str | None:
        if len(self.lines) > self.selected:
            return self.lines[self.selected]
        return None

class PixIDE:
    def __init__(self):

        self.colors: dict[str, int] = {
            'default': 1,
            'def': 3,
            'while': 3,
            'if': 3,
            'for': 3,
            'from': 3,
            'else': 3,
            'import': 3,
            'class': 3,
            'string_content': 8,
            'call.identifier': 2,
            'decorator.identifier': 4,
            'keyword_argument.identifier': 7,
            'call.attribute.identifier': 2,
            'function_definition.identifier': 6,
            'typed_parameter.type': 7,
            'type.identifier': 7,
            'integer': 8,
            'float': 8,
            'comment': 6,
            #'identifier': 4
        }

        self.palette = [
            0x2a2a2e,
            0xb1b1b3, # gray
            0xb98eff, # purple
            0xff7de9, # pink
            0xffffb4, # yellow
            0xe9f4fe, # white
            0x86de74, # green string
            0x75bfff, # light blue
            0x6b89ff, # dark blue

        ]


        self.font_size = 24
        font = pix.load_font("data/Hack.ttf", self.font_size)
        ts = pix.TileSet(font)
        self.ar_ok = font.make_image("▶", 30, pix.color.GREEN)
        self.ar_error = font.make_image("▶", 30, pix.color.RED)

        self.con = pix.Console(90, 39, ts)

        self.title = pix.Console(90, 1, font_file="data/Hack.ttf", font_size=self.font_size)
        self.title.set_color(pix.color.WHITE, 0xe17092ff)
        self.title.clear()
        self.title.write("example.py")
        self.tree = None

        self.files = sorted([p for p in Path(".").iterdir() if p.is_file() if p.suffix == ".py"])

        self.comp =  ListBox()
        self.comp_enabled = False
        self.auto_run = False
        language = tree_sitter.Language(tspython.language())
        self.parser = tree_sitter.Parser(language)

        self.current_file : Path
        self.edit = TextEdit(self.con)
        self.edit.set_color(self.palette[1], self.palette[0])
        self.edit.set_palette(self.palette)
        self.load(self.files[1])

        #self.tree = self.parser.parse(self.edit.get_text().encode())
        #self.highlight(self.tree.root_node)
        self.tree = self.parser.parse(self.edit.get_utf16(), encoding="utf16")
        self.highlight(self.tree.root_node, self.tree.root_node.type)
        self.result: list[Completion] = []

    def load(self, path: Path):
        if os.path.isfile(path):
            self.current_file = path
            self.title.clear()
            self.title.cursor_pos = (0,0)
            self.title.write(path.name)
            with open(path) as f:
                if f.readable() :
                    text = f.read()
                    self.edit.set_text(text)


    def update_completion(self):
        script = jedi.Script(self.edit.get_text(), path=self.current_file)
        x,y = self.edit.get_location()
        self.result = script.complete(line=y+1, column=x) # type: ignore
        self.comp.set_lines(list([str(r.name) for r in self.result])) # type: ignore
        self.comp_enabled = True

    def highlight(self, node: tree_sitter.Node, name: str):

        #if node.type in ('function_definition', 'string', 'identifier'): #, 'comment'):

        if node.child_count == 0:
            #print(f"## {node.start_byte} to {node.end_byte}: {name}")

            color = -1
            for nam,col in self.colors.items():
                if name.endswith(nam):
                    color = col
                    break
            if color >= 0:
                self.edit.highlight(node.start_byte//2, node.end_byte//2, color)
            else:
                self.edit.highlight(node.start_byte//2, node.end_byte//2, 1)
        
        #highlights.append((node.start_byte, node.end_byte, node.type))
        for child in node.children:
            if child.type == "call":
                self.highlight(child, child.type)
            else:
                self.highlight(child, name + "." + child.type)

    def render(self, screen: pix.Screen):
        ctrl = pix.is_pressed(pix.key.RCTRL) or pix.is_pressed(pix.key.LCTRL)
        events = pix.all_events()
        keep : list[pix.event.AnyEvent] = []
        should_update = False
        for e in events:
            if isinstance(e, pix.event.Key):
                if ctrl and e.key >= 0x30 and e.key <= 0x39:
                    i = e.key - 0x30
                    self.load(self.files[i])
                    continue
                if e.key == pix.key.TAB:
                    x,_ = self.edit.get_location()
                    if x > 0 and self.edit.get_char(x-1) != 0x20:
                        self.update_completion()
                        continue
                elif e.key == pix.key.F5:
                    if ctrl:
                        self.auto_run = not self.auto_run
                    else:
                        text = self.edit.get_text()
                        with open(Path.home() / '.pixwork.py', 'w') as f:
                            f.write(text)
                        screen.draw_color = (self.palette[1] << 8) | 0xff
                        run(self.edit.get_text())
                    continue
                elif (e.key == pix.key.UP or e.key == pix.key.DOWN) and self.comp_enabled:
                    self.comp.move(-1 if e.key == pix.key.UP else 1)
                    continue
                elif e.key == pix.key.ENTER and self.comp_enabled:
                    self.comp_enabled = False
                    res = self.result[self.comp.selected]
                    i = res.get_completion_prefix_length()
                    self.edit.insert(res.name[i:])
                    continue
                elif e.key == pix.key.BACKSPACE and self.comp_enabled:
                    should_update = True
            elif self.comp_enabled and isinstance(e, pix.event.Text):
                should_update = True
            elif isinstance(e, pix.event.Click):
                self.edit.click(int(e.x), int(e.y) - self.con.tile_size.y)
                continue
            keep.append(e)
        self.comp.set_pos(self.con.cursor_pos * self.con.tile_size)
        self.edit.update(keep)
        if should_update:
            x,_ = self.edit.get_location()
            if x > 0 and self.edit.get_char(x-1) != 0x20:
                self.update_completion()
                
        if self.edit.dirty:
            print("DIRTY")
            text = self.edit.get_utf16()
            #print(text.decode("utf-16"))
            self.tree = self.parser.parse(text, encoding="utf16")
            self.highlight(self.tree.root_node, self.tree.root_node.type)
        self.edit.render()
        #self.con.set_color(pix.color.WHITE, pix.color.RED)
        #self.con.colorize_section(0,11,100)
        #self.con.set_color(pix.color.WHITE, pix.color.LIGHT_BLUE)
        screen.clear(pix.color.DARK_GREY)
        screen.draw(self.con, top_left=(0, self.con.tile_size.y), size=self.con.size)
        screen.draw(self.title, size=self.title.size)
        if self.auto_run:
            source = self.edit.get_text()
            fc = screen.frame_counter
            screen.draw_color = (self.palette[1] << 8) | 0xff
            try:
                pix.allow_break(True)
                exec(source, { __builtins__: builtins })
                pix.allow_break(False)
                events = pix.all_events()
                if fc != screen.frame_counter:
                    self.auto_run = False
                screen.draw(self.ar_ok, top_left=(screen.size.x - 24, -8))
            except Exception as e:
                screen.draw(self.ar_error, top_left=(screen.size.x - 24, -8))
                pass

        if self.comp_enabled:
            self.comp.render(screen.context)
        


def info_box(text: str):

    lines = text.split("\n")
    maxl = len(max(lines, key=lambda i: len(i)))

    sz = pix.Int2(maxl, len(lines))
    con = pix.Console(cols = sz.x, rows = sz.y + 1)
    con.write(text)
    psz = sz * (8,16) + (8,8)
    xy = screen.size - psz 
    screen.context.draw_color = 0x000040ff
    screen.filled_rect(top_left=xy, size=psz)
    screen.draw(con, top_left = xy + (4,4))

def run(source: str):
    fc = screen.frame_counter
    try:
        pix.allow_break(True)
        exec(source, { __builtins__: builtins, __name__: "__main__" })
        pix.allow_break(False)
        if fc != screen.frame_counter:
            events = pix.all_events()
            return
        info_box("[PRESS ANY KEY]")
    except SyntaxError as se:
        screen.swap()
        info_box(f"Syntax error in line {se.lineno}")
    except Exception as e:
        screen.swap()
        info_box(str(e))

    screen.swap()
    leave = False
    while pix.run_loop() and not leave:
        events = pix.all_events()
        for e in events:
            if isinstance(e, pix.event.Key):
                leave = True

def main():
    global screen
    screen = pix.open_display(width=80 * 8 * 2, height=25 * 16 * 2, full_screen=True)

    ide = PixIDE()

    while pix.run_loop():
        ide.render(screen)
        screen.swap()

if __name__ == "__main__":
    main()
