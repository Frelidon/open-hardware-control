#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Original schematic case templates; no manufacturer artwork is bundled."""

from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class CaseTemplate:
    case_id: str
    manufacturer: str
    model: str
    form_factor: str
    fan_layout: tuple[tuple[str, int], ...]
    radiator_mm: int
    source_url: str
    exact: bool = False

    @property
    def title(self) -> str:
        return f"{self.manufacturer} · {self.model}"

    @property
    def visual_style(self) -> str:
        """Select an original OHC silhouette family without bundling product art."""
        if self.case_id == DEFAULT_CASE_ID:
            return "retro"
        if "north" in self.case_id:
            return "slatted"
        if any(token in self.case_id for token in ("h6-", "h9-", "o11-", "y60", "y70", "king-95", "nv5")):
            return "panorama"
        if "dual chamber" in self.form_factor.casefold() or "6500" in self.case_id or "5400" in self.case_id:
            return "dual"
        if "mini-itx" in self.form_factor.casefold() or "nr200" in self.case_id:
            return "compact"
        return "classic"


def _case(case_id: str, manufacturer: str, model: str, form: str,
          layout: tuple[tuple[str, int], ...], radiator: int, url: str,
          exact: bool = False) -> CaseTemplate:
    return CaseTemplate(case_id, manufacturer, model, form, layout, radiator, url, exact)


CLASSIC = (("front", 3), ("top", 3), ("rear", 1), ("bottom", 2))
PANORAMA = (("side", 3), ("top", 3), ("rear", 1), ("bottom", 3))
COMPACT = (("front", 2), ("top", 2), ("rear", 1), ("bottom", 2))
LARGE = (("front", 3), ("side", 3), ("top", 3), ("rear", 1), ("bottom", 3))

