import pixpy as pix

screen = pix.open_display(size=(1280, 720))

pos = screen.size / 2

font = pix.load_font("data/hyperspace_bold.ttf")
hello_image = font.make_image("Hello World", size=64, color=pix.color.ORANGE)

screen.draw_color = pix.color.YELLOW
screen.line_width = 4.0

p = pix.Float2(0, 0)
p.iterate(iter([pix.Float2(x, 100) for x in range(100)]))

while pix.run_loop():
    screen.clear(pix.color.BLACK)
    screen.draw(image=hello_image, center=pos, rot=pos.x / 100)
    screen.circle(center=pos, radius=pos.x / 4)
    # pos += (1, 0)
    pos = p
    screen.swap()
