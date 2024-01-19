#pragma once

#include "gl/gl.hpp"
#include "gl/texture.hpp"

#include <algorithm>
#include <cstddef>
#include <filesystem>
#include <memory>
#include <string>

namespace pix {

class pix_exception : public std::exception
{
public:
    explicit pix_exception(std::string m = "pix exception") : msg(std::move(m))
    {
    }
    [[nodiscard]] const char* what() const noexcept override { return msg.c_str(); }

private:
    std::string msg;
};

struct Image
{
    Image() = default;
    Image(int w, int h)
        : width(w),
          height(h), sptr{new std::byte[static_cast<size_t>(w) * h * 4]},
          ptr{sptr.get()}, format{GL_RGBA}
    {
    }
    Image(int w, int h, std::byte* p, unsigned f = 0)
        : width(w), height(h), sptr{nullptr}, ptr{p}, format{f}
    {
    }

    void flip() const
    {
        for (int y = 0; y < height / 2; y++) {
            auto* one = ptr + y * width * 4;
            auto* two = ptr + (height - 1 - y) * width * 4;
            std::swap_ranges(one, one + width * 4, two);
        }
    }

    int width = 0;
    int height = 0;
    std::shared_ptr<std::byte[]> sptr;
    std::byte* ptr = nullptr;
    unsigned format = 0;
};

gl::TexRef load_png(std::filesystem::path const& name);
Image load_jpg(std::filesystem::path const& name);
void save_png(Image const& image, std::string_view name);

} // namespace pix
