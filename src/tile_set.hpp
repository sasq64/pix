#pragma once

#include "gl/texture.hpp"

#include "context.hpp"
#include "font.hpp"
#include "vec2.hpp"

#include <string>
#include <unordered_map>

class TileSet
{
    int texture_width = 256 * 4;
    int texture_height = 256 * 4;
    static constexpr int gap = 0;
    std::shared_ptr<FreetypeFont> font_ptr;
    int pixel_size = -1;
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
    Vec2i distance;

    [[nodiscard]] gl::TexRef get_texture() const
    {
        return gl::TexRef{tile_texture};
    }

    //TileSet(std::string const& font_file, int size = -1,
    //        std::pair<int, int> tile_size = {-1, -1});
    explicit TileSet(std::shared_ptr<FreetypeFont> freetype_font, int size = -1,
                     std::pair<int, int> tile_size = {-1, -1}, Vec2i distance = {0, 0});
    explicit TileSet(std::pair<int, int> tile_size);
    uint32_t get_offset(char32_t c);

    char32_t get_char_from_uv(uint32_t uv);

    pix::ImageView get_texture_for_char(char32_t c);

    [[nodiscard]] std::pair<float, float> get_uvscale() const;
    void add_char(char32_t c);
    //[[nodiscard]] std::pair<int, int> get_size() const;

    void render_chars(pix::Context& context, std::string const& tiles,
                      Vec2f pos, Vec2f size);
    void render_chars(pix::Context& context, std::string const& tiles,
                      std::vector<Vec2f> const& points);

    void render_tiles(pix::Context& context, int32_t const* tiles, size_t count,
                      Vec2f pos, Vec2f size);
    void render_tiles(pix::Context& context, int32_t const* tiles,
                      std::vector<Vec2f> const& points);
};
