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


static std::shared_ptr<Screen> screen;

extern "C" pix::Context* pix_open_display(int w, int h, int flags)
{
    if (screen == nullptr) {
        auto sys = create_glfw_system();

        screen = sys->init_screen(
            {.screen = flags == 1 ? ScreenType::Full : ScreenType::Window,
             .display_width = w,
             .display_height = h});
    }

    auto [realw, realh] = screen->get_size();
    auto* context = new pix::Context(realw, realh, 0);
    context->vpscale = screen->get_scale();
    return context;
}

extern "C" void pix_circle(pix::Context* ctx, float x, float y, float radius)
{
    ctx->circle({x,y}, radius);
}

extern "C" void pix_swap()
{
    screen->swap();
}

extern "C" void pix_clear(pix::Context* context, uint32_t color)
{
    context->clear(color);
}

extern "C" void pix_destroy_context(pix::Context* context)
{
    delete context;
}
