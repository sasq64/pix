import os.path
import traceback
import pixpy as pix
from pixpy.editor import TextEdit

def info_box(text):

    lines = text.split("\n")
    maxl = len(max(lines, key=lambda l: len(l)))

    sz = pix.Int2(maxl, len(lines))
    con = pix.Console(cols = sz.x, rows = sz.y + 1)
    con.write(text)
    psz = (sz  * (8,16) + (8,8)).tof()
    xy = screen.size - psz
    screen.context.draw_color = 0x000040ff
    screen.filled_rect(top_left=xy, size=psz)
    screen.draw(con, top_left = xy + (4,4))


def run(source):
    screen.clear(0x2020a0ff)
    screen.swap()
    try:
        exec(source)
        info_box("[PRESS ANY KEY]")
    except SyntaxError as se:
        screen.swap()
        info_box(f"Syntax error in line {se.lineno}")
    except Exception as e:
        screen.swap()
        info_box(str(e))

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
    edit = TextEdit(font = None, rows = 25, cols = 80)
    edit.set_color(0xffffffff, 0x4040e0ff)
    if os.path.isfile('.pixwork.py'):
        with open('.pixwork.py') as f:
            if f.readable :
                text = f.read()
                edit.set_text(text)
    while pix.run_loop():
        events = pix.all_events()
        for e in events:
            if isinstance(e, pix.event.Key):
                if e.key == pix.key.F5:
                    text = edit.get_text()
                    with open('.pixwork.py', 'w') as f:
                        f.write(text)
                    run(edit.get_text())
        edit.update(events)
        edit.render(screen.context)
        screen.swap()

main()

