
import pixpy as pix
import math
from typing import Callable, Generator, Protocol, Self, TypeVar

class Ease:
    @staticmethod
    def in_back(t: float) -> float:
        s = 1.70158
        return (s+1)*t*t*t - s*t*t

    @staticmethod
    def out_back(t: float) -> float:
        s = 1.70158
        t -= 1
        return (t*t*((s+1)*t + s) + 1)

    @staticmethod
    def smooth_step(t: float) -> float:
        return t*t*(3-2*t)

    @staticmethod
    def linear(t: float) -> float:
        return t

    @staticmethod
    def in_sine(t: float) -> float:
        return 1 - math.cos(t * (math.pi/2))

    @staticmethod
    def out_sine(t: float) -> float:
        return math.sin(t * (math.pi/2))

    @staticmethod
    def in_out_sine(t: float) -> float:
        return -0.5 * (math.cos(math.pi*t) - 1)

    @staticmethod
    def out_bounce(t: float) -> float:
        n1 = 7.5625
        d1 = 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= (1.5 / d1)
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= (2.25 / d1)
            return n1 * t * t + 0.9375
        else:
            t -= (2.65 / d1)
            return n1 * t * t + 0.984375

    @staticmethod
    def in_out_bounce(t: float) -> float:
        return (1 - Ease.out_bounce(1 - 2 * t)) / 2 if t < 0.5 else (1 + Ease.out_bounce(2 * t - 1)) / 2

    @staticmethod
    def in_bounce(t: float) -> float:
        return 1 - Ease.out_bounce(1-t)

    @staticmethod
    def in_cubic(t: float) -> float:
        return t*t*t

    @staticmethod
    def out_cubic(t: float) -> float:
        return 1 - (1-t)**3

    @staticmethod
    def in_out_cubic(t: float) -> float:
        return 4*t*t*t if t < 0.5 else 1 - ((-2*t+2)**3)/2

    @staticmethod
    def out_in_cubic(t: float) -> float:
        if t < 0.5:
            return Ease.out_cubic(t * 2) * 0.5
        else:
            return Ease.in_cubic(t * 2 - 1) * 0.5 + 0.5

    @staticmethod
    def in_circ(t: float) -> float:
        return 1 - math.sqrt(1 - t*t)

    @staticmethod
    def out_circ(t: float) -> float:
        return math.sqrt(1 - (t-1)*(t-1))

    @staticmethod
    def in_out_circ(t: float) -> float:
        return (1 - math.sqrt(1 - (2*t)**2)) / 2 if t< 0.5 else (math.sqrt(1 - (-2 * t + 2)**2) + 1) / 2

    @staticmethod
    def sine(t: float) -> float:
        return (math.sin(t * (math.pi*2) - math.pi/2) + 1.0)/2.0

    @staticmethod
    def in_elastic(t: float) -> float:
        c4 = (2 * math.pi) / 3
        if t == 0 or t == 1:
            return t
        return -2**(10 * t - 10) * math.sin((t * 10 - 10.75) * c4)

    @staticmethod
    def out_elastic(t: float) -> float:
        c4 = (2 * math.pi) / 3
        t = 2**(-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1
        return t

    @staticmethod
    def in_out_elastic(t: float) -> float:
        c5 = (2 * math.pi) / 4.5
        if t== 0 or t == 1:
            return t
        return -(2**(20 * t - 10) * math.sin((20 * t - 11.125) * c5)) / 2 if t < 0.5 else (2**(-20 * t + 10) * math.sin((20 * t - 11.125) * c5)) / 2 + 1

    @staticmethod
    def in_quint(t: float) -> float:
        return t ** 5

    @staticmethod
    def out_quint(t: float) -> float:
        t = t - 1
        return t ** 5 + 1

    @staticmethod
    def in_out_quint(t: float) -> float:
        t *= 2
        if t < 1:
            return 0.5 * t ** 5
        else:
            t -= 2
            return 0.5 * (t ** 5 + 2)

    @staticmethod
    def out_in_quint(t: float) -> float:
        if t < 0.5:
            return Ease.out_quint(t * 2) * 0.5
        else:
            return Ease.in_quint(t * 2 - 1) * 0.5 + 0.5

class Tweenable(Protocol):
    def __sub__(self, arg0: Self, /) -> Self: ...
    def __add__(self, arg0: Self, /) -> Self: ...
    def __mul__(self, arg0: float, /) -> Self: ...

T = TypeVar('T', bound=Tweenable)

def tween(start: T, stop: T, steps: int, ease: Callable[[float], float] = Ease.out_sine) -> Generator[T, None, None]:
    x = start
    for i in range(steps):
        x = (stop - start) * ease(i / steps) + start
        yield x
    while True:
        yield x


tween(pix.Float2(1,0), pix.Float2(1,1), 3)
tween(2.0, 3.0, 2)