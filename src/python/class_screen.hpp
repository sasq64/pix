#pragma once

#include "../machine.hpp"
#include "../system.hpp"
#include "../vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <string>
#include <tuple>

namespace py = pybind11;

inline auto add_screen_class(py::module_ const& mod)
{
    auto screen = py::class_<Screen, std::shared_ptr<Screen>>(mod, "Screen");
    screen.def("set_as_target", &Screen::set_target);
    screen.def_property_readonly("frame_counter", [](Screen const&) {
        return Machine::get_instance().frame_counter;
    });
    screen.def_property_readonly(
        "seconds",
        [](Screen const& screen) { return screen.get_time().seconds; },
        "Total seconds elapsed since starting pix.");
    screen.def_property_readonly(
        "delta", [](Screen const& screen) { return screen.get_time().delta; },
        "Time in seconds for last frame.");
    screen.def_property(
        "fps", [](Screen const& screen) { return screen.get_time().fps; },
        [](Screen& screen, int fps) { screen.set_fps(fps); },
        "Current FPS. Set to 0 to disable fixed FPS. Then use `seconds` or "
        "`delta` to sync your movement.");
    screen.def_property_readonly(
        "context",
        [](Screen const&) { return Machine::get_instance().context; },
        "Get the screen context.");
    screen.def_property_readonly(
        "size", [](Screen const& screen) { return Vec2i{screen.get_size()}; }, "Size (in pixels) of screen.");
    screen.def_property_readonly(
        "width", [](Screen const& s) { return s.get_size().first; });
    screen.def_property_readonly(
        "height", [](Screen const& s) { return s.get_size().second; });
    screen.def(
        "swap",
        [](std::shared_ptr<Screen> const& screen) {
            auto& m = Machine::get_instance();
            m.frame_counter++;
            m.context->flush();
            screen->swap();
        },
        "Synchronize with the frame rate of the display and swap buffers so what you have drawn becomes visible. This "
        "is normally the last thing you do in your render loop.");

    return screen;
}
