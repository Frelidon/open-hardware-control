# SPDX-License-Identifier: GPL-3.0-or-later
"""Curated model metadata; links are reviewed, never guessed at UI runtime."""
from dataclasses import dataclass
from urllib.parse import urlsplit
from modules.gpu_profiles.v1_0.catalog import GPU_MODELS


@dataclass(frozen=True)
class Device:
    key: str
    name: str
    category: str
    vendor: str
    kind: str
    state: str
    description: str
    manufacturer_url: str
    product_url: str = ""


CATEGORIES = (
    ("gpu", "Grafikkarten"), ("cooling", "Kühlung"),
    ("mainboard", "Mainboards"), ("rgb", "RGB-Controller"),
    ("mouse", "Mäuse"), ("headset", "Headsets"),
    ("monitor", "Monitore"), ("backends", "Weitere Geräte über Backends"),
)
GPU_DESCRIPTION = "Modellprofil vorhanden. Erkennung und verfügbare Regler richten sich nach Linux-Treiber und LACT. Kein pauschaler Hardwaretest und keine Zusage für die RGB-Beleuchtung dieses Modells."
MOUSE_DESCRIPTION = "Über OpenLinkHub lokal erkannt: DPI-Stufen, Tastenbelegung und Profile. Die Bedienung nutzt nur die vom Backend gemeldeten Funktionen."
HEADSET_DESCRIPTION = "Über OpenLinkHub lokal erkannt. Verfügbare Headset-Einstellungen richten sich nach dem Backend und dem verbundenen Empfänger."

# Official product pages reviewed 11.11.26. NVIDIA family pages explicitly name
# their individual variants. An unavailable exact product page stays absent.
AMD_PRODUCTS = {
    "Radeon RX 9070 GRE": "9000-series/amd-radeon-rx-9070-gre.html",
    "Radeon RX 9070 XT": "9000-series/amd-radeon-rx-9070xt.html",
    "Radeon RX 9070": "9000-series/amd-radeon-rx-9070.html",
    "Radeon RX 9060 XT 16 GB": "9000-series/amd-radeon-rx-9060xt.html",
    "Radeon RX 9060": "9000-series/amd-radeon-rx-9060.html",
    "Radeon RX 7900 XTX": "7000-series/amd-radeon-rx-7900xtx.html",
    "Radeon RX 7900 XT": "7000-series/amd-radeon-rx-7900xt.html",
    "Radeon RX 7900 GRE": "7000-series/amd-radeon-rx-7900-gre.html",
    "Radeon RX 7800 XT": "7000-series/amd-radeon-rx-7800-xt.html",
    "Radeon RX 7700 XT": "7000-series/amd-radeon-rx-7700-xt.html",
    "Radeon RX 7700": "7000-series/amd-radeon-rx-7700.html",
    "Radeon RX 7600 XT": "7000-series/amd-radeon-rx-7600-xt.html",
    "Radeon RX 7600": "7000-series/amd-radeon-rx-7600.html",
}
NVIDIA_PRODUCTS = {
    "5090": "50-series/rtx-5090/", "5080": "50-series/rtx-5080/",
    "5070": "50-series/rtx-5070-family/", "5060": "50-series/rtx-5060-family/",
    "5050": "50-series/rtx-5050/", "4090": "40-series/rtx-4090/",
    "4080": "40-series/rtx-4080-family/", "4070": "40-series/rtx-4070-family/",
    "4060": "40-series/rtx-4060-4060ti/",
}


def gpu_product(row):
    if row["vendor"] == "AMD":
        path = AMD_PRODUCTS.get(row["name"])
        return "https://www.amd.com/en/products/graphics/desktops/radeon/" + path if path else ""
    number = row["name"].split()[2]
    path = NVIDIA_PRODUCTS.get(number)
    return "https://www.nvidia.com/en-us/geforce/graphics-cards/" + path if path else ""


GPU_DEVICES = tuple(Device(
    row["id"], row["name"], "gpu", row["vendor"], "gpu",
    "Modellprofil · Backend erforderlich", GPU_DESCRIPTION,
    "https://www.amd.com/" if row["vendor"] == "AMD" else "https://www.nvidia.com/",
    gpu_product(row),
) for row in GPU_MODELS)

