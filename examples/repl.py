import pixpy as pix


class Repl:
    def __init__(self, con: pix.Console):
        self.con = con
        self.prompt()

    def prompt(self):
        self.con.write("\n>")
        self.con.read_line()

    def update(self, events: list[pix.event.AnyEvent]):
        for e in events:
            if isinstance(e, pix.event.Text):
                try:
                    exec(e.text)
                except Exception as e:
                    print(e)
                self.prompt()
            elif isinstance(e, pix.event.Key):
                pass

    def render(self, target: pix.Canvas):
        target.draw(self.con, self.con.size)
