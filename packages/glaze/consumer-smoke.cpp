#include <glaze/glaze.hpp>
#include <string>
#include <vector>

struct Monitor {
    std::string name;
    int width;
    double scale;
};

int main() {
    const std::string input = R"({"name":"DP-1","width":1920,"scale":1.25})";
    Monitor monitor{};
    if (glz::read_json(monitor, input) || monitor.name != "DP-1" ||
        monitor.width != 1920 || monitor.scale != 1.25)
        return 1;
    auto generic = glz::read_json<glz::generic>(input);
    if (!generic || !generic->is_object())
        return 2;
    const auto output = glz::write_json(monitor);
    if (!output)
        return 3;
    Monitor roundtrip{};
    if (glz::read_json(roundtrip, *output) || roundtrip.name != monitor.name ||
        roundtrip.width != monitor.width || roundtrip.scale != monitor.scale)
        return 4;
    std::vector<Monitor> monitors;
    if (glz::read_json(monitors, std::string("[") + input + "]") ||
        monitors.size() != 1 || monitors.front().width != monitor.width)
        return 5;
    return 0;
}
