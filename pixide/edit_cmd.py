from typing import override

Char = tuple[int, int]

Pos = tuple[int, int] | None


class EditCmd:
    """
    Represent an undoable editor command
    """

    def apply(self, _target: list[list[Char]]) -> Pos:
        """Apply the command to the provided list of lines"""
        pass

    def undo(self, _target: list[list[Char]]) -> Pos:
        """
        Undo the command from the provided list of lines.
        Returns recommended cursor position after undo, or None if undo
        had no effect.
        """
        return None


class CombinedCmd(EditCmd):
    """Combines several edit commands to be applied and undone at once"""

    def __init__(self, commands: list[EditCmd]):
        self.commands = commands

    @override
    def apply(self, target: list[list[Char]]) -> Pos:
        pos: Pos = None
        for cmd in self.commands:
            pos = cmd.apply(target)
        return pos

    @override
    def undo(self, target: list[list[Char]]) -> Pos:
        pos: Pos = None
        for cmd in reversed(self.commands):
            pos = cmd.undo(target)
        return pos


class EditSplit(EditCmd):
    """Split a line at the given column"""

    def __init__(self, line: int, col: int):
        self.line: int = line
        self.col: int = col

    @override
    def apply(self, target: list[list[Char]]) -> Pos:
        line = target[self.line]
        rest = line[self.col :]
        del line[self.col :]
        target.insert(self.line + 1, rest)
        return (self.line, self.col)

    @override
    def undo(self, target: list[list[Char]]) -> Pos:
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
        return (self.line, self.col)

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
        return (self.line, self.col)

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
        return (self.line, self.col + len(self.add))

    @override
    def undo(self, target: list[list[Char]]):
        line = target[self.line]
        del line[self.col : self.col + len(self.add)]
        return (self.line, self.col)


class CmdStack:
    """
    Holds a stack of edit operations that can be undone and redone.
    """

    def __init__(self):
        self.stack: list[EditCmd] = []
        self.redo_stack: list[EditCmd] = []

    def apply(
        self, cmd: EditCmd, target: list[list[Char]], join_prev: bool = False
    ) -> EditCmd:
        """
        Apply the command to the target list of lines and remember it by
        pushing it onto a stack -- or, extend the previous command in the
        stack if appropriate, by undoing, modifying and redoing the previous
        command.
        if `join_prev` is true, join this command with the previous by creating
        a CombineCmd that holds both.
        """
        self.redo_stack.clear()
        if len(self.stack) > 0:

            if join_prev:
                prev = self.stack.pop()
                self.stack.append(CombinedCmd([prev, cmd]))
                cmd.apply(target)
                return cmd

            prev = self.stack[-1]
            if isinstance(cmd, EditInsert):
                if isinstance(prev, EditInsert):
                    if prev.line == cmd.line and prev.col == cmd.col - len(prev.add):
                        prev.undo(target)
                        prev.add += cmd.add
                        prev.apply(target)
                        return cmd
            elif isinstance(cmd, EditDelete):
                if isinstance(prev, EditDelete):
                    if prev.line == cmd.line and prev.col == cmd.col + 1:
                        prev.undo(target)
                        prev.remove += 1
                        prev.col -= 1
                        prev.apply(target)
                        return cmd
        self.stack.append(cmd)
        cmd.apply(target)
        return cmd

    def undo(self, target: list[list[Char]]) -> Pos:
        """Undo the last command, if any."""

        if len(self.stack) > 0:
            pos = self.stack[-1].undo(target)
            self.redo_stack.append(self.stack[-1])
            del self.stack[-1]
            return pos
        return None

    def redo(self, target: list[list[Char]]) -> Pos:
        """Redo the undo command, if any."""

        if len(self.redo_stack) > 0:
            last = self.redo_stack[-1]
            pos = last.apply(target)
            self.stack.append(last)
            del self.redo_stack[-1]
            return pos
        return None
