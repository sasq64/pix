#pragma once

#include "class_context.hpp"

#include "../full_console.hpp"
#include "../machine.hpp"
#include "../vec2.hpp"

#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <filesystem>
#include <memory>
#include <string>
#include <tuple>

namespace py = pybind11;
namespace fs = std::filesystem;

inline std::shared_ptr<FullConsole> make_console(int32_t cols, int32_t rows,
                                                 std::string const& font_file,
                                                 Vec2f const& tile_size,
                                                 int font_size)
{
    fs::path p{font_file};

    auto ts = std::pair<int, int>{tile_size.x, tile_size.y};
    auto font = font_file.empty()
                    ? std::make_shared<TileSet>(FreetypeFont::unscii, ts)
                    : std::make_shared<TileSet>(p.string(), font_size, ts);

    auto con = std::make_shared<PixConsole>(cols, rows, font);
    auto fcon = std::make_shared<FullConsole>(con, Machine::get_instance().sys);

    return fcon;
}
inline std::shared_ptr<FullConsole> make_console2(int32_t cols, int32_t rows,
                                                  std::shared_ptr<TileSet> const& tile_set)
{
    auto con = std::make_shared<PixConsole>(cols, rows, tile_set);
    auto fcon = std::make_shared<FullConsole>(con, Machine::get_instance().sys);
    return fcon;
}

inline void add_console_class(py::module_ const& mod)
{
    using namespace pybind11::literals;
    // Console
    py::class_<FullConsole, std::shared_ptr<FullConsole>>(mod, "Console")
        .def(py::init<>(&make_console), "cols"_a = 80, "rows"_a = 50,
             "font_file"_a = "", "tile_size"_a = Vec2i{-1, -1},
             "font_size"_a = 16,
             "Create a new Console holding `cols`*`rows` tiles.\n\n`font_file` is the file name of a TTF font to use as backing. If no font is given, the built in _Unscii_ font will be used.\n\n`tile_size` sets the size in pixels of each tile. If not given, it will be derived from the size of a character in the font with the provided `font_size`")
        .def(py::init<>(&make_console2), "cols"_a = 80, "rows"_a = 50,
             "tile_set"_a,
             "Create a new Console holding `cols`*`row` tiles. Use the provided `tile_set`.")
        .def("render", &FullConsole::render, "context"_a, "pos"_a = Vec2f(0, 0),
             "size"_a = Vec2f(-1, -1), "Render the console using the context. `pos` and `size` are in pixels. If `size` is not given, it defaults to `tile_size*grid_size`.\n\nTo render a full screen console (scaling as needed):\n\n`console.render(screen.context, size=screen.size)`")
        .def("put", &FullConsole::put, "pos"_a, "tile"_a, "fg"_a = std::nullopt,
             "bg"_a = std::nullopt,
             "Put `tile` at given position, optionally setting a specific foreground "
             "and/or background color")
        .def("get", &FullConsole::get, "Get tile at position")
        .def_readwrite("fg_color", &FullConsole::fg,
                       "Foreground color.")
        .def_readwrite("bg_color", &FullConsole::fg,
                       "Background color.")
        .def_readwrite("cursor_on", &FullConsole::cursor_on,
                       "Determine if the cursor should be visible.")
        .def_readwrite("wrapping", &FullConsole::wrap,
                       "Should we wrap when passing right edge (and scroll when passing bottom edge) ?")
        .def_property("cursor_pos", &FullConsole::get_cursor,
                      &FullConsole::set_cursor,
                      "The current location of the cursor. This will be used "
                      "when calling `write()`.")
        .def("get_tiles", &FullConsole::get_tiles,
             "Get all the tiles and colors as an array of ints. Format is: "
             "`[tile0, fg0, bg0, tile1, fg1, bg1 ...]` etc.")
        .def("set_tiles", &FullConsole::set_tiles, "tiles"_a,
             "Set tiles from an array of ints.")
        .def("clear", &FullConsole::clear, "Clear the console.")
        .def("set_color", &FullConsole::set_color, "fg"_a, "bg"_a,
             "Set the default colors used when putting/writing to the console.")
        .def_property_readonly("grid_size", &FullConsole::get_size,
                               "Get number cols and rows")
        .def_property_readonly("tile_size", &FullConsole::get_tile_size,
                               "Get size of a single tile")
        .def_property_readonly("size", &FullConsole::get_pixel_size,
                               "Get size of consoles in pixels (tile_size * grid_size)")
        .def("read_line", &FullConsole::read_line,
             "Puts the console in line edit mode.\n\nA cursor will be shown and all text events will be captured by the console until `Enter` is pressed. At this point the entire line will be pushed as a `TextEvent`.")
        .def("cancel_line", &FullConsole::stop_line, "Stop line edit mode.")
        .def("set_line", &FullConsole::set_line, "text"_a,
             "Change the edited line.")
        .def("get_font_image", &FullConsole::get_font_texture)
        .def("get_image_for", &FullConsole::get_texture_for_char, "tile"_a,
             "Get the image of a specific tile. Use to render the tile manually, or to copy another image into the tile;\n\n`console.get_image_for(1024).copy_from(some_tile_image)`")
        .def(
            "write",
            [](FullConsole& con, std::vector<char32_t> const& data) {
                con.write(utf8::utf8_encode(data));
            },
            "tiles"_a)
        .def("write",
             static_cast<void (FullConsole::*)(std::string const&)>(
                 &FullConsole::write),
             "text"_a,
             "Write text to the console at the current cursor position and using the current colors. Will advance cursor position, and wrap if it passes the right border of the console.")
        .doc() = "A console is a 2D grid of tiles that can be rendered.";
}
