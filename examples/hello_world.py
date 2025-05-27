import pixpy as pix

screen = pix.open_display(size=(1280,720))
text_console = pix.Console(rows=720//32, cols=1280//16, font_file="data/Hack.ttf", font_size=32)
text_console.write("Hello world")
screen.clear(pix.color.RED)
screen.draw(text_console, size=text_console.size)