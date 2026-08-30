#!/usr/bin/env python3
"""Regression guards for the 3.4.23 ENE-DRAM cold-boot wake path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
code = (ROOT / "kraken_control.py").read_text(encoding="utf-8")
constants = (ROOT / "app_constants.py").read_text(encoding="utf-8")
integration = (ROOT / "openrgb_integration.py").read_text(encoding="utf-8")

assert 'APP_VERSION = "3.4.29.7"' in constants
assert "def prime_ene_dram_cold_start" in code
assert "def is_ene_dram_device" in code
assert "ENE_DRAM_RECLAIM_PASSES = 2" in code
assert "RGB-ENE-WAKE: Kaltstart-Reclaim über OpenRGB-Treiber" in code
assert "self.prime_ene_dram_cold_start(self.start_openrgb_effect)" in code
assert "self.openrgb_client.color_command(" in code
assert "direct=True" in code
assert "for _pass_index in range(ENE_DRAM_RECLAIM_PASSES)" in code
assert "QTimer.singleShot(320, continuation)" in code
assert "self.ene_dram_cli_prime_done.clear()" in code
assert "self.ene_dram_cli_prime_in_progress = False" in code

# The OpenRGB client command must explicitly request Direct through the
# running local server, not touch ENE SMBus registers itself.
assert 'arguments += ["--mode", "direct"]' in integration
assert 'return self.client_command(*arguments)' in integration
assert "ENERegisterWrite" not in integration

print("3.4.23 ENE-DRAM cold-boot regression guards passed.")
