#include "python/class_canvas.hpp"
#include "python/class_console.hpp"
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
#include "screen.hpp"
#include "system.hpp"
#include "vec2.hpp"

#include <pybind11/detail/common.h>
#ifndef PYTHON_MODULE
#    include "utils.h"
#    include <pybind11/embed.h>
#endif
#include <pybind11/stl/filesystem.h>

#include <chrono>
#include <filesystem>
#include <thread>

#include <pybind11/functional.h>
#include <pybind11/stl.h>

namespace fs = std::filesystem;
namespace py = pybind11;

using namespace pybind11::literals; // NOLINT

using clk = std::chrono::steady_clock;

static inline constexpr double to_sec(clk::duration d)
{
    return static_cast<double>(
               duration_cast<std::chrono::microseconds>(d).count()) /
           1000'000.0;
}
namespace {
Machine m;
}

Machine& Machine::get_instance()
{
    return m;
}

static clk::time_point start_t;

void init()
{
    start_t = clk::now();
    if (m.sys == nullptr) {
#ifdef RASPBERRY_PI
        m.sys = create_pi_system();
#else
        m.sys = create_glfw_system();
#endif
        auto atexit = py::module_::import("atexit");
        atexit.attr("register")(py::cpp_function([] {
            Tween::tweens.clear();
            Adder::adders.clear();
            if (pix::Screen::instance != nullptr &&
                pix::Screen::instance->frame_counter() == 0) {
                log("Running at exit\n");
                pix::Screen::instance->swap();
                while (m.sys->run_loop()) {
                    std::this_thread::sleep_for(std::chrono::milliseconds(10));
                }
            }
            log("Done");
        }));
    }
}

std::shared_ptr<pix::Screen> open_display(int width, int height,
                                          bool full_screen, bool visible = true)
{
    if (pix::Screen::instance != nullptr) { return pix::Screen::instance; }
    init();
    Display::Settings const settings{
        .screen = full_screen ? DisplayType::Full : DisplayType::Window,
        .display_width = width,
        .display_height = height,
        .visible = visible};

    auto display = m.sys->init_screen(settings);
    auto screen = std::make_shared<pix::Screen>(display);

    screen->vpscale = screen->get_scale();

    pix::Screen::instance = screen;
    m.sys->add_listener([](AnyEvent const& e) {
        if (std::holds_alternative<ResizeEvent>(e)) {
            auto [w, h] = pix::Screen::instance->get_size();
            pix::Screen::instance->resize(Vec2f(w, h),
                                          pix::Screen::instance->get_scale());
        }
        return System::Propagate::Pass;
    });

    return screen;
}

static bool allow_break = false;

void set_allow_break(bool on)
{
    init();
    static int listener = m.sys->add_listener([](AnyEvent const& e) {
        if (allow_break) {
            if (std::holds_alternative<KeyEvent>(e)) {
                auto ke = std::get<KeyEvent>(e);
                if (ke.key == 'c' && (ke.mods & 2) != 0) {
                    m.sys->post_event(QuitEvent{});
                    return System::Propagate::Stop;
                }
            }
        }
        return System::Propagate::Pass;
    });
    allow_break = on;
}

std::shared_ptr<pix::Screen> open_display2(Vec2i size, bool full_screen,
                                           bool visible = true)
{
    return open_display(size.x, size.y, full_screen, visible);
}

