= PIX REFERENCE

## pix module

### Functions

#### open_display
```python
open_display(width: int, height: int, full_screen: bool = False) -> Screen
```

```python
open_display(size: Int2, full_screen: bool = False) -> Screen
```

Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.

#### run_loop
```python
run_loop() -> bool
```

Should be called first in your main rendering loop.

Clears all pending events and all pressed keys.

Returns _True_ as long as the application is running (the user has not closed the window or quit in some other way).

#### all_events
```python
all_events() -> List[AnyEvent]
```

Get all pending events.

#### is_pressed
```python
is_pressed(key: int) -> bool
```

Returns _True_ if the keyboard or mouse key is held down.

#### was_pressed
```python
was_pressed(key: int) -> bool

```
Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.

#### get_pointer
```python
get_pointer() -> Float2
```

Get the xy coordinate of the mouse pointer (in screen space).

#### load_png
```python
load_png(file_name: str) -> Image
```

Create an _Image_ from a png file on disk.

#### save_png
```python
save_png(file_name: str, image: Image)
```

Save _Image_ to disk.

#### load_font
```python
load_font(file_name: str, size: int) -> Font
```

Load TTF Font

#### rgba
```python
rgba(r: float, g:float, b:float, a: float) -> int
```

Create a color from 4 color components

## pix.Screen

Represents the display on which rendering takes place. Normally you have only one Screen, that which is returned by `open_display()`.

A Screen is also associated with a _Context_ (see below) and can be rendered to.

### Methods

#### swap
```python
swap()
```

Synchronize with the frame rate of the display and swap buffers. This is
normally the last thing you do in your render loop.

### Attributes

#### size
```python
size : Float2
```

The size of the window/screen

#### seconds
```python
seconds : float
```

Number of seconds since screen opened.

#### delta
```python
delta : float
```

Number of seconds since last frame.

#### fps
```python
fps : int
```

Current target fps. Set this to `0` to not lock to a specific frame rate. In
that case you need to make sure all your movements are time based.

## pix.Image

An Image is a reference to an array of pixels. More specifically, it is a set of UV coordinates and a reference to an Open GL/GLES Texture.

An Image can be associated with a `Context` (see below), so you can render to it.

### Constructors
```python
Image(width: int, height:int) -> Image
```

```python
Image(size: Int2) -> Image
```

Creates an empty Image of the given size. See `load_png()` for loading an Image from disk.

### Methods

#### split
```python
split(cols: int, rows: int) -> List[Image]
```

Split the image into _cols_ * _rows_ smaller images

```python
split(width: int, height: int) -> List[Image]
```

Splits the image into as many _width_ * _height_ images as possible, first going left to right, then top to bottom.

#### crop
```python
crop(top_left: Int2, size: Int2) -> Image
```

Crop the image. Returns a new view into the image.

#### copy_from
```python
copy_from(image: Image)
```

Replace the pixels of this image with the pixels of another image.

Images can be of different sizes. In practice, the source image is used as
a texture and rendered onto the destination image.

#### copy_to
```python
copy_to(image: Image)
```

The inverse of `copy_from()`, copy this image onto another image.

### Attributes

#### size
```python
size : Float2
```

Size of image in pixels. Derived from the UV coordinates associated with
this image.

#### pos
```python
pos: Float2
```

Location of this image within its backing texture. Derived from the UV coordinates associated with this image.

After _splitting_ an image into parts, _pos_ can be used to still render the image parts relative to the other parts.

#### clip_size
```python
clip_size: Float2
```

#### clip_top_left
```python
clip_top_left: Float2
```

## pix.Font

### Constructors

```python
Font(font_file: str, font_size: int)
```

### Methods

#### make_image
```python
make_image(text: str, size:int, color: int = pix.color.WHITE) -> Image
```

Create an image from the given text.

### Static attributes

#### UNSCII_FONT

```python
Font.UNSCII_FONT: Font
```

Static reference to the _unscii_ font, used as default font for the console.


## pix.Context

A `Context` is a rendering context that keeps track of rendering state. You normally need a Context to perform any rendering.

The `Screen` object, as well as all `Image` objects can be treated as Contexts implicitly. This means that they behave as though they've _inherited_ or _mixed in_ a context.

### Constructors
```python
Context(image: Image) -> Context
```

Create a rendering context from an image

```python
Context(screen: Screen) -> Context
```

Create a rendering context from a (the) screen

### Methods

#### clear
```python
clear(color: int = pix.color.BLACK)
```

Clear the render target with the color


#### filled_circle
```python
filled_circle(center: Float2, radius: float)
```

Draw a filled circle.


#### circle
```python
circle(center: Float2, radius: float)
```

Draw a circle.


#### filled_rect
```python
filled_rect(top_left: Float2, size: Float2)
```

Draw a filled rectangle.


#### line
```python
line(start: Float2, end: Float2)
```

```python
line(end: Float2)
```

Draw a line.


#### rect
```python
rect(top_left: Float2, size: Float2)
```

Draw a rectangle from lines.


#### polygon
```python
polygon(points: List[Float2], convex: bool = False)
```

Draw a polygon using the list of points. Use `convex` = true
to avoid the concave ear cutting algorithm if you know the polygon
is convex.


#### plot
```python
plot(point: Float2, color: int)
```

```python
plot(points: List[float], colors: List[int])
```

Draw a point or list of points with the given color. Uses hardware points
which may or may not be round, and may or may not be affected by `context.point_size`.


#### draw
```python
draw(image: Image, top_left: Float2 = None, size: Float2 = (0,0))
```

```python
draw(image: Image, center: Float2 = None, size: Float2 = (0,0), rot = 0)
```

Draw an `image` on to a context at the location given by `top_left`

