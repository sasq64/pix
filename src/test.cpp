#include "screen.hpp"
#include "system.hpp"
#include "vec2.hpp"

#include <array>
#include <filesystem>
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

class Drawable
{
    void render();
};

struct Star
{
    pix::Screen& screen;
    Star(pix::Screen& screen_) : screen{screen_} {}

    void render(Vec2f pos, uint32_t color, float line_width)
    {
        static std::vector<Vec2f> star{{500.0, 250.0},   {351.13, 323.47},
                                       {327.25, 487.76}, {211.37, 368.88},
                                       {47.75, 396.95},  {125.0, 250.0},
                                       {47.75, 103.05},  {211.37, 131.12},
                                       {327.25, 12.24},  {351.13, 176.53}};
        screen.set_color(gl::Color(color));
        screen.begin_lines();
        for (auto p : star) {
            screen.round_line(p + pos, line_width);
        }
        screen.round_line(star[0] + pos, line_width);
    }
};

int main()
{
    auto sys = std::shared_ptr(create_glfw_system());
    auto display = sys->init_screen({
        .screen = DisplayType::Window,
        .display_width = 960,
        .display_height = 720,
    });
    auto screen = std::make_shared<pix::Screen>(display);
    screen->vpscale = screen->get_scale();

    auto pos = Vec2f(display->get_size()) / 4;
    while (sys->run_loop()) {
        screen->clear(0x000000);
        Star(*screen).render(pos, 0xff0000ff, 50.0);
        Star(*screen).render(pos, 0xffff00ff, 8.0);
        screen->swap();
        pos += {1,0};
    }

    while (sys->run_loop()) {}
}
