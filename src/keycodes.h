#pragma once
// 00 - 1F : Most common keys
// 80 - 9F : Less common keys
// 0020 - FFFFFF : Unicode

// This is a mix of known physical buttons, and actual characters. Most of
// the time this makes sense.

// If you want to read keyboard buttons depending on there location on the
// keyboard (raw keycodes) and not through their ascii characters, you can
// not do this with this system.

// Modifers are read as separate keys, so you need to keep track of
// up/down events to check for CTRL+A for instance
//
// We have 8 standard modifiers. They can be read as keys, _but_ also
// affects other keys. You will get SHIFT, 'A' if you press shift+A,
// and not SHIFT, 'a'.

// Top bits of 32-bit word are device id. Read this if for a multiplayer
// game if you need to figure out which player is which.
// Device=0 is usually keyboard

// Keys that are commonly not found on the same device can overlap, ie
// keyboard buttons and gamepad buttons.


#define DEVICE_ID(k) ((k>>24)&0xf)
//#define IS_SHIFT(k) ((k&0x00fffff7) == RKEY_LSHIFT)


enum class Key : unsigned int
{
    NONE = 0,
    RIGHT = 1,
    DOWN = 2,
    LEFT = 3,
    UP = 4,

    FIRE = 5,
    A1 = 5,

    X1 = 6,
    Y1 = 7,

    BACKSPACE = 8,
    B1 = 8,
    TAB = 9,
    SELECT = 9,
    ENTER = 10,
    START = 10,
    END = 11,
    R1 = 11,
    HOME = 12,
    L1 = 12,
    DELETE = 13,

    PAGEDOWN = 14,
    R2 = 14,
    PAGEUP = 15,
    L2 = 15,

    INSERT = 16,

    ESCAPE = 0x1b,

    SPACE = ' ',

    F1 = 0x10'0000,
    F2,
    F3,
    F4,
    F5,
    F6,
    F7,
    F8,
    F9,
    F10,
    F11,
    F12,

    LSHIFT = 0x10'0010,
    LCTRL,
    LALT,
    LWIN,
    RSHIFT = 0x10'0018,
    RCTRL,
    RALT,
    RWIN,

    LEFT_MOUSE = 0x10'0020,
    RIGHT_MOUSE,
    MIDDLE_MOUSE,
    MOUSE4,
    MOUSE5,
    WHEEL_UP,
    WHEEL_DOWN


};

