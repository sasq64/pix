import builtins
import os.path
import sys
import traceback
from pathlib import Path
from typing import Final

import pixpy as pix
from .editor import TextEdit
from .utils.wrap import wrap_text
from .utils.tool_bar import ToolBar, ToolbarEvent
from .utils.nerd import Nerd
from .treesitter import TreeSitter

Int2 = pix.Int2
Float2 = pix.Float2

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
        self.lines = [
            font.make_image(line, size, pix.color.BLACK) for line in lines
        ]
        self.rect_size = pix.Float2(
            canvas.size.x - 2, len(lines) * self.lines[0].size.y + margin * 2
        )
        sz = pix.Float2(32, 24)
        self.triangle = pix.Image(size=sz)
        points: list[pix.Float2] = [
            pix.Float2(sz.x / 2, 0),
            sz,
            pix.Float2(0, sz.y),
        ]
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


class PixIDE:
    def __init__(self, screen: pix.Screen, font_size: int = 24):
        self.do_run: bool = False
        self.screen: pix.Screen = screen
        self.font_size: int = font_size
        self.font: pix.Font = pix.load_font(hack_font)
        self.ts: pix.TileSet = pix.TileSet(self.font, size=self.font_size)

        con_size = screen.size.toi() / self.ts.tile_size

        self.comp_enabled: bool = False
        self.console: pix.Console = pix.Console(con_size.x, con_size.y - 1, self.ts)
        self.console.wrapping = False
        self.title_bg: int = 0x2050FF
        self.running: bool = False
        tool_ts = pix.TileSet(self.font, tile_size=(50, 50))
        self.tool_bar: Final = (
            ToolBar(tile_set=tool_ts, bg_color=self.title_bg, canvas=screen)
            .add_button(Nerd.nf_fa_play_circle, pix.color.LIGHT_GREEN)
            .add_button(Nerd.nf_fa_question_circle, pix.color.LIGHT_BLUE)
        )
        self.toolbar_height: int = self.tool_bar.console.size.y
        self.scrollbar_width: int = 8

        con_size = (screen.size.toi() - self.tool_bar.size) / self.ts.tile_size
        self.title: pix.Console = pix.Console(con_size.x, 1, self.ts)

        pix.add_event_listener(self.handle_toolbar, 0)

        self.title.set_color(pix.color.WHITE, self.title_bg)
        self.set_title("example.py")

        self.files: Final = sorted(
            [
                p
                for p in Path("examples").iterdir()
                if p.is_file()
                if p.suffix == ".py"
            ]
        )

        self.current_file: Path
        self.edit: Final = TextEdit(self.console)
        self.treesitter: TreeSitter = TreeSitter(self.edit)
        self.load(self.files[1])
        self.treesitter.highlight()

        self.error_box: None | ErrorBox = None

        self.resize()

        pix.run_every_frame(self.draw_title)

    def activate(self, on: bool):
        self.edit.show_cursor = on

    def get_text(self) -> str:
        """Get the current editor text content"""
        return self.edit.get_text()

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
        self.screen.draw_color = self.title_bg
        self.screen.filled_rect(
            (0, 0), size=(self.screen.size.x, self.toolbar_height)
        )

        self.tool_bar.render()
        sz = self.tool_bar.size

        self.screen.draw(
            self.title,
            top_left=(sz.x + 2, (sz.y - self.title.size.y) / 2),
            size=self.title.size,
        )
        return True

    def resize(self):
        con_size = (
            self.screen.size.toi() - (self.scrollbar_width+2, self.toolbar_height)
        ) / self.ts.tile_size
        print(f"TARGET SIZE {self.screen.target_size} CON SIZE {con_size}")
        self.console = pix.Console(con_size.x, con_size.y, self.ts)
        self.title = pix.Console(
            con_size.x - (self.tool_bar.size.x // self.ts.tile_size.x),
            1,
            font_file=hack_font.as_posix(),
            font_size=self.font_size,
        )
        self.set_title(self.current_file.name)
        self.edit.set_console(self.console)

    def set_title(self, name: str):
        self.title.set_color(pix.color.WHITE, self.title_bg)
        self.title.clear()
        self.title.cursor_pos = Int2(0, 0)
        self.title.write(f"\ue73c {name}")
        self.title.cursor_pos = Int2(self.title.grid_size.x - 10, 0)
        # self.update_pos()

    def update_pos(self):
        col, line = self.edit.cursor_col + 1, self.edit.cursor_line + 1
        self.title.cursor_pos = pix.Int2(self.title.grid_size.x - 18, 0)
        self.title.write(f"Ln {line:<3} Col {col:<3}  ")

    def draw_scrollbar(self):
        """Draw a scroll bar on the right side of the editor area"""
        if len(self.edit.lines) <= self.edit.rows:
            return  # No scrollbar needed if all content fits

        # Scrollbar dimensions
        scrollbar_pos = pix.Float2(
            self.screen.size.x - self.scrollbar_width - 2, self.toolbar_height
        )
        scrollbar_height = self.screen.size.y - self.toolbar_height

        # Background track
        self.screen.draw_color = pix.color.DARK_GREY
        self.screen.filled_rect(
            top_left=scrollbar_pos,
            size=pix.Float2(self.scrollbar_width, scrollbar_height),
        )

        # Calculate thumb position and size
        total_lines = len(self.edit.lines)
        visible_lines = self.edit.rows
        thumb_height = max(20, (visible_lines / total_lines) * scrollbar_height)

        # Calculate thumb position (avoid division by zero)
        max_scroll = max(1, total_lines - visible_lines)
        thumb_y = (self.edit.horizontal_scroll / max_scroll) * (
            scrollbar_height - thumb_height
        )

        # Draw thumb
        self.screen.draw_color = pix.color.LIGHT_GREY
        self.screen.filled_rect(
            top_left=scrollbar_pos + (0, thumb_y),
            size=pix.Float2(self.scrollbar_width, thumb_height),
        )

    def load(self, path: Path):
        if os.path.isfile(path):
            self.current_file = path
            self.set_title(path.name)
            with open(path) as f:
                if f.readable():
                    text = f.read()
                    self.edit.set_text(text)
        self.treesitter.highlight()

    def show_error(self, text: str, source_pos: pix.Int2):
        print(f"ERROR AT {source_pos}")
        self.edit.horizontal_scroll = source_pos.y - 2

        pos = pix.Float2(
            source_pos.x - 0.5, source_pos.y - self.edit.horizontal_scroll
        )
        pos = pos * self.console.tile_size + (0, self.toolbar_height)
        self.error_box = ErrorBox(self.screen, pos, text, self.font, 20)
        print(f"ERROR BOX at {pos}")

    def run(self):
        self.tool_bar.set_button(0, Nerd.nf_fa_stop_circle, pix.color.LIGHT_RED)
        self.running = True
        self.run2()
        self.running = False
        self.tool_bar.set_button(
            0, Nerd.nf_fa_play_circle, pix.color.LIGHT_GREEN
        )

    def run2(self):
        screen = self.screen
        source = self.edit.get_text()
        file_name = self.current_file.name
        print(file_name)
        file_dir = str(self.current_file.parent.absolute())
        text = self.edit.get_text()
        with open(Path.home() / ".pixwork.py", "w") as f:
            _ = f.write(text)
        col = 0xB1B1B3
        screen.draw_color = (col << 8) | 0xFF
        fc = screen.frame_counter

        # Save current working directory and sys.path to restore later
        original_cwd = os.getcwd()
        original_sys_path = sys.path[:]

        try:
            # Change to the file's directory
            os.chdir(file_dir)
            
            # Add the current file's directory to sys.path so imports work
            if file_dir not in sys.path:
                sys.path.insert(0, file_dir)

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
        except SyntaxError as se:
            screen.swap()
            print(f"{se.lineno} {se.offset}")
            self.show_error(
                se.msg, pix.Int2((se.offset or 1) - 1, se.lineno or 0)
            )
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
        finally:
            # Restore original working directory and sys.path
            os.chdir(original_cwd)
            sys.path[:] = original_sys_path
        screen.swap()
        leave = False
        while pix.run_loop() and not leave:
            events = pix.all_events()
            for ev in events:
                if isinstance(ev, pix.event.Key):
                    leave = True

    def render(self):
        screen = self.screen
        ctrl = pix.is_pressed(pix.key.RCTRL) or pix.is_pressed(pix.key.LCTRL)
        events = pix.all_events()
        keep: list[pix.event.AnyEvent] = []
        should_update = len(events) > 0
        for e in events:
            if isinstance(e, pix.event.Key):
                self.error_box = None
                if ctrl and e.key == ord("u"):
                    self.treesitter.select_parent_node()
                if ctrl and e.key >= 0x30 and e.key <= 0x39:
                    i = e.key - 0x30
                    self.load(self.files[i])
                    continue
                # if e.key == pix.key.TAB:
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
                print("CLICK EVENT")
                if e.y >= self.toolbar_height:
                    self.error_box = None
                    keep.append(
                        pix.event.Click(
                            e.x, e.y - self.toolbar_height, e.buttons, e.mods
                        )
                    )
                    continue
            elif isinstance(e, pix.event.Move):
                self.error_box = None
                keep.append(
                    pix.event.Move(e.x, e.y - self.toolbar_height, e.buttons)
                )
                continue
            keep.append(e)
        # self.comp.set_pos(self.console.cursor_pos * self.console.tile_size)
        self.edit.update(keep)
        if should_update:
            self.update_pos()
            # x, _ = self.edit.get_location()
            # if x > 0 and self.edit.get_char(x - 1) != 0x20:
            # self.update_completion()

        if self.edit.dirty:
            self.treesitter.highlight()
        self.edit.render()
        screen.clear(pix.color.DARK_GREY)
        # size = screen.size - (0, self.toolbar_height)
        screen.draw(
            self.console, top_left=(0, self.toolbar_height), size=self.console.size
        )

        # Draw scrollbar
        self.draw_scrollbar()

        if self.error_box:
            self.error_box.render()

        # if self.comp_enabled:
        # self.comp.render(screen)
        if self.do_run:
            self.do_run = False
            self.run()
