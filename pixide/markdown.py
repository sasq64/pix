import re
import pixpy


def render_markdown(console: pixpy.Console, markdown: str):
    """
    Parse and render markdown text to a pixpy Console.
    
    Args:
        console: The pixpy Console to render to
        markdown: The markdown text to parse and render
    """
    # Color scheme for different markdown elements
    colors = {
        'h1': pixpy.color.CYAN,
        'h2': pixpy.color.LIGHT_GREY, 
        'h3': pixpy.color.WHITE,
        'bold': pixpy.color.YELLOW,
        'italic': pixpy.color.GREEN,
        'code': pixpy.color.ORANGE,
        'link': pixpy.color.BLUE,
        'normal': pixpy.color.WHITE
    }
    
    # Clear console and reset cursor
    console.clear()
    console.cursor_pos = pixpy.Int2(0, 0)
    
    lines = markdown.split('\n')
    
    for line in lines:
        # Skip empty lines but advance cursor
        if not line.strip():
            console.cursor_pos = pixpy.Int2(0, console.cursor_pos.y + 1)
            continue
            
        # Headers
        if line.startswith('# '):
            console.fg_color = colors['h1']
            console.write(line[2:].strip())
        elif line.startswith('## '):
            console.fg_color = colors['h2']
            console.write(line[3:].strip())
        elif line.startswith('### '):
            console.fg_color = colors['h3']
            console.write(line[4:].strip())
        else:
            # Process inline formatting
            _render_inline_formatting(console, line, colors)
        
        # Move to next line
        console.cursor_pos = pixpy.Int2(0, console.cursor_pos.y + 1)


def _render_inline_formatting(console: pixpy.Console, line: str, colors: dict):
    """
    Render a line with inline markdown formatting (bold, italic, code, links).
    """
    # Pattern to match markdown formatting
    patterns = [
        (r'\*\*(.*?)\*\*', 'bold'),      # **bold**
        (r'\*(.*?)\*', 'italic'),        # *italic*
        (r'`(.*?)`', 'code'),            # `code`
        (r'\[(.*?)\]\(.*?\)', 'link'),   # [text](url)
    ]
    
    pos = 0
    original_color = console.fg_color
    
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
        
        if next_match:
            # Write text before formatting
            if next_pos > pos:
                console.fg_color = colors['normal']
                console.write(line[pos:next_pos])
            
            # Write formatted text
            console.fg_color = colors[next_type]
            console.write(next_match.group(1))
            
            # Move position past the match
            pos = next_pos + len(next_match.group(0))
        else:
            # No more formatting, write remaining text
            console.fg_color = colors['normal']
            console.write(line[pos:])
            break
    
    # Restore original color
    console.fg_color = original_color
