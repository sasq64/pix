#pragma once

#include "tile_set.hpp"

#include "gl/color.hpp"
#include "gl/functions.hpp"
#include "gl/gl.hpp"
#include "gl/program.hpp"
#include "gl/texture.hpp"

#include <string>
#include <tuple>
#include <unordered_map>

class PixConsole
{
    static std::string vertex_shader;
    static std::string fragment_shader;

    gl::Program program;

    std::shared_ptr<TileSet> tile_set;

    int cols;
    int rows;

    gl::Texture uv_texture;
    gl::Texture col_texture;

    std::vector<uint32_t> uvdata;
    std::vector<uint32_t> coldata;

    bool uv_dirty = false;
    bool col_dirty = false;

    static constexpr std::pair<uint32_t, uint32_t> make_col(uint32_t fg,
                                                            uint32_t bg)
    {
        bg >>= 8;
        return std::pair<uint32_t, uint32_t>{
            fg & 0xffff0000, ((bg & 0xff) << 16) | (bg & 0xff00) | (bg >> 16) |
                                 ((fg << 16) & 0xff000000)};
    }

    void init();

public:
    PixConsole(int _cols, int _rows, std::shared_ptr<TileSet> const& _tile_set);

    std::vector<uint32_t> get_tiles();
    void set_tiles(std::vector<uint32_t> const& data);

    std::pair<int, int> get_size() const { return {cols, rows}; }
    template <typename T = int> std::pair<T, T> get_char_size() const;
    std::pair<int, int> get_pixel_size() const;

    std::shared_ptr<gl::Texture> get_font_texture() const
    {
        return tile_set->tile_texture;
    }

    gl::TexRef get_texture_for_char(char32_t c)
    {
        return tile_set->get_texture_for_char(c);
    }

    std::pair<int, int> text(int x, int y, std::string const& t,
                             uint32_t fg = 0xffffffff, uint32_t bg = 0);
    std::pair<int, int> text(int x, int y, std::u32string const& t,
                             uint32_t fg = 0xffffffff, uint32_t bg = 0);
    std::pair<int, int> text(std::pair<int, int> pos,
                             std::u32string const& text32,
                             uint32_t fg = 0xffffffff, uint32_t bg = 0);

    void put(int x, int y, uint32_t fg, uint32_t bg, char32_t c);
    void put_char(int x, int y, char32_t c);

    uint32_t get_char(int x, int y);

    void put_color(int x, int y, uint32_t fg, uint32_t bg);

    void fill(uint32_t fg, uint32_t bg);

    void fill(uint32_t bg);

    void clear_area(int32_t x, int32_t y, int32_t w, int32_t h, uint32_t fg,
                    uint32_t bg);

    void scroll(int dy, int dx);

    void render(float x0 = -1, float y0 = 1, float x1 = 1, float y1 = -1);

    template <typename F, typename S>
    void render(F const& offset, S const& scale)
    {
        auto [ox, oy] = offset;
        auto [sx, sy] = scale;
        render(ox, oy, sx, sy);
    }
};
