import builtins
from concurrent.futures import Future, ThreadPoolExecutor
import json
import os
import inspect
from pathlib import Path
import subprocess
from typing import Literal, Protocol, Callable

from openai.types.responses import (
    FunctionToolParam,
    Response,
    ResponseFunctionToolCall,
    ResponseFunctionToolCallParam,
    ResponseInputItemParam,
    ResponseReasoningItemParam,
)
from openai.types.responses.easy_input_message_param import EasyInputMessageParam
from openai.types.responses.response_input_item_param import FunctionCallOutput
from openai import OpenAI

import pixpy as pix

from .ide import PixIDE


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


Role = Literal["user", "assistant", "system", "developer"]


def message(text: str, role: Role = "user") -> EasyInputMessageParam:
    return {
        "content": [{"text": text, "type": "input_text"}],
        "role": role,
        "type": "message",
    }


class Console(Protocol):
    def write(self, text: str) -> None: ...


class SmartChat:

    def run(self) -> str:
        import sys

        screen = pix.get_display()
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

        res = "OK"
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

    def __init__(self, canvas: pix.Canvas, font: pix.Font, ide: PixIDE):
        self.canvas = canvas
        self.font_size: int = 20
        self.font = font
        self.editor = ide.edit
        self.ide = ide
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.ts: pix.TileSet = pix.TileSet(self.font, size=self.font_size)
        con_size = canvas.size.toi() / self.ts.tile_size
        self.con: pix.Console = pix.Console(con_size.x, con_size.y - 1, self.ts)
        self.con.set_device_no(1)
        pix.add_event_listener(self.handle_events, 0)

        key = (Path.home() / ".openai.key").read_text().rstrip()
        self.client = OpenAI(api_key=key)

        self.responses: list[Future[Response]] = []

        self.messages: list[ResponseInputItemParam] = []
        self.code: str | None = None
        self.tools: list[FunctionToolParam] = []
        self.functions: dict[str, Callable[..., object]] = {}

        self.add_function(self.read_users_program)
        self.add_function(self.run_users_program)

    def add_function(
        self,
        fn: Callable[..., object],
        desc: str | None = None,
        arg_desc: dict[str, str] | None = None,
    ):
        fd = create_function(fn, desc, arg_desc)
        self.tools.append(fd)
        self.functions[fd["name"]] = fn

    def handle_function_call(self, fcall: ResponseFunctionToolCall):
        if fcall.name in self.functions:
            msg: ResponseFunctionToolCallParam = {
                "name": fcall.name,
                "arguments": fcall.arguments,
                "call_id": fcall.call_id,
                "type": "function_call",
            }
            self.messages.append(msg)
            fn = self.functions[fcall.name]
            args = json.loads(fcall.arguments)
            print(args)
            ret = fn(**args)
            fr: FunctionCallOutput = {
                "call_id": fcall.call_id,
                "output": str(ret),
                "type": "function_call_output",
            }
            self.add_message(fr)

            # TODO call fn() with the correct arguments

    def set_code(self, code: str):
        self.code = code

    def get_ai_response(self, messages: list[ResponseInputItemParam]) -> Response:
        response = self.client.responses.create(
            model="gpt-4o-mini",
            instructions="""
You are an AI programming teacher. You try to help the user with their programming problems, but you want them to learn so you avoid directly solving their problems, instead give pointers so they can move forward.

The user is currently editing a python program in their text editor, and may ask questions about this program.

When the user asks questions about the program, you *should* read it so you can
answer the question.

If a user problem is not obvious, you *should* run the program and parse the error messages.

Give *short* answers, normally a single sentence will do.
""",
            input=messages,
            tools=self.tools,
        )
        return response

    def add_line(self, line: str) -> None:
        self.add_message(message(line))

    def add_message(self, message: ResponseInputItemParam):

        # Update program
        read_id = ""
        for msg in self.messages:
            if "type" in msg:
                print(msg)
                if msg["type"] == "function_call":
                    if msg["name"] == "read_users_program":
                        read_id = msg["call_id"]
                if msg["type"] == "function_call_output":
                    if msg["call_id"] == read_id:
                        msg["output"] = self.editor.get_text()

        self.messages.append(message)
        self.code = self.editor.get_text()
        messages = self.messages.copy()
        future = self.executor.submit(self.get_ai_response, messages)
        self.responses.append(future)

    def handle_response(self, response: Response):
        print(response.output)
        for output in response.output:
            if output.type == "function_call":
                self.handle_function_call(output)
                return

        self.messages.append(
            EasyInputMessageParam(role="assistant", content=response.output_text)
        )
        self.con.write(response.output_text)
        self.con.write("\n> ")
        self.read_line()

    def handle_events(self, event: object) -> bool:
        if isinstance(event, pix.event.Text):
            if event.device == 1:
                print(event.text)
                self.con.write("\n")
                self.add_line(event.text)
                return False
        return True

    def write(self, text: str):
        self.con.write(text)

    def render(self):

        if len(self.responses) > 0:
            r = self.responses[0]
            if r.done():
                print("GOT RESULT")
                self.responses.pop(0)
                self.handle_response(r.result())

        self.canvas.draw(self.con, top_left=(0, 0), size=self.con.size)

    def read_line(self):
        self.con.read_line()
