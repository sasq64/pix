
#include "gl/texture.hpp"

#include "context.hpp"
#include "pixel_console.hpp"
#include "font.hpp"
#include "image.hpp"
#include "machine.hpp"
#include "system.hpp"
#include "vec2.hpp"
#include "colors.hpp"

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

std::vector<Vec2f> star
{
    {500.0, 250.0}, {351.13, 323.47}, {327.25, 487.76}, {211.37, 368.88},
    {47.75, 396.95}, {125.0, 250.0}, {47.75, 103.05}, {211.37, 131.12},
    {327.25, 12.24}, { 351.13, 176.53 }
};

int main()
{
    std::vector<uint32_t> colors { color::blue, color::red, color::yellow};

    for (int i=0; i<20; i++) {
        auto d = (float)i / 20;
        auto col = color::blend_colors(colors, d);
        printf("%.2f -> %08x\n", d, col);
    }

    auto sys = create_glfw_system();

    int cols = 60;
    int rows = 45;

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

   // while(true) {
        //if(!sys->run_loop()) { break; }
        //context-set_target();
        context->clear(0x000000);
        //context->blit(bg,  {0,0}, Vec2f{bg.tex->size()});
        //console->render();
        std::vector<Vec2f> points {
            {100, 100},
            {900, 200},
            {700, 500},
            {200, 400}
        };
        context->set_color(gl::Color(0xff0000ff));
        context->draw_inconvex_polygon(star.data(), star.size());

        context->set_color(gl::Color(0xffff00ff));
        for(auto&& p : star) {
            context->line(p);
        }
        context->line(star[0]);
        //context->filled_rect({10, 10}, {100,100});
        screen->swap();
   // }

    while(sys->run_loop()) {}
}
