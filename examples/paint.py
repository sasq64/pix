import pixpy as pix

screen = pix.open_display(size=(1280*2, 720*2))
canvas = pix.Image(size=screen.size * 2)
canvas.point_size = 1
canvas.set_texture_filter(True, True)

last = pix.Float2.ZERO
last_d = 1.0
while pix.run_loop():
    screen.clear()
    for e in pix.all_events():
        if isinstance(e, pix.event.Click):
            last = e.pos
            canvas.rounded_line(last * 2, 10, last * 2, 10)
        elif isinstance(e, pix.event.Move):
            if e.buttons:
                d = (last - e.pos).mag() / 20 + 2
                # canvas.line_width = 8 - d / 5
                canvas.rounded_line(start=last * 2, rad0=last_d, end=e.pos * 2, rad1=d)
                last = e.pos
                last_d = d
    screen.draw(image=canvas, size=screen.size)
    screen.swap()
