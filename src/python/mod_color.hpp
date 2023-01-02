#pragma once

#include "../colors.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <cctype>
#include <string>
#include <tuple>

namespace py = pybind11;

static std::string to_upper(std::string const& s)
{
    std::string target = s;
    for (auto& c : target) {
        c = static_cast<char>(toupper(c));
    }
    return target;
}

inline void add_color_module(py::module_ const& mod)
{
#define COL(x) mod.attr(to_upper(#x).c_str()) = static_cast<uint32_t>(color::x)
    COL(black);
    COL(white);
    COL(red);
    COL(cyan);
    COL(purple);
    COL(green);
    COL(blue);
    COL(yellow);
    COL(orange);
    COL(brown);
    COL(light_red);
    COL(dark_grey);
    COL(grey);
    COL(light_green);
    COL(light_blue);
    COL(light_grey);
    COL(transp);
#undef COL
}
