#pragma once

#include "../full_console.hpp"
#include "../machine.hpp"
#include "../vec2.hpp"

#include "utf8.h"

#include <optional>
#include <pybind11/detail/common.h>
#include <pybind11/pybind11.h>

#include <filesystem>
#include <memory>
#include <string>
#include <utility>

namespace py = pybind11;
namespace fs = std::filesystem;

inline std::shared_ptr<FullConsole>
make_console(int32_t cols, int32_t rows,
             std::optional<fs::path> const& font_file, Vec2f const& tile_size,
             int font_size)
{
    bool have_font = font_file.has_value();

    auto ts = std::pair<int, int>{tile_size.x, tile_size.y};
    if (!have_font && ts.first < 0) {
        ts = {8, 16};
        font_size = 16;
    }

    auto s = font_file->string();
    auto font = !have_font ? FreetypeFont::unscii
                           : std::make_shared<FreetypeFont>(s.c_str(),
                                                            font_size);

    auto tile_set = std::make_shared<TileSet>(font, font_size, ts);
    auto con = std::make_shared<PixConsole>(cols, rows, tile_set);
    auto fcon = std::make_shared<FullConsole>(con, Machine::get_instance().sys);

    return fcon;
}
inline std::shared_ptr<FullConsole>
make_console2(int32_t cols, int32_t rows,
              std::shared_ptr<TileSet> const& tile_set)
{
    auto con = std::make_shared<PixConsole>(cols, rows, tile_set);
    auto fcon = std::make_shared<FullConsole>(con, Machine::get_instance().sys);
    return fcon;
}

inline auto add_console_class(py::module_ const& mod)
{
    // Console
    return py::class_<FullConsole, std::shared_ptr<FullConsole>>(mod,
                                                                 "Console");
}

inline void add_console_functions(auto& cls)
{
    using namespace pybind11::literals;
    cls.def(
           py::init<>(&make_console), "cols"_a, "rows"_a,
           "font_file"_a = std::nullopt, "tile_size"_a = Vec2i{-1, -1},
           "font_size"_a = -1,
           "Create a new Console holding `cols`*`rows` tiles.\n\n`font_file` is the file name of a TTF font to use as backing. If no font is given, the built in _Unscii_ font will be used.\n\n`tile_size` sets the size in pixels of each tile. If not given, it will be derived from the size of a character in the font with the provided `font_size`.")
        .def(
            py::init<>(&make_console2), "cols"_a, "rows"_a, "tile_set"_a,
            "Create a new Console holding `cols`*`row` tiles. Use the provided `tile_set`.")
        .def(
            "put", &FullConsole::put, "pos"_a, "tile"_a, "fg"_a = std::nullopt,
            "bg"_a = std::nullopt,
            "Put `tile` at given position, optionally setting a specific foreground and/or background color")
        .def("get", &FullConsole::get, "Get tile at position")
        .def_readwrite("cursor_color", &FullConsole::cursor_color, "Cursor color.")
        .def_readwrite("fg_color", &FullConsole::fg, "Foreground color.")
        .def_readwrite("bg_color", &FullConsole::bg, "Background color.")
        .def_readwrite("cursor_on", &FullConsole::cursor_on,
                       "Determine if the cursor should be visible.")
        .def_readwrite("wrap_lines", &FullConsole::wrap_lines,
                       "Should we wrap when writing passing right edge?")
        .def_readwrite(
            "autoscroll", &FullConsole::autoscroll,
            "Should we scroll console upwards when writes pass bottom edge?")
        .def_property(
            "cursor_pos", &FullConsole::get_cursor, &FullConsole::set_cursor,
            "The current location of the cursor. This will be used when calling `write()`.")
        .def(
            "get_tiles", &FullConsole::get_tiles,
            "Get all the tiles and colors as an array of ints. Format is: `[tile0, fg0, bg0, tile1, fg1, bg1 ...]` etc.")
        .def("set_tiles", &FullConsole::set_tiles, "tiles"_a,
             "Set tiles from an array of ints.")
        .def("clear", &FullConsole::clear, "Clear the console.")
        .def("set_color", &FullConsole::set_color, "fg"_a, "bg"_a,
             "Set the default colors used when putting/writing to the console.")
        .def_property_readonly("grid_size", &FullConsole::get_size,
                               "Get number cols and rows.")
        .def_property_readonly("tile_size", &FullConsole::get_tile_size,
                               "Get size of a single tile.")
        .def_readonly("reading_line", &FullConsole::reading_line,
                      "True if console is in read_line mode at the moment.")
        .def_property_readonly(
            "size", &FullConsole::get_pixel_size,
            "Get size of consoles in pixels (tile_size * grid_size).")
        .def(
            "read_line", &FullConsole::read_line,
            "Puts the console in line edit mode.\n\nA cursor will be shown and all text events will be captured by the console until `Enter` is pressed. At this point the entire line will be pushed as a `TextEvent`.")
        .def("cancel_line", &FullConsole::stop_line, "Stop line edit mode.")
        .def("set_line", &FullConsole::set_line, "text"_a,
             "Change the edited line.")
        .def("get_font_image", &FullConsole::get_font_texture)
        .def(
            "clear_area", &FullConsole::clear_area, "x"_a, "y"_a, "w"_a, "h"_a,
            "Clear the given rectangle, setting the current foreground and background colors.")
        .def(
            "set_device_no", &FullConsole::set_device, "devno"_a,
            "Set the device number that will be reported for TextEvents from this console.")
        .def(
            "get_image_for", &FullConsole::get_texture_for_char, "tile"_a,
            "Get the image of a specific tile. Use to render the tile manually, or to copy another image into the tile;\n\n`console.get_image_for(1024).copy_from(some_tile_image)`.")
        .def(
            "write",
            [](FullConsole& con, std::vector<char32_t> const& data) {
                con.write(utf8::utf8_encode(data));
            },
            "tiles"_a)
        .def(
            "write",
            static_cast<void (FullConsole::*)(std::string const&)>(
                &FullConsole::write),
            "text"_a,
            "Write text to the console at the current cursor position and using the current colors. Will advance cursor position, and wrap if it passes the right border of the console.")
        .def("set_tile_images", &FullConsole::set_tile_images, "start_no"_a,
             "images"_a,
             "Set images to use for a set of indexes, starting at `start_no`.")
        .def(
            "set_readline_callback", &FullConsole::set_readline_callback,
            "callback"_a,
            "Sets a cllback that will be called when a line of text was entered by the user. Setting this will stop the normal TextEvent from being sent.")
        .def(
            "colorize_section", &FullConsole::colorize, "x"_a, "y"_a, "width"_a,
            "Colorize the given area with the current foreground and background color, without changing the characters")
        .doc() = "A console is a 2D grid of tiles that can be rendered.";
}
