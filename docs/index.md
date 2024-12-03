# PIXPY

## pixpy (module)

### Methods

#### all_events
```python
all_events() -> list[Union[event.NoEvent, event.Key, event.Move, event.Click, event.Text, event.Resize, event.Quit]]
```
Return a list of all pending events.

#### blend_color
```python
blend_color(color0: int, color1: int, t: float) -> int
```
Blend two colors together. `t` should be between 0 and 1.

#### blend_colors
```python
blend_colors(colors: list[int], t: float) -> int
```
Get a color from a color range. Works similar to bilinear filtering of an 1D texture.

#### get_pointer
```python
get_pointer() -> Float2
```
Get the xy coordinate of the mouse pointer (in screen space).

#### inside_polygon
```python
inside_polygon(points: list[Float2], point: Float2) -> bool
```
Check if the `point` is inside the polygon formed by `points`.

#### is_pressed
```python
is_pressed(key: Union[int, str]) -> bool
```
Returns _True_ if the keyboard or mouse key is held down.

#### load_font
```python
load_font(name: os.PathLike, size: int = 0) -> Font
```
Load a TTF font.

#### load_png
```python
load_png(file_name: os.PathLike) -> Image
```
Create an _Image_ from a png file on disk.

#### open_display
```python
open_display(width: int = -1, height: int = -1, full_screen: bool = False) -> Screen
```


#### open_display
```python
open_display(size: Int2, full_screen: bool = False) -> Screen
```
Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.
Subsequent calls to this method returns the same screen instance, since you can only have one active display in pix.

#### rgba
```python
rgba(red: float, green: float, blue: float, alpha: float) -> int
```
Combine four color components into a color.

#### run_every_frame
```python
run_every_frame(arg0: Callable[[], bool]) -> None
```
Add a function that should be run every frame. If the function returns false it will stop being called.

