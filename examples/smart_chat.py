
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol
import pixpy as pix
import os
from openai import OpenAI
import json

#from openai.types.responses.response_input_param import Message

@dataclass
class Message:
    role: str = "user"
    content: str = ""

class Console(Protocol):
    def write(self, text: str) -> None: ...

class SmartChat:

    def __init__(self, canvas: pix.Canvas, font: pix.Font):
        self.canvas = canvas
        self.font_size: int = 20
        self.font = font
        self.ts: pix.TileSet = pix.TileSet(self.font, size=self.font_size)
        con_size = canvas.size.toi() / self.ts.tile_size
        self.con: pix.Console = pix.Console(con_size.x, con_size.y - 1, self.ts)
        self.con.set_device_no(1)
        pix.add_event_listener(self.handle_events, 0)

        key = (Path.home() / ".openai.key").read_text().rstrip()
        self.client = OpenAI(api_key=key)

        self.messages : list[Message] = []

    def add_line(self, line: str) -> None:

        self.messages.append(Message(content = line))
        messages = list([asdict(m) for m in self.messages])
        print(messages)
        #messages=[
        #    {"role": "system", "content": "You are a helpful assistant."},
        #    {"role": "user", "content": "Hello!"}
        #]
        response = self.client.responses.create(
            model="gpt-4o-mini",
            instructions="You are an AI programming teacher. You try to help the user with their programming problems, but you want them to learn so avoid directly solving their problems, instead give pointes so they can move forward.",
            input=messages # type: ignore
        )
        print(response.output_text)
        self.messages.append(Message(role = "assistant", content = response.output_text))
        self.con.write(response.output_text)


    def handle_events(self, event: object) -> bool:
        if isinstance(event, pix.event.Text):
            if (event.device == 1):
                print(event.text)
                self.con.write("\n")
                self.add_line(event.text)
                return False
        return True

    
    def write(self, text: str):
        self.con.write(text)

    def render(self):
        self.canvas.draw(self.con, top_left=(0, 0), size=self.con.size)

    def read_line(self):
        self.con.read_line()
