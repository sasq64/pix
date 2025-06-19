import builtins
import os.path

# import traceback
from pathlib import Path
import traceback
from typing import Final

import pixpy as pix
from editor import TextEdit


fwd = Path(os.path.dirname(os.path.abspath(__file__)))
hack_font = (fwd / "data" / "HackNerdFont-Regular.ttf").as_posix()


class ToolBar:
    def __init__(
        self,
        ts: pix.TileSet | None = None,
        pos: pix.Float2 = pix.Float2.ZERO,
        canvas: pix.Canvas | None = None,
    ):
        self.canvas: pix.Canvas = canvas or pix.get_display()
        self.tile_set: Final = ts or pix.TileSet(tile_size=(48, 48))
        self.pos: pix.Float2 = pos
        cols = 40  # int(self.canvas.size.x / self.tile_set.tile_size.x)
        self.add_pos: pix.Int2 = pix.Int2(0, 0)
        print(f"COLS {cols}")
        self.console: Final = pix.Console(rows=1, cols=cols, tile_set=self.tile_set)
        print(f"SIZE {self.console.grid_size}")
        pass

    def add_button(self, tno: int, color: int):
        self.console.put(self.add_pos, tno, color)
        print(f"{self.console.grid_size}")
        self.add_pos += (1, 0)

    def render(self):
        self.canvas.draw(self.console, self.pos, size=self.console.size)


def run(source: str, file_name: str):
    fc = screen.frame_counter
    try:
        pix.allow_break(True)
        exec(
            source,
            {
                "__builtins__": builtins,
                "__name__": "__main__",
                "__file__": file_name,
            },
        )
        pix.allow_break(False)
        if fc != screen.frame_counter:
            events = pix.all_events()
            return
        info_box("[PRESS ANY KEY]")
    except SyntaxError as se:
        screen.swap()
        info_box(f"Syntax error '{se.msg}' in line {se.lineno}")
    except Exception as e:
        screen.swap()
        info = traceback.format_exc()
        info_box(info)
    screen.swap()
    leave = False
    while pix.run_loop() and not leave:
        events = pix.all_events()
        for e in events:
            if isinstance(e, pix.event.Key):
                leave = True


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
            "string": 8,
            # "string_content": 8,
            # "string_end": 8,
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
            "ERROR": 9,
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

        self.screen: Final = screen
        self.font_size: int = 20
        self.font: pix.Font = pix.load_font(hack_font, self.font_size)
        self.ts: pix.TileSet = pix.TileSet(self.font)

        con_size = screen.size.toi() / self.ts.tile_size

        self.comp_enabled: bool = False
        self.con: pix.Console = pix.Console(con_size.x, con_size.y - 1, self.ts)
        print(self.con.tile_size)
        con_size = (screen.size.toi() - 40 * 4) / self.ts.tile_size
        self.title: pix.Console = pix.Console(con_size.x, 1, self.ts)

        tool_ts = pix.TileSet(self.font, tile_size=(50, 50))
        self.tool_bar: Final = ToolBar(ts=tool_ts)
        self.tool_bar.add_button(0xF144, pix.color.LIGHT_GREEN)
        self.tool_bar.add_button(0xF059, pix.color.LIGHT_BLUE)
        self.tool_bar.add_button(0xF28D, pix.color.LIGHT_RED)

        print(self.title.tile_size)
        self.title.set_color(pix.color.WHITE, 0xE17092FF)
        self.set_title("example.py")

        self.files: Final = sorted(
            [p for p in Path("examples").iterdir() if p.is_file() if p.suffix == ".py"]
        )

        self.treesitter: Final = pix.treesitter.TreeSitter()
        f = [(a, b) for a, b in self.colors.items()]
        self.treesitter.set_format(f)

        self.current_file: Path
        self.edit: Final = TextEdit(self.con)
        self.edit.set_color(self.palette[1], self.palette[0])
        self.edit.set_palette(self.palette)
        self.load(self.files[1])
        self.highlight()

        pix.run_every_frame(self.draw_title)
        _ = pix.add_event_listener(self.title_events, 0)

    def title_events(self, event: pix.event.AnyEvent):
        if isinstance(event, pix.event.Click):
            if event.y < self.title.size.y:
                print("CLICK TITLE")
                return False
        return True

    def draw_title(self):
        self.tool_bar.render()
        # screen.draw(self.title, top_left=(40 * 4, 8), size=self.title.size)
        return True

    def resize(self):
        # self.ts = pix.TileSet(self.font)
        # self.font_size: int = 20
        con_size = self.screen.target_size.toi() / self.ts.tile_size
        print(f"CON SIZE {con_size.x} {con_size.y}")
        self.con = pix.Console(con_size.x, con_size.y - 1, self.ts)
        self.title = pix.Console(
            con_size.x, 1, font_file=hack_font, font_size=self.font_size
        )
        self.set_title(self.current_file.name)
        self.edit.set_console(self.con)

    def set_title(self, name: str):
        self.title.set_color(pix.color.WHITE, pix.color.DARK_GREY)
        self.title.clear()
        x = 0  # self.title.grid_size.x - 20
        self.title.put((x, 0), 0xF144, pix.color.LIGHT_GREEN)
        self.title.put((x + 1, 0), 0xF059, pix.color.LIGHT_BLUE)
        self.title.put((x + 2, 0), 0xF28D, pix.color.LIGHT_RED)

        self.title.cursor_pos = (10, 0)
        self.title.write(f"\ue73c {name}")
        self.title.cursor_pos = (self.title.grid_size.x - 10, 0)
        col, line = self.con.cursor_pos
        self.title.write(f"\ue0a1 {line} \ue0a3 {col}")

    def load(self, path: Path):
        if os.path.isfile(path):
            self.current_file = path
            self.set_title(path.name)
            with open(path) as f:
                if f.readable():
                    text = f.read()
                    self.edit.set_text(text)
        self.treesitter.set_source(self.edit.get_text())
        # print(self.treesitter.dump_tree())

    def highlight(self):
        self.treesitter.set_source(self.edit.get_text())
        for col0, row0, col1, row1, color in self.treesitter.get_highlights():
            if color < 0:
                color = 1
            self.edit.highlight_lines(row0, col0, row1, col1, color)

    def render(self):
        screen = self.screen
        ctrl = pix.is_pressed(pix.key.RCTRL) or pix.is_pressed(pix.key.LCTRL)
        events = pix.all_events()
        keep: list[pix.event.AnyEvent] = []
        should_update = False
        for e in events:
            if isinstance(e, pix.event.Resize):
                print("RESIZE")
                self.resize()
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
                        pass
                    else:
                        text = self.edit.get_text()
                        with open(Path.home() / ".pixwork.py", "w") as f:
                            _ = f.write(text)
                        screen.draw_color = (self.palette[1] << 8) | 0xFF
                        run(self.edit.get_text(), self.current_file.as_posix())
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
        self.edit.render()
        # self.con.set_color(pix.color.WHITE, pix.color.RED)
        # self.con.colorize_section(0,11,100)
        # self.con.set_color(pix.color.WHITE, pix.color.LIGHT_BLUE)
        screen.clear(pix.color.DARK_GREY)
        size = screen.size - (0, self.con.tile_size.y)
        screen.draw(self.con, top_left=(0, self.con.tile_size.y), size=self.con.size)
        # if self.comp_enabled:
        # self.comp.render(screen)


