#include "LatestFrameWorker.h"
#include <atomic>
#include <cassert>

int main()
{
    using namespace std::chrono_literals;
    std::atomic<unsigned int> fast_count{0}, slow_count{0};
    std::atomic<int> last_fast{0};
    LatestFrameWorker<int> slow([&](const int&) {
        std::this_thread::sleep_for(80ms); ++slow_count;
    });
    LatestFrameWorker<int> fast([&](const int& value) {
        ++fast_count; last_fast = value;
    });
    fast.reset(60); slow.reset(60);
    auto started = std::chrono::steady_clock::now();
    for (int i = 1; std::chrono::steady_clock::now() - started < 600ms; ++i)
    {
        fast.enqueue(i, i); slow.enqueue(i, i);
        std::this_thread::sleep_for(1ms);
    }
    fast.drain(); slow.drain();
    assert(fast_count >= 25 && fast_count <= 40);
    assert(slow_count >= 3 && slow_count <= 9);
    assert(fast.status().replaced > 100 && slow.status().replaced > 100);
    assert(last_fast > 200);  // Newest samples, never a growing frame backlog.
    auto stopped_count = fast_count.load();
    std::this_thread::sleep_for(40ms);
    assert(fast_count == stopped_count);
    fast.reset(60);
    assert(fast.status().submitted == 0);
    fast.enqueue(900, 900);
    std::this_thread::sleep_for(30ms);
    fast.drain();
    assert(fast.status().sequence == 900);
}
