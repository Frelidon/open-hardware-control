// SPDX-License-Identifier: GPL-3.0-or-later
// Original OHC integration: only invokes the fixed local D-Bus service.

function invoke(method) {
    callDBus(
        "org.frelidon.OpenHardwareControl.DesktopShell",
        "/DesktopShell",
        "",
        method
    );
}

registerScreenEdge(KWin.ElectricTopRight, function () {
    invoke("ShowCharms");
});

registerScreenEdge(KWin.ElectricBottomRight, function () {
    invoke("ShowCharms");
});

registerShortcut(
    "Open Hardware Control Charms",
    "Windows 8 Charms bar",
    "Meta+C",
    function () { invoke("ToggleCharms"); }
);

registerShortcut(
    "Open Hardware Control Start",
    "Windows 8 Start screen",
    "Meta+Space",
    function () { invoke("ToggleStart"); }
);
