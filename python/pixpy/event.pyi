from __future__ import annotations
import pixpy._pixpy
import typing
import pixpy
__all__ = ['AnyEvent', 'Click', 'Key', 'Move', 'NoEvent', 'Quit', 'Resize', 'Scroll', 'Text']
class Click:
    """
    Event sent when screen was clicked.
    """
    __match_args__: typing.ClassVar[tuple] = ('pos', 'buttons')
    def __init__(self, x: float = 0, y: float = 0, buttons: int = 0, mods: int = 0) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def buttons(self) -> int:
        ...
    @property
    def mods(self) -> int:
        ...
    @property
    def pos(self) -> pixpy.Float2:
        ...
    @property
    def x(self) -> float:
        ...
    @property
    def y(self) -> float:
        ...
class Key:
    """
    Event sent when key was pressed.
    """
    __match_args__: typing.ClassVar[tuple] = ('key')
    def __init__(self, key: int = 0, mods: int = 0, device: int = 0) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def device(self) -> int:
        ...
    @property
    def key(self) -> int:
        ...
    @property
    def mods(self) -> int:
        ...
class Move:
    """
    Event sent when mouse was moved.
    """
    __match_args__: typing.ClassVar[tuple] = ('x', 'y')
    def __init__(self, x: float = 0, y: float = 0, buttons: int = 0) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def buttons(self) -> int:
        ...
    @property
    def pos(self) -> pixpy.Float2:
        ...
    @property
    def x(self) -> float:
        ...
    @property
    def y(self) -> float:
        ...
class NoEvent:
    pass
class Quit:
    """
    Event sent when window/app wants to close.
    """
class Resize:
    """
    Event sent when the window was resized
    """
    @property
    def x(self) -> int:
        ...
    @property
    def y(self) -> int:
        ...
class Scroll:
    __match_args__: typing.ClassVar[tuple] = ('x', 'y')
    def __init__(self, x: float = 0, y: float = 0) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def x(self) -> float:
        ...
    @property
    def y(self) -> float:
        ...
class Text:
    """
    Event sent when text was input into the window.
    """
    __match_args__: typing.ClassVar[tuple] = ('text')
    def __init__(self, text: str = '', device: int = 0) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def device(self) -> int:
        ...
    @property
    def text(self) -> str:
        ...
AnyEvent = typing.Union[NoEvent, Key, Move, Click, Text, Resize, Quit, Scroll]
