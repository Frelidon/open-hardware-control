#pragma once

#include <QObject>
#include <QWidget>
#include "OpenRGBPluginInterface.h"
#include "LatestFrameWorker.h"

#include <atomic>
#include <condition_variable>
#include <mutex>
#include <string>
#include <thread>
#include <memory>
#include <unordered_map>

#include <nlohmann/json.hpp>

class OHCNativePlugin final : public QObject, public OpenRGBPluginInterface
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID OpenRGBPluginInterface_IID FILE "ohc_native_plugin.json")
    Q_INTERFACES(OpenRGBPluginInterface)

public:
    OpenRGBPluginInfo GetPluginInfo() override;
    unsigned int GetPluginAPIVersion() override { return OPENRGB_PLUGIN_API_VERSION; }
    void Load(OpenRGBPluginAPIInterface* api) override;
    // OpenRGB 1.1 always wraps the returned widget in
    // OpenRGBPluginContainer and dereferences it.  Even this headless transport
    // therefore has to provide a valid, container-owned placeholder.
    QWidget* GetWidget() override { return new QWidget(); }
    QMenu* GetTrayMenu() override { return nullptr; }
    void Unload() override;
    void OnProfileAboutToLoad() override {}
    void OnProfileLoad(nlohmann::json) override {}
    nlohmann::json OnProfileSave() override { return {}; }
    unsigned char* OnSDKCommand(unsigned int, unsigned char*, unsigned int*) override { return nullptr; }
    void ProfileManagerUpdated(unsigned int) override {}
    void ResourceManagerUpdated(unsigned int) override {}
    void SettingsManagerUpdated(unsigned int) override {}

private:
    void serverLoop();
    bool handleLine(int fd, const std::string& line);
    nlohmann::json status();
    void queueFrame(const nlohmann::json& request);
    void applyTarget(RGBControllerInterface* controller, const nlohmann::json& target);
    void drainWorkers();
    void stopServer();

    OpenRGBPluginAPIInterface* api_ = nullptr;
    std::atomic<bool> running_{false};
    int server_fd_ = -1;
    std::thread server_thread_;
    std::unordered_map<RGBControllerInterface*, std::unique_ptr<LatestFrameWorker<nlohmann::json>>> workers_;
    std::unordered_map<RGBControllerInterface*, unsigned int> indices_;
    unsigned int fps_ = 60;
    std::uint64_t generation_ = 0;
    bool active_ = false;
    std::string socket_path_;
};
