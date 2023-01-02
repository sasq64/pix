#include "font.hpp"

#include "unscii-16.h"

std::shared_ptr<FreetypeFont> FreetypeFont::unscii{
    std::make_shared<FreetypeFont>(data_unscii_16_ttf, data_unscii_16_ttf_len, 16)};
void FreetypeFont::set_pixel_size(int h)
{
    FT_Set_Pixel_Sizes(face, 0, h);

    if (FT_Load_Char(face, 0x2588, FT_LOAD_NO_BITMAP) != 0) {
        FT_Load_Char(face, '%', FT_LOAD_NO_BITMAP);
    }
    //printf("%d - %d\n", face->ascender >> 6, face->descender >> 6);

    auto m = face->glyph->metrics;
    size = {m.width >> 6, m.height >> 6};
}

template <typename T>
void FreetypeFont::copy_char(T* target, uint32_t color, FT_Bitmap b, int xoffs,
                       int yoffs, int stride, int width, int height)
{

    for (unsigned y = 0; y < b.rows; y++) {
        for (unsigned x = 0; x < b.width; x++) {
            auto* row = &b.buffer[b.pitch * y];
            auto alpha = mono ? ((row[x >> 3] & (128 >> (x & 7))) ? 0xff : 0)
                              : b.buffer[x + y * b.pitch];
            int xo = x + xoffs;
            int yo = y + yoffs;
            if (xo < 0 || yo < 0 || xo >= width || yo >= height) { continue; }
            if constexpr (sizeof(T) == 1) {
                target[xo + yo * stride] = alpha;
            } else {
                target[xo + yo * stride] = (color >> 8) | (alpha << 24);
            }
        }
    }
}

template <typename T>
std::pair<int, int> FreetypeFont::render_text(std::string_view txt, T* target,
                                        uint32_t color, int stride, int width,
                                        int height)
{
    FT_Pos pen_x = 0;
    auto delta = face->size->metrics.ascender / 64;
    auto low = face->size->metrics.descender / 64;
    if (target != nullptr) { memset(target, 0, width * height * 4); }

    auto text32 = utf8::utf8_decode(txt);

    for (auto c : text32) {
        auto error = FT_Load_Char(face, c, FT_LOAD_RENDER);
        FT_GlyphSlot slot = face->glyph;
        if (error) { continue; } /* ignore errors */
        // fmt::print("{}x{} pixels to y={}\n", slot->bitmap.width,
        // slot->bitmap.rows, delta - face->glyph->bitmap_top);
        if (target) {
            copy_char(target, color, slot->bitmap, pen_x + slot->bitmap_left,
                      delta - face->glyph->bitmap_top, stride, width, height);
        }
        pen_x += slot->advance.x >> 6;
    }
    return {pen_x, delta - low};
}

std::pair<int, int> FreetypeFont::text_size(std::string_view txt)
{
    return render_text(txt, static_cast<uint8_t*>(nullptr), 0, 0, 0, 0);
}

template <typename T>
int FreetypeFont::render_char(char32_t c, T* target, uint32_t color, int stride,
                        int width, int height)
{
    using namespace std::string_literals;
    mono = false;
    if (FT_Load_Char(face, c,
                     FT_LOAD_RENDER | (mono ? FT_LOAD_MONOCHROME : 0)) != 0) {
        return 0;
    }
    auto b = face->glyph->bitmap;
    //printf("%d %d\n", b.width, b.rows);
    auto delta = face->size->metrics.ascender / 64;
    auto xoffs = face->glyph->bitmap_left;
    auto yoffs = delta - face->glyph->bitmap_top;

    // fmt::print("'{}' ({},{}) + {}x{}  {},{}\n"s, (char)c, xoffs, yoffs,
    // b.width, b.rows, face->glyph->advance.x, face->glyph->metrics.width);

    copy_char(target, color, b, xoffs, yoffs, stride, width, height);

    return xoffs + static_cast<int>(b.width);
}

template int FreetypeFont::render_char(char32_t c, uint32_t* target, uint32_t color,
                                 int stride, int width, int height);

template std::pair<int, int>
FreetypeFont::render_text(std::string_view txt,
                                                 uint32_t* target,
                                                 uint32_t color, int stride,
                                                 int width, int height);

FreetypeFont::FreetypeFont(const unsigned char* data, size_t data_size, int size)
{
    using namespace std::string_literals;
    FT_Init_FreeType(&library);
    auto rc = FT_New_Memory_Face(library, data, static_cast<FT_Long>(data_size),
                                 0, &face);
    if (rc != 0) { throw font_exception("Could not load font from memory"); }

    if (size >= 0) { set_pixel_size(size); }
}

FreetypeFont::FreetypeFont(const char* name, int size)
{
    using namespace std::string_literals;
    if (library == nullptr) { FT_Init_FreeType(&library); }
    auto rc = FT_New_Face(library, name, 0, &face);
    if (rc != 0) { throw font_exception("Could not load font:"s + name); }

    if (size >= 0) { set_pixel_size(size); }
}

std::pair<int, int> FreetypeFont::get_size(char32_t c) const
{

    if (FT_Load_Char(face, c, FT_LOAD_NO_BITMAP) == 0) {
        auto m = face->glyph->metrics;
        return {m.width >> 6, m.height >> 6};
    }
    return {0,0};
}
