#pragma once

#include "../font.hpp"
#include "../gl/texture.hpp"
#include "../image.hpp"

//#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <memory>
#include <string>

namespace py = pybind11;

static std::unordered_map<std::string, std::shared_ptr<gl::Texture>> font_images;

inline pix::ImageView text_to_image(FreetypeFont& font, std::string const& text,
                                int size, uint32_t color)
{
    const auto id = text + "::" + std::to_string(size) + "::" + std::to_string(color);

    std::shared_ptr<gl::Texture> tex;

    if (const auto it = font_images.find(id); it == font_images.end()) {
        font.set_pixel_size(size);
        auto [w, h] = font.text_size(text);
        pix::Image img(w, h);
        color = ((color & 0x0000ff00) << 16) | (color & 0xff0000) |
                ((color & 0xff000000) >> 16);
        font.render_text(text, reinterpret_cast<uint32_t*>(img.ptr), color,
                         img.width, img.width, img.height);
        img.flip();
        tex = std::make_shared<gl::Texture>(img.width, img.height,
                                                      img.ptr, GL_RGBA, img.format);
        // TODO: Intentionally leak texture here because gl context will normally be destroyed
        //       before statics
        new std::shared_ptr(tex);
        font_images[id] = tex;


    } else {
        tex = it->second;
    }
    return pix::ImageView{gl::TexRef{tex}};
}

inline std::shared_ptr<FreetypeFont> make_font(std::string const& font_name)
{
    return std::make_shared<FreetypeFont>(font_name.c_str(), 16);
}

inline auto add_font_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    py::class_<FreetypeFont, std::shared_ptr<FreetypeFont>>(mod, "Font")
        .def(py::init<>(&make_font), "font_file"_a = "",
             "Create a font from a TTF file.")
        .def("make_image", &text_to_image, py::arg("text"), "size"_a,
             "color"_a = 0xffffffff,
             "Create an image containing the given text.")
        .def_readonly_static("UNSCII_FONT", &FreetypeFont::unscii,
                             "Get a reference to the built in unscii font.")
        .doc() = "Represents a TTF (Freetype) font that can be used to create text images.";
}
