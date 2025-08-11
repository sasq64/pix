
PIXPY is a cross-platform 2D graphics library with a C++ core and Python bindings, designed for learning and game development with efficient console/tileset rendering using OpenGL.

## Core Workflow
```python
import pixpy

# Initialize display (required first)
screen = pixpy.open_display(800, 600)  # or pixpy.open_display(pixpy.Int2(800, 600))

# Main loop pattern
while pixpy.run_loop():
    screen.clear(pixpy.color.BLACK)

    # Your drawing code here

    screen.swap()  # Present frame
```

## Essential Classes & Types

### Coordinate Types
- `Float2(x, y)` - floating point coordinates/sizes
- `Int2(x, y)` - integer coordinates/sizes
- Both have `.x`, `.y` properties and arithmetic operations

### Canvas (Screen & Image base class)
Drawing operations available on both Screen and Image:
- `clear(color)` - fill with color
- `filled_rect(top_left: Float2, size: Float2)`
- `rect(top_left: Float2, size: Float2)` - outline
- `filled_circle(center: Float2, radius: float)`
- `circle(center: Float2, radius: float)` - outline
- `line(start: Float2, end: Float2)`
- `polygon(points: list[Float2], convex=False)`
- `draw(image: Image, top_left=None, center=None, size=Float2.ZERO, rot=0)`
- `draw(console: Console, top_left=Float2.ZERO, size=Float2.ZERO)`

Properties: `draw_color`, `blend_mode`, `size`

### Screen
Main display window - extends Canvas
- `swap()` - present frame (call at end of loop)
- `delta` - time for last frame
- `fps` - current FPS (set to 0 to disable fixed rate)
- `seconds` - total elapsed time

### Image
Texture-based image system - extends Canvas
- `Image(width, height)` or `Image(size: Float2)` - create empty
- `copy_from(image)` / `copy_to(image)` - copy operations
- `crop(top_left, size)` - create view into image
- `split(cols, rows, width, height)` - split into grid
- `save_png()` via `pixpy.save_png(image, filename)`

### Console
Tile-based text/graphics system for terminal-style rendering
- `Console(cols, rows, font_file=None, tile_size=Int2(-1,-1), font_size=-1)`
- `Console(cols, rows, tile_set: TileSet)`
- `write(text: str)` - write at cursor position
- `put(pos: Int2, tile: int, fg=None, bg=None)` - place tile
- `clear()` - clear console
- Properties: `cursor_pos`, `fg_color`, `bg_color`, `grid_size`, `tile_size`

## Input Handling

### Event System
```python
events = pixpy.all_events()  # Get and clear all events
for event in events:
    if isinstance(event, pixpy.event.Key):
        print(f"Key {event.key} pressed")
    elif isinstance(event, pixpy.event.Click):
        print(f"Click at {event.pos}")
    elif isinstance(event, pixpy.event.Text):
        print(f"Text input: {event.text}")
```

Event types: `Key`, `Click`, `Move`, `Text`, `Resize`, `Quit`

### Direct Input
- `pixpy.is_pressed(key)` - check if key currently held
- `pixpy.was_pressed(key)` - check if key was pressed this frame
- `pixpy.was_released(key)` - check if key was released this frame
- `pixpy.get_pointer()` - mouse position

## Constants & Utilities

### Colors (pixpy.color module)
`BLACK`, `WHITE`, `RED`, `GREEN`, `BLUE`, `YELLOW`, `CYAN`, `PURPLE`, `ORANGE`, `GREY`, `LIGHT_GREY`, `DARK_GREY`

### Keys (pixpy.key module)
`UP`, `DOWN`, `LEFT`, `RIGHT`, `SPACE`, `ENTER`, `ESCAPE`, `TAB`, `BACKSPACE`, `DELETE`
`F1`-`F12`, `LEFT_MOUSE`, `RIGHT_MOUSE`, `MIDDLE_MOUSE`
`LSHIFT`, `RSHIFT`, `LCTRL`, `RCTRL`

### Blend Modes
`BLEND_NORMAL`, `BLEND_ADD`, `BLEND_MULTIPLY`, `BLEND_COPY`

### Color Functions
- `pixpy.rgba(r, g, b, a)` - create color from components (0.0-1.0)
- `pixpy.blend_color(color0, color1, t)` - blend two colors

## File Operations
- `pixpy.load_png(filename)` - load PNG as Image
- `pixpy.save_png(image, filename)` - save Image as PNG
- `pixpy.load_font(filename, size)` - load TTF font

## Common Patterns

### Basic Drawing
```python
screen.draw_color = pixpy.color.RED
screen.filled_rect(Float2(10, 10), Float2(100, 50))
```

### Image Operations
```python
img = pixpy.load_png("sprite.png")
screen.draw(img, center=Float2(400, 300), rot=0.5)
```

### Console Usage
```python
console = pixpy.Console(80, 25)
console.write("Hello World!")
screen.draw(console, size=screen.size)  # fullscreen console
```

