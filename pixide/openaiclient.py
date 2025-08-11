from concurrent.futures import Future, ThreadPoolExecutor
import json
import inspect
from pathlib import Path
from typing import Callable, Literal, TypeGuard
from urllib import request
from openai.types.responses import (
    FunctionToolParam,
    Response,
    ResponseFunctionToolCall,
    ResponseFunctionToolCallParam,
    ResponseInputItemParam,
    ResponseOutputText,
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


Role = Literal["user", "assistant", "system", "developer"]


def message(text: str, role: Role = "user") -> EasyInputMessageParam:
    return {
        "content": [{"text": text, "type": "input_text"}],
        "role": role,
        "type": "message",
    }

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


class OpenAIClient:

    ## Public API

    def __init__(self, api_key: str = ""):
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Initialize OpenAI client
        if api_key == "":
            key_file = Path.home() / ".openai.key"
            if not key_file.exists():
                raise FileNotFoundError("Can not find .openai.key in $HOME!")
            api_key = key_file.read_text().rstrip()
        self.client: OpenAI = OpenAI(api_key=api_key)
        self.instructions: str = "You are a friendly chatbot."

        # Response queue and message handling
        self.request: Future[Response] | None = None
        self.messages: list[ResponseInputItemParam] = []
        self.tools: list[FunctionToolParam] = []
        self.functions: dict[str, Callable[..., object]] = {}

    def add_function(
        self,
        fn: Callable[..., object],
        desc: str | None = None,
        arg_desc: dict[str, str] | None = None,
    ):
        """Add a function to the OpenAI tool set"""
        fd = create_function(fn, desc, arg_desc)
        self.tools.append(fd)
        self.functions[fd["name"]] = fn

    def clear(self):
        """Clear all messages in conversation"""
        self.messages.clear()

    def add_line(self, text_line: str):
        """Add a user: message to the conversation and send it to GPT"""
        self.messages.append(message(text_line))
        self._send_request()

    def update(self) -> ResponseOutputText | None:
        """Poll GPT progress. If a new assistant message has arrived, return it."""
        if self.request is not None and self.request.done():
            print("DONE")
            request = self.request
            self.request = None
            result = self._handle_response(request.result())
            return result
        return None

    ## Private methods

    def _update_function_output(self, function_name: str, new_output: str):
        """Update the output of a specific function call in the message history"""
        read_id = ""
        for msg in self.messages:
            if "type" in msg:
                if is_function_call(msg):
                    if msg["name"] == function_name:
                        read_id = msg["call_id"]
                if is_function_call_output(msg):
                    if msg["call_id"] == read_id:
                        msg["output"] = new_output

    def _handle_function_call(
        self, fcall: ResponseFunctionToolCall
    ) -> FunctionCallOutput | None:
        """Handle a function call from OpenAI and return the result"""
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
            self.messages.append(fr)
            return fr
        return None

    def _send_request(self):
        """Send a request to OpenAI and return a Future for the response"""
        assert(self.request is None)

        messages = self.messages.copy()

        def _get_ai_response(messages: list[ResponseInputItemParam]) -> Response:
            response = self.client.responses.create(
                model="gpt-5-mini",
                instructions=self.instructions,
                input=messages,
                tools=self.tools,
            )
            return response

        print("SUBMIT")
        self.request = self.executor.submit(_get_ai_response, messages)

    def _handle_response(self, response: Response) -> ResponseOutputText | None:
        """Process a response and return any function call outputs"""
        print(response.output)
        result: ResponseOutputText | None = None
        function_outputs: list[FunctionCallOutput] = []
        do_send = False
        for output in response.output:
            print(f"Checking {output.type}")
            if output.type == "function_call":
                print("Found function")
                fres = self._handle_function_call(output)
                if fres:
                    function_outputs.append(fres)
                do_send = True
            elif output.type == "message":
                print("Found message")
                for content in output.content:
                    if content.type == "output_text":
                        print("Appending")
                        result = content
                        self.messages.append(
                            EasyInputMessageParam(
                                role="assistant", content=content.text
                            )
                        )
            else:
                print(f"**WARNING: Unhandled response type '{output.type}'")
        if do_send:
            print("Sending new request")
            self._send_request()
        return result
