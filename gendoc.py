import inspect
import os
import sys
import re
from curses.ascii import isdigit
from typing import get_type_hints

import pixpy


def generate_module(module: type, mod_name: str):

    props: dict[str, tuple[str, str]] = {}
    methods: dict[str, list[tuple[str, str]]] = {}
    constructors: dict[str, list[tuple[str, str]]] = {}
    constants: dict[str, int] = {}

    for name, obj in inspect.getmembers(module):
        if name.startswith("__") and name != "__init__":
            continue
        if inspect.isclass(obj):
            pass
        elif isinstance(obj, property):
            doc_comment = inspect.getdoc(obj)
            fget = obj.fget
            t = ""
            if fget is not None:
                # print(f"{fget.__doc__}\n", file=sys.stderr)
                p = fget.__doc__.split(" -> ")
                if len(p) > 1:
                    t = p[1].rstrip("\n").replace("pixpy._pixpy.", "")
                    print(f"{name}: {t}\n", file=sys.stderr)
            doc_comment = doc_comment or ""
            props[name] = (doc_comment.strip(), t)
            # print(f"### {name}\n{doc_comment.strip()}")
        elif callable(obj):
            doc_comment = inspect.getdoc(obj)
            if doc_comment:
                lines = doc_comment.split("\n")
                prototype = lines[0]
                lines = lines[1:]
                function: list[tuple[str, str]] = []
                if lines:
                    if lines[0].startswith("Overloaded"):
                        lines = lines[2:]
                        doc = ""
                        while lines:
                            pt = lines[0]
                            if isdigit(pt[0]):
                                pt = pt[3:]
                            else:
                                raise NameError
                            lines = lines[1:]
                            while lines and lines[0] == "":
                                lines = lines[1:]
                            doc = ""
                            while lines and not (
                                len(lines[0]) > 1
                                and lines[0][0].isdigit()
                                and lines[0][1] == "."
                            ):
                                doc += lines[0] + "\n"
                                lines = lines[1:]
                            # if function:
                            #    print(f"'{doc}' vs '{function[-1][1]}'")
                            doc = doc.strip()
                            if function and doc == function[-1][1]:
                                function[-1] = (function[-1][0], "")
                            function.append((pt, doc))
                    else:
                        while lines and lines[0] == "":
                            lines = lines[1:]
                        doc = "\n".join(lines)
                        function = [(prototype, doc)]
                    if name == "__init__":
                        constructors[name] = function
                    else:
                        methods[name] = function
                    # for pt, doc in function:
                    #     pt = pt.replace("__init__", mod_name)
                    #     pt = pt.replace("pixpy._pixpy.", "")
                    #     print(f"```python\n{pt}\n```")
                    #     if doc:
                    #         print(doc)
                    # print("")
        elif isinstance(obj, int):
            constants[name] = obj
            # print(f"{name} = 0x{obj:x}")
        else:
            pass
            # print(f"{name} {obj} {type(obj)}")
    if len(props) > 0:
        print("\n### Properties\n")
        for prop, d in props.items():
            doc, typ = d
            print(f"\n#### {mod_name}.{prop}\n`{typ}`\n\n{doc}")
    if len(constructors) > 0:
        print("\n### Constructors\n")
        ire = r"__init__\(self[^,]*,\s+(.*)\) ->"
        for _, item in constructors.items():
            for fn, doc in item:
                fn = fn.replace("pixpy._pixpy.", "")
                m = re.match(ire, fn)
                if m is not None:
                    print(f"```python\n{mod_name}({m.group(1)})\n```\n{doc}\n")
    if len(methods) > 0:
        print("\n### Methods\n")
        for m, item in methods.items():
            for fn, doc in item:
                fn = (
                    fn.replace("pixpy._pixpy.", "")
                    .replace("4294967295", "color.WHITE")
                    .replace("color: int = 255", "color: int = color.BLACK")
                )
                match = re.search(r"Union\[\s*([^\[\]]+?)\s*\]", fn)
                if match:
                    inner = match.group(1)
                    parts = [part.strip() for part in inner.split(",")]
                    p = " | ".join(parts)
                    fn = fn[: match.start(0)] + p + fn[match.end(0) :]

                fn = re.sub(r"self: \w+,\s*", "", fn)
                fn = re.sub(r"0\.0+", "0.0", fn)
                fn = re.sub(r"Float2\(0\.0+,\s*0.0+\)", "Float2.ZERO", fn)
                print(f"#### {mod_name}.{m}\n```python\n{fn}\n```\n{doc}\n")
    if len(constants) > 0:
        print("\n### Constants\n```python\n")
        for name, val in constants.items():
            print(f"{mod_name}.{name} = 0x{val:08x}")
        print("```\n")


output_file = "doc.txt"
module = pixpy

with open(output_file, "w") as f:

    print("# PIXPY\n")
    print("## pixpy (module)")
    generate_module(module, "pixpy")
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            doc = inspect.getdoc(obj)
            if not doc:
                doc = ""
            print(f"\n## {name}\n\n{doc}\n")
            generate_module(obj, name)

    print("## pixpy.event (module)")
    generate_module(pixpy.event, "event")
    for name, obj in inspect.getmembers(pixpy.event):
        if inspect.isclass(obj):
            doc = inspect.getdoc(obj)
            if not doc:
                continue
            print(f"\n## {name}\n\n{doc}\n")
            generate_module(obj, name)
    print("## pixpy.color (module)")
    generate_module(pixpy.color, "color")
    print("## pixpy.key (module)")
    generate_module(pixpy.key, "key")
