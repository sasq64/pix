from __future__ import annotations
import typing
__all__ = ['BLACK', 'BLUE', 'BROWN', 'CYAN', 'Color', 'DARK_GREY', 'GREEN', 'GREY', 'LIGHT_BLUE', 'LIGHT_GREEN', 'LIGHT_GREY', 'LIGHT_RED', 'ORANGE', 'PURPLE', 'RED', 'TRANSP', 'WHITE', 'YELLOW']
class Color:
    @typing.overload
    def __init__(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        ...
    @typing.overload
    def __init__(self, rgba: int) -> None:
        ...
    @property
    def a(self) -> float:
        ...
    @property
    def b(self) -> float:
        ...
    @property
    def g(self) -> float:
        ...
    @property
    def r(self) -> float:
        ...
BLACK: int = 255
BLUE: int = 43775
BROWN: int = 1715732735
CYAN: int = 2868899327
DARK_GREY: int = 858993663
GREEN: int = 13391103
GREY: int = 2004318207
LIGHT_BLUE: int = 8912895
LIGHT_GREEN: int = 2868864767
LIGHT_GREY: int = 3132799743
LIGHT_RED: int = 4286019583
ORANGE: int = 3716633855
PURPLE: int = 3427060991
RED: int = 2264924415
TRANSP: int = 0
WHITE: int = 4294967295
YELLOW: int = 3991762943
