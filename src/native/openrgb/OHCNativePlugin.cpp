#include "OHCNativePlugin.h"

#include "RGBControllerInterface.h"
#include "ColorCodec.h"
#include <nlohmann/json.hpp>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/stat.h>
#include <unistd.h>

#include <algorithm>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <poll.h>
#include <set>
#include <stdexcept>

using json = nlohmann::json;

namespace {
constexpr std::size_t kMaxLine = 2'000'000;

std::string socketPath()
{
    const char* runtime = std::getenv("XDG_RUNTIME_DIR");
    return runtime && *runtime ? std::string(runtime) + "/ohc-openrgb-native.sock"
                               : "/tmp/ohc-openrgb-native.sock";
}

bool writeReply(int fd, const json& reply)
{
    const std::string line = reply.dump() + "\n";
    return ::send(fd, line.data(), line.size(), MSG_NOSIGNAL) == static_cast<ssize_t>(line.size());
}

using ohc::parseColor;
}

OpenRGBPluginInfo OHCNativePlugin::GetPluginInfo()
{
    OpenRGBPluginInfo info;
    info.Name = "Open Hardware Control Native Engine";
    info.Description = "60 Hz latest-frame-wins transport for Open Hardware Control";
    info.Version = "0.2.0";
    info.Commit = "local";
    info.URL = "https://github.com/Frelidon/open-hardware-control";
    info.Location = OPENRGB_PLUGIN_LOCATION_SETTINGS;
    info.Label = "OHC Native Engine";
    info.ProtocolVersion = OPENRGB_PLUGIN_API_VERSION;
    return info;
}

