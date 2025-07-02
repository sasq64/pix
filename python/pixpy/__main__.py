import os.path
import traceback
import pixpy as pix
from .pixide import PixIDE


def main():
    global screen
    screen = pix.open_display(width=640, height=720, full_screen=False)
    ide = PixIDE(screen)

    print("RUN")
    while pix.run_loop():
        ide.render()
        screen.swap()


if __name__ == "__main__":
    main()
