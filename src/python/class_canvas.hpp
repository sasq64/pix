#pragma once

#include "../colors.hpp"
#include "../machine.hpp"
#include "../vec2.hpp"
#include "full_console.hpp"
#include "image_view.hpp"

#include <optional>
#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;

inline auto add_canvas_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    using Context = pix::Context;

    auto cls = py::class_<Context, std::shared_ptr<Context>>(mod, "Canvas")
                   .def("copy", &Context::copy, "Make a copy of the self.");
    cls.doc() =
        "A `Canvas` is used for rendering. It is implemented by both `Screen` and `Image`.";
    return cls;
}

inline void add_canvas_functions(auto& cls)
{
    using namespace pybind11::literals;
    using Context = pix::Context;
    cls.def("log_to", &Context::log_to, "path"_a,
            "Log draw commands to this file");
    cls.def("circle", &Context::circle, "center"_a, "radius"_a,
            "Draw an (outline) circle");

    cls.def("filled_circle", &Context::filled_circle, "center"_a, "radius"_a,
            "Draw a filled circle.");

    cls.def(
        "begin_lines", &Context::begin_lines,
        "Clear the last line point. The next call to `line(p)` or `rounded_line(p, r)` will start a new line sequence.");
    cls.def(
        "rounded_line",
        [](Context& self, Vec2f const& from, float r0, Vec2f const& to,
           float r1) { self.round_line(from, r0, to, r1); },
        "start"_a, "rad0"_a, "end"_a, "rad1"_a,
        "Draw a line between start and end.");

    cls.def(
        "rounded_line",
        [](Context& self, Vec2f const& to, float r) { self.round_line(to, r); },
        "end"_a, "radius"_a,
        "Draw a line from the end of the last line to the given position.");

    cls.def(
        "line",
        [](Context& self, Vec2f const& from, Vec2f const& to) {
            self.line(from, to);
        },
        "start"_a, "end"_a, "Draw a line between start and end.");

    cls.def(
        "line", [](Context& self, Vec2f const& to) { self.line(to); }, "end"_a,
        "Draw a line from the end of the last line to the given position.");

    cls.def("lines", &Context::lines, "points"_a,
            "Draw a line strip from all the given points.");

    cls.def(
        "polygon",
        [](Context& self, std::vector<Vec2f> const& points, bool convex) {
            if (convex) {
                self.draw_polygon(points.data(), points.size());
            } else {
                self.draw_inconvex_polygon(points.data(), points.size());
            }
        },
        "points"_a, "convex"_a = false,
        "Draw a filled polygon by stringing together the given points. If convex is `true` the polygon is rendered as a simple triangle fan, otherwise the polygon is split into triangles using the ear-clipping method.");
    cls.def("complex_polygon", &Context::draw_complex_polygon, "contours"_a,
            "Draw a complex filled polygon that can consist of holes.");
    cls.def(
        "plot",
        [](Context& self, Vec2f const& to, uint32_t color) {
            self.plot(to, gl::Color(color));
        },
        "center"_a, "color"_a, "Draw a point.");

    cls.def(
        "plot",
        [](Context& self, py::object const& points, py::object const& colors) {
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
        [](Context& self, Vec2f const& xy, Vec2f const& size) {
            self.rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a rectangle.");

    cls.def(
        "filled_rect",
        [](Context& self, Vec2f const& xy, Vec2f const& size) {
            self.filled_rect(xy, size);
        },
        "top_left"_a, "size"_a, "Draw a filled rectangle.");

    cls.def(
        "draw",
        [](Context& self, pix::ImageView& tr, std::optional<Vec2f> xy,
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
        [](Context& self, FullConsole& con, Vec2f const& xy,
           Vec2f const& size) { con.render2(&self, xy, size); },
        "drawable"_a, "top_left"_a = Vec2f{0, 0}, "size"_a = Vec2f{0, 0},
        "Render a console. `top_left` and `size` are in pixels. If `size` is "
        "not given, it defaults to `tile_size*grid_size`.\n\nTo render a full screen console "
        "(scaling as needed):\n\n`console.render(screen, size=screen.size)`");
    cls.def(
        "clear",
        [](pix::Context const& self, uint32_t color) { self.clear(color); },
        "color"_a = color::black, "Clear the canvas using given color.");
    cls.def_property(
        "draw_color", [](Context const& self) { return self.fg.to_rgba(); },
        [](Context& self, uint32_t color) { self.set_color(color); },
        "Set the draw color.");
    cls.def_property(
        "blend_mode", [](Context const& self) { return self.fg.to_rgba(); },
        [](Context& self, uint32_t mode) { self.set_blend_mode(mode); },
        "Set the blend mode. Normally one of the constants `BLEND_ADD`, `BLEND_MULTIPLY` or `BLEND_NORMAL`.");
    cls.def_readwrite("point_size", &Context::point_size,
                      "Set the point size in fractional pixels.");
    cls.def_readwrite("line_width", &Context::line_width,
                      "Set the line with in fractional pixels.");
    // cls.def_readwrite("clip_top_left", &Context::clip_start);
    // cls.def_readwrite("clip_size", &Context::clip_size);
    cls.def_readwrite("scale", &Context::target_scale);
    cls.def_readwrite(
        "backface_culling", &Context::backface_culling,
        "If true, backward facing polygons will not be rendered.");
    cls.def_readwrite(
        "offset", &Context::offset,
        "The offset into a the source canvas this canvas was created from, if any.");
    cls.def_readonly("size", &Context::target_size,
                     "The size of this canvas in pixels");
    cls.def_readonly("target_size", &Context::target_size);
    cls.def(
        "set_pixel",
        [](Context& self, Vec2i pos, uint32_t color) {
            self.set_pixel(pos.x, pos.y, color);
        },
        "pos"_a, "color"_a, "Write a pixel into the image.");
    cls.def(
        "flood_fill",
        [](Context& self, Vec2i pos, uint32_t color) {
            self.flood_fill(pos.x, pos.y, color);
        },
        "pos"_a, "color"_a, "Flood fill starting from the given position with the specified color.");
    cls.def("flush", &Context::flush, "Flush pixel operations");
    cls.def("to_image", &Context::to_image,
            "Create a new image from this canvas");
    cls.def(
        "get_pointer",
        [](Context const& self) {
            auto xy = Vec2f{Machine::get_instance().sys->get_pointer()};
            return (xy - self.offset) / self.target_scale;
        },
        "Get the xy coordinate of the mouse pointer (in canvas space).");
}
