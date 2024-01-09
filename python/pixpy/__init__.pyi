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
__all__ = ['Console', 'Context', 'Float2', 'Font', 'Image', 'Int2', 'Screen', 'TileSet', 'all_events', 'color', 'event', 'get_display', 'get_pointer', 'is_pressed', 'key', 'load_font', 'load_png', 'open_display', 'rgba', 'run_loop', 'save_png', 'was_pressed']
class Console:
    def __init__(self, cols: int = 80, rows: int = 50, font_file: str = '', tile_size: Union[Float2, Tuple[float, float]] = ..., font_size: int = 16) -> None:
        """
        Create a new Console holding cols*row tiles. Optionally set a backing font. If `tile_size` is not provided it will be derived from the font size.
        """
    def cancel_line(self) -> None:
        """
        Stop line edit mode.
        """
    def clear(self) -> None:
        """
        Clear the console.
        """
    def get(self, arg0: Union[Int2, Tuple[int, int]]) -> int:
        """
        Get tile at position
        """
    def get_font_image(self) -> Image:
        ...
    def get_image_for(self, tile: int) -> Image:
        """
        Get the image of a specific tile. Use to render the tile manually, or to copy another image into the tile.
        """
    def get_tiles(self) -> list[int]:
        """
        Get all the tiles and colors as an array of ints. Format is: [tile0, fg0, bg0, tile1, fg1, bg1 ...] etc.
        """
    def put(self, pos: Union[Int2, Tuple[int, int]], tile: int, fg: int | None = None, bg: int | None = None) -> None:
        """
        Put tile at position, optionally setting a specific foreground and/or background color
        """
    def read_line(self) -> None:
        """
        Enter line edit mode.
        """
    def render(self, context: Context, pos: Union[Float2, Tuple[float, float]] = ..., size: Union[Float2, Tuple[float, float]] = ...) -> None:
        """
        Render the console to a context.
        """
    def set_color(self, fg: int, bg: int) -> None:
        """
        Set the default colors used when putting/writing to the console.
        """
    def set_line(self, text: str) -> None:
        """
        Change the edited line.
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
    def grid_size(self) -> Int2:
        """
        Get number cols and rows
        """
    @property
    def tile_size(self) -> Int2:
        """
        Get size of a single tile
        """
class Context:
    clip_size: Union[Int2, Tuple[int, int]]
    clip_top_left: Union[Int2, Tuple[int, int]]
    def __init__(self, size: Union[Float2, Tuple[float, float]] = ...) -> None:
        ...
    def circle(self, center: Union[Float2, Tuple[float, float]], radius: float) -> None:
        """
        Draw an (outline) circle
        """
    def clear(self, color: int = 255) -> None:
        """
        Clear the context using given color.
        """
    @typing.overload
    def draw(self, image: Image, top_left: Union[Float2, Tuple[float, float]] | None = None, center: Union[Float2, Tuple[float, float]] | None = None, size: Union[Float2, Tuple[float, float]] = ..., rot: float = 0) -> None:
        """
        Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.
        """
    @typing.overload
    def draw(self, drawable: Console, top_left: Union[Float2, Tuple[float, float]] = ..., size: Union[Float2, Tuple[float, float]] = ...) -> None:
        ...
    def filled_circle(self, center: Union[Float2, Tuple[float, float]], radius: float) -> None:
        """
        Draw a filled circle.
        """
    def filled_rect(self, top_left: Union[Float2, Tuple[float, float]], size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a filled rectangle.
        """
    def flush(self) -> None:
        """
        Flush pixel operations
        """
    @typing.overload
    def line(self, start: Union[Float2, Tuple[float, float]], end: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a line between start and end.
        """
    @typing.overload
    def line(self, end: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a line from the end of the last line to the given position.
        """
    @typing.overload
    def plot(self, center: Union[Float2, Tuple[float, float]], color: int) -> None:
        """
        Draw a point.
        """
    @typing.overload
    def plot(self, points: typing.Any, colors: typing.Any) -> None:
        """
        Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.
        """
    def polygon(self, points: list[Float2]) -> None:
        """
        Draw a convex polygon.
        """
    def rect(self, top_left: Union[Float2, Tuple[float, float]], size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a rectangle.
        """
    def set_pixel(self, pos: Union[Int2, Tuple[int, int]], color: int) -> None:
        """
        Write a pixel into the image.
        """
    @property
    def context(self) -> Context:
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
    def line_width(self, arg1: float) -> None:
        ...
    @property
    def point_size(self) -> float:
        """
        Set the point size in fractional pixels.
        """
    @point_size.setter
    def point_size(self, arg1: float) -> None:
        ...
    @property
    def size(self) -> Float2:
        ...
    @property
    def target_size(self) -> Float2:
        ...
class Float2:
    """
    Represents an floating pont coordinate or size
    """
    ONE: typing.ClassVar[Float2]  # value = Float2(1.000000, 1.000000)
    ZERO: typing.ClassVar[Float2]  # value = Float2(0.000000, 0.000000)
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def from_angle(arg0: float) -> Float2:
        """
        From angle
        """
    @typing.overload
    def __add__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __add__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __add__(self, arg0: float) -> Float2:
        ...
    def __eq__(self, arg0: Union[Float2, Tuple[float, float]]) -> bool:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: float) -> Float2:
        ...
    def __getitem__(self, arg0: int) -> float:
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
    def __len__(self) -> int:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __mul__(self, arg0: float) -> Float2:
        ...
    def __ne__(self, arg0: Union[Float2, Tuple[float, float]]) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    @typing.overload
    def __sub__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __sub__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __sub__(self, arg0: float) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: Union[Int2, Tuple[int, int]]) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> Float2:
        ...
    def angle(self) -> float:
        """
        Get the angle between the vector and (1,0).
        """
    def clamp(self, low: Union[Float2, Tuple[float, float]], high: Union[Float2, Tuple[float, float]]) -> Float2:
        """
        Separately clamp the x and y component between the corresponding components in the given arguments.
        """
    def clip(self, low: Union[Float2, Tuple[float, float]], high: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    def cossin(self) -> Float2:
        ...
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
        ...
    def sign(self) -> Float2:
        ...
    def toi(self) -> Int2:
        """
        Convert a `Float2` to an `Int2`
        """
    @property
    def x(self) -> float:
        ...
    @property
    def y(self) -> float:
        ...
class Font:
    UNSCII_FONT: typing.ClassVar[Font]  # value = <Font object>
    def make_image(self, text: str, size: int, color: int = 4294967295) -> Image:
        """
        Create an image containing the given text.
        """
class Image:
    clip_size: Union[Int2, Tuple[int, int]]
    clip_top_left: Union[Int2, Tuple[int, int]]
    @typing.overload
    def __init__(self, width: int, height: int) -> None:
        """
        Create an empty image of the given size.
        """
    @typing.overload
    def __init__(self, size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Create an empty image of the given size.
        """
    @typing.overload
    def __init__(self, width: int, pixels: list[int]) -> None:
        """
        Create an image from an array of 32-bit colors.
        """
    def circle(self, center: Union[Float2, Tuple[float, float]], radius: float) -> None:
        """
        Draw an (outline) circle
        """
    def clear(self, color: int = 255) -> None:
        """
        Clear the context using given color.
        """
    def copy_from(self, image: Image) -> None:
        """
        Render one image into another.
        """
    def copy_to(self, image: Image) -> None:
        """
        Render one image into another.
        """
    def crop(self, top_left: Union[Float2, Tuple[float, float]] | None = None, size: Union[Float2, Tuple[float, float]] | None = None) -> Image:
        """
        Crop an image. Returns a view into the old image.
        """
    @typing.overload
    def draw(self, image: Image, top_left: Union[Float2, Tuple[float, float]] | None = None, center: Union[Float2, Tuple[float, float]] | None = None, size: Union[Float2, Tuple[float, float]] = ..., rot: float = 0) -> None:
        """
        Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.
        """
    @typing.overload
    def draw(self, drawable: Console, top_left: Union[Float2, Tuple[float, float]] = ..., size: Union[Float2, Tuple[float, float]] = ...) -> None:
        ...
    def filled_circle(self, center: Union[Float2, Tuple[float, float]], radius: float) -> None:
        """
        Draw a filled circle.
        """
    def filled_rect(self, top_left: Union[Float2, Tuple[float, float]], size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a filled rectangle.
        """
    def flush(self) -> None:
        """
        Flush pixel operations
        """
    @typing.overload
    def line(self, start: Union[Float2, Tuple[float, float]], end: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a line between start and end.
        """
    @typing.overload
    def line(self, end: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a line from the end of the last line to the given position.
        """
    @typing.overload
    def plot(self, center: Union[Float2, Tuple[float, float]], color: int) -> None:
        """
        Draw a point.
        """
    @typing.overload
    def plot(self, points: typing.Any, colors: typing.Any) -> None:
        """
        Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.
        """
    def polygon(self, points: list[Float2]) -> None:
        """
        Draw a convex polygon.
        """
    def rect(self, top_left: Union[Float2, Tuple[float, float]], size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a rectangle.
        """
    def set_pixel(self, pos: Union[Int2, Tuple[int, int]], color: int) -> None:
        """
        Write a pixel into the image.
        """
    @typing.overload
    def split(self, cols: int = -1, rows: int = -1, width: int = 8, height: int = 8) -> list[Image]:
        """
        Splits the image into as many _width_ * _height_ images as possible, first going left to right, then top to bottom.
        """
    @typing.overload
    def split(self, size: Union[Float2, Tuple[float, float]]) -> list[Image]:
        ...
    @property
    def context(self) -> Context:
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
    def height(self) -> float:
        ...
    @property
    def line_width(self) -> float:
        """
        Set the line with in fractional pixels.
        """
    @line_width.setter
    def line_width(self, arg1: float) -> None:
        ...
    @property
    def point_size(self) -> float:
        """
        Set the point size in fractional pixels.
        """
    @point_size.setter
    def point_size(self, arg1: float) -> None:
        ...
    @property
    def pos(self) -> Float2:
        """
        The position of this image in its texture. Will normally be (0, 0) unless this image was split or cropped from another image.
        """
    @property
    def size(self) -> Float2:
        ...
    @property
    def target_size(self) -> Float2:
        ...
    @property
    def width(self) -> float:
        ...
class Int2:
    """
    Represents an integer coordinate or size
    """
    ONE: typing.ClassVar[Int2]  # value = Int2(1, 1)
    ZERO: typing.ClassVar[Int2]  # value = Int2(0, 0)
    __hash__: typing.ClassVar[None] = None
    @typing.overload
    def __add__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __add__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __add__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __add__(self, arg0: float) -> Float2:
        ...
    def __eq__(self, arg0: Union[Int2, Tuple[int, int]]) -> bool:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __floordiv__(self, arg0: float) -> Float2:
        ...
    def __getitem__(self, arg0: int) -> int:
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
    def __len__(self) -> int:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    @typing.overload
    def __mul__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
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
    def __sub__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
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
    def __truediv__(self, arg0: Union[Float2, Tuple[float, float]]) -> Float2:
        ...
    @typing.overload
    def __truediv__(self, arg0: int) -> Int2:
        ...
    @typing.overload
    def __truediv__(self, arg0: float) -> Float2:
        ...
    def clamp(self, low: Union[Int2, Tuple[int, int]], high: Union[Int2, Tuple[int, int]]) -> Int2:
        ...
    def random(self) -> Int2:
        ...
    def sign(self) -> Int2:
        ...
    def tof(self: Union[Float2, Tuple[float, float]]) -> Float2:
        """
        Convert a `Int2` to an `Float2`. Convenience function, since it converts automatically.
        """
    @property
    def x(self) -> int:
        ...
    @property
    def y(self) -> int:
        ...
class Screen:
    clip_size: Union[Int2, Tuple[int, int]]
    clip_top_left: Union[Int2, Tuple[int, int]]
    fps: int
    def circle(self, center: Union[Float2, Tuple[float, float]], radius: float) -> None:
        """
        Draw an (outline) circle
        """
    def clear(self, color: int = 255) -> None:
        """
        Clear the context using given color.
        """
    @typing.overload
    def draw(self, image: Image, top_left: Union[Float2, Tuple[float, float]] | None = None, center: Union[Float2, Tuple[float, float]] | None = None, size: Union[Float2, Tuple[float, float]] = ..., rot: float = 0) -> None:
        """
        Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.
        """
    @typing.overload
    def draw(self, drawable: Console, top_left: Union[Float2, Tuple[float, float]] = ..., size: Union[Float2, Tuple[float, float]] = ...) -> None:
        ...
    def filled_circle(self, center: Union[Float2, Tuple[float, float]], radius: float) -> None:
        """
        Draw a filled circle.
        """
    def filled_rect(self, top_left: Union[Float2, Tuple[float, float]], size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a filled rectangle.
        """
    def flush(self) -> None:
        """
        Flush pixel operations
        """
    @typing.overload
    def line(self, start: Union[Float2, Tuple[float, float]], end: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a line between start and end.
        """
    @typing.overload
    def line(self, end: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a line from the end of the last line to the given position.
        """
    @typing.overload
    def plot(self, center: Union[Float2, Tuple[float, float]], color: int) -> None:
        """
        Draw a point.
        """
    @typing.overload
    def plot(self, points: typing.Any, colors: typing.Any) -> None:
        """
        Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.
        """
    def polygon(self, points: list[Float2]) -> None:
        """
        Draw a convex polygon.
        """
    def rect(self, top_left: Union[Float2, Tuple[float, float]], size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Draw a rectangle.
        """
    def set_as_target(self) -> None:
        ...
    def set_pixel(self, pos: Union[Int2, Tuple[int, int]], color: int) -> None:
        """
        Write a pixel into the image.
        """
    def swap(self) -> None:
        """
        Synchronize with the frame rate of the display and swap buffers. This is normally the last thing you do in your render loop.
        """
    @property
    def context(self) -> Context:
        ...
    @property
    def delta(self) -> float:
        """
        Time in seconds for last frame.
        """
    @property
    def draw_color(self) -> int:
        """
        Set the draw color.
        """
    @draw_color.setter
    def draw_color(self, arg1: int) -> None:
        ...
    @property
    def frame_counter(self) -> int:
        ...
    @property
    def height(self) -> int:
        ...
    @property
    def line_width(self) -> float:
        """
        Set the line with in fractional pixels.
        """
    @line_width.setter
    def line_width(self, arg1: float) -> None:
        ...
    @property
    def point_size(self) -> float:
        """
        Set the point size in fractional pixels.
        """
    @point_size.setter
    def point_size(self, arg1: float) -> None:
        ...
    @property
    def seconds(self) -> float:
        """
        Total seconds elapsed.
        """
    @property
    def size(self) -> Float2:
        ...
    @property
    def target_size(self) -> Float2:
        ...
    @property
    def width(self) -> int:
        ...
class TileSet:
    """
    A tileset is a texture split up into tiles for rendering.
    """
    @typing.overload
    def __init__(self, font_file: str, size: int) -> None:
        """
        Create a TileSet from a ttf font with the given size. The tile size will be derived from the font size.
        """
    @typing.overload
    def __init__(self, tile_size: Union[Float2, Tuple[float, float]]) -> None:
        """
        Create a tileset with the given tile size.
        """
    def get_image_for(self, arg0: str) -> Image:
        """
        Get the image for a specific tile. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.
        """
def all_events() -> list[event.NoEvent | event.Key | event.Move | event.Click | event.Text | event.Resize | event.Quit]:
    """
    Return a list of all pending events.
    """
def get_display() -> Screen:
    ...
def get_pointer() -> Float2:
    """
    Get the xy coordinate of the mouse pointer (in screen space).
    """
def is_pressed(key: int | str) -> bool:
    """
    Returns _True_ if the keyboard or mouse key is held down.
    """
def load_font(name: str, size: int = 0) -> Font:
    """
    Load a TTF font
    """
def load_png(file_name: str) -> Image:
    """
    Create an _Image_ from a png file on disk.
    """
@typing.overload
def open_display(width: int = -1, height: int = -1, full_screen: bool = False) -> Screen:
    """
    Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.
    """
@typing.overload
def open_display(size: Union[Int2, Tuple[int, int]], full_screen: bool = False) -> Screen:
    """
    Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.
    """
def rgba(red: float, green: float, blue: float, alpha: float) -> int:
    """
    Combine four color components into a color.
    """
def run_loop() -> bool:
    """
    Should be called first in your main rendering loop. Clears all pending events and all pressed keys. Returns _True_ as long as the application is running (the user has not closed the window or quit in some other way
    """
def save_png(image: Image, file_name: str) -> None:
    """
    Save an _Image_ to disk
    """
def was_pressed(key: int | str) -> bool:
    """
    Returns _True_ if the keyboard or mouse key was pressed this loop. `run_loop()` refreshes these states.
    """
