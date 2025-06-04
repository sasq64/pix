#pragma once

#include "../machine.hpp"
#include "../system.hpp"
#include "../vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

inline auto add_screen_class(py::module_ const& mod, auto ctx_class)
{
    auto screen = py::class_<pix::Screen, std::shared_ptr<pix::Screen>>(
        mod, "Screen", ctx_class);
    screen.def("set_as_target", &pix::Screen::set_target);
    screen.def_property(
        "visible", [](pix::Screen const& screen) { return screen.visible; },
        [](pix::Screen& screen, bool on) { screen.set_visible(on); },
        "Is the window visible?");
    screen.def_property_readonly("frame_counter", [](pix::Screen const&) {
        return Machine::get_instance().frame_counter;
    });
    screen.def_property_readonly(
        "seconds",
        [](pix::Screen const& screen) { return screen.get_time().seconds; },
        "Total seconds elapsed since starting pix.");
    screen.def_property_readonly(
        "delta",
        [](pix::Screen const& screen) { return screen.get_time().delta; },
        "Time in seconds for last frame.");
    screen.def_property_readonly(
        "refresh_rate",
        [](pix::Screen const& screen) {
            return screen.get_time().refresh_rate;
        },
        "Actual refresh rate of current monitor.");
    screen.def_property(
        "fps", [](pix::Screen const& screen) { return screen.get_time().fps; },
        [](pix::Screen& screen, int fps) { screen.set_fps(fps); },
        "Current FPS. Set to 0 to disable fixed FPS. Then use `seconds` or "
        "`delta` to sync your movement.");
    screen.def_property(
        "size",
        [](pix::Screen const& screen) { return Vec2f{screen.get_size()}; },
        [](pix::Screen& screen, Vec2f size) {
            screen.set_size({(int)size.x, (int)size.y});
        },
        "Size (in pixels) of screen.");
    screen.def_property_readonly(
        "width", [](pix::Screen const& s) { return s.get_size().first; });
    screen.def_property_readonly(
        "height", [](pix::Screen const& s) { return s.get_size().second; });
    screen.def(
        "swap",
        [](std::shared_ptr<pix::Screen> const& screen) {
            auto& m = Machine::get_instance();
            m.frame_counter++;
            screen->flush();
            screen->swap();
        },
        "Synchronize with the frame rate of the display and swap buffers so what you have drawn becomes visible. This is normally the last thing you do in your render loop.");
    screen.doc() =
        "The main window. Currently there can be only one instance of this class.";

    return screen;
}
