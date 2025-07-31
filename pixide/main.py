import argparse
from pathlib import Path

import pixpy as pix
from .ide import PixIDE
from .smart_chat import SmartChat


class IdeArgs:
    fullscreen: bool = False
    font_size: int = 24


fwd = Path(__file__).parent
hack_font = fwd / "data" / "HackNerdFont-Regular.ttf"


def main():
    parser = argparse.ArgumentParser(
        description="PixIDE - Python IDE for PIX graphics library"
    )
    parser.add_argument(
        "-f",
        "--fullscreen",
        action="store_true",
        help="Open display in fullscreen mode",
    )
    parser.add_argument(
        "-S",
        "--font-size",
        type=int,
        help="Set the font size",
    )

    args = parser.parse_args(namespace=IdeArgs())
    size = pix.Int2(1280, 720)
    if args.fullscreen:
        size = pix.Int2(-1, -1)

    screen = pix.open_display(size=size, full_screen=args.fullscreen)
    split = screen.split((2, 1))
    ide = PixIDE(split[0], font_size=args.font_size)
    chat = SmartChat(
        split[1].crop((10, 10), split[1].size - (20, 20)),
        pix.load_font(hack_font),
        ide,
    )

    chat.con.set_device_no(1)
    current_dev = 0

    def click_handler(event: pix.event.AnyEvent) -> bool:
        if isinstance(event, pix.event.Click):
            new_dev = -1
            nonlocal current_dev
            if event.pos.inside(split[0].offset, split[0].offset + split[0].size):
                new_dev = 0
            elif event.pos.inside(split[1].offset, split[1].offset + split[1].size):
                new_dev = 1
            pix.set_keyboard_device(new_dev)

            print(f"{new_dev} {current_dev}")
            if new_dev != current_dev:
                current_dev = new_dev
                ide.con.cursor_on = current_dev == 0
                chat.con.cursor_on = current_dev == 1
                return False
            return current_dev == 0
        return True

    pix.add_event_listener(click_handler, 0)

    chat.write("Hello and welcome!\n> ")
    chat.read_line()

    print("RUN")
    while pix.run_loop():
        ide.render()
        chat.render()
        screen.swap()


if __name__ == "__main__":
    main()
