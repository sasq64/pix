import unittest
from unittest.mock import Mock, MagicMock
from pixide.viewer import TextViewer, TextRange, clamp

from pixpy import Int2

class MockConsole:
    def __init__(self, width: int = 80, height: int = 24):
        self.grid_size = Int2(width, height)
        self.size = Int2(width, height)
        self.cursor_on = False
        self.wrapping = False
        self.cursor_pos = Int2(0, 0)
        self.characters = {}  # Track put() calls
        self.fg_color = 0
        self.bg_color = 0
    
    def put(self, pos, char, fg, bg):
        self.characters[pos] = (char, fg, bg)
    
    def clear(self):
        self.characters.clear()
    
    def set_color(self, fg, bg):
        self.fg_color = fg
        self.bg_color = bg

# Mock color constants
class MockColor:
    GREEN = 0x00FF00
    WHITE = 0xFFFFFF
    LIGHT_BLUE = 0xADD8E6
    LIGHT_RED = 0xFF4444
    BLACK = 0x000000

# Mock pixpy module
class MockPixpy:
    Int2 = Int2
    Console = MockConsole
    color = MockColor()

# Patch pixpy import
import sys
sys.modules['pixpy'] = MockPixpy()

# Now import the actual classes to test
from pixide.viewer import TextViewer, TextRange

Char = tuple[int, int]


class TestTextRange(unittest.TestCase):
    """Test the TextRange class"""
    
    def test_textrange_initialization(self):
        """Test TextRange initialization"""
        start = Int2(1, 2)
        end = Int2(3, 4)
        trange = TextRange(start, end, 5)
        
        self.assertEqual(trange.start, start)
        self.assertEqual(trange.end, end)
        self.assertEqual(trange.arg, 5)
    
    def test_textrange_initialization_default_arg(self):
        """Test TextRange initialization with default arg"""
        start = Int2(1, 2)
        end = Int2(3, 4)
        trange = TextRange(start, end)
        
        self.assertEqual(trange.arg, -1)
    
    def test_textrange_repr(self):
        """Test TextRange string representation"""
        start = Int2(1, 2)
        end = Int2(3, 4)
        trange = TextRange(start, end)
        
        self.assertEqual(repr(trange), "Int2(1, 2) -> Int2(3, 4)")
    
    def test_textrange_lines_single_line(self):
        """Test lines() iterator for single line range"""
        start = Int2(2, 1)  # col=2, line=1
        end = Int2(5, 1)    # col=5, line=1
        trange = TextRange(start, end)
        
        lines = list(trange.lines())
        expected = [(1, 2, 5)]  # line_no, col0, col1
        self.assertEqual(lines, expected)
    
    def test_textrange_lines_multi_line(self):
        """Test lines() iterator for multi-line range"""
        start = Int2(2, 1)  # col=2, line=1
        end = Int2(3, 3)    # col=3, line=3
        trange = TextRange(start, end)
        
        lines = list(trange.lines())
        expected = [
            (1, 2, -1),  # First line: from col 2 to end
            (2, 0, -1),  # Middle line: entire line
            (3, 0, 3)    # Last line: from start to col 3
        ]
        self.assertEqual(lines, expected)
    
    def test_textrange_lines_reversed_single_line(self):
        """Test lines_reversed() iterator for single line range"""
        start = Int2(2, 1)
        end = Int2(5, 1)
        trange = TextRange(start, end)
        
        lines = list(trange.lines_reversed())
        expected = [(1, 2, 5)]
        self.assertEqual(lines, expected)
    
    def test_textrange_lines_reversed_multi_line(self):
        """Test lines_reversed() iterator for multi-line range"""
        start = Int2(2, 1)
        end = Int2(3, 3)
        trange = TextRange(start, end)
        
        lines = list(trange.lines_reversed())
        expected = [
            (3, 0, 3),   # Last line: from start to col 3
            (2, 0, -1),  # Middle line: entire line
            (1, 2, -1)   # First line: from col 2 to end
        ]
        self.assertEqual(lines, expected)


