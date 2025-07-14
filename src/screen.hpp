#pragma once
#include "context.hpp"
#include "system.hpp"

namespace pix {

class Screen : public Context
{
    std::shared_ptr<Display> display;

public:
    static inline std::shared_ptr<Screen> instance;
    bool visible;
    explicit Screen(std::shared_ptr<Display> const& d)
        : Context(d->get_size().first, d->get_size().second, 0), display{d}
    {
    }

    Screen(Screen const& other) : Context{other}, display{other.display} {}

    int frame_counter() const { return display->get_time().frame_counter; }

    void swap()
    {
        if (log_fp) {
            fputs("swap\n", log_fp);
            fflush(log_fp);
        }
        display->swap();
    }

    void set_fps(int fps) { display->set_fps(fps); }

    [[nodiscard]] Display::Time get_time() const { return display->get_time(); }

    void set_target() { display->set_target(); }

    float get_scale() const { return display->get_scale(); }

    [[nodiscard]] std::pair<int, int> get_size() const
    {
        return display->get_size();
    }

    std::shared_ptr<Screen> crop(double x, double y, double w, double h) const
    {
        auto result = std::make_shared<Screen>(*this);
        result->offset = offset + Vec2f{x, y};
        result->view_size = {w, h};
        return result;
    }

    std::vector<std::shared_ptr<Screen>> split(int w, int h) const
    {
        std::vector<std::shared_ptr<Screen>> result;
        auto width = view_size.x / w;
        auto height = view_size.y / h;
        for (int y = 0; y < h; y++) {
            for (int x = 0; x < w; x++) {
                auto screen = std::make_shared<Screen>(*this);
                screen->offset =
                    offset + Vec2f(offset.x + x * width, offset.y + y * height);
                screen->view_size = {width, height};
                result.push_back(screen);
            }
        }
        return result;
    }

    void set_size(Vec2i new_size) { display->set_size(new_size.x, new_size.y); }
    void set_visible(bool on)
    {
        display->set_visible(on);
        visible = on;
    }
};
} // namespace pix
