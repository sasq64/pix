#pragma once

#include "keycodes.h"

#include <deque>
#include <functional>
#include <memory>
#include <string>
#include <tuple>
#include <unordered_map>
#include <variant>
#include <vector>

template <typename ... ARGS>
void inline log(const char* text, ARGS ... args)
{
    //printf(text, args...);
    //puts("");
}

void inline log(const char* text)
{
    //puts(text);
}

enum class ScreenType
{
    Full,
    Window,
    None
};

class system_exception : public std::exception
{
public:
    explicit system_exception(std::string m = "system exception")
        : msg(std::move(m))
    {}
    [[nodiscard]] const char* what() const noexcept override { return msg.c_str(); }

private:
    std::string msg;
};

template <typename... Ts> struct Overload : Ts... // NOLINT
{
    using Ts::operator()...;
};
template <class... Ts> Overload(Ts...) -> Overload<Ts...>;

struct KeyEvent
{
    uint32_t key;
    uint32_t mods;
    int device;
};

struct NoEvent
{};

struct QuitEvent
{};

struct ClickEvent
{
    float x;
    float y;
    int buttons;
    uint32_t mods;
};

struct ResizeEvent
{
    int w;
    int h;
};

struct MoveEvent
{
    float x;
    float y;
    int buttons;
};

struct TextEvent
{
    std::string text;
    int device;
};

using AnyEvent = std::variant<NoEvent, KeyEvent, MoveEvent, ClickEvent,
                              TextEvent, ResizeEvent, QuitEvent>;

class Screen
{
public:
    struct Settings
    {
        ScreenType screen = ScreenType::Window;
        std::string title = "pix";
        int display_width = 1600;
        int display_height = 1200;
    };

    struct Time
    {
        double seconds{};
        int frame_counter{};
        double delta{};
        int fps{};
    };

    virtual ~Screen() = default;
    virtual void swap() {}
    virtual void set_fps(int fps) {}
    virtual Time get_time() const { return {}; }
    virtual void set_target(){};
    virtual float get_scale() { return 1.0F; }
    virtual std::pair<int, int> get_size() const { return {-1, -1}; }
};

class Input
{};

class System
{
public:

    enum class Propagate
    {
        Stop,
        Pass
    };

private:
    using Listener = std::function<Propagate(AnyEvent)>;
    int counter = 0;
    std::unordered_map<int, Listener> listeners;

protected:
    virtual std::deque<AnyEvent> internal_all_events() { return {}; }

public:
    virtual ~System() = default;
    virtual std::shared_ptr<Screen> init_screen(Screen::Settings const&)
    {
        return nullptr;
    }
    virtual void init_audio() {}
    virtual void
    set_audio_callback(std::function<void(float*, size_t)> const& fcb)
    {}

    int add_listener(Listener const& l)
    {
        listeners[counter++] = l;
        return counter - 1;
    }

    std::deque<AnyEvent> posted_events;

    AnyEvent next_event()
    {
        if (posted_events.empty()) { return NoEvent{}; }
        auto e = posted_events.front();
        posted_events.pop_front();
        return e;
    }

    std::vector<AnyEvent> all_events()
    {
        std::vector<AnyEvent> result;
        while (true) {
            auto e = next_event();
            if (std::holds_alternative<NoEvent>(e)) { break; }
            result.push_back(e);
        }
        return result;
    }

    virtual void post_event(AnyEvent const& event)
    {
        posted_events.emplace_back(event);
    }

    void remove_listener(int n) { listeners.erase(n); }

    template <typename FN> void handle_events(FN f)
    {
        run_loop();
        while (!std::visit(
            [&](auto&& e) {
                using T = std::decay_t<decltype(e)>;
                if constexpr (std::is_same_v<T, NoEvent>) { return true; }
                f(e);
                return false;
            },
            next_event())) {}
    }

    // Clear old events, poll new events and begin main loop
    // Return false if app should quit
    bool run_loop()
    {
        bool quit = false;
        for (auto&& event : internal_all_events()) {
            bool propagate = true;
            for (auto&& [_, listener] : listeners) {
                auto prop = listener(event);
                if (prop == Propagate::Stop) {
                    propagate = false;
                    break;
                }
            }
            if (propagate) {
                posted_events.emplace_back(event);
            }
            if (std::holds_alternative<QuitEvent>(event)) {
                log("Got quit event");
                quit = true;
                break;
            }
        }
        return !quit;
    }

    virtual bool is_pressed(uint32_t /*code*/, int /*device*/ = -1)
    {
        return false;
    }
    virtual bool was_pressed(uint32_t /*code*/, int /*device*/ = -1)
    {
        return false;
    }
    virtual bool was_released(uint32_t /*code*/, int /*device*/ = -1)
    {
        return false;
    }

    virtual std::pair<float, float> get_pointer() { return {-1, -1}; }
};

std::unique_ptr<System> create_sdl_system();
std::unique_ptr<System> create_pi_system();
std::unique_ptr<System> create_glfw_system();
