from __future__ import annotations
__all__ = ['TreeSitter']
class TreeSitter:
    def __init__(self) -> None:
        """
        Create an empty treesitter object.
        """
    def get_highlights(self) -> list[tuple[int, int, int, int, int]]:
        ...
    def set_source(self, arg0: str) -> None:
        ...
