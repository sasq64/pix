#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pixide"))

from pixide.openaiclient import create_function


def test_basic_function():
    """Test function with basic parameters"""

    def sample_func(name: str, age: int, height: float = 6.0):
        """A sample function for testing"""
        pass

    schema = create_function(sample_func)

    expected = {
        "type": "function",
        "strict": False,
        "name": "sample_func",
        "description": "A sample function for testing",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "height": {"type": "number"},
            },
            "required": ["name", "age"],
        },
    }

    assert schema == expected, f"Expected {expected}, got {schema}"
    print("✓ Basic function test passed")


def test_no_annotations():
    """Test function without type annotations"""

    def no_types(a, b="default"):
        pass

    schema = create_function(no_types)

    expected = {
        "type": "function",
        "strict": False,
        "name": "no_types",
        "description": "Calls the no_types function",
        "parameters": {
            "type": "object",
            "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
            "required": ["a"],
        },
    }

    assert schema == expected, f"Expected {expected}, got {schema}"
    print("✓ No annotations test passed")


def test_all_types():
    """Test function with all supported types"""

    def all_types(s: str, i: int, f: float, b: bool, l: list, d: dict):
        """Function with all types"""
        pass

    schema = create_function(all_types)

    expected = {
        "type": "function",
        "strict": False,
        "name": "all_types",
        "description": "Function with all types",
        "parameters": {
            "type": "object",
            "properties": {
                "s": {"type": "string"},
                "i": {"type": "integer"},
                "f": {"type": "number"},
                "b": {"type": "boolean"},
                "l": {"type": "array"},
                "d": {"type": "object"},
            },
            "required": ["s", "i", "f", "b", "l", "d"],
        },
    }

    assert schema == expected, f"Expected {expected}, got {schema}"
    print("✓ All types test passed")


def test_no_params():
    """Test function with no parameters"""

    def no_params():
        """Function with no parameters"""
        pass

    schema = create_function(no_params)

    expected = {
        "type": "function",
        "strict": False,
        "name": "no_params",
        "description": "Function with no parameters",
        "parameters": {"type": "object", "properties": {}, "required": []},
    }

    assert schema == expected, f"Expected {expected}, got {schema}"
    print("✓ No parameters test passed")


def test_custom_descriptions():
    """Test function with custom descriptions"""

    def sample_func(name: str, age: int, height: float = 6.0):
        """Original docstring"""
        pass

    # Test with custom description
    schema = create_function(
        sample_func,
        desc="Custom function description",
        arg_desc={
            "name": "The person's name",
            "age": "The person's age in years",
            "height": "The person's height in feet",
        },
    )

    expected = {
        "type": "function",
        "strict": False,
        "name": "sample_func",
        "description": "Custom function description",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The person's name"},
                "age": {
                    "type": "integer",
                    "description": "The person's age in years",
                },
                "height": {
                    "type": "number",
                    "description": "The person's height in feet",
                },
            },
            "required": ["name", "age"],
        },
    }

    assert schema == expected, f"Expected {expected}, got {schema}"
    print("✓ Custom descriptions test passed")


def test_partial_arg_descriptions():
    """Test function with partial argument descriptions"""

    def sample_func(name: str, age: int):
        """Function docstring"""
        pass

    # Test with only some arguments described
    schema = create_function(sample_func, arg_desc={"name": "The person's name"})

    expected = {
        "type": "function",
        "strict": False,
        "name": "sample_func",
        "description": "Function docstring",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The person's name"},
                "age": {"type": "integer"},
            },
            "required": ["name", "age"],
        },
    }

    assert schema == expected, f"Expected {expected}, got {schema}"
    print("✓ Partial argument descriptions test passed")


def test_desc_only():
    """Test function with only custom description"""

    def sample_func(name: str):
        """Original docstring"""
        pass

    schema = create_function(sample_func, desc="Custom description only")

    expected = {
        "type": "function",
        "strict": False,
        "name": "sample_func",
        "description": "Custom description only",
        "parameters": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    }

    assert schema == expected, f"Expected {expected}, got {schema}"
    print("✓ Description only test passed")


if __name__ == "__main__":
    test_basic_function()
    test_no_annotations()
    test_all_types()
    test_no_params()
    test_custom_descriptions()
    test_partial_arg_descriptions()
    test_desc_only()
    print("\n🎉 All tests passed!")

