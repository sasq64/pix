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
    using namespace pybind11::literals;
    // Events

    auto se = py::class_<ScrollEvent>(mod, "Scroll")
                  .def(py::init<float, float>(), "x"_a = 0, "y"_a = 0)
                  .def_readonly("x", &ScrollEvent::x)
                  .def_readonly("y", &ScrollEvent::y)
                  .def("__repr__", [](ScrollEvent const& e) {
                      return "Scroll(" + std::to_string(e.x) + "," +
                             std::to_string(e.y) + ")";
                  });
    se.attr("__match_args__") = std::make_tuple("x", "y");

    (void)py::class_<NoEvent>(mod, "NoEvent");
    py::class_<QuitEvent>(mod, "Quit").doc() =
        "Event sent when window/app wants to close.";
    py::class_<ResizeEvent>(mod, "Resize")
        .def_readonly("x", &ResizeEvent::w)
        .def_readonly("y", &ResizeEvent::h)
        .doc() = "Event sent when the window was resized";

    auto me = py::class_<MoveEvent>(mod, "Move")
                  .def(py::init<float, float, int>(), "x"_a = 0, "y"_a = 0,
                       "buttons"_a = 0)
                  .def_property_readonly(
                      "pos", [](MoveEvent const& e) { return Vec2f{e.x, e.y}; })
                  .def_readonly("x", &MoveEvent::x)
                  .def_readonly("y", &MoveEvent::y)
                  .def_readonly("buttons", &MoveEvent::buttons)
                  .def("__repr__", [](MoveEvent const& e) {
                      return "Move(" + std::to_string(e.x) + "," +
                             std::to_string(e.y) + ")";
                  });

    me.attr("__match_args__") = std::make_tuple("x", "y");
    me.doc() = "Event sent when mouse was moved.";

    auto ce =
        py::class_<ClickEvent>(mod, "Click")
            .def(py::init<float, float, int, uint32_t>(), "x"_a = 0, "y"_a = 0,
                 "buttons"_a = 0, "mods"_a = 0)
            .def_property_readonly(
                "pos", [](ClickEvent const& e) { return Vec2f{e.x, e.y}; })
            .def_readonly("x", &ClickEvent::x)
            .def_readonly("y", &ClickEvent::y)
            .def_readonly("buttons", &ClickEvent::buttons)
            .def_readonly("mods", &ClickEvent::mods)
            .def("__repr__", [](ClickEvent const& e) {
                return "Click(x=" + std::to_string(e.x) +
                       ", y=" + std::to_string(e.y) +
                       ", buttons=" + std::to_string(e.buttons) +
                       ", mods=" + std::to_string(e.mods) + ")";
            });
    ce.attr("__match_args__") = std::make_tuple("pos", "buttons");
    ce.doc() = "Event sent when screen was clicked.";

    auto ke = py::class_<KeyEvent>(mod, "Key")
                  .def(py::init<uint32_t, uint32_t, int>(), "key"_a = 0,
                       "mods"_a = 0, "device"_a = 0)
                  .def_readonly("key", &KeyEvent::key)
                  .def_readonly("mods", &KeyEvent::mods)
                  .def_readonly("device", &KeyEvent::device)
                  .def("__repr__", [](KeyEvent const& e) {
                      return "Key(key=" + std::to_string(e.key) +
                             ", mods=" + std::to_string(e.mods) + ")";
                  });
    ke.attr("__match_args__") = std::make_tuple("key");
    ke.doc() = "Event sent when key was pressed.";

    auto te =
        py::class_<TextEvent>(mod, "Text")
            .def(py::init<std::string, int>(), "text"_a = "", "device"_a = 0)
            .def_readonly("text", &TextEvent::text)
            .def_readonly("device", &TextEvent::device)
            .def("__repr__", [](TextEvent const& e) {
                return "Text(\""s + e.text + "\")";
            });
    te.attr("__match_args__") = std::make_tuple("text");
    te.doc() = "Event sent when text was input into the window.";

    (void)py::class_<AnyEvent>(mod, "AnyEvent");
}
