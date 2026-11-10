#include "ColorCodec.h"
#include <cassert>

int main()
{
    using nlohmann::json;
    using ohc::parseColor;
    assert(parseColor("ff0000") == 0x0000ffu);
    assert(parseColor("00ff00") == 0x00ff00u);
    assert(parseColor("0000ff") == 0xff0000u);
    assert(parseColor("#00F0FF") == 0xfff000u);
    assert(parseColor("7a28ff") == 0xff287au);
    assert(parseColor("ffffff") == 0xffffffu);
    assert(parseColor("000000") == 0u);
    assert(parseColor(json::parse("[122,40,255]")) == parseColor("7a28ff"));
    // Every channel value must survive independently, including gradients.
    for (unsigned int value = 0; value <= 255; ++value)
    {
        assert(parseColor(json::array({value, 0u, 0u})) == value);
        assert(parseColor(json::array({0u, value, 0u})) == (value << 8));
        assert(parseColor(json::array({0u, 0u, value})) == (value << 16));
    }
    for (const auto& text : {"null", "42", "\"gg0000\"", "\"fff\"", "[]",
                             "[0,0]", "[256,0,0]", "[-1,0,0]", "[0.5,0,0]",
                             "[true,0,0]", "[4294967296,0,0]"})
    {
        bool rejected = false;
        try { parseColor(json::parse(text)); }
        catch (const std::runtime_error&) { rejected = true; }
        assert(rejected);
    }
}