DEVICES = (
    Device("sapphire-9070xt-nitro", "SAPPHIRE NITRO+ Radeon RX 9070 XT OC", "gpu", "AMD", "gpu", "Lokal bestätigt",
           "GPU-Daten über Linux und LACT; die bestätigte externe Beleuchtung über OpenRGB. Verfügbare Regler hängen vom Treiber ab.",
           "https://www.sapphiretech.com/", "https://www.sapphiretech.com/en/consumer/nitro-radeon-rx-9070-xt-16g-gddr6"),
    *GPU_DEVICES,
    Device("kraken-360-2023", "NZXT Kraken 360 RGB (2023)", "cooling", "NZXT", "cooling", "Lokal bestätigt",
           "Kühlmittel, Pumpe, Radiatorlüfter und LCD über liquidctl. Andere Kraken-Modelle benötigen eine eigene Prüfung.",
           "https://nzxt.com/", "https://support.nzxt.com/hc/en-us/articles/47207322896923-Kraken-2023-Specs"),
    Device("levita-360", "Thermalright Levita Vision 360", "cooling", "Thermalright", "lcd", "Lokal bestätigt",
           "Display und gespeicherte Designs über TRCC; Kühlung über bestätigte Mainboard-Anschlüsse. Der Ubuntu-Pfad ist lokal geprüft.",
           "https://www.thermalright.com/", "https://www.thermalright.com/product/levita-vision-360-argb-black/"),
    Device("msi-x870", "MSI MAG X870 TOMAHAWK WIFI", "mainboard", "MSI", "case", "Einrichtung erforderlich",
           "Mainboard-Lüfter über nct6687d und Linux hwmon. Jeder PWM-Anschluss benötigt die vorhandene Kalibrierung und Freigabe.",
           "https://www.msi.com/", "https://www.msi.com/Motherboard/MAG-X870-TOMAHAWK-WIFI"),
    Device("nzxt-rgb-2023", "NZXT RGB Controller 2023", "rgb", "NZXT", "rgb_studio", "Lokal bestätigt",
           "Drei RGB-Kanäle über liquidctl. Die angeschlossenen LEDs und ihre Reihenfolge werden ausdrücklich eingerichtet.",
           "https://nzxt.com/", "https://support.nzxt.com/hc/en-us/articles/47207322896923-Kraken-2023-Specs"),
    Device("airgoo-argb", "Airgoo ARGB Controller", "rgb", "Airgoo", "rgb_studio", "Lokal bestätigt",
           "Mehrere ARGB-Anschlüsse über OpenRGB. LED-Zahlen und Verkabelung bleiben manuelle Angaben; unbekannte Modelle werden nicht automatisch freigegeben.",
           "https://www.airgootech.com/"),
    Device("sabre-rgb-pro", "Corsair SABRE RGB PRO", "mouse", "Corsair", "openlinkhub", "Über Backend", MOUSE_DESCRIPTION,
           "https://www.corsair.com/", "https://www.corsair.com/us/en/p/gaming-mouse/ch-9303111-na/sabre-rgb-pro-champion-series-ultra-light-fps-moba-gaming-mouse-ch-9303111-na"),
    Device("hs80-max", "Corsair HS80 MAX WIRELESS", "headset", "Corsair", "openlinkhub", "Über Backend", HEADSET_DESCRIPTION,
           "https://www.corsair.com/", "https://www.corsair.com/us/en/p/gaming-headsets/ca-9011295-na/hs80-max-wireless-gaming-headset-steel-gray-ca-9011295-na"),
    Device("msi-x30mv", "MSI MAG 274QPF X30MV", "monitor", "MSI", "lcd", "Einrichtung erforderlich",
           "Modellgebundene Bildschirmkorrektur mit gesichertem EDID-Profil. Ubuntu und Fedora bleiben getrennte Wege; die Aktivierung erfolgt über Hardware Fix.",
           "https://www.msi.com/", "https://www.msi.com/Monitor/MAG-274QPF-X30MV"),
    Device("openlinkhub", "Corsair · OpenLinkHub", "backends", "Corsair", "openlinkhub", "Über Backend",
           "Mäuse, Tastaturen, Headsets, Kühlung und weitere vom lokalen OpenLinkHub gemeldete Geräte. Nur tatsächlich angebotene Funktionen sind bedienbar.", "https://www.corsair.com/"),
    Device("openrgb", "OpenRGB · RGB-Geräte", "backends", "OpenRGB", "rgb_studio", "Über Backend",
           "Geräte, Modi und Zonen stammen aus der installierten OpenRGB-Version. Eine Backend-Erkennung bestätigt nicht jedes Herstellermodell oder die sichtbare LED-Ausgabe.", "https://openrgb.org/"),
)


def safe_link(value):
    """No empty/relative links, credentials or executable schemes in buttons."""
    url = urlsplit(value)
    return value if url.scheme == "https" and url.hostname and not url.username and not url.password else ""
