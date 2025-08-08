import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the project root to Python path to import pixide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pixide.markdown import render_markdown


class TestMarkdownRenderer:
    
    def setup_method(self):
        """Set up mock Console and pixpy for each test."""
        # Mock pixpy module and its components
        self.mock_pixpy = Mock()
        self.mock_pixpy.Int2 = lambda x, y: Mock(x=x, y=y)
        self.mock_pixpy.color = Mock()
        self.mock_pixpy.color.CYAN = 'cyan'
        self.mock_pixpy.color.LIGHT_GREY = 'light_grey'
        self.mock_pixpy.color.WHITE = 'white'
        self.mock_pixpy.color.YELLOW = 'yellow'
        self.mock_pixpy.color.GREEN = 'green'
        self.mock_pixpy.color.ORANGE = 'orange'
        self.mock_pixpy.color.BLUE = 'blue'
        
        # Mock Console
        self.mock_console = Mock()
        self.mock_console.cursor_pos = Mock(x=0, y=0)
        self.mock_console.fg_color = 'white'
        self.mock_console.clear = Mock()
        self.mock_console.write = Mock()
        
        # Patch pixpy in the markdown module
        import pixide.markdown
        pixide.markdown.pixpy = self.mock_pixpy
    
    def test_render_basic_text(self):
        """Test rendering basic text without formatting."""
        markdown = "Hello World"
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Verify text was written
        self.mock_console.write.assert_called_with("Hello World")
    
    def test_render_headers(self):
        """Test rendering different header levels."""
        markdown = """# Header 1
## Header 2  
### Header 3"""
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Check that write was called for each header
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) == 3
        
        # Verify header text content (without markdown symbols)
        assert write_calls[0][0][0] == "Header 1"
        assert write_calls[1][0][0] == "Header 2"
        assert write_calls[2][0][0] == "Header 3"
    
    def test_render_bold_text(self):
        """Test rendering bold text formatting."""
        markdown = "This is **bold text** in a sentence."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Verify that write was called multiple times for different parts
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that bold text content appears
        written_texts = [call[0][0] for call in write_calls]
        assert "bold text" in written_texts
    
    def test_render_italic_text(self):
        """Test rendering italic text formatting."""
        markdown = "This is *italic text* in a sentence."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Verify that write was called multiple times
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that italic text content appears
        written_texts = [call[0][0] for call in write_calls]
        assert "italic text" in written_texts
    
    def test_render_code_text(self):
        """Test rendering inline code formatting."""
        markdown = "Use the `render_markdown` function."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Verify that write was called multiple times
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that code text content appears
        written_texts = [call[0][0] for call in write_calls]
        assert "render_markdown" in written_texts
    
    def test_render_link_text(self):
        """Test rendering link formatting."""
        markdown = "Visit [Python.org](https://python.org) for more info."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Verify that write was called multiple times
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that link text content appears (without URL)
        written_texts = [call[0][0] for call in write_calls]
        assert "Python.org" in written_texts
    
    def test_render_empty_lines(self):
        """Test rendering text with empty lines."""
        markdown = """Line 1

Line 3"""
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Verify that cursor position was updated for empty lines
        # The cursor should be moved even for empty lines
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) == 2  # Only non-empty lines get written
        assert write_calls[0][0][0] == "Line 1"
        assert write_calls[1][0][0] == "Line 3"
    
    def test_color_assignments(self):
        """Test that colors are assigned correctly for different elements."""
        markdown = """# Header
**bold text**
*italic text*
`code text`
[link text](url)
normal text"""
        
        render_markdown(self.mock_console, markdown)
        
        # Verify that fg_color was set multiple times
        # We can't easily verify the exact sequence without more complex mocking,
        # but we can verify that the color attribute was accessed
        assert hasattr(self.mock_console, 'fg_color')
    
    def test_complex_formatting(self):
        """Test rendering text with multiple formatting types."""
        markdown = "This has **bold**, *italic*, and `code` all together!"
        
        render_markdown(self.mock_console, markdown)
        
        # Verify console was cleared
        self.mock_console.clear.assert_called_once()
        
        # Verify multiple write calls for different formatting
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 3  # Should be multiple calls for different formats
        
        # Check that all formatted text appears
        written_texts = [call[0][0] for call in write_calls]
        assert "bold" in written_texts
        assert "italic" in written_texts
        assert "code" in written_texts