#pragma once

#include "../gl/texture.hpp"
#include "../vec2.hpp"
#include "image_view.hpp"

// #include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <memory>

namespace py = pybind11;

inline std::vector<pix::ImageView> split_wh(pix::ImageView img, int cols,
                                            int rows, int w, int h)
{
    if (cols < 0) { cols = static_cast<int>(img.width() / w); }
    if (rows < 0) { rows = static_cast<int>(img.height() / h); }
    return img.split(cols, rows);
}

inline std::vector<pix::ImageView> split_size(pix::ImageView img,
                                              Vec2f const& size)
{
    auto cols = img.width() / size.x;
    auto rows = img.height() / size.y;
    return img.split(static_cast<int>(cols), static_cast<int>(rows));
}

inline pix::ImageView image_from_vec2(Vec2f const& v)
{
    return {static_cast<int>(v.x), static_cast<int>(v.y)};
}
inline pix::ImageView image_from_pixels(int width, std::vector<uint32_t> pixels)
{
    // RGBA -> becomes ABGR
    for (auto& x : pixels) {
        x = (x & 0x0000FFFF) << 16 | (x & 0xFFFF0000) >> 16;
        x = (x & 0x00FF00FF) << 8 | (x & 0xFF00FF00) >> 8;
    }
    auto tex = std::make_shared<gl::Texture>(
        width, static_cast<int>(pixels.size()) / width, pixels);
    return pix::ImageView{gl::TexRef{tex}};
}

inline pix::ImageView crop(pix::ImageView img, std::optional<Vec2f> xy_,
                           std::optional<Vec2f> size_)
{
    auto xy = xy_.value_or(Vec2f(0, 0));
    auto d = Vec2f{img.width(), img.height()} - xy;
    auto size = size_.value_or(d);
    return img.crop(xy.x, xy.y, size.x, size.y);
}

inline auto add_image_class(py::module_ const& mod, auto ctx_class)
{
    using namespace pybind11::literals;
    const char* doc;

    auto c =
        py::class_<pix::ImageView>(mod, "Image", ctx_class)
            .def(py::init<int32_t, int32_t>(), "width"_a, "height"_a,
                 doc = "Create an empty image of the given size.")
            .def(py::init<>(&image_from_vec2), "size"_a, doc)
            .def(py::init<>(&image_from_pixels), "width"_a, "pixels"_a,
                 "Create an image from an array of 32-bit colors.")
            .def(
                "split", &split_wh, "cols"_a = -1, "rows"_a = -1, "width"_a = 8,
                "height"_a = 8,
                "Splits the image into as many _width_ * _height_ images as possible, first going left to right, then top to bottom.")
            .def("split", &split_size, "size"_a,
                 "Split the image into exactly size.x * size.y images.")
            .def(
                "update",
                [](pix::ImageView& img, py::bytes pixels) {
                    char* buffer;
                    ssize_t length;
                    if (PYBIND11_BYTES_AS_STRING_AND_SIZE(pixels.ptr(), &buffer,
                                                          &length)) {
                        throw std::runtime_error("Failed to extract bytes");
                    }
                    if (length > img.get_tex().tex->size()) {
                        throw std::runtime_error("Data too large!");
                    }
                    img.get_tex().tex->update((uint32_t*)buffer);
                },
                "pixels"_a,
                "Update the texture with a raw buffer that must fit the texture format.")
            .def("set_texture_filter", &pix::ImageView::set_texture_filter,
                 "min"_a, "max"_a,
                 "Set whether the texture should apply linear filtering.")
            .def("crop", &crop, "top_left"_a = std::nullopt,
                 "size"_a = std::nullopt,
                 "Crop an image. Returns a view into the old image.")
            .def("copy_from", &pix::ImageView::copy_from, "image"_a,
                 "Render another image into this one.")
            .def("copy_to", &pix::ImageView::copy_to, "image"_a,
                 "Render this image into another.")
            .def_property_readonly(
                "pos",
                [](pix::ImageView const& t) { return Vec2f(t.x(), t.y()); },
                "The position of this image in its texture. Will normally be (0, 0) unless this image was split or cropped from another image.")
            .def_property_readonly(
                "size",
                [](pix::ImageView const& t) {
                    return Vec2f(t.width(), t.height());
                },
                "Size of the image in (fractional) pixels.")
            .def_property_readonly("width", &pix::ImageView::width)
            .def_property_readonly("height", &pix::ImageView::height);
    c.doc() =
        "A (GPU Side) _image_, represented by a texture reference and 4 UV coordinates. Images works like arrays in the sense that it is cheap to create new views into images (using crop(), split() etc).";
    return c;
}
