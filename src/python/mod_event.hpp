#pragma once

#include "system.hpp"
#include "vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <string>

namespace py = pybind11;

inline void add_event_mod(py::module_ const& mod)
{
    using namespace std::string_literals;
    // Events

    (void)py::class_<NoEvent>(mod, "NoEvent");
    (void)py::class_<QuitEvent>(mod, "Quit");
    py::class_<ResizeEvent>(mod, "Resize")
        .def_readonly("x", &ResizeEvent::w)
        .def_readonly("y", &ResizeEvent::h);

    py::class_<MoveEvent>(mod, "Move")
        .def_property_readonly("pos",
                               [](MoveEvent const& e) {
                                   return Vec2f{e.x, e.y};
                               })
        .def_readonly("x", &MoveEvent::x)
        .def_readonly("y", &MoveEvent::y)
        .def_readonly("buttons", &MoveEvent::buttons)
        .def("__repr__",
             [](MoveEvent const& e) {
                 return "Move(" + std::to_string(e.x) + "," +
                        std::to_string(e.y) + ")";
             })
        .attr("__match_args__") = std::make_tuple("pos", "buttons");

    py::class_<ClickEvent>(mod, "Click")
        .def_property_readonly("pos",
                               [](ClickEvent const& e) {
                                   return Vec2f{e.x, e.y};
                               })
        .def_readonly("x", &ClickEvent::x)
        .def_readonly("y", &ClickEvent::y)
        .def_readonly("buttons", &ClickEvent::buttons)
        .def_readonly("mods", &ClickEvent::mods)
        .def("__repr__",
             [](ClickEvent const& e) {
                 return "Click(x=" + std::to_string(e.x) +
                        ", y=" + std::to_string(e.y) +
                        ", buttons=" + std::to_string(e.buttons) +
                        ", mods=" + std::to_string(e.mods) + ")";
             })
        .attr("__match_args__") = std::make_tuple("pos", "buttons");

    py::class_<KeyEvent>(mod, "Key")
        .def_readonly("key", &KeyEvent::key)
        .def_readonly("mods", &KeyEvent::mods)
        .def("__repr__",
             [](KeyEvent const& e) {
                 return "Key(key=" + std::to_string(e.key) +
                        ", mods=" + std::to_string(e.mods) + ")";
             })
        .attr("__match_args__") = std::make_tuple("key");

    py::class_<TextEvent>(mod, "Text")
        .def_readonly("text", &TextEvent::text)
        .def("__repr__",
             [](TextEvent const& e) { return "Text(\""s + e.text + "\")"; })
        .attr("__match_args__") = std::make_tuple("text");

    (void)py::class_<AnyEvent>(mod, "AnyEvent");
}
