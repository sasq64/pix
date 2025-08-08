#pragma once

#include "colors.hpp"
#include "context.hpp"
#include "keycodes.h"
#include "pixel_console.hpp"
#include "system.hpp"

#include <functional>
#include <optional>

class FullConsole
{
    int cols{};
    int rows{};

    Vec2i cursor{0, 0};

    std::shared_ptr<PixConsole> console;
    std::shared_ptr<System> system;

    Vec2i edit_start{0, 0};
    int xpos = 0;
    int scroll_pos = 0;
    std::u32string line;
    void refresh();
    int listener = -1;
    int device = 0;
    std::function<void(std::string, int)> readline_cb;

    System::Propagate put_event(KeyEvent const& event);
    System::Propagate put_event(TextEvent const& te);

public:
    FullConsole(std::shared_ptr<PixConsole> const& con,
                std::shared_ptr<System> const& sys);

    ~FullConsole();

    void set_device(int dev) { device = dev; }

    bool reading_line = false;
    bool wrap_lines = true;
    bool autoscroll = true;
    void set_wrap(bool on) { reading_line = autoscroll = on; }

    Vec2i get_cursor() const { return cursor; }
    // void set_cursor(int x, int y) { cursor = {x,y}; }
    void set_cursor(Vec2i xy) { cursor = xy; }

    pix::ImageView get_font_texture();

    Vec2i get_pixel_size() const;

    std::vector<uint32_t> get_tiles() { return console->get_tiles(); }
    void set_tiles(std::vector<uint32_t> const& data)
    {
        console->set_tiles(data);
    }

    void read_line();

    void stop_line()
    {
        cursor_on = false;
        reading_line = false;
    }

    void set_line(std::string const& text);

    Vec2i get_size() const { return Vec2i{console->get_size()}; }
    Vec2i get_tile_size() const { return Vec2i{console->get_char_size()}; }

    // void put(Vec2i pos, uint32_t c) { console->put(pos.x, pos.y, fg, bg, c);
    // }
    void put(Vec2i pos, uint32_t c, std::optional<uint32_t> fg_ = std::nullopt,
             std::optional<uint32_t> bg_ = std::nullopt)
    {
        console->put(pos.x, pos.y, fg_.value_or(fg), bg_.value_or(bg), c);
    }
    void text(Vec2i pos, std::string const& txt)
    {
        console->text(pos.x, pos.y, txt, fg, bg);
    }

    uint32_t get(Vec2i pos) const { return console->get_char(pos.x, pos.y); }

    void write(char32_t ch);

    void write(std::string const& text);

    void set_color(uint32_t fg_, uint32_t bg_);

    void colorize(int x, int y, int width);

    void set_tile_images(int start_no,
                         std::vector<pix::ImageView> const& images)
    {
        auto i = start_no;
        for (auto const& img : images) {
            auto target = console->get_texture_for_char(i++);
            target.copy_from(img);
        }
    }

    void clear_area(int32_t x, int32_t y, int32_t w, int32_t h)
    {
        console->clear_area(x, y, w, h, fg, bg);
    }

    void clear() { console->fill(fg, bg); }

    pix::ImageView get_texture_for_char(int32_t c)
    {
        return console->get_texture_for_char(c);
    }

    void render2(pix::Context* context, Vec2f xy, Vec2f sz);
    void render(std::shared_ptr<pix::Context> context, Vec2f xy, Vec2f sz)
    {
        render2(context.get(), xy, sz);
    }

    uint32_t fg = color::white;
    uint32_t bg = color::black;

    bool cursor_on = false;

    void set_readline_callback(std::function<void(std::string, int)> const& cb)
    {
        readline_cb = cb;
    }
};
