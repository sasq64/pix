import pixpy as pix

def main():
    screen = pix.open_display(size=(1280,720))
    console = pix.Console(cols=1280//16, rows=720//32)

    console.write('What is your name?\n')
    console.read_line()
    while pix.run_loop():
        for e in pix.all_events():
            if isinstance(e, pix.event.Text):
                console.write(f"\nHello {e.text}")
                console.read_line()

        screen.draw(drawable=console, top_left=(0,0), size=screen.size)
        screen.swap()

main()