CASE_TEMPLATES: tuple[CaseTemplate, ...] = (
    _case("thermaltake-retro-360-tg", "Thermaltake", "Retro 360 TG", "ATX / Micro-ATX / Mini-ITX", (("front", 2), ("side", 3), ("top", 3), ("rear", 1), ("bottom", 3)), 360, "https://file.thermaltake.com/file/qig/Retro360TG_Manual.pdf", True),
    _case("fractal-north", "Fractal Design", "North", "ATX", CLASSIC, 360, "https://www.fractal-design.com/products/cases/north/north/"),
    _case("fractal-north-xl", "Fractal Design", "North XL", "E-ATX", LARGE, 420, "https://www.fractal-design.com/products/cases/north/north-xl/"),
    _case("fractal-meshify-3", "Fractal Design", "Meshify 3", "ATX", CLASSIC, 360, "https://www.fractal-design.com/products/cases/meshify/meshify-3/"),
    _case("fractal-torrent", "Fractal Design", "Torrent", "E-ATX", LARGE, 420, "https://www.fractal-design.com/products/cases/torrent/torrent/"),
    _case("nzxt-h5-flow-2024", "NZXT", "H5 Flow (2024)", "ATX", COMPACT, 280, "https://nzxt.com/product/h5-flow"),
    _case("nzxt-h6-flow", "NZXT", "H6 Flow", "ATX", PANORAMA, 360, "https://nzxt.com/product/h6-flow"),
    _case("nzxt-h7-flow-2024", "NZXT", "H7 Flow (2024)", "ATX", CLASSIC, 360, "https://nzxt.com/product/h7-flow"),
    _case("nzxt-h9-flow", "NZXT", "H9 Flow", "ATX", LARGE, 360, "https://nzxt.com/product/h9-flow"),
    _case("corsair-3200d", "Corsair", "FRAME 4000D", "ATX", CLASSIC, 360, "https://www.corsair.com/us/en/p/pc-cases/cc-9011290-ww/frame-4000d-rs-argb-modular-mid-tower-pc-case-white-cc-9011290-ww"),
    _case("corsair-4000d-airflow", "Corsair", "4000D Airflow", "ATX", CLASSIC, 360, "https://www.corsair.com/us/en/p/pc-cases/cc-9011200-ww/4000d-airflow-tempered-glass-mid-tower-atx-case-black-cc-9011200-ww"),
    _case("corsair-5000d-airflow", "Corsair", "5000D Airflow", "ATX", LARGE, 360, "https://www.corsair.com/us/en/p/pc-cases/cc-9011210-ww/5000d-airflow-tempered-glass-mid-tower-atx-pc-case-black-cc-9011210-ww"),
    _case("corsair-6500d-airflow", "Corsair", "6500D Airflow", "Dual chamber ATX", PANORAMA, 360, "https://www.corsair.com/us/en/p/pc-cases/cc-9011259-ww/6500d-airflow-mid-tower-dual-chamber-pc-case-black-cc-9011259-ww"),
    _case("corsair-air-5400", "Corsair", "AIR 5400 RS-R", "Dual chamber ATX", LARGE, 360, "https://www.corsair.com/"),
    _case("lian-li-o11-evo", "Lian Li", "O11 Dynamic EVO", "ATX", PANORAMA, 360, "https://lian-li.com/product/o11-dynamic-evo/"),
    _case("lian-li-o11-vision", "Lian Li", "O11 Vision", "ATX", PANORAMA, 360, "https://lian-li.com/product/o11-vision/"),
    _case("lian-li-lancool-207", "Lian Li", "LANCOOL 207", "ATX", CLASSIC, 360, "https://lian-li.com/product/lancool-207/"),
    _case("lian-li-lancool-iii", "Lian Li", "LANCOOL III", "E-ATX", LARGE, 420, "https://lian-li.com/product/lancool-iii/"),
    _case("hyte-y60", "HYTE", "Y60", "ATX", PANORAMA, 360, "https://hyte.com/store/y60"),
    _case("hyte-y70", "HYTE", "Y70", "ATX", PANORAMA, 360, "https://hyte.com/store/y70"),
    _case("montech-air-903-max", "Montech", "AIR 903 MAX", "E-ATX", CLASSIC, 360, "https://www.montechpc.com/en/products_detail.php?nid=355"),
    _case("montech-king-95-pro", "Montech", "KING 95 PRO", "ATX", PANORAMA, 360, "https://www.montechpc.com/en/products_detail.php?nid=385"),
    _case("bequiet-pure-base-500dx", "be quiet!", "Pure Base 500DX", "ATX", CLASSIC, 360, "https://www.bequiet.com/en/case/1854"),
    _case("bequiet-shadow-base-800", "be quiet!", "Shadow Base 800", "E-ATX", LARGE, 420, "https://www.bequiet.com/en/case/4483"),
    _case("phanteks-g500a", "Phanteks", "Eclipse G500A", "E-ATX", CLASSIC, 420, "https://phanteks.com/product/eclipse-g500a-drgb-black/"),
    _case("phanteks-nv5", "Phanteks", "NV5", "ATX", PANORAMA, 360, "https://phanteks.com/product/nv5-black/"),
    _case("coolermaster-td500-v2", "Cooler Master", "TD500 Mesh V2", "ATX", CLASSIC, 360, "https://www.coolermaster.com/en-global/products/masterbox-td500-mesh-v2/"),
    _case("coolermaster-nr200p-v2", "Cooler Master", "NR200P V2", "Mini-ITX", COMPACT, 280, "https://www.coolermaster.com/en-global/products/masterbox-nr200p-v2/"),
    _case("asus-proart-pa602", "ASUS", "ProArt PA602", "E-ATX", LARGE, 420, "https://www.asus.com/motherboards-components/gaming-cases/proart/proart-pa602/"),
    _case("antec-flux-pro", "Antec", "FLUX PRO", "E-ATX", LARGE, 420, "https://www.antec.com/product/case/flux-pro"),
)

DEFAULT_CASE_ID = "thermaltake-retro-360-tg"


def case_template(case_id: object) -> CaseTemplate:
    clean = str(case_id or DEFAULT_CASE_ID)
    return next((item for item in CASE_TEMPLATES if item.case_id == clean), CASE_TEMPLATES[0])
