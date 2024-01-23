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

struct Color
{
    float r;
    float g;
    float b;
    float a;
    Color(float rr, float gg, float bb, float aa)
    :r{rr}, g{gg}, b{bb}, a{aa} { }

    Color(uint32_t rgba)
    {
        r = (rgba >> 24) / 255.0f;
        g = ((rgba >> 16) & 0xff) / 255.0f;
        b = ((rgba >> 8) & 0xff) / 255.0f;
        a = (rgba & 0xff) / 255.0f;
    }
};


inline void add_color_module(py::module_ const& mod)
{
    using namespace pybind11::literals;

    py::class_<Color>(mod, "Color")
        .def(py::init<float, float, float, float>(), "r"_a, "g"_a, "b"_a, "a"_a = 1.0)
        .def_readonly("r", &Color::r)
        .def_readonly("g", &Color::g)
        .def_readonly("b", &Color::b)
        .def_readonly("a", &Color::a)
        .def(py::init<uint32_t>(), "rgba"_a);


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
