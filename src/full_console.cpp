#include "full_console.hpp"

template <typename T, typename S=int>
static constexpr S len(T&& t) { return static_cast<S>(t.size()); }

System::Propagate FullConsole::put_event(const KeyEvent& event)
{
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
        system->post_event(TextEvent{utf8::utf8_encode(line), 0});
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
    return System::Propagate::Stop;
}
System::Propagate FullConsole::put_event(const TextEvent& te)
{
    for (auto&& c : utf8::utf8_decode(te.text)) {
        line.insert(xpos, 1, c);
        xpos++;
    }
    return System::Propagate::Stop;
}
void FullConsole::refresh()
{
    auto w = console->get_size().second;
    console->clear_area(edit_start.x, edit_start.y, w - edit_start.x, 1,
                        color::white, color::black);
    console->text(edit_start.x, edit_start.y, line, color::white, color::black);
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
    //printf("%d x %d\n", rows, cols);
}

FullConsole::~FullConsole()
{
    if (listener >= 0) { system->remove_listener(listener); }
}

gl_wrap::TexRef FullConsole::get_font_texture()
{
    return gl_wrap::TexRef{console->get_font_texture()};
}

Vec2i FullConsole::get_pixel_size() const
{
    return console->get_pixel_size();
}

void FullConsole::read_line()
{
    //printf("GET LINE\n");

    cursor_on = true;
    edit_start = cursor;
    reading_line = true;
}

void FullConsole::write(char32_t ch)
{
    if (ch == 10) {
        cursor.x = 0;
        cursor.y++;
        if (cursor.y >= rows) {
            console->scroll(-1, 0);
            console->clear_area(0, rows - 1, cols, 1, fg, bg);
            cursor.y--;
        }
        return;
    }
    console->put(cursor.x, cursor.y, fg, bg, ch);
    cursor.x++;
    if (cursor.x >= cols) {
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
void FullConsole::render(pix::Context* context, Vec2f xy, Vec2f sz)
{
    if (reading_line) { refresh(); }

    if (sz.x <= 0) {
        sz = Vec2f(console->get_size()) * Vec2f(console->get_char_size());
    }

    context->set_target();
    auto xy0 = context->to_screen(xy);
    auto xy1 = context->to_screen(xy + sz);
    console->render(xy0, xy1);
    if (cursor_on) {
        auto cw = sz.x / cols;
        auto ch = sz.y / rows;

        xy = Vec2f{(cursor.x + xpos) * cw, cursor.y * ch} + xy;
        context->set_color(color::orange);
        context->filled_rect(xy, {cw, ch});
        auto c = console->get_char(cursor.x + xpos, cursor.y);
        auto tex = console->get_texture_for_char(c);
        gl_wrap::ProgramCache::get_instance()
            .get_program<gl_wrap::ProgramCache::Textured>()
            .use();
        context->set_color(color::white);
        context->blit(tex, xy, {cw, ch});
    }
}
void FullConsole::set_line(const std::string& text)
{
    line = utf8::utf8_decode(text);
    xpos = len(line);
}
