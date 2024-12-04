# PIXPY

## pixpy (module)

### Methods

#### `pixpy.all_events`
```python
all_events() -> list[Union[event.NoEvent, event.Key, event.Move, event.Click, event.Text, event.Resize, event.Quit]]
```
Return a list of all pending events.

#### `pixpy.blend_color`
```python
blend_color(color0: int, color1: int, t: float) -> int
```
Blend two colors together. `t` should be between 0 and 1.

#### `pixpy.blend_colors`
```python
blend_colors(colors: list[int], t: float) -> int
```
Get a color from a color range. Works similar to bilinear filtering of an 1D texture.

#### `pixpy.get_pointer`
```python
get_pointer() -> Float2
```
Get the xy coordinate of the mouse pointer (in screen space).

#### `pixpy.inside_polygon`
```python
inside_polygon(points: list[Float2], point: Float2) -> bool
```
Check if the `point` is inside the polygon formed by `points`.

#### `pixpy.is_pressed`
```python
is_pressed(key: Union[int, str]) -> bool
```
Returns _True_ if the keyboard or mouse key is held down.

#### `pixpy.load_font`
```python
load_font(name: os.PathLike, size: int = 0) -> Font
```
Load a TTF font.

#### `pixpy.load_png`
```python
load_png(file_name: os.PathLike) -> Image
```
Create an _Image_ from a png file on disk.

#### `pixpy.open_display`
```python
open_display(width: int = -1, height: int = -1, full_screen: bool = False) -> Screen
```


#### `pixpy.open_display`
```python
open_display(size: Int2, full_screen: bool = False) -> Screen
```
Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.
Subsequent calls to this method returns the same screen instance, since you can only have one active display in pix.

#### `pixpy.rgba`
```python
rgba(red: float, green: float, blue: float, alpha: float) -> int
```
Combine four color components into a color.

#### `pixpy.run_every_frame`
```python
run_every_frame(arg0: Callable[[], bool]) -> None
```
Add a function that should be run every frame. If the function returns false it will stop being called.

