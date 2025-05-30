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

inline auto add_context_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    using namespace pybind11::literals;

    auto cls = py::class_<pix::Context, std::shared_ptr<pix::Context>>(mod,
                                                                   "Context")
        //.def(py::init<>(&make_context), "size"_a = Vec2f{0, 0})
        .def("copy", &pix::Context::copy, "Make a copy of the self.");

    cls.def(
        "circle",
        [](pix::Context& self, Vec2f const& center, float r) {
            self.circle(center, r);
        },
        "center"_a, "radius"_a, "Draw an (outline) circle");

    cls.def(
        "filled_circle",
        [](pix::Context& self, Vec2f const& center, float r) {
            self.filled_circle(center, r);
        },
        "center"_a, "radius"_a, "Draw a filled circle.");

    cls.def(
        "line",
        [](pix::Context& self, Vec2f const& from, Vec2f const& to) {
            self.line(from, to);
        },
        "start"_a, "end"_a, "Draw a line between start and end.");

    cls.def(
        "line", [](pix::Context& self, Vec2f const& to) { self.line(to); },
        "end"_a,
        "Draw a line from the end of the last line to the given position.");

    cls.def(
        "lines", [](pix::Context& self, std::vector<Vec2f> const& points) { self.lines(points); },
        "points"_a,
        "Draw a line strip from all the given points.");

    cls.def(
        "polygon",
        [](pix::Context& self, std::vector<Vec2f> const& points, bool convex) {
            if (convex) {
                self.draw_polygon(points.data(),
                                                          points.size());
            } else {
                self.draw_inconvex_polygon(points.data(),
                                                          points.size());
            }
        },
        "points"_a, "convex"_a = false, "Draw a filled polygon. If convex is `true` the polygon is rendered as a simple triangle fan, otherwise the polygon is split into triangles using the ear-clipping method.");
    cls.def(
        "complex_polygon",
        [](pix::Context& self, std::vector<std::vector<Vec2f>> const& polygons) {
                self.draw_complex_polygon(polygons);
        },
        "polygons"_a, "Draw a complex filled polygon that can consist of holes.");
    cls.def(
        "plot",
        [](pix::Context& self, Vec2f const& to, uint32_t color) {
            self.plot(to, gl::Color(color));
        },
        "center"_a, "color"_a, "Draw a point.");

    cls.def(
        "plot",
        [](pix::Context& self, py::object const& points, py::object const& colors) {
            auto sz = py::len(colors);
            auto&& fn = points.attr("__getitem__");
            auto&& cfn = colors.attr("__getitem__");
            for (size_t i = 0; i < sz; i++) {
                auto x = fn(i * 2).cast<float>();
                auto y = fn(i * 2 + 1).cast<float>();
                auto col = gl::Color(cfn(i).cast<uint32_t>());
                self.plot(Vec2f(x, y), col);
            }
        },
        py::arg("points"), py::arg("colors"),
        "Draw `n` points given by the array like objects. `points` should n*2 floats and `colors` should contain `n` unsigned ints.");
    cls.def(
        "rect",
        [](pix::Context& self, Vec2f const& xy, Vec2f const& size) {
            self.rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a rectangle.");

    cls.def(
        "filled_rect",
        [](pix::Context& self, Vec2f const& xy, Vec2f const& size) {
            self.filled_rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a filled rectangle.");

    cls.def(
        "draw",
        [](pix::Context& self, pix::ImageView& tr, std::optional<Vec2f> xy,
           std::optional<Vec2f> center, Vec2f size, float rot) {
            tr.flush();
            if (center) {
                self.draw(tr, *center, size, rot);
            } else if (xy) {
                self.blit(tr, *xy, size);
            } else {
                self.blit(tr, {0, 0}, size);
            }
        },
        "image"_a, "top_left"_a = std::nullopt, "center"_a = std::nullopt,
        "size"_a = Vec2f{0, 0}, "rot"_a = 0,
        "Render an image. The image can either be aligned to its top left corner, or centered, in which case it can also be rotated.");
    cls.def(
        "draw",
        [](pix::Context& self, FullConsole& con, Vec2f const& xy, Vec2f const& size) {
            con.render2(&self, xy, size);
        },
        "drawable"_a, "top_left"_a = Vec2f{0, 0}, "size"_a = Vec2f{0, 0},
        "Render a console. `top_left` and `size` are in pixels. If `size` is "
        "not given, it defaults to `tile_size*grid_size`.\n\nTo render a full screen console "
        "(scaling as needed):\n\n`console.render(screen.context, size=screen.size)`");
    cls.def(
        "clear",
        [](pix::Context& self, uint32_t color) { self.clear(color); },
        "color"_a = color::black, "Clear the context using given color.");
    cls.def_property(
        "draw_color", [](pix::Context& self) { return self.fg.to_rgba(); },
        [](pix::Context& self, uint32_t color) { self.set_color(color); },
        "Set the draw color.");
    cls.def_property(
        "blend_mode", [](pix::Context& self) { return self.fg.to_rgba(); },
        [](pix::Context& self, uint32_t mode) { self.set_blend_mode(mode); },
        "Set the blend mode. Normally one of the constants `pix.BLEND_ADD`, `pix.BLEND_MULTIPLY` or `pix.BLEND_NORMAL`.");
    cls.def_property(
        "point_size", [](pix::Context& self) { return self.point_size; },
        [](pix::Context& self, float lw) { self.point_size = lw; },
        "Set the point size in fractional pixels.");
    cls.def_property(
        "line_width", [](pix::Context& self) { return self.line_width; },
        [](pix::Context& self, float lw) { self.line_width = lw; },
        "Set the line with in fractional pixels.");
    cls.def_property_readonly("context",
                              [](pix::Context& self) { return &self; });
    cls.def_property(
        "clip_top_left", [](pix::Context& self) { return self.clip_start; },
        [](pix::Context& self, Vec2i xy) { self.clip_start = xy; });
    cls.def_property(
        "clip_size", [](pix::Context& self) { return self.clip_size; },
        [](pix::Context& self, Vec2i xy) { self.clip_size = xy; });
    cls.def_property(
        "scale", [](pix::Context& self) { return self.target_scale; },
        [](pix::Context& self, Vec2f xy) { self.target_scale = xy; });
    cls.def_property(
        "offset", [](pix::Context& self) { return self.offset; },
        [](pix::Context& self, Vec2f xy) { self.offset = xy; },
    "The offset into a the context this context was created from, if any.");
    cls.def_property_readonly(
        "size", [](pix::Context& self) { return self.target_size; },
    "The size of this context in pixels");
    cls.def_property_readonly(
        "target_size", [](pix::Context& self) { return self.target_size; });
    cls.def(
        "set_pixel",
        [](pix::Context& self, Vec2i pos, uint32_t color) {
            self.set_pixel(pos.x, pos.y, color);
        },
        "pos"_a, "color"_a, "Write a pixel into the image.");
    cls.def(
        "flush", [](pix::Context& self) { self.flush(); },
        "Flush pixel operations");
    cls.def(
        "get_pointer", [](pix::Context& self) {
            auto xy = Vec2f{Machine::get_instance().sys->get_pointer()};
            return (xy - self.offset) / self.target_scale;
        },
        "Get the xy coordinate of the mouse pointer (in context space).");

    cls.doc() = "A `Context` is used for rendering. It is implemented by both `Screen` and `Image`.";
    return cls;
}

