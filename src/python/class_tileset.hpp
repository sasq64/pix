#pragma once

#include "../machine.hpp"
#include "../tile_set.hpp"
#include "../vec2.hpp"
#include "class_context.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <filesystem>
#include <memory>
#include <string>
#include <tuple>

namespace py = pybind11;

inline std::shared_ptr<TileSet> make_tileset(std::string const& font_file,
                                             int size)
{
    return std::make_shared<TileSet>(font_file, size);
}

inline std::shared_ptr<TileSet> make_tileset3(std::shared_ptr<FreetypeFont> const& font, Vec2i tile_size)
{
    auto ts = std::pair<int, int>{tile_size.x, tile_size.y};
    return std::make_shared<TileSet>(font, ts);
}

inline std::shared_ptr<TileSet> make_tileset2(Vec2f size)
{
    return std::make_shared<TileSet>(std::pair{size.x, size.y});
}

inline gl::TexRef get_image_for(std::shared_ptr<TileSet> self, int32_t tile)
{
    return self->get_texture_for_char(tile);
}

inline void render_chars(std::shared_ptr<TileSet> self, std::shared_ptr<Screen> screen, std::string const& text, Vec2f pos)
{
    self->render_chars(context_from(*screen), text, pos);
};

inline void render_chars2(std::shared_ptr<TileSet> self, std::shared_ptr<Screen> screen, std::string const& text, std::vector<Vec2f> points)
{
    self->render_chars(context_from(*screen), text, points);
};

template<typename T>
void render(std::shared_ptr<TileSet> self, T& screen, py::object const& points) {
      auto* ctx = context_from(screen);
      auto sz = py::len(points);
      auto&& fn = points.attr("__getitem__");
      for (size_t i = 0; i < sz; i++) {
          //auto x = fn(i * 2).cast<float>();
          //auto y = fn(i * 2 + 1).cast<float>();
          auto pos = fn(i).cast<Vec2f>();
      }
}

inline void add_tileset_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    auto ts = py::class_<TileSet, std::shared_ptr<TileSet>>(mod, "TileSet")
        .def(py::init<>(&make_tileset), "font_file"_a, "size"_a,
             "Create a TileSet from a ttf font with the given size. The tile "
             "size will be derived from the font size.")
        .def(py::init<>(&make_tileset3), "font"_a, "tile_size"_a = Vec2i{-1, -1},
             "Create a TileSet from an existing font. The tile "
             "size will be derived from the font size.")
        .def(py::init<>(&make_tileset2), "tile_size"_a,
             "Create an empty tileset with the given tile size.")
        .def("get_tileset_image", &TileSet::get_texture, "Get tileset image")
        .def("get_image_for", &get_image_for,
            "Get the image for a specific tile. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room "
            "for the new tile in the tile texture.")
        .def("render_text", &render_chars)
        .def("render_text", &render_chars2)
        .def("get_image_for", &TileSet::get_texture_for_char,
             "Get the image for a specific character. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.");
    ts.doc() = "A tileset is a texture split up into tiles for rendering.";
}
