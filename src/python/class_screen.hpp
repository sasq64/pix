#pragma once

#include "../machine.hpp"
#include "../system.hpp"
#include "../vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

static inline std::shared_ptr<pix::Screen>
crop_screen(pix::Screen const& screen, std::optional<Vec2f> xy_,
            std::optional<Vec2f> size_)
{
    auto xy = xy_.value_or(Vec2f(0, 0));
    auto size = size_.value_or(screen.view_size - xy);
    return screen.crop(xy.x, xy.y, size.x, size.y);
}

inline std::vector<std::shared_ptr<pix::Screen>>
split_screen(pix::Screen const& screen, Vec2f const& size)
{
    return screen.split(static_cast<int>(size.x), static_cast<int>(size.y));
}

inline auto add_screen_class(py::module_ const& mod, auto ctx_class)
{
    using namespace pybind11::literals;

    auto screen = py::class_<pix::Screen, std::shared_ptr<pix::Screen>>(
        mod, "Screen", ctx_class);
    screen.def("set_as_target", &pix::Screen::set_target);
    screen.def_property(
        "visible", [](pix::Screen const& screen) { return screen.visible; },
        [](pix::Screen& screen, bool on) { screen.set_visible(on); },
        "Is the window visible?");
    screen.def_property_readonly(
        "frame_counter",
        [](pix::Screen const& screen) { return screen.frame_counter(); });
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
        [](pix::Screen const& screen) { return screen.view_size; },
        [](pix::Screen& screen, Vec2f size) {
            screen.set_size({(int)size.x, (int)size.y});
        },
        "Size (in pixels) of screen.");
    screen.def_property_readonly(
        "width", [](pix::Screen const& s) { return s.get_size().first; });
    screen.def_property_readonly(
        "height", [](pix::Screen const& s) { return s.get_size().second; });
    screen.def(
        "crop", &crop_screen, "top_left"_a = std::nullopt,
        "size"_a = std::nullopt,
        "Crop the screen. Returns a screen reference that can be used to render to that part of the screen.");
    screen
        .def(
            "split", &split_screen, "size"_a,
            "Split the screen into exactly size.x * size.y screen references that can be used as a render target for that part of the screen.")
        .def(
            "swap",
            [](std::shared_ptr<pix::Screen> const& screen) {
                screen->flush();
                auto& m = Machine::get_instance();
                auto& callbacks = m.sys->callbacks;
                auto it = callbacks.begin();
                while (it != callbacks.end()) {
                    const auto keep_running = (*it)();
                    it = keep_running ? it+1 : callbacks.erase(it);
                }
                {
                    py::gil_scoped_release gil;
                    screen->swap();
                }
            },
            "Synchronize with the frame rate of the display and swap buffers so what you have drawn becomes visible. This is normally the last thing you do in your render loop.");
    screen.doc() =
        "The main window. Currently there can be only one instance of this class.";

    return screen;
}
