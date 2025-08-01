#!/usr/bin/env python3
"""Test clipboard functionality"""

import sys

sys.path.insert(0, "python")
import pixpy as pix


def test_clipboard():

    pix.open_display(size=(128, 128), visible=False).swap()

    # Test setting clipboard
    test_text = "Hello from PIX!"
    pix.set_clipboard(test_text)
    print(f"Set clipboard to: {test_text}")

    # Test getting clipboard
    content = pix.get_clipboard()
    print(f"Got clipboard content: {content}")

    # Verify it works
    if content == test_text:
        print("✓ Clipboard test successful!")
        return True
    else:
        print("✗ Clipboard test failed!")
        return False


if __name__ == "__main__":
    test_clipboard()

