#include "full_console.hpp"

#include "image_view.hpp"
#include "utf8.h"

template <typename T, typename S = int> static constexpr S len(T&& t)
{
    return static_cast<S>(t.size());
}

System::Propagate FullConsole::put_event(const KeyEvent& event)
{
    if (event.device != device) { return System::Propagate::Pass; }
    auto key = static_cast<Key>(event.key);
    if (key == Key::RIGHT) {
        xpos++;
    } else if (key == Key::LEFT) {
        xpos--;
    } else if (key == Key::HOME) {
        xpos = 0;
    } else if (key == Key::END) {
        xpos = len(line);
    } else if (key == Key::ENTER) {
        reading_line = false;
        line.push_back(u'\n');
        if (readline_cb) {
            readline_cb(utf8::utf8_encode(line), device);
        } else {
            system->post_event(TextEvent{utf8::utf8_encode(line), device});
        }
        line.clear();
    } else if (key == Key::BACKSPACE) {
        if (xpos > 0) { line.erase(--xpos, 1); }
    } else if (key == Key::DELETE) {
        if (xpos < static_cast<int>(line.length())) { line.erase(xpos, 1); }
    } else {
        return System::Propagate::Pass;
    }

    if (xpos < 0) { xpos = 0; }
    if (xpos > len(line)) { xpos = len(line); }

    // Update scroll position when cursor comes within 2 characters of border
    auto available_width = console->get_size().first - edit_start.x;
    auto cursor_screen_pos = xpos - scroll_pos;

    if (cursor_screen_pos < 2 && scroll_pos > 0) {
        // Scroll left when cursor is within 2 chars of left edge
        scroll_pos = std::max(0, xpos - 2);
    } else if (cursor_screen_pos >= available_width - 2) {
        // Scroll right when cursor is within 2 chars of right edge
        scroll_pos = std::max(0, xpos - available_width + 3);
    }

    return System::Propagate::Stop;
}
System::Propagate FullConsole::put_event(const TextEvent& te)
{
    if (te.device != device) { return System::Propagate::Pass; }
    for (auto&& c : utf8::utf8_decode(te.text)) {
        line.insert(xpos, 1, c);
        xpos++;
    }

    // Update scroll position after text insertion
    auto available_width = console->get_size().first - edit_start.x;
    auto cursor_screen_pos = xpos - scroll_pos;

    if (cursor_screen_pos >= available_width - 2) {
        // Scroll right when cursor is within 2 chars of right edge
        scroll_pos = std::max(0, xpos - available_width + 3);
    }

    return System::Propagate::Stop;
}
void FullConsole::refresh()
{
    auto w = console->get_size().first;
    auto available_width = w - edit_start.x;

    console->clear_area(edit_start.x, edit_start.y, available_width, 1,
                        color::white, color::black);

    // Extract visible portion of line based on scroll position
    auto line_start = std::min(scroll_pos, static_cast<int>(line.length()));
    auto visible_length =
        std::min(available_width, static_cast<int>(line.length()) - line_start);

    if (visible_length > 0) {
        std::u32string visible_line = line.substr(line_start, visible_length);
        console->text(edit_start.x, edit_start.y, visible_line, fg, bg);
    }
}
FullConsole::FullConsole(const std::shared_ptr<PixConsole>& con,
                         const std::shared_ptr<System>& sys)
    : console{con}, system{sys}
{
    listener = sys->add_listener([this](AnyEvent&& e) {
        if (!reading_line || std::holds_alternative<NoEvent>(e)) {
            return System::Propagate::Pass;
        }
        return std::visit(
            Overload{[&](TextEvent const& te) { return put_event(te); },
                     [&](KeyEvent const& k) { return put_event(k); }, //
                     [&](auto) { return System::Propagate::Pass; }},
            e);
    });
    std::tie(cols, rows) = console->get_size();
    // printf("%d x %d\n", rows, cols);
}

FullConsole::~FullConsole()
{
    if (listener >= 0) { system->remove_listener(listener); }
}

pix::ImageView FullConsole::get_font_texture()
{
    return pix::ImageView{gl::TexRef{console->get_font_texture()}};
}

void FullConsole::colorize(int x, int y, int w)
{
    for (int i = x; i < x + w; i++) {
        console->put_color(i, y, this->fg, this->bg);
    }
}

Vec2i FullConsole::get_pixel_size() const
{
    return console->get_pixel_size();
}

void FullConsole::read_line()
{
    // printf("GET LINE\n");

    cursor_on = true;
    edit_start = cursor;
    reading_line = true;
    scroll_pos = 0;
}

void FullConsole::write(char32_t ch)
{
    if (ch == 10) {
        cursor.x = 0;
        cursor.y++;
        if (cursor.y >= rows) {
            if (wrap) {
                console->scroll(-1, 0);
                console->clear_area(0, rows - 1, cols, 1, fg, bg);
            }
            cursor.y--;
        }
        return;
    }
    if (!wrap && cursor.x >= cols) { return; }

    console->put(cursor.x, cursor.y, fg, bg, ch);
    cursor.x++;
    if (cursor.x >= cols && wrap) {
        cursor.x = 0;
        cursor.y++;
        if (cursor.y >= rows) {
            console->scroll(-1, 0);
            console->clear_area(0, rows - 1, cols, 1, fg, bg);
            cursor.y--;
        }
    }
}
void FullConsole::write(const std::string& text)
{
    auto t32 = utf8::utf8_decode(text);
    for (auto c : t32) {
        write(c);
    }
}
void FullConsole::set_color(uint32_t fg_, uint32_t bg_)
{
    fg = fg_;
    bg = bg_;
}
void FullConsole::render2(pix::Context* context, Vec2f xy, Vec2f sz)
{
    if (reading_line) { refresh(); }

    if (sz.x <= 0) {
        sz = Vec2f(console->get_size()) * Vec2f(console->get_char_size());
    }

    context->set_target();
    auto const xy0 = context->to_screen(xy);
    auto const xy1 = context->to_screen(xy + sz);
    console->render(xy0, xy1);
    if (cursor_on) {
        auto cw = sz.x / cols;
        auto ch = sz.y / rows;

        xy = Vec2f{(cursor.x + xpos - scroll_pos) * cw, cursor.y * ch} + xy;
        context->set_color(color::orange);
        context->filled_rect(xy, {cw, ch});
        auto const c =
            console->get_char(cursor.x + xpos - scroll_pos, cursor.y);
        auto const tex = console->get_texture_for_char(c);
        gl::ProgramCache::get_instance()
            .get_program<gl::ProgramCache::Textured>()
            .use();
        context->set_color(color::white);
        context->blit(tex, xy, {cw, ch});
    }
}

void FullConsole::set_line(const std::string& text)
{
    line = utf8::utf8_decode(text);
    xpos = len(line);
    scroll_pos = 0;

    // Adjust scroll position if cursor is beyond visible area
    auto available_width = console->get_size().second - edit_start.x;
    if (xpos >= available_width - 2) {
        scroll_pos = std::max(0, xpos - available_width + 3);
    }
}
