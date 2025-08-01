# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PIX (pixpy) is a cross-platform 2D graphics library with a C++ core and Python bindings. It's designed for learning and game development, providing efficient console/tileset rendering and composable images using OpenGL/GLES2.

## Build Commands

### C++ Library and Python Module
```bash
# Build the Python module (development)
make all

# Create Python distribution
make dist

# Generate documentation
make mkdoc

# Run Python tests
make test

# Run tests with verbose output
make test-verbose
```
## Architecture

### Core Components

- **Context** (`src/context.hpp`): OpenGL rendering context management with viewport, clipping, and blend modes
- **Image** (`src/image.hpp`): Texture-based image system with efficient cropping and compositing
- **PixConsole** (`src/pixel_console.hpp`): Console/terminal rendering system for tile-based games
- **TileSet** (`src/tile_set.hpp`): Manages character/tile graphics for console rendering
- **Screen** (`src/screen.hpp`): Main display surface and event handling
- **System** (`src/system.hpp`): Platform abstraction layer (GLFW/Pi/Emscripten)

### Python Bindings

The Python interface is implemented through PyBind11 in `src/python.cpp` with individual class bindings in `src/python/`:

- `class_screen.hpp`: Main display and event loop
- `class_image.hpp`: Image manipulation and drawing
- `class_console.hpp`: Console/terminal interface
- `class_canvas.hpp`: Drawing context
- `mod_event.hpp`: Event system (mouse, keyboard, text input)
- `mod_key.hpp`: Key constants and input handling
- `mod_color.hpp`: Color utilities

## Key Development Patterns

### Image System
Images are OpenGL texture references with UV coordinates, making cropping and sub-image operations very efficient. The `ImageView` class provides a lightweight view into texture data.

### Console System
The console uses a tile-based approach where each character/tile is stored in a texture atlas. It supports both text and custom graphics tiles.

### Event Handling
Events are queued and processed through the Machine singleton. The Python interface provides both polling (`is_pressed`) and event-driven (`all_events`) approaches.

### Headless Testing and Graphics Logging

PIX supports headless mode with drawing command logging for automated testing and verification:

```bash

# To check that a pixpy python script runs:
PIX_CHECK=1 python3 script.py

# Run in headless mode with drawing command logging
PIX_HEADLESS=1 PIX_DRAWLOG=output.log PIX_RUNFRAMES=60 python3 script.py

# Log drawing commands while showing graphics
PIX_DRAWLOG=debug.log python3 examples/hello_world.py
```

**Environment Variables:**
- `PIX_CHECK=1`: Run one frame in headless, to test the code 
- `PIX_HEADLESS=1`: Run without graphics window
- `PIX_DRAWLOG=filename.log`: Log all drawing commands to specified file
- `PIX_RUNFRAMES=N`: Automatically exit after N frames

**Logged Commands Include:**
- `filled_rect`, `rect`, `line`, `circle`, `filled_circle`
- `draw image=<id>` operations with position/rotation
- `swap` to indicate one full frame has been rendered

Use this for verifying graphics code changes: "Run this in headless mode with draw logging"

## Testing

### Python Tests
All Python tests are located in the `tests/` directory. The project uses pytest for testing with the following structure:

- `tests/test_edit_cmd.py`: Tests for editor command functionality
- `tests/test_editor.py`: Tests for editor components
- `tests/test_clipboard.py`: Tests for clipboard operations
- `tests/test_create_function.py`: Tests for function creation utilities

**Running Tests:**
```bash
# Run all tests (requires build first)
make test

# Run tests with detailed output
make test-verbose

# Run tests directly with pytest
PYTHONPATH=python python -m pytest tests/
```

**Pre-commit Hook:**
A pre-commit hook automatically runs all tests before each commit. If any tests fail, the commit is aborted. This ensures code quality and prevents broken code from being committed.

To bypass the pre-commit hook (not recommended):
```bash
git commit --no-verify
```

## Dependencies

- **FreeType**: Font rendering
- **GLFW**: Window management (desktop)
- **PyBind11**: Python bindings
- **Tree-sitter**: Code parsing (for editor features)
- **LibTess2**: Polygon tessellation
- **LodePNG**: PNG loading
