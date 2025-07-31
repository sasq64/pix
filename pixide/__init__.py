"""
PixIDE - A Python IDE built with the PIX graphics library

This module provides a complete IDE environment with text editing,
syntax highlighting, and code execution capabilities.
"""

from .editor import TextEdit, TextRange
from .main import PixIDE

__version__ = "1.0.0"
__all__ = ["TextEdit", "TextRange", "PixIDE"]

