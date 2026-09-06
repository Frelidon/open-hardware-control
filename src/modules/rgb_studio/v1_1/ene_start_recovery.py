#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded post-start recovery policy for ENE-controlled DRAM lighting."""

from __future__ import annotations


ENE_DRAM_POST_START_RETRY_DELAYS_MS = (45_000, 120_000, 240_000)


class EneDramStartRecoveryMixin:
    """Coordinate delayed native reclaims through an existing RGB controller."""

    def cancel_ene_dram_post_start_retries(self, *, reset: bool = True) -> None:
        if hasattr(self, "ene_dram_post_start_retry_timer"):
            self.ene_dram_post_start_retry_timer.stop()
        if reset:
            self.ene_dram_post_start_retry_index = 0

    def schedule_ene_dram_post_start_retries(self) -> None:
        self.cancel_ene_dram_post_start_retries()
        targets = [device for device in self.selected_openrgb_devices() if self.is_ene_dram_device(device)]
        if not targets or not self.openrgb_write_enabled or not self.openrgb_server_reachable:
            return
        self.ene_dram_post_start_retry_timer.start(ENE_DRAM_POST_START_RETRY_DELAYS_MS[0])
        self.log_message(
            "RGB-ENE-WAKE: drei vorsorgliche Start-Nachprüfungen geplant · "
            "nach 45 s, weiteren 2 min und weiteren 4 min"
        )

    def _retry_ene_dram_profile_start(self) -> None:
        if (
            not self.openrgb_write_enabled
            or not self.openrgb_server_reachable
            or self.openrgb_external_server_detected
            or self.rgb_reset_in_progress
        ):
            self.cancel_ene_dram_post_start_retries()
            return
        targets = [device for device in self.selected_openrgb_devices() if self.is_ene_dram_device(device)]
        total = len(ENE_DRAM_POST_START_RETRY_DELAYS_MS)
        if not targets or self.ene_dram_post_start_retry_index >= total:
            self.cancel_ene_dram_post_start_retries()
            return
        if self.ene_dram_cli_prime_in_progress:
            self.ene_dram_post_start_retry_timer.start(5_000)
            return
        attempt = self.ene_dram_post_start_retry_index + 1
        for device in targets:
            stable_id = self.openrgb_stable_ids.get(device.index, f"openrgb:index-{device.index}")
            self.ene_dram_cli_prime_done.discard(stable_id)
        self.log_message(
            f"RGB-ENE-WAKE: vorsorgliche Start-Nachprüfung {attempt}/{total} · "
            f"{len(targets)} ausgewählte ENE-DRAM-Gerät(e)"
        )

        def finished() -> None:
            if self.openrgb_write_enabled and self.rgb_active_design_title:
                self.log_message("RGB-ENE-WAKE: aktuelles Design wird nach der Start-Nachprüfung erneut angewendet")
                self.request_rgb_direct_apply(80)
            self.ene_dram_post_start_retry_index += 1
            if self.ene_dram_post_start_retry_index < total:
                delay = ENE_DRAM_POST_START_RETRY_DELAYS_MS[self.ene_dram_post_start_retry_index]
                self.ene_dram_post_start_retry_timer.start(delay)
            else:
                self.log_message("RGB-ENE-WAKE: begrenzte Start-Nachprüfungen abgeschlossen")

        self.prime_ene_dram_cold_start(finished)
