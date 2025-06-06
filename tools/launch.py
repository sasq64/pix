import ast
import builtins
import subprocess
import sys
import time
from pathlib import Path
from typing import override, Any

import pixpy
import pixpy as pix
from watchdog.events import DirModifiedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


def strip_ast_metadata(node: ast.AST | list[ast.AST]):
    """Recursively remove lineno, col_offset, and other non-semantic fields."""
    if isinstance(node, ast.AST):
        fields = {}
        for name, value in ast.iter_fields(node):
            if name not in (
                "lineno",
                "col_offset",
                "end_lineno",
                "end_col_offset",
                "ctx",
            ):
                fields[name] = strip_ast_metadata(value)
        return type(node)(**fields)
    elif isinstance(node, list):
        return [strip_ast_metadata(elem) for elem in node]
    else:
        return node

def is_global(node: ast.stmt) -> None | tuple[str, Any]:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = str(target.id)
                print(name)
                if name.isupper():
                    try:
                        value: Any = ast.literal_eval(node.value)
                    except Exception:
                        print("Could not eval")
                        value = None
                    if value is not None:
                        return (target.id, value)
    return None


def strip_ast(mod: ast.Module) -> ast.Module:
    mod.body = [s for s in mod.body if not is_global(s)]
    return strip_ast_metadata(mod)


                            

def ast_equal(a0: ast.Module, a1: ast.Module) -> bool:
    tree1 : ast.Module = strip_ast(a0)
    tree2 : ast.Module = strip_ast(a1)
    Path("tree1").write_text(ast.dump(tree1))
    Path("tree2").write_text(ast.dump(tree2))
    return ast.dump(tree1) == ast.dump(tree2)

class PySource(FileSystemEventHandler):
    @override
    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent):
        print(f"Got event {event.src_path}")
        # Only react to changes in the specific script file
        if Path(str(event.src_path)) == self.script_file and event.event_type == "modified":
            t = time.time()
            if t - self.last_modified_time > 1:  # Avoid rapid fire on multiple events
                print(f"{self.script_file.name} was changed")
                self.last_modified_time = t
                new_ast = ast.parse(self.script_file.read_text())
                self.set_globals(new_ast)
                same = ast_equal(self.ast, new_ast)
                self.reloaded = True
                if same:
                    print("Only whitespace, no restart")
                else:
                    print("Restarting")
                    self.ast = new_ast
                    self.do_restart = True
                    pixpy.quit_loop()

    def check_ast(self) -> bool:
        new_ast = ast.parse(self.script_file.read_text())
        return ast_equal(self.ast, new_ast)

    def set_globals(self, tree: ast.Module):
        changed = False
        for node in tree.body:
            kv = is_global(node)
            if kv is not None:
                changed = True
                self.globals[kv[0]] = kv[1]
        if changed:
            self.change_count += 1
            print(f"Globals changed, count = {self.change_count}")
            self.globals["LAUNCH_CHANGE_COUNT"] = self.change_count 

    def __init__(self, script_file: Path):
        self.change_count = 0
        self.script_file = script_file
        self.globals : dict[str, Any] = {}
        self.ast : ast.Module = ast.parse(self.script_file.read_text())
        self.do_restart = False
        self.reloaded = False
        self.last_modified_time: float = 0
        self.observer = Observer()
        self.watch = self.observer.schedule(
            self, script_file.parent.as_posix(), recursive=False
        )
        self.observer.start()
    
    def run(self):
        while True:
            source = self.script_file.read_text()
            self.globals["__builtins__"] = builtins
            self.globals["__name__"] = "__main__"
            try:
                self.reloaded = False
                self.do_restart = False
                exec(source, self.globals)
            except Exception as e:
                print(e)
                while not self.reloaded:
                    time.sleep(0.5)
            if not self.do_restart:
                break


def main(script: str):
    script_file = Path(script).absolute()
    pys = PySource(script_file)
    pys.run()


if __name__ == "__main__":
    main(sys.argv[1])
