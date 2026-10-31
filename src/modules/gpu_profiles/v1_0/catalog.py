# SPDX-License-Identifier: GPL-3.0-or-later
"""Current mainstream desktop GPU names; never a source of tuning limits."""

from __future__ import annotations


def _rows(vendor: str, generation: str, names: tuple[str, ...]) -> tuple[dict[str, str], ...]:
    return tuple({
        "id": f"{vendor.casefold()}-{name.casefold().replace(' ', '-').replace('/', '-')}",
        "vendor": vendor,
        "generation": generation,
        "name": name,
    } for name in names)


GPU_MODELS = (
    *_rows("AMD", "Radeon RX 9000", (
        "Radeon RX 9070 GRE", "Radeon RX 9070 XT", "Radeon RX 9070",
        "Radeon RX 9060 XT 16 GB", "Radeon RX 9060 XT 8 GB", "Radeon RX 9060",
    )),
    *_rows("AMD", "Radeon RX 7000", (
        "Radeon RX 7900 XTX", "Radeon RX 7900 XT", "Radeon RX 7900 GRE",
        "Radeon RX 7800 XT", "Radeon RX 7700 XT", "Radeon RX 7700",
        "Radeon RX 7600 XT", "Radeon RX 7600",
    )),
    *_rows("NVIDIA", "GeForce RTX 50", (
        "GeForce RTX 5090", "GeForce RTX 5080", "GeForce RTX 5070 Ti",
        "GeForce RTX 5070", "GeForce RTX 5060 Ti", "GeForce RTX 5060",
        "GeForce RTX 5050",
    )),
    *_rows("NVIDIA", "GeForce RTX 40", (
        "GeForce RTX 4090", "GeForce RTX 4080 SUPER", "GeForce RTX 4080",
        "GeForce RTX 4070 Ti SUPER", "GeForce RTX 4070 Ti",
        "GeForce RTX 4070 SUPER", "GeForce RTX 4070", "GeForce RTX 4060 Ti",
        "GeForce RTX 4060",
    )),
)


def model_by_id(model_id: object) -> dict[str, str] | None:
    return next((dict(row) for row in GPU_MODELS if row["id"] == str(model_id)), None)


def detect_model(device_name: object) -> dict[str, str] | None:
    name = str(device_name).casefold()
    return next((dict(row) for row in GPU_MODELS if row["name"].casefold() in name), None)
