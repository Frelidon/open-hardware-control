#pragma once

#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <functional>
#include <mutex>
#include <optional>
#include <string>
#include <thread>

// One bounded mailbox per controller. Slow I/O never holds another mailbox.
template<typename Frame> class LatestFrameWorker
{
public:
    using Clock = std::chrono::steady_clock;
    struct Status
    {
        std::uint64_t sequence = 0, submitted = 0, replaced = 0, errors = 0;
        double duration_ms = 0.0, hz = 0.0;
        std::string error;
    };
    explicit LatestFrameWorker(std::function<void(const Frame&)> apply)
        : apply_(std::move(apply)), thread_([this] { loop(); }) {}
    ~LatestFrameWorker()
    {
        { std::lock_guard<std::mutex> lock(mutex_); running_ = false; pending_.reset(); }
        condition_.notify_all();
        thread_.join();
    }
    void enqueue(std::uint64_t sequence, Frame frame)
    {
        { std::lock_guard<std::mutex> lock(mutex_);
          if (pending_) ++status_.replaced;
          pending_ = Entry{sequence, std::move(frame)}; }
        condition_.notify_all();
    }
    void reset(unsigned int fps)
    {
        std::unique_lock<std::mutex> lock(mutex_);
        pending_.reset();
        condition_.wait(lock, [this] { return !busy_; });
        status_ = {};
        period_ = std::chrono::nanoseconds(1'000'000'000 / fps);
        next_ = Clock::now();
        first_ = {};
    }
    void drain()
    {
        std::unique_lock<std::mutex> lock(mutex_);
        pending_.reset();
        condition_.wait(lock, [this] { return !busy_; });
    }
    Status status()
    {
        std::lock_guard<std::mutex> lock(mutex_);
        return status_;
    }
private:
    struct Entry { std::uint64_t sequence; Frame frame; };
    void loop()
    {
        std::unique_lock<std::mutex> lock(mutex_);
        while (running_)
        {
            condition_.wait(lock, [this] { return !running_ || pending_.has_value(); });
            if (!running_) break;
            if (Clock::now() < next_)
            {
                condition_.wait_until(lock, next_);
                continue;
            }
            auto entry = std::move(*pending_);
            pending_.reset();
            busy_ = true;
            lock.unlock();
            auto started = Clock::now();
            std::string error;
            try { apply_(entry.frame); }
            catch (const std::exception& exc) { error = exc.what(); }
            catch (...) { error = "controller update failed"; }
            auto finished = Clock::now();
            lock.lock();
            status_.duration_ms = std::chrono::duration<double, std::milli>(finished - started).count();
            status_.error = error;
            if (error.empty())
            {
                status_.sequence = entry.sequence;
                if (!status_.submitted) first_ = finished;
                ++status_.submitted;
                auto span = std::chrono::duration<double>(finished - first_).count();
                status_.hz = span > 0 ? (status_.submitted - 1) / span : 0.0;
            }
            else ++status_.errors;
            // Absolute deadlines preserve 60 Hz; missed slots are discarded.
            do { next_ += period_; } while (next_ < finished);
            busy_ = false;
            condition_.notify_all();
        }
    }
    std::function<void(const Frame&)> apply_;
    std::mutex mutex_;
    std::condition_variable condition_;
    bool running_ = true, busy_ = false;
    std::optional<Entry> pending_;
    Status status_;
    Clock::time_point first_{}, next_{};
    Clock::duration period_ = std::chrono::nanoseconds(16'666'666);
    std::thread thread_;
};
