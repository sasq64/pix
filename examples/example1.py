import pixpy as pix

display = pix.open_display(size=(1280, 720))

canvas = pix.Image(size=(11,11))
canvas.draw_color = pix.color.YELLOW
canvas.filled_rect((1,1), (8,8))
canvas.draw_color = pix.color.RED
canvas.filled_rect((2,2), (6,6))
canvas.draw_color = pix.color.GREEN
#canvas.filled_rect((3,3), (4,4))

canvas.filled_circle((5,5), 5)

display.draw(canvas, size=canvas.size * 10)
