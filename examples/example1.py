import pixpy as pix

display = pix.open_display(size=(1280,720))
display.filled_circle(center=display.size/2, radius=200)
