#!/usr/bin/env python3
"""Test for TextEdit from examples/editor.py"""

import sys
from typing import override
import unittest
from unittest.mock import Mock
from pathlib import Path
from pixpy import Int2

# Import from pixide module
from pixide.editor import TextEdit


class TestEditor(unittest.TestCase):
    """Test cases for the Editor"""

    def __init__(self, methodName: str = "runTest"):
        super(TestEditor, self).__init__(methodName)
        self.mock_console: Mock = Mock()
        self.text_edit: TextEdit

    @override
    def setUp(self):
        # Create a mock Console with all required attributes and methods
        mock_console = Mock()
        mock_console.grid_size = Int2(80, 24)
        mock_console.tile_size = Int2(8, 16)
        mock_console.size = Int2(80, 24)
        mock_console.cursor_on = True
        mock_console.wrapping = False
        mock_console.cursor_pos = Int2(0, 0)

        # Mock the methods that are called
        mock_console.set_color = Mock()
        mock_console.clear = Mock()
        mock_console.put = Mock()
        self.mock_console = mock_console

        # Create TextEdit instance
        self.text_edit = TextEdit(mock_console)

    def test_cut(self):
        """Test TextEdit.render() with a mocked Console"""

        self.text_edit.set_text("Hello World\nSecond line\nThird line")
        self.text_edit.select(Int2(7, 0), Int2(3, 2))
        cut_data = self.text_edit.cut()
        print("CUT TEXT:" + self.text_edit.get_text(cut_data))
        result = self.text_edit.get_text()
        self.assertEqual(result, "Hello Wrd line")
        print(result)

    def test_paste_single_line(self):
        """Test paste with single line content"""
        self.text_edit.set_text("Hello World")
        self.text_edit.goto(6, 0)  # Position cursor after "Hello "

        # Create paste data (list of character lists)
        paste_data = [[(ord("X"), 1), (ord("Y"), 1), (ord("Z"), 1)]]
        self.text_edit.paste(paste_data)

        result = self.text_edit.get_text()
        self.assertEqual(result, "Hello XYZWorld")
        self.assertEqual(self.text_edit.cursor_col, 9)  # Cursor after pasted content
        self.assertEqual(self.text_edit.cursor_line, 0)
        print("✓ Single line paste test passed")

    def test_paste_multi_line(self):
        """Test paste with multi-line content"""
        self.text_edit.set_text("Hello World")
        self.text_edit.goto(6, 0)  # Position cursor after "Hello "

        # Create multi-line paste data
        paste_data = [
            [(ord("F"), 1), (ord("i"), 1), (ord("r"), 1), (ord("s"), 1), (ord("t"), 1)],
            [
                (ord("S"), 1),
                (ord("e"), 1),
                (ord("c"), 1),
                (ord("o"), 1),
                (ord("n"), 1),
                (ord("d"), 1),
            ],
            [(ord("T"), 1), (ord("h"), 1), (ord("i"), 1), (ord("r"), 1), (ord("d"), 1)],
        ]
        self.text_edit.paste(paste_data)

        result = self.text_edit.get_text()
        expected = "Hello First\nSecond\nThirdWorld"
        self.assertEqual(result, expected)
        self.assertEqual(self.text_edit.cursor_col, 5)  # Cursor after "Third"
        self.assertEqual(self.text_edit.cursor_line, 2)  # On third line
        print("✓ Multi-line paste test passed")

    def test_cut_and_paste_roundtrip(self):
        """Test that cut and paste work together correctly"""
        original_text = "Hello World\nSecond line\nThird line"
        self.text_edit.set_text(original_text)

        # Select text from "World" to "Second"
        self.text_edit.select(Int2(6, 0), Int2(6, 1))
        cut_data = self.text_edit.cut()

        # Verify cut worked
        after_cut = self.text_edit.get_text()
        self.assertEqual(after_cut, "Hello  line\nThird line")

        # Move cursor to end and paste back
        self.text_edit.goto(4, 1)  # End of "line"
        self.text_edit.paste(cut_data)

        # Should restore something close to original (minus exact formatting)
        result = self.text_edit.get_text()
        # The paste should insert the cut content
        self.assertTrue("World" in result)
        self.assertTrue("Second" in result)
        print(f"✓ Cut and paste roundtrip test passed: {result}")

    def test_paste_empty_content(self):
        """Test paste with empty content"""
        self.text_edit.set_text("Hello World")
        original_text = self.text_edit.get_text()

        # Paste empty content
        self.text_edit.paste([])

        # Text should remain unchanged
        result = self.text_edit.get_text()
        self.assertEqual(result, original_text)
        print("✓ Empty paste test passed")

    def test_render(self):
        """Test TextEdit.render() with a mocked Console"""
        self.text_edit.set_text("Hello World\nSecond line\nThird line")

        # Call render
        self.text_edit.render()

        # Verify that the console methods were called
        self.mock_console.set_color.assert_called()
        self.mock_console.clear.assert_called()
        self.mock_console.put.assert_called()

        print("✓ TextEdit.render() test passed")
        print(f"  - set_color called {self.mock_console.set_color.call_count} times")
        print(f"  - clear called {self.mock_console.clear.call_count} times")
        print(f"  - put called {self.mock_console.put.call_count} times")


if __name__ == "__main__":
    unittest.main()
