import builtins
import os.path

# import traceback
from pathlib import Path
import traceback
from typing import Final

import pixpy as pix
from editor import TextEdit
from utils.wrap import wrap_lines, wrap_text
from utils.tool_bar import ToolBar, ToolbarEvent
from utils.nerd import Nerd
from smart_chat import SmartChat

fwd = Path(os.path.abspath(__file__)).parent
hack_font = fwd / "data" / "HackNerdFont-Regular.ttf"


class ErrorBox:
    def __init__(
        self,
        canvas: pix.Canvas,
        point_to: pix.Float2,
        text: str,
        font: pix.Font,
        size: int,
    ):
        self.canvas = canvas
        self.point_to = point_to
        margin = 10
        lines: list[str] = []
        for line in text.splitlines():
            lines += wrap_text(line, font, size, canvas.size.x - margin * 2)
        self.lines = [font.make_image(line, size, pix.color.BLACK) for line in lines]
        self.rect_size = pix.Float2(
            canvas.size.x - 2, len(lines) * self.lines[0].size.y + margin * 2
        )
        sz = pix.Float2(32, 24)
        self.triangle = pix.Image(size=sz)
        points: list[pix.Float2] = [pix.Float2(sz.x / 2, 0), sz, pix.Float2(0, sz.y)]
        self.triangle.draw_color = pix.color.LIGHT_RED
        self.triangle.polygon(points, True)

    def set_point(self, to: pix.Float2):
        self.point_to = to

    def render(self):
        target = self.canvas
        target.draw(image=self.triangle, top_left=self.point_to)
        target.draw_color = pix.color.LIGHT_RED
        p = pix.Float2(0, self.point_to.y + self.triangle.size.y)
        target.filled_rect(top_left=p, size=self.rect_size)
        target.draw_color = pix.color.WHITE
        target.rect(top_left=p, size=self.rect_size)
        pos = p + (10, 10)
        for line in self.lines:
            target.draw(line, top_left=pos)
            pos += (0, line.size.y)


