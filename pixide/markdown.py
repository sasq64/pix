import re
import pixpy


class MarkdownRenderer:
    """
    A markdown renderer that stores color configuration and renders to a pixpy Console.
    """

    def __init__(self, console: pixpy.Console, colors: dict[str, int] | None = None):
        """
        Initialize the markdown renderer with a console and color scheme.

        Args:
            console: The pixpy Console to render to
            colors: Optional dict of color mappings. If None, uses default colors.
        """
        self.console = console
        if colors is None:
            self.colors = {
                'h1': pixpy.color.CYAN,
                'h2': pixpy.color.LIGHT_GREY,
                'h3': pixpy.color.WHITE,
                'bold': pixpy.color.YELLOW,
                'italic': pixpy.color.GREEN,
                'code': pixpy.color.ORANGE,
                'link': pixpy.color.BLUE,
                'normal': pixpy.color.WHITE
            }
        else:
            self.colors = colors.copy()

    def set_color(self, name: str, color: int):
        self.colors[name] = color

    def render(self, markdown: str):
        """
        Parse and render markdown text to the console.

        Args:
            markdown: The markdown text to parse and render
        """
        lines = markdown.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines but advance cursor
            if not line.strip():
                self.console.write("\n")
                i += 1
                continue

            # Fenced code blocks
            if line.strip().startswith('```'):
                code_lines, format_type, end_index = self._extract_fenced_code_block(lines, i)
                self._render_fenced_code_block(code_lines, format_type)
                i = end_index + 1
                continue

            # Headers
            if line.startswith('# '):
                self.console.fg_color = self.colors['h1']
                self._render_text(line[2:].strip())
            elif line.startswith('## '):
                self.console.fg_color = self.colors['h2']
                self._render_text(line[3:].strip())
            elif line.startswith('### '):
                self.console.fg_color = self.colors['h3']
                self._render_text(line[4:].strip())
            else:
                # Process inline formatting with wrapping
                self._render_inline_formatting(line)

            # Move to next line
            self.console.write("\n")
            i += 1


    def _render_text(self, text: str):
        """
        Render plain text with word wrapping.
        """
        if not text:
            return

        console_width = self.console.grid_size.x
        words = text.split()
        current_line = ""

        for word in words:
            # Check if adding this word would exceed the line width
            test_line = current_line + (" " if current_line else "") + word

            if len(test_line) <= console_width:
                current_line = test_line
            else:
                # Write current line if it has content
                if current_line:
                    self.console.write(current_line)
                    self.console.write("\n")

                # Start new line with current word
                current_line = word

        # Write any remaining text
        if current_line:
            self.console.write(current_line)

    def _render_inline_formatting(self, line: str):
        """
        Render a line with inline markdown formatting and word wrapping.
        """
        # Check if line has any formatting
        patterns = [
            (r'\*\*(.*?)\*\*', 'bold'),      # **bold**
            (r'\*(.*?)\*', 'italic'),        # *italic*
            (r'`(.*?)`', 'code'),            # `code`
            (r'\[(.*?)\]\(.*?\)', 'link'),   # [text](url)
        ]

        has_formatting = any(re.search(pattern, line) for pattern, _ in patterns)

        if not has_formatting:
            # No formatting, just render with wrapping
            self.console.fg_color = self.colors['normal']
            self._render_text(line)
        else:
            # Has formatting - parse into segments and wrap with formatting preserved
            self._render_formatted_text(line)

    def _render_formatted_text(self, line: str):
        """
        Render formatted text with proper word wrapping, preserving formatting.
        """
        # Parse line into segments with formatting info
        segments = self._parse_line_segments(line)

        # Word wrap the segments
        console_width = self.console.grid_size.x
        current_line_length = 0

        for segment_text, segment_format in segments:
            words = segment_text.split()

            for i, word in enumerate(words):
                # Add space before word if not first word in segment and not first word on line
                space_before = " " if i > 0 or (current_line_length > 0 and segment_text.strip()) else ""
                word_with_space = space_before + word

                # Check if word fits on current line
                if current_line_length + len(word_with_space) <= console_width:
                    # Word fits, write it
                    if space_before:
                        self.console.fg_color = self.colors['normal']
                        self.console.write(space_before)
                        current_line_length += len(space_before)

                    self.console.fg_color = self.colors[segment_format]
                    self.console.write(word)
                    current_line_length += len(word)
                else:
                    # Word doesn't fit, start new line
                    if current_line_length > 0:
                        self.console.write("\n")
                        current_line_length = 0

                    self.console.fg_color = self.colors[segment_format]
                    self.console.write(word)
                    current_line_length = len(word)

    def _parse_line_segments(self, line: str):
        """
        Parse a line into segments with formatting information.
        Returns list of (text, format_type) tuples.
        """
        patterns = [
            (r'\*\*(.*?)\*\*', 'bold'),      # **bold**
            (r'\*(.*?)\*', 'italic'),        # *italic*
            (r'`(.*?)`', 'code'),            # `code`
            (r'\[(.*?)\]\(.*?\)', 'link'),   # [text](url)
        ]

        segments : list[tuple[str, str]] = []
        pos = 0

        while pos < len(line):
            # Find the next formatting
            next_match = None
            next_pos = len(line)
            next_type = None

            for pattern, format_type in patterns:
                match = re.search(pattern, line[pos:])
                if match and match.start() + pos < next_pos:
                    next_match = match
                    next_pos = match.start() + pos
                    next_type = format_type

            if next_match and next_type:
                # Add text before formatting
                if next_pos > pos:
                    segments.append((line[pos:next_pos], 'normal'))

                # Add formatted text
                segments.append((next_match.group(1), next_type))

                # Move position past the match
                pos = next_pos + len(next_match.group(0))
            else:
                # No more formatting, add remaining text
                if pos < len(line):
                    segments.append((line[pos:], 'normal'))
                break

        return segments

    def _extract_fenced_code_block(self, lines: list[str], start_index: int) -> tuple[list[str], str, int]:
        """
        Extract a fenced code block from the lines starting at start_index.

        Returns:
            tuple of (code_lines, format_type, end_index)
        """
        start_line = lines[start_index].strip()
        format_type = start_line[3:].strip()  # Extract format after ```

        code_lines : list[str] = []
        i = start_index + 1

        while i < len(lines):
            if lines[i].strip() == '```':
                return code_lines, format_type, i
            code_lines.append(lines[i])
            i += 1

        # If no closing ```, treat rest of document as code
        return code_lines, format_type, len(lines) - 1

    def _render_fenced_code_block(self, code_lines: list[str], format_type: str):
        """
        Render a fenced code block. Currently just renders as code color.

        Args:
            code_lines: The lines of code to render
            format_type: The format specified after ``` (for future syntax highlighting)
        """
        self.console.fg_color =  pixpy.color.YELLOW

        self.console.bg_color = pixpy.color.DARK_GREY
        for line in code_lines:
            cp = self.console.cursor_pos
            self.console.clear_area(0, cp.y, self.console.grid_size.x, 1) 
            self.console.write(line)
            self.console.write("\n")
        self.console.bg_color = pixpy.color.BLACK


# Convenience function to maintain backward compatibility
def render_markdown(console: pixpy.Console, markdown: str):
    """
    Parse and render markdown text to a pixpy Console using default colors.

    Args:
        console: The pixpy Console to render to
        markdown: The markdown text to parse and render
    """
    renderer = MarkdownRenderer(console)
    renderer.render(markdown)
