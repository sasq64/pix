from dataclasses import dataclass

import pixpy as pix

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2


@dataclass
class Format:
    font: pix.Font | None = None
    size: int = 16
    color: int = pix.color.BLACK
    align: int = 0


@dataclass
class DrawCommand:
    image: pix.Image
    pos: pix.Float2


formats: list[Format] = [Format()] * 10


def wrap_text(text: str, font: pix.Font, size: int, width: float) -> list[str]:
    lines: list[str] = []

    text = text.strip()
    start = 0
    length = len(text)

    print(f"len {length}")
    while start < length:
        # Binary search for max character count fitting in width
        low = 1
        high = length - start
        best = 1

        if font.text_size(text[start:], size).x <= width:
            lines.append(text[start:])
            break

        while low <= high:
            mid = (low + high) // 2
            candidate = text[start : start + mid]
            if font.text_size(candidate, size).x <= width:
                best = mid
                low = mid + 1
            else:
                high = mid - 1

        print(f"break '{text}' at {high} = {text[start:start+high]}")

        # Try to break at a space for better word boundaries
        line_end = start + best
        space_pos = text.rfind(" ", start, line_end)
        if space_pos != -1 and space_pos > start:
            line_end = space_pos

        line = text[start:line_end].rstrip()
        lines.append(line)

        # Move start index past the line (and skip leading spaces)
        start = line_end
        while start < length and text[start] == " ":
            start += 1

    print(f"{lines}")
    return lines


def parse_md(md: str, width: float) -> list[DrawCommand]:
    y = 0
    ym = 2
    result: list[DrawCommand] = []
    for line in md.splitlines():
        line = line.strip()
        text = line.lstrip("#")
        h = len(line) - len(text)
        fmt = formats[h]
        font = fmt.font or pix.Font.UNSCII_FONT
        lines = wrap_text(text, font, fmt.size, width)
        for line in lines:
            img = font.make_image(line, size=fmt.size, color=fmt.color)
            x = 0
            if fmt.align == ALIGN_CENTER:
                x = (width - img.size.x) / 2
            result.append(DrawCommand(img, pix.Float2(x, y)))
            y += img.size.y + ym
    return result


screen = pix.open_display(size=(640, 720))

pos = screen.size / 2

page = """
## PIXPY
### Make Programming Joyful Again

A graphics library for C++, with a stable python interface, and WIP interfaces for Rust and Ruby.

Designed for learning and 2D game development.

"""

font = pix.load_font("data/lazenby.ttf")
hack = pix.load_font("data/Hack.ttf")

formats[0] = Format(font=hack, size=24, color=pix.color.BLACK, align=ALIGN_CENTER)
formats[2] = Format(font=font, size=80, color=pix.color.RED, align=ALIGN_CENTER)
formats[3] = Format(font=hack, size=30, color=pix.color.LIGHT_RED, align=ALIGN_CENTER)

commands = parse_md(page, screen.size.x)

# screen.draw_color = pix.color.RED
screen.line_width = 4.0

wipe = False
while pix.run_loop():
    screen.clear(pix.color.WHITE)
    m = 14
    for cmd in commands:
        screen.draw(cmd.image, top_left=cmd.pos)
        if wipe:
            cmd.pos += (m, 0)
            m = -m
    if pix.was_pressed(pix.key.ENTER):
        wipe = True
    screen.swap()