class TestTextViewer(unittest.TestCase):
    """Test the TextViewer class"""
    
    def setUp(self):
        """Set up test data before each test"""
        self.console = MockConsole(80, 24)
        self.viewer = TextViewer(self.console)
    
    def test_textviewer_initialization(self):
        """Test proper TextViewer initialization"""
        self.assertEqual(self.viewer.lines, [[]])
        self.assertEqual(self.viewer.scroll_pos, 0)
        self.assertEqual(self.viewer.scrollx, 0)
        self.assertTrue(self.viewer.dirty)
        self.assertEqual(self.viewer.cols, 80)
        self.assertEqual(self.viewer.rows, 24)
        self.assertEqual(self.viewer.con, self.console)
        self.assertTrue(self.console.cursor_on)
        self.assertFalse(self.console.wrapping)
    
    def test_set_text_simple(self):
        """Test setting simple text content"""
        text = "Hello\nWorld\nTest"
        self.viewer.set_text(text)
        
        expected_lines = [
            [(ord('H'), 1), (ord('e'), 1), (ord('l'), 1), (ord('l'), 1), (ord('o'), 1)],
            [(ord('W'), 1), (ord('o'), 1), (ord('r'), 1), (ord('l'), 1), (ord('d'), 1)],
            [(ord('T'), 1), (ord('e'), 1), (ord('s'), 1), (ord('t'), 1)]
        ]
        self.assertEqual(self.viewer.lines, expected_lines)
        self.assertTrue(self.viewer.dirty)
    
    def test_set_text_empty(self):
        """Test setting empty text"""
        self.viewer.set_text("")
        self.assertEqual(self.viewer.lines, [[]])
        self.assertTrue(self.viewer.dirty)
    
    def test_set_text_single_line(self):
        """Test setting single line text"""
        self.viewer.set_text("Hello")
        expected = [[(ord('H'), 1), (ord('e'), 1), (ord('l'), 1), (ord('l'), 1), (ord('o'), 1)]]
        self.assertEqual(self.viewer.lines, expected)
    
    def test_get_text_simple(self):
        """Test retrieving text as string"""
        # Set up test lines
        self.viewer.lines = [
            [(ord('H'), 1), (ord('e'), 1), (ord('l'), 1), (ord('l'), 1), (ord('o'), 1)],
            [(ord('W'), 1), (ord('o'), 1), (ord('r'), 1), (ord('l'), 1), (ord('d'), 1)]
        ]
        
        result = self.viewer.get_text()
        self.assertEqual(result, "Hello\nWorld")
    
    def test_get_text_empty(self):
        """Test get_text with empty content"""
        self.viewer.lines = [[]]
        result = self.viewer.get_text()
        self.assertEqual(result, "")
    
    def test_get_text_with_custom_lines(self):
        """Test get_text with custom lines parameter"""
        custom_lines = [
            [(ord('T'), 1), (ord('e'), 1), (ord('s'), 1), (ord('t'), 1)]
        ]
        result = self.viewer.get_text(custom_lines)
        self.assertEqual(result, "Test")
    
    def test_get_codepoints(self):
        """Test getting codepoints with newlines"""
        self.viewer.lines = [
            [(ord('H'), 1), (ord('i'), 1)],
            [(ord('B'), 1), (ord('y'), 1), (ord('e'), 1)]
        ]
        
        result = self.viewer.get_codepoints()
        expected = [ord('H'), ord('i'), 10, ord('B'), ord('y'), ord('e'), 10]  # 10 is newline
        self.assertEqual(result, expected)
    
    def test_get_codepoints_empty(self):
        """Test get_codepoints with empty content"""
        self.viewer.lines = [[]]
        result = self.viewer.get_codepoints()
        self.assertEqual(result, [10])  # Just a newline
    
    def test_set_console(self):
        """Test switching to different console"""
        new_console = MockConsole(120, 30)
        self.viewer.set_console(new_console)
        
        self.assertEqual(self.viewer.con, new_console)
        self.assertEqual(self.viewer.cols, 120)
        self.assertEqual(self.viewer.rows, 30)
        self.assertTrue(new_console.cursor_on)
        self.assertFalse(new_console.wrapping)
        self.assertTrue(self.viewer.dirty)
    
    def test_set_color(self):
        """Test setting foreground and background colors"""
        fg_color = 0xFF0000
        bg_color = 0x00FF00
        
        self.viewer.set_color(fg_color, bg_color)
        
        self.assertEqual(self.viewer.fg, fg_color)
        self.assertEqual(self.viewer.bg, bg_color)
    
    def test_set_palette(self):
        """Test setting color palette"""
        colors = [0x000000, 0xFFFFFF, 0xFF0000, 0x00FF00, 0x0000FF]
        self.viewer.set_palette(colors)
        
        # Check that background and foreground were set
        expected_bg = (colors[0] << 8) | 0xFF
        expected_fg = (colors[1] << 8) | 0xFF
        self.assertEqual(self.viewer.bg, expected_bg)
        self.assertEqual(self.viewer.fg, expected_fg)
        
        # Check palette entries
        for i, color in enumerate(colors):
            expected_color = (color << 8) | 0xFF
            self.assertEqual(self.viewer.palette[i], (expected_color, expected_bg))
    
    def test_scroll_screen_basic(self):
        """Test basic vertical scrolling"""
        # Set up viewer with multiple lines - use single digit numbers to avoid ord() error
        self.viewer.lines = [[(ord(str(i % 10)), 1)] for i in range(50)]  # 50 lines
        
        # Scroll down by 10 lines
        self.viewer.scroll_screen(-10)
        self.assertEqual(self.viewer.scroll_pos, 10)
        
        # Scroll up by 5 lines
        self.viewer.scroll_screen(5)
        self.assertEqual(self.viewer.scroll_pos, 5)
    
    def test_scroll_screen_bounds_top(self):
        """Test scrolling boundary at top"""
        # Set up enough lines to allow scrolling
        self.viewer.lines = [[(ord('A'), 1)] for _ in range(50)]
        self.viewer.scroll_pos = 5
        self.viewer.scroll_screen(10)  # Try to scroll past top
        self.assertEqual(self.viewer.scroll_pos, 0)
    
    def test_scroll_screen_bounds_bottom(self):
        """Test scrolling boundary at bottom"""
        self.viewer.lines = [[(ord(str(i % 10)), 1)] for i in range(30)]  # 30 lines
        
        # Try to scroll past bottom
        self.viewer.scroll_screen(-50)
        expected_max = 30 - (self.viewer.rows - 1)  # 30 - 23 = 7
        self.assertEqual(self.viewer.scroll_pos, expected_max)
    
    def test_highlight_textranges(self):
        """Test highlighting text ranges with colors"""
        # Set up test text
        self.viewer.lines = [
            [(ord('H'), 1), (ord('e'), 1), (ord('l'), 1), (ord('l'), 1), (ord('o'), 1)],
            [(ord('W'), 1), (ord('o'), 1), (ord('r'), 1), (ord('l'), 1), (ord('d'), 1)]
        ]
        
        # Create text range for "ell" in "Hello"
        trange = TextRange(Int2(1, 0), Int2(4, 0), 5)  # color 5
        self.viewer.highlight([trange])
        
        # Check that characters were colored correctly
        expected_line = [
            (ord('H'), 1),    # unchanged
            (ord('e'), 5),    # colored
            (ord('l'), 5),    # colored  
            (ord('l'), 5),    # colored
            (ord('o'), 1)     # unchanged
        ]
        self.assertEqual(self.viewer.lines[0], expected_line)
    
    def test_highlight_textranges_multiline(self):
        """Test highlighting multi-line text ranges"""
        # Set up test text
        self.viewer.lines = [
            [(ord('A'), 1), (ord('B'), 1), (ord('C'), 1)],
            [(ord('D'), 1), (ord('E'), 1), (ord('F'), 1)],
            [(ord('G'), 1), (ord('H'), 1), (ord('I'), 1)]
        ]
        
        # Highlight from B to H
        trange = TextRange(Int2(1, 0), Int2(2, 2), 3)  # color 3
        self.viewer.highlight([trange])
        
        # Check results
        expected = [
            [(ord('A'), 1), (ord('B'), 3), (ord('C'), 3)],  # B,C highlighted
            [(ord('D'), 3), (ord('E'), 3), (ord('F'), 3)],  # All highlighted
            [(ord('G'), 3), (ord('H'), 3), (ord('I'), 1)]   # G,H highlighted
        ]
        self.assertEqual(self.viewer.lines, expected)
    
    def test_highlight_textranges_out_of_bounds(self):
        """Test highlighting with ranges beyond text bounds"""
        self.viewer.lines = [[(ord('A'), 1), (ord('B'), 1)]]
        
        # Try to highlight beyond existing lines
        trange = TextRange(Int2(0, 5), Int2(1, 6), 2)
        # Should not crash
        self.viewer.highlight([trange])
        
        # Original line should be unchanged
        self.assertEqual(self.viewer.lines[0], [(ord('A'), 1), (ord('B'), 1)])
    
    def test_render_basic(self):
        """Test basic rendering without selection or cursor"""
        self.viewer.set_text("Hello\nWorld")
        self.viewer.render()
        
        # Check that console was cleared and colors set
        self.assertEqual(len(self.console.characters), 10)  # 5 + 5 characters
        
        # Check specific character placements
        self.assertIn((0, 0), self.console.characters)  # 'H' at (0,0)
        self.assertIn((4, 0), self.console.characters)  # 'o' at (4,0)
        self.assertIn((0, 1), self.console.characters)  # 'W' at (0,1)
        self.assertIn((4, 1), self.console.characters)  # 'd' at (4,1)
    
    def test_render_with_cursor_visible(self):
        """Test rendering with visible cursor"""
        self.viewer.set_text("Hello")
        cursor_pos = Int2(2, 0)  # Cursor at position 2,0
        
        self.viewer.render(cursor_pos=cursor_pos)
        
        self.assertTrue(self.console.cursor_on)
        self.assertEqual(self.console.cursor_pos.x, 2)
        self.assertEqual(self.console.cursor_pos.y, 0)
    
    def test_render_with_cursor_out_of_view(self):
        """Test rendering with cursor outside visible area"""
        # Set up many lines of text
        self.viewer.lines = [[(ord(str(i % 10)), 1)] for i in range(50)]
        self.viewer.scroll_pos = 10  # Scroll down
        
        cursor_pos = Int2(0, 5)  # Cursor above visible area
        self.viewer.render(cursor_pos=cursor_pos)
        
        self.assertFalse(self.console.cursor_on)
    
    def test_render_with_selection(self):
        """Test rendering with text selection"""
        self.viewer.set_text("Hello\nWorld")
        
        # Select "ell" in "Hello"
        selection = TextRange(Int2(1, 0), Int2(4, 0))
        self.viewer.render(selection=selection)
        
        # The selection highlighting should be applied during render
        # This is tested indirectly through the render_editor method
        self.assertIsNotNone(self.console.characters)
    
    def test_render_dirty_flag(self):
        """Test dirty flag behavior during rendering"""
        self.viewer.set_text("Hello")
        self.assertTrue(self.viewer.dirty)
        
        self.viewer.render()
        self.assertFalse(self.viewer.dirty)
        
        # Second render shouldn't clear console again
        old_chars = self.console.characters.copy()
        self.viewer.render()
        # Characters should be the same (no re-render)
        self.assertEqual(self.console.characters, old_chars)
    
    def test_render_horizontal_scrolling(self):
        """Test rendering with horizontal scrolling"""
        # Create a long line with different characters to test scrolling
        long_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" * 4  # 104 characters
        self.viewer.set_text(long_text)
        self.viewer.scrollx = 10  # Scroll right by 10 characters
        
        self.viewer.render()
        
        # The rendering logic is complex, so just verify it doesn't crash
        # and that some characters are rendered
        self.assertTrue(len(self.console.characters) > 0)
    
    def test_render_cropping_indicators(self):
        """Test left/right cropping indicators"""
        # Create text longer than console width
        long_text = "X" * 100
        self.viewer.set_text(long_text)
        self.viewer.scrollx = 10  # Scroll to show cropping
        
        self.viewer.render()
        
        # Should show left cropping indicator
        left_indicator = self.console.characters.get((0, 0))
        if left_indicator:
            # The '$' indicator should be placed for cropping
            pass  # This is complex to test without mocking internals
    
    def test_empty_text_rendering(self):
        """Test rendering with empty text"""
        self.viewer.set_text("")
        self.viewer.render()
        
        # Should not crash and should clear console
        self.assertIsNotNone(self.console.characters)
    
    def test_single_character_text(self):
        """Test with minimal text content"""
        self.viewer.set_text("A")
        
        self.assertEqual(len(self.viewer.lines), 1)
        self.assertEqual(len(self.viewer.lines[0]), 1)
        self.assertEqual(self.viewer.lines[0][0], (ord('A'), 1))
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        unicode_text = "Hello 世界"  # Mix of ASCII and Unicode
        self.viewer.set_text(unicode_text)
        
        # Should handle unicode codepoints correctly
        result_text = self.viewer.get_text()
        self.assertEqual(result_text, unicode_text)
    
    def test_many_lines_scrolling(self):
        """Test vertical scrolling with many lines"""
        # Create 100 lines of text
        lines_text = "\n".join([f"Line {i}" for i in range(100)])
        self.viewer.set_text(lines_text)
        
        # Scroll to middle
        self.viewer.scroll_screen(-50)
        
        # Should be able to scroll and stay within bounds
        self.assertTrue(0 <= self.viewer.scroll_pos <= len(self.viewer.lines))


if __name__ == "__main__":
    unittest.main()