void OHCNativePlugin::Load(OpenRGBPluginAPIInterface* api)
{
    api_ = api;
    socket_path_ = socketPath();
    ::unlink(socket_path_.c_str());
    server_fd_ = ::socket(AF_UNIX, SOCK_STREAM, 0);
    if (server_fd_ < 0) return;
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    if (socket_path_.size() >= sizeof(address.sun_path)) { ::close(server_fd_); server_fd_ = -1; return; }
    std::strncpy(address.sun_path, socket_path_.c_str(), sizeof(address.sun_path) - 1);
    if (::bind(server_fd_, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0 || ::listen(server_fd_, 2) < 0)
    {
        ::close(server_fd_); server_fd_ = -1; return;
    }
    ::chmod(socket_path_.c_str(), 0600);
    running_ = true;
    server_thread_ = std::thread(&OHCNativePlugin::serverLoop, this);
}

void OHCNativePlugin::Unload()
{
    stopServer();
}

void OHCNativePlugin::stopServer()
{
    if (!running_.exchange(false)) return;
    if (server_fd_ >= 0) { ::shutdown(server_fd_, SHUT_RDWR); ::close(server_fd_); server_fd_ = -1; }
    if (server_thread_.joinable()) server_thread_.join();
    workers_.clear();
    if (!socket_path_.empty()) ::unlink(socket_path_.c_str());
}

void OHCNativePlugin::serverLoop()
{
    std::unordered_map<int, std::string> clients;
    while (running_)
    {
        std::vector<pollfd> sockets{{server_fd_, POLLIN, 0}};
        for (const auto& client : clients) sockets.push_back({client.first, POLLIN, 0});
        if (::poll(sockets.data(), sockets.size(), 100) <= 0) continue;
        if (!running_) break;
        if (sockets[0].revents & POLLIN)
        {
            const int fd = ::accept(server_fd_, nullptr, nullptr);
            if (fd >= 0)
            {
                timeval timeout{1, 0};
                ::setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
                if (clients.size() < 4) clients.emplace(fd, "");
                else ::close(fd);
            }
        }
        for (std::size_t i = 1; i < sockets.size(); ++i)
        {
            auto fd = sockets[i].fd;
            if (!sockets[i].revents) continue;
            bool keep = !(sockets[i].revents & (POLLERR | POLLHUP | POLLNVAL));
            if (keep && (sockets[i].revents & POLLIN))
            {
                char chunk[8192];
                auto count = ::recv(fd, chunk, sizeof(chunk), 0);
                keep = count > 0;
                if (keep)
                {
                    auto& buffer = clients.at(fd);
                    buffer.append(chunk, static_cast<std::size_t>(count));
                    keep = buffer.size() <= kMaxLine;
                    std::size_t newline;
                    while (keep && (newline = buffer.find('\n')) != std::string::npos)
                    {
                        auto line = buffer.substr(0, newline);
                        buffer.erase(0, newline + 1);
                        keep = handleLine(fd, line);
                    }
                }
            }
            if (!keep) { ::close(fd); clients.erase(fd); }
        }
    }
    for (const auto& client : clients) ::close(client.first);
}

bool OHCNativePlugin::handleLine(int fd, const std::string& line)
{
    try
    {
        const json request = json::parse(line);
        const std::string op = request.value("op", "");
        if (op == "start")
        {
            drainWorkers();
            fps_ = std::clamp(request.value("fps", 60u), 1u, 120u);
            ++generation_;
            for (auto& worker : workers_) worker.second->reset(fps_);
            active_ = true;
            return writeReply(fd, {{"ok", true}, {"generation", generation_}, {"detail", "ready"}});
        }
        if (op == "stop")
        {
            active_ = false;
            drainWorkers();
            return writeReply(fd, {{"ok", true}, {"detail", "stopped"}});
        }
        if (op == "stats") return writeReply(fd, status());
        if (op != "frame") return writeReply(fd, {{"ok", false}, {"error", "unknown operation"}});
        if (!api_ || !request.contains("devices") || !request["devices"].is_array()) return writeReply(fd, {{"ok", false}, {"error", "invalid devices"}});
        if (!active_) throw std::runtime_error("stream is stopped");
        queueFrame(request);
        auto reply = status();
        reply["id"] = request.value("id", 0u);
        reply["type"] = "queued";
        return writeReply(fd, reply);
    }
    catch (const std::exception& exc) { return writeReply(fd, {{"ok", false}, {"error", exc.what()}}); }
}

void OHCNativePlugin::drainWorkers()
{
    for (auto& worker : workers_) worker.second->drain();
}

json OHCNativePlugin::status()
{
    json devices = json::array();
    for (auto& worker : workers_)
    {
        auto state = worker.second->status();
        devices.push_back({{"device", indices_.at(worker.first)}, {"id", state.sequence},
            {"submitted", state.submitted}, {"submitted_hz", state.hz},
            {"replaced", state.replaced}, {"errors", state.errors},
            {"error", state.error}, {"duration_ms", state.duration_ms}});
    }
    return {{"ok", true}, {"generation", generation_}, {"devices", devices},
            {"physical_readback", false}, {"active", active_}};
}

void OHCNativePlugin::queueFrame(const json& request)
{
    if (request["devices"].size() > 64) throw std::runtime_error("too many devices");
    auto controllers = api_ ? api_->GetRGBControllers() : std::vector<RGBControllerInterface*>{};
    std::vector<std::pair<RGBControllerInterface*, json>> targets;
    std::set<unsigned int> seen;
    for (const auto& target : request["devices"])
    {
        if (!target.is_object() || !target.contains("device") || !target["device"].is_number_unsigned()
            || !target.contains("colors") || !target["colors"].is_array())
            throw std::runtime_error("invalid target");
        unsigned int index = target["device"].get<unsigned int>();
        if (index >= controllers.size() || !controllers[index] || !seen.insert(index).second)
            throw std::runtime_error("invalid controller identity");
        auto* controller = controllers[index];
        if (target.value("name", "") != controller->GetName())
            throw std::runtime_error("controller identity changed");
        if (target["colors"].size() != controller->GetLEDCount() || target["colors"].size() > 4096)
            throw std::runtime_error("controller LED count changed");
        for (const auto& color : target["colors"]) parseColor(color);
        targets.emplace_back(controller, target);
    }
    for (const auto& target : targets)
    {
        auto* controller = target.first;
        if (!workers_.count(controller))
        {
            auto worker = std::make_unique<LatestFrameWorker<json>>(
                [this, controller](const json& frame) { applyTarget(controller, frame); });
            worker->reset(fps_);
            workers_.emplace(controller, std::move(worker));
            indices_.emplace(controller, target.second["device"].get<unsigned int>());
        }
        workers_.at(controller)->enqueue(request.value("id", std::uint64_t{0}), target.second);
    }
}

void OHCNativePlugin::applyTarget(RGBControllerInterface* controller, const json& target)
{
    int requested = -1;
    for (unsigned int mode = 0; mode < controller->GetModeCount(); ++mode)
        if (controller->GetModeName(mode) == target.value("mode", "Direct")) requested = mode;
    if (requested < 0) throw std::runtime_error("requested mode is unavailable");
    if (controller->GetActiveMode() != requested) controller->SetActiveMode(requested);
    const auto& colors = target["colors"];
    if (colors.size() != controller->GetLEDCount()) throw std::runtime_error("LED count changed");
    for (unsigned int led = 0; led < colors.size(); ++led) controller->SetColor(led, parseColor(colors[led]));
    controller->UpdateLEDs();
}
