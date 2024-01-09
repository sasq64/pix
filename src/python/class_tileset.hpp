#pragma once

#include "../machine.hpp"
#include "../tile_set.hpp"
#include "../vec2.hpp"

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

inline std::shared_ptr<TileSet> make_tileset2(Vec2f size)
{
    return std::make_shared<TileSet>(std::pair{size.x, size.y});
}
inline void add_tileset_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    auto ts = py::class_<TileSet, std::shared_ptr<TileSet>>(mod, "TileSet")
        .def(py::init<>(&make_tileset), "font_file"_a, "size"_a,
             "Create a TileSet from a ttf font with the given size. The tile "
             "size will be derived from the font size.")
        .def(py::init<>(&make_tileset2), "tile_size"_a,
             "Create a tileset with the given tile size.")
        .def("get_image_for", &TileSet::get_texture_for_char,
             "Get the image for a specific tile. Use `copy_to()` on the image "
             "to redefine that tile with new graphics. Will allocate a new "
             "tile if necessary. Will throw an exception if there is no room "
             "for the new tile in the tile texture.");
    ts.doc() = "A tileset is a texture split up into tiles for rendering.";
}