#### `pixpy.run_loop`
```python
run_loop() -> bool
```
Should be called first in your main rendering loop. Clears all pending events and all pressed keys. Returns _True_ as long as the application is running (the user has not closed the window or quit in some other way

#### `pixpy.save_png`
```python
save_png(image: Image, file_name: os.PathLike) -> None
```
Save an _Image_ to disk

#### `pixpy.was_pressed`
```python
was_pressed(key: Union[int, str]) -> bool
```
Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.

#### `pixpy.was_released`
```python
was_released(key: Union[int, str]) -> bool
```
Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.


### Constants
```python

pixpy.BLEND_ADD = 0x03020001
pixpy.BLEND_MULTIPLY = 0x03060000
pixpy.BLEND_NORMAL = 0x03020303
```


## Console

A console is a 2D grid of tiles that can be rendered.


### Properties

#### `Console.bg_color`

Background color.
#### `Console.cursor_on`

Determine if the cursor should be visible.
#### `Console.cursor_pos`

The current location of the cursor. This will be used when calling `write()`.
#### `Console.fg_color`

Foreground color.
#### `Console.grid_size`

Get number cols and rows
#### `Console.size`

Get size of consoles in pixels (tile_size * grid_size)
#### `Console.tile_size`

Get size of a single tile
#### `Console.wrapping`

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

#### `Console.cancel_line`
```python
cancel_line(self: Console) -> None
```
Stop line edit mode.

#### `Console.clear`
```python
clear(self: Console) -> None
```
Clear the console.

#### `Console.get`
```python
get(arg0: Int2) -> int
```
Get tile at position

#### `Console.get_image_for`
```python
get_image_for(tile: int) -> Image
```
Get the image of a specific tile. Use to render the tile manually, or to copy another image into the tile;

`console.get_image_for(1024).copy_from(some_tile_image)`

#### `Console.get_tiles`
```python
get_tiles(self: Console) -> list[int]
```
Get all the tiles and colors as an array of ints. Format is: `[tile0, fg0, bg0, tile1, fg1, bg1 ...]` etc.

#### `Console.put`
```python
put(pos: Int2, tile: int, fg: Optional[int] = None, bg: Optional[int] = None) -> None
```
Put `tile` at given position, optionally setting a specific foreground and/or background color

#### `Console.read_line`
```python
read_line(self: Console) -> None
```
Puts the console in line edit mode.

A cursor will be shown and all text events will be captured by the console until `Enter` is pressed. At this point the entire line will be pushed as a `TextEvent`.

#### `Console.set_color`
```python
set_color(fg: int, bg: int) -> None
```
Set the default colors used when putting/writing to the console.

#### `Console.set_line`
```python
set_line(text: str) -> None
```
Change the edited line.

#### `Console.set_tiles`
```python
set_tiles(tiles: list[int]) -> None
```
Set tiles from an array of ints.

#### `Console.write`
```python
write(tiles: list[str]) -> None
```


#### `Console.write`
```python
write(text: str) -> None
```
Write text to the console at the current cursor position and using the current colors. Will advance cursor position, and wrap if it passes the right border of the console.


## Context

A `Context` is used for rendering. It is implemented by both `Screen` and `Image`.


### Properties

#### `Context.blend_mode`

Set the blend mode. Normally one of the constants `pix.BLEND_ADD`, `pix.BLEND_MULTIPLY` or `pix.BLEND_NORMAL`.
#### `Context.draw_color`

Set the draw color.
#### `Context.line_width`

Set the line with in fractional pixels.
#### `Context.point_size`

Set the point size in fractional pixels.

### Methods

#### `Context.circle`
```python
circle(center: Float2, radius: float) -> None
```
Draw an (outline) circle

#### `Context.clear`
```python
clear(color: int = color.BLACK) -> None
```
Clear the context using given color.

#### `Context.draw`
```python
draw(image: Image, top_left: Optional[Float2] = None, center: Optional[Float2] = None, size: Float2 = Float2.ZERO, rot: float = 0) -> None
```
Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.

#### `Context.draw`
```python
draw(drawable: Console, top_left: Float2 = Float2.ZERO, size: Float2 = Float2.ZERO) -> None
```
Render a console. `top_left` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.

To render a full screen console (scaling as needed):

`console.render(screen.context, size=screen.size)`

#### `Context.filled_circle`
```python
filled_circle(center: Float2, radius: float) -> None
```
Draw a filled circle.

#### `Context.filled_rect`
```python
filled_rect(top_left: Float2, size: Float2) -> None
```
Draw a filled rectangle.

#### `Context.flush`
```python
flush(self: Context) -> None
```
Flush pixel operations

#### `Context.line`
```python
line(start: Float2, end: Float2) -> None
```
Draw a line between start and end.

#### `Context.line`
```python
line(end: Float2) -> None
```
Draw a line from the end of the last line to the given position.

#### `Context.lines`
```python
lines(points: list[Float2]) -> None
```
Draw a line strip from all the given points.

#### `Context.plot`
```python
plot(center: Float2, color: int) -> None
```
Draw a point.

#### `Context.plot`
```python
plot(points: object, colors: object) -> None
```
Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.

#### `Context.polygon`
```python
polygon(points: list[Float2], convex: bool = False) -> None
```
Draw a filled polygon.

#### `Context.rect`
```python
rect(top_left: Float2, size: Float2) -> None
```
Draw a rectangle.

#### `Context.set_pixel`
```python
set_pixel(pos: Int2, color: int) -> None
```
Write a pixel into the image.


## Float2

Represents an floating point coordinate or size. Mostly behaves like a normal float when used in arithmetic operations.


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

#### `Float2.angle`
```python
angle(self: Float2) -> float
```
Get the angle between the vector and (1,0).

#### `Float2.clamp`
```python
clamp(low: Float2, high: Float2) -> Float2
```
Separately clamp the x and y component between the corresponding components in the given arguments.

#### `Float2.clip`
```python
clip(low: Float2, high: Float2) -> Float2
```
Compare the point against the bounding box defined by low/high. Returns (0,0) if point is inside the box, or a negative or positive distance to the edge if outside.

#### `Float2.cossin`
```python
cossin(self: Float2) -> Float2
```
Returns (cos(x), sin(y)).

#### `Float2.from_angle`
```python
from_angle(arg0: float) -> Float2
```
From angle

#### `Float2.inside_polygon`
```python
inside_polygon(points: list[Float2]) -> bool
```
Check if the `point` is inside the polygon formed by `points`.

#### `Float2.mag`
```python
mag(self: Float2) -> float
```
Get magnitude (length) of vector

#### `Float2.mag2`
```python
mag2(self: Float2) -> float
```
Get the squared magnitude

#### `Float2.norm`
```python
norm(self: Float2) -> Float2
```
Get the normalized vector.

#### `Float2.random`
```python
random(self: Float2) -> Float2
```
Returns Float2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.

#### `Float2.toi`
```python
toi(self: Float2) -> Int2
```
Convert a `Float2` to an `Int2`


## Font

Represents a TTF (Freetype) font that can be used to create text images.


### Constructors

```python
Font(font_file: str = '')
```
Create a font from a TTF file.


### Methods

#### `Font.make_image`
```python
make_image(text: str, size: int, color: int = color.WHITE) -> Image
```
Create an image containing the given text.


## Image

A `Context` is used for rendering. It is implemented by both `Screen` and `Image`.


### Properties

#### `Image.blend_mode`

Set the blend mode. Normally one of the constants `pix.BLEND_ADD`, `pix.BLEND_MULTIPLY` or `pix.BLEND_NORMAL`.
#### `Image.draw_color`

Set the draw color.
#### `Image.line_width`

Set the line with in fractional pixels.
#### `Image.point_size`

Set the point size in fractional pixels.
#### `Image.pos`

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

#### `Image.circle`
```python
circle(center: Float2, radius: float) -> None
```
Draw an (outline) circle

#### `Image.clear`
```python
clear(color: int = color.BLACK) -> None
```
Clear the context using given color.

#### `Image.copy_from`
```python
copy_from(image: Image) -> None
```
Render one image into another.

#### `Image.copy_to`
```python
copy_to(image: Image) -> None
```
Render one image into another.

#### `Image.crop`
```python
crop(top_left: Optional[Float2] = None, size: Optional[Float2] = None) -> Image
```
Crop an image. Returns a view into the old image.

#### `Image.draw`
```python
draw(image: Image, top_left: Optional[Float2] = None, center: Optional[Float2] = None, size: Float2 = Float2.ZERO, rot: float = 0) -> None
```
Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.

#### `Image.draw`
```python
draw(drawable: Console, top_left: Float2 = Float2.ZERO, size: Float2 = Float2.ZERO) -> None
```
Render a console. `top_left` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.

To render a full screen console (scaling as needed):

`console.render(screen.context, size=screen.size)`

#### `Image.filled_circle`
```python
filled_circle(center: Float2, radius: float) -> None
```
Draw a filled circle.

#### `Image.filled_rect`
```python
filled_rect(top_left: Float2, size: Float2) -> None
```
Draw a filled rectangle.

#### `Image.flush`
```python
flush(self: Image) -> None
```
Flush pixel operations

#### `Image.line`
```python
line(start: Float2, end: Float2) -> None
```
Draw a line between start and end.

#### `Image.line`
```python
line(end: Float2) -> None
```
Draw a line from the end of the last line to the given position.

#### `Image.lines`
```python
lines(points: list[Float2]) -> None
```
Draw a line strip from all the given points.

#### `Image.plot`
```python
plot(center: Float2, color: int) -> None
```
Draw a point.

#### `Image.plot`
```python
plot(points: object, colors: object) -> None
```
Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.

#### `Image.polygon`
```python
polygon(points: list[Float2], convex: bool = False) -> None
```
Draw a filled polygon.

#### `Image.rect`
```python
rect(top_left: Float2, size: Float2) -> None
```
Draw a rectangle.

#### `Image.set_pixel`
```python
set_pixel(pos: Int2, color: int) -> None
```
Write a pixel into the image.

#### `Image.set_texture_filter`
```python
set_texture_filter(min: bool, max: bool) -> None
```
Set whether the texture should apply linear filtering.

#### `Image.split`
```python
split(cols: int = -1, rows: int = -1, width: int = 8, height: int = 8) -> list[Image]
```
Splits the image into as many _width_ * _height_ images as possible, first going left to right, then top to bottom.

#### `Image.split`
```python
split(size: Float2) -> list[Image]
```



## Int2

Represents an integer coordinate or size. Mostly behaves like a normal int when used in arithmetic operations.


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

#### `Int2.clamp`
```python
clamp(low: Int2, high: Int2) -> Int2
```
Separately clamp the x and y component between the corresponding components in the given arguments.

#### `Int2.random`
```python
random(self: Int2) -> Int2
```
Returns Int2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.

#### `Int2.tof`
```python
tof(self: Int2) -> Float2
```
Convert an `Int2` to a `Float2`


## Screen

A `Context` is used for rendering. It is implemented by both `Screen` and `Image`.


### Properties

#### `Screen.blend_mode`

Set the blend mode. Normally one of the constants `pix.BLEND_ADD`, `pix.BLEND_MULTIPLY` or `pix.BLEND_NORMAL`.
#### `Screen.delta`

Time in seconds for last frame.
#### `Screen.draw_color`

Set the draw color.
#### `Screen.fps`

Current FPS. Set to 0 to disable fixed FPS. Then use `seconds` or `delta` to sync your movement.
#### `Screen.line_width`

Set the line with in fractional pixels.
#### `Screen.point_size`

Set the point size in fractional pixels.
#### `Screen.refresh_rate`

Actual refresh rate of current monitor.
#### `Screen.seconds`

Total seconds elapsed since starting pix.

### Methods

#### `Screen.circle`
```python
circle(center: Float2, radius: float) -> None
```
Draw an (outline) circle

#### `Screen.clear`
```python
clear(color: int = color.BLACK) -> None
```
Clear the context using given color.

#### `Screen.draw`
```python
draw(image: Image, top_left: Optional[Float2] = None, center: Optional[Float2] = None, size: Float2 = Float2.ZERO, rot: float = 0) -> None
```
Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.

#### `Screen.draw`
```python
draw(drawable: Console, top_left: Float2 = Float2.ZERO, size: Float2 = Float2.ZERO) -> None
```
Render a console. `top_left` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.

To render a full screen console (scaling as needed):

`console.render(screen.context, size=screen.size)`

#### `Screen.filled_circle`
```python
filled_circle(center: Float2, radius: float) -> None
```
Draw a filled circle.

#### `Screen.filled_rect`
```python
filled_rect(top_left: Float2, size: Float2) -> None
```
Draw a filled rectangle.

#### `Screen.flush`
```python
flush(self: Screen) -> None
```
Flush pixel operations

#### `Screen.line`
```python
line(start: Float2, end: Float2) -> None
```
Draw a line between start and end.

#### `Screen.line`
```python
line(end: Float2) -> None
```
Draw a line from the end of the last line to the given position.

#### `Screen.lines`
```python
lines(points: list[Float2]) -> None
```
Draw a line strip from all the given points.

#### `Screen.plot`
```python
plot(center: Float2, color: int) -> None
```
Draw a point.

#### `Screen.plot`
```python
plot(points: object, colors: object) -> None
```
Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.

#### `Screen.polygon`
```python
polygon(points: list[Float2], convex: bool = False) -> None
```
Draw a filled polygon.

#### `Screen.rect`
```python
rect(top_left: Float2, size: Float2) -> None
```
Draw a rectangle.

#### `Screen.set_pixel`
```python
set_pixel(pos: Int2, color: int) -> None
```
Write a pixel into the image.

#### `Screen.swap`
```python
swap(self: Screen) -> None
```
Synchronize with the frame rate of the display and swap buffers so what you have drawn becomes visible. This is normally the last thing you do in your render loop.


## TileSet

A tileset is a texture split up into tiles for rendering. It is used by the `Console` class but can also be used directly.


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

#### `TileSet.get_image_for`
```python
get_image_for(arg0: int) -> Image
```
Get the image for a specific tile. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.

#### `TileSet.get_image_for`
```python
get_image_for(arg0: str) -> Image
```
Get the image for a specific character. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.

#### `TileSet.get_tileset_image`
```python
get_tileset_image(self: TileSet) -> Image
```
Get the entire tileset image. Typically used with `save_png()` to check generated tileset.

#### `TileSet.render_text`
```python
render_text(screen: Screen, text: str, pos: Float2, size: Float2 = Float2.ZERO) -> None
```
Render characters from the TileSet at given `pos` and given `size` (defaults to tile_size)

#### `TileSet.render_text`
```python
render_text(screen: Screen, text: str, points: list[Float2]) -> None
```
Render characters from the TileSet, each character using the next position from `points`, using the default tile size.

## pixpy.color (module)

### Constants
```python

color.BLACK = 0x000000ff
color.BLUE = 0x0000aaff
color.BROWN = 0x664400ff
color.CYAN = 0xaaffedff
color.DARK_GREY = 0x333333ff
color.GREEN = 0x00cc54ff
color.GREY = 0x777777ff
color.LIGHT_BLUE = 0x0087ffff
color.LIGHT_GREEN = 0xaaff66ff
color.LIGHT_GREY = 0xbababaff
color.LIGHT_RED = 0xff7777ff
color.ORANGE = 0xdd8754ff
color.PURPLE = 0xcc44ccff
color.RED = 0x870000ff
color.TRANSP = 0x00000000
color.WHITE = 0xffffffff
color.YELLOW = 0xeded77ff
```

## pixpy.key (module)

### Constants
```python

key.A1 = 0x00000005
key.B1 = 0x00000008
key.BACKSPACE = 0x00000008
key.DELETE = 0x0000000d
key.DOWN = 0x00000002
key.END = 0x0000000b
key.ENTER = 0x0000000a
key.ESCAPE = 0x0000001b
key.F1 = 0x00100000
key.F10 = 0x00100009
key.F11 = 0x0010000a
key.F12 = 0x0010000b
key.F2 = 0x00100001
key.F3 = 0x00100002
key.F4 = 0x00100003
key.F5 = 0x00100004
key.F6 = 0x00100005
key.F7 = 0x00100006
key.F8 = 0x00100007
key.F9 = 0x00100008
key.FIRE = 0x00000005
key.HOME = 0x0000000c
key.INSERT = 0x00000010
key.L1 = 0x0000000c
key.L2 = 0x0000000f
key.LEFT = 0x00000003
key.LEFT_MOUSE = 0x00100020
key.MIDDLE_MOUSE = 0x00100022
key.MOD_ALT = 0x00000004
key.MOD_CTRL = 0x00000002
key.MOD_SHIFT = 0x00000001
key.MOUSE4 = 0x00100023
key.MOUSE5 = 0x00100024
key.PAGEDOWN = 0x0000000e
key.PAGEUP = 0x0000000f
key.R1 = 0x0000000b
key.R2 = 0x0000000e
key.RIGHT = 0x00000001
key.RIGHT_MOUSE = 0x00100021
key.SELECT = 0x00000009
key.SPACE = 0x00000020
key.START = 0x0000000a
key.TAB = 0x00000009
key.UP = 0x00000004
key.X1 = 0x00000006
key.Y1 = 0x00000007
```

