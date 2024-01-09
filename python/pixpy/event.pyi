from __future__ import annotations
import pixpy._pixpy
import typing
import pixpy
__all__ = ['AnyEvent', 'Click', 'Key', 'Move', 'NoEvent', 'Quit', 'Resize', 'Text']
class Click:
    __match_args__: typing.ClassVar[tuple] = ('pos', 'buttons')
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
    __match_args__: typing.ClassVar[tuple] = ('key')
    def __repr__(self) -> str:
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
    __match_args__: typing.ClassVar[tuple] = ('pos', 'buttons')
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
class Text:
    """
    Event send when text was input into the window.
    """
    __match_args__: typing.ClassVar[tuple] = ('text')
    def __repr__(self) -> str:
        ...
    @property
    def text(self) -> str:
        ...
AnyEvent = typing.Union[NoEvent, Key, Move, Click, Text, Resize, Quit]
