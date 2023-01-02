#pragma once

#include "utf8.h"

#include <freetype/fttypes.h>
#include <ft2build.h>

#include <cstdint>
#include <memory>
#include <string>
#include <type_traits>

#include FT_FREETYPE_H
#include FT_SIZES_H

class font_exception : public std::exception
{
public:
    explicit font_exception(std::string m = "Font exception")
        : msg(std::move(m))
    {
    }
    const char* what() const noexcept override { return msg.c_str(); }

private:
    std::string msg;
};

class FreetypeFont
{
    static inline FT_Library library = nullptr;
    FT_Face face = nullptr;
    bool mono = false;
    std::pair<int, int> size;

public:
    static std::shared_ptr<FreetypeFont> unscii;

    FreetypeFont(const char* name, int size);
    FreetypeFont(FreetypeFont const&&) = delete;
    FreetypeFont& operator=(FreetypeFont const&) = delete;
    FreetypeFont(const unsigned char* data, size_t data_size, int size);

    std::pair<int, int> get_size() const { return size; }
    std::pair<int, int> get_size(char32_t c) const;
    void set_pixel_size(int h);
    template <typename T>
    void copy_char(T* target, uint32_t color, FT_Bitmap bitmap, int xoffs,
                   int yoffs, int stride, int width, int height);

    template <typename T>
    std::pair<int, int> render_text(std::string_view txt, T* target,
                                    uint32_t color, int stride, int width,
                                    int height);
    std::pair<int, int> text_size(std::string_view txt);
    template <typename T>
    int render_char(char32_t c, T* target, uint32_t color, int stride,
                    int width, int height);
};
