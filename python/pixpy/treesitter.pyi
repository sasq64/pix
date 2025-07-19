from __future__ import annotations
__all__ = ['TreeSitter']
class TreeSitter:
    def __init__(self) -> None:
        """
        Create an empty treesitter object.
        """
    def dump_tree(self) -> str:
        ...
    def get_highlights(self) -> list[tuple[int, int, int, int, int]]:
        ...
    def set_format(self, arg0: list[tuple[str, int]]) -> None:
        ...
    def set_source(self, arg0: str) -> None:
        ...
    def set_source_utf16(self, arg0: list[int]) -> None:
        ...