void save_png(pix::ImageView const& image, fs::path const& file_name)
{
    auto const& tex = image.get_tex();
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

void every_frame(std::function<bool()> const& fn)
{
    m.sys->callbacks.push_back(fn);
}

#ifdef PYTHON_MODULE
PYBIND11_MODULE(_pixpy, mod)
{
#else
PYBIND11_EMBEDDED_MODULE(_pixpy, mod)
{
#endif
    mod.doc() = "pixpy native module";

    add_key_module(mod.def_submodule("key"));
    add_color_module(mod.def_submodule("color"));

    mod.attr("BLEND_NORMAL") = (GL_SRC_ALPHA << 16) | GL_ONE_MINUS_SRC_ALPHA;
    mod.attr("BLEND_ADD") = (GL_SRC_ALPHA << 16) | GL_ONE;
    mod.attr("BLEND_MULTIPLY") = (GL_DST_COLOR << 16) | GL_ZERO;
    mod.attr("BLEND_COPY") = (GL_ONE << 16) | GL_ZERO;

    add_vec2_class(mod);

    pybind11::implicitly_convertible<std::tuple<int, int>, Vec2i>();
    pybind11::implicitly_convertible<std::tuple<int, int>, Vec2f>();
    pybind11::implicitly_convertible<std::tuple<double, double>, Vec2f>();
    pybind11::implicitly_convertible<std::tuple<double, int>, Vec2f>();
    pybind11::implicitly_convertible<std::tuple<int, double>, Vec2f>();
    pybind11::implicitly_convertible<Vec2i, Vec2f>();

    auto con_class = add_console_class(mod);
    auto ctx = add_canvas_class(mod);
    auto tc = add_image_class(mod, ctx);

    add_canvas_functions(ctx);
    add_font_class(mod);

    add_console_functions(con_class);

    add_event_mod(mod.def_submodule("event"));

    auto screen = add_screen_class(mod, ctx);

    add_tileset_class(mod);

    const char* doc;

    // pybind11::implicitly_convertible<std::shared_ptr<Screen, pix::Context>();

    mod.def(
        "open_display", &open_display, "width"_a = -1, "height"_a = -1,
        "full_screen"_a = false, "visible"_a = true,
        doc =
            "Opens a new window with the given size. This also initializes pix and is expected to have been called before any other pix calls.\nSubsequent calls to this method returns the same screen instance, "
            "since you can only have one active display in pix.");
    mod.def("open_display", &open_display2, "size"_a, "full_screen"_a = false,
            "visible"_a = true, doc);
    mod.def("get_display", [] { return pix::Screen::instance; });
    mod.def("update_tweens", [] { 
        auto t = to_sec(clk::now() - start_t);
        Tween::update_all(t);
        Adder::update_all(t);
    }, "Manually update tweens");
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
        "run_every_frame", &every_frame,
        "Add a function that should be run every frame. If the function returns false it will stop being called.");
    mod.def(
        "quit_loop", [] { m.sys->quit_loop(); },
        "Make run_loop() return False. Thread safe");
    mod.def(
        "run_loop",
        [] {
            auto t = to_sec(clk::now() - start_t);
            Tween::update_all(t);
            Adder::update_all(t);
            return m.sys->run_loop();
        },
        "Should be called first in your main rendering loop. Clears all pending events and all pressed keys. Returns _True_ as long as the application is running (the user has not closed the window or quit in some other way");
    mod.def("load_png", &pix::load_png, "file_name"_a,
            "Create an _Image_ from a png file on disk.");
    mod.def("save_png", &save_png, "image"_a, "file_name"_a,
            "Save an _Image_ to disk");
    mod.def("blend_color", &color::blend_color, "color0"_a, "color1"_a, "t"_a,
            "Blend two colors together. `t` should be between 0 and 1.");
    mod.def(
        "blend_colors", &color::blend_colors<std::vector<uint32_t>>, "colors"_a,
        "t"_a,
        "Get a color from a color range. Works similar to bilinear filtering of an 1D texture.");
    mod.def("add_color", &color::add_color, "color0"_a, "color1"_a);
    mod.def("rgba", &color::rgba, "red"_a, "green"_a, "blue"_a, "alpha"_a,
            "Combine four color float components into a 32-bit color.");
    mod.def("load_font", &load_font, "name"_a, "size"_a = 0,
            "Load a TTF font.");
    mod.def("allow_break", &set_allow_break, "on"_a,
            "Allow Ctrl-C to break out of run loop");
    mod.def(
        "inside_polygon",
        [](std::vector<Vec2f> const& points, Vec2f point) {
            Vec2f const s = point + Vec2f{10000, 0};
            int count = 0;
            for (size_t i = 0; i < points.size() - 1; i++) {
                auto&& a = points[i];
                auto&& b = points[i + 1];
                if (pix::intersects(point, s, a, b)) { count++; }
            }
            auto&& a = points[points.size() - 1];
            auto&& b = points[0];
            if (pix::intersects(point, s, a, b)) { count++; }
            return (count & 1) == 1;
        },
        "points"_a, "point"_a,
        "Check if the `point` is inside the polygon formed by `points`.");
}

#ifndef PYTHON_MODULE
int main()
{
    py::scoped_interpreter guard{}; // start the interpreter and keep it alive
    py::module_ sys = py::module_::import("sys");
    py::list sys_path = sys.attr("path");
    setenv("PYTHONHOME", "../venv", 1);
    py::list path = sys.attr("path");
    sys_path.insert(0, "../venv/lib/python3.13/site-packages");

    // Add your desired directory to the module path
    sys_path.append("./pyi");
    sys_path.append("../pyi");
    sys_path.append("../examples");

    py::dict globals = py::module_::import("__main__").attr("__dict__");
    globals["__name__"] = "__main__";
    globals["__name__"] = "__main__";
    auto code = utils::read_as_string(fs::path("../examples") / "pixide.py");
    py::exec(code, globals);

    // py::exec(R"(
    //     import pixpy as pix
    //     screen = pix.open_display(size=(640,480))
    //     print(pix.open_display.__doc__)
    //     while pix.run_loop():
    //         screen.swap()
    // )");
    return 0;
}
#endif
