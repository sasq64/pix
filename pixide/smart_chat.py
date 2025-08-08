from concurrent.futures import Future, ThreadPoolExecutor
import json
import os
import inspect
from pathlib import Path
import subprocess
from textwrap import wrap
from typing import Literal, Protocol, Callable, TypeGuard

import pixpy as pix

from pixide.markdown import MarkdownRenderer, render_markdown

from .ide import PixIDE

from openai.types.responses import (
    FunctionToolParam,
    Response,
    ResponseFunctionToolCall,
    ResponseFunctionToolCallParam,
    ResponseInputItemParam,
)
from openai.types.responses.easy_input_message_param import (
    EasyInputMessageParam,
)
from openai.types.responses.response_input_item_param import FunctionCallOutput
from openai import OpenAI


def is_function_call(
    msg: ResponseInputItemParam,
) -> TypeGuard[ResponseFunctionToolCallParam]:
    return msg.get("type") == "function_call"


def is_function_call_output(
    msg: ResponseInputItemParam,
) -> TypeGuard[FunctionCallOutput]:
    return msg.get("type") == "function_call_output"



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

def get_pixpy_information():
    """Get an overview of the functions and usage that makes up the pixpy library."""

    return """
PIXPY is a cross-platform 2D graphics library with a C++ core and Python bindings, designed for learning and game development with efficient console/tileset rendering using OpenGL.

## Core Workflow
```python
import pixpy

# Initialize display (required first)
screen = pixpy.open_display(800, 600)  # or pixpy.open_display(pixpy.Int2(800, 600))

# Main loop pattern
while pixpy.run_loop():
    screen.clear(pixpy.color.BLACK)
    
    # Your drawing code here
    
    screen.swap()  # Present frame
```

## Essential Classes & Types

### Coordinate Types
- `Float2(x, y)` - floating point coordinates/sizes
- `Int2(x, y)` - integer coordinates/sizes  
- Both have `.x`, `.y` properties and arithmetic operations

### Canvas (Screen & Image base class)
Drawing operations available on both Screen and Image:
- `clear(color)` - fill with color
- `filled_rect(top_left: Float2, size: Float2)` 
- `rect(top_left: Float2, size: Float2)` - outline
- `filled_circle(center: Float2, radius: float)`
- `circle(center: Float2, radius: float)` - outline
- `line(start: Float2, end: Float2)`
- `polygon(points: list[Float2], convex=False)`
- `draw(image: Image, top_left=None, center=None, size=Float2.ZERO, rot=0)`
- `draw(console: Console, top_left=Float2.ZERO, size=Float2.ZERO)`

Properties: `draw_color`, `blend_mode`, `size`

### Screen
Main display window - extends Canvas
- `swap()` - present frame (call at end of loop)
- `delta` - time for last frame
- `fps` - current FPS (set to 0 to disable fixed rate)
- `seconds` - total elapsed time

### Image  
Texture-based image system - extends Canvas
- `Image(width, height)` or `Image(size: Float2)` - create empty
- `copy_from(image)` / `copy_to(image)` - copy operations
- `crop(top_left, size)` - create view into image
- `split(cols, rows, width, height)` - split into grid
- `save_png()` via `pixpy.save_png(image, filename)`

### Console
Tile-based text/graphics system for terminal-style rendering
- `Console(cols, rows, font_file=None, tile_size=Int2(-1,-1), font_size=-1)`
- `Console(cols, rows, tile_set: TileSet)`
- `write(text: str)` - write at cursor position
- `put(pos: Int2, tile: int, fg=None, bg=None)` - place tile
- `clear()` - clear console
- Properties: `cursor_pos`, `fg_color`, `bg_color`, `grid_size`, `tile_size`

## Input Handling

### Event System
```python
events = pixpy.all_events()  # Get and clear all events
for event in events:
    if isinstance(event, pixpy.event.Key):
        print(f"Key {event.key} pressed")
    elif isinstance(event, pixpy.event.Click):
        print(f"Click at {event.pos}")
    elif isinstance(event, pixpy.event.Text):
        print(f"Text input: {event.text}")
```

Event types: `Key`, `Click`, `Move`, `Text`, `Resize`, `Quit`

### Direct Input
- `pixpy.is_pressed(key)` - check if key currently held
- `pixpy.was_pressed(key)` - check if key was pressed this frame
- `pixpy.was_released(key)` - check if key was released this frame
- `pixpy.get_pointer()` - mouse position

## Constants & Utilities

### Colors (pixpy.color module)
`BLACK`, `WHITE`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `CYAN`, `PURPLE`, `ORANGE`, `GREY`, `LIGHT_GREY`, `DARK_GREY`

### Keys (pixpy.key module)  
`UP`, `DOWN`, `LEFT`, `RIGHT`, `SPACE`, `ENTER`, `ESCAPE`, `TAB`, `BACKSPACE`, `DELETE`
`F1`-`F12`, `LEFT_MOUSE`, `RIGHT_MOUSE`, `MIDDLE_MOUSE`
`LSHIFT`, `RSHIFT`, `LCTRL`, `RCTRL`

### Blend Modes
`BLEND_NORMAL`, `BLEND_ADD`, `BLEND_MULTIPLY`, `BLEND_COPY`

### Color Functions
- `pixpy.rgba(r, g, b, a)` - create color from components (0.0-1.0)
- `pixpy.blend_color(color0, color1, t)` - blend two colors

## File Operations
- `pixpy.load_png(filename)` - load PNG as Image
- `pixpy.save_png(image, filename)` - save Image as PNG
- `pixpy.load_font(filename, size)` - load TTF font

## Common Patterns

### Basic Drawing
```python
screen.draw_color = pixpy.color.RED
screen.filled_rect(Float2(10, 10), Float2(100, 50))
```

### Image Operations
```python
img = pixpy.load_png("sprite.png")
screen.draw(img, center=Float2(400, 300), rot=0.5)
```

### Console Usage
```python
console = pixpy.Console(80, 25)
console.write("Hello World!")
screen.draw(console, size=screen.size)  # fullscreen console
```
"""

