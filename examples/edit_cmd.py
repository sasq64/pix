from typing import override

Char = tuple[int, int]


class EditCmd:
    """
    Represent an undoable editor command
    """

    def __init__(self, join_prev: bool = False):
        self.join_prev = join_prev
        """If True, this command should be applied together with the previous command."""

    def apply(self, target: list[list[Char]]):
        """Apply the command to the provided list of lines"""
        pass

    def undo(self, target: list[list[Char]]) -> tuple[int, int] | None:
        """
        Undo the command from the provided list of lines.
        Returns recommended cursor position after undo, or None if undo
        had no effect.
        """
        return None


class EditSplit(EditCmd):
    """Split a line at the given column"""

    def __init__(self, line: int, col: int):
        super().__init__()
        self.line: int = line
        self.col: int = col

    @override
    def apply(self, target: list[list[Char]]):
        line = target[self.line]
        rest = line[self.col :]
        del line[self.col :]
        target.insert(self.line + 1, rest)

    @override
    def undo(self, target: list[list[Char]]):
        y = self.line
        x = len(target[y])
        target[y] = target[y] + target[y + 1]
        del target[y + 1]
        return (y, x)


class EditJoin(EditCmd):
    """Join this line with the next"""

    def __init__(self, line: int):
        super().__init__()
        self.line: int = line
        self.col: int = -1

    @override
    def apply(self, target: list[list[Char]]):
        y = self.line
        self.col = len(target[y])
        target[y] = target[y] + target[y + 1]
        del target[y + 1]

    @override
    def undo(self, target: list[list[Char]]):
        if self.col != -1:
            line = target[self.line]
            rest = line[self.col :]
            del line[self.col :]
            target.insert(self.line + 1, rest)
            return (self.line + 1, 0)
        return None


class EditDelete(EditCmd):
    """Delete `remove` characters from this line"""

    def __init__(self, line: int, col: int, remove: int):
        super().__init__()
        self.line: int = line
        self.col: int = col
        self.remove = remove
        self.removed: None | list[Char] = None

    @override
    def apply(self, target: list[list[Char]]):
        line = target[self.line]
        self.removed = line[self.col : self.col + self.remove]
        del line[self.col : self.col + self.remove]

    @override
    def undo(self, target: list[list[Char]]):
        if self.removed is not None:
            line = target[self.line]
            line[self.col : self.col] = self.removed
            return (self.line, self.col + len(self.removed))
        return None


class EditInsert(EditCmd):
    """Insert a list of dharacters into this line"""

    def __init__(self, line: int, col: int, add: list[Char]):
        super().__init__()
        self.line: int = line
        self.col: int = col
        self.add = add
        self.removed: None | list[Char] = None

    @override
    def apply(self, target: list[list[Char]]):
        line = target[self.line]
        line[self.col : self.col] = self.add

    @override
    def undo(self, target: list[list[Char]]):
        line = target[self.line]
        del line[self.col : self.col + len(self.add)]
        return (self.line, self.col)


class CmdStack:
    def __init__(self):
        self.stack : list[EditCmd] = []

    def apply(self, cmd: EditCmd, target: list[list[Char]]) -> EditCmd:
        """
        Apply the command to the target list of lines and remember it by
        pushing it onto a stack -- or, extend the previous command in the
        stack if appropriate.
        """
        if len(self.stack) > 0:
            prev = self.stack[-1]
            if isinstance(cmd, EditInsert):
                if not prev.join_prev and isinstance(prev, EditInsert):
                    if prev.line == cmd.line and prev.col == cmd.col - len(prev.add):
                        prev.undo(target)
                        prev.add += cmd.add
                        prev.apply(target)
                        return cmd
            elif isinstance(cmd, EditDelete):
                pass
        self.stack.append(cmd)
        cmd.apply(target)
        return cmd

    def undo(self, target: list[list[Char]]):
        """
        Undo the last command, or set of commands if the `join_prev` flag
        was set on the commands.
        """
        if len(self.stack) > 0:
            more = True
            while more:
                pos = self.stack[-1].undo(target)
                more = self.stack[-1].join_prev
                del self.stack[-1]
            return pos
        return None