#### run_loop
```python
run_loop() -> bool
```
Should be called first in your main rendering loop. Clears all pending events and all pressed keys. Returns _True_ as long as the application is running (the user has not closed the window or quit in some other way

#### save_png
```python
save_png(image: Image, file_name: os.PathLike) -> None
```
Save an _Image_ to disk

#### was_pressed
```python
was_pressed(key: Union[int, str]) -> bool
```
Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.

#### was_released
```python
was_released(key: Union[int, str]) -> bool
```
Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.


### Constants
```python

BLEND_ADD = 0x03020001
BLEND_MULTIPLY = 0x03060000
BLEND_NORMAL = 0x03020303
```


## Console

### Properties

#### bg_color

Background color.
#### cursor_on

Determine if the cursor should be visible.
#### cursor_pos

The current location of the cursor. This will be used when calling `write()`.
#### fg_color

Foreground color.
#### grid_size

Get number cols and rows
#### size

Get size of consoles in pixels (tile_size * grid_size)
#### tile_size

Get size of a single tile
#### wrapping

Should we wrap when passing right edge (and scroll when passing bottom edge) ?

### Constructors

```python
Console(cols: int, rows: int, font_file: str = '', tile_size: Float2 = Int2(-1, -1), font_size: int = 16)
```
Create a new Console holding `cols`*`rows` tiles.

`font_file` is the file name of a TTF font to use as backing. If no font is given, the built in _Unscii_ font will be used.

`tile_size` sets the size in pixels of each tile. If not given, it will be derived from the size of a character in the font with the provided `font_size`

```python
Console(cols: int, rows: int, tile_set: TileSet)
```
Create a new Console holding `cols`*`row` tiles. Use the provided `tile_set`.


### Methods

#### cancel_line
```python
cancel_line(self: Console) -> None
```
Stop line edit mode.

#### clear
```python
clear(self: Console) -> None
```
Clear the console.

#### get
```python
get(self: Console, arg0: Int2) -> int
```
Get tile at position

#### get_image_for
```python
get_image_for(self: Console, tile: int) -> Image
```
Get the image of a specific tile. Use to render the tile manually, or to copy another image into the tile;

`console.get_image_for(1024).copy_from(some_tile_image)`

#### get_tiles
```python
get_tiles(self: Console) -> list[int]
```
Get all the tiles and colors as an array of ints. Format is: `[tile0, fg0, bg0, tile1, fg1, bg1 ...]` etc.

#### put
```python
put(self: Console, pos: Int2, tile: int, fg: Optional[int] = None, bg: Optional[int] = None) -> None
```
Put `tile` at given position, optionally setting a specific foreground and/or background color

#### read_line
```python
read_line(self: Console) -> None
```
Puts the console in line edit mode.

A cursor will be shown and all text events will be captured by the console until `Enter` is pressed. At this point the entire line will be pushed as a `TextEvent`.

#### set_color
```python
set_color(self: Console, fg: int, bg: int) -> None
```
Set the default colors used when putting/writing to the console.

#### set_line
```python
set_line(self: Console, text: str) -> None
```
Change the edited line.

#### set_tiles
```python
set_tiles(self: Console, tiles: list[int]) -> None
```
Set tiles from an array of ints.

#### write
```python
write(self: Console, tiles: list[str]) -> None
```


#### write
```python
write(self: Console, text: str) -> None
```
Write text to the console at the current cursor position and using the current colors. Will advance cursor position, and wrap if it passes the right border of the console.


## Context

### Properties

#### blend_mode

Set the blend mode.
#### draw_color

Set the draw color.
#### line_width

Set the line with in fractional pixels.
#### point_size

Set the point size in fractional pixels.

### Methods

#### circle
```python
circle(self: Context, center: Float2, radius: float) -> None
```
Draw an (outline) circle

#### clear
```python
clear(self: Context, color: int = 255) -> None
```
Clear the context using given color.

#### draw
```python
draw(self: Context, image: Image, top_left: Optional[Float2] = None, center: Optional[Float2] = None, size: Float2 = Float2(0.000000, 0.000000), rot: float = 0) -> None
```
Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.

#### draw
```python
draw(self: Context, drawable: Console, top_left: Float2 = Float2(0.000000, 0.000000), size: Float2 = Float2(0.000000, 0.000000)) -> None
```
Render a console. `top_left` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.

To render a full screen console (scaling as needed):

`console.render(screen.context, size=screen.size)`

#### filled_circle
```python
filled_circle(self: Context, center: Float2, radius: float) -> None
```
Draw a filled circle.

#### filled_rect
```python
filled_rect(self: Context, top_left: Float2, size: Float2) -> None
```
Draw a filled rectangle.

#### flush
```python
flush(self: Context) -> None
```
Flush pixel operations

#### line
```python
line(self: Context, start: Float2, end: Float2) -> None
```
Draw a line between start and end.

#### line
```python
line(self: Context, end: Float2) -> None
```
Draw a line from the end of the last line to the given position.

#### lines
```python
lines(self: Context, points: list[Float2]) -> None
```
Draw a line strip from all the given points.

#### plot
```python
plot(self: Context, center: Float2, color: int) -> None
```
Draw a point.

#### plot
```python
plot(self: Context, points: object, colors: object) -> None
```
Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.

#### polygon
```python
polygon(self: Context, points: list[Float2], convex: bool = False) -> None
```
Draw a filled polygon.

#### rect
```python
rect(self: Context, top_left: Float2, size: Float2) -> None
```
Draw a rectangle.

#### set_pixel
```python
set_pixel(self: Context, pos: Int2, color: int) -> None
```
Write a pixel into the image.


## Float2

### Constructors

```python
Float2(x: int = 0, y: int = 0)
```


```python
Float2(x: int = 0, y: float = 0)
```


```python
Float2(x: float = 0, y: int = 0)
```


```python
Float2(x: float = 0, y: float = 0)
```


```python
Float2(arg0: tuple[float, float])
```



### Methods

#### angle
```python
angle(self: Float2) -> float
```
Get the angle between the vector and (1,0).

#### clamp
```python
clamp(self: Float2, low: Float2, high: Float2) -> Float2
```
Separately clamp the x and y component between the corresponding components in the given arguments.

#### clip
```python
clip(self: Float2, low: Float2, high: Float2) -> Float2
```
Compare the point against the bounding box defined by low/high. Returns (0,0) if point is inside the box, or a negative or positive distance to the edge if outside.

#### cossin
```python
cossin(self: Float2) -> Float2
```
Returns (cos(x), sin(y)).

#### from_angle
```python
from_angle(arg0: float) -> Float2
```
From angle

#### inside_polygon
```python
inside_polygon(self: Float2, points: list[Float2]) -> bool
```
Check if the `point` is inside the polygon formed by `points`.

#### mag
```python
mag(self: Float2) -> float
```
Get magnitude (length) of vector

#### mag2
```python
mag2(self: Float2) -> float
```
Get the squared magnitude

#### norm
```python
norm(self: Float2) -> Float2
```
Get the normalized vector.

#### random
```python
random(self: Float2) -> Float2
```
Returns Float2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.

#### toi
```python
toi(self: Float2) -> Int2
```
Convert a `Float2` to an `Int2`


## Font

### Constructors

```python
Font(font_file: str = '')
```
Create a font from a TTF file.


### Methods

#### make_image
```python
make_image(self: Font, text: str, size: int, color: int = 4294967295) -> Image
```
Create an image containing the given text.


## Image

### Properties

#### blend_mode

Set the blend mode.
#### draw_color

Set the draw color.
#### line_width

Set the line with in fractional pixels.
#### point_size

Set the point size in fractional pixels.
#### pos

The position of this image in its texture. Will normally be (0, 0) unless this image was split or cropped from another image.

### Constructors

```python
Image(width: int, height: int)
```


```python
Image(size: Float2)
```
Create an empty image of the given size.

```python
Image(width: int, pixels: list[int])
```
Create an image from an array of 32-bit colors.


### Methods

#### circle
```python
circle(self: Image, center: Float2, radius: float) -> None
```
Draw an (outline) circle

#### clear
```python
clear(self: Image, color: int = 255) -> None
```
Clear the context using given color.

#### copy_from
```python
copy_from(self: Image, image: Image) -> None
```
Render one image into another.

#### copy_to
```python
copy_to(self: Image, image: Image) -> None
```
Render one image into another.

#### crop
```python
crop(self: Image, top_left: Optional[Float2] = None, size: Optional[Float2] = None) -> Image
```
Crop an image. Returns a view into the old image.

#### draw
```python
draw(self: Image, image: Image, top_left: Optional[Float2] = None, center: Optional[Float2] = None, size: Float2 = Float2(0.000000, 0.000000), rot: float = 0) -> None
```
Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.

#### draw
```python
draw(self: Image, drawable: Console, top_left: Float2 = Float2(0.000000, 0.000000), size: Float2 = Float2(0.000000, 0.000000)) -> None
```
Render a console. `top_left` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.

To render a full screen console (scaling as needed):

`console.render(screen.context, size=screen.size)`

#### filled_circle
```python
filled_circle(self: Image, center: Float2, radius: float) -> None
```
Draw a filled circle.

#### filled_rect
```python
filled_rect(self: Image, top_left: Float2, size: Float2) -> None
```
Draw a filled rectangle.

#### flush
```python
flush(self: Image) -> None
```
Flush pixel operations

#### line
```python
line(self: Image, start: Float2, end: Float2) -> None
```
Draw a line between start and end.

#### line
```python
line(self: Image, end: Float2) -> None
```
Draw a line from the end of the last line to the given position.

#### lines
```python
lines(self: Image, points: list[Float2]) -> None
```
Draw a line strip from all the given points.

#### plot
```python
plot(self: Image, center: Float2, color: int) -> None
```
Draw a point.

#### plot
```python
plot(self: Image, points: object, colors: object) -> None
```
Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.

#### polygon
```python
polygon(self: Image, points: list[Float2], convex: bool = False) -> None
```
Draw a filled polygon.

#### rect
```python
rect(self: Image, top_left: Float2, size: Float2) -> None
```
Draw a rectangle.

#### set_pixel
```python
set_pixel(self: Image, pos: Int2, color: int) -> None
```
Write a pixel into the image.

#### set_texture_filter
```python
set_texture_filter(self: Image, min: bool, max: bool) -> None
```
Set whether the texture should apply linear filtering.

#### split
```python
split(self: Image, cols: int = -1, rows: int = -1, width: int = 8, height: int = 8) -> list[Image]
```
Splits the image into as many _width_ * _height_ images as possible, first going left to right, then top to bottom.

#### split
```python
split(self: Image, size: Float2) -> list[Image]
```



## Int2

### Constructors

```python
Int2(x: int = 0, y: int = 0)
```


```python
Int2(x: int = 0, y: float = 0)
```


```python
Int2(x: float = 0, y: int = 0)
```


```python
Int2(x: float = 0, y: float = 0)
```


```python
Int2(arg0: tuple[int, int])
```



### Methods

#### clamp
```python
clamp(self: Int2, low: Int2, high: Int2) -> Int2
```
Separately clamp the x and y component between the corresponding components in the given arguments.

#### random
```python
random(self: Int2) -> Int2
```
Returns Int2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.

#### tof
```python
tof(self: Int2) -> Float2
```
Convert an `Int2` to a `Float2`


## Screen

### Properties

#### blend_mode

Set the blend mode.
#### delta

Time in seconds for last frame.
#### draw_color

Set the draw color.
#### fps

Current FPS. Set to 0 to disable fixed FPS. Then use `seconds` or `delta` to sync your movement.
#### line_width

Set the line with in fractional pixels.
#### point_size

Set the point size in fractional pixels.
#### refresh_rate

Actual refresh rate of current monitor.
#### seconds

Total seconds elapsed since starting pix.

### Methods

#### circle
```python
circle(self: Screen, center: Float2, radius: float) -> None
```
Draw an (outline) circle

#### clear
```python
clear(self: Screen, color: int = 255) -> None
```
Clear the context using given color.

#### draw
```python
draw(self: Screen, image: Image, top_left: Optional[Float2] = None, center: Optional[Float2] = None, size: Float2 = Float2(0.000000, 0.000000), rot: float = 0) -> None
```
Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.

#### draw
```python
draw(self: Screen, drawable: Console, top_left: Float2 = Float2(0.000000, 0.000000), size: Float2 = Float2(0.000000, 0.000000)) -> None
```
Render a console. `top_left` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.

To render a full screen console (scaling as needed):

`console.render(screen.context, size=screen.size)`

#### filled_circle
```python
filled_circle(self: Screen, center: Float2, radius: float) -> None
```
Draw a filled circle.

#### filled_rect
```python
filled_rect(self: Screen, top_left: Float2, size: Float2) -> None
```
Draw a filled rectangle.

#### flush
```python
flush(self: Screen) -> None
```
Flush pixel operations

#### line
```python
line(self: Screen, start: Float2, end: Float2) -> None
```
Draw a line between start and end.

#### line
```python
line(self: Screen, end: Float2) -> None
```
Draw a line from the end of the last line to the given position.

#### lines
```python
lines(self: Screen, points: list[Float2]) -> None
```
Draw a line strip from all the given points.

#### plot
```python
plot(self: Screen, center: Float2, color: int) -> None
```
Draw a point.

#### plot
```python
plot(self: Screen, points: object, colors: object) -> None
```
Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.

#### polygon
```python
polygon(self: Screen, points: list[Float2], convex: bool = False) -> None
```
Draw a filled polygon.

#### rect
```python
rect(self: Screen, top_left: Float2, size: Float2) -> None
```
Draw a rectangle.

#### set_pixel
```python
set_pixel(self: Screen, pos: Int2, color: int) -> None
```
Write a pixel into the image.

#### swap
```python
swap(self: Screen) -> None
```
Synchronize with the frame rate of the display and swap buffers so what you have drawn becomes visible. This is normally the last thing you do in your render loop.


## TileSet

### Constructors

```python
TileSet(font_file: str, size: int)
```
Create a TileSet from a ttf font with the given size. The tile size will be derived from the font size.

```python
TileSet(font: Font, tile_size: Int2 = Int2(-1, -1))
```
Create a TileSet from an existing font. The tile size will be derived from the font size.

```python
TileSet(tile_size: Float2)
```
Create an empty tileset with the given tile size.


### Methods

#### get_image_for
```python
get_image_for(self: TileSet, arg0: int) -> Image
```
Get the image for a specific tile. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.

#### get_image_for
```python
get_image_for(self: TileSet, arg0: str) -> Image
```
Get the image for a specific character. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.

#### get_tileset_image
```python
get_tileset_image(self: TileSet) -> Image
```
Get the entire tileset image. Typically used with `save_png()` to check generated tileset.

#### render_text
```python
render_text(self: TileSet, screen: Screen, text: str, pos: Float2, size: Float2 = Float2(0.000000, 0.000000)) -> None
```
Render characters from the TileSet at given `pos` and given `size` (defaults to tile_size)

#### render_text
```python
render_text(self: TileSet, screen: Screen, text: str, points: list[Float2]) -> None
```


## pixpy.color (module)

### Constants
```python

BLACK = 0x000000ff
BLUE = 0x0000aaff
BROWN = 0x664400ff
CYAN = 0xaaffedff
DARK_GREY = 0x333333ff
GREEN = 0x00cc54ff
GREY = 0x777777ff
LIGHT_BLUE = 0x0087ffff
LIGHT_GREEN = 0xaaff66ff
LIGHT_GREY = 0xbababaff
LIGHT_RED = 0xff7777ff
ORANGE = 0xdd8754ff
PURPLE = 0xcc44ccff
RED = 0x870000ff
TRANSP = 0x00000000
WHITE = 0xffffffff
YELLOW = 0xeded77ff
```

## pixpy.key (module)

### Constants
```python

A1 = 0x00000005
B1 = 0x00000008
BACKSPACE = 0x00000008
DELETE = 0x0000000d
DOWN = 0x00000002
END = 0x0000000b
ENTER = 0x0000000a
ESCAPE = 0x0000001b
F1 = 0x00100000
F10 = 0x00100009
F11 = 0x0010000a
F12 = 0x0010000b
F2 = 0x00100001
F3 = 0x00100002
F4 = 0x00100003
F5 = 0x00100004
F6 = 0x00100005
F7 = 0x00100006
F8 = 0x00100007
F9 = 0x00100008
FIRE = 0x00000005
HOME = 0x0000000c
INSERT = 0x00000010
L1 = 0x0000000c
L2 = 0x0000000f
LEFT = 0x00000003
LEFT_MOUSE = 0x00100020
MIDDLE_MOUSE = 0x00100022
MOD_ALT = 0x00000004
MOD_CTRL = 0x00000002
MOD_SHIFT = 0x00000001
MOUSE4 = 0x00100023
MOUSE5 = 0x00100024
PAGEDOWN = 0x0000000e
PAGEUP = 0x0000000f
R1 = 0x0000000b
R2 = 0x0000000e
RIGHT = 0x00000001
RIGHT_MOUSE = 0x00100021
SELECT = 0x00000009
SPACE = 0x00000020
START = 0x0000000a
TAB = 0x00000009
UP = 0x00000004
X1 = 0x00000006
Y1 = 0x00000007
```

