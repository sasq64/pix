"""
pixpy native module
"""
from __future__ import annotations
from typing import Union, Tuple, List
import os
import typing
from . import color
from . import event
from . import key
from . import treesitter
__all__ = ['BLEND_ADD', 'BLEND_COPY', 'BLEND_MULTIPLY', 'BLEND_NORMAL', 'Canvas', 'Console', 'Float2', 'Font', 'Image', 'Int2', 'Screen', 'TileSet', 'add_color', 'add_event_listener', 'all_events', 'allow_break', 'blend_color', 'blend_colors', 'color', 'event', 'get_clipboard', 'get_display', 'get_pointer', 'inside_polygon', 'is_pressed', 'key', 'load_font', 'load_png', 'open_display', 'post_event', 'quit_loop', 'remove_event_listener', 'rgba', 'run_every_frame', 'run_loop', 'save_png', 'set_clipboard', 'set_keyboard_device', 'treesitter', 'update_tweens', 'was_pressed', 'was_released']
class Canvas:
    """
    A `Canvas` is used for rendering. It is implemented by both `Screen` and `Image`.
    """
    scale: Union[Float2, Int2, Tuple[float, float]]
    def begin_lines(self) -> None:
        """
        Clear the last line point. The next call to `line(p)` or `rounded_line(p, r)` will start a new line sequence.
        """
    def circle(self, center: Union[Float2, Int2, Tuple[float, float]], radius: float) -> None:
        """
        Draw an (outline) circle
        """
    def clear(self, color: int = 255) -> None:
        """
        Clear the canvas using given color.
        """
    def complex_polygon(self, contours: list[list[Float2]]) -> None:
        """
        Draw a complex filled polygon that can consist of holes.
        """
    def copy(self) -> Canvas:
        """
        Make a copy of the self.
        """
    @typing.overload
    def draw(self, image: Image, top_left: Union[Float2, Int2, Tuple[float, float]] | None = None, center: Union[Float2, Int2, Tuple[float, float]] | None = None, size: Union[Float2, Int2, Tuple[float, float]] = ..., rot: float = 0) -> None:
        """
        Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.
        """
    @typing.overload
    def draw(self, drawable: Console, top_left: Union[Float2, Int2, Tuple[float, float]] = ..., size: Union[Float2, Int2, Tuple[float, float]] = ...) -> None:
        """
        Render a console. `top_left` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.

        To render a full screen console (scaling as needed):

        `console.render(screen, size=screen.size)`
        """
    def filled_circle(self, center: Union[Float2, Int2, Tuple[float, float]], radius: float) -> None:
        """
        Draw a filled circle.
        """
    def filled_rect(self, top_left: Union[Float2, Int2, Tuple[float, float]], size: Union[Float2, Int2, Tuple[float, float]]) -> None:
        """
        Draw a filled rectangle.
        """
    def flood_fill(self, pos: Union[Int2, Tuple[int, int]], color: int) -> None:
        """
        Flood fill starting from the given position with the specified color.
        """
    def flush(self) -> None:
        """
        Flush pixel operations
        """
    def get_pointer(self) -> Float2:
        """
        Get the xy coordinate of the mouse pointer (in canvas space).
        """
    @typing.overload
    def line(self, start: Union[Float2, Int2, Tuple[float, float]], end: Union[Float2, Int2, Tuple[float, float]]) -> None:
        """
        Draw a line between start and end.
        """
    @typing.overload
    def line(self, end: Union[Float2, Int2, Tuple[float, float]]) -> None:
        """
        Draw a line from the end of the last line to the given position.
        """
    def lines(self, points: list[Float2]) -> None:
        """
        Draw a line strip from all the given points.
        """
    def log_to(self, path: Union[os.PathLike[str], str]) -> None:
        """
        Log draw commands to this file
        """
    @typing.overload
    def plot(self, center: Union[Float2, Int2, Tuple[float, float]], color: int) -> None:
        """
        Draw a point.
        """
    @typing.overload
    def plot(self, points: typing.Any, colors: typing.Any) -> None:
        """
        Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.
        """
    def polygon(self, points: list[Float2], convex: bool = False) -> None:
        """
        Draw a filled polygon by stringing together the given points. If convex is `true` the polygon is rendered as a simple triangle fan, otherwise the polygon is split into triangles using the ear-clipping method.
        """
    def rect(self, top_left: Union[Float2, Int2, Tuple[float, float]], size: Union[Float2, Int2, Tuple[float, float]]) -> None:
        """
        Draw a rectangle.
        """
    @typing.overload
    def rounded_line(self, start: Union[Float2, Int2, Tuple[float, float]], rad0: float, end: Union[Float2, Int2, Tuple[float, float]], rad1: float) -> None:
        """
        Draw a line between start and end.
        """
    @typing.overload
    def rounded_line(self, end: Union[Float2, Int2, Tuple[float, float]], radius: float) -> None:
        """
        Draw a line from the end of the last line to the given position.
        """
    def set_pixel(self, pos: Union[Int2, Tuple[int, int]], color: int) -> None:
        """
        Write a pixel into the image.
        """
    def to_image(self) -> Image:
        """
        Create a new image from this canvas
        """
    @property
    def backface_culling(self) -> bool:
        """
        If true, backward facing polygons will not be rendered.
        """
    @backface_culling.setter
    def backface_culling(self, arg0: bool) -> None:
        ...
    @property
    def blend_mode(self) -> int:
        """
        Set the blend mode. Normally one of the constants `BLEND_ADD`, `BLEND_MULTIPLY` or `BLEND_NORMAL`.
        """
    @blend_mode.setter
    def blend_mode(self, arg1: int) -> None:
        ...
    @property
    def draw_color(self) -> int:
        """
        Set the draw color.
        """
    @draw_color.setter
    def draw_color(self, arg1: int) -> None:
        ...
    @property
    def line_width(self) -> float:
        """
        Set the line with in fractional pixels.
        """
    @line_width.setter
    def line_width(self, arg0: float) -> None:
        ...
    @property
    def offset(self) -> Float2:
        """
        The offset into a the source canvas this canvas was created from, if any.
        """
    @offset.setter
    def offset(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> None:
        ...
    @property
    def point_size(self) -> float:
        """
        Set the point size in fractional pixels.
        """
    @point_size.setter
    def point_size(self, arg0: float) -> None:
        ...
    @property
    def size(self) -> Float2:
        """
        The size of this canvas in pixels
        """
    @property
    def target_size(self) -> Float2:
        ...
class Console:
    """
    A console is a 2D grid of tiles that can be rendered.
    """
    @typing.overload
    def __init__(self, cols: int, rows: int, font_file: Union[os.PathLike[str], str] | None = None, tile_size: Union[Float2, Int2, Tuple[float, float]] = ..., font_size: int = -1) -> None:
        """
        Create a new Console holding `cols`*`rows` tiles.

        `font_file` is the file name of a TTF font to use as backing. If no font is given, the built in _Unscii_ font will be used.

        `tile_size` sets the size in pixels of each tile. If not given, it will be derived from the size of a character in the font with the provided `font_size`.
        """
    @typing.overload
    def __init__(self, cols: int, rows: int, tile_set: TileSet) -> None:
        """
        Create a new Console holding `cols`*`row` tiles. Use the provided `tile_set`.
        """
    def cancel_line(self) -> None:
        """
        Stop line edit mode.
        """
    def clear(self) -> None:
        """
        Clear the console.
        """
    def clear_area(self, x: int, y: int, w: int, h: int) -> None:
        """
        Clear the given rectangle, setting the current foreground and background colors.
        """
    def colorize_section(self, x: int, y: int, width: int) -> None:
        """
        Colorize the given area with the current foreground and background color, without changing the characters
        """
    def get(self, arg0: Union[Int2, Tuple[int, int]]) -> int:
        """
        Get tile at position
        """
    def get_font_image(self) -> Image:
        ...
    def get_image_for(self, tile: int) -> Image:
        """
        Get the image of a specific tile. Use to render the tile manually, or to copy another image into the tile;

        `console.get_image_for(1024).copy_from(some_tile_image)`.
        """
    def get_tiles(self) -> list[int]:
        """
        Get all the tiles and colors as an array of ints. Format is: `[tile0, fg0, bg0, tile1, fg1, bg1 ...]` etc.
        """
    def put(self, pos: Union[Int2, Tuple[int, int]], tile: int, fg: int | None = None, bg: int | None = None) -> None:
        """
        Put `tile` at given position, optionally setting a specific foreground and/or background color
        """
    def read_line(self) -> None:
        """
        Puts the console in line edit mode.

        A cursor will be shown and all text events will be captured by the console until `Enter` is pressed. At this point the entire line will be pushed as a `TextEvent`.
        """
    def set_color(self, fg: int, bg: int) -> None:
        """
        Set the default colors used when putting/writing to the console.
        """
    def set_device_no(self, devno: int) -> None:
        """
        Set the device number that will be reported for TextEvents from this console.
        """
    def set_line(self, text: str) -> None:
        """
        Change the edited line.
        """
    def set_readline_callback(self, callback: typing.Callable[[str, int], None]) -> None:
        """
        Sets a cllback that will be called when a line of text was entered by the user. Setting this will stop the normal TextEvent from being sent.
        """
    def set_tile_images(self, start_no: int, images: list[Image]) -> None:
        """
        Set images to use for a set of indexes, starting at `start_no`.
        """
    def set_tiles(self, tiles: list[int]) -> None:
        """
        Set tiles from an array of ints.
        """
    @typing.overload
    def write(self, tiles: list[str]) -> None:
        ...
    @typing.overload
    def write(self, text: str) -> None:
        """
        Write text to the console at the current cursor position and using the current colors. Will advance cursor position, and wrap if it passes the right border of the console.
        """
    @property
    def autoscroll(self) -> bool:
        """
        Should we scroll console upwards when writes pass bottom edge?
        """
    @autoscroll.setter
    def autoscroll(self, arg0: bool) -> None:
        ...
    @property
    def bg_color(self) -> int:
        """
        Background color.
        """
    @bg_color.setter
    def bg_color(self, arg0: int) -> None:
        ...
    @property
    def cursor_on(self) -> bool:
        """
        Determine if the cursor should be visible.
        """
    @cursor_on.setter
    def cursor_on(self, arg0: bool) -> None:
        ...
    @property
    def cursor_pos(self) -> Int2:
        """
        The current location of the cursor. This will be used when calling `write()`.
        """
    @cursor_pos.setter
    def cursor_pos(self, arg1: Union[Int2, Tuple[int, int]]) -> None:
        ...
    @property
    def fg_color(self) -> int:
        """
        Foreground color.
        """
    @fg_color.setter
    def fg_color(self, arg0: int) -> None:
        ...
    @property
    def grid_size(self) -> Int2:
        """
        Get number cols and rows.
        """
    @property
    def reading_line(self) -> bool:
        """
        True if console is in read_line mode at the moment.
        """
    @property
    def size(self) -> Int2:
        """
        Get size of consoles in pixels (tile_size * grid_size).
        """
    @property
    def tile_size(self) -> Int2:
        """
        Get size of a single tile.
        """
    @property
    def wrap_lines(self) -> bool:
        """
        Should we wrap when writing passing right edge?
        """
    @wrap_lines.setter
    def wrap_lines(self, arg0: bool) -> None:
        ...
class Float2:
    """
    Represents an floating point coordinate or size. Mostly behaves like a normal float when used in arithmetic operations.
    """
    ONE: typing.ClassVar[Float2]  # value = Float2(1.000000, 1.000000)
    ZERO: typing.ClassVar[Float2]  # value = Float2(0.000000, 0.000000)
    @staticmethod
    def from_angle(angle: float) -> Float2:
        """
        Rotates the X-axis (1,0) around `angle` clockwise and returns the result.
        """
    @typing.overload
    def __add__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __add__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __add__(self, arg0: float) -> Float2:
        ...
    def __copy__(self) -> Float2:
        ...
    def __deepcopy__(self, arg0: dict) -> Float2:
        ...
    def __eq__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> bool:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: float) -> Float2:
        ...
    def __ge__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> bool:
        ...
    def __getitem__(self, arg0: int) -> float:
        ...
    def __gt__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    @typing.overload
    def __init__(self, x: int = 0, y: int = 0) -> None:
        ...
    @typing.overload
    def __init__(self, x: int = 0, y: float = 0) -> None:
        ...
    @typing.overload
    def __init__(self, x: float = 0, y: int = 0) -> None:
        ...
    @typing.overload
    def __init__(self, x: float = 0, y: float = 0) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: tuple[float, float]) -> None:
        ...
    def __iter__(self) -> typing.Iterator[float]:
        ...
    def __le__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> bool:
        ...
    def __len__(self) -> int:
        ...
    def __lt__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> bool:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __mul__(self, arg0: float) -> Float2:
        ...
    def __ne__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    @typing.overload
    def __sub__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __sub__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __sub__(self, arg0: float) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> Float2:
        ...
    def angle(self) -> float:
        """
        Get the (counter-clockwise) angle between the vector and the X-axis (1,0).
        """
    def ceil(self) -> Float2:
        ...
    def clamp(self, low: Union[Float2, Int2, Tuple[float, float]], high: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        """
        Separately clamp the x and y component between the corresponding components in the given arguments.
        """
    def clip(self, low: Union[Float2, Int2, Tuple[float, float]], high: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        """
        Compare the point against the bounding box defined by low/high. Returns (0,0) if point is inside the box, or a negative or positive distance to the edge if outside.
        """
    def cossin(self) -> Float2:
        """
        Returns (cos(x), sin(y)).
        """
    def floor(self) -> Float2:
        ...
    def inside(self, arg0: Union[Float2, Int2, Tuple[float, float]], arg1: Union[Float2, Int2, Tuple[float, float]]) -> bool:
        ...
    def inside_polygon(self, points: list[Float2]) -> bool:
        """
        Check if the `point` is inside the polygon formed by `points`.
        """
    def mag(self) -> float:
        """
        Get magnitude (length) of vector
        """
    def mag2(self) -> float:
        """
        Get the squared magnitude
        """
    def norm(self) -> Float2:
        """
        Get the normalized vector.
        """
    def random(self) -> Float2:
        """
        Returns Float2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.
        """
    def round(self) -> Float2:
        ...
    def sign(self) -> Float2:
        ...
    def toi(self) -> Int2:
        """
        Convert a `Float2` to an `Int2`
        """
    def tween_from(self, value: Union[Float2, Int2, Tuple[float, float]], secs: float = 1.0, ease: typing.Callable[[float], float] = ...) -> Float2:
        """
        Animate this Float2 from `from` to its current value in `secs` seconds.
        """
    def tween_to(self, value: Union[Float2, Int2, Tuple[float, float]], secs: float = 1.0, ease: typing.Callable[[float], float] = ...) -> Float2:
        """
        Animate this Float2 so it reaches `to` in `secs` seconds.
        """
    def tween_velocity(self, speed: Union[Float2, Int2, Tuple[float, float]], duration: float = 0.0) -> Float2:
        """
        Move Vec2f with velocity `speed`.
        """
    @property
    def with_x0(self) -> Float2:
        ...
    @property
    def with_y0(self) -> Float2:
        ...
    @property
    def x(self) -> float:
        ...
    @property
    def xx(self) -> Float2:
        ...
    @property
    def y(self) -> float:
        ...
    @property
    def yx(self) -> Float2:
        ...
    @property
    def yy(self) -> Float2:
        ...
class Font:
    """
    Represents a TTF (Freetype) font that can be used to create text images.
    """
    UNSCII_FONT: typing.ClassVar[Font]  # value = <Font object>
    def __init__(self, font_file: str = '') -> None:
        """
        Create a font from a TTF file.
        """
    def make_image(self, text: str, size: int, color: int = 4294967295) -> Image:
        """
        Create an image containing the given text.
        """
    def text_size(self, text: str, size: int) -> Float2:
        """
        Return the size (bounding rectangle) of the given text.
        """
class Image(Canvas):
    """
    A (GPU Side) _image_, represented by a texture reference and 4 UV coordinates. Images works like arrays in the sense that it is cheap to create new views into images (using crop(), split() etc).
    """
    @typing.overload
    def __init__(self, width: int, height: int) -> None:
        """
        Create an empty image of the given size.
        """
    @typing.overload
    def __init__(self, size: Union[Float2, Int2, Tuple[float, float]]) -> None:
        """
        Create an empty image of the given size.
        """
    @typing.overload
    def __init__(self, width: int, pixels: list[int]) -> None:
        """
        Create an image from an array of 32-bit colors.
        """
    def copy_from(self, image: Image) -> None:
        """
        Render another image into this one.
        """
    def copy_to(self, image: Image) -> None:
        """
        Render this image into another.
        """
    def crop(self, top_left: Union[Float2, Int2, Tuple[float, float]] | None = None, size: Union[Float2, Int2, Tuple[float, float]] | None = None) -> Image:
        """
        Crop an image. Returns a view into the old image.
        """
    def set_texture_filter(self, min: bool, max: bool) -> None:
        """
        Set whether the texture should apply linear filtering.
        """
    @typing.overload
    def split(self, cols: int = -1, rows: int = -1, width: int = 8, height: int = 8) -> list[Image]:
        """
        Splits the image into as many _width_ * _height_ images as possible, first going left to right, then top to bottom.
        """
    @typing.overload
    def split(self, size: Union[Float2, Int2, Tuple[float, float]]) -> list[Image]:
        """
        Split the image into exactly size.x * size.y images.
        """
    def update(self, pixels: bytes) -> None:
        """
        Update the texture with a raw buffer that must fit the texture format.
        """
    @property
    def height(self) -> float:
        ...
    @property
    def pos(self) -> Float2:
        """
        The position of this image in its texture. Will normally be (0, 0) unless this image was split or cropped from another image.
        """
    @property
    def size(self) -> Float2:
        """
        Size of the image in (fractional) pixels.
        """
    @property
    def width(self) -> float:
        ...
class Int2:
    """
    Represents an integer coordinate or size. Mostly behaves like a normal int when used in arithmetic operations.
    """
    ONE: typing.ClassVar[Int2]  # value = Int2(1, 1)
    ZERO: typing.ClassVar[Int2]  # value = Int2(0, 0)
    @typing.overload
    def __add__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __add__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __add__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __add__(self, arg0: float) -> Float2:
        ...
    def __copy__(self) -> Int2:
        ...
    def __deepcopy__(self, arg0: dict) -> Int2:
        ...
    def __eq__(self, arg0: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: float) -> Float2:
        ...
    def __ge__(self, arg0: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    def __getitem__(self, arg0: int) -> int:
        ...
    def __gt__(self, arg0: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    def __hash__(self) -> int:
        ...
    @typing.overload
    def __init__(self, x: int = 0, y: int = 0) -> None:
        ...
    @typing.overload
    def __init__(self, x: int = 0, y: float = 0) -> None:
        ...
    @typing.overload
    def __init__(self, x: float = 0, y: int = 0) -> None:
        ...
    @typing.overload
    def __init__(self, x: float = 0, y: float = 0) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: tuple[int, int]) -> None:
        ...
    def __iter__(self) -> typing.Iterator[int]:
        ...
    def __le__(self, arg0: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    def __len__(self) -> int:
        ...
    def __lt__(self, arg0: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __mul__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __mul__(self, arg0: float) -> Float2:
        ...
    def __ne__(self, arg0: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    @typing.overload
    def __sub__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __sub__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __sub__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __sub__(self, arg0: float) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __truediv__(self, arg0: Union[Float2, Int2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> Float2:
        ...
    def clamp(self, low: Union[Int2, Tuple[int, int]], high: Union[Int2, Tuple[int, int]]) -> Int2:
        """
        Separately clamp the x and y component between the corresponding components in the given arguments.
        """
    def inside(self, arg0: Union[Int2, Tuple[int, int]], arg1: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    def random(self) -> Int2:
        """
        Returns Int2(rnd(x), rnd(y)) where rnd(n) returns a random number between 0 and n.
        """
    def sign(self) -> Int2:
        ...
    def tof(self) -> Float2:
        """
        Convert an `Int2` to a `Float2`
        """
    @property
    def with_x0(self) -> Int2:
        ...
    @property
    def with_y0(self) -> Int2:
        ...
    @property
    def x(self) -> int:
        ...
    @property
    def xx(self) -> Int2:
        ...
    @property
    def y(self) -> int:
        ...
    @property
    def yx(self) -> Int2:
        ...
    @property
    def yy(self) -> Int2:
        ...
class Screen(Canvas):
    """
    The main window. Currently there can be only one instance of this class.
    """
    def crop(self, top_left: Union[Float2, Int2, Tuple[float, float]] | None = None, size: Union[Float2, Int2, Tuple[float, float]] | None = None) -> Screen:
        """
        Crop the screen. Returns a screen reference that can be used to render to that part of the screen.
        """
    def set_as_target(self) -> None:
        ...
    def split(self, size: Union[Float2, Int2, Tuple[float, float]]) -> list[Screen]:
        """
        Split the screen into exactly size.x * size.y screen references that can be used as a render target for that part of the screen.
        """
    def swap(self) -> None:
        """
        Synchronize with the frame rate of the display and swap buffers so what you have drawn becomes visible. This is normally the last thing you do in your render loop.
        """
    @property
    def delta(self) -> float:
        """
        Time in seconds for last frame.
        """
    @property
    def fps(self) -> int:
        """
        Current FPS. Set to 0 to disable fixed FPS. Then use `seconds` or `delta` to sync your movement.
        """
    @fps.setter
    def fps(self, arg1: int) -> None:
        ...
    @property
    def frame_counter(self) -> int:
        ...
    @property
    def height(self) -> int:
        ...
    @property
    def refresh_rate(self) -> int:
        """
        Actual refresh rate of current monitor.
        """
    @property
    def seconds(self) -> float:
        """
        Total seconds elapsed since starting pix.
        """
    @property
    def size(self) -> Float2:
        """
        Size (in pixels) of screen.
        """
    @size.setter
    def size(self, arg1: Union[Float2, Int2, Tuple[float, float]]) -> None:
        ...
    @property
    def visible(self) -> bool:
        """
        Is the window visible?
        """
    @visible.setter
    def visible(self, arg1: bool) -> None:
        ...
    @property
    def width(self) -> int:
        ...
class TileSet:
    """
    A tileset is a texture split up into tiles for rendering. It is used by the `Console` class but can also be used directly.
    """
    @typing.overload
    def __init__(self, font_file: str, size: int = -1, tile_size: Union[Int2, Tuple[int, int]] = ...) -> None:
        """
        Create a TileSet from a ttf font with the given size. The tile size will be derived from the font size.
        """
    @typing.overload
    def __init__(self, font: Font, size: int = -1, tile_size: Union[Int2, Tuple[int, int]] = ...) -> None:
        """
        Create a TileSet from an existing font. The tile size will be derived from the font size.
        """
    @typing.overload
    def __init__(self, tile_size: Union[Float2, Int2, Tuple[float, float]]) -> None:
        """
        Create an empty tileset with the given tile size.
        """
    @typing.overload
    def get_image_for(self, tile: int) -> Image:
        """
        Get the image for a specific tile. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room.for the new tile in the tile texture.
        """
    @typing.overload
    def get_image_for(self, character: str) -> Image:
        """
        Get the image for a specific character. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.
        """
    def get_tileset_image(self) -> Image:
        """
        Get the entire tileset image. Typically used with `save_png()` to check generated tileset.
        """
    @typing.overload
    def render_text(self, screen: Screen, text: str, pos: Union[Float2, Int2, Tuple[float, float]], size: Union[Float2, Int2, Tuple[float, float]] = ...) -> None:
        """
        Render characters from the TileSet at given `pos` and given `size` (defaults to tile_size).
        """
    @typing.overload
    def render_text(self, screen: Screen, text: str, points: list[Float2]) -> None:
        """
        Render characters from the TileSet, each character using the next position from `points`, using the default tile size.
        """
    @property
    def tile_size(self) -> Int2:
        ...
def add_color(color0: int, color1: int) -> int:
    ...
def add_event_listener(func: typing.Callable[[typing.Any], bool], filter: int) -> int:
    """
    Add a function that can intercept events. The function should return _False_ if the event should not be propagated. Returns `id`.
    """
def all_events() -> list[typing.Any]:
    """
    Return the list of all pending events, and clear them.
    """
def allow_break(on: bool) -> None:
    """
    Allow Ctrl-C to break out of run loop
    """
def blend_color(color0: int, color1: int, t: float) -> int:
    """
    Blend two colors together. `t` should be between 0 and 1.
    """
def blend_colors(colors: list[int], t: float) -> int:
    """
    Get a color from a color range. Works similar to bilinear filtering of an 1D texture.
    """
def get_clipboard() -> str:
    """
    Get the current clipboard content as a string.
    """
def get_display() -> Screen:
    """
    Get the current display, if any.
    """
def get_pointer() -> Float2:
    """
    Get the xy coordinate of the mouse pointer (in screen space).
    """
def inside_polygon(points: list[Float2], point: Union[Float2, Int2, Tuple[float, float]]) -> bool:
    """
    Check if the `point` is inside the polygon formed by `points`.
    """
def is_pressed(key: int | str) -> bool:
    """
    Returns _True_ if the keyboard or mouse key is held down.
    """
def load_font(name: Union[os.PathLike[str], str], size: int = 0) -> Font:
    """
    Load a TTF font.
    """
def load_png(file_name: Union[os.PathLike[str], str]) -> Image:
    """
    Create an _Image_ from a png file on disk.
    """
@typing.overload
def open_display(width: int = -1, height: int = -1, full_screen: bool = False, visible: bool = True) -> Screen:
    """
    Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.
    Subsequent calls to this method returns the same screen instance, since you can only have one active display in pix.
    """
@typing.overload
def open_display(size: Union[Int2, Tuple[int, int]], full_screen: bool = False, visible: bool = True) -> Screen:
    """
    Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.
    Subsequent calls to this method returns the same screen instance, since you can only have one active display in pix.
    """
def post_event(event: typing.Any) -> None:
    """
    Post an event to pixpy, that will be returned by the next call to `all_events()`.
    """
def quit_loop() -> None:
    """
    Make run_loop() return False. Thread safe.
    """
def remove_event_listener(id: int) -> None:
    """
    Remove event listener via its `id`.
    """
def rgba(red: float, green: float, blue: float, alpha: float) -> int:
    """
    Combine four color float components into a 32-bit color.
    """
def run_every_frame(func: typing.Callable[[], bool]) -> None:
    """
    Add a function that should be run every frame. If the function returns false it will stop being called.
    """
def run_loop() -> bool:
    """
    Should be called first in your main rendering loop. Clears all pending events and all pressed keys. Returns _True_ as long as the application is running (the user has not closed the window or quit in some other way
    """
def save_png(image: Image, file_name: Union[os.PathLike[str], str]) -> None:
    """
    Save an _Image_ to disk
    """
def set_clipboard(text: str) -> None:
    """
    Set the clipboard content to the provided text.
    """
def set_keyboard_device(device: int) -> None:
    """
    Set the device number that keyboard events will originate from. This can be used to handle multiple readline calls from consoles.
    """
def update_tweens() -> None:
    """
    Manually update tweens
    """
def was_pressed(key: int | str) -> bool:
    """
    Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.
    """
def was_released(key: int | str) -> bool:
    """
    Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.
    """
BLEND_ADD: int = 50462721
BLEND_COPY: int = 65536
BLEND_MULTIPLY: int = 50724864
BLEND_NORMAL: int = 50463491
