#pragma once

#include "../font.hpp"
#include "../gl/texture.hpp"
#include "../image.hpp"
#include "../vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <memory>
#include <string>

namespace py = pybind11;

inline gl::TexRef text_to_image(FreetypeFont& font, std::string const& text,
                                int size, uint32_t color)
{
    font.set_pixel_size(size);
    auto [w, h] = font.text_size(text);
    pix::Image img(w, h);
    color = ((color & 0x0000ff00) << 16) | (color & 0xff0000) |
            ((color & 0xff000000) >> 16);
    font.render_text(text, reinterpret_cast<uint32_t*>(img.ptr), color,
                     img.width, img.width, img.height);
    img.flip();
    auto tex = std::make_shared<gl::Texture>(img.width, img.height,
                                                  img.ptr, GL_RGBA, img.format);
    return gl::TexRef{tex};
}

inline auto add_font_class(py::module_ const& mod)
{
    py::class_<FreetypeFont, std::shared_ptr<FreetypeFont>>(mod, "Font")
        .def("make_image", &text_to_image, py::arg("text"), py::arg("size"),
             py::arg("color") = 0xffffffff,
             "Create an image containing the given text.")
        .def_readonly_static("UNSCII_FONT", &FreetypeFont::unscii,
                             "Get a reference to the built in unscii font.");
}
