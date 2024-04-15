#include "python/class_console.hpp"
#include "python/class_context.hpp"
#include "python/class_font.hpp"
#include "python/class_image.hpp"
#include "python/class_screen.hpp"
#include "python/class_tileset.hpp"
#include "python/class_vec2.hpp"
#include "python/mod_color.hpp"
#include "python/mod_event.hpp"
#include "python/mod_key.hpp"

#include "gl/texture.hpp"

#include "context.hpp"
#include "font.hpp"
#include "image.hpp"
#include "machine.hpp"
#include "system.hpp"
#include "vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl/filesystem.h>

#include <chrono>
#include <filesystem>
#include <thread>

namespace fs = std::filesystem;
namespace py = pybind11;

using namespace pybind11::literals; // NOLINT

namespace {
    Machine m;
}

Machine& Machine::get_instance()
{
    return m;
}

void init()
{
    if (m.sys == nullptr) {
#ifdef RASPBERRY_PI
        m.sys = create_pi_system();
#else
        m.sys = create_glfw_system();
#endif
    }
    auto atexit = py::module_::import("atexit");
    atexit.attr("register")(py::cpp_function([] {
        if (m.frame_counter == 0 && m.screen != nullptr) {
            log("Running at exit\n");
            m.screen->swap();
            while (m.sys->run_loop()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
            }
        }
        log("Done");
    }));
}

std::shared_ptr<Screen> open_display(int width, int height, bool full_screen)
{
    if (m.screen != nullptr) {
        return m.screen;
    }
    init();
    Screen::Settings settings{.screen = full_screen ? ScreenType::Full
                                                    : ScreenType::Window,
                              .display_width = width,
                              .display_height = height};

    m.screen = m.sys->init_screen(settings);

    auto [realw, realh] = m.screen->get_size();

    m.context = std::make_shared<pix::Context>(realw, realh, 0);
    m.context->vpscale = m.screen->get_scale();

    m.sys->add_listener([](AnyEvent const& e) {
        if (std::holds_alternative<ResizeEvent>(e)) {
            auto [w, h] = m.screen->get_size();
            m.context->resize(Vec2f(w,h), m.screen->get_scale());
        }
        if (std::holds_alternative<KeyEvent>(e)) {
            auto ke = std::get<KeyEvent>(e);
            if (ke.key == 'c' && (ke.mods & 2) != 0)
            {
                m.sys->post_event(QuitEvent{});
                return System::Propagate::Stop;
            }
        }
        return System::Propagate::Pass;
    });

    return m.screen;
}

std::shared_ptr<Screen> open_display2(Vec2i size, bool full_screen)
{
    return open_display(size.x, size.y, full_screen);
}

void save_png(gl::TexRef const& tex, fs::path const& file_name)
{
    auto pixels = tex.read_pixels();
    pix::Image img{static_cast<int>(tex.width()),
                   static_cast<int>(tex.height()), pixels.data()};
    img.flip();
    pix::save_png(img, file_name.string());
}

std::shared_ptr<FreetypeFont> load_font(fs::path const& name, int size)
{
    return std::make_shared<FreetypeFont>(name.string().c_str(), size);
}

bool is_pressed(int key)
{
    return m.sys->is_pressed(key);
}
bool was_pressed(int key)
{
    return m.sys->was_pressed(key);
}
bool was_released(int key)
{
    return m.sys->was_released(key);
}

