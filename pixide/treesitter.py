from typing import Final
import pixpy as pix
from .editor import TextEdit, TextRange


class TreeSitter:
    def __init__(self, edit: TextEdit):
        self.colors: dict[str, int] = {
            "default": 1,
            "def": 3,
            "while": 3,
            "if": 3,
            "for": 3,
            "from": 3,
            "else": 3,
            "import": 3,
            "class": 3,
            "string": 8,
            # "string_content": 8,
            # "string_end": 8,
            "call.identifier": 2,
            "decorator": 4,
            "keyword_argument.identifier": 7,
            "call.attribute.identifier": 2,
            "function_definition.parameters.identifier": 6,
            "typed_parameter.type": 7,
            "type.identifier": 7,
            "integer": 8,
            "float": 8,
            "comment": 6,
            "identifier": 1,
            # "ERROR": 9,
        }

        self.palette: Final = [
            0x2A2A2E,
            0xB1B1B3,  # gray
            0xB98EFF,  # purple
            0xFF7DE9,  # pink
            0xFFFFB4,  # yellow
            0xE9F4FE,  # white
            0x86DE74,  # green string
            0x75BFFF,  # light blue
            0x6B89FF,  # dark blue
            0xFF2020,  # red
        ]

        self.treesitter: Final = pix.treesitter.TreeSitter()
        f = [(a, b) for a, b in self.colors.items()]
        self.treesitter.set_format(f)

        self.node: pix.treesitter.TSNode | None = None

        self.edit: TextEdit = edit

        self.edit.set_color(self.palette[1], self.palette[0])
        self.edit.set_palette(self.palette)

    def highlight(self):
        if not self.edit.mark_enabled:
            self.node = None
        self.treesitter.set_source_utf16(self.edit.get_codepoints())
        highlights = [
            TextRange(
                pix.Int2(col0 // 2, row0),
                pix.Int2(col1 // 2, row1),
                color if color >= 0 else 1,
            )
            for col0, row0, col1, row1, color in self.treesitter.get_highlights()
        ]
        self.edit.highlight(highlights)

    def select_parent_node(self):
        """
        Select node of cursor position, or if selection is already active, the parent node
        """
        if self.node is None:
            self.node = self.treesitter.find_node(self.edit.xpos * 2, self.edit.ypos)
        if self.node is not None:
            start = pix.Int2(self.node.start[0] / 2, self.node.start[1])
            end = pix.Int2(self.node.end[0] / 2, self.node.end[1])
            self.edit.select(start, end)
            self.node = self.node.parent