class Console(Protocol):
    def write(self, text: str) -> None: ...


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
        self.reading_line : bool = True
        self.resize()
        self.console.cursor_on = False
        pix.add_event_listener(self.handle_events, 0)

        key_file = Path.home() / ".openai.key"
        if not key_file.exists():
            raise FileNotFoundError("Can not find .openai.key in $HOME!")
        key = (Path.home() / ".openai.key").read_text().rstrip()
        self.client = OpenAI(api_key=key)

        self.responses: list[Future[Response]] = []

        self.messages: list[ResponseInputItemParam] = []
        self.code: str | None = None
        self.tools: list[FunctionToolParam] = []
        self.functions: dict[str, Callable[..., object]] = {}


        self.add_function(self.read_users_program)
        self.add_function(self.run_users_program)
        self.add_function(get_pixpy_information)

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
        new_env["PYTHONPATH"] = (
            file_dir + os.pathsep + new_env.get("PYTHONPATH", "")
        )

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

    def set_code(self, code: str):
        self.code = code

    def get_ai_response(
        self, messages: list[ResponseInputItemParam]
    ) -> Response:
        response = self.client.responses.create(
            model="gpt-5-mini",
            instructions="""
You are an AI programming teacher. You try to help the user with their programming problems, but you want them to learn so you avoid directly solving their problems, instead give pointers so they can move forward.

The user is currently editing a python program in their text editor, and may ask questions about this program.

When the user asks questions about the program, you *should* read it so you can
answer the question.

If a user problem is not obvious, you *should* run the program and parse the error messages.

Give *short* answers, normally a single sentence will do.

Use markdown to emphasize key points.

*Always* read the program if a user comment or question seems to refer to anything related to the program.

## Examples of questions where you *must* read the program

User: What does this do?

User: Explain this

## PIXPY

pixpy is a library for python that the user works with to display graphics.
If the user asks about anything related to _graphics_ or _pix_ or _pixpy_, you *must* get information about pixy to be able to help the user.


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
                if is_function_call(msg):
                    if msg["name"] == "read_users_program":
                        read_id = msg["call_id"]
                if is_function_call_output(msg):
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
            EasyInputMessageParam(
                role="assistant", content=response.output_text
            )
        )
        self.write("\n")
        self.markdown_renderer.render(response.output_text)
        #self.write(response.output_text)
        self.write("\n")
        self.read_line()

    def handle_events(self, event: object) -> bool:
        if isinstance(event, pix.event.Text):
            if event.device == 1:
                print(event.text)
                xy = self.console.cursor_pos
                self.console.clear_area(xy.x, xy.y, self.console.grid_size.x - 2, 1)
                self.write(event.text, pix.color.LIGHT_BLUE)
                self.console.write("\n")
                self.add_line(event.text)
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

        if len(self.responses) > 0:
            r = self.responses[0]
            if r.done():
                print("GOT RESULT")
                self.responses.pop(0)
                self.handle_response(r.result())

        self.canvas.draw(self.console, top_left=(0, 0), size=self.console.size)

    def read_line(self):
        self.console.set_color(pix.color.YELLOW, pix.color.BLACK)
        self.console.write("\n> ")
        self.console.set_color(pix.color.LIGHT_BLUE, pix.color.BLACK)
        self.console.read_line()
