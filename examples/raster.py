import pixpy as pix
import math


def raster(colors: list[int], y: int, h: int, col0: int, col1: int):
    """
    Draw a "raster bar" into the provided `colors` list.
    - `y`: Position of bar
    - `h`: Height of bar
    - `col0`: Start (edge) color
    - `col1`: Center color 
    """
    for i in range(h):
        col = pix.blend_color(col0, col1, (math.cos(math.pi * 2 * i / h) + 1) / 2)
        if i + y > 0 and i + y < len(colors):
            colors[i + y] = pix.add_color(colors[i + y], col)

screen = pix.open_display(size=(1280,720))
raster_colors = [pix.color.RED, pix.color.BLUE, pix.color.GREEN, pix.color.YELLOW]

while pix.run_loop():
    screen.clear()

    # Array of colors, one for each horizontal line in the result
    colors = [0] * 256
    s = screen.frame_counter / 100
    # Draw colors into the array
    for i in range(10):
        y = int((math.sin(s) + 1) * 120 - 10)
        raster(colors, y, 48, pix.color.BLACK, raster_colors[i & 3])
        s += 0.3
    # Create a 1x256 image from the colors
    texture = pix.Image(1, colors)

    # Draw the image stretched and rotated
    screen.draw(
        texture,
        center=screen.size / 2,
        size=screen.size,
        #rot=screen.frame_counter / 500,
    )
    screen.swap()
