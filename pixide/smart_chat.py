from concurrent.futures import Future, ThreadPoolExecutor
import json
import os
import inspect
from pathlib import Path
import subprocess
from textwrap import wrap
from typing import Literal, Protocol, Callable, TypeGuard
import pixpy as pix

from pixide.voice_recorder import VoiceToText
from pixide.markdown import MarkdownRenderer
from pixide.chat import Chat, Message

from .ide import PixIDE

from pixide.openaiclient import OpenAIClient

data_path = Path(os.path.abspath(__file__)).parent / "data"



def get_pixpy_information() -> str:
    """Get an overview of the functions and usage that makes up the pixpy library."""
    return (data_path / "pixpy_prompt.md").read_text()


class SmartChat:
    def __init__(self, canvas: pix.Canvas, font: pix.Font, ide: PixIDE):
        self.canvas = canvas
        self.font_size: int = 24
        self.font = font
        self.editor = ide.edit
        self.ide = ide
        self.active: bool = False
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.tile_set: pix.TileSet = pix.TileSet(self.font, size=self.font_size)
        self.reading_line: bool = True
        self.resize()
        self.console.cursor_on = False
        self.is_recording : bool = False
        self.vtt_result: Future[str] | None = None

        self.vtt = VoiceToText()
        pix.add_event_listener(self.handle_events, 0)

        key_file = Path.home() / ".openai.key"
        if not key_file.exists():
            raise FileNotFoundError("Can not find .openai.key in $HOME!")
        key = (Path.home() / ".openai.key").read_text().rstrip()
        self.client = OpenAIClient(api_key=key)
        instructions = (data_path / "instructions.md").read_text()
        self.client.instructions = instructions

        self.code: str | None = None

        # Chat integration
        self.chat = Chat("ws://localhost:8080")

        self.client.add_function(self.read_users_program)
        self.client.add_function(self.run_users_program)
        self.client.add_function(get_pixpy_information)

        self.chat.start_threaded()

    def run(self) -> str:
        current_file = self.ide.current_file
        file_name = current_file.as_posix()
        print(file_name)
        file_dir = str(current_file.parent.absolute())
        text = self.editor.get_text()
        with open(Path.home() / ".pixwork.py", "w") as f:
            _ = f.write(text)

        new_env = os.environ.copy()
        new_env["PIX_CHECK"] = "1"
        new_env["PYTHONPATH"] = file_dir + os.pathsep + new_env.get("PYTHONPATH", "")

        pr = subprocess.run(
            ["python3", (Path.home() / ".pixwork.py").as_posix()],
            capture_output=True,
            env=new_env,
        )
        return pr.stderr.decode()

    def get_box_contents(self, box_no: int) -> str:
        """Get the contents of a numbered box"""
        return str(box_no * 5)

    def read_users_program(self) -> str:
        """Get the source of the users current python program."""
        return self.editor.get_text()

    def run_users_program(self) -> str:
        """Run the users program in headless mode for one frame. Use this function to see which errors (if any) the program contains. Will return 'OK' if no errors detected, otherwise the error in string form."""
        return self.run()

    def resize(self):
        con_size = self.canvas.size.toi() // self.tile_set.tile_size
        self.console = pix.Console(con_size.x, con_size.y - 1, self.tile_set)
        self.console.wrap_lines = False
        self.console.autoscroll = True
        self.console.set_device_no(1)
        self.markdown_renderer = MarkdownRenderer(self.console)
        self.write("Let me know if you need help.\n")
        if self.reading_line:
            self.read_line()

    def set_code(self, code: str):
        self.code = code

    def handle_events(self, event: object) -> bool:
        if isinstance(event, pix.event.Text) and event.device == 1:
            if self.reading_line:
                self.reading_line = False
                # User entered a line of text
                print(event.text)
                xy = self.console.cursor_pos
                self.console.clear_area(xy.x, xy.y, self.console.grid_size.x - 2, 1)
                self.markdown_renderer.set_color("normal", pix.color.LIGHT_BLUE)
                self.markdown_renderer.render(event.text)
                self.markdown_renderer.set_color("normal", pix.color.WHITE)
                self.client.add_line(event.text)
            return False
        return True

    def write(self, text: str, color: int = pix.color.WHITE):
        self.console.set_color(color, pix.color.BLACK)
        x = self.console.cursor_pos.x
        lines = wrap(text, self.console.grid_size.x - x - 1)
        if len(lines) == 0:
            self.console.write(text)
            return
        self.console.write(lines[0])
        self.console.write("\n")
        pre = " " * x
        for line in lines[1:]:
            self.console.write(pre + line)
            self.console.write("\n")

    def activate(self, on: bool):
        self.active = on
        if on:
            self.console.cursor_on = True
        else:
            self.console.cursor_on = False

    def render(self):

        if pix.is_pressed(pix.key.F7):
            if not self.is_recording:
                self.is_recording = True
                self.vtt.start_transribe()
            xy = self.canvas.size - (10,10)
            self.canvas.draw_color = pix.color.LIGHT_GREEN
            self.canvas.filled_circle(center=xy, radius=10)
        elif self.is_recording:
            self.is_recording = False
            self.vtt_result = self.vtt.end_transcribe()

        if self.vtt_result and self.vtt_result.done():
            text = self.vtt_result.result()
            print(f"TRANSCRIBE: {text}")
            self.vtt_result = None
            self.write(text)
            self.write("\n")
            self.add_line(text)

        # Process any pending chat messages
        self.process_chat_messages()

        if pix.is_pressed(pix.key.F7):
            if not self.is_recording:
                self.is_recording = True
                self.vtt.start_transribe()
            xy = self.canvas.size - (10,10)
            self.canvas.draw_color = pix.color.LIGHT_GREEN
            self.canvas.filled_circle(center=xy, radius=10)
        elif self.is_recording:
            self.is_recording = False
            self.vtt_result = self.vtt.end_transcribe()

        if self.vtt_result and self.vtt_result.done():
            text = self.vtt_result.result()
            print(f"TRANSCRIBE: {text}")
            self.vtt_result = None
            self.write(text)
            self.write("\n")
            self.client.add_line(text)

        # Process any pending chat messages
        response = self.client.update()
        if response is not None:
            #self.console.cancel_line()
            self.markdown_renderer.render(response.text)
            self.read_line()

        self.canvas.draw(self.console, top_left=(0, 0), size=self.console.size)

    def read_line(self):
        self.console.set_color(pix.color.YELLOW, pix.color.BLACK)
        self.console.write("\n> ")
        self.console.set_color(pix.color.LIGHT_BLUE, pix.color.BLACK)
        self.console.read_line()
        self.reading_line = True

    def stop_chat(self):
        """Stop chat functionality."""
        self.chat.stop_threaded()

    def send_chat_message(self, content: str):
        """Send a chat message."""
        self.chat.send_message_threaded(content)

    def process_chat_messages(self):
        """Process pending chat messages from the queue."""
        messages = self.chat.get_messages()
        for message in messages:
            self._process_incoming_chat_message(message)

    def _process_incoming_chat_message(self, message: Message):
        msg_type = message.get("type")
        user_id = message.get("userId", "unknown")
        content = message.get("content", "")

        if msg_type == "chat_message" and user_id != self.chat.get_user_id():
            # Display chat message
            self.write("\n")
            self.markdown_renderer.render(content)
            self.write("\n")
            print(f"Chat from {user_id}: {content}")
        elif msg_type == "user_joined":
            print(f"User {user_id} joined the chat")
        elif msg_type == "user_left":
            print(f"User {user_id} left the chat")
