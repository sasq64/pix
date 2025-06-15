import builtins
import os.path

# import traceback
from pathlib import Path
from typing import Final

import pixpy as pix
from editor import TextEdit


fwd = Path(os.path.dirname(os.path.abspath(__file__)))
hack_font = (fwd / "data" / "Hack.ttf").as_posix()


class PixIDE:
    def __init__(self, screen: pix.Screen):

        self.colors: dict[str, int] = {
            "default": 1,
            "def": 3,
            "while": 3,
            "if": 3,
            "for": 3,
            "from": 3,
            "else": 3,
            "import": 3,
            "class": 3,
            "string_start": 8,
            "string_content": 8,
            "string_end": 8,
            "call.identifier": 2,
            "decorator": 4,
            "keyword_argument.identifier": 7,
            "call.attribute.identifier": 2,
            "function_definition.parameters.identifier": 6,
            "typed_parameter.type": 7,
            "type.identifier": 7,
            "integer": 8,
            "float": 8,
            "comment": 6,
            "identifier": 1,
            "ERROR": 8,
        }

        self.palette: Final = [
            0x2A2A2E,
            0xB1B1B3,  # gray
            0xB98EFF,  # purple
            0xFF7DE9,  # pink
            0xFFFFB4,  # yellow
            0xE9F4FE,  # white
            0x86DE74,  # green string
            0x75BFFF,  # light blue
            0x6B89FF,  # dark blue
            0xFF2020,  # red
        ]

        self.font_size: Final = 24
        font = pix.load_font(hack_font, self.font_size)
        ts = pix.TileSet(font)
        self.ar_ok: Final = font.make_image("▶", 30, pix.color.GREEN)
        self.ar_error: Final = font.make_image("▶", 30, pix.color.RED)

        print(ts.tile_size)
        con_size = screen.size.toi() / ts.tile_size

        self.comp_enabled: bool = False
        self.con: Final = pix.Console(con_size.x, con_size.y - 1, ts)
        print(self.con.tile_size)

        self.title: Final = pix.Console(
            con_size.x, 1, font_file=hack_font, font_size=self.font_size
        )
        print(self.title.tile_size)
        self.title.set_color(pix.color.WHITE, 0xE17092FF)
        self.title.clear()
        self.title.write("example.py")

        self.files: Final = sorted(
            [p for p in Path("examples").iterdir() if p.is_file() if p.suffix == ".py"]
        )

        self.auto_run: bool = False
        self.treesitter: Final = pix.treesitter.TreeSitter()
        f = [(a, b) for a, b in self.colors.items()]
        self.treesitter.set_format(f)

        self.current_file: Path
        self.edit: Final = TextEdit(self.con)
        self.edit.set_color(self.palette[1], self.palette[0])
        self.edit.set_palette(self.palette)
        self.load(self.files[1])
        self.highlight()
        print(self.treesitter.dump_tree())
        # self.tree = self.parser.parse(self.edit.get_text().encode())
        # self.highlight(self.tree.root_node)
        # self.tree = self.parser.parse(self.edit.get_utf16(), encoding="utf16")
        # elf.highlight(self.tree.root_node, self.tree.root_node.type)
        # self.result: list[Completion] = []

    def load(self, path: Path):
        if os.path.isfile(path):
            self.current_file = path
            self.title.clear()
            self.title.cursor_pos = (0, 0)
            self.title.write(path.name)
            with open(path) as f:
                if f.readable():
                    text = f.read()
                    self.edit.set_text(text)

    def highlight(self):
        self.treesitter.set_source(self.edit.get_text())
        for col0, row0, col1, row1, color in self.treesitter.get_highlights():
            if color >= 0:
                self.edit.highlight_lines(row0, col0, row1, col1, color)

    def render(self, screen: pix.Screen):
        ctrl = pix.is_pressed(pix.key.RCTRL) or pix.is_pressed(pix.key.LCTRL)
        events = pix.all_events()
        keep: list[pix.event.AnyEvent] = []
        should_update = False
        for e in events:
            if isinstance(e, pix.event.Key):
                if ctrl and e.key >= 0x30 and e.key <= 0x39:
                    i = e.key - 0x30
                    self.load(self.files[i])
                    continue
                if e.key == pix.key.TAB:
                    x, _ = self.edit.get_location()
                    if x > 0 and self.edit.get_char(x - 1) != 0x20:
                        # self.update_completion()
                        continue
                elif e.key == pix.key.F5:
                    if ctrl:
                        self.auto_run = not self.auto_run
                    else:
                        text = self.edit.get_text()
                        with open(Path.home() / ".pixwork.py", "w") as f:
                            _ = f.write(text)
                        screen.draw_color = (self.palette[1] << 8) | 0xFF
                        run(self.edit.get_text())
                    continue
                elif (
                    e.key == pix.key.UP or e.key == pix.key.DOWN
                ) and self.comp_enabled:
                    # self.comp.move(-1 if e.key == pix.key.UP else 1)
                    continue
                elif e.key == pix.key.ENTER and self.comp_enabled:
                    self.comp_enabled = False
                    # res = self.result[self.comp.selected]
                    # i = res.get_completion_prefix_length()
                    # self.edit.insert(res.name[i:])
                    continue
                elif e.key == pix.key.BACKSPACE and self.comp_enabled:
                    should_update = True
            elif self.comp_enabled and isinstance(e, pix.event.Text):
                should_update = True
            elif isinstance(e, pix.event.Click):
                self.edit.click(int(e.x), int(e.y) - self.con.tile_size.y)
                continue
            keep.append(e)
        # self.comp.set_pos(self.con.cursor_pos * self.con.tile_size)
        self.edit.update(keep)
        if should_update:
            x, _ = self.edit.get_location()
            # if x > 0 and self.edit.get_char(x - 1) != 0x20:
            # self.update_completion()

        if self.edit.dirty:
            print("DIRTY")
            self.highlight()
            # text = self.edit.get_utf16()
            # print(text.decode("utf-16"))
            # self.tree = self.parser.parse(text, encoding="utf16")
            # self.highlight(self.tree.root_node, self.tree.root_node.type)
        self.edit.render()
        # self.con.set_color(pix.color.WHITE, pix.color.RED)
        # self.con.colorize_section(0,11,100)
        # self.con.set_color(pix.color.WHITE, pix.color.LIGHT_BLUE)
        screen.clear(pix.color.DARK_GREY)
        size = screen.size - (0, self.con.tile_size.y)
        screen.draw(self.con, top_left=(0, self.con.tile_size.y), size=self.con.size)
        screen.draw(self.title, size=self.title.size)
        if self.auto_run:
            source = self.edit.get_text()
            fc = screen.frame_counter
            screen.draw_color = (self.palette[1] << 8) | 0xFF
            try:
                pix.allow_break(True)
                exec(source, {__builtins__: builtins})
                pix.allow_break(False)
                events = pix.all_events()
                if fc != screen.frame_counter:
                    self.auto_run = False
                screen.draw(self.ar_ok, top_left=(screen.size.x - 24, -8))
            except Exception as e:
                screen.draw(self.ar_error, top_left=(screen.size.x - 24, -8))
                pass

        if self.comp_enabled:
            self.comp.render(screen)


def info_box(text: str):

    lines = text.split("\n")
    maxl = len(max(lines, key=lambda i: len(i)))

    sz = pix.Int2(maxl, len(lines))
    con = pix.Console(cols=sz.x, rows=sz.y + 1)
    con.write(text)
    psz = sz * (8, 16) + (8, 8)
    xy = screen.size - psz
    screen.draw_color = 0x000040FF
    screen.filled_rect(top_left=xy, size=psz)
    screen.draw(con, top_left=xy + (4, 4))


def run(source: str):
    fc = screen.frame_counter
    try:
        pix.allow_break(True)
        exec(source, {__builtins__: builtins, __name__: "__main__"})
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
    screen = pix.open_display(
        width=1280, height=720, full_screen=False, visible=True
    )
    ide = PixIDE(screen)

    print("RUN")
    while pix.run_loop():
        ide.render(screen)
        screen.swap()


if __name__ == "__main__":
    main()
