#pragma once

#include "gl/color.hpp"
#include "gl/functions.hpp"
#include "gl/gl.hpp"
#include "gl/program.hpp"
#include "gl/texture.hpp"

#include "vec2.hpp"
#include "font.hpp"
#include "context.hpp"

#include <string>
#include <tuple>
#include <unordered_map>

class TileSet
{
    int texture_width = 256 * 4;
    int texture_height = 256 * 4;
    static const int gap = 0;
    std::shared_ptr<FreetypeFont> font_ptr;
    std::pair<int, int> next_pos{0, 0};
    std::array<uint32_t, 0xffff> char_array;

    void init();
    std::pair<int, int> alloc_char(char32_t c);

public:
    std::unordered_map<char32_t, uint32_t> char_uvs;
    std::unordered_map<uint32_t, char32_t> reverse_chars;
    std::shared_ptr<gl::Texture> tile_texture;
    int char_width = -1;
    int char_height = -1;

    gl::TexRef get_texture() { return gl::TexRef{tile_texture}; }

    TileSet(std::string const& font_file, int size,
                std::pair<int, int> tile_size = {-1, -1});
    explicit TileSet(std::shared_ptr<FreetypeFont> freetype_font,
                         std::pair<int, int> tile_size = {-1, -1});
    explicit TileSet(std::pair<int, int> tile_size);
    uint32_t get_offset(char32_t c);

    char32_t get_char_from_uv(uint32_t uv);

    gl::TexRef get_texture_for_char(char32_t c);

    std::pair<float, float> get_uvscale() const;
    void add_char(char32_t c);
    std::pair<int, int> get_size() const;

    void render_chars(pix::Context* context, std::string const& tiles, Vec2f pos, Vec2f size);
    void render_chars(pix::Context* context, std::string const& tiles, std::vector<Vec2f> const& points);

    void render_tiles(pix::Context* context, int32_t const* tiles, size_t n, Vec2f pos, Vec2f size);
    void render_tiles(pix::Context* context, int32_t const* tiles, std::vector<Vec2f> const& points);
};
