
#include "gl/texture.hpp"

#include "context.hpp"
#include "pixel_console.hpp"
#include "font.hpp"
#include "image.hpp"
#include "machine.hpp"
#include "system.hpp"
#include "vec2.hpp"

#include <array>
#include <filesystem>
#include <format>
#include <fstream>
#include <istream>

namespace fs = std::filesystem;

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

static std::vector<uint8_t> read_file(fs::path name)
{
    std::ifstream jpg_file;
    jpg_file.open(name, std::ios::binary);
    return read_all<std::vector<uint8_t>>(jpg_file);
}

int main()
{
    auto sys = create_glfw_system();

    int cols = 40;
    int rows = 25;

    auto screen = sys->init_screen({
        .screen = ScreenType::Window,
        .display_width = cols * 8 * 2,
        .display_height = rows * 8 * 2});

    auto [realw, realh] = screen->get_size();
    auto context = std::make_shared<pix::Context>(realw, realh, 0);
    context->vpscale = screen->get_scale();

    std::vector<uint32_t> pixels(realw*realh);
    for (auto y = 0; y<realh ; y++) {
        for (auto x = 0; x<realw ; x++) {
            pixels[x+y*realw] = 0xff00ffff;
        }
    }

    auto bg = gl::TexRef(realw, realh);
    bg.tex->update(pixels.data());

    auto font = std::make_shared<TileSet>(FreetypeFont::unscii);
    auto console = std::make_shared<PixConsole>(cols, rows, font);

    for (auto y = 0; y<rows ; y++) {
        for (auto x = 0; x<cols ; x++) {
            console->put_char(x, y, '0' + x + y);
        }
    }

    while(true) {
        if(!sys->run_loop()) { break; }
        //context-set_target();
        context->blit(bg,  {0,0}, Vec2f{bg.tex->size()});
        console->render();
        screen->swap();
    }

}
