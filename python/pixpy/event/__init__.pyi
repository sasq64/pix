from __future__ import annotations
import pixpy.event
import typing
import pixpy

__all__ = [
    "AnyEvent",
    "Click",
    "Key",
    "Move",
    "NoEvent",
    "Quit",
    "Resize",
    "Text"
]


class Click():
    def __repr__(self) -> str: ...
    @property
    def buttons(self) -> int:
        """
        :type: int
        """
    @property
    def mods(self) -> int:
        """
        :type: int
        """
    @property
    def pos(self) -> pixpy.Float2:
        """
        :type: pixpy.Float2
        """
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @property
    def y(self) -> float:
        """
        :type: float
        """
    __match_args__ = ('pos', 'buttons')
    pass
class Key():
    def __repr__(self) -> str: ...
    @property
    def key(self) -> int:
        """
        :type: int
        """
    @property
    def mods(self) -> int:
        """
        :type: int
        """
    __match_args__ = ('key',)
    pass
class Move():
    def __repr__(self) -> str: ...
    @property
    def buttons(self) -> int:
        """
        :type: int
        """
    @property
    def pos(self) -> pixpy.Float2:
        """
        :type: pixpy.Float2
        """
    @property
    def x(self) -> float:
        """
        :type: float
        """
    @property
    def y(self) -> float:
        """
        :type: float
        """
    __match_args__ = ('pos', 'buttons')
    pass
class NoEvent():
    pass
class Quit():
    pass
class Resize():
    @property
    def x(self) -> int:
        """
        :type: int
        """
    @property
    def y(self) -> int:
        """
        :type: int
        """
    pass
class Text():
    def __repr__(self) -> str: ...
    @property
    def text(self) -> str:
        """
        :type: str
        """
    __match_args__ = ('text',)
    pass
AnyEvent = typing.Union[NoEvent, Key, Move, Click, Text, Resize, Quit]
