from pathlib import Path
from typing import Literal, Protocol, Callable
from openai.types.responses import FunctionToolParam, ResponseInputItemParam
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
import pixpy as pix
from openai import OpenAI
import inspect

from . import TextEdit


def create_function(
    fn: Callable[..., object],
    desc: str | None = None,
    arg_desc: dict[str, str] | None = None,
) -> FunctionToolParam:
    """Create an OpenAI function schema from a Python function using inspect.signature"""
    sig = inspect.signature(fn)
    properties = {}
    required: list[str] = []

    for param_name, param in sig.parameters.items():
        param_type = "string"
        if param.annotation != inspect.Parameter.empty:
            if param.annotation is int:
                param_type = "integer"
            elif param.annotation is float:
                param_type = "number"
            elif param.annotation is bool:
                param_type = "boolean"
            elif param.annotation is list:
                param_type = "array"
            elif param.annotation is dict:
                param_type = "object"

        properties[param_name] = {"type": param_type}
        if arg_desc:
            if param_name in arg_desc:
                properties[param_name]["description"] = arg_desc[param_name]

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    description = desc or fn.__doc__ or f"Calls the {fn.__name__} function"

    return {
        "type": "function",
        "strict": False,
        "name": fn.__name__,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }



class Console(Protocol):
    def write(self, text: str) -> None: ...


def get_user_name() -> str:
    return "Jonas"


Role = Literal["user", "assistant", "system", "developer"]


def message(text: str, role: Role = "user") -> EasyInputMessageParam:
    return {
        "content": [{"text": text, "type": "input_text"}],
        "role": role,
        "type": "message",
    }


class SmartChat:

    def __init__(self, canvas: pix.Canvas, font: pix.Font, editor: TextEdit):
        self.canvas = canvas
        self.font_size: int = 20
        self.font = font
        self.editor = editor
        self.ts: pix.TileSet = pix.TileSet(self.font, size=self.font_size)
        con_size = canvas.size.toi() / self.ts.tile_size
        self.con: pix.Console = pix.Console(con_size.x, con_size.y - 1, self.ts)
        self.con.set_device_no(1)
        pix.add_event_listener(self.handle_events, 0)

        key = (Path.home() / ".openai.key").read_text().rstrip()
        self.client = OpenAI(api_key=key)

        self.messages: list[ResponseInputItemParam] = []
        self.code: str | None = None
        self.tools: list[FunctionToolParam] = []

        self.add_function(get_user_name)

    def add_function(
        self,
        fn: Callable[..., object],
        desc: str | None = None,
        arg_desc: dict[str, str] | None = None,
    ):
        fd = create_function(fn, desc, arg_desc)
        self.tools.append(fd)

    def set_code(self, code: str):
        self.code = code

    def add_line(self, line: str) -> None:

        self.messages.append(message(line))
        self.code = self.editor.get_text()
        if self.code:
            self.messages.insert(
                0,
                message(
                    f"This is the python code I am currently working on:\n\n{self.code}"
                ),
            )

        response = self.client.responses.create(
            model="gpt-4o-mini",
            instructions="""
You are an AI programming teacher. You try to help the user with their programming problems, but you want them to learn so avoid directly solving their problems, instead give pointers so they can move forward.

Give *short* answers, normally a single sentence would do.
""",
            input=self.messages,
            tools=self.tools,
        )
        print(self.tools)
        print("DONE")
        print(response.output)
        self.messages.append(
            EasyInputMessageParam(role="assistant", content=response.output_text)
        )
        self.con.write(response.output_text)

    def handle_events(self, event: object) -> bool:
        if isinstance(event, pix.event.Text):
            if event.device == 1:
                print(event.text)
                self.con.write("\n")
                self.add_line(event.text)
                self.con.write("\n> ")
                self.read_line()
                return False
        return True

    def write(self, text: str):
        self.con.write(text)

    def render(self):
        self.canvas.draw(self.con, top_left=(0, 0), size=self.con.size)

    def read_line(self):
        self.con.read_line()
