#include "image.hpp"

#include <lodepng.h>

#include <cstdint>
#include <filesystem>
#include <fstream>
#include <istream>

#include "gl/buffer.hpp"
#include "gl/texture.hpp"
#include "jpeg_decoder.h"

namespace fs = std::filesystem;

namespace pix {

template <typename Result = std::string, typename Stream>
static Result read_all(Stream& in)
{
    Result contents;
    auto here = in.tellg();
    in.seekg(0, std::ios::end);
    contents.resize(in.tellg() - here);
    in.seekg(here, std::ios::beg);
    in.read(reinterpret_cast<char*>(contents.data()), contents.size());
    in.close();
    return contents;
}

Image load_jpg(fs::path const& name)
{
    std::ifstream jpg_file;
    jpg_file.open(name, std::ios::binary);
    auto data = read_all<std::vector<uint8_t>>(jpg_file);
    jpeg::Decoder decoder{data.data(), data.size()};

    Image image{decoder.GetWidth(), decoder.GetHeight()};
    auto* rgb = decoder.GetImage();
    auto* ptr = reinterpret_cast<uint8_t*>(image.ptr);
    for (int i = 0; i < image.width * image.height; i++) {
        auto j = i * 3;
        ptr[i] =
            (rgb[j + 2] << 16) | (rgb[j + 1] << 8) | (rgb[j]) | (0xff000000);
    }
    return image;
}

Image load_png_image(fs::path const& name)
{
    Image image;
    std::byte* out{};
    unsigned w = 0;
    unsigned h = 0;
    auto err = lodepng_decode32_file(reinterpret_cast<unsigned char**>(&out),
                                     &w, &h, name.string().c_str());
    if (err != 0) {
        throw pix_exception("Could not load image: " + name.string());
    }
    image.width = static_cast<int>(w);
    image.height = static_cast<int>(h);
    image.sptr = std::shared_ptr<std::byte[]>(out, &free);
    image.ptr = out;
    image.format = GL_RGBA;
    return image;
}

gl_wrap::TexRef load_png(fs::path const& file_name)
{
    auto image = pix::load_png_image(file_name);
    image.flip();

    auto tex = std::make_shared<gl_wrap::Texture>(
        image.width, image.height, image.ptr, GL_RGBA, image.format);
    return gl_wrap::TexRef{tex};
}

void save_png(Image const& image, std::string_view name)
{
    auto* ptr = reinterpret_cast<unsigned char*>(image.ptr);
    lodepng_encode_file(std::string(name).c_str(), ptr, image.width,
                        image.height, LCT_RGBA, 8);
}

} // namespace pix
