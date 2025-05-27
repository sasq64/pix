import pixpy as pix

screen = pix.open_display(size=(1280,720))
canvas = pix.Image(size=screen.size)
canvas.point_size = 1

last = pix.Float2.ZERO
while pix.run_loop():
    screen.clear()
    for e in pix.all_events():
        if isinstance(e, pix.event.Click):
            last = e.pos
            canvas.line(start=last, end=last)
        elif isinstance(e, pix.event.Move):
            if e.buttons:
                canvas.line(start=last, end=e.pos)
                last = e.pos
    screen.draw(image=canvas, size=canvas.size)
    screen.swap()

