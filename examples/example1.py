import pixpy as pix

display = pix.open_display(size=(1280, 720))
display.draw_color = pix.color.GREEN
display.rect((3,3), (50,50))
display.circle(center=display.size/2, radius=300)
for y in range(50):
    display.set_pixel((8,8+y), pix.color.YELLOW)
    display.set_pixel((80,80+y), pix.color.YELLOW)

display.flush()
#display.flood_fill((640,360), pix.color.RED)
#display.flood_fill((18,18), pix.color.RED)
