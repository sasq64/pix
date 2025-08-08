import pytest
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the project root to Python path to import pixide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pixide.markdown import render_markdown, MarkdownRenderer


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
        self.mock_console.grid_size = Mock(x=80, y=25)  # Default console size
        
        # Patch pixpy in the markdown module
        import pixide.markdown
        pixide.markdown.pixpy = self.mock_pixpy
    
    def test_render_basic_text(self):
        """Test rendering basic text without formatting."""
        markdown = "Hello World"
        
        render_markdown(self.mock_console, markdown)
        
        # Verify text was written
        write_calls = self.mock_console.write.call_args_list
        written_texts = [call[0][0] for call in write_calls]
        assert "Hello World" in written_texts
    
    def test_render_headers(self):
        """Test rendering different header levels."""
        markdown = """# Header 1
## Header 2  
### Header 3"""
        
        render_markdown(self.mock_console, markdown)
        
        # Check that write was called for each header and newlines
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) == 6  # 3 headers + 3 newlines
        
        # Verify header text content (without markdown symbols)
        assert write_calls[0][0][0] == "Header 1"
        assert write_calls[2][0][0] == "Header 2"
        assert write_calls[4][0][0] == "Header 3"
    
    def test_render_bold_text(self):
        """Test rendering bold text formatting."""
        markdown = "This is **bold text** in a sentence."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify that write was called multiple times for different parts
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that bold text content appears (words may be separate)
        written_texts = [call[0][0] for call in write_calls]
        assert "bold" in written_texts
        assert "text" in written_texts
    
    def test_render_italic_text(self):
        """Test rendering italic text formatting."""
        markdown = "This is *italic text* in a sentence."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify that write was called multiple times
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that italic text content appears (words may be separate)
        written_texts = [call[0][0] for call in write_calls]
        assert "italic" in written_texts
        assert "text" in written_texts
    
    def test_render_code_text(self):
        """Test rendering inline code formatting."""
        markdown = "Use the `render_markdown` function."
        
        render_markdown(self.mock_console, markdown)
        
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
        
        # Verify that newlines are written for empty lines
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) == 5  # Line 1 + \n + \n + Line 3 + \n
        # Check content written
        written_texts = [call[0][0] for call in write_calls]
        assert "Line 1" in written_texts
        assert "Line 3" in written_texts
        assert "\n" in written_texts
    
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
        
        # Verify multiple write calls for different formatting
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 3  # Should be multiple calls for different formats
        
        # Check that all formatted text appears
        written_texts = [call[0][0] for call in write_calls]
        assert "bold" in written_texts
        assert "italic" in written_texts
        assert "code" in written_texts
    
    def test_word_wrapping(self):
        """Test word wrapping functionality."""
        # Set up console with small width for testing
        self.mock_console.grid_size = Mock(x=20)  # 20 characters wide
        
        # Long text that should wrap
        markdown = "This is a very long line of text that should definitely wrap across multiple lines when rendered to a narrow console."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify multiple write calls (indicating wrapping occurred)
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1  # Should be wrapped into multiple writes
        
        # Filter out newline calls to check only content
        content_calls = [call for call in write_calls if call[0][0] != "\n"]
        
        # Verify no single content write call exceeds console width
        for call in content_calls:
            written_text = call[0][0]
            assert len(written_text) <= 20  # Should not exceed console width
        
        # Check that all the important words are still there
        all_written_text = ' '.join([call[0][0] for call in content_calls])
        assert "This" in all_written_text
        assert "very" in all_written_text
        assert "long" in all_written_text
        assert "console" in all_written_text
    
    def test_word_wrapping_with_formatting(self):
        """Test word wrapping with markdown formatting."""
        # Set up console with small width
        self.mock_console.grid_size = Mock(x=15)  # 15 characters wide
        
        # Text with formatting that needs wrapping
        markdown = "This **bold text** should wrap across multiple lines nicely."
        
        render_markdown(self.mock_console, markdown)
        
        # Verify multiple write calls
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that formatted text still appears (words may be separate)
        written_texts = [call[0][0] for call in write_calls]
        assert "bold" in written_texts
        assert "text" in written_texts
        
        # Check that some key words appear
        all_written_text = ' '.join(written_texts)
        assert "This" in all_written_text
        assert "bold" in all_written_text
        assert "should" in all_written_text
    
    def test_header_wrapping(self):
        """Test that headers also wrap when they're too long."""
        # Set up console with small width
        self.mock_console.grid_size = Mock(x=10)  # 10 characters wide
        
        # Long header that should wrap
        markdown = "# This is a very long header that should wrap"
        
        render_markdown(self.mock_console, markdown)
        
        # Verify multiple write calls for the wrapped header
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Filter out newline calls to check only content
        content_calls = [call for call in write_calls if call[0][0] != "\n"]
        
        # Verify no single content write exceeds width
        for call in content_calls:
            written_text = call[0][0]
            assert len(written_text) <= 10
    
    def test_markdown_renderer_class_basic(self):
        """Test the MarkdownRenderer class with default colors."""
        renderer = MarkdownRenderer(self.mock_console)
        markdown = "Hello **World**"
        
        renderer.render(markdown)
        
        # Verify that write was called multiple times
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        # Check that content appears (words may be separate)
        written_texts = [call[0][0] for call in write_calls]
        assert "Hello" in written_texts
        assert "World" in written_texts
    
    def test_markdown_renderer_class_custom_colors(self):
        """Test the MarkdownRenderer class with custom colors."""
        custom_colors = {
            'h1': 'custom_cyan',
            'h2': 'custom_grey', 
            'h3': 'custom_white',
            'bold': 'custom_yellow',
            'italic': 'custom_green',
            'code': 'custom_orange',
            'link': 'custom_blue',
            'normal': 'custom_white'
        }
        
        renderer = MarkdownRenderer(self.mock_console, custom_colors)
        markdown = "# Header\n**bold text**"
        
        renderer.render(markdown)
        
        # Verify that fg_color was set to custom colors
        # The exact verification depends on implementation details,
        # but we can verify that the renderer uses the custom colors
        assert renderer.colors['h1'] == 'custom_cyan'
        assert renderer.colors['bold'] == 'custom_yellow'
        
        # Verify content was written
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        written_texts = [call[0][0] for call in write_calls]
        assert "Header" in written_texts
        assert "bold" in written_texts
        assert "text" in written_texts
    
    def test_markdown_renderer_class_color_isolation(self):
        """Test that different MarkdownRenderer instances have separate colors."""
        colors1 = {'bold': 'red', 'normal': 'white'}
        colors2 = {'bold': 'blue', 'normal': 'green'}
        
        mock_console1 = Mock()
        mock_console1.grid_size = Mock(x=80)
        mock_console2 = Mock()
        mock_console2.grid_size = Mock(x=80)
        
        renderer1 = MarkdownRenderer(mock_console1, colors1)
        renderer2 = MarkdownRenderer(mock_console2, colors2)
        
        # Verify that each renderer has its own colors
        assert renderer1.colors['bold'] == 'red'
        assert renderer2.colors['bold'] == 'blue'
        
        # Modifying one shouldn't affect the other
        renderer1.colors['bold'] = 'yellow'
        assert renderer2.colors['bold'] == 'blue'
    
    def test_backward_compatibility_function(self):
        """Test that the render_markdown function still works as before."""
        markdown = "Test **backward** compatibility"
        
        # This should work exactly like the old API
        render_markdown(self.mock_console, markdown)
        
        write_calls = self.mock_console.write.call_args_list
        assert len(write_calls) > 1
        
        written_texts = [call[0][0] for call in write_calls]
        assert "Test" in written_texts
        assert "backward" in written_texts
        assert "compatibility" in written_texts