def wrap_lines(lines: list[str], max_len: int, break_chars: str = " ") -> list[str]:
    result: list[str] = []
    for line in lines:
        start = 0
        while start < len(line):
            # Try to find a break point
            end = min(start + max_len, len(line))
            if end == len(line):
                result.append(line[start:end])
                break
            # Scan backwards for break char
            break_pos = -1
            for i in range(end - 1, start - 1, -1):
                if line[i] in break_chars:
                    break_pos = i + 1  # include the break character
                    break
            if break_pos == -1 or break_pos == start:
                # no break char found, or stuck — force break
                break_pos = end
            result.append(line[start:break_pos].rstrip())
            start = break_pos
    return result


def info_box(text: str):
    lines = text.split("\n")
    lines = wrap_lines(lines, 60, " .")
    maxl = len(max(lines, key=lambda i: len(i)))

    sz = pix.Int2(maxl, len(lines))
    con = pix.Console(cols=sz.x, rows=sz.y + 1)
    con.write(text)
    psz = sz * (8, 16) + (8, 8)
    xy = screen.size - psz
    screen.draw_color = 0x000040FF
    screen.filled_rect(top_left=xy, size=psz)
    screen.draw(con, top_left=xy + (4, 4))


def main():
    global screen
    screen = pix.open_display(width=640, height=720, full_screen=False)
    ide = PixIDE(screen)

    print("RUN")
    while pix.run_loop():
        ide.render()
        screen.swap()


if __name__ == "__main__":
    main()
