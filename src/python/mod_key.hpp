#pragma once

#include "../keycodes.h"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <string>
#include <tuple>

namespace py = pybind11;

inline void add_key_module(py::module_ const& mod)
{
    mod.attr("MOD_SHIFT") = 1;
    mod.attr("MOD_CTRL") = 2;
    mod.attr("MOD_ALT") = 4;

#define KEY(x) mod.attr(#x) = static_cast<int>(Key::x)
    KEY(LEFT);
    KEY(RIGHT);
    KEY(UP);
    KEY(DOWN);
    KEY(LEFT_MOUSE);
    KEY(RIGHT_MOUSE);
    KEY(MIDDLE_MOUSE);
    KEY(MOUSE4);
    KEY(MOUSE5);

    KEY(FIRE);
    KEY(A1);
    KEY(X1);
    KEY(Y1);
    KEY(BACKSPACE);
    KEY(B1);
    KEY(TAB);
    KEY(SELECT);
    KEY(ENTER);
    KEY(START);
    KEY(END);
    KEY(R1);
    KEY(HOME);
    KEY(L1);
    KEY(DELETE);
    KEY(PAGEDOWN);
    KEY(R2);
    KEY(PAGEUP);
    KEY(L2);
    KEY(INSERT);
    KEY(ESCAPE);
    KEY(SPACE);
    KEY(F1);
    KEY(F2);
    KEY(F3);
    KEY(F4);
    KEY(F5);
    KEY(F6);
    KEY(F7);
    KEY(F8);
    KEY(F9);
    KEY(F10);
    KEY(F11);
    KEY(F12);
#undef KEY
}