class NerdIcon:
    pass


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
            # "ERROR": 9,
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
        self.do_run: bool = False
        self.screen: Final = screen
        self.font_size: int = 20
        self.font: pix.Font = pix.load_font(hack_font)
        self.ts: pix.TileSet = pix.TileSet(self.font, size=self.font_size)

        con_size = screen.size.toi() / self.ts.tile_size

        self.comp_enabled: bool = False
        self.con: pix.Console = pix.Console(con_size.x, con_size.y - 1, self.ts)
        con_size = (screen.size.toi() - 40 * 4) / self.ts.tile_size
        self.title: pix.Console = pix.Console(con_size.x, 1, self.ts)

        self.title_bg: int = 0x205020
        self.running: bool = False
        tool_ts = pix.TileSet(self.font, tile_size=(50, 50))
        self.tool_bar: Final = (
            ToolBar(tile_set=tool_ts, bg_color=self.title_bg, canvas=screen)
            .add_button(Nerd.nf_fa_play_circle, pix.color.LIGHT_GREEN)
            .add_button(Nerd.nf_fa_question_circle, pix.color.LIGHT_BLUE)
        )
        pix.add_event_listener(self.handle_toolbar, 0)

        self.title.set_color(pix.color.WHITE, self.title_bg)
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

        self.error_box: None | ErrorBox = None

        pix.run_every_frame(self.draw_title)

    def handle_toolbar(self, event: object):
        if isinstance(event, ToolbarEvent):
            button = event.button
            print(f"PRESSED {button}")
            if button == 0:
                if self.running:
                    pix.quit_loop()
                else:
                    self.do_run = True
            return False
        return True

    def draw_title(self):
        self.tool_bar.render()
        self.screen.draw(self.title, top_left=(40 * 4, 8), size=self.title.size)
        return True

    def resize(self):
        # self.ts = pix.TileSet(self.font)
        # self.font_size: int = 20
        con_size = self.screen.target_size.toi() / self.ts.tile_size
        print(f"CON SIZE {con_size.x} {con_size.y}")
        self.con = pix.Console(con_size.x, con_size.y - 1, self.ts)
        self.title = pix.Console(
            con_size.x, 1, font_file=hack_font.as_posix(), font_size=self.font_size
        )
        self.set_title(self.current_file.name)
        self.edit.set_console(self.con)

    def set_title(self, name: str):
        self.title.set_color(pix.color.WHITE, self.title_bg)
        self.title.clear()
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

    def show_error(self, text: str, source_pos: pix.Int2):
        print(f"ERROR AT {source_pos}")
        self.edit.scroll_pos = source_pos.y - 2

        # self.edit.dirty = True
        pos = pix.Float2(source_pos.x - 0.5, source_pos.y - self.edit.scroll_pos)
        pos = pos * self.con.tile_size + (0, 48)
        self.error_box = ErrorBox(self.screen, pos, text, self.font, 20)
        print(f"ERROR BOX at {pos}")

    def run(self):
        self.tool_bar.set_button(0, Nerd.nf_fa_stop_circle, pix.color.LIGHT_RED)
        self.running = True
        self.run2()
        self.running = False
        self.tool_bar.set_button(0, Nerd.nf_fa_play_circle, pix.color.LIGHT_GREEN)

    def run2(self):
        screen = self.screen
        # run(self.edit.get_text(), self.current_file.as_posix())
        source = self.edit.get_text()
        file_name = self.current_file.as_posix()
        text = self.edit.get_text()
        with open(Path.home() / ".pixwork.py", "w") as f:
            _ = f.write(text)
        screen.draw_color = (self.palette[1] << 8) | 0xFF
        fc = screen.frame_counter
        try:
            pix.allow_break(True)
            exec(
                source,
                {
                    "__module__": "runcode",
                    "__builtins__": builtins,
                    "__name__": "__main__",
                    "__file__": file_name,
                },
            )
            pix.allow_break(False)
            if fc != screen.frame_counter:
                events = pix.all_events()
                return
            # info_box("[PRESS ANY KEY]")
        except SyntaxError as se:
            screen.swap()
            # info_box(f"Syntax error '{se.msg}' in line {se.lineno}")
            print(f"{se.lineno} {se.offset}")
            self.show_error(se.msg, pix.Int2((se.offset or 1) - 1, se.lineno or 0))
            events = pix.all_events()
            return
        except Exception as e:
            screen.swap()
            info = str(e)
            tbe = traceback.TracebackException.from_exception(e)
            s = tbe.stack[-1]
            self.show_error(info, pix.Int2(s.colno or 0, s.lineno or 0))
            events = pix.all_events()
            return
        screen.swap()
        leave = False
        while pix.run_loop() and not leave:
            events = pix.all_events()
            for e in events:
                if isinstance(e, pix.event.Key):
                    leave = True

    def render(self):
        # print(self.xxx)
        screen = self.screen
        ctrl = pix.is_pressed(pix.key.RCTRL) or pix.is_pressed(pix.key.LCTRL)
        events = pix.all_events()
        keep: list[pix.event.AnyEvent] = []
        should_update = False
        for e in events:
            if isinstance(e, pix.event.Resize):
                print("RESIZE")
                self.resize()
            elif isinstance(e, pix.event.Key):
                self.error_box = None
                if ctrl and e.key >= 0x30 and e.key <= 0x39:
                    i = e.key - 0x30
                    self.load(self.files[i])
                    continue
                #if e.key == pix.key.TAB:
                #    x, _ = self.edit.get_location()
                #    if x > 0 and self.edit.get_char(x - 1) != 0x20:
                #        # self.update_completion()
                #        continue
                if e.key == pix.key.F5:
                    self.run()
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
                self.error_box = None
                should_update = True
            elif isinstance(e, pix.event.Click):
                self.error_box = None
                tbh = self.tool_bar.console.size.y
                self.edit.click(int(e.x), int(e.y) - tbh)
                continue
            keep.append(e)
        # self.comp.set_pos(self.con.cursor_pos * self.con.tile_size)
        self.edit.update(keep)
        if should_update:
            x, _ = self.edit.get_location()
            # if x > 0 and self.edit.get_char(x - 1) != 0x20:
            # self.update_completion()

        if self.edit.dirty:
            self.highlight()
        self.edit.render()
        # self.con.set_color(pix.color.WHITE, pix.color.RED)
        # self.con.colorize_section(0,11,100)
        # self.con.set_color(pix.color.WHITE, pix.color.LIGHT_BLUE)
        screen.clear(pix.color.DARK_GREY)
        tbh = self.tool_bar.console.size.y
        # size = screen.size - (0, tbh)
        screen.draw(self.con, top_left=(0, tbh), size=self.con.size)

        if self.error_box:
            # p = self.con.cursor_pos * self.con.tile_size + (0, 48 + self.con.tile_size.y)
            # self.error_box.set_point(p.tof())
            self.error_box.render()

        # if self.comp_enabled:
        # self.comp.render(screen)
        if self.do_run:
            self.do_run = False
            self.run()


# def info_box(line: int, col: int, text: str):
#     lines = text.split("\n")
#     lines = wrap_lines(lines, 60, " .")
#     maxl = len(max(lines, key=lambda i: len(i)))

#     sz = pix.Int2(maxl, len(lines))
#     con = pix.Console(cols=sz.x, rows=sz.y + 1)
#     con.write(text)
#     psz = sz * (8, 16) + (8, 8)
#     xy = screen.size - psz
#     screen.draw_color = 0x000040FF
#     screen.filled_rect(top_left=xy, size=psz)
#     screen.draw(con, top_left=xy + (4, 4))

def main():
    screen = pix.open_display(width=1280, height=720, full_screen=False)
    split = screen.split((2, 1))
    ide = PixIDE(split[0])
    chat = SmartChat(split[1], pix.load_font(hack_font))
    chat.write("Hello and welcome!\n> ")
    chat.read_line()

    print("RUN")
    while pix.run_loop():
        ide.render()
        chat.render()
        screen.swap()


if __name__ == "__main__":
    main()
