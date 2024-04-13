#pragma once

#include "../vec2.hpp"

#include "../gl/texture.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <memory>
#include <string>
#include <tuple>

namespace py = pybind11;

inline std::vector<gl::TexRef> split_wh(gl::TexRef img, int cols, int rows,
                                        int w, int h)
{
    if (cols < 0) { cols = static_cast<int>(img.width() / w); }
    if (rows < 0) { rows = static_cast<int>(img.height() / h); }
    return img.split(cols, rows);
}

inline std::vector<gl::TexRef> split_size(gl::TexRef img, Vec2f const& size)
{
    auto cols = img.width() / size.x;
    auto rows = img.height() / size.y;
    return img.split(static_cast<int>(cols), static_cast<int>(rows));
}

inline gl::TexRef image_from_vec2(Vec2f const& v)
{
    return {static_cast<int>(v.x), static_cast<int>(v.y)};
}
inline gl::TexRef image_from_pixels(int width,
                                    std::vector<uint32_t> pixels)
{
    // RGBA -> becomes ABGR 
    for(auto& x : pixels) {
        x = (x & 0x0000FFFF) << 16 | (x & 0xFFFF0000) >> 16;
        x = (x & 0x00FF00FF) << 8 | (x & 0xFF00FF00) >> 8;  
    }
    auto tex = std::make_shared<gl::Texture>(
        width, static_cast<int>(pixels.size()) / width, pixels);
    return gl::TexRef{tex};
}

inline gl::TexRef crop(gl::TexRef img, std::optional<Vec2f> xy_,
                       std::optional<Vec2f> size_)
{
    auto xy = xy_.value_or(Vec2f(0, 0));
    auto d = Vec2f{img.width(), img.height()} - xy;
    auto size = size_.value_or(d);
    return img.crop(xy.x, xy.y, size.x, size.y);
}

inline auto add_image_class(py::module_ const& mod)
{
    using namespace pybind11::literals;

    // Image
    return py::class_<gl::TexRef>(mod, "Image")
        .def(py::init<int32_t, int32_t>(), "width"_a, "height"_a,
             "Create an empty image of the given size.")
        .def(py::init<>(&image_from_vec2), "size"_a,
             "Create an empty image of the given size.")
        .def(py::init<>(&image_from_pixels), "width"_a, "pixels"_a,
             "Create an image from an array of 32-bit colors.")
        .def("split", &split_wh, "cols"_a = -1, "rows"_a = -1, "width"_a = 8,
             "height"_a = 8,
             "Splits the image into as many _width_ * _height_ images as "
             "possible, first going left to right, then top to bottom.")
        .def("split", &split_size, "size"_a)
        .def("set_texture_filter", &gl::TexRef::set_texture_filter, "min"_a, "max"_a,
             "Set whether the texture should apply linear filtering.")
        //.def("bind", &gl::TexRef::bind, "unit"_a = 0)
        .def("crop", &crop, "top_left"_a = std::nullopt,
             "size"_a = std::nullopt,
             "Crop an image. Returns a view into the old image.")
        .def("copy_from", &gl::TexRef::copy_from, "image"_a,
             "Render one image into another.")
        .def("copy_to", &gl::TexRef::copy_to, "image"_a,
             "Render one image into another.")
        //.def("set_as_target", &gl::TexRef::set_target)
        .def_property_readonly(
            "pos", [](gl::TexRef const& t) { return Vec2f(t.x(), t.y()); },
            "The position of this image in its texture. Will normally be (0, "
            "0) unless this image was split or cropped from another image.")
        .def_property_readonly(
            "size",
            [](gl::TexRef const& t) { return Vec2f(t.width(), t.height()); },
            "Size of the image in (fractional) pixels.")
        .def_property_readonly("width", &gl::TexRef::width)
        .def_property_readonly("height", &gl::TexRef::height);
}