PYBIND11_MODULE(_pixpy, mod)
{
    mod.doc() = "pixpy native module";

    add_key_module(mod.def_submodule("key"));
    add_color_module(mod.def_submodule("color"));

    add_vec2_class(mod);

    pybind11::implicitly_convertible<std::tuple<int, int>, Vec2i>();
    pybind11::implicitly_convertible<std::tuple<int, int>, Vec2f>();
    pybind11::implicitly_convertible<std::tuple<double, double>, Vec2f>();
    pybind11::implicitly_convertible<std::tuple<double, int>, Vec2f>();
    pybind11::implicitly_convertible<std::tuple<int, double>, Vec2f>();
    pybind11::implicitly_convertible<Vec2i, Vec2f>();

    auto tc = add_image_class(mod);
    auto ctx = add_context_class(mod);

    add_font_class(mod);

    add_tileset_class(mod);

    add_console_class(mod);

    add_draw_functions(tc);
    tc.def_property_readonly(
        "size", [](gl::TexRef& self) { return Vec2f{self.width(), self.height()}; });


    add_draw_functions(ctx);

    add_event_mod(mod.def_submodule("event"));

    auto screen = add_screen_class(mod);
    add_draw_functions(screen);

    //pybind11::implicitly_convertible<std::shared_ptr<Screen, pix::Context>();
    // MODULE
    mod.def("open_display", &open_display, "width"_a = -1, "height"_a = -1,
            "full_screen"_a = false,
            "Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.\nSubsequent calls to this method returns the same screen instance, " "since you can only have one active display in pix.");
    mod.def("open_display", &open_display2, "size"_a, "full_screen"_a = false,
            "Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.\nSubsequent calls to this method returns the same screen instance, since you can only have one active display in pix.");
    mod.def("get_display", [] { return m.screen; });
    mod.def(
        "all_events", [] { return m.sys->all_events(); },
        "Return a list of all pending events.");
    mod.def(
        "is_pressed",
        [](std::variant<int, char32_t> key) {
            return std::visit(&is_pressed, key);
        },
        "key"_a, "Returns _True_ if the keyboard or mouse key is held down.");
    mod.def(
        "was_pressed",
        [](std::variant<int, char32_t> key) {
            return std::visit(&was_pressed, key);
        },
        "key"_a,
        "Returns _True_ if the keyboard or mouse key was pressed this loop. "
        "`run_loop()` refreshes these states.");
    mod.def(
        "was_released",
        [](std::variant<int, char32_t> key) {
          return std::visit(&was_released, key);
        },
        "key"_a,
        "Returns _True_ if the keyboard or mouse key was pressed this loop. "
        "`run_loop()` refreshes these states.");
    mod.def(
        "get_pointer", [] { return Vec2f{m.sys->get_pointer()}; },
        "Get the xy coordinate of the mouse pointer (in screen space).");
    mod.def(
        "run_loop", [] { return m.sys->run_loop(); },
        "Should be called first in your main rendering loop. Clears all pending events and all pressed keys. Returns _True_ as long as the application is running (the user has not closed the window or quit in some other way");
    mod.def("load_png", &pix::load_png, "file_name"_a,
            "Create an _Image_ from a png file on disk.");
    mod.def("save_png", &save_png, "image"_a, "file_name"_a,
            "Save an _Image_ to disk");
    mod.def("blend_color", &color::blend_color, "color0"_a, "color1"_a, "t"_a, "Blend two colors together. `t` should be between 0 and 1.");
    mod.def("blend_colors", &color::blend_colors, "colors"_a, "t"_a, "Get a color from a color range. Works similar to bilinear filtering of an 1D texture.");
    mod.def("add_color", &color::add_color, "color0"_a, "color1"_a);
    mod.def("rgba", &color::rgba, "red"_a, "green"_a, "blue"_a, "alpha"_a,
            "Combine four color components into a color.");
    mod.def("load_font", &load_font, "name"_a, "size"_a = 0, "Load a TTF font.");
    mod.def(
        "inside_polygon",
        [](std::vector<Vec2f> const& points, Vec2f point) {
            Vec2f s = point + Vec2f{10000, 0};
            int count = 0;
            for(size_t i=0; i<points.size()-1; i++) {

                auto&& a = points[i];
                auto&& b = points[i+1];
                if (pix::instersects(point, s, a, b)) {
                    count++;
                }
            }
            auto&& a = points[points.size()-1];
            auto&& b = points[0];
            if (pix::instersects(point, s, a, b)) {
                count++;
            }
            return (count & 1) == 1;
        },
        "points"_a, "point"_a, "Check if the `point` is inside the polygon formed by `points`.");
}
