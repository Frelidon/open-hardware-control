#!/usr/bin/env python3
"""Static/runtime regression guards for the 3.4.22 stability hotfix."""
from pathlib import Path
import inspect
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import kraken_cam_streamer as streamer

code = (ROOT / "kraken_control.py").read_text(encoding="utf-8")

# LCD: UI passes scale as sixth positional argument; streamer must accept it.
sig = inspect.signature(streamer.prepare_gif)
assert "scale_percent" in sig.parameters
assert sig.parameters["scale_percent"].default == 100

# RGB: the persistent SDK worker must not be killed for every native/NZXT write.
seq = code[code.index("    def run_rgb_command_sequence("):code.index("    def run_openrgb_write(")]
assert "openrgb_effect_process.kill()" not in seq
assert "uses_sdk_helper and self.openrgb_worker_frame_inflight" in seq

# ENE-DRAM/device test: the selected target must be allowed to force a one-shot prepare.
test_block = code[code.index("    def build_rgb_device_test_commands("):code.index("    def run_rgb_device_test(")]
assert "direct=is_target or stable_id not in" in test_block

# Animated design confirmation waits for both native and Direct paths.
assert "def begin_rgb_design_confirmation(" in code
assert 'self.acknowledge_rgb_design_part("native", applied)' in code
assert 'self.acknowledge_rgb_design_part("direct", completed_snapshot)' in code

# CPU profile button must load and immediately activate both recommended curves.
cpu = code[code.index("    def apply_selected_cpu_profile("):code.index("    # ---------- status ----------")]
assert '"pump": pump_target, "fan": fan_target' in cpu
assert "apply_cpu_curve_targets(" in cpu
assert "Beide empfohlenen CPU-Kurven wurden direkt aktiviert." in cpu

print("3.4.22 stability-hotfix regression guards passed.")
