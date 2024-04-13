#pragma once

#include "../colors.hpp"
#include "../gl/texture.hpp"
#include "../machine.hpp"
#include "../vec2.hpp"
#include "full_console.hpp"

#include <optional>
#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <string>
#include <tuple>

namespace py = pybind11;

inline std::shared_ptr<pix::Context> make_context(Vec2f size)
{
    if (size.x == 0 && size.y == 0) {
        size = Vec2f{Machine::get_instance().screen->get_size()};
    }
    return std::make_shared<pix::Context>(size.x, size.y);
}

inline pix::Context* context_from(gl::TexRef& tr)
{
    if (tr.data != nullptr) {
        return static_cast<pix::Context*>(tr.data.get());
    }

    auto* context = new pix::Context(
        {static_cast<float>(tr.x()), static_cast<float>(tr.y())},
        {static_cast<float>(tr.width()), static_cast<float>(tr.height())},
        {static_cast<float>(tr.tex->width), static_cast<float>(tr.tex->height)},
        tr.get_target());
    tr.data = std::shared_ptr<void>(static_cast<void*>(context), [](void* ptr) {
        delete static_cast<pix::Context*>(ptr);
    });
    context->texture = tr.tex;
    return context;
}

inline pix::Context* context_from(Screen& /*screen*/)
{
    return Machine::get_instance().context.get();
}

inline pix::Context* context_from(pix::Context& context)
{
    return &context;
}

template <typename T, typename... O>
inline void add_draw_functions(pybind11::class_<T, O...>& cls)
{
    using namespace pybind11::literals;

    cls.def(
        "circle",
        [](T& self, Vec2f const& center, float r) {
            context_from(self)->circle(center, r);
        },
        "center"_a, "radius"_a, "Draw an (outline) circle");

    cls.def(
        "filled_circle",
        [](T& self, Vec2f const& center, float r) {
            context_from(self)->filled_circle(center, r);
        },
        "center"_a, "radius"_a, "Draw a filled circle.");

    cls.def(
        "line",
        [](T& self, Vec2f const& from, Vec2f const& to) {
            context_from(self)->line(from, to);
        },
        "start"_a, "end"_a, "Draw a line between start and end.");

    cls.def(
        "line", [](T& self, Vec2f const& to) { context_from(self)->line(to); },
        "end"_a,
        "Draw a line from the end of the last line to the given position.");

    cls.def(
        "lines", [](T& self, std::vector<Vec2f> const& points) { context_from(self)->lines(points); },
        "points"_a,
        "Draw a line strip from all the given points.");

    cls.def(
        "polygon",
        [](T& self, std::vector<Vec2f> const& points, bool convex) {
            if (convex) {
                context_from(self)->draw_polygon(points.data(),
                                                          points.size());
            } else {
                context_from(self)->draw_inconvex_polygon(points.data(),
                                                          points.size());
            }
        },
        "points"_a, "convex"_a = false, "Draw a filled polygon.");
    cls.def(
        "plot",
        [](T& self, Vec2f const& to, uint32_t color) {
            context_from(self)->plot(to, gl::Color(color));
        },
        "center"_a, "color"_a, "Draw a point.");

    cls.def(
        "plot",
        [](T& self, py::object const& points, py::object const& colors) {
            auto* ctx = context_from(self);
            auto sz = py::len(colors);
            auto&& fn = points.attr("__getitem__");
            auto&& cfn = colors.attr("__getitem__");
            for (size_t i = 0; i < sz; i++) {
                auto x = fn(i * 2).cast<float>();
                auto y = fn(i * 2 + 1).cast<float>();
                auto col = gl::Color(cfn(i).cast<uint32_t>());
                ctx->plot(Vec2f(x, y), col);
            }
        },
        py::arg("points"), py::arg("colors"),
        "Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.");
    cls.def(
        "rect",
        [](T& self, Vec2f const& xy, Vec2f const& size) {
            context_from(self)->rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a rectangle.");

    cls.def(
        "filled_rect",
        [](T& self, Vec2f const& xy, Vec2f const& size) {
            context_from(self)->filled_rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a filled rectangle.");

    cls.def(
        "draw",
        [](T& self, gl::TexRef& tr, std::optional<Vec2f> xy,
           std::optional<Vec2f> center, Vec2f size, float rot) {
            context_from(tr)->flush();
            pix::Context* ctx = context_from(self);
            if (center) {
                ctx->draw(tr, *center, size, rot);
            } else if (xy) {
                ctx->blit(tr, *xy, size);
            } else {
                ctx->blit(tr, {0, 0}, size);
            }
        },
        "image"_a, "top_left"_a = std::nullopt, "center"_a = std::nullopt,
        "size"_a = Vec2f{0, 0}, "rot"_a = 0,
        "Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.");
    cls.def(
        "draw",
        [](T& self, FullConsole& con, Vec2f const& xy, Vec2f const& size) {
            con.render2(context_from(self), xy, size);
        },
        "drawable"_a, "top_left"_a = Vec2f{0, 0}, "size"_a = Vec2f{0, 0});
    cls.def(
        "clear",
        [](T& self, uint32_t color) { context_from(self)->clear(color); },
        "color"_a = color::black, "Clear the context using given color.");
    cls.def_property(
        "draw_color", [](T& self) { return context_from(self)->fg.to_rgba(); },
        [](T& self, uint32_t color) { context_from(self)->set_color(color); },
        "Set the draw color.");
    cls.def_property(
        "point_size", [](T& self) { return context_from(self)->point_size; },
        [](T& self, float lw) { context_from(self)->point_size = lw; },
        "Set the point size in fractional pixels.");
    cls.def_property(
        "line_width", [](T& self) { return context_from(self)->line_width; },
        [](T& self, float lw) { context_from(self)->line_width = lw; },
        "Set the line with in fractional pixels.");
    cls.def_property_readonly("context",
                              [](T& tr) { return context_from(tr); });
    cls.def_property(
        "clip_top_left", [](T& self) { return context_from(self)->clip_start; },
        [](T& self, Vec2i xy) { context_from(self)->clip_start = xy; });
    cls.def_property(
        "clip_size", [](T& self) { return context_from(self)->clip_size; },
        [](T& self, Vec2i xy) { context_from(self)->clip_size = xy; });
    cls.def_property_readonly(
        "size", [](T& self) { return context_from(self)->target_size; });
    cls.def_property_readonly(
        "target_size", [](T& self) { return context_from(self)->target_size; });
    cls.def(
        "set_pixel",
        [](T& self, Vec2i pos, uint32_t color) {
            context_from(self)->set_pixel(pos.x, pos.y, color);
        },
        "pos"_a, "color"_a, "Write a pixel into the image.");
    cls.def(
        "flush", [](T& self) { context_from(self)->flush(); },
        "Flush pixel operations");
}
inline auto add_context_class(py::module_ const& mod)
{
    using namespace pybind11::literals;

    return py::class_<pix::Context, std::shared_ptr<pix::Context>>(mod,
                                                                   "Context")
        .def(py::init<>(&make_context), "size"_a = Vec2f{0, 0})
        .def("copy", &pix::Context::copy);
}
