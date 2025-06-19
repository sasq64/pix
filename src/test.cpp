#include "full_console.hpp"
#include "gl/texture.hpp"

#include "context.hpp"
#include "pixel_console.hpp"
#include "tile_set.hpp"
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


template<typename Result = std::string, typename Stream>
static Result read_all(Stream &in) {
    Result contents;
    auto here = in.tellg();
    in.seekg(0, std::ios::end);
    contents.resize(in.tellg() - here);
    in.seekg(here, std::ios::beg);
    in.read(reinterpret_cast<char *>(contents.data()), contents.size());
    in.close();
    return contents;
}

static std::vector<uint8_t> read_file(fs::path name) {
    std::ifstream jpg_file;
    jpg_file.open(name, std::ios::binary);
    return read_all<std::vector<uint8_t> >(jpg_file);
}

auto star = std::vector<Vec2f>{
    {500.0, 250.0}, {351.13, 323.47}, {327.25, 487.76}, {211.37, 368.88},
    {47.75, 396.95}, {125.0, 250.0}, {47.75, 103.05}, {211.37, 131.12},
    {327.25, 12.24}, {351.13, 176.53}
};

int main() {

    //init_treesitter();
    //return 0;

    //constexpr std::array colors{color::blue, color::red, color::yellow};
    constexpr std::array colors{0x800000ffU, 0xff0000ffU, 0x00ff00ffU};

    for (int i = 0; i < 20; i++) {
        auto d = static_cast<float>(i) / 20;
        auto col = color::blend_colors(colors, d);
    }

    auto sys = std::shared_ptr(create_glfw_system());

    int cols = 60;
    int rows = 45;

    auto display = sys->init_screen({
        .screen = DisplayType::Window,
        .display_width = 960,
        .display_height = 720,
    });


    auto screen = std::make_shared<pix::Screen>(display);


    auto [realw, realh] = screen->get_size();
    //auto context = std::make_shared<pix::Context>(realw, realh, 0);
    screen->vpscale = screen->get_scale();


    auto ts = std::make_shared<TileSet>(std::pair{48,48});
    auto consolex = std::make_shared<PixConsole>(40, 1, ts);
    auto full_con = std::make_shared<FullConsole>(consolex, sys);


    std::vector<uint32_t> pixels(realw * realh);
    for (auto y = 0; y < realh; y++) {
        for (auto x = 0; x < realw; x++) {
            pixels[x + y * realw] = 0xff00ffff;
        }
    }

    auto bg_ = gl::TexRef(100, 100);
    bg_.tex->update(pixels.data());
    pix::ImageView bg{bg_};
    bg.set_color(gl::Color(0xff0000ff));
    bg.filled_circle({40, 40}, 20);

    auto bg2 = bg.crop(10, 10, 80, 80);
    //bg2.clip_start = {10, 10};
    //bg2.clip_size = {40, 40};
    bg2.set_color(gl::Color(0xffffffff));
    bg2.clear({0x808080ff});
    bg2.filled_circle({40, 40}, 10);


    auto font2 = std::make_shared<FreetypeFont>("examples/data/HackNerdFont-Regular.ttf", 20);

    font2->set_pixel_size(30);
    //printf("%d %d", font2->get_size().first, font2->get_size().second);

    auto font = std::make_shared<TileSet>(FreetypeFont::unscii);
    auto console = std::make_shared<PixConsole>(cols, rows, font);

    for (auto y = 0; y < rows; y++) {
        for (auto x = 0; x < cols; x++) {
            console->put_char(x, y, '0' + x + y);
        }
    }

    for (auto& p : star) {
        p = p * 0.5 + Vec2f(200, 200);
    }

    screen->set_fps(0);
    //auto screen2 = screen->crop(50, 50, 500, 300);
     auto splits = screen->split(2, 2);
     for(auto& split : splits) {
         auto [sx, sy] = split->view_size;
         split = split->crop(4, 4, sx - 8, sy - 8);
     }
    while (true) {
        auto pos = Vec2(0, 0);
        if (!sys->run_loop()) { break; }
        //context-set_target();
        screen->clear(0x000000);
        //console->render();
        std::vector<Vec2f> points{
            {100, 100},
            {900, 200},
            {700, 500},
            {200, 400}
        };
        // for (auto& screen2 : splits) {
        //     screen2->clear(0x00ff00);
        //     screen2->set_color(gl::Color(0xff0000ff));
        //     std::vector<std::vector<Vec2f>> multi { points, star }; //, points };
        //     screen2->draw_complex_polygon(multi);
        //
        //     screen2->set_color(gl::Color(0xffff00ff));
        //     //for (int i = 0; i < 400; i++) {
        //         for (auto p : star) {
        //             screen2->line(p);
        //         }
        //         //pos += {4, 0};
        //     //}
        //     screen2->line(star[0]);
        //     //context->filled_rect({10, 10}, {100,100});
        //     screen2->blit(bg, {20,20}, Vec2f{bg.size()});
        // }
        full_con->render(screen, {0,0}, full_con->get_size());
        screen->swap();
    }

    while (sys->run_loop()) {
    }
}
