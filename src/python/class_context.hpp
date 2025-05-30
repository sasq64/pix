#pragma once

#include "../colors.hpp"
#include "../gl/texture.hpp"
#include "../machine.hpp"
#include "../vec2.hpp"
#include "full_console.hpp"
#include "image_view.hpp"

#include <optional>
#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <string>
#include <tuple>

namespace py = pybind11;

// inline std::shared_ptr<pix::Context> make_context(Vec2f size)
// {
//     if (size.x == 0 && size.y == 0) {
//         size = Vec2f{Machine::get_instance().screen->get_size()};
//     }
//     return std::make_shared<pix::Context>(size.x, size.y);
// }

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

inline pix::Context* context_from(pix::Screen& screen)
{
    return &screen;
}

inline pix::Context* context_from(pix::Context& context)
{
    return &context;
}

inline auto add_context_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    using namespace pybind11::literals;

    auto cls = py::class_<pix::Context, std::shared_ptr<pix::Context>>(mod,
                                                                   "Context")
        //.def(py::init<>(&make_context), "size"_a = Vec2f{0, 0})
        .def("copy", &pix::Context::copy, "Make a copy of the context.");

    cls.def(
        "circle",
        [](pix::Context& self, Vec2f const& center, float r) {
            context_from(self)->circle(center, r);
        },
        "center"_a, "radius"_a, "Draw an (outline) circle");

    cls.def(
        "filled_circle",
        [](pix::Context& self, Vec2f const& center, float r) {
            context_from(self)->filled_circle(center, r);
        },
        "center"_a, "radius"_a, "Draw a filled circle.");

    cls.def(
        "line",
        [](pix::Context& self, Vec2f const& from, Vec2f const& to) {
            context_from(self)->line(from, to);
        },
        "start"_a, "end"_a, "Draw a line between start and end.");

    cls.def(
        "line", [](pix::Context& self, Vec2f const& to) { context_from(self)->line(to); },
        "end"_a,
        "Draw a line from the end of the last line to the given position.");

    cls.def(
        "lines", [](pix::Context& self, std::vector<Vec2f> const& points) { context_from(self)->lines(points); },
        "points"_a,
        "Draw a line strip from all the given points.");

    cls.def(
        "polygon",
        [](pix::Context& self, std::vector<Vec2f> const& points, bool convex) {
            if (convex) {
                context_from(self)->draw_polygon(points.data(),
                                                          points.size());
            } else {
                context_from(self)->draw_inconvex_polygon(points.data(),
                                                          points.size());
            }
        },
        "points"_a, "convex"_a = false, "Draw a filled polygon. If convex is `true` the polygon is rendered as a simple triangle fan, otherwise the polygon is split into triangles using the ear-clipping method.");
    cls.def(
        "complex_polygon",
        [](pix::Context& self, std::vector<std::vector<Vec2f>> const& polygons) {
                context_from(self)->draw_complex_polygon(polygons);
        },
        "polygons"_a, "Draw a complex filled polygon that can consist of holes.");
    cls.def(
        "plot",
        [](pix::Context& self, Vec2f const& to, uint32_t color) {
            context_from(self)->plot(to, gl::Color(color));
        },
        "center"_a, "color"_a, "Draw a point.");

    cls.def(
        "plot",
        [](pix::Context& self, py::object const& points, py::object const& colors) {
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
        [](pix::Context& self, Vec2f const& xy, Vec2f const& size) {
            context_from(self)->rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a rectangle.");

    cls.def(
        "filled_rect",
        [](pix::Context& self, Vec2f const& xy, Vec2f const& size) {
            context_from(self)->filled_rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a filled rectangle.");

    cls.def(
        "draw",
        [](pix::Context& self, pix::ImageView& tr, std::optional<Vec2f> xy,
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
        [](pix::Context& self, FullConsole& con, Vec2f const& xy, Vec2f const& size) {
            con.render2(context_from(self), xy, size);
        },
        "drawable"_a, "top_left"_a = Vec2f{0, 0}, "size"_a = Vec2f{0, 0},
        "Render a console. `top_left` and `size` are in pixels. If `size` is "
        "not given, it defaults to `tile_size*grid_size`.\n\nTo render a full screen console "
        "(scaling as needed):\n\n`console.render(screen.context, size=screen.size)`");
    cls.def(
        "clear",
        [](pix::Context& self, uint32_t color) { context_from(self)->clear(color); },
        "color"_a = color::black, "Clear the context using given color.");
    cls.def_property(
        "draw_color", [](pix::Context& self) { return context_from(self)->fg.to_rgba(); },
        [](pix::Context& self, uint32_t color) { context_from(self)->set_color(color); },
        "Set the draw color.");
    cls.def_property(
        "blend_mode", [](pix::Context& self) { return context_from(self)->fg.to_rgba(); },
        [](pix::Context& self, uint32_t mode) { context_from(self)->set_blend_mode(mode); },
        "Set the blend mode. Normally one of the constants `pix.BLEND_ADD`, `pix.BLEND_MULTIPLY` or `pix.BLEND_NORMAL`.");
    cls.def_property(
        "point_size", [](pix::Context& self) { return context_from(self)->point_size; },
        [](pix::Context& self, float lw) { context_from(self)->point_size = lw; },
        "Set the point size in fractional pixels.");
    cls.def_property(
        "line_width", [](pix::Context& self) { return context_from(self)->line_width; },
        [](pix::Context& self, float lw) { context_from(self)->line_width = lw; },
        "Set the line with in fractional pixels.");
    cls.def_property_readonly("context",
                              [](pix::Context& tr) { return context_from(tr); });
    cls.def_property(
        "clip_top_left", [](pix::Context& self) { return context_from(self)->clip_start; },
        [](pix::Context& self, Vec2i xy) { context_from(self)->clip_start = xy; });
    cls.def_property(
        "clip_size", [](pix::Context& self) { return context_from(self)->clip_size; },
        [](pix::Context& self, Vec2i xy) { context_from(self)->clip_size = xy; });
    cls.def_property(
        "scale", [](pix::Context& self) { return context_from(self)->target_scale; },
        [](pix::Context& self, Vec2f xy) { context_from(self)->target_scale = xy; });
    cls.def_property(
        "offset", [](pix::Context& self) { return context_from(self)->offset; },
        [](pix::Context& self, Vec2f xy) { context_from(self)->offset = xy; },
    "The offset into a the context this context was created from, if any.");
    cls.def_property_readonly(
        "size", [](pix::Context& self) { return context_from(self)->target_size; },
    "The size of this context in pixels");
    cls.def_property_readonly(
        "target_size", [](pix::Context& self) { return context_from(self)->target_size; });
    cls.def(
        "set_pixel",
        [](pix::Context& self, Vec2i pos, uint32_t color) {
            context_from(self)->set_pixel(pos.x, pos.y, color);
        },
        "pos"_a, "color"_a, "Write a pixel into the image.");
    cls.def(
        "flush", [](pix::Context& self) { context_from(self)->flush(); },
        "Flush pixel operations");
    cls.def(
        "get_pointer", [](pix::Context& self) {
            auto ctx = context_from(self);
            auto xy = Vec2f{Machine::get_instance().sys->get_pointer()};
            return (xy - ctx->offset) / ctx->target_scale;
        },
        "Get the xy coordinate of the mouse pointer (in context space).");

    cls.doc() = "A `Context` is used for rendering. It is implemented by both `Screen` and `Image`.";
    return cls;
}

