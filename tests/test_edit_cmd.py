import unittest
from pixide.edit_cmd import EditCmd, EditSplit, EditJoin, EditDelete, EditInsert

Char = tuple[int, int]


class TestEditCmd(unittest.TestCase):
    """Test cases for the EditCmd base class and all its subclasses"""

    def setUp(self):
        """Set up test data before each test"""
        # Create a simple test document with 3 lines
        self.test_doc = [
            [(0, ord("H")), (0, ord("e")), (0, ord("l")), (0, ord("l")), (0, ord("o"))],
            [(0, ord("W")), (0, ord("o")), (0, ord("r")), (0, ord("l")), (0, ord("d"))],
            [(0, ord("T")), (0, ord("e")), (0, ord("s")), (0, ord("t"))],
        ]

    def test_edit_cmd_base_class(self):
        """Test the base EditCmd class"""
        cmd = EditCmd()
        # Base class has basic apply/undo methods
        self.assertIsNone(cmd.apply([]))

    def test_edit_split_basic(self):
        """Test basic line splitting functionality"""
        doc = [self.test_doc[0].copy()]  # Copy to avoid modifying original

        # Split "Hello" at position 2 (after "He")
        cmd = EditSplit(0, 2)
        cmd.apply(doc)

        # Should result in two lines: "He" and "llo"
        expected = [
            [(0, ord("H")), (0, ord("e"))],
            [(0, ord("l")), (0, ord("l")), (0, ord("o"))],
        ]
        self.assertEqual(doc, expected)

    def test_edit_split_undo(self):
        """Test undoing a line split"""
        doc = [self.test_doc[0].copy()]

        # Split the line
        cmd = EditSplit(0, 2)
        cmd.apply(doc)

        # Undo the split
        cursor_pos = cmd.undo(doc)

        # Should restore original line
        self.assertEqual(doc, [self.test_doc[0]])
        self.assertEqual(cursor_pos, (0, 2))  # Cursor at split point

    def test_edit_split_at_beginning(self):
        """Test splitting at the beginning of a line"""
        doc = [self.test_doc[0].copy()]

        cmd = EditSplit(0, 0)
        cmd.apply(doc)

        expected = [
            [],
            [(0, ord("H")), (0, ord("e")), (0, ord("l")), (0, ord("l")), (0, ord("o"))],
        ]
        self.assertEqual(doc, expected)

    def test_edit_split_at_end(self):
        """Test splitting at the end of a line"""
        doc = [self.test_doc[0].copy()]

        cmd = EditSplit(0, 5)
        cmd.apply(doc)

        expected = [
            [(0, ord("H")), (0, ord("e")), (0, ord("l")), (0, ord("l")), (0, ord("o"))],
            [],
        ]
        self.assertEqual(doc, expected)

    def test_edit_join_basic(self):
        """Test basic line joining functionality"""
        doc: list[list[Char]] = [
            [(0, ord("H")), (0, ord("e")), (0, ord("l"))],
            [(0, ord("l")), (0, ord("o"))],
        ]

        cmd = EditJoin(0)
        cmd.apply(doc)

        expected: list[list[Char]] = [
            [(0, ord("H")), (0, ord("e")), (0, ord("l")), (0, ord("l")), (0, ord("o"))]
        ]
        self.assertEqual(doc, expected)

    def test_edit_join_undo(self):
        """Test undoing a line join"""
        original_doc: list[list[Char]] = [
            [(0, ord("H")), (0, ord("e")), (0, ord("l"))],
            [(0, ord("l")), (0, ord("o"))],
        ]
        doc: list[list[Char]] = [line.copy() for line in original_doc]

        cmd = EditJoin(0)
        cmd.apply(doc)
        cursor_pos = cmd.undo(doc)

        # Should restore original lines
        self.assertEqual(doc, original_doc)
        self.assertEqual(cursor_pos, (1, 0))  # Cursor at start of second line

    def test_edit_join_empty_lines(self):
        """Test joining empty lines"""
        doc = [[], []]

        cmd = EditJoin(0)
        cmd.apply(doc)

        expected = [[]]
        self.assertEqual(doc, expected)

    def test_edit_delete_basic(self):
        """Test basic character deletion"""
        doc = [self.test_doc[0].copy()]

        # Delete 2 characters starting at position 1
        cmd = EditDelete(0, 1, 2)
        cmd.apply(doc)

        expected = [[(0, ord("H")), (0, ord("l")), (0, ord("o"))]]
        self.assertEqual(doc, expected)

    def test_edit_delete_undo(self):
        """Test undoing character deletion"""
        doc = [self.test_doc[0].copy()]

        cmd = EditDelete(0, 1, 2)
        cmd.apply(doc)
        cursor_pos = cmd.undo(doc)

        # Should restore original line
        self.assertEqual(doc, [self.test_doc[0]])
        self.assertEqual(cursor_pos, (0, 3))  # Cursor after restored characters

    def test_edit_delete_undo_without_apply(self):
        """Test undoing deletion without applying first"""
        doc = [self.test_doc[0].copy()]

        cmd = EditDelete(0, 1, 2)
        # Don't apply the command, just try to undo
        cursor_pos = cmd.undo(doc)

        # Should return None when no characters were removed
        self.assertIsNone(cursor_pos)
        # Document should remain unchanged
        self.assertEqual(doc, [self.test_doc[0]])

    def test_edit_delete_at_beginning(self):
        """Test deleting characters at the beginning of a line"""
        doc = [self.test_doc[0].copy()]

        cmd = EditDelete(0, 0, 2)
        cmd.apply(doc)

        expected = [[(0, ord("l")), (0, ord("l")), (0, ord("o"))]]
        self.assertEqual(doc, expected)

    def test_edit_delete_at_end(self):
        """Test deleting characters at the end of a line"""
        doc = [self.test_doc[0].copy()]

        cmd = EditDelete(0, 3, 2)
        cmd.apply(doc)

        expected = [[(0, ord("H")), (0, ord("e")), (0, ord("l"))]]
        self.assertEqual(doc, expected)

    def test_edit_delete_entire_line(self):
        """Test deleting the entire line"""
        doc = [self.test_doc[0].copy()]

        cmd = EditDelete(0, 0, 5)
        cmd.apply(doc)

        expected = [[]]
        self.assertEqual(doc, expected)

    def test_edit_insert_basic(self):
        """Test basic character insertion"""
        doc = [self.test_doc[0].copy()]

        new_chars = [(0, ord("X")), (0, ord("Y"))]
        cmd = EditInsert(0, 2, new_chars)
        cmd.apply(doc)

        expected = [
            [
                (0, ord("H")),
                (0, ord("e")),
                (0, ord("X")),
                (0, ord("Y")),
                (0, ord("l")),
                (0, ord("l")),
                (0, ord("o")),
            ]
        ]
        self.assertEqual(doc, expected)

    def test_edit_insert_undo(self):
        """Test undoing character insertion"""
        doc = [self.test_doc[0].copy()]

        new_chars = [(0, ord("X")), (0, ord("Y"))]
        cmd = EditInsert(0, 2, new_chars)
        cmd.apply(doc)
        cursor_pos = cmd.undo(doc)

        # Should restore original line
        self.assertEqual(doc, [self.test_doc[0]])
        self.assertEqual(cursor_pos, (0, 2))  # Cursor at insertion point

    def test_edit_insert_at_beginning(self):
        """Test inserting characters at the beginning of a line"""
        doc = [self.test_doc[0].copy()]

        new_chars = [(0, ord("X")), (0, ord("Y"))]
        cmd = EditInsert(0, 0, new_chars)
        cmd.apply(doc)

        expected = [
            [
                (0, ord("X")),
                (0, ord("Y")),
                (0, ord("H")),
                (0, ord("e")),
                (0, ord("l")),
                (0, ord("l")),
                (0, ord("o")),
            ]
        ]
        self.assertEqual(doc, expected)

    def test_edit_insert_at_end(self):
        """Test inserting characters at the end of a line"""
        doc = [self.test_doc[0].copy()]

        new_chars = [(0, ord("X")), (0, ord("Y"))]
        cmd = EditInsert(0, 5, new_chars)
        cmd.apply(doc)

        expected = [
            [
                (0, ord("H")),
                (0, ord("e")),
                (0, ord("l")),
                (0, ord("l")),
                (0, ord("o")),
                (0, ord("X")),
                (0, ord("Y")),
            ]
        ]
        self.assertEqual(doc, expected)

    def test_edit_insert_empty(self):
        """Test inserting empty character list"""
        doc = [self.test_doc[0].copy()]

        cmd = EditInsert(0, 2, [])
        cmd.apply(doc)

        # Should not change the document
        self.assertEqual(doc, [self.test_doc[0]])

    def test_edit_insert_empty_undo(self):
        """Test undoing empty insertion"""
        doc = [self.test_doc[0].copy()]

        cmd = EditInsert(0, 2, [])
        cmd.apply(doc)
        cursor_pos = cmd.undo(doc)

        # Should not change the document
        self.assertEqual(doc, [self.test_doc[0]])
        self.assertEqual(cursor_pos, (0, 2))

    def test_multiple_operations(self):
        """Test multiple operations on the same document"""
        doc = [self.test_doc[0].copy()]

        # Insert characters
        insert_cmd = EditInsert(0, 2, [(0, ord("X")), (0, ord("Y"))])
        insert_cmd.apply(doc)

        # Delete some characters
        delete_cmd = EditDelete(0, 1, 2)
        delete_cmd.apply(doc)

        # Split the line
        split_cmd = EditSplit(0, 3)
        split_cmd.apply(doc)

        expected = [
            [(0, ord("H")), (0, ord("Y")), (0, ord("l"))],
            [(0, ord("l")), (0, ord("o"))],
        ]
        self.assertEqual(doc, expected)

    def test_undo_chain(self):
        """Test undoing multiple operations in reverse order"""
        doc = [self.test_doc[0].copy()]

        # Apply multiple operations
        insert_cmd = EditInsert(0, 2, [(0, ord("X")), (0, ord("Y"))])
        insert_cmd.apply(doc)

        delete_cmd = EditDelete(0, 1, 2)
        delete_cmd.apply(doc)

        split_cmd = EditSplit(0, 3)
        split_cmd.apply(doc)

        # Undo in reverse order
        split_cmd.undo(doc)
        delete_cmd.undo(doc)
        insert_cmd.undo(doc)

        # Should restore original document
        self.assertEqual(doc, [self.test_doc[0]])

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test with empty document
        empty_doc: list[list[Char]] = []

        # These should raise IndexError or behave appropriately
        with self.assertRaises(IndexError):
            cmd = EditSplit(0, 0)
            cmd.apply(empty_doc)

        with self.assertRaises(IndexError):
            cmd = EditJoin(0)
            cmd.apply(empty_doc)

        with self.assertRaises(IndexError):
            cmd = EditDelete(0, 0, 1)
            cmd.apply(empty_doc)

        with self.assertRaises(IndexError):
            cmd = EditInsert(0, 0, [(0, ord("X"))])
            cmd.apply(empty_doc)

    def test_cmd_stack_join_prev(self):
        """Test the CmdStack join_prev parameter functionality"""
        from pixide.edit_cmd import CmdStack, CombinedCmd
        
        doc = [self.test_doc[0].copy()]
        stack = CmdStack()
        
        # Apply two commands with join_prev=True for the second
        cmd1 = EditInsert(0, 0, [(0, ord("X"))])
        stack.apply(cmd1, doc)
        
        cmd2 = EditInsert(0, 1, [(0, ord("Y"))])
        stack.apply(cmd2, doc, join_prev=True)
        
        # The stack should have combined the commands
        self.assertEqual(len(stack.stack), 1)
        self.assertIsInstance(stack.stack[0], CombinedCmd)


if __name__ == "__main__":
    unittest.main()

