import os
import re
import sys


class WorkFile:

    def __init__(self, file_name: str):
        if not os.path.exists(file_name):
            return
        self.file_name = file_name
        self.file = open(file_name, "r")
        self.lines = self.file.readlines()

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        print(typ, value, tb)
        self.save()

    def save(self):
        self.file.close()
        nl = [line.rstrip() + "\n" for line in self.lines]
        with open(self.file_name, "w") as f:
            f.writelines(nl)

    def replace_all(self, pattern: str, text: str):
        for i, line in enumerate(self.lines):
            new_line = re.sub(pattern, text, line)
            if new_line != line:
                self.lines[i] = new_line

    def add_after(self, pattern, line: str | list[str]):
        if isinstance(line, list):
            self.add_all_after(pattern, line)
        i = self.find(pattern)
        if i is not None:
            self.insert_line(i + 1, line)

    def add_all_after(self, pattern, lines: list[str]):
        i = self.find(pattern)
        if i is not None:
            self.lines = self.lines[: i + 1] + lines + self.lines[i + 1 :]

    def remove_lines_containing(self, pattern):
        for i in reversed(range(len(self.lines))):
            if pattern in self.lines[i]:
                del self.lines[i]

    def remove_line(self, i):
        del self.lines[i]

    def add_line(self, i, line):
        if i == len(self.lines):
            self.lines.append(line)
        else:
            self.lines.insert(i, line)

    def swap_line(self, a, b):
        line = self.lines[a]
        self.lines[a] = self.lines[b]
        self.lines[b] = line

    def __len__(self):
        return len(self.lines)

    def dump(self):
        for line in self.lines:
            print(line.rstrip())

    def find(self, pattern, start=0) -> int | None:
        for i, line in enumerate(self.lines):
            if i >= start and re.match(pattern, line):
                return i
        return None

    def insert_line(self, i, text):
        self.lines.insert(i, text)


def main(_):
    with WorkFile("python/pixpy/__init__.pyi") as wf:
        if not wf.find("from typing"):
            wf.add_after("from __future__", "from typing import Union, Tuple, List")
            # if not wf.find('color as color'):
            #     wf.add_all_after('import os', [
            #         'import pixpy.color as color',
            #         'import pixpy.event as event',
            #         'import pixpy.key as key',
            #     ])
        wf.replace_all(r"class Screen:", "class Screen(Context):")
        wf.replace_all(r"class Image:", "class Image(Context):")
        wf.replace_all(r": Float2", ": Union[Float2, Int2, Tuple[float, float]]")
        wf.replace_all(r": Int2", ": Union[Int2, Tuple[int, int]]")
        wf.replace_all(r": os.PathLike", ": str")
        wf.replace_all(
            r"Optional\[Float2\]", "Optional[Union[Float2, Int2, Tuple[float, float]]]"
        )
        wf.replace_all(r"pixpy\._pixpy\.", "")

        ops = ["add", "sub", "mul", "truediv", "floordiv", "eq", "ne"]

        start = wf.find("class Int2")
        if start is not None:
            for op in ops:
                print(op)
                a = wf.find(f".*__{op}__.*Float2", start)
                b = wf.find(f".*__{op}__.*Int2", start)
                print(a, b)
                if a is not None and b is not None and b == a + 2:
                    wf.swap_line(a, b)

    with WorkFile("python/pixpy/event.pyi") as wf:
        line_no = wf.find("class AnyEvent")
        if line_no is not None:
            wf.remove_line(line_no)
            wf.remove_line(line_no)
        if not wf.find("import pixpy$"):
            wf.add_after("import typing", "import pixpy")
        wf.replace_all(r"_pixpy\.", "")
        if not wf.find("AnyEvent ="):
            wf.add_line(
                len(wf),
                "AnyEvent = typing.Union"
                + "[NoEvent, Key, Move, Click, Text, Resize, Quit]",
            )


if __name__ == "__main__":
    main(sys.argv)