If `size` is given, scale the image to that size (in screen coordinates). Size can be negative to flip the image.

If `rot` is given, rotate image around `center`


#### set_pixel
```python
set_pixel(point: Int2, color: int)
```

Write a pixel directly into a CPU side copy of the texture. Use `flush()` to
flush changes back into the the actual texture.

####  flush()
```python
flush()
```

Flush pixel operations by uploading the CPU side pixel array to the texture,
and then removing the array.


### Attributes

#### draw_color
```python
draw_color : int
```

The color to use for drawing operations

#### line_width
```python
line_width : float
```

The width of lines and rects


#### point_size
```python
point_size : float
```

The radius of points. May not be supported on all platforms.

#### clip_top_left
```python
clip_top_left : Int2
```

#### clip_size
```python
clip_size : Int2
```

## pix.TileSet

### Constructors

```python
TileSet(font_file: str, size: int)
```

```python
TileSet(font: pix.Font, tile_size: Float2)
```

### Methods

#### get_image_for
```python
get_image_for(tile: int) -> Image
```

#### get_tileset_image
```python
get_tileset_image() -> Image
```

#### render_text
```python
render_text(screen: Screen, text: str, pos: Float2, size: Float2)
```

```python
render_text(screen: Screen, text: str, points: List[Float2])
```

## pix.Console

### Constructors

```python
Console(cols: int, rows: int, font_file: str = "", tile_size: Int2 = (0,0), font_size: int = 0)
```

Create a Console that can display `cols`*`rows` characters or tiles.

`font_file` is the file name of a TTF font to use a backing. If no font is given, the built-in _Unscii_ font will be used.

`tile_size` sets the size in pixels of each tile. If not given, it will be derived from the size of a character in the font with the provided `font_size`.


```python
Console(cols: int, rows: int, tile_set: TileSet)
```

Create a Console that can display `cols`*`rows` characters or tiles, and use the given `TileSet`.

### Methods

#### render
```python
render(context: Context, pos: Float2 = (0,0), size: Float2 = (0,0))
```

Render the console using the context. `pos` and `size` are in pixels. If `size`
is not given, it defaults to `tile_size*grid_size`.

To render a full screen console (scaling as needed):

`console.render(screen.context, size=screen.size)`

#### put
```python
put(pos: Int2, tile: int, fg: int = color.WHITE, bg: int = color.BLACK)
```

Put a tile or text on the console

#### get
```python
get(pos: Int2) -> int
```

#### get_image_for
```python
get_image_for(tile: int) -> Image
```

Get an image referencing a specific tile in the tile set for
the console. Normally used to define your own tiles;
`console.get_image_for(1024).copy_from(some_tile_image)`

#### read_line
```python
read_line()
```

Puts the console in _line edit mode_.

A cursor will be shown and all text events will be captured by the console
until _Enter_ is pressed. At this point the entire line will be pushed as a
TextEvent.

#### cancel_line
```python
cancel_line()
```

Cancels line editing.

#### set_line
```python
set_line(text: str)
```

Updates the contents of the edited line


#### get_tiles
```python
get_tiles() -> List[int]
```

Get all the tiles and colors as an array of ints.

Format is: `[tile0, fg0, bg0, tile1, fg1, bg1 ...]` etc.

#### set_tiles
```python
set_tiles(List[int])
```

Set all the tiles and colors from an array of ints.


### Attributes

#### tile_size
```python
tile_size: Int2
```

Size of a single tile or character in pixels.

#### grid_size
```python
grid_size: Int2
```

Size of the grid; Number of columns and rows.

## pix.events

### Key
Event sent when a key was pressed

```python
key: int
mods: int
```

### Click
Event sent when use clicks on the screen

```python
x: int
y: int
pos: Float2
buttons: int
```

### Move
Event sent when user moves mouse

```python
x: int
y: int
pos: Float2
buttons: int
```

### Text
Event sent when text was input in the window. This event is used by `Console.read_line()` to post its result.

```python
text: str
```

### Resize
Screen was resized

```python
size: Float2
```

## pix.key

Constants for keys on keyboards and other devices

```python
# Cursor keys and gamepad
pix.key.LEFT
pix.key.RIGHT
pix.key.UP
pix.key.DOWN

# Mouse buttons
pix.key.LEFT_MOUSE
pix.key.RIGHT_MOUSE
pix.key.MIDDLE_MOUSE
pix.key.MOUSE4
pix.key.MOUSE5

# Gamepad
pix.key.FIRE
pix.key.A1
pix.key.X1
pix.key.Y1
pix.key.B1
pix.key.R1
pix.key.L1
pix.key.R2
pix.key.L2
pix.key.SELECT
pix.key.START

# Keyboard

pix.key.ENTER
pix.key.BACKSPACE
pix.key.TAB
pix.key.END
pix.key.HOME
pix.key.DELETE
pix.key.PAGEDOWN
pix.key.PAGEUP
pix.key.INSERT
pix.key.ESCAPE
pix.key.SPACE

pix.key.F1
pix.key.F2
pix.key.F3
pix.key.F4
pix.key.F5
pix.key.F6
pix.key.F7
pix.key.F8
pix.key.F9
pix.key.F10
pix.key.F11
pix.key.F12
```

## pix.color

Constants for colors

```python
pix.color.BLACK
pix.color.WHITE
pix.color.RED
pix.color.CYAN
pix.color.PURPLE
pix.color.GREEN
pix.color.BLUE
pix.color.YELLOW
pix.color.ORANGE
pix.color.BROWN
pix.color.LIGHT_RED
pix.color.DARK_GREY
pix.color.GREY
pix.color.LIGHT_GREEN
pix.color.LIGHT_BLUE
pix.color.LIGHT_GREY
```
