#pragma once

#include <nlohmann/json.hpp>
#include <cstdint>
#include <stdexcept>
#include <string>

namespace ohc {
// OpenRGB RGBColor stores red in the least significant byte (0x00BBGGRR).
// Do not pass bitwise expressions to its unparenthesized ToRGBColor macro.
inline unsigned int parseColor(const nlohmann::json& value)
{
    unsigned int red, green, blue;
    if (value.is_string())
    {
        std::string text = value.get<std::string>();
        if (!text.empty() && text.front() == '#') text.erase(0, 1);
        if (text.size() != 6 || text.find_first_not_of("0123456789abcdefABCDEF") != std::string::npos)
            throw std::runtime_error("invalid RGB colour");
        const auto rgb = std::stoul(text, nullptr, 16);
        red = (rgb >> 16) & 0xffu;
        green = (rgb >> 8) & 0xffu;
        blue = rgb & 0xffu;
    }
    else if (value.is_array() && value.size() == 3)
    {
        for (const auto& channel : value)
            if (!channel.is_number_unsigned() || channel.get<std::uint64_t>() > 255)
                throw std::runtime_error("invalid RGB channel");
        red = value[0].get<unsigned int>();
        green = value[1].get<unsigned int>();
        blue = value[2].get<unsigned int>();
    }
    else throw std::runtime_error("invalid RGB colour");
    return red | (green << 8u) | (blue << 16u);
}
}
