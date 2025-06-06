import os.path
import traceback
import argparse
import pixpy as pix
from pixpy.editor import TextEdit


def run(source: str):
    screen.clear(0x2020A0FF)
    screen.swap()
    try:
        exec(source)
    except SyntaxError as se:
        screen.swap()
    except Exception as e:
        screen.swap()

    screen.swap()
    leave = False
    while pix.run_loop() and not leave:
        events = pix.all_events()
        for e in events:
            if isinstance(e, pix.event.Key):
                leave = True


def main():
    global screen
    screen = pix.open_display(width=80 * 8 * 2, height=25 * 16 * 2)
    edit = TextEdit(font=None, rows=25, cols=80)
    edit.set_color(0xFFFFFFFF, 0x4040E0FF)
    if os.path.isfile(".pixwork.py"):
        with open(".pixwork.py") as f:
            if f.readable:
                text = f.read()
                edit.set_text(text)
    while pix.run_loop():
        events = pix.all_events()
        for e in events:
            if isinstance(e, pix.event.Key):
                if e.key == pix.key.F5:
                    text = edit.get_text()
                    with open(".pixwork.py", "w") as f:
                        f.write(text)
                    run(edit.get_text())
        edit.update(events)
        edit.render(screen.context)
        screen.swap()


main()
