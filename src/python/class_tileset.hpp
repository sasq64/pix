#pragma once

#include "../machine.hpp"
#include "../tile_set.hpp"
#include "../vec2.hpp"
#include "class_canvas.hpp"
#include "image_view.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <filesystem>
#include <memory>
#include <string>
#include <tuple>

namespace py = pybind11;

inline std::shared_ptr<TileSet> make_tileset(std::string const& font_file,
                                             int size, Vec2i tile_size, Vec2i dist)
{
    auto font = std::make_shared<FreetypeFont>(font_file.c_str(), size);
    auto ts = std::pair<int, int>{tile_size.x, tile_size.y};
    return std::make_shared<TileSet>(font, size, ts, dist);
}

inline std::shared_ptr<TileSet>
make_tileset3(std::shared_ptr<FreetypeFont> const& font, int size,
              Vec2i tile_size, Vec2i dist)
{
    auto ts = std::pair<int, int>{tile_size.x, tile_size.y};
    return std::make_shared<TileSet>(font, size, ts, dist);
}

inline std::shared_ptr<TileSet> make_tileset2(Vec2f size)
{
    return std::make_shared<TileSet>(std::pair{size.x, size.y});
}

inline pix::ImageView get_image_for(std::shared_ptr<TileSet> self, int32_t tile)
{
    return self->get_texture_for_char(tile);
}

inline void render_chars(std::shared_ptr<TileSet> self,
                         std::shared_ptr<pix::Screen> screen,
                         std::string const& text, Vec2f pos, Vec2f size)
{
    self->render_chars(*screen, text, pos, size);
};

inline void render_chars2(std::shared_ptr<TileSet> self,
                          std::shared_ptr<pix::Screen> screen,
                          std::string const& text, std::vector<Vec2f> points)
{
    self->render_chars(*screen, text, points);
};

template <typename T>
void render(std::shared_ptr<TileSet> self, T& screen, py::object const& points)
{
    auto* ctx = context_from(screen);
    auto sz = py::len(points);
    auto&& fn = points.attr("__getitem__");
    for (size_t i = 0; i < sz; i++) {
        // auto x = fn(i * 2).cast<float>();
        // auto y = fn(i * 2 + 1).cast<float>();
        auto pos = fn(i).cast<Vec2f>();
    }
}

inline pix::ImageView get_texture(TileSet* ts)
{
    return pix::ImageView{ts->get_texture()};
}

inline void add_tileset_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    auto ts = py::class_<TileSet, std::shared_ptr<TileSet>>(mod, "TileSet");
    ts.def(
          py::init<>(&make_tileset), "font_file"_a, "size"_a = -1,
          "tile_size"_a = Vec2i{-1, -1}, "distance"_a = Vec2i{0,0},
          "Create a TileSet from a ttf font with the given size. The tile size will be derived from the font size.")
        .def(
            py::init<>(&make_tileset3), "font"_a, "size"_a = -1,
            "tile_size"_a = Vec2i{-1, -1}, "distance"_a = Vec2i{0,0},
            "Create a TileSet from an existing font. The tile size will be derived from the font size.")
        .def(py::init<>(&make_tileset2), "tile_size"_a,
             "Create an empty tileset with the given tile size.")
        .def(
            "get_tileset_image", &get_texture,
            "Get the entire tileset image. Typically used with `save_png()` to check generated tileset.")
        .def(
            "get_image_for", &get_image_for, "tile"_a,
            "Get the image for a specific tile. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room."
            "for the new tile in the tile texture.")
        .def(
            "render_text", &render_chars, "screen"_a, "text"_a, "pos"_a,
            "size"_a = Vec2f{0, 0},
            "Render characters from the TileSet at given `pos` and given `size` (defaults to tile_size).")
        .def(
            "render_text", &render_chars2, "screen"_a, "text"_a, "points"_a,
            "Render characters from the TileSet, each character using the next position from `points`, using the default tile size.")
        .def(
            "get_image_for", &TileSet::get_texture_for_char, "character"_a,
            "Get the image for a specific character. Use `copy_to()` on the image to redefine that tile with new graphics. Will allocate a new tile if necessary. Will throw an exception if there is no room for the new tile in the tile texture.")
        .def_property_readonly("tile_size", [](TileSet const& ts) {
            return Vec2i(ts.char_width, ts.char_height);
        });
    ts.doc() =
        "A tileset is a texture split up into tiles for rendering. It is used by the `Console` class but can also be used directly.";
}
