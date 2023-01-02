## PIX (pixpy)

A graphics library with a python interface.
Designed for learning and 2D game development.

* Uses OpenGL/GLES2 to make it fast and portable
* Efficient Console/TileSet rendering for tile or text based games
* Composable Images using only GL textures

### Install

```sh
pip install pixpy
```

For Linux, we need to build from source so dependencies must be installed first;

```sh
sudo apt install libxinerama-dev libxi-dev libxrandr-dev libxcursor-dev
```

### The Basics

The following is a full program that opens a window and draws a circle;

```python
import pixpy as pix
screen = pix.open_display(size=(1280,720))
screen.circle(center=(640,360), radius=300)
```

**NOTE:** This simple example works because pix is smart enough to "swap" the screen to automatically display what you have drawn, and then leave the window open and wait for the user to close the window, before the script ends.

Normally you create your own main loop and do this yourself;

```python
import pixpy as pix

screen = pix.open_display(width=1280, height=720)

x = 0
while pix.run_loop():
    screen.clear()
    screen.circle(center=(x, screen.height/2), radius=x/4)
    x += 1
    screen.swap()
```

To read the keyboard and/or mouse, you can use _is_pressed()_ or _was_pressed()_

```python
import pixpy as pix

screen = pix.open_display(width=640, height=480)

background = pix.load_png("data/background.png")
sprite = pix.load_png("data/ufo.png")

# Starting position will be the center of the bottom of the screen
pos = pix.Float2(screen.size.x/2, screen.size.y - 50)

while pix.run_loop():
    # Draw the background so it fills the screen
    screen.draw(image=background, size=screen.size)
    
    if pix.is_pressed(pix.key.RIGHT):
        pos += (2,0)
    elif pix.is_pressed(pix.key.LEFT):
        pos -= (2,0)
        
    screen.draw(image=sprite, center=pos)
    screen.swap()
```

For more advanced needs you use events

```python
# A simple paint program
import pixpy as pix

screen = pix.open_display(width=1280, height=720)
canvas = pix.Image(size=screen.size)

while pix.run_loop():
    # Get all events generated this "frame"
    for e in pix.all_events():
        if isinstance(e, pix.event.Click):
            # Zero length line just to remember last `end`
            canvas.line(start=e.pos, end=e.pos)
        elif isinstance(e, pix.event.Move):
            if e.buttons:
                # Draw from last end to new end
                canvas.line(end=e.pos)
    screen.draw(image=canvas)
    screen.swap()
```


### _Float2_ and _Int2_

The _Float2_ and _Int2_ classes acts like tuples of 2 elements, except allows
for basic math operations. They are used to represents points and sizes throughout pixpy.

The act similar to pythons normal _float_ and _int_, so for instance a true division
between two Int2 will always be promoted to a Float2.


### Images

All images are actually just references into Open GL Textures.This means that it's easy to cheaply manipulate images without doing a lot of copying.

One way to think of it is that an image is like an _array slice_ or _array view_; it is cheap to create another view into an existing image.

For instance, you can crop an image like this;

```python
cropped = image.crop(top_left=(10,10), size=image.size-(20,20))
```

`cropped` now becomes a new view into the image, no need to duplicate the actual pixels.

(*NOTE:* In practice, an image is _"a reference to a GL texture, and 4 pairs of UV coordinates"_.)


### The Console

A major part of pix is the _Console_

In its simplest form, it can be used for text output and input.

You can also (re)define the tiles in the console and use it for graphics, such as a tile based platform game.

The console needs to be drawn to be visible, just like everything else.

#### Text output
The console starts out with a backing font that lets you write text;

```python
import pixpy as pix

screen = pix.open_display(width=1280, height=720)
con = pix.Console(cols=80, rows=50)
con.write('Hello\n')
screen.draw(con)
```

#### Text input
`console.read_line()` can be used to read lines of text. The result will be posted as a _TextEvent_.

```python
import pixpy as pix

screen = pix.open_display(width=1280, height=720)
con = pix.Console(cols=40, rows=25)
con.write('What is your name?\n')
con.read_line()
while pix.run_loop():
    for e in pix.all_events():
        if isinstance(e, pix.event.Text):
            con.write(f"Hello {e.text.rstrip()}!")
            con.read_line()

    screen.draw(con)
    screen.swap()
```

#### Graphic tiles

Tiles can be both text and graphics. We can easily add more tiles to the
console by copying images into it.

Note that the `split()` call below is (as we mentioned) cheap -- we only create new views into the original image.

```python
import pixpy as pix

screen = pix.open_display(width=1280, height=720)
con = pix.Console(cols=128, rows=128)

# Load our tile sheet, and split it into an array of tile images
tile_sheet = pix.load_png('tiles16x16.png')
tiles = tile_sheet.split(width=16, height=16)

# Iterate over all tile images, and copy them into the console tile map
for i,tile in enumerate(tiles):
    
    # Get a reference to the image used to represent tile number i+1000.
    # If there is no such tile, an image will be allocated for that tile.
    console_tile = con.get_image_for(i+1000)
    
    # Copy the actual pixels from one image to another.
    console_tile.copy_from(tile)

con.put(pos=(5,5), tile=1000)

screen.draw(con)

```


