import array
import pixpy as pix

display = pix.open_display(size=(1280, 720))
display.draw_color = pix.color.WHITE
display.rect((3,3), (50,50))
display.circle(center=display.size/2, radius=300)
for y in range(50):
    display.set_pixel((8,8+y), pix.color.YELLOW)
    display.set_pixel((80,80+y), pix.color.YELLOW)
display.flush()

image = pix.Image((64, 64))
image.clear(pix.color.LIGHT_BLUE)
image.set_pixel((5, 5), pix.color.YELLOW)
image.set_pixel((30, 30), pix.color.YELLOW)
image.flush()
image.rect((40, 40), (20, 20))
image.flood_fill((45,45), pix.color.RED)
display.draw(image, top_left=(100, 100), size=image.size * 4)

a = array.array('I', [0xff0000ff] * 160*240)

image2 = pix.Image(160, a)

display.draw(image2)

#display.flood_fill((640,360), pix.color.RED)
#display.flood_fill((18,18), pix.color.RED)
